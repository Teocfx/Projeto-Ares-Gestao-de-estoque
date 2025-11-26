# 🏠 HomePage Pública Wagtail - Documentação

**Data de Implementação:** 25/11/2025  
**Status:** ✅ Completo (100%)  
**Localização:** App `home/`

---

## 📋 Resumo da Implementação

Sistema completo de páginas públicas usando Wagtail CMS com StreamFields para máxima flexibilidade de conteúdo. Permite que usuários não-técnicos gerenciem completamente o site público através do Wagtail Admin.

---

## 🗂️ Estrutura de Arquivos Criados

```
home/
├── models.py              # HomePage e InternalPage com StreamFields
├── admin.py               # Admin Wagtail (auto-registrado)
├── templates/
│   └── home/
│       ├── home_page.html           # Template principal da HomePage
│       ├── internal_page.html       # Template para páginas internas
│       └── blocks/
│           ├── banner_block.html         # Slide do carrossel
│           ├── destaque_block.html       # Card de destaque
│           ├── noticia_block.html        # Card de notícia/blog
│           ├── cta_block.html            # Call-to-action section
│           └── texto_imagem_block.html   # Texto com imagem lateral
└── migrations/
    └── 0001_initial.py    # Migração inicial

scripts/
└── create_homepage.py     # Script para criar HomePage inicial
```

---

## 🎨 Modelos Implementados

### 1. HomePage (home.models.HomePage)

**Características:**
- `max_count = 1` - Apenas uma homepage no site
- Hero section com imagem de fundo e gradiente
- 4 StreamFields principais:
  - `banners` - Carrossel de banners principais
  - `destaques` - Cards de destaque (funcionalidades, serviços)
  - `body` - Conteúdo flexível (CTA, texto+imagem)
  - `noticias` - Blog posts / notícias

**Campos do Hero:**
- `hero_title` - Título principal grande (display-3)
- `hero_subtitle` - Subtítulo explicativo
- `hero_image` - Imagem de fundo (1920x800)

**Campos Adicionais:**
- `destaques_title` - Título da seção de destaques
- `noticias_title` - Título da seção de notícias
- `footer_text` - Rodapé customizável (RichText)
- `show_in_menus` - Aparecer no menu Wagtail

**Organização Admin:**
- MultiFieldPanel "Hero Section"
- MultiFieldPanel "Seções de Conteúdo"
- FieldPanel "Configurações"

### 2. InternalPage (home.models.InternalPage)

**Características:**
- Páginas internas genéricas
- Sem limite de quantidade (`parent_page_types = [HomePage, 'self']`)
- Pode ter hierarquia (páginas filhas)

**Campos:**
- `subtitle` - Subtítulo da página
- `featured_image` - Imagem destaque (1200x400)
- `intro` - Texto introdutório (RichText)
- `body` - Conteúdo flexível (StreamField)
- `show_date` - Exibir data de publicação
- `author` - Nome do autor

---

## 🧩 Blocks Personalizados (StreamFields)

### 1. BannerBlock
**Uso:** Slides do carrossel principal

**Campos:**
- `image` (ImageChooserBlock) - Imagem de fundo 1920x600
- `title` (CharBlock) - Título do banner
- `subtitle` (TextBlock) - Subtítulo opcional
- `button_text` (CharBlock) - Texto do botão CTA
- `button_url` (URLBlock) - Link do botão

**Template:** `home/blocks/banner_block.html`

**Estilo:** Overlay escuro com gradiente, texto branco, botão destacado

---

### 2. DestaqueBlock
**Uso:** Cards de funcionalidades/serviços

**Campos:**
- `title` (CharBlock) - Título do destaque
- `icon` (CharBlock) - Classe Bootstrap Icon (ex: "bi-star")
- `image` (ImageChooserBlock) - Imagem 400x300
- `description` (TextBlock) - Descrição breve
- `link` (URLBlock) - Link opcional

**Template:** `home/blocks/destaque_block.html`

**Estilo:** Card com hover effect, ícone overlay na imagem

---

### 3. NoticiaBlock
**Uso:** Cards de notícias/blog posts

**Campos:**
- `title` (CharBlock) - Título da notícia
- `date` (DateBlock) - Data de publicação
- `author` (CharBlock) - Nome do autor
- `image` (ImageChooserBlock) - Imagem 400x300
- `summary` (TextBlock) - Resumo da notícia
- `link` (URLBlock) - Link para notícia completa

**Template:** `home/blocks/noticia_block.html`

**Estilo:** Card de blog com metadata (data + autor), imagem superior

---

### 4. CallToActionBlock
**Uso:** Seções de call-to-action

**Campos:**
- `title` (CharBlock) - Título da CTA
- `text` (RichTextBlock) - Texto rico explicativo
- `button_text` (CharBlock) - Texto do botão
- `button_url` (URLBlock) - Link do botão
- `background_color` (ChoiceBlock) - Cor de fundo:
  - `primary` - Azul primário
  - `secondary` - Cinza
  - `success` - Verde
  - `danger` - Vermelho
  - `dark` - Escuro
  - `light` - Claro

**Template:** `home/blocks/cta_block.html`

**Estilo:** Seção full-width com padding, centralizada

---

### 5. TextoComImagemBlock
**Uso:** Blocos de texto com imagem lateral

**Campos:**
- `title` (CharBlock) - Título da seção
- `text` (RichTextBlock) - Texto rico completo
- `image` (ImageChooserBlock) - Imagem 600x400
- `image_position` (ChoiceBlock) - Posição da imagem:
  - `left` - Imagem à esquerda
  - `right` - Imagem à direita

**Template:** `home/blocks/texto_imagem_block.html`

