# 🚀 Sistema ARES - Informações de Acesso

## ✅ Ambiente Preparado com Sucesso!

O ambiente de desenvolvimento está configurado e pronto para testes.

> 📖 **Para seus colegas de equipe:** Veja o [SETUP-WINDOWS.md](SETUP-WINDOWS.md) para guia completo de instalação ou [QUICKSTART.md](QUICKSTART.md) para setup rápido.

---

## 🌐 Acesso ao Sistema

### URL do Sistema
**http://127.0.0.1:8000/**

### 👤 Credenciais de Administrador
- **Usuário:** `admin`
- **Senha:** `admin123`
- **Email:** admin@ares.com

### 👥 Usuários Operadores (para teste)
1. **João Silva**
   - Usuário: `joao.silva`
   - Senha: `senha123`

2. **Maria Santos**
   - Usuário: `maria.santos`
   - Senha: `senha123`

3. **Carlos Oliveira**
   - Usuário: `carlos.oliveira`
   - Senha: `senha123`

---

## 📊 Dados Populados

O banco de dados foi populado com dados de teste:

### Produtos
- **Total:** 88 produtos ativos
- **Categorias:** 12 categorias diferentes
- **Status:** 25 produtos com estoque baixo

### Movimentações
- **Total:** 1.807 movimentações
- **Entradas:** 881 (48%)
- **Saídas:** 720 (39%)
- **Ajustes:** 206 (11%)

### Categorias Disponíveis
- Alimentos (15 produtos)
- Automotivo (5 produtos)
- Bebidas (10 produtos)
- Eletrônicos (8 produtos)
- Ferramentas (6 produtos)
- Higiene (10 produtos)
- Jardinagem (4 produtos)
- Limpeza (8 produtos)
- Medicamentos (5 produtos)
- Papelaria (8 produtos)
- Pet Shop (4 produtos)
- Vestuário (5 produtos)

---

## 🛠️ Comandos Úteis

### Parar o Servidor
Pressione `CTRL+C` no terminal onde o servidor está rodando

### Iniciar o Servidor Novamente
```powershell
cd "c:\Users\Pc\OneDrive\Documents\Projeto FPB\Ares\Projeto-Ares-Gestao-de-estoque"
C:/Users/Pc/AppData/Local/Programs/Python/Python314/python.exe manage.py runserver
```

### Recompilar Frontend (após mudanças no CSS/JS)
```powershell
npm run build
```

### Criar Novo Superusuário
```powershell
C:/Users/Pc/AppData/Local/Programs/Python/Python314/python.exe manage.py createsuperuser
```

---

## ⚠️ Observações Importantes

### Versão do Python
- **Python 3.14** está sendo usado (versão alpha)
- **Django 5.2.8** instalado para compatibilidade
- Em produção, recomenda-se usar Python 3.12 (versão LTS)

### Bibliotecas Não Disponíveis no Windows
Algumas bibliotecas não funcionam nativamente no Windows:

1. **WeasyPrint** - Para geração de PDFs
   - O sistema está configurado para funcionar sem ela
   - Funcionalidades de PDF não estarão disponíveis
   - Em produção Linux, instale as dependências necessárias

2. **python-magic** - Para detecção de tipos de arquivo
   - O sistema está configurado para funcionar sem ela
   - Usa detecção por extensão de arquivo como fallback

### Configurações de Desenvolvimento
- Banco de dados: **SQLite** (arquivo `db.sqlite3`)
- Debug: **Ativado** (DEBUG=True)
- Arquivos estáticos coletados em: `static/`
- Assets compilados pelo Webpack
- Django: **5.2.8** (atualizado para Python 3.14)

---

## 📱 Funcionalidades do Sistema

### ✅ Autenticação
- Login/Logout
- Controle de permissões por perfil

### ✅ Dashboard
- Métricas em tempo real
- Alertas de estoque
- Gráficos e estatísticas

### ✅ Gestão de Produtos
- CRUD completo
- Controle de estoque
- Categorização
- Alertas de estoque mínimo

### ✅ Movimentações
- Registro de entradas
- Registro de saídas
- Ajustes de estoque
- Histórico completo

### ⚠️ Relatórios
- Visualização em tela: **Funcionando**
- Exportação PDF: **Não disponível** (requer WeasyPrint no Linux)
- Exportação Excel: **Funcionando**

---

## 🔧 Troubleshooting

### Servidor não inicia
1. Verifique se a porta 8000 não está em uso
2. Certifique-se de estar na pasta correta do projeto

### Erros de módulo não encontrado
```powershell
C:/Users/Pc/AppData/Local/Programs/Python/Python314/python.exe -m pip install -r requirements/base.txt
```

### Assets não carregam
```powershell
npm install
npm run build
C:/Users/Pc/AppData/Local/Programs/Python/Python314/python.exe manage.py collectstatic --noinput
```

---

## 📞 Suporte

Para dúvidas ou problemas, consulte:
- README.md principal do projeto
- Documentação em `docs/`
- Issues no GitHub

---

**Desenvolvido pela Equipe Projeto Ares**
*Sistema de Gestão de Estoque v1.0*
