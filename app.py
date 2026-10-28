from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PROYECTO X | Financial Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# SISTEMA DE ESTILOS VISUALES (Paneles anchos + Botones multilínea elegantes)
# =========================================================================
css_estilos = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background-color: #0f172a !important;
    color: #f8fafc !important;
}

/* Maximizar ancho útil de los paneles */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 96% !important;
}

section[data-testid="stSidebar"] {
    background-color: #0b1329 !important;
    border-right: 1px solid #1e293b !important;
}

/* Tarjeta de Login */
.premium-card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    margin-bottom: 20px;
}

/* Transformar botones centrales en Tarjetas Flotantes Elegantes */
div[data-testid="stColumn"] .stButton > button {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 16px !important;
    padding: 22px 24px !important;
    text-align: left !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3) !important;
    display: block !important;
    width: 100% !important;
    min-height: 140px !important;
    height: auto !important;
    white-space: normal !important; /* Permite saltos de línea sin cortar textos */
    line-height: 1.55 !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

div[data-testid="stColumn"] .stButton > button:hover {
    background: #24344d !important;
    border-color: #38bdf8 !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 16px 30px -5px rgba(56, 189, 248, 0.22) !important;
}

/* Estilo del texto interior del botón */
div[data-testid="stColumn"] .stButton > button div p {
    font-size: 0.88rem !important;
    color: #94a3b8 !important;
    white-space: normal !important;
    text-align: left !important;
}

h1, h2, h3, h4 {
    color: #ffffff !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}

.stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
    background-color: #090d16 !important;
    color: #f1f5f9 !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 1px #2563eb !important;
}

/* Botones regulares (Login y Sidebar) */
.stFormSubmitButton>button, .stSidebar button {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(59, 130, 246, 0.4) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1.2rem !important;
    box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.25) !important;
}

hr {
    border-color: #1e293b !important;
}
"""
st.markdown(f"<style>{css_estilos}</style>", unsafe_allow_html=True)

# =========================================================================
# GESTIÓN DE SESIÓN Y LOGIN
# =========================================================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.6, 1])
    
    with c2:
        card_login_html = """
        <div class="premium-card" style="text-align: center; padding: 32px 28px;">
            <div style="background: rgba(37, 99, 245, 0.15); width: 56px; height: 56px; border-radius: 14px; margin: 0 auto 14px auto; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(59, 130, 246, 0.35);">
                <span style="font-size: 1.8rem;">⚡</span>
            </div>
            <span style="background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.25); padding: 3px 10px; border-radius: 9999px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
                Portal Corporativo Seguro
            </span>
            <h2 style="margin: 12px 0 4px 0; font-size: 1.7rem; color: #ffffff;">PROYECTO X</h2>
            <p style="color: #94a3b8; font-size: 0.82rem; margin: 0 0 16px 0;">SISTEMA CENTRAL DE GESTIÓN Y FINANZAS</p>
            <div style="height: 1px; background: #1e293b; margin: 18px 0;"></div>
        </div>
        """
        st.markdown(card_login_html, unsafe_allow_html=True)
        
        with st.form("login_form"):
            correo_ingresado = st.text_input("Credencial / Correo Electrónico", placeholder="usuario@empresa.com")
            password_ingresada = st.text_input("Contraseña de Acceso", type="password", placeholder="••••••••")
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
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

# =========================================================================
# MENÚ LATERAL Y CIERRE DE SESIÓN
# =========================================================================
sidebar_html = """
<div style="padding: 12px 4px 8px 4px; border-bottom: 1px solid #1e293b; margin-bottom: 15px;">
    <span style="font-size: 0.7rem; font-weight: 700; color: #10b981; letter-spacing: 0.08em; text-transform: uppercase;">
        ● En Línea
    </span>
    <h3 style="color: #ffffff; margin: 4px 0 0 0; font-size: 1.25rem;">⚡ PROYECTO X</h3>
    <p style="color: #94a3b8; font-size: 0.75rem; margin: 0;">Plataforma Cloud Activa</p>
