# 🚀 Plano de Melhorias - Alcançar 10/10 em Todas as Categorias

**Data:** 26/11/2025  
**Versão Alvo:** 1.1.0  
**Objetivo:** Elevar todas as notas da Revisão Técnica para 10/10

---

## 📊 SITUAÇÃO ATUAL vs OBJETIVO

| Categoria | Nota Atual | Nota Alvo | Gap | Prioridade |
|-----------|------------|-----------|-----|------------|
| Arquitetura | 9.0/10 | 10/10 | -1.0 | 🟡 Média |
| Qualidade de Código | 8.5/10 | 10/10 | -1.5 | 🟡 Média |
| Segurança | 8.0/10 | 10/10 | -2.0 | 🔴 Alta |
| Performance | 9.0/10 | 10/10 | -1.0 | 🟡 Média |
| Documentação | 10/10 | 10/10 | 0.0 | ✅ Completo |
| Testes | 2.0/10 | 10/10 | -8.0 | 🔴 Crítica |
| **MÉDIA** | **7.8/10** | **10/10** | **-2.2** | - |

---

## 🎯 MELHORIAS POR CATEGORIA

### 1. TESTES: 2.0 → 10.0 (🔴 Crítico - 200h)

#### Situação Atual
- ❌ Cobertura: 0% (26 testes de API apenas)
- ❌ 121 casos de teste pendentes
- ❌ Sem testes unitários de models
- ❌ Sem testes de integração
- ❌ Sem testes E2E

#### Ações Necessárias

**1.1. Testes Unitários de Models (60h)**
```python
# core/tests/test_models.py
from typing import Optional
import pytest
from django.contrib.auth import get_user_model
from core.models import PerfilUsuario, AuditLog

User = get_user_model()

@pytest.mark.django_db
class TestPerfilUsuario:
    """Testes para modelo PerfilUsuario."""
    
    def test_create_perfil_with_permissions(self, admin_user: User) -> None:
        """Testa criação de perfil com permissões."""
        perfil = PerfilUsuario.objects.create(
            user=admin_user,
            nome="Administrador",
            permissoes={
                "produtos": {"criar": True, "editar": True}
            }
        )
        assert perfil.nome == "Administrador"
        assert perfil.tem_permissao("produtos", "criar")
```

**1.2. Testes de Integração (40h)**
```python
# integration/test_movement_workflow.py
@pytest.mark.django_db
class TestMovementWorkflow:
    """Testes de workflow completo de movimentações."""
    
    def test_entrada_product_updates_stock(
        self, 
        authenticated_client, 
        product: Product
    ) -> None:
        """Testa que entrada atualiza estoque corretamente."""
        initial_stock = product.current_stock
        
        response = authenticated_client.post("/api/v1/movements/", {
            "product": product.id,
            "movement_type": "ENTRADA",
            "quantity": 50,
            "document_number": "NF-001"
        })
        
        assert response.status_code == 201
        product.refresh_from_db()
        assert product.current_stock == initial_stock + 50
```

**1.3. Testes E2E com Selenium (30h)**
```python
# e2e/test_product_management.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import pytest

class TestProductManagementE2E:
    """Testes E2E de gerenciamento de produtos."""
    
    @pytest.fixture
    def browser(self) -> webdriver.Chrome:
        """Setup do navegador."""
        driver = webdriver.Chrome()
        yield driver
        driver.quit()
    
    def test_create_product_via_ui(self, browser, live_server) -> None:
        """Testa criação de produto pela interface."""
        browser.get(f"{live_server.url}/produtos/create/")
        
        # Login
        browser.find_element(By.ID, "id_username").send_keys("admin")
        browser.find_element(By.ID, "id_password").send_keys("admin123")
        browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Criar produto
        browser.find_element(By.ID, "id_name").send_keys("Produto Teste")
        browser.find_element(By.ID, "id_sku").send_keys("SKU-001")
        # ... preencher demais campos
        
        browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        assert "Produto criado com sucesso" in browser.page_source
```

