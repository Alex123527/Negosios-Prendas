import streamlit as st
import pandas as pd
from datetime import datetime
import io
from supabase import create_client, Client

st.set_page_config(page_title="Gastos Personales | PROYECTO X", page_icon="👤", layout="wide")

# Estilo visual coherente
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #071426; color: #E6EDF5; }
    section[data-testid="stSidebar"] { background-color: #0b1a2f !important; }
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(135deg, #4388FF 0%, #2f6de0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] { color: #21D4C4 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #9FB2C8 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input {
        background-color: #0d1b30 !important;
        color: #E6EDF5 !important;
        border: 1px solid #1E365D !important;
    }
    </style>
""", unsafe_allow_html=True)

# Validación de seguridad
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso restringido. Por favor autentíquese en app.py.")
    st.stop()

# Conexión Supabase
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

def formato_gs(valor):
    try:
        val_int = int(round(float(valor or 0)))
        return f"Gs. {val_int:,}".replace(",", ".")
    except Exception:
        return "Gs. 0"

# Cargar gastos personales desde Supabase
def cargar_gastos():
    try:
        res = supabase.table("gastos_personales").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        return pd.DataFrame()

df_gastos = cargar_gastos()

st.title("👤 GESTIÓN DE GASTOS PERSONALES")
st.caption("CONTROL INDEPENDIENTE DE EGRESOS PRIVADOS (SEPARADO DEL CAPITAL DEL NEGOCIO)")

# Métricas acumuladas
total_gastos = 0
total_registros = 0
if not df_gastos.empty and "monto" in df_gastos.columns:
    df_gastos["monto_num"] = pd.to_numeric(df_gastos["monto"], errors="coerce").fillna(0)
    total_gastos = int(df_gastos["monto_num"].sum())
    total_registros = len(df_gastos)

m1, m2 = st.columns(2)
m1.metric("💸 TOTAL GASTOS ACUMULADOS", formato_gs(total_gastos), f"{total_registros} movimientos")
m2.metric("🛡️ ESTADO PATRIMONIAL", "Cuentas Separadas", "Protegiendo capital de giro")

st.markdown("---")

col_form, col_cat = st.columns([1.8, 1.2])

with col_form:
    st.subheader("📝 REGISTRAR NUEVO GASTO")
    
    with st.form("form_gasto_personal", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_g = st.date_input("Fecha", value=datetime.now())
            categoria_g = st.selectbox("Categoría de Gasto", [
                "Alimentación / Supermercado",
                "Combustible / Transporte",
                "Servicios (Luz, Agua, Internet)",
                "Salud / Medicamentos",
                "Ocio / Salidas",
                "Educación / Cursos",
                "Ropa / Uso Propio",
                "Otros Gastos"
            ])
            forma_pago_g = st.selectbox("Método de Pago", ["Efectivo", "Transferencia", "Billetera Digital / Tarjeta"])

        with c2:
            monto_g = st.number_input("Monto (Gs.)", min_value=0, value=50000, step=5000, format="%d")
            st.caption(f"Monto: **{formato_gs(monto_g)}**")
            descripcion_g = st.text_input("Descripción / Motivo", placeholder="Ej: Compra de almuerzo / Carga de combustible")

        btn_guardar_gasto = st.form_submit_button("💾 ASENTAR GASTO PERSONAL", use_container_width=True)

        if btn_guardar_gasto:
            if monto_g > 0 and descripcion_g.strip():
                nuevo_reg = {
                    "fecha": str(fecha_g),
                    "categoria": categoria_g,
                    "monto": int(monto_g),
                    "descripcion": f"{descripcion_g.strip()} ({forma_pago_g})"
                }
                try:
                    supabase.table("gastos_personales").insert(nuevo_reg).execute()
                    st.success("¡Gasto personal registrado con éxito!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar en Supabase: {e}")
            else:
                st.warning("Ingresa un monto válido y una breve descripción.")

with col_cat:
    st.subheader("📊 DISTRIBUCIÓN POR CATEGORÍA")
    if not df_gastos.empty and "categoria" in df_gastos.columns:
        resumen_cat = df_gastos.groupby("categoria")["monto_num"].sum().reset_index()
        resumen_cat.columns = ["Categoría", "Monto"]
        st.dataframe(resumen_cat.set_index("Categoría"), use_container_width=True)
    else:
        st.info("Sin registros suficientes para graficar.")

st.markdown("---")

# Tabla histórica y exportación
col_th, col_exp = st.columns([2.5, 1.5])
with col_th:
    st.subheader("📋 HISTORIAL DE GASTOS PERSONALES")

if not df_gastos.empty:
    cols_base = ["id", "fecha", "categoria", "descripcion", "monto"]
    cols_vis = [c for c in cols_base if c in df_gastos.columns]
    df_ver = df_gastos[cols_vis].copy()
    if "monto" in df_ver.columns:
        df_ver["MONTO (GS.)"] = pd.to_numeric(df_ver["monto"], errors="coerce").apply(formato_gs)

    # Exportar en Excel
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df_ver.to_excel(writer, index=False, sheet_name='Gastos_Personales')
    excel_file = buf.getvalue()

    with col_exp:
        st.download_button(
            label="📗 Descargar Gastos en Excel (.xlsx)",
            data=excel_file,
            file_name=f"Gastos_Personales_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.dataframe(df_ver, use_container_width=True)

    # Eliminar o corregir un registro
    st.markdown("### ⚙️ ADMINISTRAR REGISTRO")
    opciones_g = {f"ID #{r['id']} - {r.get('fecha')} - {r.get('categoria')} ({formato_gs(r.get('monto'))})": r['id'] for _, r in df_gastos.iterrows()}
    sel_g_txt = st.selectbox("Seleccione registro:", list(opciones_g.keys()))
    sel_g_id = opciones_g[sel_g_txt]

    if st.button("🗑️ ELIMINAR GASTO SELECCIONADO", use_container_width=True):
        try:
            supabase.table("gastos_personales").delete().eq("id", sel_g_id).execute()
            st.success("Gasto eliminado correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"Error al eliminar: {e}")
else:
    st.info("No hay gastos personales registrados aún.")