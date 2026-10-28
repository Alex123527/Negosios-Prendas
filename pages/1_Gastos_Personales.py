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
# SISTEMA DE ESTILOS VISUALES (Inspirado en Canvas UI de Alto Nivel)
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
# BANNER PRINCIPAL Y FILTROS
# =========================================================================
st.markdown("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); padding: 22px 26px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);">
        <span style="background: rgba(37, 99, 245, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.35); padding: 3px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
            Módulo Privado & Finanzas
        </span>
        <h1 style="color: #ffffff; font-size: 1.7rem; font-weight: 800; margin: 8px 0 4px 0; letter-spacing: -0.02em;">
            👤 Gestión de Gastos Personales
        </h1>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            Control independiente de egresos privados estructurado para blindar y no mezclar el capital de giro del emprendimiento.
        </p>
    </div>
""", unsafe_allow_html=True)

mes_actual = datetime.now().strftime("%Y-%m")

if not df_gastos.empty and "periodo" in df_gastos.columns:
    periodos_disponibles = sorted([p for p in df_gastos["periodo"].dropna().unique()], reverse=True)
    if mes_actual not in periodos_disponibles:
        periodos_disponibles.insert(0, mes_actual)
    
    col_f1, col_f2 = st.columns([1.5, 2.5])
    with col_f1:
        filtro_periodo = st.selectbox("📅 Período de Análisis:", ["Todos"] + periodos_disponibles)
    
    if filtro_periodo != "Todos":
        df_filtrado = df_gastos[df_gastos["periodo"] == filtro_periodo].copy()
    else:
        df_filtrado = df_gastos.copy()
else:
    df_filtrado = df_gastos.copy()
    filtro_periodo = "Todos"

# Cálculos de Métricas
total_acumulado = int(df_gastos["monto_num"].sum()) if not df_gastos.empty else 0
total_filtrado = int(df_filtrado["monto_num"].sum()) if not df_filtrado.empty else 0
cant_movimientos = len(df_filtrado)

col_k1, col_k2, col_k3 = st.columns(3)

with col_k1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">💸 Gasto del Período ({filtro_periodo})</div>
            <div class="kpi-val" style="color: #f87171;">{formato_gs(total_filtrado)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">{cant_movimientos} movimientos registrados</span>
        </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📦 Total Histórico Acumulado</div>
            <div class="kpi-val" style="color: #38bdf8;">{formato_gs(total_acumulado)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">{len(df_gastos)} registros totales</span>
        </div>
    """, unsafe_allow_html=True)

with col_k3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🛡️ Estado Patrimonial</div>
            <div class="kpi-val" style="color: #10b981; font-size: 1.35rem; margin-top: 8px;">Cuentas Separadas</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Protegiendo capital de giro</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# =========================================================================
# NAVEGACIÓN MODERNA POR PESTAÑAS (TABS)
# =========================================================================
tab_nuevo, tab_historial, tab_analisis, tab_editar = st.tabs([
    "📝 Registrar Nuevo Gasto",
    "📋 Historial & Exportación (Excel / PDF)",
    "📊 Distribución & Categorías",
    "⚙️ Modificar / Eliminar Registro"
])