</div>
"""
st.sidebar.markdown(sidebar_html, unsafe_allow_html=True)

if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
    st.session_state["autenticado"] = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Haz clic en cualquier tarjeta central para ingresar al módulo.")

# =========================================================================
# BANNER PRINCIPAL
# =========================================================================
banner_html = """
<div style="background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); padding: 28px 34px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 26px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);">
    <span style="background: rgba(37, 99, 245, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.35); padding: 3px 12px; border-radius: 9999px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
        Centro de Operaciones
    </span>
    <h1 style="color: #ffffff; font-size: 1.95rem; font-weight: 800; margin: 10px 0 6px 0; letter-spacing: -0.02em;">
        Bienvenido al Centro de Mando Financiero
    </h1>
    <p style="color: #94a3b8; font-size: 0.92rem; margin: 0; line-height: 1.6;">
        Selecciona un módulo para gestionar pedidos, registrar movimientos de caja, revisar vencimientos o auditar las finanzas.
    </p>
</div>
"""
st.markdown(banner_html, unsafe_allow_html=True)

# =========================================================================
# TARJETAS NATIVAS CLICKEABLES (Mantiene sesión activa sin refresco HTTP)
# =========================================================================
col1, col2 = st.columns(2)

with col1:
    btn_pedidos = st.button(
        "🏷️ **PEDIDOS Y CATÁLOGO DE PRENDAS**  \n\n"
        "Control de catálogo de prendas, registro por talle, fletes con transportadoras, calculadora de márgenes comerciales y exportación en Excel y PDF.",
        key="card_pedidos",
        use_container_width=True
    )
    if btn_pedidos:
        st.switch_page("pages/3_Pedidos_Precios.py")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    btn_caja = st.button(
        "💼 **CAJA DE NEGOCIO Y TESORERÍA**  \n\n"
        "Libro diario de ingresos y egresos comerciales, rendición por clientes, adjuntos de comprobantes y arqueo del saldo neto disponible.",
        key="card_caja",
        use_container_width=True
    )
    if btn_caja:
        st.switch_page("pages/2_Caja_Negocio.py")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    btn_gastos = st.button(
        "👤 **GESTIÓN DE GASTOS PERSONALES**  \n\n"
        "Control independiente de salidas privadas por categoría (supermercado, combustible, servicios) para blindar y proteger el capital de giro.",
        key="card_gastos",
        use_container_width=True
    )
    if btn_gastos:
        st.switch_page("pages/1_Gastos_Personales.py")

with col2:
    btn_deudas = st.button(
        "💳 **DEUDAS Y CUENTAS POR COBRAR**  \n\n"
        "Supervisión del capital en la calle, compromisos con proveedores, semáforo de vencimientos en mora y liquidación directa con pase a caja.",
        key="card_deudas",
        use_container_width=True
    )
    if btn_deudas:
        st.switch_page("pages/4_Deudas.py")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    btn_finanzas = st.button(
        "📈 **FINANZAS GENERALES Y BALANCE**  \n\n"
        "Consolidación financiera ejecutiva, balance integral entre negocio y retiros personales, rentabilidad por prenda y descarga de libros multi-hoja en Excel.",
        key="card_finanzas",
        use_container_width=True
    )
    if btn_finanzas:
        st.switch_page("pages/5_Finanzas_Generales.py")

# =========================================================================
# HERRAMIENTA DE DIAGNÓSTICO EN SIDEBAR
# =========================================================================
with st.sidebar.expander("🛠️ DIAGNÓSTICO DEL SISTEMA", expanded=False):
    st.caption("Verificación de credenciales en secrets y conexión con Supabase.")
    
    if st.button("🔍 EJECUTAR TEST DE SALUD", use_container_width=True):
        st.write("---")
        if "supabase" in st.secrets and "url" in st.secrets["supabase"] and "key" in st.secrets["supabase"]:
            st.success("✅ Credenciales detectadas en st.secrets.")
            try:
                from supabase import create_client
                supabase_client = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
                
                tablas_a_probar = ["transacciones", "pedidos_inventario", "deudas", "gastos_personales"]
                
                for tabla in tablas_a_probar:
                    try:
                        res = supabase_client.table(tabla).select("id", count="exact").limit(1).execute()
                        cant = res.count if hasattr(res, "count") and res.count is not None else len(res.data or [])
                        st.write(f"• **{tabla}**: ✅ OK ({cant} registros)")
                    except Exception as err:
                        st.error(f"• **{tabla}**: ❌ Error detectado:")
                        st.code(str(err), language="bash")
            except Exception as e_conn:
                st.error("❌ Error al inicializar el cliente de Supabase:")
                st.code(str(e_conn), language="bash")
        else:
            st.error("❌ Faltan credenciales de Supabase en st.secrets.")

        st.write("---")
        st.caption("Estado de la Sesión:")
        st.write(f"- Autenticado: `{st.session_state.get('autenticado', False)}`")
        st.write("- Entorno: Producción Streamlit")