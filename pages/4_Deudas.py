import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from supabase import create_client, Client

st.set_page_config(
    page_title="Deudas y Cobranzas | PROYECTO X",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# SISTEMA DE ESTILOS VISUALES PREMIUM
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .stApp {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }
    
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
    
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input {
        background-color: #090d16 !important;
        color: #f1f5f9 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 1px #2563eb !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0b1329 !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 6px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 8px 16px !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
    }
    
    [data-testid="stDataFrame"] {
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    .kpi-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .kpi-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
    }
    .kpi-val {
        font-size: 1.55rem;
        font-weight: 800;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# SEGURIDAD Y CONEXIÓN
# =========================================================================
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso restringido. Por favor autentíquese en app.py.")
    st.stop()

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

def cargar_deudas():
    try:
        res = supabase.table("deudas").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con tabla deudas: {e}")
        return pd.DataFrame()

def cargar_pedidos():
    try:
        res = supabase.table("pedidos_inventario").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

df_deudas = cargar_deudas()
df_pedidos = cargar_pedidos()

# =========================================================================
# BANNER PRINCIPAL Y KPIs SUPERIORES
# =========================================================================
st.markdown("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); padding: 22px 26px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);">
        <span style="background: rgba(37, 99, 245, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.35); padding: 3px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
            Módulo de Crédito & Cobranzas
        </span>
        <h1 style="color: #ffffff; font-size: 1.7rem; font-weight: 800; margin: 8px 0 4px 0; letter-spacing: -0.02em;">
            💳 Gestión de Deudas y Cuentas por Cobrar
        </h1>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            Supervisión de saldos a favor, compromisos pendientes con talleres/proveedores y liquidación directa en Caja.
        </p>
    </div>
""", unsafe_allow_html=True)

# Métricas Principales
total_por_cobrar = 0
total_por_pagar = 0
cuentas_pendientes_cobro = 0
cuentas_pendientes_pago = 0

if not df_deudas.empty:
    df_temp = df_deudas.copy()
    df_temp["monto_num"] = pd.to_numeric(df_temp.get("monto_deuda", 0), errors="coerce").fillna(0)
    
    pendientes = df_temp[df_temp.get("estado", "").str.contains("Pendiente|Parcial", case=False, na=False)]
    
    por_cobrar_df = pendientes[~pendientes.get("tipo", "").str.contains("Pagar|Proveedor", case=False, na=False)]
    por_pagar_df = pendientes[pendientes.get("tipo", "").str.contains("Pagar|Proveedor", case=False, na=False)]
    
    total_por_cobrar = int(por_cobrar_df["monto_num"].sum())
    total_por_pagar = int(por_pagar_df["monto_num"].sum())
    cuentas_pendientes_cobro = len(por_cobrar_df)
    cuentas_pendientes_pago = len(por_pagar_df)

saldo_neto_credito = total_por_cobrar - total_por_pagar

col_k1, col_k2, col_k3 = st.columns(3)

with col_k1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">💰 Capital en la Calle (Por Cobrar)</div>
            <div class="kpi-val" style="color: #10b981;">{formato_gs(total_por_cobrar)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">{cuentas_pendientes_cobro} cuentas pendientes de cobro</span>
        </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🧾 Compromisos (Por Pagar)</div>
            <div class="kpi-val" style="color: #ef4444;">{formato_gs(total_por_pagar)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">{cuentas_pendientes_pago} compromisos con terceros</span>
        </div>
    """, unsafe_allow_html=True)

with col_k3:
    color_neto = "#38bdf8" if saldo_neto_credito >= 0 else "#f87171"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">⚖️ Saldo Neto a Favor</div>
            <div class="kpi-val" style="color: {color_neto};">{formato_gs(saldo_neto_credito)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Diferencial entre cobros y pagos</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# =========================================================================
# NAVEGACIÓN POR PESTAÑAS
# =========================================================================
tab_registro, tab_maestro, tab_vencimientos, tab_liquidacion = st.tabs([
    "📝 Asentar Nueva Cuenta",
    "📋 Registro Maestro & Reportes (Excel / PDF)",
    "🔔 Semáforo de Vencimientos",
    "⚙️ Modificar / Liquidar Cuenta"
])

# -------------------------------------------------------------------------
# TAB 1: ASENTAR NUEVA CUENTA
# -------------------------------------------------------------------------
with tab_registro:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    dict_pedidos = {"-- Cargar manualmente (sin vincular pedido) --": None}
    if not df_pedidos.empty:
        for _, p in df_pedidos.iterrows():
            p_id = p.get("id")
            p_cli = p.get("cliente", "Sin Cliente")
            p_prod = p.get("modelo_prenda", "")
            p_cant = p.get("cantidad", 1)
            p_prec = p.get("precio_venta", 0)
            p_tot = int(p_cant) * int(p_prec)
            etiqueta = f"Pedido #{p_id} | {p_cli} | {p_prod} ({formato_gs(p_tot)})"
            dict_pedidos[etiqueta] = p

    sel_ped_vinculo = st.selectbox("🔗 Vincular con Pedido Registrado (Autocompletar datos):", list(dict_pedidos.keys()))
    pedido_elegido = dict_pedidos[sel_ped_vinculo]

    def_cliente = ""
    def_concepto = ""
    def_monto = 0
    def_fecha = datetime.now().date()

    if pedido_elegido is not None:
        def_cliente = str(pedido_elegido.get("cliente", ""))
        cant_v = pedido_elegido.get("cantidad", 1)
        talle_v = pedido_elegido.get("talle", "")
        def_concepto = f"{pedido_elegido.get('modelo_prenda', '')} (Talle: {talle_v}) x {cant_v} uds"
        def_monto = int(cant_v) * int(pedido_elegido.get("precio_venta", 0))
        try:
            def_fecha = datetime.strptime(str(pedido_elegido.get("fecha")), "%Y-%m-%d").date()
        except Exception:
            def_fecha = datetime.now().date()

    with st.form("form_registro_deuda", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            tipo_deuda = st.selectbox("Tipo de Operación", ["Por Cobrar (Cliente me debe)", "Por Pagar (Debo a Proveedor/Taller)"])
            fecha_reg = st.date_input("Fecha de Registro", value=def_fecha)
            cliente_contacto = st.text_input("Nombre de la Persona / Cliente / Proveedor", value=def_cliente, placeholder="Ej: Juan Pérez / Proveedor")
            forma_pago = st.selectbox("Forma de Pago Acordada", ["Efectivo", "Transferencia Bancaria", "Billetera Digital", "Cheque / Pagaré", "Otro"])

        with c2:
            monto_cuenta = st.number_input("Monto de la Deuda (Gs.)", min_value=0, value=def_monto, step=10000, format="%d")
            st.caption(f"Monto: **{formato_gs(monto_cuenta)}**")
            
            fecha_vencimiento = st.date_input("Fecha Límite / Vencimiento", value=datetime.now() + timedelta(days=15))
            estado_inicial = st.selectbox("Estado Actual", ["Pendiente", "Abono Parcial", "Cancelado / Pagado"])
            concepto_det = st.text_input("Concepto / Prenda entregada / Motivo", value=def_concepto, placeholder="Ej: Pantalón Cargo talle 42")

        asentar_en_caja = st.checkbox("Asentar automáticamente en Caja de Negocio si ya se abonó / canceló", value=False)
        
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        btn_guardar_deuda = st.form_submit_button("💾 ASENTAR REGISTRO DE CUENTA", use_container_width=True)

        if btn_guardar_deuda:
            if cliente_contacto.strip() and concepto_det.strip() and monto_cuenta > 0:
                nueva_deuda = {
                    "fecha": str(fecha_reg),
                    "cliente": cliente_contacto.strip(),
                    "concepto": concepto_det.strip(),
                    "monto_deuda": int(monto_cuenta),
                    "estado": estado_inicial,
                    "tipo": tipo_deuda,
                    "forma_pago": forma_pago,
                    "fecha_vencimiento": str(fecha_vencimiento)
                }
                try:
                    supabase.table("deudas").insert(nueva_deuda).execute()

                    if asentar_en_caja and estado_inicial == "Cancelado / Pagado":
                        tipo_trans = "Ingreso" if "Cobrar" in tipo_deuda else "Egreso"
                        categoria_trans = "Cobro de Deuda" if tipo_trans == "Ingreso" else "Proveedores / Costos"
                        
                        transaccion_caja = {
                            "fecha": str(fecha_reg),
                            "tipo": tipo_trans,
                            "categoria": categoria_trans,
                            "monto": int(monto_cuenta),
                            "descripcion": f"Cobro/Pago Cuenta: {cliente_contacto.strip()} | {concepto_det.strip()} [{forma_pago}]"
                        }
                        supabase.table("transacciones").insert(transaccion_caja).execute()
                        st.info(f"✅ Se registró automáticamente el {tipo_trans} de {formato_gs(monto_cuenta)} en Caja de Negocio.")

                    st.success("¡Cuenta asentada exitosamente!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar en Supabase: {e}")
            else:
                st.warning("Completa el nombre, concepto y verifica que el monto sea mayor a 0 Gs.")

# -------------------------------------------------------------------------
# TAB 2: REGISTRO MAESTRO Y EXPORTACIONES
# -------------------------------------------------------------------------
with tab_maestro:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_deudas.empty:
        col_t_tab, col_btn_exp1, col_btn_exp2 = st.columns([2, 1, 1])
        with col_t_tab:
            st.markdown("### 📋 Registro Maestro de Cuentas y Deudas")
            st.caption("Planilla completa con estados, vencimientos y herramientas de exportación oficial.")

        cols_base = ["id", "fecha", "tipo", "cliente", "concepto", "monto_deuda", "forma_pago", "fecha_vencimiento", "estado"]
        cols_existentes = [c for c in cols_base if c in df_deudas.columns]
        df_mostrar = df_deudas[cols_existentes].copy()
        
        if "monto_deuda" in df_mostrar.columns:
            m_num = pd.to_numeric(df_mostrar["monto_deuda"], errors="coerce")