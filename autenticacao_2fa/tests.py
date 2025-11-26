"""
Testes para autenticacao_2fa.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice


class Setup2FATestCase(TestCase):
    """Testes para configuração de 2FA."""
    
    def setUp(self):
        """Configuração inicial dos testes."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_setup_page_requires_login(self):
        """Testa que página de setup requer login."""
        response = self.client.get(reverse('autenticacao_2fa:setup_2fa'))
        self.assertEqual(response.status_code, 302)  # Redirect para login
    
    def test_setup_page_loads_for_authenticated_user(self):
        """Testa que página de setup carrega para usuário autenticado."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('autenticacao_2fa:setup_2fa'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Configurar Autenticação')
    
    def test_totp_device_creation_on_setup(self):
        """Testa que dispositivo TOTP é criado ao acessar setup."""
        self.client.login(username='testuser', password='testpass123')
        
        # Não deve existir dispositivo antes
        self.assertEqual(TOTPDevice.objects.filter(user=self.user).count(), 0)
        
        # Acessa página de setup
        response = self.client.get(reverse('autenticacao_2fa:setup_2fa'))
        
        # Dispositivo não confirmado deve ser criado
        device = TOTPDevice.objects.filter(user=self.user, confirmed=False).first()
        self.assertIsNotNone(device)
        self.assertEqual(device.user, self.user)
        self.assertFalse(device.confirmed)
    
    def test_verify_valid_token(self):
        """Testa verificação de token válido."""
        self.client.login(username='testuser', password='testpass123')
        
        # Criar dispositivo
        device = TOTPDevice.objects.create(
            user=self.user,
            name='default',
            confirmed=False
        )
        
        # Gerar token válido - TOTPDevice usa bin_key para gerar tokens
        import time
        from django_otp.oath import totp
        token = str(totp(device.bin_key, step=device.step, t0=device.t0, digits=device.digits))
        
        # Submeter token
        response = self.client.post(
            reverse('autenticacao_2fa:setup_2fa'),
            {'token': token}
        )
        
        # Deve redirecionar para sucesso
        self.assertEqual(response.status_code, 302)
        
        # Dispositivo deve estar confirmado
        device.refresh_from_db()
        self.assertTrue(device.confirmed)
    
    def test_verify_invalid_token(self):
        """Testa verificação de token inválido."""
        self.client.login(username='testuser', password='testpass123')
        
        # Criar dispositivo
        TOTPDevice.objects.create(
            user=self.user,
            name='default',
            confirmed=False
        )
        
        # Submeter token inválido
        response = self.client.post(
            reverse('autenticacao_2fa:setup_2fa'),
            {'token': '000000'}
        )
        
        # Deve redirecionar de volta para setup
        self.assertEqual(response.status_code, 302)
        
        # Dispositivo não deve estar confirmado
        device = TOTPDevice.objects.filter(user=self.user).first()
        self.assertFalse(device.confirmed)
    
    def test_disable_2fa(self):
        """Testa desabilitação de 2FA."""
        self.client.login(username='testuser', password='testpass123')
        
        # Criar dispositivo confirmado
        device = TOTPDevice.objects.create(
            user=self.user,
            name='default',
            confirmed=True
        )
        
        # Desabilitar 2FA
        response = self.client.post(reverse('autenticacao_2fa:disable_2fa'))
        
        # Deve redirecionar
        self.assertEqual(response.status_code, 302)
        
        # Dispositivo deve ser deletado
        self.assertEqual(TOTPDevice.objects.filter(user=self.user).count(), 0)
    
    def test_status_api_without_2fa(self):
        """Testa API de status sem 2FA configurado."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('autenticacao_2fa:status'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertFalse(data['has_2fa'])
        self.assertEqual(data['username'], 'testuser')
    
    def test_status_api_with_2fa(self):
        """Testa API de status com 2FA configurado."""
        self.client.login(username='testuser', password='testpass123')
        
        # Criar dispositivo confirmado
        TOTPDevice.objects.create(
            user=self.user,
            name='default',
            confirmed=True
        )
        
        response = self.client.get(reverse('autenticacao_2fa:status'))
        data = response.json()
        self.assertTrue(data['has_2fa'])


class Verify2FATestCase(TestCase):
    """Testes para verificação de 2FA durante login."""
    
    def setUp(self):
        """Configuração inicial dos testes."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.device = TOTPDevice.objects.create(
            user=self.user,
            name='default',
            confirmed=True
        )
    
    def test_verify_page_requires_login(self):
        """Testa que página de verificação requer login."""
        response = self.client.get(reverse('autenticacao_2fa:verify_2fa'))
        self.assertEqual(response.status_code, 302)
    
    def test_verify_page_loads_for_authenticated_user(self):
        """Testa que página de verificação carrega para usuário autenticado."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('autenticacao_2fa:verify_2fa'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Verificação')
    
    def test_successful_verification_sets_session(self):
        """Testa que verificação bem-sucedida marca sessão."""
        self.client.login(username='testuser', password='testpass123')
        
        # Gerar token válido
        from django_otp.oath import totp
        token = str(totp(self.device.bin_key, step=self.device.step, 
                        t0=self.device.t0, digits=self.device.digits))
        
        # Submeter token
        response = self.client.post(
            reverse('autenticacao_2fa:verify_2fa'),
            {'token': token}
        )
        
        # Deve redirecionar
        self.assertEqual(response.status_code, 302)
        
        # Sessão deve estar marcada como verificada
        session = self.client.session
        self.assertTrue(session.get('otp_verified', False))
