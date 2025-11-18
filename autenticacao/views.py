"""Views de Autenticação."""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def user_login(request):
    """View de login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'🎉 Bem-vindo(a), {user.get_full_name() or user.username}!')
                    
                    # Redirecionar para a página solicitada ou dashboard
                    next_page = request.GET.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect('dashboard:index')
                else:
                    messages.error(request, '❌ Sua conta está desativada. Entre em contato com o administrador.')
            else:
                messages.error(request, '❌ Usuário ou senha incorretos. Tente novamente.')
        else:
            messages.error(request, '⚠️ Por favor, preencha todos os campos.')
    
    return render(request, 'autenticacao/login.html')


@login_required
def user_logout(request):
    """View de logout."""
    logout(request)
    return redirect('autenticacao:login')


def recuperar_senha(request):
    """View de recuperação de senha (placeholder)."""
    messages.info(request, '🔧 Funcionalidade em desenvolvimento. Entre em contato com o administrador.')
    return redirect('autenticacao:login')
