# 🧪 Plano de Testes - Sistema ARES

**Projeto:** Sistema de Gestão de Estoque ARES  
**Data:** 26/11/2025  
**Versão:** 1.0.0  
**Status:** Ready for Testing

---

## 📋 1. PLANO DE TESTES (Tabela Executiva)

| ID | Módulo | Tipo | Casos | Prioridade | Cobertura | Status | Responsável | Prazo |
|----|--------|------|-------|------------|-----------|--------|-------------|-------|
| T01 | Autenticação | Funcional | 8 | Alta | 100% | ⏳ Pendente | QA Team | 27/11 |
| T02 | Produtos | Funcional | 12 | Alta | 90% | ⏳ Pendente | QA Team | 27/11 |
| T03 | Movimentações | Funcional | 10 | Alta | 90% | ⏳ Pendente | QA Team | 28/11 |
| T04 | ACL/Permissões | Segurança | 15 | Crítica | 95% | ⏳ Pendente | Security | 28/11 |
| T05 | Auditoria | Compliance | 8 | Alta | 100% | ⏳ Pendente | QA Team | 29/11 |
| T06 | API REST | Integração | 20 | Alta | 85% | ⏳ Pendente | API Team | 29/11 |
| T07 | Upload | Funcional | 6 | Média | 80% | ⏳ Pendente | QA Team | 30/11 |
| T08 | Relatórios | Funcional | 8 | Média | 75% | ⏳ Pendente | QA Team | 30/11 |
| T09 | HomePage Wagtail | UI/UX | 10 | Média | 85% | ⏳ Pendente | UX Team | 01/12 |
| T10 | Theme Switcher | UI/UX | 5 | Baixa | 90% | ⏳ Pendente | UX Team | 01/12 |
| T11 | Performance | Carga | 5 | Alta | 70% | ⏳ Pendente | DevOps | 02/12 |
| T12 | Segurança | Penetração | 10 | Crítica | 80% | ⏳ Pendente | Security | 03/12 |
| **TOTAL** | **12 módulos** | **6 tipos** | **117** | - | **87%** | **0%** | - | **03/12** |

---

## 🎯 2. CASOS DE TESTE DETALHADOS

### T01 - Autenticação (8 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T01.1 | Login com credenciais válidas | username: admin, password: senha123 | Redirecionamento para dashboard | Alta |
| T01.2 | Login com senha incorreta | username: admin, password: errada | Mensagem de erro, permanece na tela | Alta |
| T01.3 | Login com usuário inexistente | username: naoexiste, password: 123 | Mensagem de erro | Alta |
| T01.4 | Logout de usuário autenticado | Clicar em "Sair" | Redirecionamento para login | Alta |
| T01.5 | Acesso a página protegida sem login | Acessar /dashboard/ sem auth | Redirecionamento para login | Alta |
| T01.6 | Sessão expirada | Aguardar timeout da sessão | Redirecionamento para login | Média |
| T01.7 | Tentativas de login bloqueadas | 5 tentativas falhas consecutivas | Conta bloqueada temporariamente | Alta |
| T01.8 | Login via SSO (se habilitado) | Autenticar via Keycloak | Login bem-sucedido | Média |

### T02 - Produtos (12 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T02.1 | Criar produto válido | SKU: PROD-001, Nome: Mouse | Produto criado com sucesso | Alta |
| T02.2 | Criar produto com SKU duplicado | SKU existente | Erro de validação | Alta |
| T02.3 | Criar produto sem campos obrigatórios | SKU vazio | Erro de validação | Alta |
| T02.4 | Editar produto existente | Alterar nome | Produto atualizado | Alta |
| T02.5 | Excluir produto (soft delete) | Clicar em "Remover" | Produto marcado como inativo | Alta |
| T02.6 | Listar produtos com filtros | Filtrar por categoria | Apenas produtos da categoria | Média |
| T02.7 | Buscar produto por SKU/nome | Buscar "mouse" | Produtos correspondentes | Média |
| T02.8 | Visualizar produto com estoque baixo | Produto com current_stock ≤ min_stock | Alerta visual exibido | Alta |
| T02.9 | Visualizar produto vencido | Produto com expiry_date < hoje | Alerta visual exibido | Alta |
| T02.10 | Criar categoria | Nome: Eletrônicos | Categoria criada | Média |
| T02.11 | Criar unidade de medida | Nome: UN | Unidade criada | Média |
| T02.12 | Validar campos numéricos | Preço: -10 | Erro de validação | Média |

