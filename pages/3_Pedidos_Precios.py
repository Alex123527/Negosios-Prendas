import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
from supabase import create_client, Client

st.set_page_config(
    page_title="Pedidos y Precios | AGL STORE",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# SISTEMA DE ESTILOS PREMIUM
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
    st.warning("⚠️ Acceso restringido. Por favor autentíquese en el portal principal.")
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

# Cargar pedidos con Caché de 60 segundos
@st.cache_data(ttl=60)
def cargar_pedidos():
    try:
        res = supabase.table("pedidos_inventario").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        return pd.DataFrame()

df_pedidos_raw = cargar_pedidos()

# =========================================================================
# MOTOR DE CÁLCULOS FINANCIEROS Y COSTO PROMEDIO PONDERADO (CPP)
# =========================================================================
def procesar_finanzas_pedidos(df_in: pd.DataFrame):
    if df_in.empty:
        return pd.DataFrame(), {}, {}
    
    df = df_in.copy()
    df["cantidad_n"] = pd.to_numeric(df.get("cantidad", 0), errors="coerce").fillna(0)
    df["costo_n"] = pd.to_numeric(df.get("costo", 0), errors="coerce").fillna(0)
    df["precio_n"] = pd.to_numeric(df.get("precio_venta", 0), errors="coerce").fillna(0)

    # 1. Costo Promedio Ponderado (CPP) por modelo de prenda
    cpp_dict = {}
    grupos = df.groupby("modelo_prenda")
    for modelo, g in grupos:
        total_cant = g["cantidad_n"].sum()
        if total_cant > 0:
            cpp_val = (g["cantidad_n"] * g["costo_n"]).sum() / total_cant
        else:
            cpp_val = g["costo_n"].mean()
        cpp_dict[modelo] = round(cpp_val, 2)
    
    df["costo_cpp"] = df["modelo_prenda"].map(cpp_dict).fillna(df["costo_n"])

    # 2. Facturación, CMV y Ganancia Bruta
    df["facturacion_bruta"] = df["cantidad_n"] * df["precio_n"]
    df["cmv_total"] = df["cantidad_n"] * df["costo_cpp"]
    df["ganancia_bruta"] = df["facturacion_bruta"] - df["cmv_total"]

    # 3. Recargo sobre Costo (Markup) y Margen sobre Venta
    df["markup_pct"] = np.where(
        df["costo_cpp"] > 0,
        ((df["precio_n"] - df["costo_cpp"]) / df["costo_cpp"]) * 100,
        0.0
    ).round(1)

    df["margen_pct"] = np.where(
        df["facturacion_bruta"] > 0,
        (df["ganancia_bruta"] / df["facturacion_bruta"]) * 100,
        0.0
    ).round(1)

    # 4. Extracción de Gastos Operativos (Fletes asumidos por el negocio en 'canal')
    def extraer_gasto_flete(canal_str):
        if pd.isna(canal_str):
            return 0
        txt = str(canal_str)
        if "Negocio (Envío Gratis" in txt and "Flete:" in txt:
            try:
                parte = txt.split("Flete:")[1].split("|")[0].replace("Gs.", "").replace(".", "").strip()
                return int(parte)
            except Exception:
                return 0
        return 0

    df["gastos_operativos"] = df["canal"].apply(extraer_gasto_flete)
    df["ganancia_operativa"] = df["ganancia_bruta"] - df["gastos_operativos"]

    # Resumen ejecutivo
    kpis = {
        "total_unidades": int(df["cantidad_n"].sum()),
        "facturacion_total": int(df["facturacion_bruta"].sum()),
        "cmv_total": int(df["cmv_total"].sum()),
        "ganancia_bruta_total": int(df["ganancia_bruta"].sum()),
        "gastos_operativos_total": int(df["gastos_operativos"].sum()),
        "ganancia_operativa_total": int(df["ganancia_operativa"].sum()),
        "margen_operativo_global": round(
            (df["ganancia_operativa"].sum() / df["facturacion_bruta"].sum() * 100), 1
        ) if df["facturacion_bruta"].sum() > 0 else 0.0,
        "markup_global": round(
            (df["ganancia_bruta"].sum() / df["cmv_total"].sum() * 100), 1
        ) if df["cmv_total"].sum() > 0 else 0.0
    }

    return df, kpis, cpp_dict

df_pedidos, kpi_finanzas, tabla_cpp = procesar_finanzas_pedidos(df_pedidos_raw)

# =========================================================================
# BANNER PRINCIPAL Y KPIs SUPERIORES
# =========================================================================
st.markdown("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); padding: 22px 26px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);">
        <span style="background: rgba(37, 99, 245, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.35); padding: 3px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
            Módulo Comercial & Finanzas de Catálogo
        </span>
        <h1 style="color: #ffffff; font-size: 1.7rem; font-weight: 800; margin: 8px 0 4px 0; letter-spacing: -0.02em;">
            🏷️ Pedidos, Inventario & Análisis de Rentabilidad
        </h1>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            Valoración por Costo Promedio Ponderado (CPP), discriminación de Markup vs. Margen, CMV y cálculo de utilidad operativa neta.
        </p>
    </div>
""", unsafe_allow_html=True)

# FILA DE MÉTRICAS KPI (4 tarjetas financieras)
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🛍️ Facturación Bruta</div>
            <div class="kpi-val" style="color: #38bdf8;">{formato_gs(kpi_finanzas.get("facturacion_total", 0))}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">{kpi_finanzas.get("total_unidades", 0)} prendas comercializadas</span>
        </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📦 CMV (Costo Mercadería)</div>
            <div class="kpi-val" style="color: #ef4444;">{formato_gs(kpi_finanzas.get("cmv_total", 0))}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Valuado con CPP</span>
        </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">✨ Ganancia Bruta</div>
            <div class="kpi-val" style="color: #818cf8;">{formato_gs(kpi_finanzas.get("ganancia_bruta_total", 0))}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Recargo (Markup): <strong>{kpi_finanzas.get("markup_global", 0)}%</strong></span>
        </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    color_op = "#10b981" if kpi_finanzas.get("ganancia_operativa_total", 0) >= 0 else "#ef4444"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">💎 Ganancia Operativa</div>
            <div class="kpi-val" style="color: {color_op};">{formato_gs(kpi_finanzas.get("ganancia_operativa_total", 0))}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Margen Neto: <strong>{kpi_finanzas.get("margen_operativo_global", 0)}%</strong></span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# =========================================================================
# NAVEGACIÓN POR PESTAÑAS (TABS)
# =========================================================================
tab_registro, tab_catalogo, tab_edicion, tab_calculadora = st.tabs([
    "🛍️ Registrar Nuevo Pedido",
    "📋 Catálogo & Reportes (Excel / PDF)",
    "⚙️ Modificar / Eliminar Pedidos",
    "💡 Análisis Financiero (CPP, Markup & Margen)"
])

# -------------------------------------------------------------------------
# TAB 1: REGISTRAR PEDIDO CON ANÁLISIS DE COSTO Y SEÑAS
# -------------------------------------------------------------------------
with tab_registro:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        fecha_ped = st.date_input("Fecha de Registro", value=datetime.now())
        cliente_ped = st.text_input("Cliente / Contacto", placeholder="Ej: María González (0981xxxxxx)")
        modelo_ped = st.text_input("Modelo de Prenda / Calzado", placeholder="Ej: Calza Lycra Sport, Jogger...")
        
        categorias_lista = ["Calzados", "Remeras", "Pantalones / Jeans", "Calzas / Leggins", "Buzos / Hoodies", "Camperas", "Shorts", "Accesorios", "Otros"]
        cat_ped = st.selectbox("Categoría", categorias_lista)
        
        if cat_ped == "Calzados":
            talles_disponibles = [str(i) for i in range(1, 51)]
            talle_ped = st.selectbox("Calce / Talle", talles_disponibles, index=39)
        else:
            talles_disponibles = ["XS", "S", "M", "L", "XL", "XXL", "Único", "Surtido"]
            talle_ped = st.selectbox("Talle", talles_disponibles, index=2)
            
        canal_ped = st.selectbox("Canal de Venta", ["WhatsApp", "Instagram", "Tienda Física", "Feria", "Otro"])

    with c2:
        cant_ped = st.number_input("Cantidad de Unidades", min_value=1, value=1, step=1)
        
        # Sugerir CPP si el modelo ya existe en la base
        cpp_existente = tabla_cpp.get(modelo_ped.strip(), 35000) if modelo_ped.strip() in tabla_cpp else 35000
        costo_unit = st.number_input(
            "Precio de Costo Unitario (Gs.)", 
            min_value=0, 
            value=int(cpp_existente), 
            step=5000, 
            format="%d",
            help="Costo de confección o compra del lote actual."
        )
        
        # Diferenciador: Markup vs Margen
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            recargo_markup = st.slider("Recargo sobre Costo (Markup %)", min_value=5, max_value=250, value=60, step=5)
            precio_sugerido = int(round(costo_unit * (1 + recargo_markup / 100)))
        with col_m2:
            margen_teorico = round((recargo_markup / (100 + recargo_markup)) * 100, 1) if recargo_markup > 0 else 0
            st.metric("Margen sobre Venta", f"{margen_teorico}%")

        precio_final = st.number_input("Precio de Venta Final (Gs.)", min_value=0, value=precio_sugerido, step=5000, format="%d")
        
        monto_total_pedido = int(cant_ped * precio_final)
        cmv_pedido_estimado = int(cant_ped * costo_unit)
        ganancia_bruta_est = monto_total_pedido - cmv_pedido_estimado
        
        st.caption(f"Venta: **{formato_gs(monto_total_pedido)}** | CMV: **{formato_gs(cmv_pedido_estimado)}** | Ganancia Bruta: **{formato_gs(ganancia_bruta_est)}**")
        estado_ped = st.selectbox("Estado del Pedido", ["Pendiente", "En Preparación", "En Camino / Enviado", "Entregado / Pagado", "Cancelado"])

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # SECCIÓN: FINANZAS Y CONDICIONES DE PAGO
    st.markdown("""
        <div style="background-color: #0b1329; border: 1px solid #1e293b; padding: 14px 18px; border-radius: 12px; margin-bottom: 15px;">
            <span style="color: #38bdf8; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">💰 Condiciones de Cobro (Seña & Saldo)</span>
        </div>
    """, unsafe_allow_html=True)
    
    cp1, cp2, cp3 = st.columns(3)
    with cp1:
        medio_pago_seña = st.selectbox("Medio de Cobro de Seña", ["Efectivo", "Transferencia SIPAP", "Billetera Digital", "Tarjeta Débito/Crédito", "Sin Seña"])
    with cp2:
        monto_sena = st.number_input("Seña Inicial Cobrada (Gs.)", min_value=0, max_value=monto_total_pedido, value=0, step=5000, format="%d")
        st.caption(f"Seña asentada: **{formato_gs(monto_sena)}**")
    with cp3:
        saldo_pendiente = max(0, monto_total_pedido - monto_sena)
        color_saldo = "#ef4444" if saldo_pendiente > 0 else "#10b981"
        st.markdown(f"""
            <div style="background-color: #090d16; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; margin-top: 4px;">
                <span style="font-size: 0.72rem; color: #94a3b8; font-weight: 700;">SALDO A COBRAR:</span>
                <div style="font-size: 1.25rem; font-weight: 800; color: {color_saldo};">{formato_gs(saldo_pendiente)}</div>
            </div>
        """, unsafe_allow_html=True)

    # SECCIÓN: LOGÍSTICA Y ENVÍOS (GASTOS OPERATIVOS)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background-color: #0b1329; border: 1px solid #1e293b; padding: 14px 18px; border-radius: 12px; margin-bottom: 15px;">
            <span style="color: #60a5fa; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">🚚 Logística, Despacho y Flete</span>
        </div>
    """, unsafe_allow_html=True)
    
    cl1, cl2, cl3 = st.columns(3)
    with cl1:
        empresa_envio = st.selectbox("Transportadora / Medio", ["Retiro en Local", "AEX", "NSA Encomiendas", "Rysa", "Delivery Local (Moto)", "Otra Encomienda"])
    with cl2:
        costo_envio = st.number_input("Costo Envío / Flete (Gs.)", min_value=0, value=0, step=5000, format="%d")
        st.caption(f"Flete: **{formato_gs(costo_envio)}**")
    with cl3:
        quien_paga_envio = st.selectbox("¿Quién asume el envío?", ["Cliente (Paga al recibir / Sumado)", "Negocio (Envío Gratis / Promoción)", "Sin Costo de Envío"])

    comprobante_ped = st.file_uploader("Comprobante de Seña / Guía de Despacho (Opcional)", type=["png", "jpg", "jpeg", "pdf"], key="comp_ped_nuevo")
    
    btn_crear_ped = st.button("💾 ASENTAR PEDIDO & VINCULAR CONTABILIDAD", use_container_width=True)
    
    if btn_crear_ped:
        if modelo_ped.strip() and cliente_ped.strip():
            nombre_doc = comprobante_ped.name if comprobante_ped is not None else ""
            
            info_canal = f"{canal_ped} | Seña: {formato_gs(monto_sena)} ({medio_pago_seña}) | Saldo: {formato_gs(saldo_pendiente)} | Envio: {empresa_envio} ({quien_paga_envio}) | Flete: {costo_envio}"
            if nombre_doc:
                info_canal += f" | Doc: {nombre_doc}"

            nuevo_pedido = {
                "fecha": str(fecha_ped),
                "cliente": cliente_ped.strip(),
                "modelo_prenda": modelo_ped.strip(),
                "categoria": cat_ped,
                "talle": talle_ped,
                "cantidad": int(cant_ped),
                "costo": int(costo_unit),
                "margen_ganancia": int(recargo_markup),
                "precio_venta": int(precio_final),
                "stock_inicial": int(cant_ped),
                "canal": info_canal,
                "estado": estado_ped
            }
            
            try:
                res_ped = supabase.table("pedidos_inventario").insert(nuevo_pedido).execute()
                pedido_creado_id = res_ped.data[0]["id"] if (res_ped.data and len(res_ped.data) > 0) else "N/A"
                
                # VINCULACIÓN 1: Ingreso a Caja si hubo seña
                if monto_sena > 0:
                    ingreso_caja = {
                        "fecha": str(fecha_ped),
                        "tipo": "Ingreso",
                        "categoria": "Ventas de Prendas",
                        "monto": int(monto_sena),
                        "descripcion": f"Seña Pedido #{pedido_creado_id} | {modelo_ped.strip()} ({cliente_ped.strip()}) [{medio_pago_seña}]"
                    }
                    supabase.table("transacciones").insert(ingreso_caja).execute()
                    st.toast(f"✅ Caja de Negocio: Seña de {formato_gs(monto_sena)} ingresada.")

                # VINCULACIÓN 2: Cuentas por Cobrar (Deudas) si hay saldo
                if saldo_pendiente > 0:
                    fecha_limite = (datetime.strptime(str(fecha_ped), "%Y-%m-%d").date() + timedelta(days=15))
                    cuenta_cobrar = {
                        "fecha": str(fecha_ped),
                        "tipo": "Por Cobrar (Cliente me debe)",
                        "cliente": cliente_ped.strip(),
                        "concepto": f"Saldo Pedido #{pedido_creado_id} | {modelo_ped.strip()} ({cant_ped} uds.)",
                        "monto_deuda": int(saldo_pendiente),
                        "forma_pago": medio_pago_seña if medio_pago_seña != "Sin Seña" else "Efectivo",
                        "fecha_vencimiento": str(fecha_limite),
                        "estado": "Pendiente"
                    }
                    supabase.table("deudas").insert(cuenta_cobrar).execute()
                    st.toast(f"💳 Cuentas por Cobrar: Saldo de {formato_gs(saldo_pendiente)} asentado.")

                # VINCULACIÓN 3: Flete asumido como Egreso en Caja
                if quien_paga_envio == "Negocio (Envío Gratis / Promoción)" and costo_envio > 0:
                    egreso_envio = {
                        "fecha": str(fecha_ped),
                        "tipo": "Egreso",
                        "categoria": "Packaging / Envíos",
                        "monto": int(costo_envio),
                        "descripcion": f"Flete {empresa_envio} Pedido #{pedido_creado_id}: {modelo_ped.strip()} ({cliente_ped.strip()})"
                    }
                    supabase.table("transacciones").insert(egreso_envio).execute()
                    st.toast(f"🚚 Flete absorbido de {formato_gs(costo_envio)} registrado en Caja.")

                cargar_pedidos.clear()
                st.success(f"¡Pedido #{pedido_creado_id} registrado exitosamente con sincronización financiera total!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al registrar pedido o sincronizar módulos: {e}")
        else:
            st.warning("Complete el nombre del cliente y el modelo de la prenda para continuar.")

# -------------------------------------------------------------------------
# TAB 2: CATÁLOGO Y REPORTES EJECUTIVOS (EXCEL / PDF)
# -------------------------------------------------------------------------
with tab_catalogo:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_pedidos.empty:
        col_tit_cat, col_btn_exp1, col_btn_exp2 = st.columns([2, 1, 1])

        with col_tit_cat:
            st.markdown("### 📋 Registro General de Pedidos & Rentabilidad")
            st.caption("Visualiza, audita y descarga en Excel o formato imprimible con análisis de márgenes.")

        # Tabla visual completa
        cols_mostrar = [
            "id", "fecha", "cliente", "modelo_prenda", "talle", 
            "cantidad_n", "costo_cpp", "precio_n", "facturacion_bruta", 
            "cmv_total", "ganancia_bruta", "margen_pct", "ganancia_operativa", "estado"
        ]
        
        df_grid = df_pedidos[cols_mostrar].copy()
        df_grid.columns = [
            "ID", "FECHA", "CLIENTE", "PRENDA", "TALLE",
            "CANT", "COSTO POND. (GS)", "PRECIO (GS)", "FACTURADO (GS)",
            "CMV (GS)", "GAN. BRUTA (GS)", "MARGEN %", "GAN. OPERATIVA (GS)", "ESTADO"
        ]

        df_grid["COSTO POND. (GS)"] = df_grid["COSTO POND. (GS)"].apply(formato_gs)
        df_grid["PRECIO (GS)"] = df_grid["PRECIO (GS)"].apply(formato_gs)
        df_grid["FACTURADO (GS)"] = df_grid["FACTURADO (GS)"].apply(formato_gs)
        df_grid["CMV (GS)"] = df_grid["CMV (GS)"].apply(formato_gs)
        df_grid["GAN. BRUTA (GS)"] = df_grid["GAN. BRUTA (GS)"].apply(formato_gs)
        df_grid["GAN. OPERATIVA (GS)"] = df_grid["GAN. OPERATIVA (GS)"].apply(formato_gs)
        df_grid["MARGEN %"] = df_grid["MARGEN %"].apply(lambda x: f"{x}%")

        # 1. Exportación Excel (.xlsx)
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_pedidos.to_excel(writer, index=False, sheet_name='Pedidos_Detallados')
        excel_data = buffer_excel.getvalue()

        with col_btn_exp1:
            st.download_button(
                label="📗 Descargar Excel (.xlsx)",
                data=excel_data,
                file_name=f"Pedidos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # 2. Exportación PDF Imprimible (AGL STORE)
        with col_btn_exp2:
            fecha_hoy_corte = datetime.now().strftime('%d/%m/%Y')
            df_impresion = df_pedidos.sort_values(by="id", ascending=True)

            filas_html = ""
            for _, f in df_impresion.iterrows():
                filas_html += f"""
                <tr>
                    <td style='text-align: center; color: #000000;'>{f.get('id', '')}</td>
                    <td style='color: #000000;'>{f.get('fecha', '')}</td>
                    <td style='color: #000000; font-weight: 600;'>{f.get('cliente', '')}</td>
                    <td style='color: #000000;'>{f.get('modelo_prenda', '')} ({f.get('cantidad_n', 0)} uds.)</td>
                    <td style='text-align: right; color: #000000;'>{formato_gs(f.get('cmv_total', 0))}</td>
                    <td style='text-align: right; color: #000000;'>{formato_gs(f.get('facturacion_bruta', 0))}</td>
                    <td style='text-align: right; font-weight: bold; color: #16a34a;'>{formato_gs(f.get('ganancia_operativa', 0))}</td>
                    <td style='text-align: center; color: #000000;'>{f.get('estado', '')}</td>
                </tr>
                """

            html_reporte = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>AGL STORE - Pedidos y Rentabilidad</title>
                <style>
                    @page {{ size: auto; margin: 0; }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                        margin: 0; padding-top: 1cm; padding-right: 1cm; padding-bottom: 1cm; padding-left: 2cm;
                        color: #000000; background: #ffffff;
                        -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
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
                        font-weight: 700; border: 1px solid #cbd5e1;
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
                        <div class="card-label">Facturación Bruta</div>
                        <div class="card-val">{formato_gs(kpi_finanzas.get('facturacion_total', 0))}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">CMV (Costo Mercadería)</div>
                        <div class="card-val">{formato_gs(kpi_finanzas.get('cmv_total', 0))}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Ganancia Bruta</div>
                        <div class="card-val">{formato_gs(kpi_finanzas.get('ganancia_bruta_total', 0))}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Ganancia Operativa Real</div>
                        <div class="card-val">{formato_gs(kpi_finanzas.get('ganancia_operativa_total', 0))}</div>
                    </div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th style="width: 35px; text-align: center;">ID</th>
                            <th style="width: 75px;">Fecha</th>
                            <th>Cliente</th>
                            <th>Prenda</th>
                            <th style="text-align: right;">CMV</th>
                            <th style="text-align: right;">Facturación</th>
                            <th style="text-align: right;">Ganancia Neta</th>
                            <th style="text-align: center; width: 90px;">Estado</th>
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
                data=html_reporte,
                file_name=f"Reporte_Pedidos_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        st.dataframe(df_grid, use_container_width=True)
    else:
        st.info("Sin pedidos cargados actualmente en la base de datos.")

# -------------------------------------------------------------------------
# TAB 3: MODIFICAR / ELIMINAR PEDIDOS
# -------------------------------------------------------------------------
with tab_edicion:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_pedidos.empty:
        st.markdown("### ⚙️ Modificar o Actualizar Pedido Completo")
        st.caption("Selecciona cualquier registro para corregir costos, estado o precios.")
        
        opciones_pedidos = {
            f"ID #{row['id']} | {row.get('cliente', '')} ({row.get('modelo_prenda', '')})": row['id']
            for _, row in df_pedidos.iterrows()
        }
        pedido_seleccionado_txt = st.selectbox("Seleccione el pedido:", list(opciones_pedidos.keys()))
        sel_ped_id = opciones_pedidos[pedido_seleccionado_txt]
        
        fila_ped = df_pedidos[df_pedidos["id"] == sel_ped_id].iloc[0]

        try:
            fecha_previa = datetime.strptime(str(fila_ped.get("fecha")), "%Y-%m-%d").date()
        except Exception:
            fecha_previa = datetime.now().date()

        with st.form("form_edit_pedido_completo"):
            e_c1, e_c2 = st.columns(2)
            
            with e_c1:
                ed_fecha = st.date_input("Fecha de Registro", value=fecha_previa)
                ed_cliente = st.text_input("Cliente / Contacto", value=str(fila_ped.get("cliente", "")))
                ed_modelo = st.text_input("Modelo de Prenda / Calzado", value=str(fila_ped.get("modelo_prenda", "")))
                
                idx_cat = categorias_lista.index(fila_ped.get("categoria")) if fila_ped.get("categoria") in categorias_lista else 0
                ed_cat = st.selectbox("Categoría", categorias_lista, index=idx_cat)
                
                ed_talle = st.text_input("Talle / Calce", value=str(fila_ped.get("talle", "M")))

            with e_c2:
                ed_cant = st.number_input("Cantidad de Unidades", min_value=1, value=int(fila_ped.get("cantidad_n", 1)), step=1)
                ed_costo = st.number_input("Costo Unitario (Gs.)", min_value=0, value=int(fila_ped.get("costo_n", 35000)), step=5000, format="%d")
                ed_precio = st.number_input("Precio Venta Final (Gs.)", min_value=0, value=int(fila_ped.get("precio_n", 0)), step=5000, format="%d")
                
                estados_opts = ["Pendiente", "En Preparación", "En Camino / Enviado", "Entregado / Pagado", "Cancelado"]
                idx_estado = estados_opts.index(fila_ped["estado"]) if fila_ped.get("estado") in estados_opts else 0
                ed_estado = st.selectbox("Estado del Pedido", estados_opts, index=idx_estado)

            c_bt1, c_bt2 = st.columns(2)
            if c_bt1.form_submit_button("🔄 ACTUALIZAR ESTADO Y DATOS", use_container_width=True):
                # Recalcular recargo porcentual
                markup_nuevo = int(round(((ed_precio - ed_costo) / ed_costo * 100))) if ed_costo > 0 else 0
                datos_actualizados = {
                    "fecha": str(ed_fecha),
                    "cliente": ed_cliente.strip(),
                    "modelo_prenda": ed_modelo.strip(),
                    "categoria": ed_cat,
                    "talle": str(ed_talle),
                    "cantidad": int(ed_cant),
                    "costo": int(ed_costo),
                    "margen_ganancia": markup_nuevo,
                    "precio_venta": int(ed_precio),
                    "estado": ed_estado
                }

                try:
                    supabase.table("pedidos_inventario").update(datos_actualizados).eq("id", sel_ped_id).execute()
                    cargar_pedidos.clear()
                    st.success("¡Pedido actualizado con éxito!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar en Supabase: {e}")

            if c_bt2.form_submit_button("🗑️ ELIMINAR PEDIDO", use_container_width=True):
                try:
                    supabase.table("pedidos_inventario").delete().eq("id", sel_ped_id).execute()
                    cargar_pedidos.clear()
                    st.success("Pedido eliminado de la base de datos.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")
    else:
        st.info("No hay pedidos registrados para modificar.")

# -------------------------------------------------------------------------
# TAB 4: ANÁLISIS FINANCIERO (CPP, MARKUP & MARGEN OPERATIVO)
# -------------------------------------------------------------------------
with tab_calculadora:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 Valuación de Existencias por Costo Promedio Ponderado (CPP)")
    st.caption("Consolidación contable de costos unitarios de entrada, margen de comercialización y absorción de fletes.")

    if not df_pedidos.empty:
        # Tabla resumen por modelo
        resumen_modelo = df_pedidos.groupby("modelo_prenda").agg({
            "cantidad_n": "sum",
            "costo_cpp": "first",
            "facturacion_bruta": "sum",
            "cmv_total": "sum",
            "ganancia_bruta": "sum",
            "gastos_operativos": "sum",
            "ganancia_operativa": "sum"
        }).reset_index()

        resumen_modelo["MARKUP REAL %"] = np.where(
            resumen_modelo["cmv_total"] > 0,
            ((resumen_modelo["facturacion_bruta"] - resumen_modelo["cmv_total"]) / resumen_modelo["cmv_total"]) * 100,
            0.0
        ).round(1)

        resumen_modelo["MARGEN NETO %"] = np.where(
            resumen_modelo["facturacion_bruta"] > 0,
            (resumen_modelo["ganancia_operativa"] / resumen_modelo["facturacion_bruta"]) * 100,
            0.0
        ).round(1)

        # Formato visual
        resumen_vis = resumen_modelo.copy()
        resumen_vis.columns = [
            "MODELO", "UNIDADES", "CPP UNITARIO", "FACTURACIÓN",
            "CMV TOTAL", "GAN. BRUTA", "FLETES/ENVÍOS", "GAN. OPERATIVA",
            "MARKUP %", "MARGEN %"
        ]

        resumen_vis["CPP UNITARIO"] = resumen_vis["CPP UNITARIO"].apply(formato_gs)
        resumen_vis["FACTURACIÓN"] = resumen_vis["FACTURACIÓN"].apply(formato_gs)
        resumen_vis["CMV TOTAL"] = resumen_vis["CMV TOTAL"].apply(formato_gs)
        resumen_vis["GAN. BRUTA"] = resumen_vis["GAN. BRUTA"].apply(formato_gs)
        resumen_vis["FLETES/ENVÍOS"] = resumen_vis["FLETES/ENVÍOS"].apply(formato_gs)
        resumen_vis["GAN. OPERATIVA"] = resumen_vis["GAN. OPERATIVA"].apply(formato_gs)
        resumen_vis["MARKUP %"] = resumen_vis["MARKUP %"].apply(lambda x: f"{x}%")
        resumen_vis["MARGEN %"] = resumen_vis["MARGEN %"].apply(lambda x: f"{x}%")

        st.dataframe(resumen_vis, use_container_width=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("#### ⚖️ Comparativa Contable: Facturación vs. CMV vs. Utilidad Neta")
        df_chart_finanzas = pd.DataFrame({
            "Concepto": ["Facturación Bruta", "CMV (Costo Stock)", "Ganancia Operativa"],
            "Monto": [
                kpi_finanzas.get("facturacion_total", 0),
                kpi_finanzas.get("cmv_total", 0),
                kpi_finanzas.get("ganancia_operativa_total", 0)
            ]
        }).set_index("Concepto")
        st.bar_chart(df_chart_finanzas, height=280)
    else:
        st.info("Sin datos para generar análisis financiero.")