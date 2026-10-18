import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Gastos Personales | PROYECTO X", page_icon="⚡", layout="wide")

# CSS Futurista Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #071426; color: #E6EDF5; }
    section[data-testid="stSidebar"] { background-color: #0b1a2f !important; }
    .premium-card {
        background-color: #10213A;
        border: 1px solid #1E365D;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #4388FF 0%, #2f6de0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(67, 136, 255, 0.25) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #5c9bff 0%, #4388FF 100%) !important;
        transform: translateY(-1px);
    }
    [data-testid="stMetricValue"] { color: #21D4C4 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #9FB2C8 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #0d1b30 !important;
        color: #E6EDF5 !important;
        border: 1px solid #1E365D !important;
    }
    </style>
""", unsafe_allow_html=True)

# Escudo de Seguridad
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso restringido. Por favor autentíquese en app.py.")
    st.stop()

# Conexión a Supabase
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

# Función para formatear Guaraníes (sin decimales, separador de miles con punto)
def formato_gs(valor):
    try:
        val_int = int(round(float(valor or 0)))
        return f"Gs. {val_int:,}".replace(",", ".")
    except Exception:
        return "Gs. 0"

# Cargar gastos desde Supabase
def cargar_gastos():
    try:
        res = supabase.table("gastos_personales").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        return pd.DataFrame()

df_gp = cargar_gastos()

st.title("⚡ CONTROL DE GASTOS PERSONALES")
st.caption("CLOUD PERSISTENCE & WEALTH BUILDING")

# Cálculos
if not df_gp.empty and "monto" in df_gp.columns:
    df_gp["monto_num"] = pd.to_numeric(df_gp["monto"], errors="coerce").fillna(0)
    total_gastos_p = float(df_gp["monto_num"].sum())
else:
    total_gastos_p = 0.0

total_ingresos_p = 2500000.0
ahorro_p = max(0.0, total_ingresos_p - total_gastos_p)

# Métricas Principales en Gs.
m1, m2, m3 = st.columns(3)
m1.metric("💰 INGRESOS COMPUTADOS", formato_gs(total_ingresos_p))
m2.metric("🛒 GASTOS REGISTRADOS", formato_gs(total_gastos_p))
m3.metric("✨ CAPACIDAD DE AHORRO", formato_gs(ahorro_p))

st.markdown("---")

col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("📝 Nuevo Registro de Egreso")
    st.caption("💡 *Tip: Puedes presionar **Enter** tras ingresar el monto para guardar automáticamente.*")
    
    with st.form("form_gasto_personal", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            fecha_gasto = st.date_input("Fecha", value=datetime.now())
            descripcion_gasto = st.text_input("Concepto / Descripción")
            categoria_gasto = st.selectbox("Categoría", ["Vivienda", "Comida", "Transporte", "Servicios", "Ocio", "Salud", "Estudios", "Otros"])
        with f_col2:
            metodo_pago = st.selectbox("Canal de Pago", ["Efectivo", "Débito", "Débito automático", "Transferencia", "Tarjeta de crédito"])
            monto_gasto = st.number_input("Monto (Gs.)", min_value=0, value=0, step=5000, format="%d")
            archivo_comprobante = st.file_uploader("Documento de Respaldo", type=["png", "jpg", "jpeg", "pdf"])
        
        submit_gasto = st.form_submit_button("💾 ASENTAR GASTO (ENTER)")
        
        if submit_gasto:
            if monto_gasto > 0 and descripcion_gasto.strip():
                nombre_archivo = archivo_comprobante.name if archivo_comprobante else "Sin archivo"
                nuevo_registro = {
                    "fecha": str(fecha_gasto),
                    "descripcion": descripcion_gasto,
                    "categoria": categoria_gasto,
                    "metodo_pago": metodo_pago,
                    "monto": int(monto_gasto),
                    "comprobante_nombre": nombre_archivo
                }
                try:
                    supabase.table("gastos_personales").insert(nuevo_registro).execute()
                    st.success("Operación guardada en Supabase.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Ingresa una descripción válida y un monto mayor a 0.")

with col_der:
    st.subheader("📊 Distribución por Categoría")
    categorias_lista = ["Vivienda", "Comida", "Transporte", "Servicios", "Ocio", "Salud", "Estudios", "Otros"]
    for cat in categorias_lista:
        if not df_gp.empty and "categoria" in df_gp.columns and "monto_num" in df_gp.columns:
            sub_monto = df_gp[df_gp["categoria"] == cat]["monto_num"].sum()
        else:
            sub_monto = 0.0
        st.write(f"• **{cat}**: `{formato_gs(sub_monto)}`")

st.markdown("---")

col_meta1, col_meta2 = st.columns(2)
with col_meta1:
    st.subheader("🎯 Objetivo de Capitalización")
    meta_objetivo = st.number_input("Meta de Ahorro Activo (Gs.):", min_value=10000, value=1000000, step=50000, format="%d")
    porcentaje_ahorro = min(100, int((ahorro_p / meta_objetivo) * 100))
    st.progress(porcentaje_ahorro / 100, text=f"Rendimiento: {porcentaje_ahorro}% ({formato_gs(ahorro_p)} / {formato_gs(meta_objetivo)})")
    if porcentaje_ahorro >= 100:
        st.success("✨ Meta superada con éxito.")

with col_meta2:
    st.subheader("📌 Anotaciones Financieras")
    st.text_area("Notas estratégicas:", placeholder="Estrategia de reducción de costes, compras planificadas...")
    if st.button("Guardar Nota"):
        st.success("Nota preservada.")

st.markdown("---")
st.subheader("📋 Registro Maestro de Gastos (Supabase)")

if not df_gp.empty:
    cols_mostrar = [c for c in ["id", "fecha", "descripcion", "categoria", "metodo_pago", "monto", "comprobante_nombre"] if c in df_gp.columns]
    st.dataframe(df_gp[cols_mostrar], use_container_width=True)

    st.markdown("### ⚙️ ADMINISTRACIÓN DE REGISTROS")
    sel_id = st.selectbox("ID de Transacción a Modificar / Eliminar:", df_gp['id'].tolist())
    fila_sel = df_gp[df_gp['id'] == sel_id].iloc[0]

    with st.form("form_edit_supabase"):
        eg_desc = st.text_input("Descripción", value=str(fila_sel['descripcion']))
        eg_monto = st.number_input("Monto (Gs.)", value=int(fila_sel['monto']), format="%d", step=1000)
        c_bt1, c_bt2 = st.columns(2)
        if c_bt1.form_submit_button("🔄 ACTUALIZAR (ENTER)"):
            try:
                supabase.table("gastos_personales").update({"descripcion": eg_desc, "monto": int(eg_monto)}).eq("id", sel_id).execute()
                st.success("Registro modificado en la nube.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar: {e}")
        if c_bt2.form_submit_button("🗑️ PURGAR REGISTRO"):
            try:
                supabase.table("gastos_personales").delete().eq("id", sel_id).execute()
                st.success("Registro eliminado de la nube.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")
else:
    st.info("Sin operaciones registradas todavía en la nube.")