# 🏷️ Versionamento e Estratégia de Releases - Sistema ARES

**Projeto:** Sistema de Gestão de Estoque ARES  
**Data:** 26/11/2025  
**Versão Atual:** 1.0.0  
**Responsável:** Tech Lead

---

## 1. RESUMO EXECUTIVO

Este documento estabelece a política de versionamento, estratégia de releases, procedimentos de deploy e gestão de mudanças para o Sistema ARES.

**Estratégia Adotada:** Semantic Versioning 2.0.0

---

## 2. SEMANTIC VERSIONING

### 2.1. Formato

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

Exemplos:
1.0.0          - Release estável
1.2.3          - Release com melhorias
2.0.0          - Breaking changes
1.0.0-alpha.1  - Pre-release alpha
1.0.0-beta.2   - Pre-release beta
1.0.0-rc.1     - Release candidate
1.0.0+20250126 - Build metadata
```

### 2.2. Incremento de Versão

| Tipo | Quando Incrementar | Exemplo |
|------|-------------------|---------|
| **MAJOR** | Breaking changes (incompatibilidade) | 1.5.2 → 2.0.0 |
| **MINOR** | Novas features (compatível) | 1.5.2 → 1.6.0 |
| **PATCH** | Bug fixes (compatível) | 1.5.2 → 1.5.3 |

### 2.3. Regras de Incremento

#### MAJOR (X.0.0)
Incrementar quando:
- ❌ Remover endpoints/funcionalidades da API
- ❌ Mudar schema de banco incompatível
- ❌ Alterar comportamento de features existentes
- ❌ Mudar estrutura de responses da API
- ❌ Remover campos de modelos

**Exemplo:**
```python
# v1.x.x - Campo obrigatório
class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50)

# v2.0.0 - Remoção de campo (BREAKING)
class Product(models.Model):
    name = models.CharField(max_length=100)
    # sku removido - BREAKING CHANGE
```

#### MINOR (x.Y.0)
Incrementar quando:
- ✅ Adicionar novos endpoints à API
- ✅ Adicionar novos campos opcionais
- ✅ Adicionar novas features
- ✅ Melhorias de performance
- ✅ Deprecar funcionalidades (sem remover)

**Exemplo:**
```python
# v1.5.0 - Novo campo opcional
class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50)
    barcode = models.CharField(max_length=13, null=True)  # NOVO
```

#### PATCH (x.y.Z)
Incrementar quando:
- 🐛 Corrigir bugs
- 🔒 Patches de segurança
- 📝 Melhorias de documentação
- 🎨 Ajustes de UI/UX
- ⚡ Otimizações internas

**Exemplo:**
```python
# v1.5.2 - Bug fix
def calculate_total(self):
    # ANTES (bug): return self.price * self.quantity + 10
    # DEPOIS (fix): return self.price * self.quantity  # FIX
    return self.price * self.quantity
```

---

## 3. PRE-RELEASES

### 3.1. Tipos

| Tipo | Propósito | Público |
|------|-----------|---------|
| **alpha** | Desenvolvimento ativo | Interno (devs) |
| **beta** | Teste de features | Selecionado (beta testers) |
| **rc** | Release candidate | Staging/UAT |

### 3.2. Numeração

```
1.0.0-alpha.1  → 1.0.0-alpha.2  → 1.0.0-alpha.3
              ↓
         1.0.0-beta.1   → 1.0.0-beta.2
              ↓
         1.0.0-rc.1     → 1.0.0-rc.2
              ↓
            1.0.0 (STABLE)
```

### 3.3. Quando Usar

```python
# Alpha - Features incompletas
VERSION = "2.0.0-alpha.1"
# - Nova API de relatórios (50% completa)
# - Sistema de notificações (em progresso)

# Beta - Features completas, testes em progresso
VERSION = "2.0.0-beta.1"
# - Todas as features implementadas
# - Testes em andamento

