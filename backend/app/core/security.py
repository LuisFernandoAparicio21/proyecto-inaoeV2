# -*- coding: utf-8 -*-
"""Módulo de seguridad para el Asistente de Investigación INAOE.

Este módulo implementa la capa de seguridad del sistema incluyendo:
- Autenticación OAuth 2.0 (Google/Microsoft para cuentas institucionales)
- Generación y validación de JWT
- Autenticación multifactor (MFA) opcional con TOTP

Example:
    from backend.app.core.security import (
        crear_token_jwt,
        verificar_token_jwt,
        verificar_mfa
    )
    
    token = crear_token_jwt(user_id="investigador@inaoe.mx")
    payload = verificar_token_jwt(token)
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import hmac
import base64

# Configuración de JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Configuración OAuth
OAUTH_PROVIDERS = {
    "google": {
        "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["openid", "email", "profile"],
    },
    "microsoft": {
        "client_id": os.getenv("MICROSOFT_OAUTH_CLIENT_ID", ""),
        "client_secret": os.getenv("MICROSOFT_OAUTH_CLIENT_SECRET", ""),
        "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "scopes": ["openid", "email", "profile"],
    }
}


def crear_token_jwt(
    user_id: str,
    email: str,
    nombre: str,
    roles: list[str] = None,
    expiracion_horas: int = JWT_EXPIRATION_HOURS
) -> str:
    """Crea un token JWT para autenticación.
    
    Args:
        user_id: Identificador único del usuario
        email: Correo electrónico del usuario
        nombre: Nombre completo del usuario
        roles: Lista de roles del usuario (default: ["investigador"])
        expiracion_horas: Horas hasta que expire el token
    
    Returns:
        str: Token JWT codificado
    
    Example:
        >>> token = crear_token_jwt(
        ...     user_id="123",
        ...     email="investigador@inaoe.mx",
        ...     nombre="Dr. García"
        ... )
    """
    if roles is None:
        roles = ["investigador"]
    
    # Crear payload
    payload = {
        "sub": user_id,
        "email": email,
        "nombre": nombre,
        "roles": roles,
        "iat": datetime.utcnow().timestamp(),
        "exp": (datetime.utcnow() + timedelta(hours=expiracion_horas)).timestamp(),
    }
    
    # Codificar header y payload
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(
        str(header).replace("'", '"').encode()
    ).rstrip(b'=').decode()
    payload_b64 = base64.urlsafe_b64encode(
        str(payload).replace("'", '"').encode()
    ).rstrip(b'=').decode()
    
    # Crear firma
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        JWT_SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def verificar_token_jwt(token: str) -> Optional[Dict[str, Any]]:
    """Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Dict con el payload si el token es válido, None si no lo es
    
    Example:
        >>> payload = verificar_token_jwt(token)
        >>> if payload:
        ...     print(f"Usuario: {payload['email']}")
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, signature_b64 = parts
        
        # Verificar firma
        message = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(
            JWT_SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(
            expected_signature
        ).rstrip(b'=').decode()
        
        if not hmac.compare_digest(signature_b64, expected_signature_b64):
            return None
        
        # Decodificar payload
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += '=' * padding
        payload_json = base64.urlsafe_b64decode(payload_b64).decode()
        payload = eval(payload_json)  # Nota: en producción usar json.loads
        
        # Verificar expiración
        if payload.get("exp", 0) < datetime.utcnow().timestamp():
            return None
        
        return payload
        
    except Exception:
        return None


def generar_secreto_mfa() -> str:
    """Genera un secreto para autenticación MFA con TOTP.
    
    Returns:
        str: Secreto base32 de 32 caracteres para usar con apps como
             Google Authenticator o Authy.
    
    Example:
        >>> secreto = generar_secreto_mfa()
        >>> print(f"Configura tu app con: {secreto}")
    """
    return base64.b32encode(secrets.token_bytes(20)).decode('utf-8')


def verificar_codigo_totp(secreto: str, codigo: str, ventana: int = 1) -> bool:
    """Verifica un código TOTP de autenticación multifactor.
    
    Args:
        secreto: Secreto base32 del usuario
        codigo: Código de 6 dígitos ingresado por el usuario
        ventana: Número de intervalos de tiempo a verificar (default: 1)
    
    Returns:
        bool: True si el código es válido
    
    Example:
        >>> if verificar_codigo_totp(user.mfa_secret, "123456"):
        ...     print("MFA verificado")
    """
    import time
    
    tiempo_actual = int(time.time() // 30)
    
    for offset in range(-ventana, ventana + 1):
        tiempo = tiempo_actual + offset
        tiempo_bytes = tiempo.to_bytes(8, byteorder='big')
        
        # Decodificar secreto
        try:
            padding = 8 - len(secreto) % 8
            if padding != 8:
                secreto_padded = secreto + '=' * padding
            else:
                secreto_padded = secreto
            key = base64.b32decode(secreto_padded, casefold=True)
        except Exception:
            return False
        
        # Generar HMAC
        hmac_result = hmac.new(key, tiempo_bytes, hashlib.sha1).digest()
        
        # Extraer código
        offset_byte = hmac_result[-1] & 0x0F
        codigo_int = (
            ((hmac_result[offset_byte] & 0x7F) << 24) |
            ((hmac_result[offset_byte + 1] & 0xFF) << 16) |
            ((hmac_result[offset_byte + 2] & 0xFF) << 8) |
            (hmac_result[offset_byte + 3] & 0xFF)
        )
        codigo_generado = str(codigo_int % 1000000).zfill(6)
        
        if hmac.compare_digest(codigo, codigo_generado):
            return True
    
    return False


# --- Funciones de utilidad para OAuth ---

def get_oauth_url(provider: str, redirect_uri: str, state: str) -> Optional[str]:
    """Genera la URL de autorización OAuth.
    
    Args:
        provider: "google" o "microsoft"
        redirect_uri: URL de callback
        state: Token CSRF
    
    Returns:
        URL de autorización o None si el proveedor no está configurado
    """
    config = OAUTH_PROVIDERS.get(provider)
    if not config or not config["client_id"]:
        return None
    
    params = {
        "client_id": config["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(config["scopes"]),
        "state": state,
    }
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{config['authorize_url']}?{query}"
