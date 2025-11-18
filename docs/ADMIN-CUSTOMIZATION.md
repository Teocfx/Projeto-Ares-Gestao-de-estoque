# 🎨 Customizações do Admin - ARES

Este documento descreve as customizações aplicadas ao Wagtail Admin para o projeto ARES.

## 📋 Visão Geral

O admin do ARES foi personalizado com:

- ✅ Logo e identidade visual customizada
- ✅ Esquema de cores do projeto (azul escuro + verde)
- ✅ CSS customizado com variáveis CSS
- ✅ JavaScript com funcionalidades extras
- ✅ Dashboard personalizado com links rápidos
- ✅ Hooks do Wagtail para customizar menu e painéis

---

## 🎨 Cores do Sistema

### Paleta Principal
```css
--ares-primary: #2c3e50       /* Azul escuro principal */
--ares-primary-dark: #1a252f  /* Azul mais escuro */
--ares-primary-light: #34495e /* Azul claro */

--ares-success: #27ae60       /* Verde (ações positivas) */
--ares-warning: #f39c12       /* Amarelo (alertas) */
--ares-danger: #e74c3c        /* Vermelho (crítico) */
--ares-info: #3498db          /* Azul claro (informação) */
```

---

## 📂 Arquivos Customizados

### 1. Templates
```
siteares/templates/wagtailadmin/
├── admin_base.html          # Base do admin com logo e CSS
└── base.html                # Template base (se necessário)
```

**admin_base.html**: Estende o template padrão do Wagtail e adiciona:
- Logo ARES no sidebar (📦 + texto)
- Logo na página de login
- CSS inline customizado
- Blocos: `branding_logo`, `branding_login`, `extra_css`

### 2. Hooks do Wagtail
```
core/wagtail_hooks.py
```

**Funcionalidades:**
- `insert_global_admin_css`: Injeta CSS customizado
- `insert_global_admin_js`: Injeta JavaScript customizado
- `construct_main_menu`: Remove itens desnecessários do menu
- `construct_homepage_panels`: Adiciona painel com links rápidos

### 3. Assets Estáticos

#### CSS
```
siteares/static/css/admin/custom-admin.css
```

**Customizações:**
- Sidebar com gradiente
- Botões com cores personalizadas
- Cards e painéis estilizados
- Tabelas com hover effects
- Badges e status coloridos
- Formulários melhorados
- Mensagens de sistema
- Animações suaves
- Responsividade
- Acessibilidade

#### JavaScript
```
siteares/static/js/admin/custom-admin.js
```

**Funcionalidades:**
- Mensagem de boas-vindas no console
- Indicadores visuais de estoque
- Atalhos de teclado:
  - `Ctrl/Cmd + K`: Busca rápida
  - `Ctrl/Cmd + S`: Salvar formulário
  - `ESC`: Fechar modais
- Highlight de linhas em tabelas
- Confirmações para ações críticas
- Utilitários globais:
  - `aresShowToast()`: Notificações toast
  - `aresFormatCurrency()`: Formatar valores BRL
  - `aresFormatDate()`: Formatar datas pt-BR

---

## 🔧 Configurações

### Settings (base.py)
```python
WAGTAIL_SITE_NAME = "ARES - Gestão de Estoque"
```

---

## 🚀 Como Usar

### 1. Acessar o Admin
```
http://localhost:8000/admin/
```

### 2. Atalhos de Teclado

| Atalho | Função |
|--------|--------|
| `Ctrl/Cmd + K` | Foco na busca |
| `Ctrl/Cmd + S` | Salvar formulário |
| `ESC` | Fechar modal |

### 3. Utilitários JavaScript

```javascript
// Mostrar notificação
aresShowToast('Produto salvo com sucesso!', 'success');

// Formatar moeda
const preco = aresFormatCurrency(1234.56); // "R$ 1.234,56"

// Formatar data
const data = aresFormatDate('2025-01-15'); // "15/01/2025"
```

