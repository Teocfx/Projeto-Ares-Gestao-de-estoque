"""
Testes para o módulo de autenticação.
"""
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


# Desabilitar ManifestStaticFilesStorage durante os testes
@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)


class LoginViewTests(TestCase):
    """Testes para a view de login."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.login_url = reverse('autenticacao:login')
    
    def test_login_view_loads(self):
        """Testa se a view de login carrega corretamente."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
    
    def test_login_with_valid_credentials(self):
        """Testa login com credenciais válidas."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect após login
    
    def test_login_with_invalid_credentials(self):
        """Testa login com credenciais inválidas."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Permanece na página
    
    def test_login_redirects_authenticated_user(self):
        """Testa se usuário autenticado é redirecionado."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.login_url)
        # Usuário já autenticado deve ser redirecionado
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)


class LogoutViewTests(TestCase):
    """Testes para a view de logout."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.logout_url = reverse('autenticacao:logout')
    
    def test_logout_authenticated_user(self):
        """Testa logout de usuário autenticado."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
    
    def test_logout_redirects_to_login(self):
        """Testa se logout redireciona para login."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.logout_url, follow=False)
        # Verificar se redireciona para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
