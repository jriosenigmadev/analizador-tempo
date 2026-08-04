import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta
import calendar
import base64
import plotly.express as px
import plotly.graph_objects as go
import streamlit_authenticator as stauth
import yaml
from pathlib import Path

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Dashboard Financiero Tempo", layout="wide", page_icon="⏱️")

# Función para aplicar tema empresarial claro
def aplicar_tema_empresarial():
    """Aplica CSS profesional y empresarial a la aplicación"""
    css = """
    <style>
        /* ===== VARIABLES Y BASE ===== */
        :root {
            --primary-color: #003d99;
            --primary-light: #0066cc;
            --primary-dark: #002e73;
            --accent-color: #0099ff;
            --bg-main: #f8f9fb;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f0f4f8;
            --text-primary: #1a1a1a;
            --text-secondary: #505050;
            --border-color: #d0d8e0;
            --shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.12);
        }

        /* ===== APP GENERAL ===== */
        [data-testid="stApp"] {
            background-color: var(--bg-main) !important;
        }

        body {
            background-color: var(--bg-main) !important;
            color: var(--text-primary) !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }

        /* ===== SIDEBAR ===== */
        [data-testid="stSidebar"] {
            background-color: var(--bg-secondary) !important;
            border-right: 1px solid var(--border-color);
        }

        [data-testid="stSidebar"] .stMarkdown {
            color: var(--text-primary) !important;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--primary-color) !important;
            font-weight: 600;
        }

        /* ===== HEADER Y TÍTULOS ===== */
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-color) !important;
            font-weight: 600 !important;
        }

        .stMarkdown h1 {
            font-size: 2.2em !important;
            margin-bottom: 0.5em !important;
            border-bottom: 3px solid var(--primary-light);
            padding-bottom: 0.3em;
        }

        .stMarkdown h2 {
            font-size: 1.6em !important;
            margin-top: 1.2em !important;
            margin-bottom: 0.6em !important;
            color: var(--primary-dark) !important;
        }

        .stMarkdown h3 {
            font-size: 1.2em !important;
            margin-top: 0.8em !important;
            color: var(--primary-color) !important;
        }

        /* ===== TEXTO GENERAL ===== */
        .stMarkdown p,
        .stMarkdown span {
            color: var(--text-primary) !important;
            line-height: 1.6;
        }

        .stMarkdown {
            color: var(--text-primary) !important;
        }

        /* ===== BOTONES ===== */
        .stButton > button {
            background-color: var(--primary-light) !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            padding: 0.6em 1.5em !important;
            transition: all 0.3s ease !important;
            box-shadow: var(--shadow) !important;
        }

        .stButton > button:hover {
            background-color: var(--primary-color) !important;
            box-shadow: var(--shadow-md) !important;
            transform: translateY(-2px) !important;
        }

        /* ===== INPUTS Y SELECTS ===== */
        .stTextInput input,
        .stNumberInput input,
        .stDateInput input {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 6px !important;
            padding: 0.75em !important;
        }

        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stDateInput input:focus {
            border-color: var(--primary-light) !important;
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
        }

        .stSelectbox {
            color: var(--text-primary) !important;
        }

        .stSelectbox label {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }

        /* ===== TABS ===== */
        [role="tablist"] {
            border-bottom: 2px solid var(--border-color) !important;
        }

        [role="tab"] {
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
        }

        [role="tab"][aria-selected="true"] {
            color: var(--primary-light) !important;
            font-weight: 600 !important;
            border-bottom: 3px solid var(--primary-light) !important;
        }

        /* ===== MÉTRICAS ===== */
        .stMetric {
            background-color: var(--bg-secondary) !important;
            padding: 1.5em !important;
            border-radius: 8px !important;
            box-shadow: var(--shadow) !important;
            border: 1px solid var(--border-color) !important;
        }

        .stMetric label {
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
            font-size: 0.9em !important;
        }

        .stMetric [data-testid="stMetricValue"] {
            color: var(--primary-color) !important;
            font-size: 1.8em !important;
            font-weight: 700 !important;
        }

        /* ===== DATAFRAMES ===== */
        .stDataFrame {
            background-color: var(--bg-secondary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }

        .stDataFrame tbody tr:hover {
            background-color: var(--bg-tertiary) !important;
        }

        /* ===== DIVIDER ===== */
        hr {
            border-color: var(--border-color) !important;
        }

        /* ===== PROGRESS BAR ===== */
        .stProgress > div > div {
            background-color: var(--primary-light) !important;
        }

        /* ===== ALERTS Y MENSAJES ===== */
        [data-testid="stAlert"] {
            border-radius: 6px !important;
        }

        /* Success */
        [data-testid="stAlert"][kind="success"] {
            background-color: #e6f7f0 !important;
            border-color: #20c997 !important;
            color: #0d6047 !important;
        }

        /* Error */
        [data-testid="stAlert"][kind="error"] {
            background-color: #fce8e6 !important;
            border-color: #d33b27 !important;
            color: #8a0000 !important;
        }

        /* Warning */
        [data-testid="stAlert"][kind="warning"] {
            background-color: #fef7e0 !important;
            border-color: #f57f17 !important;
            color: #664d03 !important;
        }

        /* Info */
        [data-testid="stAlert"][kind="info"] {
            background-color: #e3f2fd !important;
            border-color: #0066cc !important;
            color: #003d99 !important;
        }

        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-main);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-light);
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.session_state.plotly_template = "plotly"

# Aplicar tema empresarial
aplicar_tema_empresarial()

# Inicializar estado de gráficos
if "plotly_template" not in st.session_state:
    st.session_state.plotly_template = "plotly"

# Función helper para aplicar tema a gráficos Plotly
def aplicar_tema_plotly(fig):
    """Aplica el template de tema a un gráfico Plotly"""
    fig.update_layout(template=st.session_state.plotly_template)
    return fig

# ---------------------------------------------------------
# FUNCIONES DE GESTIÓN DE PRESUPUESTOS POR PROYECTO
# ---------------------------------------------------------
@st.cache_data
def cargar_presupuestos():
    """Carga los presupuestos desde el archivo YAML"""
    presupuestos_file = Path(__file__).parent / "presupuestos.yaml"

    if not presupuestos_file.exists():
        return {}

    with open(presupuestos_file) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    return config.get("proyectos", {}) if config else {}

def guardar_presupuestos(presupuestos):
    """Guarda los presupuestos en el archivo YAML"""
    presupuestos_file = Path(__file__).parent / "presupuestos.yaml"
    config = {"proyectos": presupuestos}

    with open(presupuestos_file, "w") as f:
        yaml.dump(config, f)

def obtener_presupuesto_proyecto(nombre_proyecto, presupuestos):
    """Obtiene el presupuesto y costo de un proyecto"""
    if nombre_proyecto in presupuestos:
        return presupuestos[nombre_proyecto]
    return {"presupuesto_horas": 0, "costo_hora": 0}

def calcular_estado_proyecto(horas_usadas, presupuesto_horas, costo_hora):
    """Calcula el estado de un proyecto basado en su presupuesto"""
    if presupuesto_horas <= 0:
        return {
            "estado": "⚠️ Sin presupuesto",
            "porcentaje": 0,
            "horas_restantes": 0,
            "costo_total": horas_usadas * costo_hora,
            "costo_presupuestado": 0
        }

    porcentaje = (horas_usadas / presupuesto_horas) * 100
    horas_restantes = max(0, presupuesto_horas - horas_usadas)
    costo_total = horas_usadas * costo_hora
    costo_presupuestado = presupuesto_horas * costo_hora

    # Determinar el estado
    if porcentaje < 75:
        estado = "🟢 En control"
    elif porcentaje < 100:
        estado = "🟡 Cerca del límite"
    elif porcentaje < 120:
        estado = "🔴 Excedido"
    else:
        estado = "🔴🔴 Muy excedido"

    return {
        "estado": estado,
        "porcentaje": porcentaje,
        "horas_restantes": horas_restantes,
        "costo_total": costo_total,
        "costo_presupuestado": costo_presupuestado
    }

# ---------------------------------------------------------
# CONFIGURACIÓN DE AUTENTICACIÓN
# ---------------------------------------------------------
config_file = Path(__file__).parent / "config.yaml"

# Si no existe config.yaml, crear uno por defecto
if not config_file.exists():
    default_config = {
        "credentials": {
            "usernames": {
                "admin": {
                    "email": "admin@example.com",
                    "name": "Administrador",
                    "password": "admin123"
                },
                "usuario": {
                    "email": "user@example.com",
                    "name": "Usuario Demo",
                    "password": "demo123"
                }
            }
        },
        "cookie": {
            "expiry_days": 30,
            "key": "tempo_dashboard_key",
            "name": "tempo_auth"
        },
        "pre-authorized": {
            "emails": []
        }
    }
    with open(config_file, "w") as f:
        yaml.dump(default_config, f)

# Cargar configuración
with open(config_file) as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

# Inicializar autenticador
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Mostrar formulario de login
authenticator.login(location="main")

# Si no está autenticado, mostrar mensaje y parar
if st.session_state.authentication_status is False:
    st.error("Usuario o contraseña incorrectos")
    st.stop()
elif st.session_state.authentication_status is None:
    st.warning("Por favor, ingresa tu usuario y contraseña")
    st.stop()

# Si está autenticado, mostrar el dashboard
st.markdown("""
    <style>
        .header-container {
            background: linear-gradient(135deg, #003d99 0%, #0066cc 100%);
            padding: 2rem;
            border-radius: 8px;
            color: white;
            margin-bottom: 2rem;
        }
        .header-container h1 {
            color: white !important;
            margin: 0;
            font-size: 2.5em;
        }
        .header-container p {
            color: rgba(255, 255, 255, 0.9) !important;
            margin: 0.5rem 0 0 0;
            font-size: 1.1em;
        }
    </style>
    <div class="header-container">
        <h1>📊 Tempo Analytics</h1>
        <p>Gestión integral de tiempos, actividades y presupuestos</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("**Integración en tiempo real con la API v4 de Tempo para Jira**", help="Dashboard de análisis y control de gestión de tiempo")

# Botón de logout en la barra lateral
with st.sidebar:
    st.write(f"**Bienvenido, {st.session_state.name}!** 👋")
    authenticator.logout(button_name="Cerrar sesión", location="sidebar")
    st.divider()

# ---------------------------------------------------------
# BARRA LATERAL: AUTENTICACIÓN Y FILTROS GENERALES
# ---------------------------------------------------------
st.sidebar.header("🔐 1. Conexión a Tempo")
api_token = st.sidebar.text_input("Tempo API Token", type="password")
region = st.sidebar.selectbox("Región de la API", ["api.tempo.io", "api.us.tempo.io"])

st.sidebar.header("🔑 2. Conexión a Jira (Para traducir IDs)")
st.sidebar.caption("Necesario para convertir los códigos en nombres reales.")
jira_email = st.sidebar.text_input("Email de Jira")
jira_token = st.sidebar.text_input("Jira API Token", type="password", help="Géralo en tu cuenta de Atlassian > Seguridad")

# Rango de fechas
today = date.today()
primer_dia_mes = today.replace(day=1)
ultimo_dia_mes = today.replace(day=calendar.monthrange(today.year, today.month)[1])

st.sidebar.header("📅 3. Rango de Fechas")
fecha_inicio = st.sidebar.date_input("Fecha de Inicio", primer_dia_mes)
fecha_fin = st.sidebar.date_input("Fecha de Fin", ultimo_dia_mes)

if st.sidebar.button("🔄 Actualizar Datos"):
    st.cache_data.clear()

# ---------------------------------------------------------
# Cargar presupuestos existentes
presupuestos = cargar_presupuestos()

# SECCIÓN DE GESTIÓN DE PRESUPUESTOS EN SIDEBAR
# ---------------------------------------------------------
st.sidebar.header("💰 Gestión de Presupuestos")
st.sidebar.caption("📌 Configura valores por defecto con 'Todos' o específicos por proyecto")

with st.sidebar.expander("✏️ Agregar/Editar Presupuesto"):
    col1, col2 = st.columns(2)

    with col1:
        nombre_proyecto = st.text_input(
            "Nombre del Proyecto",
            value="Nuevo Proyecto",
            key="proyecto_name"
        )

    with col2:
        # Obtener presupuesto anterior si existe
        config_actual = presupuestos.get(nombre_proyecto, {"presupuesto_horas": 0, "costo_hora": 0})
        presupuesto_horas = st.number_input(
            "Presupuesto (Horas)",
            min_value=0.0,
            value=float(config_actual.get("presupuesto_horas", 0)),
            step=5.0,
            key="presupuesto_h"
        )

    costo_hora = st.number_input(
        "Costo por Hora ($)",
        min_value=0.0,
        value=float(config_actual.get("costo_hora", 0)),
        step=5.0,
        key="costo_h"
    )

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("💾 Guardar", use_container_width=True):
            presupuestos[nombre_proyecto] = {
                "presupuesto_horas": presupuesto_horas,
                "costo_hora": costo_hora
            }
            guardar_presupuestos(presupuestos)
            st.cache_data.clear()
            st.success(f"✅ Presupuesto guardado")
            st.rerun()

    with col_btn2:
        if st.button("🗑️ Eliminar", use_container_width=True):
            if nombre_proyecto in presupuestos:
                del presupuestos[nombre_proyecto]
                guardar_presupuestos(presupuestos)
                st.cache_data.clear()
                st.success(f"🗑️ Presupuesto eliminado")
                st.rerun()

# ---------------------------------------------------------
# FUNCIÓN PARA CONSUMIR LA API DE TEMPO
# ---------------------------------------------------------
@st.cache_data(ttl=600, show_spinner="Descargando datos de Tempo...")
def obtener_datos_tempo(token, url_region, f_inicio, f_fin):
    if not token:
        return None
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    url = f"https://{url_region}/4/worklogs?from={f_inicio}&to={f_fin}&limit=1000"
    worklogs = []
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            worklogs.extend(data.get('results', []))
            url = data.get('metadata', {}).get('next', None)
        else:
            st.error(f"❌ Error HTTP {response.status_code} en Tempo.")
            return None
    return worklogs

# ---------------------------------------------------------
# FUNCIÓN PARA TRADUCIR IDs CONSULTANDO A JIRA (CON TIMEOUT Y PROYECTOS)
# ---------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner="Traduciendo IDs y Proyectos desde Jira...")
def procesar_worklogs(_datos_crudos, j_email, j_token):
    if not _datos_crudos:
        return pd.DataFrame()
        
    filas = []
    
    jira_headers = {"Accept": "application/json"}
    if j_email and j_token:
        auth_string = f"{j_email}:{j_token}"
        base64_auth = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        jira_headers["Authorization"] = f"Basic {base64_auth}"

    cache_usuarios = {}
    cache_tickets = {} # Ahora guardará tanto el Ticket como el Proyecto

    for log in _datos_crudos:
        # 1. Obtener datos de la Persona
        author_obj = log.get("author", {})
        account_id = author_obj.get("accountId", "Desconocido")
        user_url = author_obj.get("self")
        
        persona_nombre = account_id 
        
        if j_email and j_token and user_url:
            if account_id not in cache_usuarios:
                try:
                    res_user = requests.get(user_url, headers=jira_headers, timeout=5)
                    if res_user.status_code == 200:
                        cache_usuarios[account_id] = res_user.json().get("displayName", account_id)
                    else:
                        cache_usuarios[account_id] = account_id
                except requests.exceptions.RequestException:
                    cache_usuarios[account_id] = account_id
                    
            persona_nombre = cache_usuarios[account_id]

        # 2. Obtener datos del Ticket y PROYECTO
        issue_obj = log.get("issue", {})
        issue_id = str(issue_obj.get("id", "Sin Ticket"))
        issue_url = issue_obj.get("self")
        
        ticket_key = issue_id 
        proyecto_nombre = "Proyecto Desconocido"
        
        if j_email and j_token and issue_url:
            if issue_id not in cache_tickets:
                try:
                    res_issue = requests.get(issue_url, headers=jira_headers, timeout=5)
                    if res_issue.status_code == 200:
                        data_issue = res_issue.json()
                        t_key = data_issue.get("key", issue_id)
                        
                        # Extraer el nombre del proyecto desde Jira
                        p_name = data_issue.get("fields", {}).get("project", {}).get("name", "Proyecto Desconocido")
                        
                        # Si Jira no devuelve el nombre, intentamos deducirlo de la clave (Ej: GVUR de GVUR-102)
                        if p_name == "Proyecto Desconocido" and "-" in t_key:
                            p_name = f"Proyecto {t_key.split('-')[0]}"
                            
                        cache_tickets[issue_id] = {"key": t_key, "proyecto": p_name}
                    else:
                        cache_tickets[issue_id] = {"key": issue_id, "proyecto": "Proyecto Desconocido"}
                except requests.exceptions.RequestException:
                    cache_tickets[issue_id] = {"key": issue_id, "proyecto": "Proyecto Desconocido"}
                    
            ticket_key = cache_tickets[issue_id]["key"]
            proyecto_nombre = cache_tickets[issue_id]["proyecto"]

        # 3. Guardar la fila con las nuevas columnas
        filas.append({
            "Fecha": log.get("startDate", ""),
            "Persona": persona_nombre,
            "Proyecto": proyecto_nombre,
            "Ticket": ticket_key,
            "Actividad": log.get("description", "Sin descripción"),
            "Horas": round(log.get("timeSpentSeconds", 0) / 3600, 2) 
        })
        
    return pd.DataFrame(filas)


# ---------------------------------------------------------
# LÓGICA PRINCIPAL DEL DASHBOARD
# ---------------------------------------------------------
if not api_token:
    st.warning("⚠️ Por favor, ingresa tu **Tempo API Token** en la barra lateral para comenzar.")
else:
    # 1. Obtener y procesar datos
    datos_api = obtener_datos_tempo(api_token, region, fecha_inicio, fecha_fin)
    # df = procesar_worklogs(datos_api)
    df = procesar_worklogs(datos_api, jira_email, jira_token)

    # --- MODO DEBUG: Mostrar qué está respondiendo realmente la API ---
    if st.sidebar.checkbox("🐞 Activar Modo Debug (Ver JSON crudo)"):
        st.warning("Mostrando la respuesta cruda de la API para depuración:")
        st.json(datos_api[:3]) # Muestra solo los primeros 3 registros
    # ----------------------------------------------------------------
    
    if df.empty:
        st.info("No se encontraron registros de tiempo en las fechas seleccionadas.")
    else:
        st.sidebar.markdown("---")
        st.sidebar.header("⚙️ 5. Selección de Proyecto")

        # Filtro de Proyecto/Ticket
        proyectos_disponibles = sorted(df['Proyecto'].unique())
        proyecto_seleccionado = st.sidebar.selectbox("Seleccionar Ticket / Proyecto:", ["Todos"] + list(proyectos_disponibles))

        # Obtener valores por defecto globales (si "Todos" no está configurado o es 0, usar 50.0/100.0)
        config_global = presupuestos.get("Todos", {})
        valor_hora_default = config_global.get("costo_hora") or 50.0
        presupuesto_horas_default = config_global.get("presupuesto_horas") or 100.0

        def costo_hora_de_proyecto(nombre_proyecto):
            """Devuelve el costo/hora configurado para un proyecto, o el default si no está configurado."""
            config = presupuestos.get(nombre_proyecto, {})
            return config.get("costo_hora") or valor_hora_default

        # Aplicar filtro
        if proyecto_seleccionado == "Todos":
            df_filtrado = df.copy()
            valor_hora = valor_hora_default
            presupuesto_horas = presupuesto_horas_default
        else:
            df_filtrado = df[df['Proyecto'] == proyecto_seleccionado].copy()
            # Obtener presupuesto específico del proyecto (si no existe o es 0, usa valores por defecto globales)
            config_proyecto = presupuestos.get(proyecto_seleccionado, {})
            valor_hora = config_proyecto.get("costo_hora") or valor_hora_default
            presupuesto_horas = config_proyecto.get("presupuesto_horas") or presupuesto_horas_default

        # Cálculos de la tabla: cada fila usa el costo/hora de SU PROPIO proyecto
        # (importante para la vista "Todos", donde cada proyecto puede tener un costo distinto)
        df_filtrado['Costo ($)'] = df_filtrado['Horas'] * df_filtrado['Proyecto'].apply(costo_hora_de_proyecto)

        # 2. Tarjetas de Métricas (KPIs)
        total_horas = df_filtrado['Horas'].sum()
        # Usar la suma real de costos por fila (respeta el costo/hora propio de cada proyecto en la vista "Todos")
        costo_total = df_filtrado['Costo ($)'].sum()

        # Calcular estado del proyecto
        if presupuesto_horas > 0:
            horas_restantes = presupuesto_horas - total_horas
            porcentaje_uso = (total_horas / presupuesto_horas) * 100
        else:
            horas_restantes = 0
            porcentaje_uso = 0

        # Usar la función de estado
        estado_info = calcular_estado_proyecto(total_horas, presupuesto_horas, valor_hora)
        estado_color = estado_info["estado"]

        st.markdown(f"### 📊 Resumen: {proyecto_seleccionado}")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Horas", f"{total_horas:,.2f} hrs", f"de {presupuesto_horas:.0f}")
        kpi2.metric("Costo Real", f"${costo_total:,.2f}", f"de ${estado_info['costo_presupuestado']:,.2f}")
        kpi3.metric("Horas Restantes", f"{max(horas_restantes, 0):,.2f} hrs")
        kpi4.metric("Estado", estado_color)
        
        st.markdown("---")

        # TABS para organizar el dashboard
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 Por Proyecto", "📊 Análisis General", "👥 Por Persona", "📋 Actividades", "💰 Presupuestos", "📥 Descargar"])

        # ---------------------------------------------------------
        # TAB 1: ANÁLISIS POR PROYECTO
        # ---------------------------------------------------------
        with tab1:
            st.subheader("Análisis Detallado de Proyectos")

            # Crear análisis por proyecto
            proyectos_analisis = df_filtrado.groupby("Proyecto").agg({
                "Horas": "sum",
                "Costo ($)": "sum",
                "Persona": "nunique"
            }).reset_index()
            proyectos_analisis.columns = ["Proyecto", "Horas", "Costo", "Desarrolladores"]
            proyectos_analisis = proyectos_analisis.sort_values("Horas", ascending=False)
            proyectos_analisis["% del Total"] = (proyectos_analisis["Horas"] / proyectos_analisis["Horas"].sum() * 100).round(2)
            proyectos_analisis = proyectos_analisis.reset_index(drop=True)
            proyectos_analisis.index = proyectos_analisis.index + 1

            # KPIs de proyectos
            st.markdown("#### 📊 Resumen de Proyectos")
            col_proy1, col_proy2, col_proy3, col_proy4 = st.columns(4)

            col_proy1.metric("Total de Proyectos", len(proyectos_analisis))
            col_proy2.metric("Desarrolladores Únicos", df_filtrado["Persona"].nunique())
            col_proy3.metric("Total de Horas", f"{proyectos_analisis['Horas'].sum():.2f} hrs")
            col_proy4.metric("Inversión Total", f"${proyectos_analisis['Costo'].sum():,.2f}")

            st.markdown("---")

            # Tabla principal de proyectos
            st.markdown("#### 🏆 Detalles por Proyecto")
            st.dataframe(
                proyectos_analisis[["Proyecto", "Horas", "Costo", "Desarrolladores", "% del Total"]],
                use_container_width=True,
                column_config={
                    "Horas": st.column_config.NumberColumn("Horas", format="%.2f"),
                    "Costo": st.column_config.NumberColumn("Costo ($)", format="$%.2f"),
                    "Desarrolladores": st.column_config.NumberColumn("Desarrolladores", format="%d"),
                    "% del Total": st.column_config.NumberColumn("% del Total", format="%.2f%%")
                }
            )

            st.markdown("---")

            # Desglose por proyecto seleccionado
            st.markdown("#### 👥 Desglose de Desarrolladores por Proyecto")

            proyecto_selec_desglose = st.selectbox(
                "Selecciona un proyecto para ver el desglose de desarrolladores:",
                proyectos_analisis["Proyecto"].tolist(),
                key="proyecto_desglose"
            )

            if proyecto_selec_desglose:
                # Filtrar datos del proyecto seleccionado
                df_proyecto = df_filtrado[df_filtrado["Proyecto"] == proyecto_selec_desglose]

                # Crear tabla de desarrolladores del proyecto
                dev_proyecto = df_proyecto.groupby("Persona").agg({
                    "Horas": "sum",
                    "Costo ($)": "sum"
                }).reset_index()
                dev_proyecto.columns = ["Desarrollador", "Horas", "Costo"]
                dev_proyecto = dev_proyecto.sort_values("Horas", ascending=False)
                dev_proyecto["% del Proyecto"] = (dev_proyecto["Horas"] / dev_proyecto["Horas"].sum() * 100).round(2)
                dev_proyecto = dev_proyecto.reset_index(drop=True)
                dev_proyecto.index = dev_proyecto.index + 1

                # Mostrar métricas del proyecto
                col_proj_1, col_proj_2, col_proj_3 = st.columns(3)
                col_proj_1.metric("Desarrolladores en Proyecto", len(dev_proyecto))
                col_proj_2.metric("Total de Horas", f"{dev_proyecto['Horas'].sum():.2f}")
                col_proj_3.metric("Costo Total del Proyecto", f"${dev_proyecto['Costo'].sum():,.2f}")

                # Tabla de desarrolladores
                st.dataframe(
                    dev_proyecto[["Desarrollador", "Horas", "Costo", "% del Proyecto"]],
                    use_container_width=True,
                    column_config={
                        "Horas": st.column_config.NumberColumn("Horas", format="%.2f"),
                        "Costo": st.column_config.NumberColumn("Costo ($)", format="$%.2f"),
                        "% del Proyecto": st.column_config.NumberColumn("% del Proyecto", format="%.2f%%")
                    }
                )

                # Gráfico de distribución de desarrolladores en el proyecto
                col_dev_1, col_dev_2 = st.columns(2)

                with col_dev_1:
                    fig_dev_pie = px.pie(
                        dev_proyecto,
                        values="Horas",
                        names="Desarrollador",
                        title=f"Distribución de Horas en {proyecto_selec_desglose}"
                    )
                    fig_dev_pie.update_layout(height=400)
                    fig_dev_pie = aplicar_tema_plotly(fig_dev_pie)
                    st.plotly_chart(fig_dev_pie, use_container_width=True)

                with col_dev_2:
                    fig_dev_bar = px.bar(
                        dev_proyecto.sort_values("Horas", ascending=True),
                        x="Horas",
                        y="Desarrollador",
                        orientation='h',
                        title=f"Horas por Desarrollador en {proyecto_selec_desglose}",
                        text="Horas"
                    )
                    fig_dev_bar.update_traces(texttemplate='%{x:.2f}', textposition='outside')
                    fig_dev_bar.update_layout(height=max(300, len(dev_proyecto) * 40))
                    fig_dev_bar = aplicar_tema_plotly(fig_dev_bar)
                    st.plotly_chart(fig_dev_bar, use_container_width=True)

            st.markdown("---")

            # Gráficos de proyectos en dos columnas
            col_graf_proy1, col_graf_proy2 = st.columns(2)

            # Gráfico 1: Horas por Proyecto
            with col_graf_proy1:
                st.markdown("#### Horas por Proyecto")
                fig_horas_proy = px.bar(
                    proyectos_analisis.sort_values("Horas", ascending=True),
                    x="Horas",
                    y="Proyecto",
                    orientation='h',
                    title="Horas Registradas por Proyecto",
                    labels={"Horas": "Horas"}
                )
                fig_horas_proy.update_traces(texttemplate='%{x:.2f}', textposition='outside')
                fig_horas_proy.update_layout(height=max(300, len(proyectos_analisis) * 30))
                fig_horas_proy = aplicar_tema_plotly(fig_horas_proy)
                st.plotly_chart(fig_horas_proy, use_container_width=True)

            # Gráfico 2: Costo por Proyecto
            with col_graf_proy2:
                st.markdown("#### Costo por Proyecto")
                fig_costo_proy = px.bar(
                    proyectos_analisis.sort_values("Costo", ascending=True),
                    x="Costo",
                    y="Proyecto",
                    orientation='h',
                    title="Costo Total por Proyecto",
                    labels={"Costo": "Costo ($)"}
                )
                fig_costo_proy.update_traces(texttemplate='$%{x:,.0f}', textposition='outside')
                fig_costo_proy.update_layout(height=max(300, len(proyectos_analisis) * 30))
                fig_costo_proy = aplicar_tema_plotly(fig_costo_proy)
                st.plotly_chart(fig_costo_proy, use_container_width=True)

            st.markdown("---")

            # Gráficos adicionales
            col_graf_proy3, col_graf_proy4 = st.columns(2)

            # Gráfico 3: Distribución de Horas
            with col_graf_proy3:
                st.markdown("#### Distribución de Horas por Proyecto")
                fig_dist_proy = px.pie(
                    proyectos_analisis,
                    values="Horas",
                    names="Proyecto",
                    title="Proporción de Horas por Proyecto"
                )
                fig_dist_proy.update_layout(height=400)
                fig_dist_proy = aplicar_tema_plotly(fig_dist_proy)
                st.plotly_chart(fig_dist_proy, use_container_width=True)

            # Gráfico 4: Desarrolladores por Proyecto
            with col_graf_proy4:
                st.markdown("#### Desarrolladores por Proyecto")
                fig_dev_proy = px.bar(
                    proyectos_analisis.sort_values("Desarrolladores", ascending=True),
                    x="Desarrolladores",
                    y="Proyecto",
                    orientation='h',
                    title="Número de Desarrolladores por Proyecto",
                    labels={"Desarrolladores": "Cantidad"}
                )
                fig_dev_proy.update_traces(texttemplate='%{x}', textposition='outside')
                fig_dev_proy.update_layout(height=max(300, len(proyectos_analisis) * 30))
                fig_dev_proy = aplicar_tema_plotly(fig_dev_proy)
                st.plotly_chart(fig_dev_proy, use_container_width=True)

        # ---------------------------------------------------------
        # TAB 2: ANÁLISIS GENERAL
        # ---------------------------------------------------------
        with tab2:
            st.subheader("Análisis de Consumo del Presupuesto")

            # Barra de progreso mejorada
            col_prog1, col_prog2 = st.columns([3, 1])
            with col_prog1:
                st.write("**Consumo del Presupuesto de Horas:**")
                progress_value = min(porcentaje_uso / 100, 1.0)
                st.progress(progress_value)
            with col_prog2:
                st.metric("Consumo", f"{porcentaje_uso:.1f}%")

            st.caption(f"**{total_horas:.2f}** de **{presupuesto_horas}** horas utilizadas")

            st.markdown("---")

            # Gráficos en dos columnas
            col_grafico1, col_grafico2 = st.columns(2)

            # Gráfico 1: Horas vs Presupuesto (Gauche/Gauge)
            with col_grafico1:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=total_horas,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Horas Utilizadas"},
                    delta={'reference': presupuesto_horas},
                    gauge={
                        'axis': {'range': [0, presupuesto_horas * 1.1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, presupuesto_horas * 0.8], 'color': "lightgray"},
                            {'range': [presupuesto_horas * 0.8, presupuesto_horas], 'color': "orange"},
                            {'range': [presupuesto_horas, presupuesto_horas * 1.1], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': presupuesto_horas
                        }
                    }
                ))
                fig_gauge.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
                fig_gauge = aplicar_tema_plotly(fig_gauge)
                st.plotly_chart(fig_gauge, use_container_width=True)

            # Gráfico 2: Costo vs Presupuesto
            with col_grafico2:
                costo_presupuestado = presupuesto_horas * valor_hora
                fig_costo = go.Figure(go.Indicator(
                    mode="number+delta",
                    value=costo_total,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Costo Total"},
                    delta={'reference': costo_presupuestado},
                    number={'prefix': "$", 'suffix': ""}
                ))
                fig_costo.update_layout(height=150, margin=dict(l=10, r=10, t=30, b=10))
                fig_costo = aplicar_tema_plotly(fig_costo)
                st.plotly_chart(fig_costo, use_container_width=True)

                col_c1, col_c2, col_c3 = st.columns(3)
                col_c1.metric("Costo Real", f"${costo_total:,.2f}")
                col_c2.metric("Presupuesto", f"${costo_presupuestado:,.2f}")
                col_c3.metric("Diferencia", f"${costo_presupuestado - costo_total:,.2f}")

            st.markdown("---")

            # Gráfico de Horas por Persona
            st.subheader("Consumo de Horas por Persona")
            horas_por_persona = df_filtrado.groupby("Persona")["Horas"].sum().sort_values(ascending=True)

            fig_persona = px.bar(
                x=horas_por_persona.values,
                y=horas_por_persona.index,
                orientation='h',
                labels={'x': 'Horas', 'y': 'Persona'},
                title="Horas Registradas por Persona"
            )
            fig_persona.update_traces(texttemplate='%{x:.2f}', textposition='outside')
            fig_persona.update_layout(height=max(300, len(horas_por_persona) * 30))
            fig_persona = aplicar_tema_plotly(fig_persona)
            st.plotly_chart(fig_persona, use_container_width=True)

        # ---------------------------------------------------------
        # TAB 3: ANÁLISIS POR PERSONA
        # ---------------------------------------------------------
        with tab3:
            st.subheader("Top Consumidores de Horas")

            # Filtro por persona
            personas_disponibles = sorted(df_filtrado["Persona"].unique())
            personas_seleccionadas = st.multiselect(
                "🔎 Filtrar por Persona(s):",
                personas_disponibles,
                default=personas_disponibles,
                key="filtro_personas"
            )

            if not personas_seleccionadas:
                st.warning("⚠️ Selecciona al menos una persona para ver el análisis.")
            else:
                df_personas_filtrado = df_filtrado[df_filtrado["Persona"].isin(personas_seleccionadas)]

                # Crear ranking de personas
                ranking = df_personas_filtrado.groupby("Persona").agg({
                    "Horas": "sum",
                    "Costo ($)": "sum"
                }).reset_index()
                ranking.columns = ["Persona", "Horas", "Costo"]
                ranking = ranking.sort_values("Horas", ascending=False).reset_index(drop=True)
                ranking.index = ranking.index + 1
                ranking["% del Total"] = (ranking["Horas"] / ranking["Horas"].sum() * 100).round(2)

                # Top 5
                st.markdown("#### 🏆 Top 5 Consumidores")
                col_top = st.columns(5)
                top_5 = ranking.head(5)

                for idx, (col, (_, row)) in enumerate(zip(col_top, top_5.iterrows())):
                    with col:
                        st.metric(
                            f"#{idx+1} - {row['Persona']}",
                            f"{row['Horas']:.2f} hrs",
                            f"{row['% del Total']:.1f}% del total"
                        )

                st.markdown("---")

                # Tabla completa de ranking
                st.markdown("#### 📊 Ranking Completo")
                st.dataframe(
                    ranking[["Persona", "Horas", "Costo", "% del Total"]],
                    use_container_width=True
                )

                st.markdown("---")

                # Desglose por persona seleccionada
                st.markdown("#### 📋 Desglose de Proyectos por Persona")

                persona_selec_desglose = st.selectbox(
                    "Selecciona una persona para ver sus proyectos y horas:",
                    ranking["Persona"].tolist(),
                    key="persona_desglose"
                )

                if persona_selec_desglose:
                    # Filtrar datos de la persona seleccionada
                    df_persona = df_personas_filtrado[df_personas_filtrado["Persona"] == persona_selec_desglose]

                    # Crear tabla de proyectos de la persona
                    proyectos_persona = df_persona.groupby("Proyecto").agg({
                        "Horas": "sum",
                        "Costo ($)": "sum"
                    }).reset_index()
                    proyectos_persona.columns = ["Proyecto", "Horas", "Costo"]
                    proyectos_persona = proyectos_persona.sort_values("Horas", ascending=False)
                    proyectos_persona["% de Sus Horas"] = (proyectos_persona["Horas"] / proyectos_persona["Horas"].sum() * 100).round(2)
                    proyectos_persona = proyectos_persona.reset_index(drop=True)
                    proyectos_persona.index = proyectos_persona.index + 1

                    # Mostrar métricas de la persona
                    col_pers_1, col_pers_2, col_pers_3 = st.columns(3)
                    col_pers_1.metric("Proyectos en los que trabajó", len(proyectos_persona))
                    col_pers_2.metric("Total de Horas", f"{proyectos_persona['Horas'].sum():.2f}")
                    col_pers_3.metric("Costo Total Generado", f"${proyectos_persona['Costo'].sum():,.2f}")

                    # Tabla de proyectos
                    st.dataframe(
                        proyectos_persona[["Proyecto", "Horas", "Costo", "% de Sus Horas"]],
                        use_container_width=True,
                        column_config={
                            "Horas": st.column_config.NumberColumn("Horas", format="%.2f"),
                            "Costo": st.column_config.NumberColumn("Costo ($)", format="$%.2f"),
                            "% de Sus Horas": st.column_config.NumberColumn("% de Sus Horas", format="%.2f%%")
                        }
                    )

                    # Gráficos de proyectos de la persona
                    col_pers_graf_1, col_pers_graf_2 = st.columns(2)

                    with col_pers_graf_1:
                        fig_pers_pie = px.pie(
                            proyectos_persona,
                            values="Horas",
                            names="Proyecto",
                            title=f"Distribución de Horas de {persona_selec_desglose}"
                        )
                        fig_pers_pie.update_layout(height=400)
                        fig_pers_pie = aplicar_tema_plotly(fig_pers_pie)
                        st.plotly_chart(fig_pers_pie, use_container_width=True)

                    with col_pers_graf_2:
                        fig_pers_bar = px.bar(
                            proyectos_persona.sort_values("Horas", ascending=True),
                            x="Horas",
                            y="Proyecto",
                            orientation='h',
                            title=f"Proyectos de {persona_selec_desglose}",
                            text="Horas"
                        )
                        fig_pers_bar.update_traces(texttemplate='%{x:.2f}', textposition='outside')
                        fig_pers_bar.update_layout(height=max(300, len(proyectos_persona) * 40))
                        fig_pers_bar = aplicar_tema_plotly(fig_pers_bar)
                        st.plotly_chart(fig_pers_bar, use_container_width=True)

                    st.markdown("---")

                    # Detalle de actividades de la persona
                    st.markdown(f"#### 📝 Actividades de {persona_selec_desglose}")
                    actividades_persona = df_persona.groupby(["Proyecto", "Actividad"]).agg({
                        "Horas": "sum",
                        "Costo ($)": "sum"
                    }).reset_index()
                    actividades_persona = actividades_persona.sort_values("Horas", ascending=False)
                    st.dataframe(
                        actividades_persona,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Horas": st.column_config.NumberColumn("Horas", format="%.2f"),
                            "Costo ($)": st.column_config.NumberColumn("Costo ($)", format="$%.2f")
                        }
                    )

                st.markdown("---")

                # Gráfico de distribución
                st.subheader("Distribución de Horas por Persona")
                fig_dist = px.pie(
                    ranking,
                    values="Horas",
                    names="Persona",
                    title="Proporción de Horas por Persona"
                )
                fig_dist.update_layout(height=400)
                fig_dist = aplicar_tema_plotly(fig_dist)
                st.plotly_chart(fig_dist, use_container_width=True)

        # ---------------------------------------------------------
        # TAB 4: ANÁLISIS POR ACTIVIDAD
        # ---------------------------------------------------------
        with tab4:
            st.subheader("Análisis por Tipo de Actividad")

            # Horas por actividad
            actividades = df_filtrado.groupby("Actividad").agg({
                "Horas": "sum",
                "Costo ($)": "sum"
            }).reset_index()
            actividades = actividades.sort_values("Horas", ascending=False)
            actividades.columns = ["Actividad", "Horas", "Costo"]
            actividades["% del Total"] = (actividades["Horas"] / actividades["Horas"].sum() * 100).round(2)

            # Top actividades
            st.markdown("#### Top Actividades")
            col_act1, col_act2, col_act3 = st.columns(3)

            if len(actividades) > 0:
                col_act1.metric("Más Común", actividades.iloc[0]["Actividad"], f"{actividades.iloc[0]['Horas']:.2f} hrs")
            if len(actividades) > 1:
                col_act2.metric("2ª Actividad", actividades.iloc[1]["Actividad"], f"{actividades.iloc[1]['Horas']:.2f} hrs")
            if len(actividades) > 2:
                col_act3.metric("3ª Actividad", actividades.iloc[2]["Actividad"], f"{actividades.iloc[2]['Horas']:.2f} hrs")

            st.markdown("---")

            # Tabla de actividades
            st.dataframe(actividades, use_container_width=True)

            st.markdown("---")

            # Gráfico de barras
            st.subheader("Horas por Actividad")
            fig_act = px.bar(
                actividades.head(10),
                x="Actividad",
                y="Horas",
                text="Horas",
                title="Top 10 Actividades por Horas",
                labels={"Horas": "Horas Registradas"}
            )
            fig_act.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_act.update_layout(height=400, xaxis_tickangle=-45)
            fig_act = aplicar_tema_plotly(fig_act)
            st.plotly_chart(fig_act, use_container_width=True)

        # ---------------------------------------------------------
        # TAB 5: ANÁLISIS DE PRESUPUESTOS
        # ---------------------------------------------------------
        with tab5:
            # Mostrar presupuestos configurados
            st.markdown("### 📊 Presupuestos Configurados")

            if presupuestos:
                # Agregar CSS personalizado para tarjetas
                st.markdown("""
                <style>
                    .presupuesto-card {
                        background: linear-gradient(135deg, #f0f4f8 0%, #ffffff 100%);
                        border: 2px solid #003d99;
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin-bottom: 1rem;
                        box-shadow: 0 4px 12px rgba(0, 61, 153, 0.08);
                        transition: transform 0.2s, box-shadow 0.2s;
                    }
                    .presupuesto-card:hover {
                        transform: translateY(-4px);
                        box-shadow: 0 8px 16px rgba(0, 61, 153, 0.15);
                    }
                    .presupuesto-title {
                        color: #003d99;
                        font-size: 1.2em;
                        font-weight: 600;
                        margin-bottom: 0.8rem;
                    }
                    .presupuesto-value {
                        font-size: 1.5em;
                        font-weight: 700;
                        color: #002e73;
                    }
                    .presupuesto-label {
                        font-size: 0.85em;
                        color: #505050;
                        font-weight: 500;
                        margin-top: 0.3rem;
                    }
                </style>
                """, unsafe_allow_html=True)

                # Mostrar presupuestos en grid
                num_cols = 3
                cols = st.columns(num_cols)

                for idx, (proyecto, config) in enumerate(presupuestos.items()):
                    with cols[idx % num_cols]:
                        st.markdown(f"""
                        <div class="presupuesto-card">
                            <div class="presupuesto-title">{proyecto}</div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                                <div>
                                    <div class="presupuesto-value">{config['presupuesto_horas']:.0f}</div>
                                    <div class="presupuesto-label">Horas</div>
                                </div>
                                <div>
                                    <div class="presupuesto-value">${config['costo_hora']:.2f}</div>
                                    <div class="presupuesto-label">Costo/Hora</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ No hay presupuestos configurados. Agrega uno en el sidebar.")

            st.markdown("---")
            st.subheader("💰 Análisis de Presupuestos por Proyecto")

            # Obtener lista de proyectos únicos
            proyectos_unicos = df['Proyecto'].unique()

            # Crear tabla de análisis de presupuestos
            datos_presupuestos = []

            for proyecto in sorted(proyectos_unicos):
                df_proyecto = df[df['Proyecto'] == proyecto]
                horas_proyecto = df_proyecto['Horas'].sum()

                config = obtener_presupuesto_proyecto(proyecto, presupuestos)
                presupuesto = config.get("presupuesto_horas", 0)
                costo_hora_p = config.get("costo_hora", 0)

                estado = calcular_estado_proyecto(horas_proyecto, presupuesto, costo_hora_p)

                datos_presupuestos.append({
                    "Proyecto": proyecto,
                    "Horas Usadas": horas_proyecto,
                    "Presupuesto": presupuesto,
                    "% Utilización": estado["porcentaje"],
                    "Horas Restantes": estado["horas_restantes"],
                    "Costo/Hora": costo_hora_p,
                    "Costo Real": estado["costo_total"],
                    "Costo Presupuestado": estado["costo_presupuestado"],
                    "Estado": estado["estado"]
                })

            df_presupuestos = pd.DataFrame(datos_presupuestos)

            if len(df_presupuestos) > 0:
                # Mostrar tabla resumen
                st.markdown("### 📋 Resumen de Presupuestos")
                st.dataframe(
                    df_presupuestos,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Horas Usadas": st.column_config.NumberColumn("Horas Usadas", format="%.2f"),
                        "Presupuesto": st.column_config.NumberColumn("Presupuesto", format="%.2f"),
                        "% Utilización": st.column_config.NumberColumn("% Utilización", format="%.1f%%"),
                        "Horas Restantes": st.column_config.NumberColumn("Horas Restantes", format="%.2f"),
                        "Costo/Hora": st.column_config.NumberColumn("Costo/Hora", format="$%.2f"),
                        "Costo Real": st.column_config.NumberColumn("Costo Real", format="$%.2f"),
                        "Costo Presupuestado": st.column_config.NumberColumn("Costo Presupuestado", format="$%.2f")
                    }
                )

                st.markdown("---")

                # Gráficos de análisis de presupuestos
                col_grafico_p1, col_grafico_p2 = st.columns(2)

                with col_grafico_p1:
                    st.markdown("#### Utilización vs Presupuesto por Proyecto")
                    fig_presup = px.bar(
                        df_presupuestos,
                        x="Proyecto",
                        y=["Horas Usadas", "Presupuesto"],
                        barmode="group",
                        title="Comparativa: Horas Usadas vs Presupuesto",
                        labels={"value": "Horas", "variable": "Tipo"}
                    )
                    fig_presup = aplicar_tema_plotly(fig_presup)
                    st.plotly_chart(fig_presup, use_container_width=True)

                with col_grafico_p2:
                    st.markdown("#### % Utilización del Presupuesto")
                    # Crear gráfico de progress/utilización
                    fig_util = px.bar(
                        df_presupuestos.sort_values("% Utilización", ascending=True),
                        x="% Utilización",
                        y="Proyecto",
                        orientation="h",
                        title="Porcentaje de Utilización por Proyecto",
                        labels={"% Utilización": "% Utilización"}
                    )
                    fig_util.add_vline(x=100, line_dash="dash", line_color="red", annotation_text="Límite")
                    fig_util.add_vline(x=75, line_dash="dash", line_color="orange", annotation_text="Alerta")
                    fig_util = aplicar_tema_plotly(fig_util)
                    st.plotly_chart(fig_util, use_container_width=True)

                st.markdown("---")

                # Gráfico de costo
                col_grafico_p3, col_grafico_p4 = st.columns(2)

                with col_grafico_p3:
                    st.markdown("#### Costo Real vs Presupuestado")
                    fig_costo_p = px.bar(
                        df_presupuestos,
                        x="Proyecto",
                        y=["Costo Real", "Costo Presupuestado"],
                        barmode="group",
                        title="Comparativa de Costos",
                        labels={"value": "Costo ($)", "variable": "Tipo"}
                    )
                    fig_costo_p = aplicar_tema_plotly(fig_costo_p)
                    st.plotly_chart(fig_costo_p, use_container_width=True)

                with col_grafico_p4:
                    st.markdown("#### Estado de Proyectos")
                    # Contar proyectos por estado
                    conteo_estados = df_presupuestos['Estado'].value_counts()
                    fig_estados = px.pie(
                        values=conteo_estados.values,
                        names=conteo_estados.index,
                        title="Distribución de Estados"
                    )
                    fig_estados = aplicar_tema_plotly(fig_estados)
                    st.plotly_chart(fig_estados, use_container_width=True)

        # ---------------------------------------------------------
        # TAB 6: DESCARGAS
        # ---------------------------------------------------------
        with tab6:
            st.subheader("📥 Descargar Reportes")

            # Datos detallados
            st.markdown("#### Registro Detallado de Actividades")
            df_mostrar = df_filtrado.sort_values(by="Fecha", ascending=False)
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

            csv_detalle = df_mostrar.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Detalle en CSV",
                data=csv_detalle,
                file_name=f"reporte_tempo_detalle_{proyecto_seleccionado}.csv",
                mime="text/csv",
            )

            st.markdown("---")

            # Resumen por proyecto y usuario
            st.markdown("#### Resumen por Proyecto y Usuario")
            df_resumen = df_filtrado.groupby(["Proyecto", "Persona"])[["Horas", "Costo ($)"]].sum().reset_index()
            st.dataframe(df_resumen, use_container_width=True, hide_index=True)

            csv_resumen = df_resumen.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Resumen en CSV",
                data=csv_resumen,
                file_name=f"reporte_tempo_resumen_{proyecto_seleccionado}.csv",
                mime="text/csv",
            )
            st.markdown("---")
            # Ranking de personas
            st.markdown("#### Ranking de Consumo por Persona")
            ranking_export = df_filtrado.groupby("Persona").agg({
                "Horas": "sum",
                "Costo ($)": "sum"
            }).reset_index()
            ranking_export.columns = ["Persona", "Horas", "Costo"]
            ranking_export = ranking_export.sort_values("Horas", ascending=False).reset_index(drop=True)
            ranking_export.index = ranking_export.index + 1
            ranking_export["% del Total"] = (ranking_export["Horas"] / ranking_export["Horas"].sum() * 100).round(2)
            st.dataframe(ranking_export, use_container_width=True)

            csv_ranking = ranking_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Ranking en CSV",
                data=csv_ranking,
                file_name=f"reporte_tempo_ranking_{proyecto_seleccionado}.csv",
                mime="text/csv",
            )
            st.markdown("---")
            # Análisis por proyecto
            st.markdown("#### Análisis por Proyecto")
            proyectos_descarga = df_filtrado.groupby("Proyecto").agg({
                "Horas": "sum",
                "Costo ($)": "sum",
                "Persona": "nunique"
            }).reset_index()
            proyectos_descarga.columns = ["Proyecto", "Horas", "Costo", "Desarrolladores"]
            proyectos_descarga = proyectos_descarga.sort_values("Horas", ascending=False)
            st.dataframe(proyectos_descarga, use_container_width=True, hide_index=True)

            csv_proyectos = proyectos_descarga.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Análisis de Proyectos en CSV",
                data=csv_proyectos,
                file_name=f"reporte_tempo_proyectos.csv",
                mime="text/csv",
            )