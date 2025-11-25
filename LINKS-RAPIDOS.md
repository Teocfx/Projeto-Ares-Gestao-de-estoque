# 🔗 Links Rápidos - Sistema ARES

## 🌐 URLs Principais

### Páginas Públicas
- **Home Pública:** http://127.0.0.1:8000/
- **Páginas Wagtail:** Criar via admin

### Sistema Interno
- **Dashboard:** http://127.0.0.1:8000/dashboard/
- **Produtos:** http://127.0.0.1:8000/produtos/
- **Movimentações:** http://127.0.0.1:8000/movimentacoes/
- **Relatórios:** http://127.0.0.1:8000/relatorios/

### Auditoria e Logs
- **Lista de Logs:** http://127.0.0.1:8000/core/logs/
- **Filtrar Logs:** Usar filtros na página de lista

### Upload de Arquivos
- **Exemplo de Upload:** http://127.0.0.1:8000/core/upload-exemplo/

### API REST v1
- **Swagger UI:** http://127.0.0.1:8000/api/v1/docs/
- **ReDoc:** http://127.0.0.1:8000/api/v1/redoc/
- **Obter Token JWT:** POST http://127.0.0.1:8000/api/v1/auth/token/
- **Produtos API:** http://127.0.0.1:8000/api/v1/products/
- **Movimentações API:** http://127.0.0.1:8000/api/v1/movements/
- **Documentação:** [API-REST.md](docs/API-REST.md)
- **Upload de Imagens:** POST /core/upload/image/
- **Upload de Documentos:** POST /core/upload/document/
- **Upload de Avatar:** POST /core/upload/avatar/

### Administração
- **Wagtail Admin:** http://127.0.0.1:8000/admin/
  - Gerenciar HomePage
  - Adicionar/editar páginas
  - Upload de imagens
  - Gerenciar usuários Wagtail

- **Django Admin:** http://127.0.0.1:8000/django-admin/
  - Gerenciar perfis de usuário
  - Ver logs de auditoria
  - Gestão de produtos/movimentações
  - Configurações do sistema

### Autenticação
- **Login:** http://127.0.0.1:8000/autenticacao/login/
- **Logout:** http://127.0.0.1:8000/autenticacao/logout/

---

## 👤 Usuários de Teste

### Representante Legal (Acesso Total)
```
Usuário: admin
Senha: admin123
Perfil: Representante Legal
```

### Representante Delegado (Administrativo)
```
Usuário: joao
Senha: senha123
Perfil: Representante Delegado (permanente)
```

```
Usuário: maria
Senha: senha123
Perfil: Representante Delegado (expira em 90 dias)
```

### Operador (Básico)
```
Usuário: carlos
Senha: senha123
Perfil: Operador
```

---

## 📚 Documentação

- **Setup Windows:** [SETUP-WINDOWS.md](SETUP-WINDOWS.md)
- **Quickstart:** [QUICKSTART.md](QUICKSTART.md)
- **Acesso Teste:** [ACESSO-TESTE.md](ACESSO-TESTE.md)
- **Componentes HTML:** [docs/COMPONENTES-GUIA.md](docs/COMPONENTES-GUIA.md)
- **HomePage Wagtail:** [docs/HOMEPAGE-WAGTAIL.md](docs/HOMEPAGE-WAGTAIL.md)
- **Sistema de Upload:** [docs/UPLOAD-SISTEMA.md](docs/UPLOAD-SISTEMA.md)
- **Theme Switcher:** [docs/THEME-SWITCHER.md](docs/THEME-SWITCHER.md)
- **Status Projeto:** [STATUS-PROJETO.md](STATUS-PROJETO.md)
- **Implementações 25/11:** [IMPLEMENTACOES-25-11-2025.md](IMPLEMENTACOES-25-11-2025.md)

---

## 🚀 Comandos Úteis

### Iniciar Servidor
```powershell
python manage.py runserver
```

### Criar Migrações
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Coletar Static Files
```powershell
python manage.py collectstatic --noinput
```

### Compilar Frontend
```powershell
npm run build
# ou em modo watch:
npm run dev
```

### Criar Superusuário
```powershell
python manage.py createsuperuser
```

### Popular Dados de Teste
```powershell
python scripts/create_perfis.py
python scripts/create_homepage.py
python scripts/populate_complete.py
```

### Executar Testes
```powershell
python manage.py test
```

### Alternar Tema (Claro/Escuro)
- **Via Botão:** Clicar no ícone sol/lua no menu superior
- **Via Teclado:** `Ctrl + Shift + T`
- **Via JavaScript:** `window.ThemeSwitcher.toggleTheme()`

---

## 🎨 Componentes Disponíveis

### Navegação
- `{% include 'components/top_menu.html' %}`
- `{% include 'base/header.html' %}`
- `{% include 'base/breadcrumbs.html' %}`

### Layout
- `{% include 'components/titulo.html' with title='...' %}`
- `{% include 'components/card.html' with title='...' %}`
- `{% include 'components/panel.html' with title='...' %}`

### Formulários
- `{% include 'components/form_field.html' with field=form.campo %}`
- `{% include 'components/button.html' with text='Salvar' %}`

### Feedback
- `{% include 'components/alert.html' with type='success' message='...' %}`
- `{% include 'components/modal.html' with id='confirmModal' title='...' %}`

Ver mais em: [docs/COMPONENTES-GUIA.md](docs/COMPONENTES-GUIA.md)

---

## 🔍 Funcionalidades por Perfil

### Representante Legal
✅ Todas as funcionalidades  
✅ Gerenciar usuários e perfis  
✅ Aprovar movimentações críticas  
✅ Gerar e visualizar todos os relatórios  
✅ Editar produtos e categorias  
✅ Acessar logs de auditoria  

### Representante Delegado
✅ Gerenciar usuários operadores (criar, editar)  
✅ Aprovar movimentações padrão  
✅ Visualizar relatórios  
✅ Editar produtos  
⛔ Não pode alterar outros Representantes  

### Operador
✅ Criar movimentações (aguardam aprovação)  
✅ Visualizar produtos  
✅ Visualizar relatórios básicos  
⛔ Não pode editar produtos  
⛔ Não pode gerar relatórios  
⛔ Não pode gerenciar usuários  

---

## 🛠️ Tecnologias

- **Backend:** Python 3.14 + Django 5.2.8
- **CMS:** Wagtail 7.2
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Frontend:** Bootstrap 5 + SCSS + Webpack
- **Icons:** Bootstrap Icons
- **PDF:** WeasyPrint (não disponível no Windows)

---

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação ou entre em contato com a equipe de desenvolvimento.

**Última atualização:** 25/11/2025