**1.4. Testes de Performance (20h)**
```python
# performance/test_load.py
import pytest
from locust import HttpUser, task, between

class ProductAPIUser(HttpUser):
    """Teste de carga da API de produtos."""
    
    wait_time = between(1, 3)
    
    def on_start(self) -> None:
        """Autenticação antes dos testes."""
        response = self.client.post("/api/v1/auth/token/", {
            "username": "testuser",
            "password": "testpass"
        })
        self.token = response.json()["access"]
    
    @task(3)
    def list_products(self) -> None:
        """Lista produtos com autenticação."""
        self.client.get(
            "/api/v1/products/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def get_product_detail(self) -> None:
        """Obtém detalhes de um produto."""
        self.client.get(
            "/api/v1/products/1/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

**1.5. CI/CD com GitHub Actions (10h)**
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements/test.txt
      
      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml --cov-report=html
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

**Meta de Cobertura:**
- Unit Tests: 85%
- Integration Tests: 75%
- E2E Tests: 60%
- **Cobertura Total: 80%+**

---

### 2. SEGURANÇA: 8.0 → 10.0 (🔴 Alta - 50h)

#### Ações Necessárias

**2.1. Implementar 2FA com django-otp (12h)**
```python
# core/views.py
from typing import Any
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.http import HttpRequest, HttpResponse

@otp_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    """Dashboard administrativo com 2FA obrigatório."""
    return render(request, 'dashboard/admin.html')

class Setup2FAView(LoginRequiredMixin, View):
    """View para configurar 2FA."""
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """Exibe QR code para configuração."""
        device = TOTPDevice.objects.filter(
            user=request.user, 
            confirmed=False
        ).first()
        
        if not device:
            device = TOTPDevice.objects.create(
                user=request.user,
                name='default',
                confirmed=False
            )
        
        qr_code_url = device.config_url
        
        return render(request, '2fa/setup.html', {
            'qr_code_url': qr_code_url,
            'device': device
        })
```

**2.2. Rate Limiting Granular com django-ratelimit (8h)**
```python
# core/decorators.py
from typing import Callable
from functools import wraps
from django_ratelimit.decorators import ratelimit
from django.http import HttpRequest

def sensitive_operation_limit(func: Callable) -> Callable:
    """Rate limit para operações sensíveis."""
    @wraps(func)
    @ratelimit(key='user', rate='5/m', method='POST')
    @ratelimit(key='ip', rate='10/m', method='POST')
    def wrapper(request: HttpRequest, *args, **kwargs):
        return func(request, *args, **kwargs)
    return wrapper

# movimentacoes/views.py
class MovementCreateView(CreateView):
    """Criação de movimentação com rate limiting."""
    
    @method_decorator(sensitive_operation_limit)
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """POST com rate limiting."""
        return super().post(request, *args, **kwargs)
```

**2.3. Content Security Policy (CSP) Headers (6h)**
```python
# siteares/settings/production.py
from typing import List

MIDDLEWARE: List[str] = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',  # Novo
    # ... outros middlewares
]

# Content Security Policy
CSP_DEFAULT_SRC: tuple = ("'self'",)
CSP_SCRIPT_SRC: tuple = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net")
CSP_STYLE_SRC: tuple = ("'self'", "'unsafe-inline'", "fonts.googleapis.com")
CSP_FONT_SRC: tuple = ("'self'", "fonts.gstatic.com")
CSP_IMG_SRC: tuple = ("'self'", "data:", "https:")
CSP_CONNECT_SRC: tuple = ("'self'",)
CSP_FRAME_ANCESTORS: tuple = ("'none'",)
CSP_BASE_URI: tuple = ("'self'",)
CSP_FORM_ACTION: tuple = ("'self'",)
```

**2.4. Honeypot Fields (4h)**
```python
# core/forms.py
from typing import Dict, Any
from django import forms

class HoneypotMixin:
    """Mixin para adicionar campo honeypot em formulários."""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['website'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={
                'autocomplete': 'off',
                'tabindex': '-1',
                'style': 'position:absolute;left:-5000px'
            })
        )
    
    def clean(self) -> Dict[str, Any]:
        """Valida que honeypot está vazio."""
        cleaned_data = super().clean()
        if cleaned_data.get('website'):
            raise forms.ValidationError("Bot detected")
        return cleaned_data