# -------------------------------------------------------------------------
# TAB 1: REGISTRAR NUEVO GASTO
# -------------------------------------------------------------------------
with tab_nuevo:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    with st.form("form_nuevo_gasto", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_g = st.date_input("Fecha de Operación", value=datetime.now())
            categoria_g = st.selectbox("Categoría de Gasto", [
                "Alimentación / Supermercado",
                "Combustible / Transporte",
                "Servicios (Luz, Agua, Internet)",
                "Salud / Farmacia",
                "Ocio / Salidas",
                "Educación / Cursos",
                "Ropa / Uso Propio",
                "Otros Gastos"
            ])
            forma_pago_g = st.selectbox("Método de Pago", ["Efectivo", "Transferencia", "Billetera Digital / Tarjeta"])

        with c2:
            monto_g = st.number_input("Monto en Guaraníes (Gs.)", min_value=0, value=50000, step=5000, format="%d")
            st.caption(f"Valor a asentar: **{formato_gs(monto_g)}**")
            descripcion_g = st.text_input("Descripción / Motivo", placeholder="Ej: Supermercado mensual, carga combustible...")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        btn_guardar = st.form_submit_button("💾 ASENTAR GASTO PERSONAL", use_container_width=True)

        if btn_guardar:
            if monto_g > 0 and descripcion_g.strip():
                nuevo_reg = {
                    "fecha": str(fecha_g),
                    "categoria": categoria_g,
                    "monto": int(monto_g),
                    "descripcion": f"{descripcion_g.strip()} ({forma_pago_g})"
                }
                try:
                    supabase.table("gastos_personales").insert(nuevo_reg).execute()
                    st.success("¡Gasto registrado con éxito en la base de datos!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar en Supabase: {e}")
            else:
                st.warning("Ingrese un monto válido y una descripción representativa.")

# -------------------------------------------------------------------------
# TAB 2: HISTORIAL Y REPORTES EXCEL / PDF
# -------------------------------------------------------------------------
with tab_historial:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_filtrado.empty:
        col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
        with col_t1:
            st.markdown(f"### 📋 Registros del Período ({filtro_periodo})")
            st.caption("Consulta detallada de movimientos y descargas en formatos ejecutivos.")

        cols_mostrar = ["id", "fecha", "categoria", "descripcion", "monto"]
        cols_existentes = [c for c in cols_mostrar if c in df_filtrado.columns]
        
        df_visual = df_filtrado[cols_existentes].copy()
        if "monto" in df_visual.columns:
            df_visual["MONTO (GS.)"] = df_visual["monto"].apply(formato_gs)

        # 1. Exportación Excel
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
            <h2>👤 REPORTE DE GASTOS PERSONALES</h2>
            <p>Período: {filtro_periodo} | Emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <table>
                <thead>
                    <tr>
                        <th>ID</th><th>Fecha</th><th>Categoría</th><th>Descripción</th><th>Monto</th>
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
        st.info("No se encontraron registros de gastos personales para el período seleccionado.")

# -------------------------------------------------------------------------
# TAB 3: DISTRIBUCIÓN POR CATEGORÍAS
# -------------------------------------------------------------------------
with tab_analisis:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_filtrado.empty and "categoria" in df_filtrado.columns:
        st.markdown(f"### 📊 Egresos por Categoría ({filtro_periodo})")
        st.caption("Concentración de gastos personales según destino financiero.")
        
        resumen_cat = df_filtrado.groupby("categoria")["monto_num"].sum().reset_index()
        resumen_cat.columns = ["Categoría", "Monto"]
        resumen_cat = resumen_cat.sort_values(by="Monto", ascending=False)
        
        col_g1, col_g2 = st.columns([1.8, 1.2])
        with col_g1:
            st.bar_chart(resumen_cat.set_index("Categoría"), height=320)
        
        with col_g2:
            resumen_tabla = resumen_cat.copy()
            resumen_tabla["Total (Gs.)"] = resumen_tabla["Monto"].apply(formato_gs)
            st.dataframe(resumen_tabla[["Categoría", "Total (Gs.)"]], use_container_width=True)
    else:
        st.info("Sin registros suficientes para graficar en este intervalo.")

# -------------------------------------------------------------------------
# TAB 4: MODIFICAR O ELIMINAR REGISTRO
# -------------------------------------------------------------------------
with tab_editar:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_filtrado.empty:
        st.markdown("### ⚙️ Modificar o Eliminar Gasto")
        st.caption("Selecciona cualquier asiento contable para ajustar montos o descartar registros erróneos.")
        
        opciones_dict = {}
        for _, row in df_filtrado.iterrows():
            etiqueta = f"ID #{row['id']} | {row.get('fecha')} | {row.get('categoria')} | {formato_gs(row.get('monto'))} - {row.get('descripcion')}"
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
                cat_lista = [
                    "Alimentación / Supermercado",
                    "Combustible / Transporte",
                    "Servicios (Luz, Agua, Internet)",
                    "Salud / Farmacia",
                    "Ocio / Salidas",
                    "Educación / Cursos",
                    "Ropa / Uso Propio",
                    "Otros Gastos"
                ]
                idx_c = cat_lista.index(fila_sel.get("categoria")) if fila_sel.get("categoria") in cat_lista else 0
                e_cat = st.selectbox("Categoría", cat_lista, index=idx_c)
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