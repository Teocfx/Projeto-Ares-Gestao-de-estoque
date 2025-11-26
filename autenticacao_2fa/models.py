"""
Models para autenticacao_2fa.

Os modelos TOTP são fornecidos pelo django-otp.plugins.otp_totp:
- TOTPDevice: Dispositivo TOTP associado a um usuário
"""
from django.db import models

# Usamos os modelos do django-otp diretamente
# from django_otp.plugins.otp_totp.models import TOTPDevice
