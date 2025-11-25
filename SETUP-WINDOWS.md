# 🚀 Guia de Configuração - Sistema ARES (Windows)

## 📋 Pré-requisitos

Antes de começar, você precisa ter instalado:

- **Python 3.14** (ou Python 3.12+ recomendado)
  - Download: https://www.python.org/downloads/
  - ⚠️ **IMPORTANTE**: Marque a opção "Add Python to PATH" durante a instalação

- **Node.js 20+** (para compilar o frontend)
  - Download: https://nodejs.org/
  - Versão LTS recomendada

- **Git** (para clonar o repositório)
  - Download: https://git-scm.com/downloads

---

## 📥 Passo 1: Clonar o Repositório

Abra o PowerShell e execute:

```powershell
# Navegar até a pasta onde deseja clonar
cd "C:\Users\SeuUsuario\Documents"

# Clonar o repositório
git clone https://github.com/Teocfx/Projeto-Ares-Gestao-de-estoque.git

# Entrar na pasta do projeto
cd Projeto-Ares-Gestao-de-estoque
```

---

## 🐍 Passo 2: Instalar Dependências Python

```powershell
# Instalar dependências do backend
python -m pip install -r requirements/base.txt
```

**Observação:** Se você estiver usando Python 3.14, o Django será atualizado automaticamente para 5.2.8 para compatibilidade.

---

## 📦 Passo 3: Instalar Dependências Node.js

```powershell
# Instalar pacotes npm
npm install
```

**Nota:** Pode aparecer alguns warnings de dependências deprecated, isso é normal.

---

## 🗄️ Passo 4: Configurar Banco de Dados

```powershell
# Executar migrações
python manage.py migrate
```

Isso criará o banco de dados SQLite (`db.sqlite3`) com todas as tabelas necessárias.

---

## 🎨 Passo 5: Compilar Frontend

```powershell
# Compilar assets (CSS, JS, imagens)
npx webpack --mode=production

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

---

## 👤 Passo 6: Criar Superusuário

```powershell
# Criar usuário administrador
python manage.py createsuperuser
```

**Você será solicitado a fornecer:**
- Username (ex: admin)
- Email (pode deixar em branco pressionando Enter)
- Password (ex: admin123)
- Password confirmation

---

## 📊 Passo 7: Popular Banco com Dados de Teste (Opcional)

```powershell
# Popular banco com produtos e movimentações de exemplo
Get-Content scripts\populate_complete.py | python manage.py shell
```

Isso criará:
- 88 produtos em 12 categorias
- 1800+ movimentações históricas
- 3 usuários operadores para teste

---

## 🚀 Passo 8: Iniciar Servidor

```powershell
# Iniciar servidor de desenvolvimento
python manage.py runserver
```

**Pronto! O servidor estará rodando em:** http://127.0.0.1:8000/

---

## 🔐 Credenciais de Acesso

### Administrador
- **URL:** http://127.0.0.1:8000/admin/
- **Usuário:** admin (ou o que você criou)
- **Senha:** admin123 (ou a que você definiu)

### Usuários de Teste (se você executou o populate)
- **joao.silva** / senha123
- **maria.santos** / senha123
- **carlos.oliveira** / senha123

---

## 🛠️ Comandos Úteis

### Parar o Servidor
No terminal onde o servidor está rodando, pressione: **CTRL + C**

### Reiniciar o Servidor
```powershell
python manage.py runserver
```

### Recompilar Frontend (após mudanças CSS/JS)
```powershell
npx webpack --mode=production
python manage.py collectstatic --noinput
```

### Criar Migrações (após alterar models.py)
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Abrir Shell Django (para testes)
```powershell
python manage.py shell
```

### Resetar Banco de Dados (⚠️ apaga tudo)
```powershell
# No Windows PowerShell
Remove-Item db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## ⚠️ Problemas Comuns e Soluções

### Erro: "python não é reconhecido"
**Solução:** Adicione Python ao PATH do Windows ou use `py` ao invés de `python`

### Erro: "npm não é reconhecido"
**Solução:** Reinstale Node.js marcando a opção para adicionar ao PATH

### Erro: "Port 8000 already in use"
**Solução:** 
```powershell
# Usar outra porta
python manage.py runserver 8001
```

### Erro ao instalar dependências Python
**Solução:**
```powershell
# Atualizar pip
python -m pip install --upgrade pip

# Tentar novamente
python -m pip install -r requirements/base.txt
```

### Frontend não carrega (arquivos estáticos 404)
**Solução:**
```powershell
npx webpack --mode=production
python manage.py collectstatic --noinput --clear
```

### Erro com WeasyPrint no Windows
**Normal:** WeasyPrint não funciona no Windows. A funcionalidade de PDF não estará disponível, mas o resto do sistema funciona normalmente.

---

## 📁 Estrutura do Projeto

```
Projeto-Ares-Gestao-de-estoque/
├── siteares/              # Configurações principais
│   ├── settings/          # Settings por ambiente
│   │   ├── base.py       # Configurações base
│   │   ├── dev.py        # Desenvolvimento
│   │   └── production.py # Produção
│   └── urls.py           # URLs principais
├── produtos/              # App de produtos
├── movimentacoes/         # App de movimentações
├── dashboard/             # App de dashboard
├── relatorios/           # App de relatórios
├── autenticacao/         # App de autenticação
├── frontend/             # Assets frontend
│   ├── js/              # JavaScript
│   └── scss/            # Estilos
├── static/              # Arquivos estáticos coletados
├── db.sqlite3           # Banco de dados (gerado)
├── manage.py            # CLI do Django
├── requirements/        # Dependências Python
└── package.json         # Dependências Node.js
```

---

## 🌐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (opcional):

```env
# Configurações Django
DJANGO_SETTINGS_MODULE=siteares.settings.dev
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados
DATABASE_URL=sqlite:///db.sqlite3

# Localização
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Recife
```

---

## 🔄 Atualizando o Projeto

```powershell
# Atualizar código
git pull origin main

# Atualizar dependências Python
python -m pip install -r requirements/base.txt --upgrade

# Atualizar dependências Node.js
npm install

# Executar migrações
python manage.py migrate

# Recompilar frontend
npx webpack --mode=production
python manage.py collectstatic --noinput
```

---

## 📞 Suporte

**Em caso de dúvidas:**
1. Consulte a documentação em `docs/`
2. Veja o README.md principal
3. Abra uma issue no GitHub

---

## 👥 Equipe

- Teófilo da costa Fernandes - RA 1362321634
- Miqueias Oliveira Ferreira – RA 1362219767
- Nicollye Crisitna Coutinho Gomes – RA 1362318966
- Lucas Adryell Ramalho – RA 1362219767
- Isaac Bezerra de Menezes - RA 1362318834
- Felipe Maciel - RA 1362419474

---

**Desenvolvido pela Equipe Projeto Ares**  
*Sistema de Gestão de Estoque v1.0*
