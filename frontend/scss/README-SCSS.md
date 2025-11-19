# 🎨 Guia de Estilo SCSS - Projeto Ares

> **Última atualização**: 19 de Novembro de 2025  
> **Status**: ✅ Padronizado e otimizado

---

## 📋 Índice

1. [Estrutura de Arquivos](#estrutura-de-arquivos)
2. [Variáveis e Cores](#variáveis-e-cores)
3. [Boas Práticas](#boas-práticas)
4. [Melhorias Realizadas](#melhorias-realizadas)
5. [Sistema de Temas (Futuro)](#sistema-de-temas-futuro)

---

## 📁 Estrutura de Arquivos

```
frontend/scss/
├── variables.scss          # ⭐ Variáveis globais (ÚNICA fonte de verdade)
├── _themes.scss           # Componentes reutilizáveis base
├── main.scss              # Entry point principal
├── core/                  # Componentes globais
│   ├── theme-selector.scss
│   └── compartilhamento.scss
├── dashboard/             # Módulo Dashboard
│   ├── dashboard.scss
│   └── dashboard_escuro.scss
├── produtos/              # Módulo Produtos
│   ├── produtos.scss
│   └── produtos_escuro.scss
├── movimentacoes/         # Módulo Movimentações
│   ├── movimentacoes.scss
│   └── movimentacoes_escuro.scss
└── autenticacao/          # Módulo Autenticação
    ├── login.scss
    └── login_escuro.scss
```

---

## 🎨 Variáveis e Cores

### ✅ SEMPRE use variáveis do `variables.scss`

#### **Cores Base**
```scss
// ✅ CORRETO
background-color: variables.$color-white;
color: variables.$color-grey-900;
border: 1px solid variables.$color-light-border;

// ❌ ERRADO
background-color: #ffffff;
color: #212121;
border: 1px solid #f1f3f5;
```

#### **Cores Primárias**
```scss
// Vermelho principal
variables.$color-primary           // #C8102E
variables.$color-primary-dark      // #9B0C23
variables.$color-primary-hover     // #9B0C23 (igual ao dark)
variables.$color-primary-light     // #E74A5B
variables.$color-primary-lighter   // #F29BA6
```

#### **Opacidades do Primary**
```scss
variables.$color-primary-05   // rgba(200, 16, 46, 0.05)
variables.$color-primary-10   // rgba(200, 16, 46, 0.1)
variables.$color-primary-12   // rgba(200, 16, 46, 0.12)
variables.$color-primary-20   // rgba(200, 16, 46, 0.2)
variables.$color-primary-40   // rgba(200, 16, 46, 0.4)
variables.$color-primary-70   // rgba(200, 16, 46, 0.7)
```

#### **Escala de Cinza**
```scss
variables.$color-grey-50    // #F9F9F9 (quase branco)
variables.$color-grey-100   // #f6f6f6
variables.$color-grey-200   // #eeeeee
variables.$color-grey-300   // #e0e0e0
variables.$color-grey-400   // #bdbdbd
variables.$color-grey-500   // #9e9e9e (meio tom)
variables.$color-grey-600   // #757575
variables.$color-grey-700   // #616161
variables.$color-grey-800   // #424242
variables.$color-grey-900   // #212121 (quase preto)
```

#### **Opacidades do Preto**
```scss
variables.$color-black-10   // #0000001A (10%)
variables.$color-black-20   // #00000033 (20%)
variables.$color-black-30   // #0000004D (30%)
variables.$color-black-40   // #00000066 (40%)
variables.$color-black-50   // #00000080 (50%)
```

#### **Estados Semânticos**
```scss
variables.$color-success    // #2E7D32 (verde)
variables.$color-warning    // #FFB300 (amarelo)
variables.$color-error      // #C8102E (vermelho)
variables.$color-info       // #0288D1 (azul)
```

#### **Tema Escuro**
```scss
variables.$dark-bg          // #121212
variables.$dark-surface     // #1E1E1E
variables.$dark-surface-alt // #2A2A2A
variables.$dark-text-primary   // #F5F5F5
variables.$dark-text-secondary // #BDBDBD
variables.$dark-border      // #3A3A3A

// Primary adaptado para dark mode
variables.$theme-primary-darkmode       // #FF4D5E
variables.$theme-primary-darkmode-hover // #FF6F7B
```

---

## ✅ Boas Práticas

### 1. **SEMPRE use @use no topo dos arquivos**
```scss
@use '../variables';

// Depois use as variáveis com namespace:
color: variables.$color-primary;
```

### 2. **Backgrounds - Use Branco**
```scss
// ✅ CORRETO - Cards e containers devem ser brancos
.card {
    background-color: variables.$color-white;
}

// ❌ ERRADO - Cinza-200 é para background de página
.card {
    background-color: variables.$color-grey-200;
}
```

### 3. **Texto - Use Cinza-900**
```scss
// ✅ CORRETO
color: variables.$color-grey-900;

// ❌ ERRADO
color: variables.$color-text-primary; // Essa variável não existe!
```

### 4. **Cor de Texto em Botões Primários**
```scss
// ✅ CORRETO
.btn-primary {
    background: variables.$color-primary;
    color: variables.$color-white;
}

// ❌ ERRADO
.btn-primary {
    background: variables.$color-primary;
    color: variables.$color-grey-200; // Grey-200 é background!
}
```

### 5. **Sombras - Use Variáveis de Opacidade**
```scss
// ✅ CORRETO
box-shadow: 0 2px 8px variables.$color-primary-20;
box-shadow: 0 4px 12px variables.$color-black-10;

// ❌ ERRADO
box-shadow: 0 2px 8px rgba(198, 40, 40, 0.2);
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
```

### 6. **Hover States - Use Opacidades**
```scss
// ✅ CORRETO
.nav-link {
    color: variables.$color-white;
    opacity: 0.9;
    
    &:hover {
        opacity: 1;
        background-color: variables.$color-primary-12;
    }
}

// ❌ ERRADO
.nav-link {
    color: rgba(255, 255, 255, 0.9);
    
    &:hover {
        color: rgba(255, 255, 255, 1);
    }
}
```

### 7. **Gradientes**
```scss
// ✅ CORRETO
background: linear-gradient(135deg, 
    variables.$color-primary 0%, 
    variables.$color-primary-hover 100%
);

// No tema escuro:
background: linear-gradient(135deg, 
    variables.$theme-primary-darkmode 0%, 
    variables.$theme-primary-darkmode-hover 100%
);
```

---

## 🔧 Melhorias Realizadas

### ✅ **Correções de Cores**
- ✅ Substituído `$color-grey-200` (background) por `$color-white` em cards e containers
- ✅ Substituído `$color-text-primary` (não existe) por `$color-grey-900`
- ✅ Corrigido cores de texto em navbars (white ao invés de grey-200)
- ✅ Padronizado backgrounds de inputs para branco

### ✅ **Padronização de Opacidades**
- ✅ Criado variáveis `$color-primary-05`, `$color-primary-12`, etc.
- ✅ Substituído `rgba(198, 40, 40, 0.2)` por `$color-primary-20`
- ✅ Substituído `rgba(0, 0, 0, 0.1)` por `$color-black-10`
- ✅ Substituído `rgba(255, 255, 255, 0.1)` por opacidade + white

### ✅ **Tema Escuro**
- ✅ Corrigido backgrounds (dark-bg, dark-surface)
- ✅ Implementado cores darkmode para primary
- ✅ Padronizado cores de texto (dark-text-primary)
- ✅ Ajustado borders e sombras para tema escuro

### ✅ **Consistência**
- ✅ Todos arquivos usam `@use '../variables'`
- ✅ Removido valores hardcoded (#ffffff, #212121, etc.)
- ✅ Padronizado box-shadows com variáveis
- ✅ Melhorado hover states com opacidades

---

## 🚀 Sistema de Temas (Futuro)

**Status**: ⏸️ Desabilitado temporariamente

O sistema de temas com CSS custom properties (`var(--theme-*)`) foi removido temporariamente. No futuro, quando ativado, teremos:

### Temas Disponíveis:
1. **Ares** (Vermelho) - Guerra - Tema padrão
2. **Athena** (Azul) - Sabedoria
3. **Gaia** (Verde) - Terra
4. **Afrodite** (Rosa/Roxo) - Amor
5. **Zeus** (Amarelo/Laranja) - Rei dos Deuses

**Cada tema terá**:
- Modo claro
- Modo escuro

**Arquivos prontos** (em `frontend/scss/themes/`):
- `ares.scss`
- `athena.scss`
- `gaia.scss`
- `afrodite.scss`
- `zeus.scss`

---

## 📝 Checklist de Revisão

Ao criar ou editar arquivos SCSS:

- [ ] ✅ Adicionei `@use '../variables'` no topo?
- [ ] ✅ Usei `variables.$color-white` para backgrounds de cards?
- [ ] ✅ Usei `variables.$color-grey-900` para texto principal?
- [ ] ✅ Usei variáveis de opacidade para sombras?
- [ ] ✅ Removi todos os valores hardcoded (#fff, rgba(), etc.)?
- [ ] ✅ Testei em tema claro E escuro (se aplicável)?
- [ ] ✅ Build compilou sem erros? (`npm run build`)

---

## 🎯 Regras de Ouro

1. **Nunca hardcode cores** - Sempre use variáveis
2. **Branco é para cards** - Cinza-200 é para background de página
3. **Cinza-900 é texto** - Não use variáveis que não existem
4. **Opacidades têm variáveis** - Use `$color-primary-20` ao invés de `rgba()`
5. **Tema escuro é diferente** - Use `$theme-primary-darkmode`

---

## 📚 Referências

- [Sass Documentation](https://sass-lang.com/documentation/)
- [BEM Methodology](http://getbem.com/)
- [Material Design Colors](https://m2.material.io/design/color/)

---

**✨ Última build**: `webpack 5.101.3 compiled with 14 warnings`  
**📦 CSS gerado**: `styles.17596173c4f14624d07a.css (719 KiB)`
