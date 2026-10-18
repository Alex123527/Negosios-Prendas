import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(page_title="Finanzas y Reportes | PROYECTO X", page_icon="📈", layout="wide")

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

# Carga de datos de todas las tablas de Supabase
@st.cache_data(ttl=60)
def cargar_todos_los_datos():
    try:
        res_gp = supabase.table("gastos_personales").select("*").execute()
        res_tx = supabase.table("transacciones").select("*").execute()
        res_ped = supabase.table("pedidos_inventario").select("*").execute()
        res_deu = supabase.table("deudas").select("*").execute()
        
        df_gp = pd.DataFrame(res_gp.data) if res_gp.data else pd.DataFrame()
        df_tx = pd.DataFrame(res_tx.data) if res_tx.data else pd.DataFrame()
        df_ped = pd.DataFrame(res_ped.data) if res_ped.data else pd.DataFrame()
        df_deu = pd.DataFrame(res_deu.data) if res_deu.data else pd.DataFrame()
        return df_gp, df_tx, df_ped, df_deu
    except Exception as e:
        st.error(f"Error al sincronizar reportes: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_gp, df_tx, df_ped, df_deu = cargar_todos_los_datos()

st.title("📈 BALANCE GENERAL & INTELIGENCIA FINANCIERA")
st.caption("CONSOLIDADO EJECUTIVO EN TIEMPO REAL DESDE SUPABASE")

if st.button("🔄 Actualizar Datos en Vivo"):
    st.cache_data.clear()
    st.rerun()

# 1. Cálculos de Negocio (Caja)
ingresos_negocio = 0.0
egresos_negocio = 0.0
if not df_tx.empty and "tipo" in df_tx.columns and "monto" in df_tx.columns:
    df_tx["monto_num"] = pd.to_numeric(df_tx["monto"], errors="coerce").fillna(0)
    ingresos_negocio = float(df_tx[df_tx["tipo"] == "Ingreso"]["monto_num"].sum())
    egresos_negocio = float(df_tx[df_tx["tipo"] == "Egreso"]["monto_num"].sum())

flujo_neto_negocio = ingresos_negocio - egresos_negocio

# 2. Cálculos de Finanzas Personales
gastos_personales_total = 0.0
if not df_gp.empty and "monto" in df_gp.columns:
    df_gp["monto_num"] = pd.to_numeric(df_gp["monto"], errors="coerce").fillna(0)
    gastos_personales_total = float(df_gp["monto_num"].sum())

# 3. Cuentas por Cobrar (Deudas activas)
cuentas_pendientes = 0.0
if not df_deu.empty and "monto_deuda" in df_deu.columns and "estado" in df_deu.columns:
    df_deu["monto_num"] = pd.to_numeric(df_deu["monto_deuda"], errors="coerce").fillna(0)
    cuentas_pendientes = float(df_deu[df_deu["estado"] == "Pendiente"]["monto_num"].sum())

# 4. Valoración de Stock
valor_stock_proyectado = 0.0
if not df_ped.empty and "cantidad" in df_ped.columns and "precio_venta" in df_ped.columns:
    df_ped["cant_num"] = pd.to_numeric(df_ped["cantidad"], errors="coerce").fillna(0)
    df_ped["precio_num"] = pd.to_numeric(df_ped["precio_venta"], errors="coerce").fillna(0)
    valor_stock_proyectado = float((df_ped["cant_num"] * df_ped["precio_num"]).sum())

# Métricas Ejecutivas
m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 DISPONIBLE CAJA NEGOCIO", formato_gs(flujo_neto_negocio))
m2.metric("💳 GASTOS PERSONALES TOTALES", formato_gs(gastos_personales_total))
m3.metric("⏳ PENDIENTE DE COBRO (DEUDAS)", formato_gs(cuentas_pendientes))
m4.metric("📦 VALOR DE MERCADERÍA", formato_gs(valor_stock_proyectado))

st.markdown("---")

col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("📊 Rentabilidad de la Operación (Caja)")
    margen_neto = (flujo_neto_negocio / ingresos_negocio * 100) if ingresos_negocio > 0 else 0
    st.write(f"• **Ingresos Brutos:** `{formato_gs(ingresos_negocio)}`")
    st.write(f"• **Costes / Egresos:** `{formato_gs(egresos_negocio)}`")
    st.write(f"• **Utilidad Neta de Caja:** `{formato_gs(flujo_neto_negocio)}`")
    st.write(f"• **Margen Neto:** `{margen_neto:.1f}%`")
    
    if flujo_neto_negocio > 0:
        st.success("✨ Operación comercial superavitaria.")
    elif flujo_neto_negocio < 0:
        st.error("⚠️ La caja opera con saldo deficitario.")
    else:
        st.info("Sin movimientos operativos registrados.")

with col_der:
    st.subheader("🏛️ Patrimonio y Liquidez Integral")
    liquidez_potencial = flujo_neto_negocio + cuentas_pendientes
    patrimonio_total = liquidez_potencial + valor_stock_proyectado
    
    st.write(f"• **Liquidez Inmediata:** `{formato_gs(flujo_neto_negocio)}`")
    st.write(f"• **Liquidez Esperada (Caja + Cobros):** `{formato_gs(liquidez_potencial)}`")
    st.write(f"• **Activos en Inventario:** `{formato_gs(valor_stock_proyectado)}`")
    st.write(f"• **Patrimonio Comercial Bruto:** `{formato_gs(patrimonio_total)}`")

st.markdown("---")
st.subheader("📑 Auditoría y Exportación de Registros")

tab1, tab2, tab3, tab4 = st.tabs(["💼 Transacciones Negocio", "🛒 Gastos Personales", "🛍️ Pedidos e Inventario", "⚖️ Deudas"])

with tab1:
    if not df_tx.empty:
        st.dataframe(df_tx, use_container_width=True)
    else:
        st.info("No hay datos en transacciones.")

with tab2:
    if not df_gp.empty:
        st.dataframe(df_gp, use_container_width=True)
    else:
        st.info("No hay datos en gastos personales.")

with tab3:
    if not df_ped.empty:
        st.dataframe(df_ped, use_container_width=True)
    else:
        st.info("No hay datos en inventario.")

with tab4:
    if not df_deu.empty:
        st.dataframe(df_deu, use_container_width=True)
    else:
        st.info("No hay datos en deudas.")