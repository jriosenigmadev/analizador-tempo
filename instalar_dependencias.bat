@echo off
echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
echo.
echo ✓ Instalación completada
pause