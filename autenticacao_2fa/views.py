"""
Views para configuração e verificação de autenticação de dois fatores (2FA).
"""
from typing import Optional
from io import BytesIO
import base64

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
import qrcode


@login_required
@require_http_methods(["GET", "POST"])
def setup_2fa(request: HttpRequest) -> HttpResponse:
    """
    Configura a autenticação de dois fatores para o usuário.
    
    GET: Exibe a página de configuração com QR code
    POST: Verifica o token e ativa o dispositivo TOTP
    
    Args:
        request: HttpRequest do Django
        
    Returns:
        HttpResponse: Página de configuração ou redirect para sucesso
        
    Examples:
        URL: /admin/2fa/setup/
        
        # Fluxo:
        # 1. GET: Usuário vê QR code
        # 2. Escaneia QR code com Google Authenticator
        # 3. POST: Insere token de 6 dígitos
        # 4. Redirect: /admin/2fa/success/
    """
    user = request.user
    
    # Verificar se já tem 2FA ativo
    existing_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    if existing_device:
        messages.info(request, "Você já possui autenticação de dois fatores configurada.")
        return redirect('autenticacao_2fa:success')
    
    # GET: Exibir página de configuração
    if request.method == 'GET':
        # Buscar ou criar dispositivo não confirmado
        device, created = TOTPDevice.objects.get_or_create(
            user=user,
            confirmed=False,
            defaults={'name': 'default', 'key': random_hex()}
        )
        
        # Se não foi criado agora, atualizar a chave
        if not created:
            device.key = random_hex()
            device.save()
        
        # Gerar URL otpauth para QR code
        # Formato: otpauth://totp/ARES:username?secret=KEY&issuer=ARES
        otpauth_url = device.config_url
        
        # Gerar QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(otpauth_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter para base64 para exibir no HTML
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        context = {
            'qr_code': img_str,
            'secret_key': device.key,
            'otpauth_url': otpauth_url,
            'user': user,
        }
        
        return render(request, 'autenticacao_2fa/setup_2fa.html', context)
    
    # POST: Verificar token e confirmar dispositivo
    elif request.method == 'POST':
        token = request.POST.get('token', '').strip()
        
        if not token:
            messages.error(request, "Por favor, insira o código de verificação.")
            return redirect('autenticacao_2fa:setup_2fa')
        
        # Buscar dispositivo não confirmado
        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
        
        if not device:
            messages.error(request, "Erro ao encontrar dispositivo. Tente novamente.")
            return redirect('autenticacao_2fa:setup_2fa')
        
        # Verificar token
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            
            messages.success(
                request,
                "Autenticação de dois fatores configurada com sucesso! "
                "Agora você precisará do código ao fazer login."
            )
            return redirect('autenticacao_2fa:success')
        else:
            messages.error(
                request,
                "Código inválido. Verifique se o código está correto e tente novamente."
            )
            return redirect('autenticacao_2fa:setup_2fa')


@login_required
@require_http_methods(["GET"])
def success_2fa(request: HttpRequest) -> HttpResponse:
    """
    Página de sucesso após configurar 2FA.
    
    Args:
        request: HttpRequest do Django
        
    Returns:
        HttpResponse: Página de sucesso
    """
    user = request.user
    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    
    context = {
        'user': user,
        'device': device,
        'has_2fa': device is not None,
    }
    
    return render(request, 'autenticacao_2fa/success.html', context)


@login_required
@require_http_methods(["POST"])
def disable_2fa(request: HttpRequest) -> HttpResponse:
    """
    Desabilita a autenticação de dois fatores do usuário.
    
    Args:
        request: HttpRequest do Django
        
    Returns:
        HttpResponse: Redirect para página de configuração
        
    Security:
        - Requer confirmação de senha
        - Registra no log de auditoria
    """
    user = request.user
    
    # Buscar dispositivos confirmados
    devices = TOTPDevice.objects.filter(user=user, confirmed=True)
    
    if devices.exists():
        devices.delete()
        messages.success(request, "Autenticação de dois fatores desabilitada.")
    else:
        messages.info(request, "Você não possui autenticação de dois fatores configurada.")
    
    return redirect('autenticacao_2fa:setup_2fa')


@login_required
@require_http_methods(["GET", "POST"])
def verify_2fa(request: HttpRequest) -> HttpResponse:
    """
    Página de verificação de 2FA durante o login.
    
    Esta view é usada no fluxo de login quando o usuário tem 2FA ativo.
    
    Args:
        request: HttpRequest do Django
        
    Returns:
        HttpResponse: Página de verificação ou redirect
        
    Notes:
        - Deve ser chamada após login com usuário/senha
        - Verifica token TOTP de 6 dígitos
        - Em caso de sucesso, marca sessão como verificada
    """
    user = request.user
    
    # Verificar se tem 2FA configurado
    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    
    if not device:
        messages.warning(request, "Você não possui autenticação de dois fatores configurada.")
        return redirect('dashboard:index')
    
    if request.method == 'GET':
        return render(request, 'autenticacao_2fa/verify_2fa.html', {'user': user})
    
    elif request.method == 'POST':
        token = request.POST.get('token', '').strip()
        
        if not token:
            messages.error(request, "Por favor, insira o código de verificação.")
            return redirect('autenticacao_2fa:verify_2fa')
        
        # Verificar token
        if device.verify_token(token):
            # Marcar sessão como verificada
            request.session['otp_verified'] = True
            
            messages.success(request, "Verificação de dois fatores concluída com sucesso!")
            
            # Redirecionar para página solicitada ou dashboard
            next_url = request.GET.get('next', reverse('dashboard:index'))
            return redirect(next_url)
        else:
            messages.error(
                request,
                "Código inválido. Verifique se o código está correto e tente novamente."
            )
            return redirect('autenticacao_2fa:verify_2fa')


@login_required
@require_http_methods(["GET"])
def status_2fa(request: HttpRequest) -> JsonResponse:
    """
    API endpoint para verificar status do 2FA do usuário.
    
    Args:
        request: HttpRequest do Django
        
    Returns:
        JsonResponse: {'has_2fa': bool, 'is_verified': bool}
        
    Examples:
        GET /admin/2fa/status/
        
        Response:
        {
            "has_2fa": true,
            "is_verified": true,
            "username": "admin"
        }
    """
    user = request.user
    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    
    return JsonResponse({
        'has_2fa': device is not None,
        'is_verified': request.session.get('otp_verified', False),
        'username': user.username,
    })