### T03 - Movimentações (10 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T03.1 | Criar entrada de estoque | Tipo: ENTRADA, Qtd: 100 | Estoque aumentado corretamente | Alta |
| T03.2 | Criar saída de estoque | Tipo: SAIDA, Qtd: 50 | Estoque diminuído corretamente | Alta |
| T03.3 | Saída com estoque insuficiente | Qtd: 1000 (maior que estoque) | Erro de validação | Alta |
| T03.4 | Criar ajuste de estoque | Tipo: AJUSTE, Qtd: 10 | Estoque ajustado | Média |
| T03.5 | Movimentação com documento | NF: 12345 | Documento registrado | Média |
| T03.6 | Listar movimentações por produto | Produto ID: 1 | Apenas movimentações do produto | Média |
| T03.7 | Filtrar movimentações por tipo | Tipo: ENTRADA | Apenas entradas | Média |
| T03.8 | Filtrar por período | Data: 01/11 a 30/11 | Movimentações do período | Média |
| T03.9 | Validar stock_before e stock_after | Criar movimentação | Valores corretos registrados | Alta |
| T03.10 | Verificar auditoria de movimentação | Criar movimentação | Log de auditoria criado | Alta |

### T04 - ACL/Permissões (15 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T04.1 | Representante Legal - acesso total | Perfil: REPR_LEGAL | Acesso a todas as funcionalidades | Crítica |
| T04.2 | Representante Delegado - acesso limitado | Perfil: REPR_DELEGADO | Acesso administrativo limitado | Crítica |
| T04.3 | Operador - acesso básico | Perfil: OPERADOR | Apenas operações básicas | Crítica |
| T04.4 | Operador tentando acessar admin | Acessar /admin/ | Acesso negado (403) | Crítica |
| T04.5 | Criar perfil com permissões customizadas | Definir permissões JSON | Perfil criado corretamente | Alta |
| T04.6 | Validar expiração de perfil | Perfil com data_expiracao passada | Acesso negado | Alta |
| T04.7 | Validar perfil inativo | Perfil com ativo=False | Acesso negado | Alta |
| T04.8 | Decorator @require_perfil | View com decorator | Apenas perfis permitidos acessam | Alta |
| T04.9 | Mixin PerfilRequiredMixin | View com mixin | Apenas perfis permitidos acessam | Alta |
| T04.10 | Template tag tem_perfil | {% if user\|tem_perfil:'REPR_LEGAL' %} | Exibição condicional funciona | Média |
| T04.11 | Permissão pode_editar_produtos | Operador editando produto | Verificar permissão | Alta |
| T04.12 | Permissão pode_aprovar_movimentacoes | Operador aprovando | Verificar permissão | Alta |
| T04.13 | Permissão pode_gerenciar_usuarios | Delegado gerenciando usuários | Verificar permissão | Alta |
| T04.14 | Badge de perfil no template | Usuário autenticado | Badge correto exibido | Baixa |
| T04.15 | Auditoria de mudança de perfil | Alterar perfil de usuário | Log de auditoria criado | Alta |

### T05 - Auditoria (8 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T05.1 | Log de criação de produto | Criar produto | AuditLog com action=CREATE | Alta |
| T05.2 | Log de atualização | Editar produto | AuditLog com action=UPDATE e changes | Alta |
| T05.3 | Log de exclusão | Remover produto | AuditLog com action=DELETE | Alta |
| T05.4 | Captura de IP do usuário | Criar log | ip_address registrado | Alta |
| T05.5 | Captura de User-Agent | Criar log | user_agent registrado | Média |
| T05.6 | Filtrar logs por usuário | Filtro user_id=1 | Apenas logs do usuário | Média |
| T05.7 | Filtrar logs por ação | Filtro action=CREATE | Apenas criações | Média |
| T05.8 | Visualizar detalhes de log | Clicar em log | Changes exibido corretamente | Média |

