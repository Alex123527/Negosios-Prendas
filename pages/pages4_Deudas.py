import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Gestión de Deudas | PROYECTO X", page_icon="⚖️", layout="wide")

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

# Cargar deudas desde Supabase
def cargar_deudas():
    try:
        res = supabase.table("deudas").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        return pd.DataFrame()

df_deudas = cargar_deudas()

st.title("⚖️ CONTROL DE DEUDAS Y CRÉDITOS")
st.caption("CUENTAS POR COBRAR Y LIQUIDACIÓN EN LA NUBE")

# Cálculos de Métricas
total_por_cobrar = 0.0
total_saldado = 0.0
cant_pendientes = 0

if not df_deudas.empty and "monto_deuda" in df_deudas.columns and "estado" in df_deudas.columns:
    df_deudas["monto_num"] = pd.to_numeric(df_deudas["monto_deuda"], errors="coerce").fillna(0)
    total_por_cobrar = float(df_deudas[df_deudas["estado"] == "Pendiente"]["monto_num"].sum())
    total_saldado = float(df_deudas[df_deudas["estado"] == "Cobrado / Pagado"]["monto_num"].sum())
    cant_pendientes = int((df_deudas["estado"] == "Pendiente").sum())

col1, col2, col3 = st.columns(3)
col1.metric("⏳ TOTAL POR COBRAR (PENDIENTE)", formato_gs(total_por_cobrar))
col2.metric("✅ TOTAL LIQUIDADO / SALDADO", formato_gs(total_saldado))
col3.metric("👤 CUENTAS PENDIENTES", f"{cant_pendientes} registros")

st.markdown("---")

col_reg, col_info = st.columns([2, 1])

with col_reg:
    st.subheader("📝 Asentar Nueva Cuenta / Deuda")
    st.caption("💡 *Tip: Puedes presionar **Enter** tras ingresar el monto para asentar inmediatamente.*")

    with st.form("form_deuda", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            fecha_d = st.date_input("Fecha", value=datetime.now())
            cliente_d = st.text_input("Nombre de la Persona / Cliente", placeholder="Ej: Juan Pérez")
            concepto_d = st.text_input("Concepto / Prenda entregada", placeholder="Ej: Pantalón Cargo talle L")
        with f2:
            monto_d = st.number_input("Monto de la Deuda (Gs.)", min_value=0, value=0, step=5000, format="%d")
            estado_d = st.selectbox("Estado Actual", ["Pendiente", "Cobrado / Pagado"])

        btn_guardar_d = st.form_submit_button("💾 ASENTAR REGISTRO (ENTER)")

        if btn_guardar_d:
            if monto_d > 0 and cliente_d.strip():
                nueva_deuda = {
                    "fecha": str(fecha_d),
                    "cliente": cliente_d,
                    "concepto": concepto_d,
                    "monto_deuda": int(monto_d),
                    "estado": estado_d
                }
                try:
                    supabase.table("deudas").insert(nueva_deuda).execute()
                    st.success("Cuenta registrada correctamente en Supabase.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar: {e}")
            else:
                st.warning("Ingresa el nombre del cliente y un monto mayor a 0.")

with col_info:
    st.subheader("💡 Resumen Rápido")
    st.write(f"• **Pendientes activas:** `{cant_pendientes}`")
    st.write(f"• **Capital en la calle:** `{formato_gs(total_por_cobrar)}`")
    if total_por_cobrar > 0:
        st.warning("Existen cobros pendientes por liquidar.")
    else:
        st.success("¡Al día! No hay cuentas pendientes.")

st.markdown("---")
st.subheader("📋 Registro Maestro de Cuentas")

if not df_deudas.empty:
    cols_d = [c for c in ["id", "fecha", "cliente", "concepto", "monto_deuda", "estado"] if c in df_deudas.columns]
    st.dataframe(df_deudas[cols_d], use_container_width=True)

    st.markdown("### ⚙️ Marcar como Cobrado o Modificar")
    id_d_sel = st.selectbox("Seleccione ID de registro:", df_deudas["id"].tolist())
    fila_d = df_deudas[df_deudas["id"] == id_d_sel].iloc[0]

    with st.form("form_edit_deuda"):
        ed_cli = st.text_input("Cliente", value=str(fila_d.get("cliente", "")))
        ed_conc = st.text_input("Concepto", value=str(fila_d.get("concepto", "")))
        ed_monto_d = st.number_input("Monto (Gs.)", value=int(fila_d.get("monto_deuda", 0)), step=5000, format="%d")
        
        estados_posibles = ["Pendiente", "Cobrado / Pagado"]
        idx_est = estados_posibles.index(fila_d["estado"]) if fila_d.get("estado") in estados_posibles else 0
        ed_est = st.selectbox("Estado de Deuda", estados_posibles, index=idx_est)

        c_d1, c_d2 = st.columns(2)
        if c_d1.form_submit_button("🔄 ACTUALIZAR ESTADO (ENTER)"):
            try:
                supabase.table("deudas").update({
                    "cliente": ed_cli,
                    "concepto": ed_conc,
                    "monto_deuda": int(ed_monto_d),
                    "estado": ed_est
                }).eq("id", id_d_sel).execute()
                st.success("Estado de cuenta actualizado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar: {e}")

        if c_d2.form_submit_button("🗑️ PURGAR REGISTRO"):
            try:
                supabase.table("deudas").delete().eq("id", id_d_sel).execute()
                st.success("Registro eliminado de Supabase.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")
else:
    st.info("Sin registros de deudas o cuentas por cobrar por el momento.")