# movimentacoes/forms.py
class MovementForm(HoneypotMixin, forms.ModelForm):
    """Formulário de movimentação com proteção anti-bot."""
    
    class Meta:
        model = InventoryMovement
        fields = ['product', 'movement_type', 'quantity']
```

**2.5. Password Policy Rigorosa (5h)**
```python
# siteares/settings/base.py
from typing import List, Dict

AUTH_PASSWORD_VALIDATORS: List[Dict[str, str]] = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}  # Aumentado de 8 para 12
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'core.validators.PasswordComplexityValidator',  # Novo
    },
]

# core/validators.py
import re
from typing import Optional
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class PasswordComplexityValidator:
    """Validador de complexidade de senha."""
    
    def validate(self, password: str, user: Optional[Any] = None) -> None:
        """Valida complexidade da senha."""
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra maiúscula."),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra minúscula."),
                code='password_no_lower',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                _("A senha deve conter pelo menos um número."),
                code='password_no_digit',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos um caractere especial."),
                code='password_no_special',
            )
    
    def get_help_text(self) -> str:
        """Retorna texto de ajuda."""
        return _(
            "Sua senha deve conter: maiúsculas, minúsculas, números e caracteres especiais."
        )
```

**2.6. Atualizar Dependências Vulneráveis (3h)**
```bash
# requirements/base.txt
Pillow==10.4.0  # Atualizado de 10.1.0
django-allauth==65.0.2  # Atualizado de 0.57.0
Django==4.2.16  # Última versão LTS
djangorestframework==3.16.2  # Atualizado
```

**2.7. Pentest Automatizado (12h)**
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  schedule:
    - cron: '0 2 * * 1'  # Segunda-feira às 2h
  push:
    branches: [main, develop]

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Bandit (Python Security)
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json
      
      - name: Run Safety (Dependency Check)
        run: |
          pip install safety
          safety check --json > safety-report.json
      
      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'ARES'
          path: '.'
          format: 'ALL'
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
            dependency-check-report.html
```

---

### 3. PERFORMANCE: 9.0 → 10.0 (🟡 Média - 40h)

#### Ações Necessárias

**3.1. Implementar Redis Cache (16h)**
```python
# siteares/settings/production.py
from typing import Dict, Any

CACHES: Dict[str, Dict[str, Any]] = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': os.environ.get('REDIS_PASSWORD'),
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        }
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
}

# Usar Redis para sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# Cache de templates
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# dashboard/views.py
from typing import Dict, Any
from django.views.decorators.cache import cache_page
from django.core.cache import cache

class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard com cache de estatísticas."""
    
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Obtém dados com cache."""
        context = super().get_context_data(**kwargs)
        
        # Cache de 5 minutos para estatísticas
        cache_key = f'dashboard_stats_{self.request.user.id}'
        stats = cache.get(cache_key)
        
        if stats is None:
            stats = self._calculate_stats()
            cache.set(cache_key, stats, 300)  # 5 minutos
        
        context['stats'] = stats
        return context
    
    def _calculate_stats(self) -> Dict[str, Any]:
        """Calcula estatísticas (operação pesada)."""
        return {
            'total_products': Product.objects.count(),
            'low_stock': Product.objects.filter(
                current_stock__lt=models.F('min_stock')
            ).count(),
            # ... outras estatísticas
        }

# produtos/viewsets.py
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet de produtos com cache."""
    
    @method_decorator(cache_page(60))  # Cache de 1 minuto
    def list(self, request, *args, **kwargs):
        """Lista produtos com cache."""
        return super().list(request, *args, **kwargs)
```

**3.2. Corrigir N+1 Queries (6h)**
```python
# core/views.py
from typing import Any
from django.db.models import QuerySet

class AuditLogListView(ListView):
    """Lista de logs de auditoria otimizada."""
    
    model = AuditLog
    template_name = 'audit/logs_list.html'
    paginate_by = 50
    
    def get_queryset(self) -> QuerySet:
        """Obtém queryset otimizado."""
        return AuditLog.objects.select_related(
            'user',
            'content_type'
        ).prefetch_related(
            'user__perfil'
        ).order_by('-created_at')
```

