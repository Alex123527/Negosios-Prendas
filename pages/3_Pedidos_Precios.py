import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from supabase import create_client, Client

st.set_page_config(
    page_title="Pedidos y Precios | PROYECTO X",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# SISTEMA DE ESTILOS PREMIUM (Canvas UI de Alto Nivel)
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

# Cargar pedidos
def cargar_pedidos():
    try:
        res = supabase.table("pedidos_inventario").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        return pd.DataFrame()

df_pedidos = cargar_pedidos()

# =========================================================================
# BANNER PRINCIPAL Y KPIs SUPERIORES
# =========================================================================
st.markdown("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); padding: 22px 26px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);">
        <span style="background: rgba(37, 99, 245, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.35); padding: 3px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
            Módulo Comercial & Gestión de Ventas
        </span>
        <h1 style="color: #ffffff; font-size: 1.7rem; font-weight: 800; margin: 8px 0 4px 0; letter-spacing: -0.02em;">
            🏷️ Pedidos, Catálogo y Fijación de Precios
        </h1>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            Control de señas, balance de saldos pendientes, fletes y vinculación automática con Caja y Deudas.
        </p>
    </div>
""", unsafe_allow_html=True)

# Cálculos de métricas
total_articulos = 0
valor_inventario = 0.0
pedidos_pendientes = 0

if not df_pedidos.empty:
    if "cantidad" in df_pedidos.columns:
        df_pedidos["cantidad_num"] = pd.to_numeric(df_pedidos["cantidad"], errors="coerce").fillna(0)
        total_articulos = int(df_pedidos["cantidad_num"].sum())
    
    if "precio_venta" in df_pedidos.columns and "cantidad_num" in df_pedidos.columns:
        df_pedidos["precio_num"] = pd.to_numeric(df_pedidos["precio_venta"], errors="coerce").fillna(0)
        valor_inventario = float((df_pedidos["precio_num"] * df_pedidos["cantidad_num"]).sum())
        
    if "estado" in df_pedidos.columns:
        pedidos_pendientes = int((df_pedidos["estado"].str.contains("Pendiente|Preparación", case=False, na=False)).sum())

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📦 Volumen Total Prendas</div>
            <div class="kpi-val" style="color: #38bdf8;">{total_articulos} <span style="font-size: 0.9rem; font-weight: 500; color: #94a3b8;">uds.</span></div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">💎 Valor Facturado / Cartera</div>
            <div class="kpi-val" style="color: #10b981;">{formato_gs(valor_inventario)}</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">⏳ Pedidos en Curso / Espera</div>
            <div class="kpi-val" style="color: #f59e0b;">{pedidos_pendientes} <span style="font-size: 0.9rem; font-weight: 500; color: #94a3b8;">pedidos</span></div>
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
    "💡 Rendimiento & Liquidez"
])

# -------------------------------------------------------------------------
# TAB 1: REGISTRAR PEDIDO CON SEÑAS Y SALDOS VINCULADOS
# -------------------------------------------------------------------------
with tab_registro:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        fecha_ped = st.date_input("Fecha de Registro", value=datetime.now())
        cliente_ped = st.text_input("Cliente / Contacto", placeholder="Ej: María González (0981xxxxxx)")
        modelo_ped = st.text_input("Modelo de Prenda / Calzado", placeholder="Ej: Championes Urbanos, Calza Lycra...")
        
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
        costo_unit = st.number_input("Costo Unitario Prenda (Gs.)", min_value=0, value=35000, step=5000, format="%d")
        margen_pct = st.slider("Margen Deseado (%)", min_value=5, max_value=250, value=60, step=5)
        
        precio_sugerido = int(round(costo_unit * (1 + margen_pct / 100)))
        precio_final = st.number_input("Precio de Venta Unitario (Gs.)", min_value=0, value=precio_sugerido, step=5000, format="%d")
        
        monto_total_pedido = int(cant_ped * precio_final)
        st.text_input("Total Pactado del Pedido (Gs.)", value=formato_gs(monto_total_pedido), disabled=True)
        
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

    # SECCIÓN: LOGÍSTICA Y ENVÍOS
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
            
            info_canal = f"{canal_ped} | Seña: {formato_gs(monto_sena)} ({medio_pago_seña}) | Saldo: {formato_gs(saldo_pendiente)} | Envio: {empresa_envio} ({quien_paga_envio})"
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
                "margen_ganancia": int(margen_pct),
                "precio_venta": int(precio_final),
                "stock_inicial": int(cant_ped),
                "canal": info_canal,
                "estado": estado_ped
            }
            
            try:
                res_ped = supabase.table("pedidos_inventario").insert(nuevo_pedido).execute()
                pedido_creado_id = res_ped.data[0]["id"] if (res_ped.data and len(res_ped.data) > 0) else "N/A"
                
                # VINCULACIÓN 1: Pase automático a Caja de Negocio por la seña recibida
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

                # VINCULACIÓN 2: Pase a Cuentas por Cobrar con nombres exactos de tabla deudas
                if saldo_pendiente > 0:
                    cuenta_cobrar = {
                        "fecha": str(fecha_ped),
                        "tipo": "Por Cobrar (Cliente me debe)",
                        "cliente": cliente_ped.strip(),
                        "concepto": f"Saldo Pedido #{pedido_creado_id} | {modelo_ped.strip()} ({cant_ped} uds.)",
                        "monto_deuda": int(saldo_pendiente),
                        "estado": "Pendiente"
                    }
                    supabase.table("deudas").insert(cuenta_cobrar).execute()
                    st.toast(f"💳 Cuentas por Cobrar: Saldo de {formato_gs(saldo_pendiente)} asentado.")

                # VINCULACIÓN 3: Flete absorbido por el negocio
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
            st.markdown("### 📋 Registro General de Pedidos")
            st.caption("Visualiza, filtra y descarga los registros oficiales en Excel o PDF listo para imprimir.")

        cols_base = ["id", "fecha", "cliente", "modelo_prenda", "categoria", "talle", "cantidad", "costo", "precio_venta", "canal", "estado"]
        cols_existentes = [c for c in cols_base if c in df_pedidos.columns]
        
        df_mostrar = df_pedidos[cols_existentes].copy()
        
        if "cantidad" in df_mostrar.columns and "precio_venta" in df_mostrar.columns:
            c_num = pd.to_numeric(df_mostrar["cantidad"], errors="coerce").fillna(0)
            p_num = pd.to_numeric(df_mostrar["precio_venta"], errors="coerce").fillna(0)
            cost_num = pd.to_numeric(df_mostrar.get("costo", 0), errors="coerce").fillna(0)
            
            df_mostrar["TOTAL PACTADO (GS.)"] = (c_num * p_num).apply(formato_gs)
            df_mostrar["costo"] = cost_num.apply(formato_gs)
            df_mostrar["precio_venta"] = p_num.apply(formato_gs)

        # Totales para el reporte PDF
        df_calc = df_pedidos.copy()
        df_calc["cant_n"] = pd.to_numeric(df_calc.get("cantidad", 0), errors="coerce").fillna(0)
        df_calc["prec_n"] = pd.to_numeric(df_calc.get("precio_venta", 0), errors="coerce").fillna(0)
        df_calc["subtotal"] = df_calc["cant_n"] * df_calc["prec_n"]

        total_pendiente = int(df_calc[df_calc["estado"].str.contains("Pendiente", case=False, na=False)]["subtotal"].sum())
        total_pagado = int(df_calc[df_calc["estado"].str.contains("Entregado / Pagado", case=False, na=False)]["subtotal"].sum())
        total_general = int(df_calc["subtotal"].sum())

        # 1. Exportación Excel (.xlsx)
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_mostrar.to_excel(writer, index=False, sheet_name='Pedidos')
        excel_data = buffer_excel.getvalue()

        with col_btn_exp1:
            st.download_button(
                label="📗 Descargar Excel (.xlsx)",
                data=excel_data,
                file_name=f"Pedidos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # 2. Exportación PDF Imprimible (Limpio y con Resumen Superior)
        filas_html = ""
        for _, f in df_mostrar.iterrows():
            filas_html += f"""
            <tr>
                <td>{f.get('id', '')}</td>
                <td>{f.get('fecha', '')}</td>
                <td><strong>{f.get('cliente', '')}</strong></td>
                <td>{f.get('modelo_prenda', '')} ({f.get('talle', '')})</td>
                <td style='text-align: center;'>{f.get('cantidad', '')}</td>
                <td style='text-align: right; font-weight: bold;'>{f.get('TOTAL PACTADO (GS.)', '')}</td>
                <td>{f.get('canal', '')}</td>
                <td>{f.get('estado', '')}</td>
            </tr>
            """
            
        html_reporte = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Reporte de Pedidos - PROYECTO X</title>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; margin: 30px; color: #0f172a; }}
                h2 {{ color: #0f172a; margin-bottom: 4px; font-size: 20px; }}
                p {{ color: #64748b; font-size: 12px; margin-top: 0; }}
                
                .resumen-container {{
                    display: flex;
                    gap: 15px;
                    margin: 15px 0 20px 0;
                }}
                .card-resumen {{
                    flex: 1;
                    padding: 12px 14px;
                    border-radius: 8px;
                    border: 1px solid #cbd5e1;
                    background-color: #f8fafc;
                }}
                .card-title {{
                    font-size: 10px;
                    text-transform: uppercase;
                    font-weight: 700;
                    letter-spacing: 0.05em;
                    color: #64748b;
                }}
                .card-val {{
                    font-size: 16px;
                    font-weight: 800;
                    margin-top: 4px;
                }}
                
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 10px; }}
                th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }}
                th {{ background-color: #0f172a; color: #ffffff; text-transform: uppercase; font-size: 9px; letter-spacing: 0.05em; }}
                tr:nth-child(even) {{ background-color: #f8fafc; }}
                @media print {{
                    body {{ margin: 0; }}
                }}
            </style>
        </head>
        <body onload="window.print()">
            <h2>📦 AUDITORÍA Y REPORTE DE PEDIDOS</h2>
            <p>Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            
            <div class="resumen-container">
                <div class="card-resumen">
                    <div class="card-title">⏳ Total Pendiente</div>
                    <div class="card-val" style="color: #d97706;">{formato_gs(total_pendiente)}</div>
                </div>
                <div class="card-resumen">
                    <div class="card-title">✅ Entregado / Pagado</div>
                    <div class="card-val" style="color: #16a34a;">{formato_gs(total_pagado)}</div>
                </div>
                <div class="card-resumen">
                    <div class="card-title">💎 Total Cartera General</div>
                    <div class="card-val" style="color: #2563eb;">{formato_gs(total_general)}</div>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>ID</th><th>Fecha</th><th>Cliente</th><th>Prenda / Talle</th><th>Cant.</th><th>Total</th><th>Detalle / Finanzas</th><th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </body>
        </html>
        """

        with col_btn_exp2:
            st.download_button(
                label="📕 Imprimir / PDF",
                data=html_reporte.encode('utf-8'),
                file_name=f"Reporte_Pedidos_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        st.dataframe(df_mostrar, use_container_width=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📊 Consolidado de Unidades por Modelo")
        if "modelo_prenda" in df_pedidos.columns and "cantidad_num" in df_pedidos.columns:
            agrupado_prod = df_pedidos.groupby("modelo_prenda")["cantidad_num"].sum().reset_index()
            agrupado_prod.columns = ["MODELO DE PRENDA", "CANTIDAD TOTAL PEDIDA (UDS)"]
            st.dataframe(agrupado_prod, use_container_width=True)
    else:
        st.info("Sin pedidos cargados actualmente en la base de datos.")

# -------------------------------------------------------------------------
# TAB 3: MODIFICAR / ELIMINAR PEDIDOS
# -------------------------------------------------------------------------
with tab_edicion:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_pedidos.empty:
        st.markdown("### ⚙️ Modificar o Actualizar Pedido Completo")
        st.caption("Selecciona cualquier registro para corregir datos, alterar logística o adjuntar comprobantes.")
        
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
                
                if ed_cat == "Calzados":
                    talles_ed = [str(i) for i in range(1, 51)]
                    idx_talle = talles_ed.index(str(fila_ped.get("talle"))) if str(fila_ped.get("talle")) in talles_ed else 39
                else:
                    talles_ed = ["XS", "S", "M", "L", "XL", "XXL", "Único", "Surtido"]
                    idx_talle = talles_ed.index(str(fila_ped.get("talle"))) if str(fila_ped.get("talle")) in talles_ed else 0
                ed_talle = st.selectbox("Talle / Calce", talles_ed, index=idx_talle)

            with e_c2:
                ed_cant = st.number_input("Cantidad de Unidades", min_value=1, value=int(fila_ped.get("cantidad", 1)), step=1)
                ed_costo = st.number_input("Costo Unitario (Gs.)", min_value=0, value=int(fila_ped.get("costo", 35000)), step=5000, format="%d")
                
                margen_prev = int(fila_ped.get("margen_ganancia", 60)) if fila_ped.get("margen_ganancia") else 60
                ed_margen = st.slider("Margen (%)", min_value=5, max_value=250, value=min(250, max(5, margen_prev)), step=5)
                
                ed_precio = st.number_input("Precio Venta Final (Gs.)", min_value=0, value=int(fila_ped.get("precio_venta", 0)), step=5000, format="%d")
                st.text_input("Total Recalculado (Gs.)", value=formato_gs(ed_cant * ed_precio), disabled=True)
                
                estados_opts = ["Pendiente", "En Preparación", "En Camino / Enviado", "Entregado / Pagado", "Cancelado"]
                idx_estado = estados_opts.index(fila_ped["estado"]) if fila_ped.get("estado") in estados_opts else 0
                ed_estado = st.selectbox("Estado del Pedido", estados_opts, index=idx_estado)

            canal_anterior = str(fila_ped.get("canal", ""))
            st.text_input("Detalles Financieros / Logísticos Actuales:", value=canal_anterior, disabled=True)

            c_bt1, c_bt2 = st.columns(2)
            if c_bt1.form_submit_button("🔄 ACTUALIZAR ESTADO Y DATOS", use_container_width=True):
                datos_actualizados = {
                    "fecha": str(ed_fecha),
                    "cliente": ed_cliente.strip(),
                    "modelo_prenda": ed_modelo.strip(),
                    "categoria": ed_cat,
                    "talle": str(ed_talle),
                    "cantidad": int(ed_cant),
                    "costo": int(ed_costo),
                    "margen_ganancia": int(ed_margen),
                    "precio_venta": int(ed_precio),
                    "estado": ed_estado
                }

                try:
                    supabase.table("pedidos_inventario").update(datos_actualizados).eq("id", sel_ped_id).execute()
                    st.success("¡Pedido actualizado con éxito!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar en Supabase: {e}")

            if c_bt2.form_submit_button("🗑️ ELIMINAR PEDIDO", use_container_width=True):
                try:
                    supabase.table("pedidos_inventario").delete().eq("id", sel_ped_id).execute()
                    st.success("Pedido eliminado de la base de datos.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")
    else:
        st.info("No hay pedidos registrados para modificar.")

# -------------------------------------------------------------------------
# TAB 4: RENDIMIENTO & PROYECCIÓN FINANCIERA
# -------------------------------------------------------------------------
with tab_calculadora:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    gasto_envio_negocio = costo_envio if quien_paga_envio == "Negocio (Envío Gratis / Promoción)" else 0
    ganancia_neta_estimada = (monto_total_pedido - (costo_unit * cant_ped)) - gasto_envio_negocio
    
    st.markdown(f"""
        <div style="background-color: #0b1329; border: 1px solid #1e293b; padding: 18px; border-radius: 12px; margin-bottom: 20px;">
            <span style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Proyección Unitaria del Pedido Actual</span>
            <div style="font-size: 1.3rem; font-weight: 800; color: #10b981; margin-top: 5px;">
                Ganancia Neta Estimada: {formato_gs(ganancia_neta_estimada)}
            </div>
            <p style="color: #64748b; font-size: 0.78rem; margin: 4px 0 0 0;">(Descontando costo de mercadería y flete asumido por la empresa)</p>
        </div>
    """, unsafe_allow_html=True)

    hoy = datetime.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    primer_dia_mes = hoy.replace(day=1)
    
    pedidos_dia = 0
    pedidos_semana = 0
    pedidos_mes = 0
    capital_semana_requerido = 0.0
    venta_semana_proyectada = 0.0
    
    if not df_pedidos.empty and "fecha" in df_pedidos.columns:
        df_temp = df_pedidos.copy()
        df_temp["fecha_dt"] = pd.to_datetime(df_temp["fecha"], errors="coerce").dt.date
        df_temp["cant_n"] = pd.to_numeric(df_temp.get("cantidad", 0), errors="coerce").fillna(0)
        df_temp["costo_n"] = pd.to_numeric(df_temp.get("costo", 0), errors="coerce").fillna(0)
        df_temp["precio_n"] = pd.to_numeric(df_temp.get("precio_venta", 0), errors="coerce").fillna(0)
        
        df_dia = df_temp[df_temp["fecha_dt"] == hoy]
        pedidos_dia = int(df_dia["cant_n"].sum())
        
        df_sem = df_temp[df_temp["fecha_dt"] >= hace_7_dias]
        pedidos_semana = int(df_sem["cant_n"].sum())
        capital_semana_requerido = float((df_sem["cant_n"] * df_sem["costo_n"]).sum())
        venta_semana_proyectada = float((df_sem["cant_n"] * df_sem["precio_n"]).sum())
        
        df_mes = df_temp[df_temp["fecha_dt"] >= primer_dia_mes]
        pedidos_mes = int(df_mes["cant_n"].sum())
    
    st.markdown("#### 📅 Volumen de Pedidos por Período")
    cd1, cd2, cd3 = st.columns(3)
    cd1.metric("HOY", f"{pedidos_dia} uds.")
    cd2.metric("ÚLTIMOS 7 DÍAS", f"{pedidos_semana} uds.")
    cd3.metric("MES EN CURSO", f"{pedidos_mes} uds.")
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 💼 Capital Operativo y Retorno Semanal")
    
    c_cap1, c_cap2, c_cap3 = st.columns(3)
    with c_cap1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Capital Requerido Semanal</div>
                <div class="kpi-val" style="color: #ef4444;">{formato_gs(capital_semana_requerido)}</div>
            </div>
        """, unsafe_allow_html=True)
    with c_cap2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Facturación Semanal Proyectada</div>
                <div class="kpi-val" style="color: #38bdf8;">{formato_gs(venta_semana_proyectada)}</div>
            </div>
        """, unsafe_allow_html=True)
    with c_cap3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Retorno Neto Proyectado</div>
                <div class="kpi-val" style="color: #10b981;">{formato_gs(venta_semana_proyectada - capital_semana_requerido)}</div>
            </div>
        """, unsafe_allow_html=True)