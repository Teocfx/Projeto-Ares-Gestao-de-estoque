# 🔐 Guia de Teste Manual - Autenticação 2FA (TOTP)

## 📱 O que é 2FA?

Autenticação de Dois Fatores adiciona uma camada extra de segurança ao login. Além da senha, você precisa de um código temporário gerado por um aplicativo autenticador no seu celular.

**Tecnologia**: TOTP (Time-based One-Time Password) - RFC 6238
- Códigos de 6 dígitos
- Válidos por 30 segundos
- Funcionam offline

---

## 📲 Aplicativos Autenticadores Recomendados

Escolha um dos seguintes apps (gratuitos):

### Android
- **Google Authenticator** (mais popular)
- **Microsoft Authenticator** (recomendado pela Microsoft)
- **Authy** (backup em nuvem)
- **FreeOTP+** (open-source)

### iOS
- **Google Authenticator**
- **Microsoft Authenticator**
- **Authy**
- **2FAS Auth** (open-source)

---

## 🚀 Passo a Passo - Teste Completo

### 1. Preparar Ambiente

```powershell
# 1.1. Navegar até o projeto
cd "c:\Users\Pc\OneDrive\Documents\Projeto FPB\Ares\Projeto-Ares-Gestao-de-estoque"

# 1.2. Verificar se migrations estão aplicadas
python manage.py showmigrations otp_totp

# Saída esperada:
# otp_totp
#  [X] 0001_initial
#  [X] 0002_auto_20190420_0723
#  [X] 0003_add_timestamps
```

---

### 2. Criar Superusuário (se necessário)

```powershell
# 2.1. Verificar se já existe superuser
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(is_superuser=True).exists()
>>> exit()

# 2.2. Se não existir, criar:
python manage.py createsuperuser
# Username: admin
# Email: admin@ares.local
# Password: (senha forte)
# Password (again): (confirmar senha)
```

---

### 3. Iniciar Servidor de Desenvolvimento

```powershell
# 3.1. Iniciar servidor
python manage.py runserver

# Saída esperada:
# Django version 5.2.8, using settings 'siteares.settings.development'
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.
```

---

### 4. Testar Fluxo de Configuração 2FA

#### 4.1. Acessar Página de Setup

1. Abra o navegador: **http://127.0.0.1:8000/admin/2fa/setup/**
2. Faça login com as credenciais do superuser
3. Você verá a página "Configurar Autenticação de Dois Fatores"

**O que verificar**:
- ✅ Página carrega sem erros
- ✅ QR code é exibido
- ✅ Chave secreta alternativa é visível (32 caracteres)
- ✅ Instruções estão claras

---

#### 4.2. Escanear QR Code

1. Abra o app autenticador no celular
2. Toque em "+" ou "Adicionar conta"
3. Escolha "Escanear QR code"
4. Aponte a câmera para o QR code na tela

**Alternativa (entrada manual)**:
1. No app, escolha "Entrada manual"
2. Nome da conta: `Ares - admin`
3. Chave: copie a chave secreta da página (ex: `JBSWY3DPEHPK3PXP`)
4. Tipo: Baseado em tempo (Time-based)

**O que verificar**:
- ✅ QR code é lido corretamente
- ✅ Conta "Ares - admin" aparece no app
- ✅ Código de 6 dígitos é gerado a cada 30 segundos

---

#### 4.3. Verificar Código de Ativação

1. No app autenticador, observe o código de 6 dígitos (ex: `123456`)
2. Digite o código no campo "Código de verificação" da página
3. Clique em "Verificar e Ativar"

**O que verificar**:
- ✅ Se código correto: redirecionado para página de sucesso
- ✅ Mensagem: "2FA configurado com sucesso!"
- ✅ Se código incorreto: erro "Código inválido ou expirado"
- ✅ Se código expirado (>30s): erro de validação

---

### 5. Testar Gerenciamento 2FA

#### 5.1. Verificar Status

**URL**: http://127.0.0.1:8000/admin/2fa/success/

**O que verificar**:
- ✅ Página mostra "2FA está ativo"
- ✅ Informações do dispositivo:
  - Nome: `admin's device`
  - Confirmado: Sim
  - Data de criação
