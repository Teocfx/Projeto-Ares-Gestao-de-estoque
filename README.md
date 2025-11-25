# Sistema de Gestão de Estoque - Projeto Ares

**Ares** é um sistema de gestão de estoque desenvolvido para facilitar o controle de entradas, saídas e inventários. Com uma interface intuitiva, o Ares oferece agilidade, organização e eficiência para empresas que buscam otimizar seus processos logísticos.

## 👥 Equipe
Teófilo da costa Fernandes- RA 1362321634
Miqueias Oliveira Ferreira – RA 1362219767
Nicollye Crisitna Coutinho Gomes – RA 1362318966
Lucas Adryell Ramalho –RA 1362219767
Isaac Bezerra de Menezes- RA 1362318834
Felipe Maciel- RA 1362419474

## 📋 Sobre o Projeto

Este sistema foi desenvolvido para facilitar a gestão de estoques em empresas de qualquer porte, oferecendo:

- **Backend**: Django 5.2 + Wagtail 7.x (Python 3.12+)
- **Frontend**: JavaScript/Webpack + Bootstrap 5 + SCSS (responsivo)
- **Banco de Dados**: PostgreSQL (produção), SQLite (desenvolvimento)
- **Apps principais**:
  - `core/` - Configurações centrais e modelos base
  - `autenticacao/` - Sistema de login/logout
  - `produtos/` - CRUD de produtos, categorias e unidades
  - `movimentacoes/` - Controle de entradas, saídas e ajustes
  - `dashboard/` - Dashboard com métricas e alertas
  - `relatorios/` - Geração de relatórios em PDF

## 🎯 Funcionalidades

### ✅ Autenticação
- Login com usuário/email e senha
- Controle de permissões (Admin, Gestor, Operador)
- Logout seguro

### ✅ Dashboard
- Valor total do estoque
- Produtos cadastrados
- Alertas de estoque crítico
- Últimas movimentações
- Produtos próximos ao vencimento

### ✅ Gestão de Produtos
- CRUD completo de produtos
- Categorização por tipo
- Controle de unidades (UN, KG, L, etc.)
- Estoque mínimo configurável
- Controle de validade
- Status automático (CRÍTICO/BAIXO/OK)

### ✅ Movimentações
- Registro de entradas (compras, devoluções)
- Registro de saídas (vendas, baixas, transferências)
- Ajustes de estoque
- Histórico completo com auditoria
- Documentos fiscais (NF, CF-e)
- Atualização automática de estoque

### ✅ Relatórios
- Relatório de estoque atual
- Relatório de movimentações por período
- Relatório de produtos vencidos/próximos ao vencimento
- Exportação em PDF
- Filtros por categoria e período

## 🚀 Instalação

### Pré-requisitos

- Python 3.12+ (ou Python 3.14 com Django 5.2+)
- Node.js 20+
- PostgreSQL (produção) ou SQLite (desenvolvimento)

### 📖 Guias de Setup

**Para Windows:**
- **[SETUP-WINDOWS.md](SETUP-WINDOWS.md)** - Guia completo passo a passo para Windows

**Para Linux/Mac:**

1. **Clone o repositório:**
```bash
git clone https://github.com/Teocfx/Projeto-Ares-Gestao-de-estoque.git
cd Projeto-Ares-Gestao-de-estoque
```

2. **Configure o ambiente Python:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

3. **Instale as dependências:**
```bash
pip install -r requirements/base.txt
npm install
```

4. **Configure o banco de dados:**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **Compile o frontend e colete arquivos estáticos:**
```bash
npx webpack --mode=production
python manage.py collectstatic --noinput
```

6. **Inicie o servidor:**
```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

5. **Inicie o servidor:**
```bash
python manage.py runserver
```

6. **Acesse o sistema:**
- Sistema: http://localhost:8000/
- Admin Django: http://localhost:8000/django-admin/
- Admin Wagtail: http://localhost:8000/admin/

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
Projeto-Ares-Gestao-de-estoque/
├── backend/                    # Apps Django
│   ├── core/                  # Modelos base e configurações
│   ├── autenticacao/          # Sistema de login
│   ├── produtos/              # CRUD de produtos
│   ├── movimentacoes/         # Entradas/saídas
│   ├── dashboard/             # Dashboard principal
│   ├── relatorios/            # Relatórios PDF
│   └── gestaoestoque/         # Settings Django
├── frontend/                  # Assets frontend
│   ├── scss/                  # Estilos SCSS
│   └── js/                    # JavaScript
├── requirements.txt           # Dependências Python
├── package.json              # Dependências Node.js
└── manage.py                 # Comando Django
```

