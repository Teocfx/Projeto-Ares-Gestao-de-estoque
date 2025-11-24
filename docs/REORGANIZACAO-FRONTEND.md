# 🎨 Plano de Reorganização Frontend ARES

## 📋 Situação Atual

### Problemas Identificados:
1. ❌ **Duplicação de variáveis**: `variables.scss` (antigo) e `_variables.scss` (novo com temas)
2. ❌ **Styles inline em templates**: `admin_base.html`, `base.html`, `erro_base.html`
3. ❌ **Scripts inline em templates**: `base.html`
4. ❌ **Falta estrutura modular**: Apps não têm pastas SCSS dedicadas
5. ❌ **Theme manager não integrado**: JavaScript criado mas não conectado

---

## 🎯 Estratégia de Reorganização

### Fase 1: Consolidar Variáveis SCSS
**Objetivo**: Um único arquivo de variáveis que funciona com temas

#### Estrutura Final:
```
frontend/scss/
├── _variables.scss         ← CONSOLIDADO (tema + cores antigas)
├── _mixins.scss            ← Mixins reutilizáveis
├── _themes.scss            ← Estilos base que usam variáveis
├── _utilities.scss         ← Classes utilitárias
├── main.scss               ← Importa tudo na ordem correta
```

#### Ações:
- [ ] Mesclar `variables.scss` → `_variables.scss`
- [ ] Converter cores hardcoded para CSS custom properties
- [ ] Manter compatibilidade com SCSS antigo ($color-primary, etc.)
- [ ] Extrair mixins para `_mixins.scss`

---

### Fase 2: Modularizar por App
**Objetivo**: Cada app Django tem seu próprio diretório SCSS

#### Estrutura Final:
```
frontend/scss/
├── core/
│   ├── _index.scss         ← Importa todos os partials do core
│   ├── _layout.scss
│   ├── _components.scss
│   ├── _filtros.scss
│   └── _compartilhamento.scss
├── dashboard/
│   ├── _index.scss
│   ├── _dashboard.scss
│   └── _widgets.scss
├── produtos/
│   ├── _index.scss
│   ├── _produtos-list.scss
│   └── _produtos-form.scss
├── movimentacoes/
│   ├── _index.scss
│   └── _movimentacoes.scss
├── relatorios/
│   ├── _index.scss
│   └── _relatorios.scss
├── autenticacao/
│   ├── _index.scss
│   └── _login.scss
├── admin/
│   ├── _wagtail-custom.scss  ← Move styles do admin_base.html
│   └── _django-admin.scss
```

#### Ações:
- [ ] Criar pastas para cada app
- [ ] Mover styles existentes para os respectivos apps
- [ ] Criar `_index.scss` em cada pasta (barril de exportação)

---

### Fase 3: Limpar Templates (Remover Inline Styles/Scripts)
**Objetivo**: Zero `<style>` e `<script>` inline nos templates

#### Templates a Limpar:

##### 1. `siteares/templates/wagtailadmin/admin_base.html`
**Problema**: 150+ linhas de CSS inline
**Solução**:
- [ ] Criar `frontend/scss/admin/_wagtail-custom.scss`
- [ ] Mover TODO o CSS inline para lá
- [ ] Usar variáveis de tema (`var(--color-primary)`)
- [ ] Template final: apenas `{% load static %}` + `<link>`

##### 2. `siteares/templates/wagtailadmin/base.html`
**Problema**: Styles inline para logo
**Solução**:
- [ ] Mover para `_wagtail-custom.scss`
- [ ] Remover `<style>` block completamente

##### 3. `siteares/templates/base.html`
**Problema**: Scripts inline
**Solução**:
- [ ] Identificar o que o script faz
- [ ] Criar arquivo JS modular
- [ ] Adicionar ao webpack entry points

##### 4. `siteares/templates/errors/erro_base.html`
**Problema**: Styles inline para página de erro
**Solução**:
- [ ] Criar `frontend/scss/core/_errors.scss`
- [ ] Mover styles inline
- [ ] Importar no main.scss

---

### Fase 4: Integrar Theme Manager
**Objetivo**: Sistema de troca de temas funcionando end-to-end

#### Ações:
- [ ] Atualizar `webpack.config.js` para incluir `theme-manager.js`
- [ ] Adicionar script no `base.html`:
  ```html
  <script src="{% static 'js/theme-manager.js' %}"></script>
  ```
- [ ] Criar widget de seleção de tema no Wagtail admin
- [ ] Adicionar botão de tema no header do site público
- [ ] Testar persistência (localStorage)
- [ ] Testar alternância: Alt + T

---

### Fase 5: Webpack e Build Process
**Objetivo**: Build otimizado e organizado

