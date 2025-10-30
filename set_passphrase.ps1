# Script para configurar la passphrase de OCI
# Ejecutar este script antes de ejecutar deploy_oci.py

Write-Host "Configurando passphrase para OCI..." -ForegroundColor Green

# Solicitar la passphrase de forma segura
$passphrase = Read-Host "Ingrese la passphrase de su clave privada OCI" -AsSecureString

# Convertir SecureString a texto plano
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($passphrase)
$plaintext = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Establecer la variable de entorno
[Environment]::SetEnvironmentVariable("OCI_KEY_PASSPHRASE", $plaintext, "Process")

Write-Host "Passphrase configurada para esta sesión." -ForegroundColor Green
Write-Host "Ahora puede ejecutar: python src/deploy_oci.py" -ForegroundColor Yellow

