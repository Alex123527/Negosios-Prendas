import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Caja Negocio | PROYECTO X", page_icon="💼", layout="wide")

# CSS Estilo Futurista
st.markdown("""
    <style>
    @import url('[https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap)');
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

# Cargar transacciones desde Supabase
def cargar_transacciones():
    try:
        res = supabase.table("transacciones").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        return pd.DataFrame()

df_tx = cargar_transacciones()

st.title("💼 FLUJO DE CAJA NEGOCIO")
st.caption("GESTIÓN OPERATIVA Y RENTABILIDAD EN LA NUBE")

# Cálculos de Totales
ingresos_total = 0.0
egresos_total = 0.0

if not df_tx.empty and "monto" in df_tx.columns and "tipo" in df_tx.columns:
    df_tx["monto_num"] = pd.to_numeric(df_tx["monto"], errors="coerce").fillna(0)
    ingresos_total = float(df_tx[df_tx["tipo"] == "Ingreso"]["monto_num"].sum())
    egresos_total = float(df_tx[df_tx["tipo"] == "Egreso"]["monto_num"].sum())

saldo_neto = ingresos_total - egresos_total

# Métricas Principales
col1, col2, col3 = st.columns(3)
col1.metric("📈 INGRESOS NEGOCIO", formato_gs(ingresos_total))
col2.metric("📉 EGRESOS OPERATIVOS", formato_gs(egresos_total))
col3.metric("💵 SALDO NETO DE CAJA", formato_gs(saldo_neto))

st.markdown("---")

col_form, col_resumen = st.columns([2, 1])

with col_form:
    st.subheader("➕ Nueva Operación de Caja")
    st.caption("💡 *Tip: Puedes presionar **Enter** al finalizar para asentar inmediatamente.*")
    
    with st.form("form_caja", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_op = st.date_input("Fecha", value=datetime.now())
            tipo_op = st.selectbox("Tipo de Movimiento", ["Ingreso", "Egreso"])
            categoria_op = st.selectbox("Categoría", [
                "Venta de Prenda", "Cobro de Deuda", "Inversión Mercadería", 
                "Packaging / Envíos", "Publicidad", "Alquiler / Servicios", "Otros Gastos"
            ])
        with c2:
            monto_op = st.number_input("Monto (Gs.)", min_value=0, value=0, step=5000, format="%d")
            desc_op = st.text_input("Concepto / Cliente / Detalle")
        
        btn_guardar = st.form_submit_button("💾 ASENTAR OPERACIÓN (ENTER)")
        
        if btn_guardar:
            if monto_op > 0 and desc_op.strip():
                nueva_tx = {
                    "fecha": str(fecha_op),
                    "tipo": tipo_op,
                    "categoria": categoria_op,
                    "monto": int(monto_op),
                    "descripcion": desc_op
                }
                try:
                    supabase.table("transacciones").insert(nueva_tx).execute()
                    st.success("Transacción registrada con éxito en Supabase.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar: {e}")
            else:
                st.warning("Ingresa una descripción válida y un monto mayor a 0.")

with col_resumen:
    st.subheader("📊 Movimientos por Tipo")
    st.write(f"• **Ingresos totales:** `{formato_gs(ingresos_total)}`")
    st.write(f"• **Egresos totales:** `{formato_gs(egresos_total)}`")
    margen = (saldo_neto / ingresos_total * 100) if ingresos_total > 0 else 0
    st.write(f"• **Margen operativo:** `{margen:.1f}%`")

st.markdown("---")
st.subheader("📋 Libro Diario de Caja")

if not df_tx.empty:
    columnas_mostrar = [c for c in ["id", "fecha", "tipo", "categoria", "monto", "descripcion"] if c in df_tx.columns]
    st.dataframe(df_tx[columnas_mostrar], use_container_width=True)

    st.markdown("### ⚙️ Modificar o Eliminar Transacción")
    tx_id_sel = st.selectbox("Seleccione ID de operación:", df_tx["id"].tolist())
    fila_tx = df_tx[df_tx["id"] == tx_id_sel].iloc[0]

    with st.form("form_edit_caja"):
        ed_desc = st.text_input("Detalle", value=str(fila_tx["descripcion"]))
        ed_monto = st.number_input("Monto (Gs.)", value=int(fila_tx["monto"]), format="%d", step=5000)
        c_ed1, c_ed2 = st.columns(2)
        if c_ed1.form_submit_button("🔄 ACTUALIZAR (ENTER)"):
            try:
                supabase.table("transacciones").update({"descripcion": ed_desc, "monto": int(ed_monto)}).eq("id", tx_id_sel).execute()
                st.success("Operación actualizada en Supabase.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar: {e}")
        if c_ed2.form_submit_button("🗑️ ELIMINAR OPERACIÓN"):
            try:
                supabase.table("transacciones").delete().eq("id", tx_id_sel).execute()
                st.success("Operación eliminada de Supabase.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")
else:
    st.info("No hay movimientos registrados en el flujo de caja aún.")