#### `webpack.config.js` atualizado:
```javascript
entry: {
  main: ['./frontend/js/index.js', './frontend/scss/main.scss'],
  'theme-manager': './frontend/js/theme-manager.js',
  admin: './frontend/scss/admin/_wagtail-custom.scss'
}
```

#### Ações:
- [ ] Verificar webpack.config.js atual
- [ ] Adicionar entry points
- [ ] Configurar CSS extraction
- [ ] Testar build: `npm run build`
- [ ] Verificar bundles gerados

---

## 📂 Estrutura Final Desejada

```
frontend/
├── bundles/                  ← Arquivos compilados (gerados)
│   ├── main.js
│   ├── theme-manager.js
│   ├── styles.css
│   └── admin.css
├── js/
│   ├── index.js             ← Entry point principal
│   ├── theme-manager.js     ✅ Já criado
│   ├── components/
│   │   ├── modal.js
│   │   ├── alerts.js
│   │   └── forms.js
│   ├── dashboard/
│   ├── produtos/
│   └── movimentacoes/
├── scss/
│   ├── main.scss            ← Importa tudo
│   ├── _variables.scss      ✅ Consolidado (temas)
│   ├── _mixins.scss         ← Mixins reutilizáveis
│   ├── _themes.scss         ✅ Já criado
│   ├── _utilities.scss      ← Classes utilitárias
│   ├── core/
│   ├── dashboard/
│   ├── produtos/
│   ├── movimentacoes/
│   ├── relatorios/
│   ├── autenticacao/
│   └── admin/
│       ├── _wagtail-custom.scss
│       └── _django-admin.scss
└── img/
    └── Logo.svg             ✅ Já existe
```

---

## 🔄 Ordem de Execução

### Sprint Reorganização Frontend (1 semana)

#### Dia 1-2: Variáveis e Mixins
1. ✅ Criar `_variables.scss` com temas
2. Mesclar variáveis antigas
3. Criar `_mixins.scss`
4. Testar compatibilidade

#### Dia 3-4: Modularização
1. Criar estrutura de pastas por app
2. Mover arquivos existentes
3. Criar `_index.scss` em cada pasta
4. Atualizar `main.scss`

#### Dia 5: Limpar Templates
1. Extrair styles inline → SCSS
2. Extrair scripts inline → JS
3. Testar páginas

#### Dia 6: Integração Theme Manager
1. Configurar webpack
2. Adicionar aos templates
3. Criar widgets de seleção
4. Testar todos os temas

#### Dia 7: Testes e Ajustes
1. Build completo
2. Testes em diferentes browsers
3. Validação de acessibilidade
4. Correções finais

---

## 🎨 Padrão de Migração de Cores

### Antes (Hardcoded):
```scss
.button {
  background-color: #30599b;
  color: #ffffff;
}
```

### Depois (Com Tema):
```scss
.button {
  background-color: var(--color-primary);
  color: var(--text-inverse);
}
```

### Com Fallback SCSS (Compatibilidade):
```scss
// Mantém variável SCSS para compatibilidade
$color-primary: var(--color-primary);

.button {
  background-color: $color-primary; // Usa var CSS via SCSS var
}
```

---

## ✅ Checklist de Validação

### Após cada mudança:
- [ ] Build do webpack sem erros
- [ ] Página carrega corretamente
- [ ] Tema default aplicado
- [ ] Tema dark funciona
- [ ] Tema high-contrast funciona
- [ ] Atalho Alt+T alterna temas
- [ ] localStorage persiste preferência
- [ ] Zero console errors
- [ ] Zero styles/scripts inline

---

## 📝 Convenções de Código

### Nomenclatura:
- **CSS Custom Properties**: `--color-primary`, `--spacing-md`
- **Variáveis SCSS**: `$color-primary` (mapeia para custom property)
- **Mixins**: `@mixin button-variant($color)`
- **Classes**: `.btn-primary`, `.card-header` (BEM se complexo)

### Organização de Arquivos:
- **Partials**: `_nome-do-arquivo.scss` (começa com underscore)
- **Index**: `_index.scss` ou `index.scss` (barril de exportação)
- **Main**: `main.scss` (único sem underscore, entry point)

### Imports:
```scss
// Ordem correta em main.scss
@use './variables';   // 1. Variáveis e temas
@use './mixins';      // 2. Mixins
@use './themes';      // 3. Estilos base com temas
@use './utilities';   // 4. Utilitários
@use './core';        // 5. Apps (core primeiro)
@use './dashboard';
@use './produtos';
// ... outros apps
```

---

**Status**: 🟡 Em Progresso
**Responsável**: AI Assistant + Gedes
**Prazo**: 1 semana

