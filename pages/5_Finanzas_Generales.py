import streamlit as st
import pandas as pd
from datetime import datetime
import io
from supabase import create_client, Client

st.set_page_config(
    page_title="Finanzas Generales | AGL STORE",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# SISTEMA DE ESTILOS VISUALES
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
# VALIDACIÓN DE SEGURIDAD Y CONEXIÓN A SUPABASE
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

# Cargas consolidadas desde Supabase
def cargar_datos():
    data = {}
    try:
        t_res = supabase.table("transacciones").select("*").execute()
        data["transacciones"] = pd.DataFrame(t_res.data) if t_res.data else pd.DataFrame()
    except Exception:
        data["transacciones"] = pd.DataFrame()

    try:
        p_res = supabase.table("pedidos_inventario").select("*").execute()
        data["pedidos"] = pd.DataFrame(p_res.data) if p_res.data else pd.DataFrame()
    except Exception:
        data["pedidos"] = pd.DataFrame()

    try:
        d_res = supabase.table("deudas").select("*").execute()
        data["deudas"] = pd.DataFrame(d_res.data) if d_res.data else pd.DataFrame()
    except Exception:
        data["deudas"] = pd.DataFrame()

    try:
        g_res = supabase.table("gastos_personales").select("*").execute()
        data["gastos_personales"] = pd.DataFrame(g_res.data) if g_res.data else pd.DataFrame()
    except Exception:
        data["gastos_personales"] = pd.DataFrame()

    return data

tablas = cargar_datos()
df_trans = tablas["transacciones"]
df_pedidos = tablas["pedidos"]
df_deudas = tablas["deudas"]
df_gastos_p = tablas["gastos_personales"]

# =========================================================================
# BANNER PRINCIPAL Y KPIs SUPERIORES
# =========================================================================
st.markdown("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); padding: 22px 26px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);">
        <span style="background: rgba(37, 99, 245, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.35); padding: 3px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
            Consolidador Financiero & Balance General
        </span>
        <h1 style="color: #ffffff; font-size: 1.7rem; font-weight: 800; margin: 8px 0 4px 0; letter-spacing: -0.02em;">
            📈 Finanzas Generales y Balance Ejecutivo
        </h1>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            Auditoría cruzada en tiempo real: flujo de caja, margen comercial de prendas, capital pendiente de cobro y separación patrimonial.
        </p>
    </div>
""", unsafe_allow_html=True)

# Cálculos de Caja
ingresos_caja = 0
egresos_caja = 0
saldo_caja = 0

if not df_trans.empty and "monto" in df_trans.columns:
    df_trans["monto_num"] = pd.to_numeric(df_trans["monto"], errors="coerce").fillna(0)
    ingresos_caja = int(df_trans[df_trans["tipo"] == "Ingreso"]["monto_num"].sum())
    egresos_caja = int(df_trans[df_trans["tipo"] == "Egreso"]["monto_num"].sum())
    saldo_caja = ingresos_caja - egresos_caja

# Cálculos de Pedidos y Ventas
facturacion_pedidos = 0
costo_total_mercaderia = 0
unidades_totales_pedidas = 0

if not df_pedidos.empty:
    df_ped_calc = df_pedidos.copy()
    c_n = pd.to_numeric(df_ped_calc.get("cantidad", 0), errors="coerce").fillna(0)
    p_n = pd.to_numeric(df_ped_calc.get("precio_venta", 0), errors="coerce").fillna(0)
    cos_n = pd.to_numeric(df_ped_calc.get("costo", 0), errors="coerce").fillna(0)
    
    unidades_totales_pedidas = int(c_n.sum())
    facturacion_pedidos = int((c_n * p_n).sum())
    costo_total_mercaderia = int((c_n * cos_n).sum())

ganancia_bruta_pedidos = facturacion_pedidos - costo_total_mercaderia
margen_bruto_pct = round((ganancia_bruta_pedidos / facturacion_pedidos * 100), 1) if facturacion_pedidos > 0 else 0

# Cálculos de Deudas (Capital en la Calle)
capital_en_calle = 0
if not df_deudas.empty and "monto_deuda" in df_deudas.columns:
    df_d_pend = df_deudas[df_deudas.get("estado", "").str.contains("Pendiente|Parcial", case=False, na=False)].copy()
    por_cobrar = df_d_pend[~df_d_pend.get("tipo", "").str.contains("Pagar|Proveedor", case=False, na=False)]
    capital_en_calle = int(pd.to_numeric(por_cobrar["monto_deuda"], errors="coerce").fillna(0).sum())

# Cálculo Gastos Personales
total_gastos_personales = 0
if not df_gastos_p.empty and "monto" in df_gastos_p.columns:
    total_gastos_personales = int(pd.to_numeric(df_gastos_p["monto"], errors="coerce").fillna(0).sum())

# FILA DE MÉTRICAS KPI
col_k1, col_k2, col_k3, col_k4 = st.columns(4)

with col_k1:
    color_caja = "#10b981" if saldo_caja >= 0 else "#ef4444"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">💵 Disponible en Caja</div>
            <div class="kpi-val" style="color: {color_caja};">{formato_gs(saldo_caja)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Saldo neto operativo</span>
        </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🛍️ Facturación Pedidos</div>
            <div class="kpi-val" style="color: #38bdf8;">{formato_gs(facturacion_pedidos)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">{unidades_totales_pedidas} prendas comercializadas</span>
        </div>
    """, unsafe_allow_html=True)

with col_k3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">✨ Ganancia Bruta Retail</div>
            <div class="kpi-val" style="color: #818cf8;">{formato_gs(ganancia_bruta_pedidos)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Margen sobre ventas: <strong>{margen_bruto_pct}%</strong></span>
        </div>
    """, unsafe_allow_html=True)

with col_k4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">⏳ Capital en la Calle</div>
            <div class="kpi-val" style="color: #f59e0b;">{formato_gs(capital_en_calle)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Créditos pendientes de cobro</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# =========================================================================
# NAVEGACIÓN MODERNA POR PESTAÑAS (TABS)
# =========================================================================
tab_flujo, tab_productos, tab_patrimonio, tab_exportar = st.tabs([
    "📊 Balances y Flujo de Fondos",
    "📦 Rentabilidad por Producto",
    "👤 Separación Personal vs. Negocio",
    "📑 Descargar Balance General (Excel / PDF)"
])

# -------------------------------------------------------------------------
# TAB 1: FLUJO DE EFECTIVO
# -------------------------------------------------------------------------
with tab_flujo:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    col_t1, col_t2 = st.columns([1.5, 1.5])
    
    with col_t1:
        st.markdown("### 🏦 Resumen de Flujo de Efectivo")
        st.write(f"• **Ingresos Asentados en Caja:** `{formato_gs(ingresos_caja)}`")
        st.write(f"• **Egresos Operativos / Fletes:** `{formato_gs(egresos_caja)}`")
        st.write(f"• **Saldo Neto Operativo:** `{formato_gs(saldo_caja)}`")
        st.write(f"• **Pendientes por Cobrar (Deudas):** `{formato_gs(capital_en_calle)}`")
        
        capital_proyectado = saldo_caja + capital_en_calle
        st.markdown(f"""
            <div style="background-color: #0b1329; border: 1px solid #1e293b; padding: 16px; border-radius: 12px; margin-top: 15px;">
                <span style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Patrimonio Líquido Proyectado</span>
                <div style="font-size: 1.4rem; font-weight: 800; color: #38bdf8; margin-top: 4px;">
                    {formato_gs(capital_proyectado)}
                </div>
                <span style="font-size: 0.78rem; color: #64748b;">(Caja de Negocio + Capital en la Calle por Cobrar)</span>
            </div>
        """, unsafe_allow_html=True)

    with col_t2:
        st.markdown("### 📈 Balance Ingresos vs. Egresos")
        df_chart_caja = pd.DataFrame({
            "Concepto": ["Ingresos Caja", "Egresos Caja", "Ganancia Bruta Ventas"],
            "Monto (Gs.)": [ingresos_caja, egresos_caja, ganancia_bruta_pedidos]
        }).set_index("Concepto")
        st.bar_chart(df_chart_caja, height=280)

# -------------------------------------------------------------------------
# TAB 2: RENTABILIDAD POR PRENDA (CON EXPORTACIÓN EXCEL / PDF)
# -------------------------------------------------------------------------
with tab_productos:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    if not df_pedidos.empty and "modelo_prenda" in df_pedidos.columns:
        df_p_analisis = df_pedidos.copy()
        df_p_analisis["cant_n"] = pd.to_numeric(df_p_analisis.get("cantidad", 0), errors="coerce").fillna(0)
        df_p_analisis["precio_n"] = pd.to_numeric(df_p_analisis.get("precio_venta", 0), errors="coerce").fillna(0)
        df_p_analisis["costo_n"] = pd.to_numeric(df_p_analisis.get("costo", 0), errors="coerce").fillna(0)
        df_p_analisis["subtotal_venta"] = df_p_analisis["cant_n"] * df_p_analisis["precio_n"]
        df_p_analisis["ganancia_neta"] = df_p_analisis["subtotal_venta"] - (df_p_analisis["cant_n"] * df_p_analisis["costo_n"])

        ranking_prendas = df_p_analisis.groupby("modelo_prenda").agg({
            "cant_n": "sum",
            "subtotal_venta": "sum",
            "ganancia_neta": "sum"
        }).reset_index().sort_values(by="cant_n", ascending=False)

        ranking_prendas.columns = ["MODELO DE PRENDA", "UNIDADES VENDIDAS", "FACTURACIÓN (GS.)", "GANANCIA ESTIMADA (GS.)"]
        
        # Preparación de la tabla visual con formato en Gs.
        tabla_vis = ranking_prendas.copy()
        tabla_vis["FACTURACIÓN (GS.)"] = tabla_vis["FACTURACIÓN (GS.)"].apply(formato_gs)
        tabla_vis["GANANCIA ESTIMADA (GS.)"] = tabla_vis["GANANCIA ESTIMADA (GS.)"].apply(formato_gs)

        # Encabezado y botones de exportación
        col_tit_prod, col_btn_p_xl, col_btn_p_pdf = st.columns([2, 1, 1])
        with col_tit_prod:
            st.markdown("### 🏷️ Rendimiento y Demanda por Prenda")
            st.caption("Consolidado de unidades despachadas, facturación y margen neto por artículo.")

        # 1. Exportación Excel (.xlsx)
        buffer_excel_prendas = io.BytesIO()
        with pd.ExcelWriter(buffer_excel_prendas, engine='openpyxl') as writer:
            ranking_prendas.to_excel(writer, index=False, sheet_name='Rentabilidad_Prendas')
        excel_prendas_data = buffer_excel_prendas.getvalue()

        with col_btn_p_xl:
            st.download_button(
                label="📗 Descargar Excel (.xlsx)",
                data=excel_prendas_data,
                file_name=f"Rentabilidad_Prendas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # 2. Exportación PDF Imprimible (Plantilla AGL STORE)
        with col_btn_p_pdf:
            fecha_hoy_corte = datetime.now().strftime('%d/%m/%Y')
            total_unidades = int(ranking_prendas["UNIDADES VENDIDAS"].sum())
            total_fact = int(ranking_prendas["FACTURACIÓN (GS.)"].sum())
            total_utilidad = int(ranking_prendas["GANANCIA ESTIMADA (GS.)"].sum())

            filas_prendas_html = ""
            for _, fila in ranking_prendas.iterrows():
                filas_prendas_html += f"""
                <tr>
                    <td style='color: #000000; font-weight: 600;'>{fila['MODELO DE PRENDA']}</td>
                    <td style='text-align: center; color: #000000;'>{fila['UNIDADES VENDIDAS']}</td>
                    <td style='text-align: right; color: #000000;'>{formato_gs(fila['FACTURACIÓN (GS.)'])}</td>
                    <td style='text-align: right; font-weight: bold; color: #16a34a;'>{formato_gs(fila['GANANCIA ESTIMADA (GS.)'])}</td>
                </tr>
                """

            html_reporte_prendas = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>AGL STORE - Rentabilidad por Prenda</title>
                <style>
                    @page {{ size: auto; margin: 0; }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                        margin: 0;
                        padding-top: 1cm; padding-right: 1cm; padding-bottom: 1cm; padding-left: 2cm;
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
                    th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }}
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
                        <div class="card-label">Prendas Comercializadas</div>
                        <div class="card-val">{total_unidades} uds.</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Facturación Bruta</div>
                        <div class="card-val">{formato_gs(total_fact)}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Utilidad Neta Estimada</div>
                        <div class="card-val">{formato_gs(total_utilidad)}</div>
                    </div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Modelo de Prenda</th>
                            <th style="width: 100px; text-align: center;">Unidades Vendidas</th>
                            <th style="width: 130px; text-align: right;">Facturación Total</th>
                            <th style="width: 130px; text-align: right;">Ganancia Bruta</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_prendas_html}
                    </tbody>
                </table>
            </body>
            </html>
            """

            st.download_button(
                label="📄 Imprimir / PDF",
                data=html_reporte_prendas,
                file_name=f"Rentabilidad_Prendas_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )

        st.dataframe(tabla_vis, use_container_width=True)
    else:
        st.info("Sin registros de prendas para calcular rotación.")