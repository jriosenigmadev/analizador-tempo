# 🚀 Guía de Deploy: Dashboard Tempo

## Opción 1: Streamlit Cloud ⭐ (Recomendado)

**Ventajas:**
- Gratuito
- Diseñado específicamente para Streamlit
- Deploy en 5 minutos
- Soporte oficial
- Uptime garantizado

### Pasos:

1. **Sube tu código a GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/extraercalendar.git
   git push -u origin main
   ```

2. **Ve a [Streamlit Cloud](https://share.streamlit.io/)**

3. **Haz click en "New app"**

4. **Completa los datos:**
   - Repository: `TU_USUARIO/extraercalendar`
   - Branch: `main`
   - Main file path: `app.py`

5. **Deploy automático en segundos**

### Cambiar contraseñas en Streamlit Cloud:

En el archivo `config.yaml`, edita los usuarios:

```yaml
credentials:
  usernames:
    admin:
      email: tu_email@example.com
      name: Tu Nombre
      password: tu_contraseña_segura  # ⚠️ CAMBIAR
    otro_usuario:
      email: otro@example.com
      name: Otro Usuario
      password: otra_contraseña  # ⚠️ CAMBIAR
```

Luego push a GitHub y Streamlit Cloud redeploy automáticamente.

---

## Opción 2: Railway.app (Alternativa Gratuita)

### Pasos:

1. **Ve a [Railway](https://railway.app)**
2. **Login con GitHub**
3. **Click en "New Project" → "Deploy from GitHub repo"**
4. **Selecciona tu repositorio**
5. **Agrega variables de entorno:**
   - No necesitas agregar nada especial
   - El `config.yaml` es local
6. **Deploy automático**

---

## Opción 3: Render.com (Alternativa)

Similar a Railway pero con UI más amigable.

---

## 🔐 Seguridad: Cambiar Contraseñas

### Para usuarios locales:
Edita `config.yaml`:
```yaml
credentials:
  usernames:
    admin:
      password: nueva_contraseña_segura
```

### Para Streamlit Cloud:
1. Edita `config.yaml` en tu repo
2. Haz commit y push a GitHub
3. Streamlit Cloud redeploy automáticamente

---

## ⚙️ Variables de Entorno (Tempo y Jira)

Si no quieres dejar credenciales en el código, crea un archivo `.streamlit/secrets.toml` (LOCAL, no en GitHub):

```toml
tempo_api_token = "tu_token_aqui"
jira_email = "tu_email@example.com"
jira_token = "tu_token_jira"
```

Luego actualiza `app.py` para leerlas:
```python
tempo_token = st.secrets.get("tempo_api_token", "")
```

---

## 📋 Checklist Antes de Deploy

- [ ] Cambiar contraseñas en `config.yaml`
- [ ] Agregar usuarios reales (editar `config.yaml`)
- [ ] Revisar que `requirements.txt` está actualizado
- [ ] Probar localmente: `streamlit run app.py`
- [ ] Subir código a GitHub
- [ ] Deploy en Streamlit Cloud

---

## Usuarios de Prueba (por defecto)

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin123` | Administrador |
| `usuario` | `demo123` | Usuario Demo |

⚠️ **Cambiar INMEDIATAMENTE después de desplegar**
