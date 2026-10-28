import streamlit as st
import pandas as pd
from datetime import datetime
import io
from supabase import create_client, Client

st.set_page_config(
    page_title="Gastos Personales | PROYECTO X",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# SISTEMA DE ESTILOS VISUALES (Futurist Premium / Canvas Dark UI)
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Fondo principal y textos */
    .stApp {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }
    
    /* Maximizar ancho útil */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 96% !important;
    }
    
    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #0b1329 !important;
        border-right: 1px solid #1e293b !important;
    }
    
    /* Botones de acción y descarga */
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
    
    /* Entradas de formulario */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input, .stTextArea textarea {
        background-color: #090d16 !important;
        color: #f1f5f9 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 1px #2563eb !important;
    }
    
    /* Pestañas (Tabs) estilo Nav */
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
    
    /* Tablas y DataFrames */
    [data-testid="stDataFrame"] {
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    /* Tarjetas personalizadas KPI */
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
    
    /* Barra de progreso de presupuesto */
    .budget-bar-bg {
        background-color: #090d16;
        border-radius: 9999px;
        height: 10px;
        width: 100%;
        margin-top: 8px;
        overflow: hidden;
        border: 1px solid #1e293b;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# VALIDACIÓN DE SESIÓN Y CONEXIÓN A SUPABASE
# =========================================================================
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso restringido. Inicie sesión en app.py.")
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

# Listado maestro de categorías
CATEGORIAS_GASTO = [
    "Alimentación y Supermercado",
    "Vivienda y Alquiler",
    "Servicios Básicos (Luz, Agua, Internet)",
    "Combustible y Movilidad",
    "Salud, Farmacia y Bienestar",
    "Educación, Libros y Capacitación",
    "Ocio, Salidas y Restaurantes",
    "Ropa y Calzado Personal",
    "Varios / Imprevistos"
]

METODOS_PAGO = [
    "Efectivo",
    "Transferencia Bancaria (SIPAP)",
    "Tarjeta de Débito",
    "Tarjeta de Crédito",
    "Billetera Digital"
]

# Carga de datos
def cargar_gastos():
    try:
        res = supabase.table("gastos_personales").select("*").order("fecha", desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df["monto_num"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0).astype(int)
            df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")
            df["periodo"] = df["fecha_dt"].dt.strftime("%Y-%m")
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

df_gastos = cargar_gastos()

# =========================================================================
# BANNER PRINCIPAL Y FILTROS INTELIGENTES
# =========================================================================
st.markdown("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); padding: 22px 26px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);">
        <span style="background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.35); padding: 3px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
            Módulo 01 • Finanzas Privadas
        </span>
        <h1 style="color: #ffffff; font-size: 1.7rem; font-weight: 800; margin: 8px 0 4px 0; letter-spacing: -0.02em;">
            👤 Control Integral de Gastos Personales
        </h1>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            Supervisión presupuestaria, métodos de desembolso y métricas de consumo para blindar el capital de giro.
        </p>
    </div>
""", unsafe_allow_html=True)

mes_actual = datetime.now().strftime("%Y-%m")

# Presupuesto mensual configurable en sesión
if "presupuesto_mensual" not in st.session_state:
    st.session_state["presupuesto_mensual"] = 3500000

# Filtros superiores
if not df_gastos.empty and "periodo" in df_gastos.columns:
    periodos_disponibles = sorted([p for p in df_gastos["periodo"].dropna().unique()], reverse=True)
    if mes_actual not in periodos_disponibles:
        periodos_disponibles.insert(0, mes_actual)
    
    col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 1])
    with col_f1:
        filtro_periodo = st.selectbox("📅 Período de Análisis:", ["Todos"] + periodos_disponibles)
    with col_f2:
        filtro_cat = st.selectbox("🏷️ Filtrar por Categoría:", ["Todas"] + CATEGORIAS_GASTO)
    with col_f3:
        st.session_state["presupuesto_mensual"] = st.number_input(
            "🎯 Límite Presupuesto (Gs.)",
            min_value=100000,
            value=int(st.session_state["presupuesto_mensual"]),
            step=250000,
            format="%d"
        )
    
    # Aplicar filtros
    df_filtrado = df_gastos.copy()
    if filtro_periodo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["periodo"] == filtro_periodo]
    if filtro_cat != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == filtro_cat]
else:
    df_filtrado = df_gastos.copy()
    filtro_periodo = "Todos"
    filtro_cat = "Todas"

# =========================================================================
# CÁLCULOS AVANZADOS DE KPIS Y MÉTRICAS
# =========================================================================
total_filtrado = int(df_filtrado["monto_num"].sum()) if not df_filtrado.empty else 0
cant_movimientos = len(df_filtrado)

# Promedio diario del período
dias_con_gasto = df_filtrado["fecha_dt"].dt.date.nunique() if not df_filtrado.empty else 1
promedio_diario = int(total_filtrado / max(dias_con_gasto, 1))

# Comparación con mes anterior
total_mes_anterior = 0
var_pct_str = "0.0%"
if not df_gastos.empty:
    meses_ordenados = sorted(df_gastos["periodo"].dropna().unique())
    if filtro_periodo in meses_ordenados:
        idx = meses_ordenados.index(filtro_periodo)
        if idx > 0:
            mes_ant = meses_ordenados[idx - 1]
            total_mes_anterior = int(df_gastos[df_gastos["periodo"] == mes_ant]["monto_num"].sum())
            if total_mes_anterior > 0:
                diff = ((total_filtrado - total_mes_anterior) / total_mes_anterior) * 100
                signo = "+" if diff > 0 else ""
                var_pct_str = f"{signo}{diff:.1f}% vs {mes_ant}"

# Porcentaje de presupuesto consumido
limite_pres = st.session_state["presupuesto_mensual"]
pct_presupuesto = min(int((total_filtrado / max(limite_pres, 1)) * 100), 100)
color_pres = "#10b981" if pct_presupuesto < 75 else ("#f59e0b" if pct_presupuesto < 95 else "#ef4444")

col_k1, col_k2, col_k3, col_k4 = st.columns(4)

with col_k1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">💸 Gasto del Período</div>
            <div class="kpi-val" style="color: #f87171;">{formato_gs(total_filtrado)}</div>
            <span style="font-size: 0.74rem; color: #94a3b8;">{cant_movimientos} movimientos | {var_pct_str}</span>
        </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📅 Promedio por Día de Uso</div>
            <div class="kpi-val" style="color: #38bdf8;">{formato_gs(promedio_diario)}</div>
            <span style="font-size: 0.74rem; color: #94a3b8;">En {dias_con_gasto} días activos detectados</span>
        </div>
    """, unsafe_allow_html=True)

with col_k3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🎯 Ejecución de Presupuesto</div>
            <div class="kpi-val" style="color: {color_pres};">{pct_presupuesto}%</div>
            <div class="budget-bar-bg">
                <div style="background-color: {color_pres}; width: {pct_presupuesto}%; height: 100%;"></div>
            </div>
            <span style="font-size: 0.72rem; color: #94a3b8; display: block; margin-top: 4px;">Tope: {formato_gs(limite_pres)}</span>
        </div>
    """, unsafe_allow_html=True)

with col_k4:
    restante = max(limite_pres - total_filtrado, 0)
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🛡️ Margen Disponible</div>
            <div class="kpi-val" style="color: #10b981;">{formato_gs(restante)}</div>
            <span style="font-size: 0.74rem; color: #94a3b8;">Capital personal remanente</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# =========================================================================
# NAVEGACIÓN MODERNA POR PESTAÑAS (TABS)
# =========================================================================
tab_nuevo, tab_historial, tab_analisis, tab_editar = st.tabs([
    "📝 Registrar Nuevo Gasto",
    "📋 Historial & Exportación (Excel / PDF)",
    "📊 Distribución & Visualizaciones",
    "⚙️ Modificar / Eliminar Asiento"
])

# -------------------------------------------------------------------------
# TAB 1: REGISTRAR NUEVO GASTO (Campos Extendidos)
# -------------------------------------------------------------------------
with tab_nuevo:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    with st.form("form_nuevo_gasto", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_g = st.date_input("Fecha de Operación", value=datetime.now())
            categoria_g = st.selectbox("Categoría de Gasto", CATEGORIAS_GASTO)
            forma_pago_g = st.selectbox("Método de Pago", METODOS_PAGO)
            comprobante_g = st.text_input("Nro. Factura / Comprobante (Opcional)", placeholder="Ej: Fact. 001-002-12345")

        with c2:
            monto_g = st.number_input("Monto en Guaraníes (Gs.)", min_value=0, value=50000, step=5000, format="%d")
            st.caption(f"Valor a asentar: **{formato_gs(monto_g)}**")
            descripcion_g = st.text_input("Concepto / Motivo", placeholder="Ej: Compra semanal carne y verduras")
            notas_g = st.text_area("Observaciones Adicionales", placeholder="Detalles de la compra, local, etc.", height=68)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        btn_guardar = st.form_submit_button("💾 ASENTAR GASTO PERSONAL", use_container_width=True)

        if btn_guardar:
            if monto_g > 0 and descripcion_g.strip():
                # Estructuración segura para persistencia sin alterar el esquema de Supabase
                detalles_extra = []
                if forma_pago_g:
                    detalles_extra.append(f"Pago: {forma_pago_g}")
                if comprobante_g.strip():
                    detalles_extra.append(f"Comp: {comprobante_g.strip()}")
                if notas_g.strip():
                    detalles_extra.append(f"Obs: {notas_g.strip()}")

                desc_final = descripcion_g.strip()
                if detalles_extra:
                    desc_final += f" [{' | '.join(detalles_extra)}]"

                nuevo_reg = {
                    "fecha": str(fecha_g),
                    "categoria": categoria_g,
                    "monto": int(monto_g),
                    "descripcion": desc_final
                }
                try:
                    supabase.table("gastos_personales").insert(nuevo_reg).execute()
                    st.success("¡Gasto registrado con éxito en la base de datos!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar en Supabase: {e}")
            else:
                st.warning("Ingrese un monto mayor a 0 y un concepto representativo.")

# -------------------------------------------------------------------------
# TAB 2: HISTORIAL Y REPORTES EXCEL / PDF
# -------------------------------------------------------------------------
with tab_historial:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_filtrado.empty:
        col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
        with col_t1:
            st.markdown(f"### 📋 Registros Filtrados ({len(df_filtrado)} movimientos)")
            st.caption(f"Período: **{filtro_periodo}** | Categoría: **{filtro_cat}**")

        cols_mostrar = ["id", "fecha", "categoria", "descripcion", "monto"]
        cols_existentes = [c for c in cols_mostrar if c in df_filtrado.columns]
        
        df_visual = df_filtrado[cols_existentes].copy()
        if "monto" in df_visual.columns:
            df_visual["MONTO (GS.)"] = df_visual["monto"].apply(formato_gs)

        # 1. Exportación Excel enriquecida
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df_visual.to_excel(writer, index=False, sheet_name='Gastos_Personales')
        excel_data = buf.getvalue()

        with col_t2:
            st.download_button(
                label="📗 Descargar Excel (.xlsx)",
                data=excel_data,
                file_name=f"Gastos_Personales_{filtro_periodo}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # 2. Exportación PDF Imprimible
        filas_html = ""
        for _, f in df_visual.iterrows():
            filas_html += f"""
            <tr>
                <td>{f.get('id', '')}</td>
                <td>{f.get('fecha', '')}</td>
                <td><strong>{f.get('categoria', '')}</strong></td>
                <td>{f.get('descripcion', '')}</td>
                <td style='text-align: right; font-weight: bold;'>{f.get('MONTO (GS.)', '')}</td>
            </tr>
            """
            
        html_reporte = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Reporte de Gastos Personales - PROYECTO X</title>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; margin: 30px; color: #0f172a; }}
                h2 {{ color: #0f172a; margin-bottom: 4px; font-size: 20px; }}
                p {{ color: #64748b; font-size: 12px; margin-top: 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 11px; }}
                th, td {{ border: 1px solid #cbd5e1; padding: 9px 12px; text-align: left; }}
                th {{ background-color: #0f172a; color: #ffffff; text-transform: uppercase; font-size: 10px; letter-spacing: 0.05em; }}
                tr:nth-child(even) {{ background-color: #f8fafc; }}
                @media print {{
                    .no-print {{ display: none !important; }}
                    body {{ margin: 0; }}
                }}
            </style>
        </head>
        <body onload="window.print()">
            <div class="no-print" style="margin-bottom: 20px; background: #e0f2fe; color: #0369a1; padding: 12px; border-radius: 8px; font-size: 12px;">
                ℹ️ <em>Se abrirá la ventana de impresión. Selecciona <strong>"Guardar como PDF"</strong> para archivarlo.</em>
            </div>
            <h2>👤 REPORTE EJECUTIVO DE GASTOS PERSONALES</h2>
            <p>Período: {filtro_periodo} | Categoría: {filtro_cat} | Total Auditado: {formato_gs(total_filtrado)} | Emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <table>
                <thead>
                    <tr>
                        <th>ID</th><th>Fecha</th><th>Categoría</th><th>Descripción & Detalles</th><th>Monto</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </body>
        </html>
        """

        with col_t3:
            st.download_button(
                label="📕 Imprimir / PDF",
                data=html_reporte.encode('utf-8'),
                file_name=f"Reporte_Gastos_{filtro_periodo}_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )

        st.dataframe(df_visual, use_container_width=True)
    else:
        st.info("No se encontraron registros de gastos personales para los filtros aplicados.")

# -------------------------------------------------------------------------
# TAB 3: DISTRIBUCIÓN Y REPORTES VISUALES
# -------------------------------------------------------------------------
with tab_analisis:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_filtrado.empty:
        col_g1, col_g2 = st.columns([1.5, 1.5])
        
        with col_g1:
            st.markdown("#### 📊 Distribución por Categoría")
            st.caption("Participación de cada rubro en el monto total filtrado.")
            resumen_cat = df_filtrado.groupby("categoria")["monto_num"].sum().reset_index()
            resumen_cat.columns = ["Categoría", "Monto"]
            resumen_cat = resumen_cat.sort_values(by="Monto", ascending=False)
            st.bar_chart(resumen_cat.set_index("Categoría"), height=300)

        with col_g2:
            st.markdown("#### 📈 Evolución Cronológica")
            st.caption("Tendencia de egresos agrupados por día.")
            evolucion_dia = df_filtrado.groupby(df_filtrado["fecha_dt"].dt.date)["monto_num"].sum().reset_index()
            evolucion_dia.columns = ["Fecha", "Monto"]
            evolucion_dia = evolucion_dia.sort_values(by="Fecha")
            st.line_chart(evolucion_dia.set_index("Fecha"), height=300)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📋 Balance Consolidado de Rubros")
        resumen_tabla = resumen_cat.copy()
        resumen_tabla["% del Total"] = ((resumen_tabla["Monto"] / max(total_filtrado, 1)) * 100).round(1).astype(str) + "%"
        resumen_tabla["Total (Gs.)"] = resumen_tabla["Monto"].apply(formato_gs)
        st.dataframe(resumen_tabla[["Categoría", "Total (Gs.)", "% del Total"]], use_container_width=True)
    else:
        st.info("Sin registros suficientes para graficar en este intervalo.")

# -------------------------------------------------------------------------
# TAB 4: MODIFICAR O ELIMINAR ASIENTO
# -------------------------------------------------------------------------
with tab_editar:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_filtrado.empty:
        st.markdown("### ⚙️ Modificar o Eliminar Asiento Contable")
        st.caption("Selecciona cualquier asiento contable para ajustar montos, rubros o descartar registros erróneos.")
        
        opciones_dict = {}
        for _, row in df_filtrado.iterrows():
            etiqueta = f"ID #{row['id']} | {row.get('fecha')} | {row.get('categoria')} | {formato_gs(row.get('monto'))} | {str(row.get('descripcion'))[:40]}"
            opciones_dict[etiqueta] = row

        sel_etiqueta = st.selectbox("Seleccione el registro a modificar:", list(opciones_dict.keys()))
        fila_sel = opciones_dict[sel_etiqueta]
        id_sel = fila_sel["id"]

        with st.form("form_edit_gasto"):
            ce1, ce2 = st.columns(2)
            with ce1:
                e_desc = st.text_input("Descripción", value=str(fila_sel.get("descripcion", "")))
                e_monto = st.number_input("Monto (Gs.)", value=int(fila_sel.get("monto", 0)), step=5000, format="%d")
            with ce2:
                cat_actual = fila_sel.get("categoria")
                idx_c = CATEGORIAS_GASTO.index(cat_actual) if cat_actual in CATEGORIAS_GASTO else 0
                e_cat = st.selectbox("Categoría", CATEGORIAS_GASTO, index=idx_c)
                e_fecha = st.date_input("Fecha", value=pd.to_datetime(fila_sel.get("fecha")).date() if fila_sel.get("fecha") else datetime.now())

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            b_act, b_elim = st.columns(2)
            with b_act:
                btn_actualizar = st.form_submit_button("🔄 ACTUALIZAR GASTO", use_container_width=True)
            with b_elim:
                btn_eliminar = st.form_submit_button("🗑️ ELIMINAR GASTO", use_container_width=True)

            if btn_actualizar:
                try:
                    supabase.table("gastos_personales").update({
                        "descripcion": e_desc.strip(),
                        "monto": int(e_monto),
                        "categoria": e_cat,
                        "fecha": str(e_fecha)
                    }).eq("id", id_sel).execute()
                    st.success("Gasto actualizado exitosamente en Supabase.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar: {e}")

            if btn_eliminar:
                try:
                    supabase.table("gastos_personales").delete().eq("id", id_sel).execute()
                    st.success("Gasto eliminado correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")
    else:
        st.info("No hay registros disponibles para editar en el período seleccionado.")