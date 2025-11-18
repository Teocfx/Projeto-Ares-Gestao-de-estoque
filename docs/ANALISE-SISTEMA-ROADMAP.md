# 📊 ARES - Análise do Sistema Atual e Roadmap

**Data:** 18 de Novembro de 2025
**Versão:** 1.0.0

---

## ✅ O que já está implementado

### 1. Infraestrutura Base
- ✅ Django 5.1.14 + Wagtail 7.2
- ✅ PostgreSQL (produção) / SQLite (dev)
- ✅ Webpack + SCSS + JavaScript modular
- ✅ Sistema de templates responsivo
- ✅ Autenticação via Keycloak/AllAuth
- ✅ Admin do Wagtail customizado (logo, cores)

### 2. Apps Django Existentes

#### ✅ **core/**
**Status:** Parcialmente implementado
- Models base: `TimeStampedModel`, `UserTrackingModel`, `SoftDeleteModel`
- `SiteSettings` (BaseSiteSetting): configurações do site
- `ApiSettings` (BaseSiteSetting): configurações de API
- Utils compartilhados

**Faltando:**
- Sistema de permissões granulares
- Auditoria automática
- Logs imutáveis

#### ⚠️ **autenticacao/**
**Status:** Básico implementado
- Login/Logout via Keycloak
- CustomUser (estende AbstractUser)
- Recuperação de senha

**Faltando:**
- Perfis (Representante Legal, Delegado, Operador, Auditor)
- MFA (autenticação multifator)
- Gerenciamento de dispositivos
- Histórico de login
- Bloqueio por tentativas malsucedidas

#### ⚠️ **dashboard/**
**Status:** Estrutura criada
**Faltando:**
- Dashboard Operacional completo
- Dashboard Gerencial (Legal/Delegado)
- Métricas e KPIs
- Gráficos interativos
- Alertas visuais

#### ⚠️ **produtos/**
**Status:** Estrutura básica
**Modelos esperados:**
- `Product`: SKU, nome, descrição, categoria, unidade, estoque min/atual, validade
- `Category`: nome, descrição
- `Unit`: nome (UN, KG, L)

**Faltando:**
- CRUD completo
- Controle por lote
- Rastreabilidade
- Atributos customizáveis
- Alertas de estoque

#### ⚠️ **movimentacoes/**
**Status:** Estrutura básica
**Modelos esperados:**
- `InventoryMovement`: produto, tipo (ENTRADA/SAIDA/AJUSTE), quantidade, documento, usuário
- `StockLocation`: nome, descrição

**Faltando:**
- Aprovação de movimentações críticas
- Anexar documentos fiscais
- Lançamento por lote
- Correção com auditoria
- Histórico detalhado

#### ⚠️ **relatorios/**
**Status:** Estrutura básica
**Faltando:**
- Relatórios de estoque
- Relatórios de movimentações
- Giro de estoque
- Perdas e vencimentos
- Custos consolidados
- Exportação (PDF, XLSX, CSV, JSON)

### 3. Frontend

#### ✅ **Temas (NOVO)**
- ✅ Sistema de variáveis CSS (_variables.scss)
- ✅ 3 temas implementados (default, dark, high-contrast)
- ✅ ThemeManager JavaScript
- ✅ Persistência em localStorage
- ✅ Atalho: Alt + T para alternar

#### ⚠️ **SCSS**
**Existente:**
- Estrutura básica em `frontend/scss/`
- Alguns componentes customizados

**Faltando:**
- Reorganizar para usar variáveis de tema
- Remover cores hardcoded
- Criar estrutura modular completa

#### ⚠️ **JavaScript**
**Existente:**
- Webpack configurado
- Alguns scripts básicos

**Faltando:**
- Componentes reutilizáveis
- Validações de formulário
- Interações avançadas

---

## ❌ O que precisa ser criado

### 1. **Módulo de Governança e Auditoria** (NOVO)
**Prioridade:** ALTA

#### Funcionalidades:
- [ ] Registro automático de todas as ações
- [ ] Logs imutáveis (append-only)
- [ ] Consultas por período/usuário/ação
- [ ] Exportação de auditoria (PDF/CSV)
- [ ] Trilha de alterações (quem, quando, o quê)
- [ ] Histórico de permissões