### T06 - API REST (20 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T06.1 | Obter JWT token | POST /api/v1/auth/token/ | access e refresh tokens | Crítica |
| T06.2 | Renovar JWT token | POST /api/v1/auth/token/refresh/ | Novo access token | Alta |
| T06.3 | Verificar JWT token | POST /api/v1/auth/token/verify/ | Status 200 | Alta |
| T06.4 | Acessar endpoint sem token | GET /api/v1/products/ sem auth | 401 Unauthorized | Crítica |
| T06.5 | Listar produtos via API | GET /api/v1/products/ | Lista paginada | Alta |
| T06.6 | Criar produto via API | POST /api/v1/products/ | 201 Created | Alta |
| T06.7 | Atualizar produto via API | PUT /api/v1/products/1/ | 200 OK | Alta |
| T06.8 | Remover produto via API | DELETE /api/v1/products/1/ | 204 No Content | Alta |
| T06.9 | Filtrar produtos via API | ?category=1&low_stock=true | Produtos filtrados | Média |
| T06.10 | Paginação da API | ?page=2 | Página 2 retornada | Média |
| T06.11 | Criar movimentação via API | POST /api/v1/movements/ | 201 Created | Alta |
| T06.12 | Bulk create movimentações | POST /api/v1/movements/bulk_create/ | Múltiplas criadas | Alta |
| T06.13 | Estatísticas de produtos | GET /api/v1/products/stats/ | JSON com stats | Média |
| T06.14 | Produtos com estoque baixo | GET /api/v1/products/low_stock/ | Produtos filtrados | Média |
| T06.15 | Swagger UI acessível | GET /api/v1/docs/ | Documentação carregada | Média |
| T06.16 | Rate limiting anônimo | 101 requests/hora sem auth | 429 Too Many Requests | Alta |
| T06.17 | Rate limiting autenticado | 1001 requests/hora com auth | 429 Too Many Requests | Média |
| T06.18 | CORS headers | Request de origem externa | Headers CORS corretos | Alta |
| T06.19 | Validação de campos API | Campo inválido | 400 Bad Request | Alta |
| T06.20 | Endpoint /users/me/ | GET /api/v1/users/me/ | Dados do usuário | Média |

### T07 - Upload (6 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T07.1 | Upload de imagem válida | JPG 2MB | Upload bem-sucedido | Alta |
| T07.2 | Upload de arquivo grande | 15MB | Erro de validação | Alta |
| T07.3 | Upload de tipo não permitido | EXE | Erro de validação | Alta |
| T07.4 | Redimensionamento automático | Imagem 5000x5000 | Imagem redimensionada | Média |
| T07.5 | Limpeza de uploads antigos | Task scheduled | Arquivos antigos removidos | Baixa |
| T07.6 | Eventos de upload | Upload completado | Evento disparado | Baixa |

### T08 - Relatórios (8 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T08.1 | Gerar relatório PDF | Clicar em "Gerar PDF" | PDF baixado | Alta |
| T08.2 | Exportar relatório CSV | Clicar em "Exportar CSV" | CSV baixado | Alta |
| T08.3 | Relatório de estoque | Filtrar por categoria | Relatório correto | Alta |
| T08.4 | Relatório de movimentações | Período: 01/11 a 30/11 | Movimentações do período | Alta |
| T08.5 | Relatório com dados vazios | Período sem movimentações | Mensagem apropriada | Média |
| T08.6 | Performance de relatório grande | 10.000+ registros | Carrega em < 10s | Alta |
| T08.7 | Agendamento de relatório | Agendar envio diário | Relatório enviado | Baixa |
| T08.8 | Gráficos de dashboard | Acessar dashboard | Gráficos carregados | Média |