# RC - Pronto para produção, validação final
VERSION = "2.0.0-rc.1"
# - Todos os testes passaram
# - Aguardando aprovação final
```

---

## 4. ESTRATÉGIA DE BRANCHES

### 4.1. Git Flow Adaptado

```
main (production)
├── develop (integration)
│   ├── feature/001/nova-api
│   ├── feature/002/dashboard-v2
│   └── feature/003/windows
├── release/1.1.0
├── hotfix/1.0.1
└── support/1.x (LTS)
```

### 4.2. Descrição das Branches

| Branch | Propósito | Deploy | Proteção |
|--------|-----------|--------|----------|
| **main** | Produção estável | ✅ Auto | 🔒 Protected |
| **develop** | Integração | ✅ Staging | 🔒 Protected |
| **feature/** | Desenvolvimento | ❌ Manual | ⚠️ Revisar |
| **release/** | Preparação release | ✅ UAT | 🔒 Protected |
| **hotfix/** | Correções urgentes | ✅ Production | ⚠️ Revisar |
| **support/** | LTS maintenance | ✅ LTS env | 🔒 Protected |

### 4.3. Fluxo de Trabalho

#### Nova Feature
```bash
# 1. Criar branch de feature
git checkout develop
git pull origin develop
git checkout -b feature/004/nova-funcionalidade

# 2. Desenvolver e commitar
git add .
git commit -m "feat(produtos): add barcode scanner"

# 3. Push e Pull Request
git push origin feature/004/nova-funcionalidade
# Abrir PR: feature/004 → develop

# 4. Após aprovação e merge
git checkout develop
git pull origin develop
git branch -d feature/004/nova-funcionalidade
```

#### Release
```bash
# 1. Criar branch de release
git checkout develop
git checkout -b release/1.1.0

# 2. Atualizar versão
echo "1.1.0" > VERSION
git commit -am "chore(release): bump version to 1.1.0"

# 3. Deploy em UAT e testes
# ... testes ...

# 4. Merge em main e develop
git checkout main
git merge --no-ff release/1.1.0
git tag -a v1.1.0 -m "Release 1.1.0"

git checkout develop
git merge --no-ff release/1.1.0

# 5. Push
git push origin main develop --tags
git branch -d release/1.1.0
```

#### Hotfix
```bash
# 1. Criar branch de hotfix
git checkout main
git checkout -b hotfix/1.0.1

# 2. Corrigir bug
# ... fix ...
git commit -am "fix(auth): corrige validação de token"

# 3. Merge em main e develop
git checkout main
git merge --no-ff hotfix/1.0.1
git tag -a v1.0.1 -m "Hotfix 1.0.1"

git checkout develop
git merge --no-ff hotfix/1.0.1

# 4. Push
git push origin main develop --tags
git branch -d hotfix/1.0.1
```

---

## 5. CONVENTIONAL COMMITS

### 5.1. Formato

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### 5.2. Tipos

| Tipo | Descrição | Bump |
|------|-----------|------|
| **feat** | Nova feature | MINOR |
| **fix** | Bug fix | PATCH |
| **docs** | Documentação | - |
| **style** | Formatação | - |
| **refactor** | Refatoração | - |
| **perf** | Performance | PATCH |
| **test** | Testes | - |
| **chore** | Manutenção | - |
| **ci** | CI/CD | - |
| **build** | Build system | - |
| **revert** | Reverter commit | * |

### 5.3. Scopes

| Scope | Módulo |
|-------|--------|
| **auth** | autenticacao/ |
| **produtos** | produtos/ |
| **movimentos** | movimentacoes/ |
| **relatorios** | relatorios/ |
| **api** | API REST |
| **core** | core/ |
| **ui** | Frontend |
| **db** | Database |
| **config** | Configurações |

### 5.4. Exemplos

```bash
# Feature (MINOR)
git commit -m "feat(produtos): add barcode scanner support"

# Bug fix (PATCH)
git commit -m "fix(auth): corrige validação de refresh token"

# Breaking change (MAJOR)
git commit -m "feat(api)!: remove endpoint /api/v1/old-products/

BREAKING CHANGE: endpoint /api/v1/old-products/ foi removido.
Use /api/v1/products/ em seu lugar."

# Performance (PATCH)
git commit -m "perf(produtos): otimiza query de listagem com select_related"

# Documentation
git commit -m "docs(api): adiciona exemplos de curl para autenticação"

# Multiple changes
git commit -m "chore: atualiza dependências