**3.3. Adicionar Índices de Banco de Dados (4h)**
```python
# movimentacoes/models.py
from typing import Optional
from django.db import models

class InventoryMovement(TimeStampedModel):
    """Movimentação de inventário com índices otimizados."""
    
    # ... campos existentes ...
    
    class Meta:
        verbose_name = "Movimentação de Inventário"
        verbose_name_plural = "Movimentações de Inventário"
        ordering = ['-movement_date', '-created_at']
        indexes = [
            models.Index(
                fields=['product', 'movement_type', 'movement_date'],
                name='inv_mov_prod_type_date_idx'
            ),
            models.Index(
                fields=['movement_date', '-created_at'],
                name='inv_mov_date_created_idx'
            ),
            models.Index(
                fields=['user', 'movement_date'],
                name='inv_mov_user_date_idx'
            ),
        ]

# core/models.py
class AuditLog(models.Model):
    """Log de auditoria com índices otimizados."""
    
    # ... campos existentes ...
    
    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['content_type', 'object_id', 'created_at'],
                name='audit_log_ct_obj_date_idx'
            ),
            models.Index(
                fields=['user', 'action', 'created_at'],
                name='audit_log_user_action_idx'
            ),
            models.Index(
                fields=['created_at'],
                name='audit_log_created_idx'
            ),
        ]
```

**3.4. Minificação e Code Splitting (8h)**
```javascript
// webpack.config.js
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
    optimization: {
        minimize: true,
        minimizer: [
            new TerserPlugin({
                terserOptions: {
                    compress: {
                        drop_console: true,
                    },
                },
            }),
            new CssMinimizerPlugin(),
        ],
        splitChunks: {
            chunks: 'all',
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    priority: 10,
                },
                common: {
                    minChunks: 2,
                    priority: 5,
                    reuseExistingChunk: true,
                },
            },
        },
    },
};
```

**3.6. Monitoramento APM (6h)**
```python
# siteares/settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True,
    environment='production',
)
```

---

### 4. QUALIDADE DE CÓDIGO: 8.5 → 10.0 (🟡 Média - 40h)

#### Ações Necessárias

**4.1. Adicionar Type Hints Completos (20h)**

Já mostrei exemplos acima. Aplicar em TODOS os arquivos:
- ✅ models.py
- ✅ views.py
- ✅ serializers.py
- ✅ forms.py
- ✅ utils.py

**4.2. Refatorar Funções Complexas (8h)**
```python
# movimentacoes/views.py
from typing import Dict, Any, Optional
from django.http import HttpRequest

class MovementCreateView(CreateView):
    """Criação de movimentação refatorada."""
    
    def form_valid(self, form: forms.Form) -> HttpResponse:
        """Processa formulário válido (complexidade reduzida)."""
        movement = form.save(commit=False)
        movement.user = self.request.user
        
        self._validate_stock_availability(movement)
        self._update_product_stock(movement)
        movement.save()
        
        self._create_audit_log(movement)
        messages.success(self.request, "Movimentação criada com sucesso!")
        
        return redirect('movimentacoes:list')
    
    def _validate_stock_availability(self, movement: InventoryMovement) -> None:
        """Valida disponibilidade de estoque para saídas."""
        if movement.movement_type == 'SAIDA':
            if movement.product.current_stock < movement.quantity:
                raise ValidationError("Estoque insuficiente")
    
    def _update_product_stock(self, movement: InventoryMovement) -> None:
        """Atualiza estoque do produto."""
        product = movement.product
        
        if movement.movement_type == 'ENTRADA':
            product.current_stock += movement.quantity
        else:
            product.current_stock -= movement.quantity
        
        product.save()
    
    def _create_audit_log(self, movement: InventoryMovement) -> None:
        """Cria log de auditoria."""
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE',
            content_object=movement,
            changes={'status': 'created'}
        )
```