### Comandos Úteis

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Rodar migrations
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar servidor de desenvolvimento
python manage.py runserver

# Rodar testes
python manage.py test

# Build frontend
npm install
npm run build
```

### 🎨 Frontend

- **Bootstrap 5**: Framework CSS responsivo
- **SCSS**: Pré-processador CSS com variáveis
- **JavaScript ES6+**: Módulos organizados por app
- **Webpack**: Bundling de assets
- **Alpine.js**: Interatividade leve

### 🧪 Testes

```bash
# Rodar todos os testes
python manage.py test

# Rodar testes com cobertura
coverage run manage.py test
coverage report
coverage html
```

## 🤖 Testes Automatizados
- Ferramentas utilizadas
- Como rodar os testes

## 📊 Métricas e Estimativas
- Métricas aplicadas (ex: cobertura, defeitos, complexidade)
- Estimativas de esforço
  
## 🔍 Revisão Técnica
- Técnicas usadas (pareamento, SonarQube, Lint)
- Resultados encontrados
  
## 🔧 Versionamento
Adotamos práticas modernas de desenvolvimento com foco em qualidade, escalabilidade e colaboração. Utilizamos o GitHub como plataforma principal, seguindo uma estratégia baseada em branches e pull requests para garantir controle de versão, revisão de código e integração contínua.

Link para PRs e commits
## 🚀 Execução
Passo a passo para rodar o sistema localmente e os testes.

## 🐳 Docker

### Desenvolvimento
```bash
docker compose up --build
```

### Produção
```bash
docker build -f Dockerfile -t gestao-estoque .
docker run -p 8000:8080 gestao-estoque
```

## 📊 Modelos Principais

### Product
```python
- sku (CharField): Código único do produto
- name (CharField): Nome do produto
- category (ForeignKey): Categoria do produto
- unit (ForeignKey): Unidade de medida
- current_stock (DecimalField): Estoque atual
- min_stock (DecimalField): Estoque mínimo
- expiry_date (DateField): Data de validade
- stock_status (Property): CRITICO/BAIXO/OK
```

### InventoryMovement
```python
- product (ForeignKey): Produto movimentado
- type (CharField): ENTRADA/SAIDA/AJUSTE
- quantity (DecimalField): Quantidade
- user (ForeignKey): Usuário responsável
- timestamp (DateTimeField): Data/hora da movimentação
- document (CharField): Documento fiscal
```

## 🔒 Permissões

- **Admin**: Acesso total ao sistema
- **Gestor**: Visualizar relatórios, gerenciar produtos
- **Operador**: Registrar movimentações apenas

## 📈 Status do Projeto

- ✅ **Backend**: Django 5.2 + Wagtail 7.2 configurados
- ✅ **Models**: Produtos, Movimentações, Relatórios implementados
- ✅ **URLs**: Roteamento completo
- ✅ **Views**: CRUD e Dashboard implementados
- ✅ **Templates**: Interface completa responsiva
- ✅ **Forms**: Formulários de cadastro e edição
- ✅ **Frontend**: Bootstrap 5 + JavaScript/Webpack
- ✅ **Autenticação**: Sistema de login implementado
- ✅ **Dashboard**: Métricas e gráficos funcionais
- ⬜ **Testes**: A ser implementado

## 🔗 Links Úteis

- **[SETUP-WINDOWS.md](SETUP-WINDOWS.md)** - Guia completo de instalação no Windows
- **[ACESSO-TESTE.md](ACESSO-TESTE.md)** - Informações de acesso ao sistema
- **[docs/](docs/)** - Documentação adicional do projeto

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 🌐 GitHub Pages
[Link para a landing page do projeto](https://seuusuario.github.io/repositorio)

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