- Django 4.2.8 → 4.2.16
- DRF 3.14.0 → 3.16.1
- Pillow 10.1.0 → 10.4.0"
```

---

## 6. CHANGELOG

### 6.1. Formato

Baseado em [Keep a Changelog](https://keepachangelog.com/).

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Feature em desenvolvimento

## [1.1.0] - 2025-12-15
### Added
- Barcode scanner para produtos
- Exportação de relatórios em Excel
- Dashboard de analytics avançado

### Changed
- Interface do cadastro de produtos melhorada
- Performance de listagem otimizada

### Fixed
- Correção de bug no cálculo de estoque
- Fix de validação de datas

### Deprecated
- Endpoint `/api/v1/old-products/` (será removido em 2.0.0)

## [1.0.1] - 2025-11-30
### Fixed
- Correção de validação de refresh token
- Fix de SQL injection em relatórios

### Security
- Atualização de dependências vulneráveis

## [1.0.0] - 2025-11-26
### Added
- ACL system completo
- Auditoria de ações
- API REST com JWT
- Upload de imagens
- Relatórios em PDF
- Theme switcher
- Sistema de movimentações
- Dashboard analytics

[Unreleased]: https://github.com/user/ares/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/user/ares/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/user/ares/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/user/ares/releases/tag/v1.0.0
```

### 6.2. Categorias

| Categoria | Descrição |
|-----------|-----------|
| **Added** | Novas features |
| **Changed** | Mudanças em features existentes |
| **Deprecated** | Features que serão removidas |
| **Removed** | Features removidas |
| **Fixed** | Bug fixes |
| **Security** | Correções de segurança |

### 6.3. Automação

```bash
# Gerar changelog automaticamente
npm install -g conventional-changelog-cli

# Gerar changelog
conventional-changelog -p angular -i CHANGELOG.md -s

# Gerar changelog para release
conventional-changelog -p angular -i CHANGELOG.md -s -r 0
```

---

## 7. TAGS E RELEASES

### 7.1. Convenção de Tags

```bash
# Formato
v<MAJOR>.<MINOR>.<PATCH>[-PRERELEASE]

# Exemplos
v1.0.0
v1.1.0
v1.1.1
v2.0.0-alpha.1
v2.0.0-beta.1
v2.0.0-rc.1
```

### 7.2. Criar Tag

```bash
# Tag anotada (recomendado)
git tag -a v1.1.0 -m "Release 1.1.0

Features:
- Barcode scanner
- Excel export
- Analytics dashboard

Bug Fixes:
- Stock calculation fix
- Date validation fix"

# Push tag
git push origin v1.1.0

# Push todas as tags
git push origin --tags
```

### 7.3. Release Notes

Template para GitHub Releases:

```markdown
## Sistema ARES v1.1.0

**Data de Release:** 15/12/2025  
**Tipo:** Minor Release

### 🎉 Novas Features

- **Barcode Scanner** (#42)
  - Leitura de códigos de barras para produtos
  - Suporte para EAN-13, Code 128, QR Code
  
- **Exportação para Excel** (#45)
  - Relatórios em formato XLSX
  - Múltiplas planilhas por arquivo

- **Dashboard Analytics** (#48)
  - Gráficos interativos
  - Filtros avançados
  - Exportação de gráficos

### 🔄 Melhorias

- Interface de cadastro de produtos reformulada
- Performance de listagens otimizada (30% mais rápido)
- Validações de formulários melhoradas

### 🐛 Bug Fixes

- Correção de cálculo de estoque em movimentações (#52)
- Fix de validação de datas em relatórios (#54)
- Correção de exibição de avatar no header (#56)

### 📦 Dependências

- Django 4.2.8 → 4.2.16
- DRF 3.14.0 → 3.16.1
- Pillow 10.1.0 → 10.4.0

### 📚 Documentação

- Adicionado guia de integração com sistemas externos
- Atualizado diagrama de arquitetura
- Novos exemplos de API

### ⚠️ Deprecations

- Endpoint `/api/v1/old-products/` será removido em v2.0.0
  - Use `/api/v1/products/` em seu lugar

### 🔐 Segurança

- Atualização de dependências com vulnerabilidades conhecidas
- Correção de possível SQL injection em relatórios

### 📥 Download

- [Source code (zip)](https://github.com/user/ares/archive/refs/tags/v1.1.0.zip)
- [Source code (tar.gz)](https://github.com/user/ares/archive/refs/tags/v1.1.0.tar.gz)

### 📝 Full Changelog

[v1.0.1...v1.1.0](https://github.com/user/ares/compare/v1.0.1...v1.1.0)

---

**Docker:**
```bash
docker pull ghcr.io/user/ares:1.1.0
```

**Migration:**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

**Breaking Changes:** None
```

