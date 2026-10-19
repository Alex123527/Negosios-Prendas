from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(
    page_title="PROYECTO X | Financial Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de estilos Futurista Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Fondo principal de la app */
    .stApp {
        background-color: #071426;
        color: #E6EDF5;
    }

    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #0b1a2f !important;
        border-right: 1px solid rgba(67, 136, 255, 0.15);
    }

    /* Tarjetas y Contenedores */
    .premium-card {
        background-color: #10213A;
        border: 1px solid #1E365D;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        margin-bottom: 20px;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* Inputs de texto y formularios */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #0d1b30 !important;
        color: #E6EDF5 !important;
        border: 1px solid #1E365D !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #4388FF !important;
        box-shadow: 0 0 10px rgba(67, 136, 255, 0.3) !important;
    }

    /* Botones primarios */
    .stButton>button {
        background: linear-gradient(135deg, #4388FF 0%, #2f6de0 100%) !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.4rem !important;
        letter-spacing: 0.3px;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 15px rgba(67, 136, 255, 0.25) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #5c9bff 0%, #4388FF 100%) !important;
        box-shadow: 0 6px 20px rgba(67, 136, 255, 0.45) !important;
        transform: translateY(-1px);
    }

    /* Métricas superiores */
    [data-testid="stMetricValue"] {
        color: #21D4C4 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #9FB2C8 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Divisores */
    hr {
        border-color: rgba(67, 136, 255, 0.15) !important;
    }
    </style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.8, 1])
    with c2:
        st.markdown("""
            <div class="premium-card" style="text-align: center;">
                <div style="font-size: 2.8rem; margin-bottom: 10px;">⚡</div>
                <h2 style="margin: 0; font-size: 1.8rem; color: #FFFFFF;">PROYECTO X</h2>
                <p style="color: #9FB2C8; font-size: 0.9rem; margin-top: 5px;">ENTERPRISE FINANCIAL DASHBOARD</p>
                <hr style="margin: 20px 0;">
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            correo_ingresado = st.text_input("Credencial / Correo", placeholder="usuario@empresa.com")
            password_ingresada = st.text_input("Contraseña de Acceso", type="password", placeholder="••••••••")
            login_btn = st.form_submit_button("ACCEDER AL SISTEMA", use_container_width=True)

            if login_btn:
                correo_valido = st.secrets.get("auth", {}).get("correo", "ozunaramon22@gmail.com")
                password_valida = st.secrets.get("auth", {}).get("password", "123456")

                if correo_ingresado.strip().lower() == correo_valido.lower() and password_ingresada == password_valida:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Credenciales no válidas. Acceso restringido.")
    st.stop()

# Menú lateral cuando está autenticado
st.sidebar.markdown("""
    <div style="padding: 10px 0;">
        <h3 style="color: #FFFFFF; margin:0; font-size: 1.3rem;">⚡ PROYECTO X</h3>
        <p style="color: #21D4C4; font-size: 0.8rem; margin:0; letter-spacing: 1px;">SISTEMA ACTIVO</p>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
    st.session_state["autenticado"] = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Selecciona un módulo en el menú superior para comenzar.")

st.markdown("""
    <div class="premium-card">
        <h1 style="color: #FFFFFF; margin-bottom: 8px;">Centro de Mando Financiero</h1>
        <p style="color: #9FB2C8; font-size: 1.05rem; margin: 0;">
            Gestión descentralizada de tesorería, catálogo, deudas y reportes predictivos.
        </p>
    </div>
""", unsafe_allow_html=True)

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.markdown("""
        <div class="premium-card">
            <h4 style="color: #4388FF; margin: 0;">💎 Seguridad Reforzada</h4>
            <p style="color: #9FB2C8; font-size: 0.85rem; margin-top: 8px;">Tokens de sesión protegidos en cada endpoint.</p>
        </div>
    """, unsafe_allow_html=True)
with col_info2:
    st.markdown("""
        <div class="premium-card">
            <h4 style="color: #21D4C4; margin: 0;">⚡ Modo Multipágina</h4>
            <p style="color: #9FB2C8; font-size: 0.85rem; margin-top: 8px;">Módulos autónomos de alto rendimiento.</p>
        </div>
    """, unsafe_allow_html=True)
with col_info3:
    st.markdown("""
        <div class="premium-card">
            <h4 style="color: #9670FF; margin: 0;">📊 Motor SQLite</h4>
            <p style="color: #9FB2C8; font-size: 0.85rem; margin-top: 8px;">Base de datos unificada sin latencia externa.</p>
        </div>
    """, unsafe_allow_html=True)
# =====================================================================
# HERRAMIENTA DE DIAGNÓSTICO RÁPIDO DEL SISTEMA
# =====================================================================
with st.sidebar.expander("🛠️ DIAGNÓSTICO DEL SISTEMA", expanded=False):
    st.caption("Verificación de conexiones y estado de base de datos.")
    
    if st.button("🔍 EJECUTAR TEST DE SALUD", use_container_width=True):
        st.write("---")
        # 1. Test de Secretos y Conexión
        if "supabase" in st.secrets and "url" in st.secrets["supabase"] and "key" in st.secrets["supabase"]:
            st.success("✅ Secretos configurados correctamente.")
            try:
                from supabase import create_client
                supabase_client = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
                
                # 2. Test de Tablas
                tablas_a_probar = ["transacciones", "pedidos_inventario", "gastos_personales"]
                
                for tabla in tablas_a_probar:
                    try:
                        res = supabase_client.table(tabla).select("id", count="exact").limit(1).execute()
                        cant = res.count if hasattr(res, "count") and res.count is not None else len(res.data or [])
                        st.write(f"• **{tabla}**: ✅ OK ({cant} registros detectados)")
                    except Exception as err:
                        st.error(f"• **{tabla}**: ❌ Error detectado:")
                        st.code(str(err), language="bash")
            except Exception as e_conn:
                st.error("❌ Error al inicializar el cliente de Supabase:")
                st.code(str(e_conn), language="bash")
        else:
            st.error("❌ Faltan claves en st.secrets.")

        # 3. Datos de Sesión y Entorno
        st.write("---")
        st.caption("Información del Entorno:")
        st.write(f"- Estado de autenticación: `{st.session_state.get('autenticado', False)}`")
        st.write("- Python runtime: Activo")