**4.3. Adicionar Docstrings Completas (8h)**
```python
# produtos/models.py
from typing import Optional
from datetime import date

class Product(SoftDeleteModel, TimeStampedModel):
    """
    Modelo de produto do sistema de estoque.
    
    Representa um produto comercializável com controle de estoque,
    preços e informações adicionais como data de validade.
    
    Attributes:
        name: Nome do produto (máximo 200 caracteres)
        sku: Código único de identificação (Stock Keeping Unit)
        category: Categoria do produto (ForeignKey para Category)
        unit: Unidade de medida (ForeignKey para Unit)
        current_stock: Quantidade atual em estoque
        min_stock: Estoque mínimo para alerta
        unit_price: Preço unitário do produto
        expiry_date: Data de validade (opcional)
        image: Imagem do produto (opcional)
        description: Descrição detalhada (opcional)
        
    Methods:
        is_low_stock(): Verifica se está abaixo do estoque mínimo
        is_expired(): Verifica se está vencido
        get_total_value(): Calcula valor total do estoque
        
    Examples:
        >>> product = Product.objects.create(
        ...     name="Arroz 5kg",
        ...     sku="ARR-001",
        ...     current_stock=100,
        ...     min_stock=20,
        ...     unit_price=Decimal("25.90")
        ... )
        >>> product.is_low_stock()
        False
        >>> product.get_total_value()
        Decimal('2590.00')
    """
    
    name: str = models.CharField(
        max_length=200,
        verbose_name="Nome",
        help_text="Nome completo do produto"
    )
    
    def is_low_stock(self) -> bool:
        """
        Verifica se o produto está com estoque baixo.
        
        Compara o estoque atual com o estoque mínimo configurado.
        Útil para alertas automáticos e reposição.
        
        Returns:
            bool: True se current_stock < min_stock, False caso contrário
            
        Examples:
            >>> product = Product(current_stock=15, min_stock=20)
            >>> product.is_low_stock()
            True
        """
        return self.current_stock < self.min_stock
```

**4.4. Remover Magic Numbers (2h)**
```python
# core/constants.py
"""Constantes do sistema."""
from typing import Final

# Limites de estoque
MIN_STOCK_THRESHOLD: Final[int] = 10
LOW_STOCK_PERCENTAGE: Final[float] = 0.2

# Paginação
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100

# Cache timeouts (segundos)
CACHE_TIMEOUT_SHORT: Final[int] = 60  # 1 minuto
CACHE_TIMEOUT_MEDIUM: Final[int] = 300  # 5 minutos
CACHE_TIMEOUT_LONG: Final[int] = 3600  # 1 hora

# Rate limiting
RATE_LIMIT_ANON: Final[str] = '100/hour'
RATE_LIMIT_AUTHENTICATED: Final[str] = '1000/hour'
RATE_LIMIT_SENSITIVE: Final[str] = '10/minute'

# Usar nas views
from core.constants import CACHE_TIMEOUT_MEDIUM

@cache_page(CACHE_TIMEOUT_MEDIUM)
def dashboard_view(request):
    ...
```

**4.5. Configurar Pre-commit Hooks (2h)**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.10
        
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203,W503']
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

### 5. ARQUITETURA: 9.0 → 10.0 (🟡 Média - 15h)

#### Ações Necessárias

**5.1. Resolver Dependências Circulares (6h)**
```python
# core/signals.py - Remover imports circulares
from typing import Any, Type
from django.db.models import Model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

def register_audit_signals(model: Type[Model]) -> None:
    """Registra signals de auditoria para um model dinamicamente."""
    
    @receiver(post_save, sender=model)
    def log_save(sender: Type[Model], instance: Model, created: bool, **kwargs: Any) -> None:
        """Log de criação/atualização."""
        from core.models import AuditLog  # Import local
        
        action = 'CREATE' if created else 'UPDATE'
        AuditLog.objects.create(
            user=getattr(instance, 'updated_by', None),
            action=action,
            content_object=instance
        )

# Em cada app/apps.py
from django.apps import AppConfig

class ProdutosConfig(AppConfig):
    name = 'produtos'
    
    def ready(self) -> None:
        """Registra signals ao iniciar o app."""
        from core.signals import register_audit_signals
        from produtos.models import Product, Category, Unit
        
        for model in [Product, Category, Unit]:
            register_audit_signals(model)
```