---

## 8. CICLO DE RELEASES

### 8.1. Calendário

| Release | Frequência | Conteúdo |
|---------|------------|----------|
| **Major** | Anual | Breaking changes, grandes features |
| **Minor** | Mensal | Novas features, melhorias |
| **Patch** | Semanal | Bug fixes, segurança |
| **Hotfix** | Sob demanda | Correções urgentes |

### 8.2. Roadmap de Versões

```
2025 Q4:
├── v1.0.0 (26/11) ✅ - Release inicial
├── v1.0.1 (30/11) ⏳ - Hotfix segurança
├── v1.1.0 (15/12) 📅 - Barcode + Excel
└── v1.2.0 (30/12) 📅 - Mobile responsivo

2026 Q1:
├── v1.3.0 (15/01) 📅 - Integrações ERP
├── v1.4.0 (15/02) 📅 - BI/Analytics
└── v2.0.0 (15/03) 📅 - Nova API v2

2026 Q2+:
├── v2.1.0 (15/04) 📅 - Multi-tenancy
├── v2.2.0 (15/05) 📅 - App mobile
└── v3.0.0 (Q4) 📅 - Microservices
```

### 8.3. Suporte de Versões

| Versão | Status | Suporte até | Tipo |
|--------|--------|-------------|------|
| 3.x | Futuro | - | - |
| 2.x | Futuro | - | Standard |
| **1.x** | **Current** | **15/03/2027** | **LTS** |
| 0.x | EOL | 26/11/2025 | Beta |

**LTS (Long Term Support):** 24 meses de suporte  
**Standard:** 12 meses de suporte

---

## 9. PROCESSO DE RELEASE

### 9.1. Checklist de Release

#### Preparação (1 semana antes)
- [ ] Code freeze na branch develop
- [ ] Criar branch release/X.Y.Z
- [ ] Atualizar VERSION file
- [ ] Atualizar CHANGELOG.md
- [ ] Atualizar documentação
- [ ] Gerar release notes

#### Testes (3-5 dias)
- [ ] Executar suite completa de testes
- [ ] Testes de regressão
- [ ] Testes de performance
- [ ] Testes de segurança
- [ ] UAT (User Acceptance Testing)

#### Deploy
- [ ] Backup do banco de produção
- [ ] Deploy em staging
- [ ] Smoke tests em staging
- [ ] Deploy em produção
- [ ] Smoke tests em produção
- [ ] Monitoramento ativo (24h)

#### Pós-Release
- [ ] Merge release → main
- [ ] Merge release → develop
- [ ] Criar tag vX.Y.Z
- [ ] Criar GitHub Release
- [ ] Publicar release notes
- [ ] Notificar stakeholders
- [ ] Atualizar documentação externa

### 9.2. Scripts de Automação

#### Script: `scripts/release.sh`
```bash
#!/bin/bash
# Release automation script

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh <version>"
    exit 1
fi

echo "🚀 Iniciando release $VERSION"

# 1. Verificar branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "develop" ]; then
    echo "❌ Erro: Execute na branch develop"
    exit 1
fi

# 2. Atualizar código
git pull origin develop

# 3. Criar branch de release
git checkout -b "release/$VERSION"

# 4. Atualizar VERSION
echo "$VERSION" > VERSION

# 5. Atualizar __init__.py
sed -i "s/__version__ = .*/__version__ = '$VERSION'/" siteares/__init__.py

# 6. Gerar changelog
conventional-changelog -p angular -i CHANGELOG.md -s

# 7. Commit
git add VERSION CHANGELOG.md siteares/__init__.py
git commit -m "chore(release): bump version to $VERSION"

# 8. Push
git push origin "release/$VERSION"

echo "✅ Branch release/$VERSION criada"
echo "📝 Próximos passos:"
echo "  1. Testar em staging"
echo "  2. Merge em main: git checkout main && git merge --no-ff release/$VERSION"
echo "  3. Tag: git tag -a v$VERSION -m 'Release $VERSION'"
echo "  4. Push: git push origin main --tags"
echo "  5. Merge em develop: git checkout develop && git merge --no-ff release/$VERSION"
```

