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

# Inicializar estado de tema
if "theme" not in st.session_state:
    st.session_state.theme = "Automático"

# Función para aplicar tema
def aplicar_tema(tema):
    if tema == "Claro":
        # Configurar template de Plotly para tema claro
        import plotly.graph_objects as go
        go.Figure().update_layout(template="plotly")

        css = """
        <style>
            [data-testid="stApp"] {
                background-color: #ffffff;
                color: #1f1f1f;
            }
            body {
                background-color: #ffffff !important;
                color: #1f1f1f !important;
            }
            .stMarkdown, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
            .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, .stMarkdown p {
                color: #1f1f1f !important;
            }
            .stMetric label {
                color: #1f1f1f !important;
            }
            .stDataFrame {
                background-color: #ffffff !important;
            }
            .stSelectbox label, .stTextInput label {
                color: #1f1f1f !important;
            }
            .stSelectbox [data-baseweb="select"] {
                background-color: #f0f2f6 !important;
            }
            /* Cambiar el fondo de la sidebar */
            [data-testid="stSidebar"] {
                background-color: #f8f9fa !important;
            }
            [data-testid="stSidebar"] .stMarkdown {
                color: #1f1f1f !important;
            }
        </style>
        """
        st.session_state.plotly_template = "plotly"
    elif tema == "Oscuro":
        import plotly.graph_objects as go
        go.Figure().update_layout(template="plotly_dark")

        css = ""
        st.session_state.plotly_template = "plotly_dark"
    else:  # Automático
        st.session_state.plotly_template = "plotly"
        css = ""

    if css:
        st.markdown(css, unsafe_allow_html=True)

# Aplicar tema inicial
if "plotly_template" not in st.session_state:
    st.session_state.plotly_template = "plotly"

# Función helper para aplicar tema a gráficos Plotly
def aplicar_tema_plotly(fig):
    """Aplica el template de tema a un gráfico Plotly"""
    fig.update_layout(template=st.session_state.plotly_template)
    return fig

aplicar_tema(st.session_state.theme)

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
st.title("⏱️ Cuadro de Control: Tiempos, Actividades y Presupuestos")
st.markdown("Integración en tiempo real con la API v4 de **Tempo para Jira**.")

# Botón de logout en la barra lateral
with st.sidebar:
    st.write(f"**Bienvenido, {st.session_state.name}!** 👋")
    authenticator.logout(button_name="Cerrar sesión", location="sidebar")

    # Selector de tema
    theme = st.selectbox(
        "🎨 Tema",
        ["Automático", "Claro", "Oscuro"],
        index=["Automático", "Claro", "Oscuro"].index(st.session_state.theme)
    )
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        aplicar_tema(theme)
        st.rerun()

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
        st.sidebar.header("⚙️ 3. Parámetros del Proyecto")
        
        # Filtro de Proyecto/Ticket
        proyectos_disponibles = sorted(df['Proyecto'].unique())
        proyecto_seleccionado = st.sidebar.selectbox("Seleccionar Ticket / Proyecto:", ["Todos"] + list(proyectos_disponibles))
        
        # Parámetros Financieros
        valor_hora = st.sidebar.number_input("Valor de la Hora ($):", min_value=0.0, value=50.0, step=5.0)
        presupuesto_horas = st.sidebar.number_input("Presupuesto (Horas):", min_value=1.0, value=100.0, step=10.0)
        
        # Aplicar filtro
        if proyecto_seleccionado == "Todos":
            df_filtrado = df.copy()
        else:
            df_filtrado = df[df['Proyecto'] == proyecto_seleccionado].copy()
            
        # Cálculos de la tabla
        df_filtrado['Costo ($)'] = df_filtrado['Horas'] * valor_hora
        
        # 2. Tarjetas de Métricas (KPIs)
        total_horas = df_filtrado['Horas'].sum()
        costo_total = total_horas * valor_hora
        horas_restantes = presupuesto_horas - total_horas
        porcentaje_uso = (total_horas / presupuesto_horas) * 100
        
        # Lógica de Semáforo
        if porcentaje_uso < 80:
            estado_color = "🟢 Saludable"
        elif porcentaje_uso < 100:
            estado_color = "🟠 Alerta (Cerca del límite)"
        else:
            estado_color = "🔴 Peligro (Excedido)"
            
        st.markdown(f"### Resumen de Trabajo: {proyecto_seleccionado}")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Horas Registradas", f"{total_horas:,.2f} hrs")
        kpi2.metric("Costo Total Generado", f"${costo_total:,.2f}")
        kpi3.metric("Horas Restantes", f"{horas_restantes:,.2f} hrs")
        kpi4.metric("Estado del Presupuesto", estado_color)
        
        st.markdown("---")

        # TABS para organizar el dashboard
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Por Proyecto", "📊 Análisis General", "👥 Por Persona", "📋 Actividades", "📥 Descargar"])

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

            # Crear ranking de personas
            ranking = df_filtrado.groupby("Persona").agg({
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
                df_persona = df_filtrado[df_filtrado["Persona"] == persona_selec_desglose]

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
        # TAB 5: DESCARGAS
        # ---------------------------------------------------------
        with tab5:
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
            ranking_export = ranking[["Persona", "Horas", "Costo", "% del Total"]]
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