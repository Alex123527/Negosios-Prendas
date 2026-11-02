import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from supabase import create_client, Client

st.set_page_config(
    page_title="Deudas y Cobranzas | AGL STORE",
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

# Cargas con Memoria Caché de 60 segundos
@st.cache_data(ttl=60)
def cargar_deudas():
    try:
        res = supabase.table("deudas").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con tabla deudas: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
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
            Supervisión de capital en la calle, compromisos pendientes con talleres y pase contable directo a Caja de Negocio.
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

                    st.cache_data.clear()
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
            m_num = pd.to_numeric(df_mostrar["monto_deuda"], errors="coerce").fillna(0)
            df_mostrar["TOTAL (GS.)"] = m_num.apply(formato_gs)

        # 1. Exportación Excel
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_mostrar.to_excel(writer, index=False, sheet_name='Deudas')
        excel_data = buffer_excel.getvalue()

        with col_btn_exp1:
            st.download_button(
                label="📗 Descargar Excel (.xlsx)",
                data=excel_data,
                file_name=f"Cuentas_Deudas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # 2. Exportación PDF Imprimible (AGL STORE)
        with col_btn_exp2:
            fecha_hoy_corte = datetime.now().strftime('%d/%m/%Y')
            df_impresion = df_deudas.sort_values(by="id", ascending=True) if "id" in df_deudas.columns else df_deudas

            calc_monto_total = int(df_deudas["monto_deuda"].sum()) if "monto_deuda" in df_deudas.columns else 0
            
            # Pendiente real
            df_pend_print = df_deudas[df_deudas.get("estado", "").str.contains("Pendiente|Parcial", case=False, na=False)]
            calc_saldo = int(pd.to_numeric(df_pend_print.get("monto_deuda", 0), errors="coerce").fillna(0).sum())

            filas_html = ""
            for _, f in df_impresion.iterrows():
                m_val = f.get('monto_deuda', 0)
                filas_html += f"""
                <tr>
                    <td style='text-align: center; color: #000000;'>{f.get('id', '')}</td>
                    <td style='text-align: center; color: #000000;'>{f.get('fecha', '')}</td>
                    <td style='text-align: center; color: #000000;'>{f.get('tipo', '')}</td>
                    <td style='color: #000000; font-weight: 600;'>{f.get('cliente', '')}</td>
                    <td style='color: #000000;'>{f.get('concepto', '')}</td>
                    <td style='text-align: right; font-weight: bold; color: #000000;'>{formato_gs(m_val)}</td>
                </tr>
                """

            html_reporte_deudas = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>AGL STORE - Deudas</title>
                <style>
                    @page {{ size: auto; margin: 0; }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                        margin: 0;
                        padding-top: 1cm; padding-right: 1cm; padding-bottom: 1cm; padding-left: 2cm;
                        color: #000000; background: #ffffff;
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }}
                    .header {{
                        display: flex; justify-content: space-between; align-items: center;
                        border-bottom: 2px solid #000000; padding-bottom: 8px; margin-bottom: 14px;
                    }}
                    .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; color: #000000; letter-spacing: -0.02em; }}
                    .fecha-emision {{ text-align: right; font-size: 11px; color: #000000; }}
                    .resumen-cards {{ display: flex; gap: 12px; margin-bottom: 14px; }}
                    .card {{
                        flex: 1; background: #ffffff !important; border: 1px solid #000000;
                        border-radius: 4px; padding: 8px 12px;
                    }}
                    .card-label {{ font-size: 9px; font-weight: 700; text-transform: uppercase; color: #334155; letter-spacing: 0.05em; }}
                    .card-val {{ font-size: 14px; font-weight: 800; margin-top: 2px; color: #000000; }}
                    table {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
                    th, td {{ border: 1px solid #cbd5e1; padding: 7px 10px; text-align: left; }}
                    th {{
                        background-color: #e2e8f0 !important; color: #0f172a !important;
                        font-size: 9px; text-transform: uppercase; letter-spacing: 0.05em;
                        font-weight: 700; text-align: center !important; border: 1px solid #cbd5e1;
                        -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
                    }}
                    tbody tr:nth-child(odd) {{ background-color: #ffffff !important; }}
                    tbody tr:nth-child(even) {{
                        background-color: #f1f5f9 !important;
                        -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
                    }}
                </style>
            </head>
            <body onload="window.print()">
                <div class="header">
                    <div><h1>AGL STORE</h1></div>
                    <div class="fecha-emision">Fecha de Emisión: <strong>{fecha_hoy_corte}</strong></div>
                </div>
                <div class="resumen-cards">
                    <div class="card">
                        <div class="card-label">Total Registros</div>
                        <div class="card-val">{len(df_deudas)}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Monto Histórico Total</div>
                        <div class="card-val">{formato_gs(calc_monto_total)}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Saldo Pendiente Activo</div>
                        <div class="card-val">{formato_gs(calc_saldo)}</div>
                    </div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 35px; text-align: center;">ID</th>
                            <th style="width: 85px; text-align: center;">Fecha</th>
                            <th style="width: 80px; text-align: center;">Tipo</th>
                            <th style="width: 140px; text-align: center;">Cliente / Contacto</th>
                            <th style="text-align: center;">Concepto</th>
                            <th style="width: 100px; text-align: center;">Monto</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_html}
                    </tbody>
                </table>
            </body>
            </html>
            """

            st.download_button(
                label="📄 Imprimir / PDF",
                data=html_reporte_deudas,
                file_name=f"Reporte_Deudas_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )

        st.dataframe(df_mostrar, use_container_width=True)
    else:
        st.info("Sin registros de deudas o cuentas por cobrar por el momento.")

# -------------------------------------------------------------------------
# TAB 3: SEMÁFORO DE VENCIMIENTOS
# -------------------------------------------------------------------------
with tab_vencimientos:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🔔 Control de Vencimientos y Compromisos")
    st.caption("Semáforo preventivo según la fecha acordada de cobro o pago.")

    if not df_deudas.empty and "fecha_vencimiento" in df_deudas.columns:
        df_semaforo = df_deudas.copy()
        df_semaforo["venc_date"] = pd.to_datetime(df_semaforo["fecha_vencimiento"], errors="coerce").dt.date
        hoy = datetime.now().date()

        # Filtrar solo cuentas pendientes
        df_pend = df_semaforo[~df_semaforo.get("estado", "").str.contains("Cancelado|Pagado", case=False, na=False)].copy()

        if not df_pend.empty:
            df_vencidas = df_pend[df_pend["venc_date"] < hoy]
            df_proximas = df_pend[(df_pend["venc_date"] >= hoy) & (df_pend["venc_date"] <= hoy + timedelta(days=5))]
            df_en_fecha = df_pend[df_pend["venc_date"] > hoy + timedelta(days=5)]

            c_v1, c_v2, c_v3 = st.columns(3)
            with c_v1:
                st.markdown(f"""
                    <div class="kpi-card" style="border-left: 4px solid #ef4444;">
                        <div class="kpi-label" style="color: #ef4444;">🔴 Plazo Vencido</div>
                        <div class="kpi-val" style="color: #ef4444;">{len(df_vencidas)} cuentas</div>
                        <span style="font-size: 0.75rem; color: #94a3b8;">Requieren gestión inmediata</span>
                    </div>
                """, unsafe_allow_html=True)
            with c_v2:
                st.markdown(f"""
                    <div class="kpi-card" style="border-left: 4px solid #f59e0b;">
                        <div class="kpi-label" style="color: #f59e0b;">🟡 Por Vencer (≤ 5 días)</div>
                        <div class="kpi-val" style="color: #f59e0b;">{len(df_proximas)} cuentas</div>
                        <span style="font-size: 0.75rem; color: #94a3b8;">Próximos compromisos</span>
                    </div>
                """, unsafe_allow_html=True)
            with c_v3:
                st.markdown(f"""
                    <div class="kpi-card" style="border-left: 4px solid #10b981;">
                        <div class="kpi-label" style="color: #10b981;">🟢 En Plazo Normal</div>
                        <div class="kpi-val" style="color: #10b981;">{len(df_en_fecha)} cuentas</div>
                        <span style="font-size: 0.75rem; color: #94a3b8;">Plazo holgado</span>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            cols_sem = [c for c in ["id", "fecha", "tipo", "cliente", "concepto", "monto_deuda", "fecha_vencimiento", "estado"] if c in df_pend.columns]
            st.dataframe(df_pend[cols_sem], use_container_width=True)
        else:
            st.success("🎉 ¡Excelente! No hay cuentas pendientes ni vencidas actualmente.")
    else:
        st.info("Sin registros de deudas para calcular vencimientos.")

# -------------------------------------------------------------------------
# TAB 4: MODIFICAR / LIQUIDAR CUENTA (CON PASE DIRECTO A CAJA Y CACHÉ)
# -------------------------------------------------------------------------
with tab_liquidacion:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_deudas.empty:
        opciones_deudas = {
            f"ID #{r['id']} | [{r.get('estado')}] {r.get('cliente', '')} ({r.get('concepto', '')}) - {formato_gs(r.get('monto_deuda', 0))}": r['id']
            for _, r in df_deudas.iterrows()
        }
        sel_deuda_txt = st.selectbox("Seleccione registro para gestionar:", list(opciones_deudas.keys()))
        sel_deuda_id = opciones_deudas[sel_deuda_txt]
        fila_d = df_deudas[df_deudas["id"] == sel_deuda_id].iloc[0]
        
        monto_actual = int(fila_d.get("monto_deuda", 0))
        es_por_cobrar = "Cobrar" in str(fila_d.get("tipo", ""))

        # -----------------------------------------------------------------
        # SUBSECCIÓN A: COBRO / LIQUIDACIÓN RÁPIDA (CON PASE DIRECTO A CAJA)
        # -----------------------------------------------------------------
        st.markdown("""
            <div style="background-color: #0b1329; border: 1px solid #1e293b; padding: 16px 20px; border-radius: 12px; margin-bottom: 15px;">
                <span style="color: #38bdf8; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">
                    ⚡ Cobro / Liquidación con Asiento Directo en Caja
                </span>
                <p style="color: #94a3b8; font-size: 0.82rem; margin: 4px 0 0 0;">
                    Al liquidar o registrar un abono, el movimiento impactará inmediatamente en el <strong>Libro Diario de Caja</strong>.
                </p>
            </div>
        """, unsafe_allow_html=True)

        col_liq1, col_liq2, col_liq3 = st.columns(3)
        with col_liq1:
            fecha_cobro_efectivo = st.date_input("Fecha de Cobro/Pago", value=datetime.now().date(), key="f_cobro_liq")
        with col_liq2:
            medio_cobro_efectivo = st.selectbox("Medio de Pago Utilizado", ["Efectivo", "Transferencia Bancaria", "Billetera Digital", "Tarjeta Débito/Crédito", "Otro"], key="medio_cobro_liq")
        with col_liq3:
            monto_a_liquidar = st.number_input("Monto Recibido / Abonado (Gs.)", min_value=1, max_value=max(1, monto_actual), value=monto_actual, step=5000, format="%d", key="monto_liq_val")

        saldo_restante_despues = monto_actual - monto_a_liquidar
        texto_accion = "LIQUIDACIÓN TOTAL" if saldo_restante_despues == 0 else f"ABONO PARCIAL (Quedará saldo de {formato_gs(saldo_restante_despues)})"
        st.caption(f"Acción a ejecutar: **{texto_accion}**")

        btn_liquidar_ahora = st.button("🚀 ASENTAR COBRO EN CAJA Y ACTUALIZAR CUENTA", use_container_width=True)

        if btn_liquidar_ahora:
            try:
                tipo_t = "Ingreso" if es_por_cobrar else "Egreso"
                categoria_trans = "Cobro de Deuda" if es_por_cobrar else "Proveedores / Costos"
                desc_t = f"Liquidación Saldo ID #{sel_deuda_id} | {fila_d.get('cliente', '')} | {fila_d.get('concepto', '')} [{medio_cobro_efectivo}]"
                
                # 1. Asiento en Caja
                supabase.table("transacciones").insert({
                    "fecha": str(fecha_cobro_efectivo),
                    "tipo": tipo_t,
                    "categoria": categoria_trans,
                    "monto": int(monto_a_liquidar),
                    "descripcion": desc_t
                }).execute()

                # 2. Actualización de Deuda
                if saldo_restante_despues == 0:
                    supabase.table("deudas").update({
                        "estado": "Cancelado / Pagado",
                        "forma_pago": medio_cobro_efectivo
                    }).eq("id", sel_deuda_id).execute()
                    st.toast(f"✅ ¡Cuenta #{sel_deuda_id} liquidada! Se ingresó {formato_gs(monto_a_liquidar)} a Caja.", icon="💰")
                else:
                    supabase.table("deudas").update({
                        "monto_deuda": int(saldo_restante_despues),
                        "estado": "Abono Parcial",
                        "forma_pago": medio_cobro_efectivo
                    }).eq("id", sel_deuda_id).execute()
                    st.toast(f"✅ Abono de {formato_gs(monto_a_liquidar)} asentado en Caja.", icon="💳")

                # 3. Invalidación de Caché
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error durante el proceso de liquidación: {e}")

        st.markdown("<hr style='border: 1px solid #1e293b; margin: 25px 0;'>", unsafe_allow_html=True)

        # -----------------------------------------------------------------
        # SUBSECCIÓN B: REVERTIR / ANULAR ÚLTIMA LIQUIDACIÓN
        # -----------------------------------------------------------------
        st.markdown("""
            <div style="background-color: #17120a; border: 1px solid #78350f; padding: 16px 20px; border-radius: 12px; margin-bottom: 15px;">
                <span style="color: #fbbf24; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">
                    ↩️ Revertir / Anular Última Liquidación o Abono
                </span>
                <p style="color: #cbd5e1; font-size: 0.82rem; margin: 4px 0 0 0;">
                    Busca el movimiento en <strong>Caja de Negocio</strong> vinculado a esta cuenta, elimina el asiento para no descuadrar la caja y restaura el saldo volviendo el estado a <strong>Pendiente</strong>.
                </p>
            </div>
        """, unsafe_allow_html=True)

        tx_asociada = None
        try:
            res_tx = supabase.table("transacciones").select("*").order("id", desc=True).execute()
            if res_tx.data:
                for t in res_tx.data:
                    desc_check = str(t.get("descripcion", ""))
                    if f"#{sel_deuda_id}" in desc_check and "Liquidación" in desc_check:
                        tx_asociada = t
                        break
        except Exception as e:
            st.warning(f"No se pudo consultar el historial de transacciones: {e}")

        if tx_asociada:
            monto_tx = int(tx_asociada.get("monto", 0))
            nuevo_saldo_restaurado = monto_tx if fila_d.get("estado") == "Cancelado / Pagado" else (monto_actual + monto_tx)
            col_rev1, col_rev2 = st.columns(2)
            with col_rev1:
                st.caption(f"**Asiento detectado:** ID #{tx_asociada.get('id')} ({tx_asociada.get('fecha')})")
                st.caption(f"**Monto a revertir:** {formato_gs(monto_tx)} ({tx_asociada.get('tipo')})")
            with col_rev2:
                st.caption(f"**Detalle:** {tx_asociada.get('descripcion', '')}")
                st.caption(f"**Saldo resultante:** {formato_gs(nuevo_saldo_restaurado)} (Pendiente)")

            if st.button("⚠️ CONFIRMAR Y ANULAR ÚLTIMA LIQUIDACIÓN", use_container_width=True):
                try:
                    supabase.table("transacciones").delete().eq("id", tx_asociada["id"]).execute()
                    supabase.table("deudas").update({
                        "monto_deuda": int(nuevo_saldo_restaurado),
                        "estado": "Pendiente"
                    }).eq("id", sel_deuda_id).execute()

                    st.cache_data.clear()
                    st.toast(f"Liquidación anulada. Saldo restaurado a {formato_gs(nuevo_saldo_restaurado)}.", icon="↩️")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al revertir la liquidación: {e}")
        else:
            st.info(f"ℹ️ No se detectó asiento con '#{sel_deuda_id}' y 'Liquidación' en Caja para anular.")

        st.markdown("<hr style='border: 1px solid #1e293b; margin: 25px 0;'>", unsafe_allow_html=True)

        # -----------------------------------------------------------------
        # SUBSECCIÓN C: EDICIÓN MANUAL / ELIMINACIÓN
        # -----------------------------------------------------------------
        st.markdown("#### ✏️ Modificación Manual de Datos / Eliminar")
        with st.form("form_editar_deuda_manual"):
            ed1, ed2 = st.columns(2)
            with ed1:
                ed_cliente = st.text_input("Cliente / Contacto", value=str(fila_d.get("cliente", "")))
                ed_concepto = st.text_input("Concepto", value=str(fila_d.get("concepto", "")))
                ed_monto = st.number_input("Saldo / Monto Actual (Gs.)", value=int(fila_d.get("monto_deuda", 0)), step=10000, format="%d")
            with ed2:
                estados_d = ["Pendiente", "Abono Parcial", "Cancelado / Pagado"]
                idx_est = estados_d.index(fila_d["estado"]) if fila_d.get("estado") in estados_d else 0
                ed_estado_d = st.selectbox("Estado", estados_d, index=idx_est)
                ed_forma = st.selectbox("Forma de Pago", ["Efectivo", "Transferencia Bancaria", "Billetera Digital", "Cheque / Pagaré", "Otro"])
                
                val_venc = fila_d.get("fecha_vencimiento")
                try:
                    fecha_def_venc = pd.to_datetime(val_venc).date() if pd.notna(val_venc) and str(val_venc).strip() != "" else datetime.now().date()
                except Exception:
                    fecha_def_venc = datetime.now().date()

                ed_venc = st.date_input("Fecha Vencimiento", value=fecha_def_venc)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            b_act, b_elim = st.columns(2)
            with b_act:
                btn_act = st.form_submit_button("🔄 GUARDAR DATOS (SIN PASAR A CAJA)", use_container_width=True)
            with b_elim:
                btn_elim = st.form_submit_button("🗑️ ELIMINAR CUENTA", use_container_width=True)

            if btn_act:
                try:
                    supabase.table("deudas").update({
                        "cliente": ed_cliente.strip(),
                        "concepto": ed_concepto.strip(),
                        "monto_deuda": int(ed_monto),
                        "estado": ed_estado_d,
                        "forma_pago": ed_forma,
                        "fecha_vencimiento": str(ed_venc)
                    }).eq("id", sel_deuda_id).execute()
                    
                    st.cache_data.clear()
                    st.success("Cuenta actualizada exitosamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar: {e}")

            if btn_elim:
                try:
                    supabase.table("deudas").delete().eq("id", sel_deuda_id).execute()
                    st.cache_data.clear()
                    st.success("Cuenta eliminada de la base de datos.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")
    else:
        st.info("Sin cuentas registradas para modificar o liquidar.")