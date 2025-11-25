"""
Script para criar perfis de acesso para os usuários de teste.

Usage:
    python manage.py shell < scripts/create_perfis.py
    
Ou:
    Get-Content scripts/create_perfis.py | python manage.py shell
"""
from django.contrib.auth.models import User
from core.models import PerfilUsuario, PerfilAcesso
from datetime import date, timedelta

print("=" * 70)
print("CRIANDO PERFIS DE ACESSO PARA USUÁRIOS")
print("=" * 70)

# Buscar ou criar usuários
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@ares.com',
        'first_name': 'Administrador',
        'last_name': 'Sistema',
        'is_staff': True,
        'is_superuser': True
    }
)
admin_user.set_password('admin123')
admin_user.save()

joao_user, _ = User.objects.get_or_create(
    username='joao',
    defaults={
        'email': 'joao@ares.com',
        'first_name': 'João',
        'last_name': 'Silva',
        'is_staff': True
    }
)
joao_user.set_password('senha123')
joao_user.save()

maria_user, _ = User.objects.get_or_create(
    username='maria',
    defaults={
        'email': 'maria@ares.com',
        'first_name': 'Maria',
        'last_name': 'Santos',
        'is_staff': True
    }
)
maria_user.set_password('senha123')
maria_user.save()

carlos_user, created = User.objects.get_or_create(
    username='carlos',
    defaults={
        'email': 'carlos@ares.com',
        'first_name': 'Carlos',
        'last_name': 'Operador',
        'is_staff': False
    }
)
if created:
    carlos_user.set_password('senha123')
    carlos_user.save()

print(f"\n✅ Usuários configurados:")
print(f"   - admin (Superuser)")
print(f"   - joao (Staff)")
print(f"   - maria (Staff)")
print(f"   - carlos (Regular)")

# Criar ou atualizar perfis
print("\n" + "=" * 70)
print("CONFIGURANDO PERFIS DE ACESSO")
print("=" * 70)

# Admin = Representante Legal
perfil_admin, created = PerfilUsuario.objects.update_or_create(
    user=admin_user,
    defaults={
        'perfil': PerfilAcesso.REPRESENTANTE_LEGAL,
        'ativo': True,
        'observacoes': 'Administrador do sistema com acesso total'
    }
)
print(f"\n{'✨ Criado' if created else '🔄 Atualizado'}: {perfil_admin}")

# João = Representante Delegado
perfil_joao, created = PerfilUsuario.objects.update_or_create(
    user=joao_user,
    defaults={
        'perfil': PerfilAcesso.REPRESENTANTE_DELEGADO,
        'ativo': True,
        'autorizado_por': admin_user,
        'observacoes': 'Representante delegado com permissões administrativas limitadas'
    }
)
print(f"{'✨ Criado' if created else '🔄 Atualizado'}: {perfil_joao}")

# Maria = Representante Delegado
perfil_maria, created = PerfilUsuario.objects.update_or_create(
    user=maria_user,
    defaults={
        'perfil': PerfilAcesso.REPRESENTANTE_DELEGADO,
        'ativo': True,
        'autorizado_por': admin_user,
        'data_expiracao': date.today() + timedelta(days=90),  # Expira em 90 dias
        'observacoes': 'Representante delegado temporário (90 dias)'
    }
)
print(f"{'✨ Criado' if created else '🔄 Atualizado'}: {perfil_maria}")

# Carlos = Operador
perfil_carlos, created = PerfilUsuario.objects.update_or_create(
    user=carlos_user,
    defaults={
        'perfil': PerfilAcesso.OPERADOR,
        'ativo': True,
        'autorizado_por': admin_user,
        'permissoes_customizadas': {
            'visualizar_relatorios': True,
            'editar_produtos': False,  # Operador padrão não pode editar
        },
        'observacoes': 'Operador com acesso básico ao sistema'
    }
)
print(f"{'✨ Criado' if created else '🔄 Atualizado'}: {perfil_carlos}")

print("\n" + "=" * 70)
print("RESUMO DOS PERFIS")
print("=" * 70)

print(f"\n📊 Total de perfis criados: {PerfilUsuario.objects.count()}")
print(f"   - Representante Legal: {PerfilUsuario.objects.filter(perfil=PerfilAcesso.REPRESENTANTE_LEGAL).count()}")
print(f"   - Representante Delegado: {PerfilUsuario.objects.filter(perfil=PerfilAcesso.REPRESENTANTE_DELEGADO).count()}")
print(f"   - Operador: {PerfilUsuario.objects.filter(perfil=PerfilAcesso.OPERADOR).count()}")

print("\n" + "=" * 70)
print("CREDENCIAIS DE ACESSO")
print("=" * 70)

print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║                    REPRESENTANTE LEGAL                            ║
╠═══════════════════════════════════════════════════════════════════╣
║ Username: admin                                                   ║
║ Password: admin123                                                ║
║ Perfil:   Representante Legal (Acesso Total)                     ║
║ Pode:     - Gerenciar usuários                                    ║
║           - Aprovar movimentações                                 ║
║           - Editar produtos                                       ║
║           - Gerar relatórios                                      ║
║           - Alterar configurações                                 ║
║           - Visualizar logs                                       ║
║           - Excluir registros                                     ║
╚═══════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════╗
║                  REPRESENTANTE DELEGADO (João)                    ║
╠═══════════════════════════════════════════════════════════════════╣
║ Username: joao                                                    ║
║ Password: senha123                                                ║
║ Perfil:   Representante Delegado (Admin Limitado)                ║
║ Pode:     - Aprovar movimentações                                 ║
║           - Editar produtos                                       ║
║           - Gerar relatórios                                      ║
║           - Visualizar logs                                       ║
║ NÃO Pode: - Gerenciar usuários                                    ║
║           - Alterar configurações                                 ║
║           - Excluir registros                                     ║
╚═══════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════╗
║                 REPRESENTANTE DELEGADO (Maria)                    ║
╠═══════════════════════════════════════════════════════════════════╣
║ Username: maria                                                   ║
║ Password: senha123                                                ║
║ Perfil:   Representante Delegado TEMPORÁRIO (90 dias)            ║
║ Expira:   {perfil_maria.data_expiracao.strftime('%d/%m/%Y')}                                            ║
║ Pode:     - Aprovar movimentações                                 ║
║           - Editar produtos                                       ║
║           - Gerar relatórios                                      ║
║           - Visualizar logs                                       ║
╚═══════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════╗
║                         OPERADOR (Carlos)                         ║
╠═══════════════════════════════════════════════════════════════════╣
║ Username: carlos                                                  ║
║ Password: senha123                                                ║
║ Perfil:   Operador (Acesso Básico)                               ║
║ Pode:     - Visualizar relatórios                                 ║
║           - Consultar produtos                                    ║
║           - Consultar movimentações                               ║
║ NÃO Pode: - Editar produtos                                       ║
║           - Aprovar movimentações                                 ║
║           - Gerar relatórios                                      ║
║           - Gerenciar usuários                                    ║
╚═══════════════════════════════════════════════════════════════════╝
""")

print("=" * 70)
print("✅ PERFIS CRIADOS COM SUCESSO!")
print("=" * 70)
print("\n💡 Para acessar o sistema:")
print("   1. Inicie o servidor: python manage.py runserver")
print("   2. Acesse: http://127.0.0.1:8000/admin/")
print("   3. Faça login com uma das credenciais acima")
print("\n")