**Estilo:** Layout responsivo 2 colunas (inverte no mobile)

---

## 🎯 Funcionalidades Principais

### ✅ Sistema de Hero Section
- Imagem de fundo full-width
- Gradiente overlay (roxo/azul)
- Título display-3 com text-shadow
- Botão dinâmico (Dashboard se logado, Login se anônimo)
- Responsivo

### ✅ Carrossel de Banners Bootstrap
- Indicadores automáticos
- Controles prev/next
- Auto-play habilitado (`data-bs-ride="carousel"`)
- Transições suaves
- Múltiplos slides via StreamField

### ✅ Grid Responsivo de Destaques
- Layout 3 colunas (col-md-4)
- Cards com hover effect
- Ícones Bootstrap Icons
- Imagens otimizadas (fill-400x300)
- Links opcionais

### ✅ Seção de Notícias/Blog
- Grid 3 colunas responsivo
- Metadata (data, autor)
- Imagens otimizadas
- Resumo truncado
- Links para posts completos

### ✅ Blocos CTA Configuráveis
- 6 cores de fundo pré-definidas
- Rich text para formatação
- Botões com Bootstrap styling
- Full-width sections

### ✅ Conteúdo Flexível (Body StreamField)
- Mistura qualquer block no corpo
- Reordenação via drag-and-drop no admin
- Adicionar/remover blocks dinamicamente
- Preview em tempo real no admin

---

## 🚀 Como Usar

### 1. Acessar Wagtail Admin
```
http://127.0.0.1:8000/admin/
```
Fazer login com: `admin` / `admin123`

### 2. Editar HomePage
1. No menu lateral: **Pages** → **Home**
2. Clicar em **Edit**
3. Preencher Hero Section (título, subtítulo, imagem)
4. Adicionar Banners (botão **+ Add banner**)
5. Adicionar Destaques (botão **+ Add destaque**)
6. Adicionar Notícias (botão **+ Add notícia**)
7. Adicionar CTAs ou Texto+Imagem no Body
8. Clicar em **Publish** (canto superior direito)

### 3. Gerenciar Imagens
1. No menu lateral: **Images**
2. Fazer upload de imagens
3. Imagens disponíveis automaticamente nos image choosers

### 4. Criar Páginas Internas
1. No menu lateral: **Pages** → **Home**
2. Clicar nos 3 pontos (⋮)
3. Selecionar **Add child page**
4. Escolher **Internal Page**
5. Preencher conteúdo
6. Publish

---

## 📐 Tamanhos de Imagem Recomendados

| Uso | Tamanho Ideal | Aspect Ratio | Max File Size |
|-----|---------------|--------------|---------------|
| Hero Background | 1920x800 | 2.4:1 | 500KB |
| Banner Slide | 1920x600 | 3.2:1 | 400KB |
| Destaque Card | 400x300 | 4:3 | 100KB |
| Notícia Card | 400x300 | 4:3 | 100KB |
| Texto+Imagem | 600x400 | 3:2 | 200KB |
| Internal Page Featured | 1200x400 | 3:1 | 300KB |

**Nota:** Wagtail otimiza imagens automaticamente com o filtro `fill-WIDTHxHEIGHT`

---

## 🎨 Customização de Estilos

### Cores do Hero Overlay
```css
/* home_page.html - linha 67 */
background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
```

### Hover Effects nos Destaques
```css
/* destaque_block.html - linhas 20-30 */
.destaque-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}
```

### Transições do Carrossel
```html
<!-- home_page.html - linha 23 -->
data-bs-ride="carousel"
```

---

## 🔒 Permissões e Segurança

- Apenas usuários com permissão Wagtail podem editar páginas
- Publicação requer permissão `publish`
- Workflow de aprovação disponível (não configurado ainda)
- Histórico de revisões automático
- Suporte a moderação de conteúdo

---

## 🐛 Troubleshooting

### Página não aparece
- Verificar se foi publicada (botão **Publish**)
- Verificar `live = True` no banco
- Verificar Site.root_page aponta para HomePage

### Imagens não carregam
- Verificar `python manage.py collectstatic`
- Verificar MEDIA_ROOT e MEDIA_URL configurados
- Verificar permissões de pasta media/

### StreamFields vazios
- Adicionar pelo menos 1 block no admin
- Verificar template usa `{% include_block %}`
- Verificar `{% load wagtailcore_tags %}`

### Carrossel não funciona
- Verificar Bootstrap JS carregado
- Verificar IDs únicos (`#bannersCarousel`)
- Verificar `data-bs-*` attributes

---

## 📈 Próximas Melhorias Sugeridas

- [ ] Sistema de categorias para notícias
- [ ] Paginação de notícias (archive page)
- [ ] Formulários de contato via Wagtail Forms
- [ ] Integração com redes sociais (share buttons)
- [ ] SEO metadata fields (description, keywords)
- [ ] Sitemap.xml automático
- [ ] Sistema de comentários
- [ ] Newsletter signup form
- [ ] Multilíngua (i18n)
- [ ] A/B testing de CTAs

---

## 📚 Referências

- [Wagtail StreamField Guide](https://docs.wagtail.org/en/stable/topics/streamfield.html)
- [Bootstrap 5 Carousel](https://getbootstrap.com/docs/5.0/components/carousel/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Wagtail Images](https://docs.wagtail.org/en/stable/topics/images.html)

---

## 👥 Créditos

**Desenvolvido em:** 25/11/2025  
**Por:** GitHub Copilot (Claude Sonnet 4.5)  
**Projeto:** Sistema ARES - Gestão de Estoque  

---

**Status Final:** ✅ 100% Implementado e Funcional