#### Tecnologias sugeridas:
- `django-simple-history` ou implementação custom
- Modelo `AuditLog` com campos: user, action, model, object_id, changes, timestamp, ip_address

---

### 2. **Sistema de Permissões Granulares** (NOVO)
**Prioridade:** ALTA

#### Perfis a criar:

##### **Representante Legal**
- Controle total do sistema
- Único que pode criar Delegados
- Acesso a todas as configurações
- Gerenciamento de dispositivos
- Auditoria completa

##### **Representante Delegado**
- Quase controle total (exceto remover Legal)
- Criar e editar Operadores
- Configurar alertas e regras
- Relatórios avançados
- Auditoria parcial

##### **Operador**
- Acesso limitado conforme permissões
- Consultas e movimentações básicas
- Sem acesso a configurações críticas
- Sem gerenciamento de usuários

##### **Auditor** (NOVO)
- Somente leitura em todos os módulos
- Acesso completo a auditoria
- Exportação de relatórios
- Sem capacidade de modificar dados

#### Implementação:
```python
# core/models.py
class PermissionProfile(models.Model):
    LEGAL = 'LEGAL'
    DELEGADO = 'DELEGADO'
    OPERADOR = 'OPERADOR'
    AUDITOR = 'AUDITOR'
    
    PROFILE_CHOICES = [...]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_type = models.CharField(max_length=20, choices=PROFILE_CHOICES)
    permissions = models.JSONField(default=dict)  # Permissões granulares
```

#### Permissões por módulo:
- `view_*`: Visualizar
- `add_*`: Criar
- `change_*`: Editar
- `delete_*`: Excluir
- `report_*`: Gerar relatórios
- `authorize_*`: Autorizar ações críticas
- `audit_*`: Acessar auditoria

---

### 3. **Módulo de Segurança** (NOVO)
**Prioridade:** MÉDIA-ALTA

#### Funcionalidades:
- [ ] Gerenciamento de dispositivos autorizados
- [ ] MFA opcional (SMS/Email/App)
- [ ] Bloqueio por tentativas malsucedidas
- [ ] Histórico de login (IP, dispositivo, localização)
- [ ] Assinaturas digitais de relatórios
- [ ] Políticas de senha
- [ ] Expiração de sessão configurável

#### Models:
```python
class AuthorizedDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_name = models.CharField(max_length=255)
    device_fingerprint = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)
    
class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField()
    failure_reason = models.CharField(max_length=255, blank=True)
```

---

### 4. **Módulo de Documentos Fiscais** (NOVO)
**Prioridade:** MÉDIA

#### Funcionalidades:
- [ ] Upload de NF-e, CF-e, outros documentos
- [ ] Classificação automática
- [ ] OCR opcional (pytesseract / AWS Textract)
- [ ] Associação com movimentações
- [ ] Histórico fiscal completo
- [ ] Validação de XML de NF-e

#### Models:
```python
class FiscalDocument(TimeStampedModel):
    DOC_TYPES = [
        ('NFE', 'Nota Fiscal Eletrônica'),
        ('CFE', 'Cupom Fiscal Eletrônico'),
        ('DANFE', 'DANFE'),
    ]
    
    movement = models.ForeignKey('movimentacoes.InventoryMovement', on_delete=models.CASCADE)
    doc_type = models.CharField(max_length=10, choices=DOC_TYPES)
    document_number = models.CharField(max_length=100)
    file = models.FileField(upload_to='fiscal_documents/')
    xml_file = models.FileField(upload_to='fiscal_xml/', blank=True)
    ocr_text = models.TextField(blank=True)
    validated = models.BooleanField(default=False)
```

---

### 5. **Sistema de Alertas Inteligentes** (NOVO)
**Prioridade:** ALTA

#### Tipos de alertas:
- [ ] **Validade**: Produtos próximos do vencimento
- [ ] **Estoque mínimo**: Abaixo do limite configurado
- [ ] **Estoque crítico**: Zerado
- [ ] **Movimentações suspeitas**: Padrões anormais
- [ ] **Giro lento**: Produtos parados há muito tempo
- [ ] **Ruptura de cadeia**: Falhas na rastreabilidade

#### Canais de notificação:
- [ ] Notificações push (Web Push API)
- [ ] Email automático
- [ ] Notificações internas (dashboard)
- [ ] SMS (opcional, via Twilio)
- [ ] Webhook para integrações