#### Script: `scripts/hotfix.sh`
```bash
#!/bin/bash
# Hotfix automation script

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/hotfix.sh <version>"
    exit 1
fi

echo "🔥 Iniciando hotfix $VERSION"

# 1. Criar branch de hotfix
git checkout main
git pull origin main
git checkout -b "hotfix/$VERSION"

# 2. Atualizar VERSION
echo "$VERSION" > VERSION

# 3. Atualizar __init__.py
sed -i "s/__version__ = .*/__version__ = '$VERSION'/" siteares/__init__.py

echo "✅ Branch hotfix/$VERSION criada"
echo "📝 Próximos passos:"
echo "  1. Corrigir o bug"
echo "  2. Commit: git commit -am 'fix: descrição'"
echo "  3. Merge em main: git checkout main && git merge --no-ff hotfix/$VERSION"
echo "  4. Tag: git tag -a v$VERSION -m 'Hotfix $VERSION'"
echo "  5. Merge em develop: git checkout develop && git merge --no-ff hotfix/$VERSION"
```

---

## 10. VERSIONAMENTO DE API

### 10.1. URL Versioning

```python
# Atual: URL Versioning
urlpatterns = [
    path('api/v1/', include('siteares.api_urls')),
    path('api/v2/', include('siteares.api_v2_urls')),  # Futuro
]
```

### 10.2. Deprecação de API

```python
# API v1 - Deprecated endpoint
@api_view(['GET'])
@deprecated(reason="Use /api/v2/products/ instead", version="2.0.0")
def old_product_list(request):
    """
    Deprecated: This endpoint will be removed in v2.0.0.
    Use /api/v2/products/ instead.
    """
    return Response(...)
```

### 10.3. Compatibilidade

| Versão API | Suporte até | Status |
|------------|-------------|--------|
| v3 | - | Futuro |
| **v2** | **15/03/2027** | **Planejada** |
| **v1** | **15/03/2026** | **Atual** |

---

## 11. DOCUMENTAÇÃO DE VERSÃO

### 11.1. VERSION File

```
# VERSION
1.0.0
```

### 11.2. __init__.py

```python
# siteares/__init__.py
__version__ = '1.0.0'
__version_info__ = (1, 0, 0)
__api_version__ = 'v1'

def get_version():
    """Retorna versão completa."""
    return __version__
```

### 11.3. settings.py

```python
# settings/base.py
from siteares import __version__, __api_version__

VERSION = __version__
API_VERSION = __api_version__

# Expor no template context
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ...
                lambda request: {
                    'VERSION': VERSION,
                    'API_VERSION': API_VERSION,
                },
            ],
        },
    },
]
```

### 11.4. API Response

```python
# core/views.py
@api_view(['GET'])
def api_version(request):
    """Retorna informações de versão."""
    return Response({
        'version': settings.VERSION,
        'api_version': settings.API_VERSION,
        'build_date': '2025-11-26',
        'commit': 'a9eb109',
    })
```

---

## 12. MIGRATIONS

### 12.1. Versionamento de Migrations

```python
# produtos/migrations/0001_initial.py
# Version: 1.0.0

# produtos/migrations/0002_product_barcode.py
# Version: 1.1.0

# produtos/migrations/0003_remove_product_old_field.py
# Version: 2.0.0 (BREAKING)
```

### 12.2. Rollback Strategy

```bash
# Rollback para versão anterior
python manage.py migrate produtos 0001

# Verificar status
python manage.py showmigrations

# Rollback completo
python manage.py migrate produtos zero
```

---

## 13. CONCLUSÃO

### 13.1. Resumo da Estratégia

✅ **Semantic Versioning 2.0.0**  
✅ **Git Flow adaptado**  
✅ **Conventional Commits**  
✅ **Changelog automatizado**  
✅ **Releases mensais**  
✅ **LTS de 24 meses**

### 13.2. Próximos Passos

1. **Imediato:**
   - Criar v1.0.0 tag
   - Publicar primeira release no GitHub
   - Configurar CI/CD com versionamento automático

2. **Curto Prazo:**
   - Automatizar geração de changelog
   - Implementar semantic-release
   - Configurar branch protection rules

3. **Médio Prazo:**
   - Planejar roadmap v2.0.0
   - Definir estratégia de deprecação
   - Implementar versionamento de API v2

---

**Preparado por:** Tech Lead  
**Aprovado por:** Gerente de Projeto  
**Data:** 26/11/2025  
**Próxima Revisão:** Trimestral