- ✅ Botão "Desabilitar 2FA" está visível

---

#### 5.2. API de Status JSON

**URL**: http://127.0.0.1:8000/admin/2fa/status/

**Resposta esperada** (2FA ativo):
```json
{
  "has_2fa": true,
  "devices": [
    {
      "id": 1,
      "name": "admin's device",
      "confirmed": true,
      "created_at": "2025-11-25T14:30:00Z"
    }
  ]
}
```

**Resposta esperada** (2FA inativo):
```json
{
  "has_2fa": false,
  "devices": []
}
```

---

#### 5.3. Desabilitar 2FA

1. Acesse: http://127.0.0.1:8000/admin/2fa/success/
2. Clique em "Desabilitar 2FA"
3. Confirme a ação

**O que verificar**:
- ✅ Redirecionado para `/admin/2fa/setup/`
- ✅ Mensagem: "2FA desabilitado com sucesso"
- ✅ API status retorna `has_2fa: false`
- ✅ Dispositivo TOTP removido do banco

---

### 6. Testar Proteções de Segurança

#### 6.1. Tentativa de Acesso Sem Login

```powershell
# Teste com curl (PowerShell)
Invoke-WebRequest -Uri "http://127.0.0.1:8000/admin/2fa/setup/" -UseBasicParsing
```

**O que verificar**:
- ✅ Retorna status 302 (redirect)
- ✅ Redireciona para `/admin/login/?next=/admin/2fa/setup/`

---

#### 6.2. Tentativa de POST com Código Inválido

1. Acesse `/admin/2fa/setup/`
2. Configure 2FA mas **NÃO** digite o código
3. No navegador, abra DevTools (F12) > Console
4. Execute:
```javascript
fetch('/admin/2fa/setup/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
  },
  body: 'verification_code=000000'
})
```

**O que verificar**:
- ✅ Retorna erro "Código inválido ou expirado"
- ✅ Dispositivo não é confirmado
- ✅ 2FA não é ativado

---

#### 6.3. Proteção CSRF

Tente fazer POST sem CSRF token:

```javascript
// DevTools Console
fetch('/admin/2fa/disable/', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'}
})
```

**O que verificar**:
- ✅ Retorna erro 403 Forbidden
- ✅ Mensagem: "CSRF verification failed"

---

### 7. Testar Edge Cases

#### 7.1. Tentar Configurar 2FA Duas Vezes

1. Configure 2FA (sucesso)
2. Acesse `/admin/2fa/setup/` novamente

**O que verificar**:
- ✅ Redireciona para `/admin/2fa/success/`
- ✅ Não permite criar segundo dispositivo
- ✅ Mensagem: "2FA já está configurado"

---

#### 7.2. Código Próximo do Tempo de Expiração

1. Configure 2FA
2. Espere até os últimos 5 segundos do ciclo de 30s
3. Digite o código rapidamente

**O que verificar**:
- ✅ Código ainda funciona (janela de tolerância)
- ✅ Se expirar, próximo código funciona

---

#### 7.3. Dispositivo Não Confirmado

1. Acesse `/admin/2fa/setup/` (cria dispositivo)
2. **NÃO** digite o código
3. Acesse `/admin/2fa/status/`

**O que verificar**:
```json
{
  "has_2fa": false,  // dispositivo não confirmado = sem 2FA
  "devices": []
}
```

---

## 🧪 Checklist de Testes

### Setup e Configuração
- [ ] Página `/admin/2fa/setup/` carrega
- [ ] QR code é gerado e exibido
- [ ] Chave secreta é exibida (32 caracteres)
- [ ] QR code pode ser escaneado pelo app
- [ ] Código válido ativa 2FA
- [ ] Código inválido mostra erro
- [ ] Código expirado mostra erro

### Gerenciamento
- [ ] `/admin/2fa/success/` mostra status correto
- [ ] `/admin/2fa/status/` retorna JSON correto
- [ ] Desabilitar 2FA funciona
- [ ] Mensagens de feedback são claras

### Segurança
- [ ] Páginas requerem login
- [ ] CSRF protection funciona
- [ ] Não permite múltiplos dispositivos
- [ ] Dispositivos não confirmados não ativam 2FA
- [ ] Redirecionamentos corretos

