# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-11-26

### Added

#### Sistema de Controle de Acesso (ACL)
- Sistema completo de perfis de usuário com permissões granulares
- 5 perfis pré-configurados: Admin, Diretor, Representante Legal, Funcionário, Delegado
- 25+ permissões específicas por módulo
- Decorators `@require_perfil` para proteção de views
- Permission classes para DRF
- Interface de gerenciamento de perfis e permissões

#### Sistema de Auditoria
- Auditoria automática de todas as operações CRUD
- Registro de criação, edição e deleção de registros
- Campos auditados: user, timestamp, IP, user agent, modelo, objeto
- Signals pré-configurados para todos os modelos
- Views de consulta de logs com filtros avançados
- API de logs com estatísticas

#### Componentes HTML Reutilizáveis
- Sistema de blocos Wagtail para páginas dinâmicas
- 10+ componentes: cards, botões, alertas, badges, tabelas, forms
- Suporte a variantes (primary, secondary, success, danger, warning, info)
- Tamanhos configuráveis (sm, md, lg, xl)
- Template tags customizadas
- Documentação completa de uso

#### Sistema de Logs UI
- Interface de visualização de logs de auditoria
- Filtros por usuário, modelo, ação, período
- Timeline de eventos
- Detalhes de mudanças (before/after)
- Exportação de logs
- Dashboard de estatísticas

#### HomePage com Wagtail CMS
- Página inicial editável via Wagtail admin
- Hero section dinâmico
- Blocos de features
- Seção de depoimentos
- Call-to-action configurável
- SEO otimizado
- Preview ao vivo

#### Sistema de Upload de Imagens
- Upload de imagens para produtos
- Validação de tipo e tamanho
- Geração de thumbnails automática
- Compressão de imagens
- Organização por data
- Suporte a múltiplas imagens

#### Theme Switcher
- Alternância entre tema claro e escuro
- Persistência da preferência em localStorage
- Suporte a preferência do sistema (prefers-color-scheme)
- Transições suaves
- Ícones animados
- Compatibilidade completa com todos os componentes

#### API REST Completa
- Django REST Framework 3.16.1
- Autenticação JWT (access 2h, refresh 7d)
- Documentação Swagger/OpenAPI em /api/v1/docs/
- 30+ endpoints RESTful
- Versionamento de API (v1)
- Rate limiting (100/h anon, 1000/h auth)
- CORS configurado
- Filtros avançados (django-filter)
- Paginação (20 itens/página)
- Ordenação personalizável
- Serializers com validação
- ViewSets com custom actions
- Permissions integradas com ACL

#### Endpoints de Produtos
- CRUD completo de categorias
- CRUD completo de unidades
- CRUD completo de produtos
- Ações: low_stock, expired, stats, movements
- Filtros: name, sku, category, low_stock, expired
- Busca por texto completo

#### Endpoints de Movimentações
- Listagem de movimentações (read-only)
- Criação de movimentações (ENTRADA/SAÍDA)
- Bulk create (até 100 registros)
- Ações: stats, by_product, by_type
- Filtros: product, type, user, date range, document
- Imutabilidade (sem PUT/PATCH/DELETE)

#### Endpoints de Usuários e Perfis
- CRUD de usuários
- Endpoint /me/ para dados do usuário atual
- CRUD de perfis
- Estatísticas por perfil
- Logs de auditoria por usuário
- Logs por modelo

#### Documentação
- API-REST.md com 600+ linhas
- Exemplos em Python, JavaScript, cURL
- Guia de autenticação JWT
- Matriz de permissões
- Filtros e ordenação
- Rate limiting
- Tratamento de erros
- Status codes

### Changed
- Reorganização completa da estrutura de templates
- Migração de CSS para SCSS com variáveis
- Atualização de dependências para versões mais recentes
- Melhoria na performance de queries com select_related/prefetch_related
- Otimização de assets com Webpack

### Fixed
- Correção de N+1 queries em listagens
- Fix de validação de datas em movimentações
- Correção de permissões em views sensíveis
- Fix de CORS para requisições externas

### Security
- Implementação de HTTPS em produção
- CSRF protection em todos os formulários
- SQL injection prevention via ORM
- XSS prevention via template escaping
- Secure cookies (SECURE=True em produção)
- HSTS headers configurados
- Content-Type nosniff
- X-Frame-Options: DENY
- JWT com tokens de curta duração

### Documentation
- README.md atualizado com guia completo
- PLANO-TESTES.md com 117 casos de teste
- METRICAS-ESTIMATIVAS.md com análise completa
- REVISAO-TECNICA.md com avaliação de qualidade
- VERSIONAMENTO.md com estratégia de releases
- API-REST.md com documentação completa
- STATUS-PROJETO.md atualizado para 100%
- Docstrings em 60% das funções

### Testing
- Estrutura de testes com pytest configurada
- 26 testes de API implementados
- Fixtures para testes (users, products, categories)
- Test plan com 117 casos documentados
- Coverage target: 80%

### Infrastructure
- Dockerfile para produção
- Dockerfile.dev para desenvolvimento
- docker-compose.yml configurado
- Makefile com comandos úteis
- Configurações separadas por ambiente
- PostgreSQL como banco principal
- WhiteNoise para servir arquivos estáticos
- Gunicorn como WSGI server

[Unreleased]: https://github.com/user/ares/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/user/ares/releases/tag/v1.0.0
