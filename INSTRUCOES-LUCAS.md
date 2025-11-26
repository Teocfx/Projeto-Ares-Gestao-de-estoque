# 👨‍💻 Instruções para o Lucas - Instalação Rápida

Olá Lucas! Este guia vai te ajudar a instalar o projeto sem os erros que você teve.

## 🚀 Opção 1: Instalação Automática (RECOMENDADO)

Abra o terminal e execute:

```bash
cd ~/Desktop/testeAres/Projeto-Ares-Gestao-de-estoque
bash install-quickstart.sh
```

Pronto! O script vai:
- ✅ Criar ambiente virtual
- ✅ Instalar dependências (sem PostgreSQL)
- ✅ Compilar frontend
- ✅ Configurar banco de dados SQLite

Depois:
```bash
source .venv/bin/activate
python manage.py createsuperuser
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

---

## 🔧 Opção 2: Instalação Manual (se a automática falhar)

### 1. Criar ambiente virtual
```bash
cd ~/Desktop/testeAres/Projeto-Ares-Gestao-de-estoque
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Atualizar pip
```bash
pip install --upgrade pip
```

### 3. Instalar dependências LOCAIS (sem PostgreSQL)
```bash
pip install -r requirements/local.txt
```

**IMPORTANTE**: Use `requirements/local.txt`, NÃO use `requirements.txt` ou `requirements/production.txt`!

### 4. Instalar frontend
```bash
npm install
npm run build
```

### 5. Configurar banco de dados
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Coletar arquivos estáticos
```bash
python manage.py collectstatic --noinput
```

### 7. Executar o servidor
```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

---

## ❌ Se der erro: `ModuleNotFoundError: No module named 'dj_database_url'`

Certifique-se de que está usando `requirements/local.txt`:

```bash
# Ative o ambiente virtual primeiro
source .venv/bin/activate

# Instale as dependências corretas
pip install -r requirements/local.txt
```

## ❌ Se der erro: `ModuleNotFoundError: No module named 'decouple'`

As dependências não foram instaladas completamente:

```bash
# Ative o ambiente virtual
source .venv/bin/activate

# Reinstale as dependências
pip install -r requirements/local.txt

# Ou instale manualmente os pacotes que faltam
pip install python-decouple
```

---

## ❌ Se der erro de conflito do `psycopg`

O arquivo `requirements/local.txt` **não** inclui o psycopg (PostgreSQL).

Se ainda assim der erro:
```bash
pip uninstall psycopg psycopg-binary -y
pip install -r requirements/local.txt
```

---

## ❌ Se der erro: `python3: command not found`

Tente com `python`:
```bash
python -m venv .venv
```

Ou instale o Python 3.12+:
```bash
# Fedora
sudo dnf install python3.12

# Ubuntu
sudo apt install python3.12
```

---

## ❌ Se der erro no frontend (npm)

Se não tiver Node.js instalado:
```bash
# Fedora
sudo dnf install nodejs npm

# Ubuntu
sudo apt install nodejs npm
```

Depois:
```bash
npm install
npm run build
```

---

## 🧪 Verificar que está tudo OK

Depois de instalar, rode:

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Verificar Python
python --version  # Deve ser 3.12+

# Verificar Django
python -c "import django; print(django.get_version())"

# Verificar settings (não deve dar erro)
python -c "from siteares.settings.base import *; print('✅ OK')"

# Listar apps instalados
python manage.py showmigrations
```

---

## 📝 Criar superusuário

```bash
source .venv/bin/activate
python manage.py createsuperuser
```

Digite:
- Username: `admin`
- Email: `admin@example.com`
- Password: (escolha uma senha)

---

## 🚀 Executar o sistema

```bash
source .venv/bin/activate
python manage.py runserver
```

Acesse:
- Sistema: http://127.0.0.1:8000/
- Admin Django: http://127.0.0.1:8000/django-admin/
- Admin Wagtail: http://127.0.0.1:8000/admin/

---

## 🆘 Se AINDA der problema

1. **Apague tudo e comece do zero:**
```bash
cd ~/Desktop/testeAres/Projeto-Ares-Gestao-de-estoque
rm -rf .venv node_modules db.sqlite3
bash install-quickstart.sh
```

2. **Me mande o erro completo** (print ou copie o terminal)

3. **Verifique as versões:**
```bash
python3 --version
node --version
pip --version
```

---

## 💡 Dicas

- ✅ SEMPRE ative o ambiente virtual antes: `source .venv/bin/activate`
- ✅ Use `requirements/local.txt` para testes
- ✅ Use SQLite (não precisa instalar PostgreSQL)
- ✅ Se der erro, leia o `TROUBLESHOOTING.md`
- ✅ O script `install-quickstart.sh` faz tudo automaticamente

---

## 📚 Arquivos Úteis

- `QUICKSTART-TEST.md` - Guia completo passo a passo
- `TROUBLESHOOTING.md` - Erros comuns e soluções
- `README.md` - Documentação geral do projeto
- `install-quickstart.sh` - Script de instalação automática

Boa sorte! 🚀