### T09 - HomePage Wagtail (10 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T09.1 | Criar HomePage via admin | Adicionar blocos StreamField | Página criada | Média |
| T09.2 | Adicionar HeroBlock | Título, subtítulo, imagem | Hero exibido | Média |
| T09.3 | Adicionar BannerBlock | 3 banners com imagens | Carrossel funciona | Média |
| T09.4 | Adicionar DestaqueBlock | Destaque com ícone | Destaque exibido | Baixa |
| T09.5 | Adicionar NoticiaBlock | Notícia com data | Notícia exibida | Baixa |
| T09.6 | Adicionar CallToActionBlock | CTA com botão | Botão funciona | Baixa |
| T09.7 | Reordenar blocos | Arrastar e soltar | Ordem alterada | Baixa |
| T09.8 | Publicar página | Clicar em "Publicar" | Página pública visível | Média |
| T09.9 | Preview de página | Clicar em "Preview" | Preview carregado | Baixa |
| T09.10 | Responsividade mobile | Acessar em mobile | Layout responsivo | Alta |

### T10 - Theme Switcher (5 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T10.1 | Alternar para tema escuro | Clicar no botão sol/lua | Tema muda para dark | Média |
| T10.2 | Alternar para tema claro | Clicar no botão sol/lua | Tema muda para light | Média |
| T10.3 | Persistência de preferência | Fechar e reabrir navegador | Tema mantido | Média |
| T10.4 | Atalho de teclado | Ctrl+Shift+T | Tema alterna | Baixa |
| T10.5 | Detecção de preferência do sistema | prefers-color-scheme: dark | Tema dark aplicado | Baixa |

### T11 - Performance (5 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T11.1 | Tempo de carregamento homepage | Acessar / | < 2 segundos | Alta |
| T11.2 | Tempo de carregamento dashboard | Acessar /dashboard/ | < 3 segundos | Alta |
| T11.3 | Listagem de 1000 produtos | GET /produtos/?page=1 | < 5 segundos | Alta |
| T11.4 | Consulta complexa com joins | Relatório com múltiplas tabelas | < 10 segundos | Média |
| T11.5 | Carga simultânea | 100 usuários simultâneos | Sistema responsivo | Alta |

### T12 - Segurança (10 casos)

| ID | Caso de Teste | Entrada | Resultado Esperado | Prioridade |
|----|---------------|---------|-------------------|------------|
| T12.1 | SQL Injection | ' OR '1'='1 em campo | Entrada sanitizada | Crítica |
| T12.2 | XSS (Cross-Site Scripting) | <script>alert('XSS')</script> | HTML escapado | Crítica |
| T12.3 | CSRF Token | POST sem token | 403 Forbidden | Crítica |
| T12.4 | Clickjacking | Tentar iframe | X-Frame-Options bloqueado | Alta |
| T12.5 | Força bruta em login | 100 tentativas rápidas | Bloqueio temporário | Alta |
| T12.6 | Acesso a arquivos sensíveis | GET /settings.py | 404 Not Found | Crítica |
| T12.7 | Privilege escalation | Operador tentando admin | 403 Forbidden | Crítica |
| T12.8 | Session hijacking | Cookie de outro usuário | Sessão inválida | Alta |
| T12.9 | Password strength | Senha fraca: 123 | Erro de validação | Média |
| T12.10 | HTTPS enforcement | HTTP request | Redirect para HTTPS | Alta |

---

## 📊 3. MÉTRICAS E ESTIMATIVAS

### 3.1. Cobertura de Testes

| Categoria | Meta | Atual | Gap |
|-----------|------|-------|-----|
| Testes Unitários | 90% | 0% | -90% |
| Testes de Integração | 80% | 0% | -80% |
| Testes E2E | 70% | 0% | -70% |
| Testes de API | 85% | 0% | -85% |
| Testes de Segurança | 80% | 0% | -80% |
| **MÉDIA** | **81%** | **0%** | **-81%** |

### 3.2. Estimativas de Tempo

| Fase | Casos | Horas/Caso | Total Horas | Dias (8h) |
|------|-------|------------|-------------|-----------|
| Preparação de ambiente | - | - | 8h | 1 |
| Testes Unitários | 50 | 0.5h | 25h | 3 |
| Testes Integração | 40 | 1h | 40h | 5 |
| Testes E2E | 27 | 2h | 54h | 7 |
| Testes API | 20 | 1h | 20h | 2.5 |
| Testes Segurança | 10 | 3h | 30h | 4 |
| Correção de bugs | - | - | 40h | 5 |
| Documentação | - | - | 16h | 2 |
| **TOTAL** | **147** | **-** | **233h** | **29.5 dias** |