### UX/UI
- [ ] Página é responsiva (mobile/desktop)
- [ ] Instruções são claras
- [ ] Erros são informativos
- [ ] Layout é consistente com admin

---

## 🐛 Problemas Comuns e Soluções

### 1. QR Code Não Aparece

**Sintoma**: Página carrega mas QR code está quebrado

**Causa**: Biblioteca `qrcode` não instalada

**Solução**:
```powershell
pip install qrcode[pil]==7.4.2
python manage.py runserver
```

---

### 2. Código Sempre Inválido

**Sintoma**: App gera código mas sempre falha na verificação

**Causa**: Relógio do servidor/celular desincronizado

**Solução**:
```powershell
# Verificar hora do servidor (Windows)
Get-Date

# Comparar com hora do celular
# Diferença deve ser < 30 segundos

# Sincronizar relógio do Windows
w32tm /resync
```

---

### 3. Erro "CSRF verification failed"

**Sintoma**: Erro 403 ao enviar formulário

**Causa**: CSRF token ausente ou inválido

**Solução**:
1. Limpe cookies do navegador
2. Acesse `/admin/` para gerar nova sessão
3. Tente novamente

---

### 4. ImportError: No module named 'django_otp'

**Sintoma**: Erro ao iniciar servidor

**Causa**: django-otp não instalado

**Solução**:
```powershell
pip install django-otp==1.6.3
python manage.py migrate
python manage.py runserver
```

---

### 5. Migrations Não Aplicadas

**Sintoma**: Erro "no such table: otp_totp_totpdevice"

**Causa**: Migrations do django-otp não aplicadas

**Solução**:
```powershell
python manage.py migrate otp_totp
# Operations to perform:
#   Apply all migrations: otp_totp
# Running migrations:
#   Applying otp_totp.0001_initial... OK
#   Applying otp_totp.0002_auto_20190420_0723... OK
#   Applying otp_totp.0003_add_timestamps... OK
```

---

## 📊 Resultados Esperados

### Sucesso Total ✅
- 12/12 testes passando
- 2FA funciona em todos os cenários
- Proteções de segurança ativas
- UX fluida e intuitiva

### Sucesso Parcial ⚠️
- 8-11 testes passando
- 2FA funciona mas com pequenos bugs
- Algumas proteções não funcionam
- UX precisa ajustes

### Falha ❌
- <8 testes passando
- 2FA não funciona
- Erros críticos de segurança
- UX quebrada

---

## 🎯 Próximos Passos Após Testes

### Se Sucesso ✅
1. **Integrar 2FA ao fluxo de login**
   - Modificar view de login para verificar 2FA
   - Adicionar campo de código na página de login
   - Implementar lógica de verificação pós-senha

2. **Adicionar códigos de backup**
   - Gerar 10 códigos de uso único
   - Permitir uso quando app não disponível
   - Armazenar hasheados no banco

3. **Logs de auditoria para 2FA**
   - Registrar ativações/desativações
   - Registrar falhas de verificação
   - Alertas de tentativas suspeitas

4. **Documentação para usuários finais**
   - Tutorial em vídeo
   - FAQ com problemas comuns
   - Suporte para recuperação de conta

### Se Falha ❌
1. **Coletar logs detalhados**
   ```powershell
   # Logs do Django
   python manage.py runserver --verbosity=3
   
   # Logs do banco
   python manage.py dbshell
   SELECT * FROM otp_totp_totpdevice;
   ```

2. **Validar configurações**
   ```powershell
   python manage.py check
   python manage.py diffsettings
   ```

3. **Testes unitários específicos**
   ```powershell
   python manage.py test autenticacao_2fa --verbosity=2 --failfast
   ```

---

## 📚 Referências

- [RFC 6238 - TOTP](https://datatracker.ietf.org/doc/html/rfc6238)
- [django-otp Documentation](https://django-otp-official.readthedocs.io/)
- [Google Authenticator](https://support.google.com/accounts/answer/1066447)
- [OWASP 2FA Guidelines](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)

---

**Criado por**: GitHub Copilot (Claude Sonnet 4.5)  
**Data**: 25 de Novembro de 2025  
**Versão**: 1.0  
**Status**: Pronto para teste
