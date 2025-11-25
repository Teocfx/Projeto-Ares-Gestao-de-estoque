# ⚡ Quick Start - Windows

## 🚀 Setup Rápido (5 minutos)

### 1. Clone e Entre no Projeto
```powershell
git clone https://github.com/Teocfx/Projeto-Ares-Gestao-de-estoque.git
cd Projeto-Ares-Gestao-de-estoque
```

### 2. Instale Dependências
```powershell
python -m pip install -r requirements/base.txt
npm install
```

### 3. Configure Banco e Frontend
```powershell
python manage.py migrate
npx webpack --mode=production
python manage.py collectstatic --noinput
```

### 4. Crie Superusuário
```powershell
python manage.py createsuperuser
```
- Username: admin
- Password: admin123

### 5. Popular Dados de Teste (Opcional)
```powershell
Get-Content scripts\populate_complete.py | python manage.py shell
```

### 6. Inicie o Servidor
```powershell
python manage.py runserver
```

## ✅ Pronto!
Acesse: **http://127.0.0.1:8000/**

---

**Guia completo:** [SETUP-WINDOWS.md](SETUP-WINDOWS.md)
