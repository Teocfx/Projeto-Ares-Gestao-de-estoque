"""
Testes para o módulo de autenticação Keycloak.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock, PropertyMock

from .adapters import KeycloakAdapter
from .utils import obter_provedor_recente, pode_fazer_logout_sso

User = get_user_model()


class KeycloakAdapterTests(TestCase):
    """Testes para o adaptador Keycloak."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.adapter = KeycloakAdapter()
    
    def test_adapter_initialization(self):
        """Testa inicialização do adaptador."""
        self.assertIsNotNone(self.adapter)
        self.assertIsInstance(self.adapter, KeycloakAdapter)
    
    @patch('auth_keycloak.adapters.obter_provedor_recente')
    @patch('auth_keycloak.adapters.pode_fazer_logout_sso')
    def test_get_logout_redirect_url_local_user(self, mock_pode_logout, mock_obter_provedor):
        """Testa redirect de logout para usuário local."""
        mock_obter_provedor.return_value = None
        mock_pode_logout.return_value = False
        
        request = MagicMock()
        request.user = self.user
        
        # Não deve fazer logout SSO para usuário local
        redirect_url = self.adapter.get_logout_redirect_url(request)
        self.assertIsNotNone(redirect_url)
    
    @patch('auth_keycloak.adapters.obter_provedor_recente')
    @patch('auth_keycloak.adapters.pode_fazer_logout_sso')
    @patch('auth_keycloak.adapters.logout_sso')
    def test_get_logout_redirect_url_sso_user(self, mock_logout_sso, mock_pode_logout, mock_obter_provedor):
        """Testa redirect de logout para usuário SSO."""
        mock_provedor = MagicMock()
        mock_obter_provedor.return_value = mock_provedor
        mock_pode_logout.return_value = True
        
        request = MagicMock()
        request.user = self.user
        # is_authenticated é uma propriedade read-only, então usamos um mock
        type(request.user).is_authenticated = PropertyMock(return_value=True)
        
        # Deve fazer logout SSO para usuário autenticado via SSO
        redirect_url = self.adapter.get_logout_redirect_url(request)
        self.assertIsNotNone(redirect_url)
        mock_logout_sso.assert_called_once_with(self.user, mock_provedor)


class KeycloakUtilsTests(TestCase):
    """Testes para utilitários do Keycloak."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_obter_provedor_recente_sem_provedor(self):
        """Testa obtenção de provedor quando usuário não tem provedor."""
        provedor = obter_provedor_recente(self.user)
        # Usuário local não deve ter provedor
        self.assertIsNone(provedor)
    
    def test_pode_fazer_logout_sso_usuario_local(self):
        """Testa se usuário local pode fazer logout SSO."""
        pode_logout = pode_fazer_logout_sso(self.user, None)
        # Usuário local não deve poder fazer logout SSO
        self.assertFalse(pode_logout)


class KeycloakIntegrationTests(TestCase):
    """Testes de integração com Keycloak."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_logout_local_user(self):
        """Testa logout de usuário local."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('autenticacao:logout'))
        # Deve redirecionar após logout
        self.assertEqual(response.status_code, 302)
    
    @patch('auth_keycloak.utils.logout_sso')
    def test_logout_redirects_correctly(self, mock_logout_sso):
        """Testa se logout redireciona corretamente."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('autenticacao:logout'))
        self.assertIn(response.status_code, [200, 302])


class KeycloakAuthenticationTests(TestCase):
    """Testes para fluxo de autenticação Keycloak."""
    
    def test_login_without_keycloak(self):
        """Testa login sem Keycloak (usuário local)."""
        User.objects.create_user(
            username='localuser',
            email='local@example.com',
            password='localpass123'
        )
        
        client = Client()
        logged_in = client.login(username='localuser', password='localpass123')
        
        self.assertTrue(logged_in)
    
    def test_user_creation(self):
        """Testa criação de usuário."""
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')


class KeycloakPermissionsTests(TestCase):
    """Testes para permissões relacionadas ao Keycloak."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_has_default_permissions(self):
        """Testa se usuário tem permissões padrão."""
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.is_active)
    
    def test_superuser_creation(self):
        """Testa criação de superusuário."""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