### 3.3. Recursos Necessários

| Perfil | Quantidade | Dedicação | Período |
|--------|------------|-----------|---------|
| QA Engineer | 2 | 100% | 4 semanas |
| Security Tester | 1 | 50% | 1 semana |
| DevOps Engineer | 1 | 25% | 2 semanas |
| Dev Frontend | 1 | 25% | 1 semana |
| Dev Backend | 1 | 25% | 2 semanas |

### 3.4. Cronograma Sugerido

| Semana | Atividades | Progresso Esperado |
|--------|------------|-------------------|
| Semana 1 | Setup + Testes Unitários (T01, T02) | 20% |
| Semana 2 | Testes Integração (T03, T04, T05) | 45% |
| Semana 3 | Testes E2E (T06, T07, T08) | 70% |
| Semana 4 | Testes Segurança + Correções (T09-T12) | 100% |

---

## 🎯 4. CRITÉRIOS DE ACEITE

### 4.1. Obrigatórios (Must Have)

- ✅ 100% dos testes críticos passando
- ✅ Cobertura mínima de 80% em código crítico (auth, ACL, movimentações)
- ✅ 0 vulnerabilidades de segurança críticas
- ✅ Tempo de resposta < 3s para 95% das requisições
- ✅ API REST 100% funcional e documentada

### 4.2. Desejáveis (Should Have)

- ⚠️ Cobertura geral de 85%+
- ⚠️ Testes automatizados em CI/CD
- ⚠️ Relatórios de teste automatizados
- ⚠️ Performance < 2s para 90% das requisições

### 4.3. Opcionais (Nice to Have)

- ⏳ Testes de carga com 500+ usuários
- ⏳ Testes de stress
- ⏳ Testes de compatibilidade multi-browser
- ⏳ Análise de acessibilidade (WCAG)

---

## 📝 5. FERRAMENTAS RECOMENDADAS

### 5.1. Testes Automatizados

| Tipo | Ferramenta | Status |
|------|-----------|--------|
| Unit Tests | pytest + pytest-django | ✅ Disponível |
| Coverage | pytest-cov | ✅ Disponível |
| API Tests | pytest-rest-framework | ⏳ Instalar |
| E2E Tests | Selenium + pytest | ⏳ Instalar |
| Load Tests | Locust | ⏳ Instalar |
| Security | Bandit + Safety | ⏳ Instalar |

### 5.2. CI/CD

| Ferramenta | Propósito | Prioridade |
|-----------|----------|-----------|
| GitHub Actions | Pipeline CI/CD | Alta |
| SonarQube | Análise de código | Média |
| CodeCov | Relatório de cobertura | Média |
| Snyk | Segurança de dependências | Alta |

---

## 🚨 6. RISCOS IDENTIFICADOS

| ID | Risco | Impacto | Probabilidade | Mitigação |
|----|-------|---------|---------------|-----------|
| R01 | Cobertura insuficiente | Alto | Média | Priorizar testes críticos |
| R02 | Bugs em produção | Alto | Média | Testes de regressão completos |
| R03 | Performance inadequada | Médio | Baixa | Load tests antecipados |
| R04 | Vulnerabilidades de segurança | Crítico | Média | Pentest antes de produção |
| R05 | Prazo insuficiente | Alto | Alta | Priorização rigorosa |
| R06 | Falta de recursos | Médio | Média | Automatização máxima |

---

## ✅ 7. CHECKLIST DE ENTREGA

- [ ] Todos os casos de teste documentados
- [ ] Ambiente de testes configurado
- [ ] Dados de teste (fixtures) criados
- [ ] Testes unitários implementados
- [ ] Testes de integração implementados
- [ ] Testes E2E implementados
- [ ] Testes de API implementados
- [ ] Testes de segurança realizados
- [ ] Relatório de cobertura gerado
- [ ] Bugs críticos corrigidos
- [ ] Documentação de testes atualizada
- [ ] Pipeline CI/CD configurado
- [ ] Sign-off do stakeholder

---

**Aprovado por:** _________________  
**Data:** __/__/____  
**Assinatura:** _________________
