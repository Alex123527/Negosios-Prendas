import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from supabase import create_client, Client

st.set_page_config(page_title="Finanzas Generales | PROYECTO X", page_icon="📈", layout="wide")

# CSS Estilo Futurista Coherente
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #071426; color: #E6EDF5; }
    section[data-testid="stSidebar"] { background-color: #0b1a2f !important; }
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(135deg, #4388FF 0%, #2f6de0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] { color: #21D4C4 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #9FB2C8 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input {
        background-color: #0d1b30 !important;
        color: #E6EDF5 !important;
        border: 1px solid #1E365D !important;
    }
    </style>
""", unsafe_allow_html=True)

# Validación de seguridad
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso restringido. Por favor autentíquese en app.py.")
    st.stop()

# Conexión Supabase
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

# Cargas de datos desde Supabase
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

st.title("📈 FINANZAS GENERALES Y BALANCE EJECUTIVO")
st.caption("CONSOLIDACIÓN FINANCIERA: CAJA DE NEGOCIO, CAPITAL, DEMANDA Y AUDITORÍA")

# CÁLCULOS PRINCIPALES DE CAJA DE NEGOCIO
ingresos_caja = 0
egresos_caja = 0
saldo_caja = 0

if not df_trans.empty and "monto" in df_trans.columns:
    df_trans["monto_num"] = pd.to_numeric(df_trans["monto"], errors="coerce").fillna(0)
    ingresos_caja = int(df_trans[df_trans["tipo"] == "Ingreso"]["monto_num"].sum())
    egresos_caja = int(df_trans[df_trans["tipo"] == "Egreso"]["monto_num"].sum())
    saldo_caja = ingresos_caja - egresos_caja

# CÁLCULOS DE PEDIDOS Y VENTAS TOTALES
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

# CÁLCULOS DE DEUDAS (CAPITAL EN LA CALLE)
capital_en_calle = 0
if not df_deudas.empty and "monto_deuda" in df_deudas.columns:
    df_d_pend = df_deudas[df_deudas.get("estado", "").str.contains("Pendiente|Parcial", case=False, na=False)].copy()
    por_cobrar = df_d_pend[~df_d_pend.get("tipo", "").str.contains("Pagar|Proveedor", case=False, na=False)]
    capital_en_calle = int(pd.to_numeric(por_cobrar["monto_deuda"], errors="coerce").fillna(0).sum())

# CÁLCULO GASTOS PERSONALES
total_gastos_personales = 0
if not df_gastos_p.empty and "monto" in df_gastos_p.columns:
    total_gastos_personales = int(pd.to_numeric(df_gastos_p["monto"], errors="coerce").fillna(0).sum())

# FILA 1: MÉTRICAS DE IMPACTO
m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 DISPONIBLE EN CAJA", formato_gs(saldo_caja))
m2.metric("🛍️ FACTURACIÓN PEDIDOS", formato_gs(facturacion_pedidos), f"{unidades_totales_pedidas} prendas")
m3.metric("✨ GANANCIA BRUTA RETAIL", formato_gs(ganancia_bruta_pedidos), f"{margen_bruto_pct}% margen")
m4.metric("⏳ CAPITAL EN LA CALLE", formato_gs(capital_en_calle), "Por cobrar")

st.markdown("---")

# PESTAÑAS ANALÍTICAS
tab1, tab2, tab3 = st.tabs(["📊 Balances y Flujo de Fondos", "📦 Rentabilidad por Producto", "👤 Separación Personal vs. Negocio"])

with tab1:
    col_t1, col_t2 = st.columns([1.5, 1.5])
    with col_t1:
        st.subheader("🏦 Resumen de Flujo de Efectivo")
        st.write(f"• **Ingresos Asentados en Caja:** `{formato_gs(ingresos_caja)}`")
        st.write(f"• **Egresos Operativos / Fletes:** `{formato_gs(egresos_caja)}`")
        st.write(f"• **Saldo Neto Operativo:** `{formato_gs(saldo_caja)}`")
        st.write(f"• **Pendientes por Cobrar (Deudas):** `{formato_gs(capital_en_calle)}`")
        
        capital_proyectado = saldo_caja + capital_en_calle
        st.info(f"💎 **Patrimonio Líquido Proyectado (Caja + Cobros):** {formato_gs(capital_proyectado)}")

    with col_t2:
        st.subheader("📈 Balance Ingresos vs. Egresos")
        df_chart_caja = pd.DataFrame({
            "Concepto": ["Ingresos Caja", "Egresos Caja", "Ganancia Bruta Ventas"],
            "Monto (Gs.)": [ingresos_caja, egresos_caja, ganancia_bruta_pedidos]
        }).set_index("Concepto")
        st.bar_chart(df_chart_caja)

with tab2:
    st.subheader("🏷️ Rendimiento y Demanda por Prenda")
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
        
        # Formatear para tabla
        tabla_vis = ranking_prendas.copy()
        tabla_vis["FACTURACIÓN (GS.)"] = tabla_vis["FACTURACIÓN (GS.)"].apply(formato_gs)
        tabla_vis["GANANCIA ESTIMADA (GS.)"] = tabla_vis["GANANCIA ESTIMADA (GS.)"].apply(formato_gs)
        
        st.dataframe(tabla_vis, use_container_width=True)
    else:
        st.info("Sin registros de prendas para calcular rotación.")

with tab3:
    st.subheader("⚖️ Auditoría: Gastos Personales vs. Dinero del Negocio")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.write(f"• **Ganancia Neta Generada por Ventas:** `{formato_gs(ganancia_bruta_pedidos)}`")
        st.write(f"• **Total Gastos Personales Registrados:** `{formato_gs(total_gastos_personales)}`")
        
        diferencia_patrimonial = ganancia_bruta_pedidos - total_gastos_personales
        if diferencia_patrimonial >= 0:
            st.success(f"✅ **Superávit Personal/Negocio:** {formato_gs(diferencia_patrimonial)} de excedente neto.")
        else:
            st.error(f"⚠️ **Alerta:** Los gastos personales superan las ganancias generadas por `{formato_gs(abs(diferencia_patrimonial))}`.")

    with col_p2:
        df_comparativa = pd.DataFrame({
            "Ámbito": ["Ganancia Negocio", "Gastos Personales"],
            "Monto": [ganancia_bruta_pedidos, total_gastos_personales]
        }).set_index("Ámbito")
        st.bar_chart(df_comparativa)

st.markdown("---")

# EXPORTACIÓN DE REPORTES GENERALES
st.subheader("📑 DESCARGAR BALANCE GENERAL")
c_exp1, c_exp2 = st.columns(2)

# 1. Excel con múltiples pestañas
buffer_balance_excel = io.BytesIO()
with pd.ExcelWriter(buffer_balance_excel, engine='openpyxl') as writer:
    if not df_trans.empty:
        df_trans.to_excel(writer, index=False, sheet_name='Caja_Transacciones')
    if not df_pedidos.empty:
        df_pedidos.to_excel(writer, index=False, sheet_name='Pedidos_Ventas')
    if not df_deudas.empty:
        df_deudas.to_excel(writer, index=False, sheet_name='Deudas_Cobros')
    if not df_gastos_p.empty:
        df_gastos_p.to_excel(writer, index=False, sheet_name='Gastos_Personales')
excel_balance_data = buffer_balance_excel.getvalue()

with c_exp1:
    st.download_button(
        label="📗 Descargar Balance Completo en Excel (.xlsx)",
        data=excel_balance_data,
        file_name=f"Balance_General_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# 2. Reporte Ejecutivo Imprimible / Guardar como PDF
html_ejecutivo = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reporte Ejecutivo de Finanzas - PROYECTO X</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 30px; color: #1a202c; }}
        h1 {{ color: #071426; border-bottom: 2px solid #4388FF; padding-bottom: 8px; }}
        h2 {{ color: #10213A; margin-top: 25px; }}
        .metric-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 15px; }}
        .metric-title {{ font-size: 13px; color: #64748b; font-weight: bold; text-transform: uppercase; }}
        .metric-value {{ font-size: 22px; color: #0f172a; font-weight: bold; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 9px; text-align: left; }}
        th {{ background-color: #0d1b30; color: white; }}
        tr:nth-child(even) {{ background-color: #f1f5f9; }}
        @media print {{ .no-print {{ display: none; }} }}
    </style>
</head>
<body onload="window.print()">
    <div class="no-print" style="margin-bottom: 20px; background: #e0f2fe; padding: 12px; border-radius: 6px; color: #0369a1;">
        ℹ️ <em>Se abrirá automáticamente el cuadro de impresión. Elige la opción <strong>"Guardar como PDF"</strong>.</em>
    </div>
    <h1>📊 INFORME EJECUTIVO DE FINANZAS Y RENTABILIDAD</h1>
    <p>Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    
    <div class="metric-card">
        <div class="metric-title">Disponible en Caja de Negocio</div>
        <div class="metric-value">{formato_gs(saldo_caja)}</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-title">Facturación Total Pedidos</div>
        <div class="metric-value">{formato_gs(facturacion_pedidos)} ({unidades_totales_pedidas} prendas comercializadas)</div>
    </div>

    <div class="metric-card">
        <div class="metric-title">Ganancia Bruta Estimada</div>
        <div class="metric-value">{formato_gs(ganancia_bruta_pedidos)} (Margen: {margen_bruto_pct}%)</div>
    </div>

    <div class="metric-card">
        <div class="metric-title">Capital Pendiente por Cobrar en la Calle</div>
        <div class="metric-value">{formato_gs(capital_en_calle)}</div>
    </div>

    <h2>Resumen de Separación Patrimonial</h2>
    <table>
        <thead>
            <tr><th>Concepto</th><th>Monto Acumulado (Gs.)</th></tr>
        </thead>
        <tbody>
            <tr><td>Ganancia Bruta Negocio</td><td><strong>{formato_gs(ganancia_bruta_pedidos)}</strong></td></tr>
            <tr><td>Total Gastos Personales Retirados</td><td><strong>{formato_gs(total_gastos_personales)}</strong></td></tr>
            <tr><td>Excedente / Margen de Seguridad</td><td><strong>{formato_gs(ganancia_bruta_pedidos - total_gastos_personales)}</strong></td></tr>
        </tbody>
    </table>
</body>
</html>
"""

with c_exp2:
    st.download_button(
        label="📕 Descargar Reporte Ejecutivo en PDF",
        data=html_ejecutivo.encode('utf-8'),
        file_name=f"Reporte_Ejecutivo_{datetime.now().strftime('%Y%m%d')}.html",
        mime="text/html",
        use_container_width=True
    )