**5.2. Refatorar Core App (6h)**
```
core/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── base.py         # TimeStampedModel, SoftDeleteModel
│   ├── user.py         # PerfilUsuario
│   └── audit.py        # AuditLog
├── views/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── audit.py
│   └── user.py
├── permissions/
│   ├── __init__.py
│   ├── base.py
│   └── decorators.py
└── utils/
    ├── __init__.py
    ├── cache.py
    └── validators.py
```

**5.3. Documentar Arquitetura (3h)**
```markdown
# docs/ARQUITETURA.md

## Diagrama de Camadas

```
┌─────────────────────────────────────────────────────┐
│                 Presentation Layer                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │Templates │  │   Views  │  │ ViewSets │       │
│   └──────────┘  └──────────┘  └──────────┘       │
├─────────────────────────────────────────────────────┤
│                Business Logic Layer                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │  Models  │  │  Forms   │  │Serializer│       │
│   └──────────┘  └──────────┘  └──────────┘       │
├─────────────────────────────────────────────────────┤
│                 Data Access Layer                    │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │    ORM   │  │ Managers │  │QuerySets │       │
│   └──────────┘  └──────────┘  └──────────┘       │
├─────────────────────────────────────────────────────┤
│                  Infrastructure                      │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │PostgreSQL│  │  Redis   │  │  S3/FS   │       │
│   └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────┘
```
```

---

## 📅 CRONOGRAMA DE IMPLEMENTAÇÃO

### Fase 1: Melhorias Críticas (Semana 1-4)
- **Semana 1:** Testes Unitários (60h)
- **Semana 2:** Testes de Integração (40h)
- **Semana 3:** Segurança (2FA, CSP, Rate Limiting) (30h)
- **Semana 4:** Performance (Redis Cache, Índices) (30h)

### Fase 2: Melhorias Importantes (Semana 5-6)
- **Semana 5:** Testes E2E, Type Hints, Refatoração (40h)
- **Semana 6:** Docstrings, Pre-commit, Arquitetura (30h)

### Fase 3: Validação (Semana 7-8)
- **Semana 7:** Testes de Performance, Pentest (30h)
- **Semana 8:** CI/CD, Monitoramento, Documentação (20h)

**Total:** 280 horas (7-8 semanas com 2 desenvolvedores)

---

## 💰 ESTIMATIVA DE CUSTO

| Categoria | Horas | Taxa/hora | Subtotal |
|-----------|-------|-----------|----------|
| Desenvolvimento (Testes) | 140h | R$ 150 | R$ 21,000 |
| Desenvolvimento (Segurança) | 50h | R$ 150 | R$ 7,500 |
| Desenvolvimento (Performance) | 40h | R$ 150 | R$ 6,000 |
| Desenvolvimento (Qualidade) | 40h | R$ 150 | R$ 6,000 |
| Infraestrutura (Redis, Sentry) | - | - | R$ 800/mês |
| Pentest Externo | - | - | R$ 8,000 |
| **TOTAL** | **270h** | - | **R$ 49,300** |

---

## 🎯 RESULTADO ESPERADO

### Após Implementação Completa

| Categoria | Antes | Depois | Melhoria |
|-----------|-------|--------|----------|
| Arquitetura | 9.0 | 10.0 | +11% |
| Qualidade | 8.5 | 10.0 | +18% |
| Segurança | 8.0 | 10.0 | +25% |
| Performance | 9.0 | 10.0 | +11% |
| Documentação | 10.0 | 10.0 | 0% |
| Testes | 2.0 | 10.0 | +400% |
| **MÉDIA** | **7.8** | **10.0** | **+28%** |

**Status Final:** 🌟 **EXCELENTE** - Projeto production-ready de classe mundial!

---

**Preparado por:** Tech Lead  
**Aprovado por:** Gerente de Projeto  
**Data:** 26/11/2025  
**Versão:** 1.0