#### Models:
```python
class Alert(TimeStampedModel):
    ALERT_TYPES = [
        ('VALIDADE', 'Produto próximo do vencimento'),
        ('ESTOQUE_MIN', 'Estoque mínimo'),
        ('ESTOQUE_CRITICO', 'Estoque crítico'),
        ('SUSPEITA', 'Movimentação suspeita'),
        ('GIRO_LENTO', 'Giro lento'),
    ]
    
    SEVERITY = [
        ('LOW', 'Baixa'),
        ('MEDIUM', 'Média'),
        ('HIGH', 'Alta'),
        ('CRITICAL', 'Crítica'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY)
    product = models.ForeignKey('produtos.Product', on_delete=models.CASCADE, null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```

---

### 6. **Dashboards Diferenciados** (NOVO)
**Prioridade:** ALTA

#### Dashboard Operacional (todos os usuários)
- Valor total do estoque
- Itens cadastrados
- Produtos em alerta (crítico/baixo/OK)
- Últimas movimentações
- Próximos vencimentos

#### Dashboard Gerencial (Legal + Delegado)
- Custos totais
- Giro de estoque (ABC)
- Demonstrativos consolidados
- Análise de risco operacional
- Indicadores de performance (KPIs)
- Comparativos por período
- Previsão de demanda (opcional)

---

### 7. **Melhorias nos Módulos Existentes**

#### produtos/
- [ ] Controle por lote/batch
- [ ] Rastreabilidade completa
- [ ] Atributos customizáveis (JSON field)
- [ ] Histórico de alterações de preço
- [ ] Múltiplas localizações de estoque
- [ ] Produtos compostos (kits)

#### movimentacoes/
- [ ] Aprovação de movimentações críticas (workflow)
- [ ] Anexar múltiplos documentos
- [ ] Lançamento em lote (importação CSV/Excel)
- [ ] Correção de movimentações com justificativa
- [ ] Movimentações recorrentes agendadas

#### relatorios/
- [ ] Relatórios customizáveis
- [ ] Agendamento de relatórios
- [ ] Envio automático por email
- [ ] Templates de relatório
- [ ] Filtros avançados
- [ ] Gráficos interativos (Chart.js / Plotly)

---

## 🎯 Roadmap Sugerido

### **Sprint 1: Segurança e Permissões** (2-3 semanas)
1. Sistema de permissões granulares
2. Perfis de usuário (Legal, Delegado, Operador, Auditor)
3. Gerenciamento de dispositivos
4. MFA básico

### **Sprint 2: Auditoria e Logs** (2 semanas)
1. Módulo de auditoria completo
2. Logs imutáveis
3. Histórico de alterações
4. Consultas e exportações

### **Sprint 3: Alertas e Notificações** (2 semanas)
1. Sistema de alertas inteligentes
2. Notificações push
3. Email automático
4. Dashboard de alertas

### **Sprint 4: Dashboards** (2-3 semanas)
1. Dashboard Operacional completo
2. Dashboard Gerencial
3. Gráficos e KPIs
4. Exportações

### **Sprint 5: Documentos Fiscais** (2 semanas)
1. Upload e gerenciamento
2. OCR opcional
3. Validação de NF-e
4. Associação com movimentações

### **Sprint 6: Melhorias e Polimento** (2 semanas)
1. Controle por lote
2. Rastreabilidade
3. Relatórios avançados
4. Testes E2E

---

## 📝 Próximos Passos Imediatos

1. ✅ **Reorganizar SCSS** para usar variáveis de tema
2. ✅ **Integrar theme-manager.js** no template base
3. [ ] **Auditar apps existentes** (verificar models, views, templates)
4. [ ] **Criar sistema de permissões** (models + mixins)
5. [ ] **Implementar dashboard operacional** básico

---

## 📚 Documentação Necessária

- [ ] Guia de estilo (cores, tipografia, componentes)
- [ ] Manual de permissões
- [ ] Guia de auditoria
- [ ] Manual do usuário (por perfil)
- [ ] Documentação de API (se implementar)

---

**Desenvolvido para o Projeto ARES** 📦
*Sistema Empresarial de Gestão de Estoque*
