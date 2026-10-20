import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Gastos Personales | PROYECTO X", page_icon="⚡", layout="wide")

# CSS Estilo Futurista Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #071426; color: #E6EDF5; }
    section[data-testid="stSidebar"] { background-color: #0b1a2f !important; }
    .stButton>button {
        background: linear-gradient(135deg, #4388FF 0%, #2f6de0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] { color: #21D4C4 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #9FB2C8 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #0d1b30 !important;
        color: #E6EDF5 !important;
        border: 1px solid #1E365D !important;
    }
    </style>
""", unsafe_allow_html=True)

# Escudo de seguridad
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

df_gastos = cargar_gastos()

# Título limpio
st.title("⚡ CONTROL DE GASTOS PERSONALES")
st.caption("GESTIÓN PATRIMONIAL Y OPTIMIZACIÓN FINANCIERA")

# Cálculos de Métricas
ingreso_mensual_fijo = 2500000.0  # Base mensual estimada en Gs.
gastos_registrados_total = 0.0

if not df_gastos.empty and "monto" in df_gastos.columns:
    df_gastos["monto_num"] = pd.to_numeric(df_gastos["monto"], errors="coerce").fillna(0)
    gastos_registrados_total = float(df_gastos["monto_num"].sum())

capacidad_ahorro = ingreso_mensual_fijo - gastos_registrados_total

# Métricas Superiores
col1, col2, col3 = st.columns(3)
col1.metric("💰 INGRESOS COMPUTADOS", formato_gs(ingreso_mensual_fijo))
col2.metric("🛒 GASTOS REGISTRADOS", formato_gs(gastos_registrados_total))
col3.metric("✨ CAPACIDAD DE AHORRO", formato_gs(capacidad_ahorro))

st.markdown("---")

col_form, col_resumen = st.columns([2, 1])

with col_form:
    # Cambio: Solo dice "REGISTRO DE EGRESO" y se eliminó el texto del Tip
    st.subheader("📝 REGISTRO DE EGRESO")
    
    with st.form("form_gastos", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_g = st.date_input("Fecha", value=datetime.now())
            concepto_g = st.text_input("Concepto / Descripción", placeholder="Ej: Compra de insumos, almuerzo, etc.")
            canal_g = st.selectbox("Canal de Pago", ["Efectivo", "Transferencia / Bancard", "Billetera Zimple / Tigo Money", "Tarjeta de Débito/Crédito"])
        with c2:
            categoria_g = st.selectbox("Categoría", [
                "Alimentación / Supermercado", "Vivienda / Alquiler", "Transporte / Combustible",
                "Servicios (Luz, Agua, Internet)", "Salud / Farmacia", "Educación / Cursos",
                "Ocio / Salidas", "Ropa / Cuidado Personal", "Otros Gastos"
            ])
            monto_g = st.number_input("Monto (Gs.)", min_value=0, value=0, step=5000, format="%d")
            comprobante = st.file_uploader("Adjuntar Comprobante (Opcional)", type=["png", "jpg", "jpeg", "pdf"])

        btn_guardar_g = st.form_submit_button("💾 ASENTAR GASTO")

        if btn_guardar_g:
            if monto_g > 0 and concepto_g.strip():
                nombre_archivo = comprobante.name if comprobante is not None else ""
                nuevo_gasto = {
                    "fecha": str(fecha_g),
                    "descripcion": concepto_g,
                    "categoria": categoria_g,
                    "metodo_pago": canal_g,
                    "monto": int(monto_g),
                    "comprobante_nombre": nombre_archivo
                }
                try:
                    supabase.table("gastos_personales").insert(nuevo_gasto).execute()
                    st.success("Gasto registrado exitosamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Por favor ingresa un concepto y un monto mayor a 0.")

with col_resumen:
    st.subheader("📊 Distribución por Categoría")
    if not df_gastos.empty and "categoria" in df_gastos.columns:
        resumen_cat = df_gastos.groupby("categoria")["monto_num"].sum()
        for cat, val in resumen_cat.items():
            st.write(f"• **{cat}:** `{formato_gs(val)}`")
    else:
        st.write("• *Sin consumos categorizados todavía.*")

st.markdown("---")

# Objetivo de Capitalización con formato de puntos
st.subheader("🎯 OBJETIVO DE CAPITALIZACIÓN")
meta_ahorro_defecto = 1000000  # Gs. 1.000.000
meta_ahorro = st.number_input(
    "Meta de Ahorro Mensual (Gs.)", 
    min_value=0, 
    value=meta_ahorro_defecto, 
    step=50000, 
    format="%d"
)

# Visualización con punto separador de miles
porcentaje_progreso = min(1.0, max(0.0, capacidad_ahorro / meta_ahorro)) if meta_ahorro > 0 else 0.0
st.progress(porcentaje_progreso)
st.caption(f"Meta definida: **{formato_gs(meta_ahorro)}** | Progreso actual: **{porcentaje_progreso * 100:.1f}%** hacia tu objetivo.")

st.markdown("---")

# Cambio: Título simplificado a "REGISTRO DE GASTOS"
st.subheader("📋 REGISTRO DE GASTOS")

if not df_gastos.empty:
    cols_mostrar = [c for c in ["id", "fecha", "descripcion", "categoria", "metodo_pago", "monto", "comprobante_nombre"] if c in df_gastos.columns]
    
    # Formatear visualmente el dataframe para mostrar los montos con puntos
    df_visual = df_gastos[cols_mostrar].copy()
    if "monto" in df_visual.columns:
        df_visual["monto"] = df_visual["monto"].apply(formato_gs)
        
    st.dataframe(df_visual, use_container_width=True)

    st.markdown("### ⚙️ Modificar o Eliminar Gasto")
    id_sel = st.selectbox("Seleccione ID de registro:", df_gastos["id"].tolist())
    fila_sel = df_gastos[df_gastos["id"] == id_sel].iloc[0]

    with st.form("form_edit_gasto"):
        e_desc = st.text_input("Descripción", value=str(fila_sel.get("descripcion", "")))
        e_monto = st.number_input("Monto (Gs.)", value=int(fila_sel.get("monto", 0)), step=5000, format="%d")
        
        c_act1, c_act2 = st.columns(2)
        if c_act1.form_submit_button("🔄 ACTUALIZAR"):
            try:
                supabase.table("gastos_personales").update({
                    "descripcion": e_desc,
                    "monto": int(e_monto)
                }).eq("id", id_sel).execute()
                st.success("Gasto modificado exitosamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar: {e}")

        if c_act2.form_submit_button("🗑️ ELIMINAR REGISTRO"):
            try:
                supabase.table("gastos_personales").delete().eq("id", id_sel).execute()
                st.success("Registro eliminado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")
else:
    st.info("Sin registros de gastos cargados aún en la base de datos.")