---

## 📊 Indicadores de Estoque

O sistema usa indicadores visuais para status de estoque:

```html
<span data-stock-status="critical">Crítico</span>  <!-- Vermelho -->
<span data-stock-status="low">Baixo</span>         <!-- Amarelo -->
<span data-stock-status="ok">OK</span>             <!-- Verde -->
```

O JavaScript adiciona automaticamente bolinhas coloridas:
- 🔴 **Crítico**: Estoque zerado
- 🟡 **Baixo**: Abaixo do mínimo
- 🟢 **OK**: Estoque adequado

---

## 🎯 Dashboard Personalizado

O painel do dashboard inclui links rápidos para:

- 🏠 **Dashboard Principal** (`/dashboard/`)
- 🏷️ **Produtos** (`/produtos/`)
- ↕️ **Movimentações** (`/movimentacoes/`)
- 📄 **Relatórios** (`/relatorios/`)

---

## 🔄 Atualizações

### Após modificar CSS/JS:

```bash
# 1. Coletar arquivos estáticos
python3 manage.py collectstatic --noinput

# 2. Limpar cache do navegador (Ctrl + Shift + R)
```

### Após modificar templates:

Basta recarregar a página (F5), não precisa collectstatic.

### Após modificar wagtail_hooks.py:

```bash
# Reiniciar o servidor
python3 manage.py runserver
```

---

## 📱 Responsividade

O admin é totalmente responsivo:

- **Desktop**: Sidebar expandido, layout completo
- **Tablet**: Sidebar compactado, cards adaptados
- **Mobile**: Menu hambúrguer, layout vertical

---

## ♿ Acessibilidade

Recursos implementados:

- Contraste adequado (WCAG AA)
- Foco visível em elementos interativos
- Skip links para navegação
- Textos alternativos
- Atalhos de teclado

---

## 🎨 Customizações Futuras

Ideias para expandir:

- [ ] Tema escuro (dark mode)
- [ ] Mais atalhos de teclado
- [ ] Filtros avançados nas tabelas
- [ ] Gráficos no dashboard
- [ ] Exportação de relatórios
- [ ] Notificações push
- [ ] Upload de logo via admin

---

## 📝 Notas de Desenvolvimento

### Ordem de carregamento CSS:
1. CSS padrão do Wagtail
2. CSS inline do `admin_base.html`
3. `custom-admin.css` (via hook)

### Ordem de carregamento JS:
1. JavaScript padrão do Wagtail
2. `custom-admin.js` (via hook)

### Convenção de nomes:
- Classes CSS: `ares-*`
- Variáveis CSS: `--ares-*`
- Funções JS: `ares*`
- Atributos data: `data-stock-status`, etc.

---

## 🐛 Troubleshooting

### CSS não está sendo aplicado?
```bash
# 1. Verificar se os arquivos existem
ls siteares/static/css/admin/custom-admin.css

# 2. Coletar estáticos novamente
python3 manage.py collectstatic --noinput --clear

# 3. Limpar cache do navegador (Ctrl + Shift + R)
```

### JavaScript não está funcionando?
```bash
# 1. Abrir console do navegador (F12)
# 2. Verificar erros
# 3. Procurar pela mensagem "🎯 ARES Admin Customizado"
```

### Logo não aparece?
```bash
# 1. Verificar template
cat siteares/templates/wagtailadmin/admin_base.html

# 2. Verificar se bloco branding_logo existe
# 3. Limpar cache do template (reiniciar servidor)
```

---

## 📚 Referências

- [Wagtail Admin Customization](https://docs.wagtail.org/en/stable/advanced_topics/customisation/admin_templates.html)
- [Wagtail Hooks](https://docs.wagtail.org/en/stable/reference/hooks.html)
- [Django Static Files](https://docs.djangoproject.com/en/5.1/howto/static-files/)

---

**Desenvolvido para o Projeto ARES** 📦
*Sistema de Gestão de Estoque*
