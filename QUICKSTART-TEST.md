# 🚀 Guia Rápido de Instalação para Testes

Este guia é para quem quer testar o sistema rapidamente **sem configurar PostgreSQL**.

## ⚡ Instalação Rápida (SQLite - Desenvolvimento)

### 1️⃣ Pré-requisitos
- Python 3.12+ ou Python 3.14+
- Node.js 20+

### 2️⃣ Clonar o repositório
```bash
git clone https://github.com/Teocfx/Projeto-Ares-Gestao-de-estoque.git
cd Projeto-Ares-Gestao-de-estoque
```

### 3️⃣ Criar ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 4️⃣ Instalar dependências mínimas

**Para desenvolvimento local (sem PostgreSQL):**
```bash
pip install -r requirements/local.txt
```

**Ou se preferir as dependências completas:**
```bash
pip install -r requirements/development.txt
```

### 5️⃣ Instalar dependências do frontend
```bash
npm install
```

### 6️⃣ Configurar banco de dados SQLite
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7️⃣ Compilar frontend
```bash
npm run build
```

### 8️⃣ Executar o servidor
```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

---

## 🔧 Solução de Problemas

### Erro: `ModuleNotFoundError: No module named 'dj_database_url'`

**Solução:** Use `requirements/local.txt` em vez de `requirements/production.txt`:
```bash
pip install -r requirements/local.txt
```

### Erro: `ModuleNotFoundError: No module named 'decouple'`

**Causa:** Dependências não instaladas completamente.

**Solução:**
```bash
source .venv/bin/activate  # Linux/Mac
pip install -r requirements/local.txt

# Ou instale manualmente
pip install python-decouple
```

**Verificar dependências:**
```bash
python check-dependencies.py
```

### Erro: Conflito de dependências do `psycopg`

**Causa:** O `psycopg` (driver do PostgreSQL) tem conflitos em alguns ambientes.

**Solução:** Use SQLite para desenvolvimento (não precisa de PostgreSQL):
```bash
pip install -r requirements/local.txt
```

Se realmente precisar do PostgreSQL, instale manualmente:
```bash
pip install psycopg[binary]==3.1.20
```

### Erro: `weasyprint` não instala no Windows

**Causa:** O WeasyPrint (geração de PDF) tem dependências complexas no Windows.

**Solução temporária:** Comente a linha no `requirements/base.txt`:
```
# weasyprint>=62.0,<63.0
```

Depois reinstale:
```bash
pip install -r requirements/local.txt
```

---

## 📁 Estrutura de Arquivos de Requisitos

- `requirements/base.txt` - Dependências core do Django e Wagtail
- `requirements/local.txt` - **NOVO**: Mínimo para testes locais (SQLite)
- `requirements/development.txt` - Ferramentas de desenvolvimento
- `requirements/production.txt` - Dependências de produção (PostgreSQL, AWS, etc.)
- `requirements.txt` - Aponta para `production.txt`

---

## 🎯 Ambientes

### Desenvolvimento Local (SQLite)
```bash
pip install -r requirements/local.txt
python manage.py migrate
python manage.py runserver
```

### Desenvolvimento Completo
```bash
pip install -r requirements/development.txt
```

### Produção (PostgreSQL)
```bash
pip install -r requirements/production.txt
```

---

## 🧪 Executar Testes
```bash
python manage.py test --keepdb
```

---

## 🆘 Suporte

Se encontrar problemas, abra uma issue no GitHub:
https://github.com/Teocfx/Projeto-Ares-Gestao-de-estoque/issues
