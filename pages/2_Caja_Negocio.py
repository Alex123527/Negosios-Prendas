import streamlit as st
import pandas as pd
from datetime import datetime
import io
from supabase import create_client, Client

st.set_page_config(
    page_title="Caja de Negocio | PROYECTO X",
    page_icon="💼",
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
# ESCUDO DE SEGURIDAD Y CONEXIÓN A SUPABASE
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

# =========================================================================
# BANNER PRINCIPAL Y KPIs SUPERIORES
# =========================================================================
st.markdown("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); padding: 22px 26px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);">
        <span style="background: rgba(37, 99, 245, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.35); padding: 3px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
            Módulo Operativo & Tesorería
        </span>
        <h1 style="color: #ffffff; font-size: 1.7rem; font-weight: 800; margin: 8px 0 4px 0; letter-spacing: -0.02em;">
            💼 Caja de Negocio y Flujo Financiero
        </h1>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            Supervisión diaria de ingresos comerciales, egresos operativos, fletes y balance neto en tiempo real.
        </p>
    </div>
""", unsafe_allow_html=True)

# Cálculos Totales
ingresos_total = 0.0
egresos_total = 0.0

if not df_tx.empty and "monto" in df_tx.columns and "tipo" in df_tx.columns:
    df_tx["monto_num"] = pd.to_numeric(df_tx["monto"], errors="coerce").fillna(0)
    ingresos_total = float(df_tx[df_tx["tipo"] == "Ingreso"]["monto_num"].sum())
    egresos_total = float(df_tx[df_tx["tipo"] == "Egreso"]["monto_num"].sum())

saldo_neto = ingresos_total - egresos_total
margen = (saldo_neto / ingresos_total * 100) if ingresos_total > 0 else 0

col_k1, col_k2, col_k3 = st.columns(3)

with col_k1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📈 Ingresos Totales Negocio</div>
            <div class="kpi-val" style="color: #10b981;">{formato_gs(ingresos_total)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Facturación y cobros registrados</span>
        </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📉 Egresos Operativos Totales</div>
            <div class="kpi-val" style="color: #ef4444;">{formato_gs(egresos_total)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Compras, fletes y servicios</span>
        </div>
    """, unsafe_allow_html=True)

with col_k3:
    color_saldo = "#38bdf8" if saldo_neto >= 0 else "#f87171"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">💵 Saldo Neto Disponible</div>
            <div class="kpi-val" style="color: {color_saldo};">{formato_gs(saldo_neto)}</div>
            <span style="font-size: 0.75rem; color: #94a3b8;">Margen operativo global: <strong>{margen:.1f}%</strong></span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# =========================================================================
# NAVEGACIÓN MODERNA POR PESTAÑAS (TABS)
# =========================================================================
tab_operacion, tab_diario, tab_balance, tab_edicion = st.tabs([
    "➕ Asentar Movimiento",
    "📋 Libro Diario & Reportes (Excel / PDF)",
    "📊 Balance & Distribución",
    "⚙️ Modificar / Eliminar Operación"
])

# -------------------------------------------------------------------------
# TAB 1: ASENTAR OPERACIÓN DE CAJA
# -------------------------------------------------------------------------
with tab_operacion:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    with st.form("form_caja", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            fecha_op = st.date_input("Fecha de Operación", value=datetime.now())
            tipo_op = st.selectbox("Tipo de Movimiento", ["Ingreso", "Egreso"])
            categoria_op = st.selectbox("Categoría", [
                "Venta de Prenda", "Cobro de Deuda", "Inversión Mercadería", 
                "Packaging / Envíos", "Publicidad", "Alquiler / Servicios", "Otros Gastos"
            ])

        with c2:
            cliente_op = st.text_input("Cliente / Proveedor", placeholder="Ej: María González / Distribuidor")
            concepto_op = st.text_input("Concepto Principal", placeholder="Ej: 2x Calzas Deportivas, Bobina Cinta...")
            monto_op = st.number_input("Monto en Guaraníes (Gs.)", min_value=0, value=0, step=5000, format="%d")
            st.caption(f"Valor asentado: **{formato_gs(monto_op)}**")

        with c3:
            estado_entrega = st.selectbox("Estado del Pedido / Flujo", ["Entregado", "En proceso", "Rechazado"])
            tipo_pago = st.selectbox("Medio de Pago", ["Efectivo", "Transferencia Bancaria", "Billetera Zimple / Giros", "Tarjeta de Débito/Crédito", "Otro"])
            comprobante = st.file_uploader("Comprobante / Recibo (Opcional)", type=["png", "jpg", "jpeg", "pdf"])

        detalle_op = st.text_input("Detalle Adicional", placeholder="Ej: Entregado por delivery / Pedido confirmado vía Instagram")
        
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        btn_guardar = st.form_submit_button("💾 ASENTAR OPERACIÓN EN CAJA", use_container_width=True)
        
        if btn_guardar:
            partes_desc = []
            if cliente_op.strip():
                partes_desc.append(f"Cliente: {cliente_op.strip()}")
            if concepto_op.strip():
                partes_desc.append(f"Concepto: {concepto_op.strip()}")
            if estado_entrega:
                partes_desc.append(f"Estado: {estado_entrega}")
            if tipo_pago:
                partes_desc.append(f"Pago: {tipo_pago}")
            if comprobante is not None:
                partes_desc.append(f"Doc: {comprobante.name}")
            if detalle_op.strip():
                partes_desc.append(f"Detalle: {detalle_op.strip()}")
            
            descripcion_completa = " | ".join(partes_desc)

            if monto_op > 0 and descripcion_completa.strip():
                nueva_tx = {
                    "fecha": str(fecha_op),
                    "tipo": tipo_op,
                    "categoria": categoria_op,
                    "monto": int(monto_op),
                    "descripcion": descripcion_completa
                }
                try:
                    supabase.table("transacciones").insert(nueva_tx).execute()
                    st.success("Transacción registrada con éxito en Supabase.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar: {e}")
            else:
                st.warning("Completa los datos de la operación e ingresa un monto mayor a 0.")

# -------------------------------------------------------------------------
# TAB 2: LIBRO DIARIO Y EXPORTACIONES EXCEL / PDF
# -------------------------------------------------------------------------
with tab_diario:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_tx.empty:
        col_tit, col_exp1, col_exp2 = st.columns([2, 1, 1])
        with col_tit:
            st.markdown("### 📋 Libro Diario Contable")
            st.caption("Registro histórico de transacciones operativas con filtros y descargas auditables.")

        cols_mostrar = [c for c in ["id", "fecha", "tipo", "categoria", "monto", "descripcion"] if c in df_tx.columns]
        df_visual = df_tx[cols_mostrar].copy()
        
        if "monto" in df_visual.columns:
            df_visual["MONTO (GS.)"] = df_visual["monto"].apply(formato_gs)

        # 1. Exportación Excel (.xlsx)
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_visual.to_excel(writer, index=False, sheet_name='Caja_Diaria')
        excel_data = buffer_excel.getvalue()

        with col_exp1:
            st.download_button(
                label="📗 Descargar Excel (.xlsx)",
                data=excel_data,
                file_name=f"Libro_Caja_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # 2. Exportación PDF Imprimible
        filas_html = ""
        for _, f in df_visual.iterrows():
            color_tipo = "#10b981" if f.get("tipo") == "Ingreso" else "#ef4444"
            filas_html += f"""
            <tr>
                <td>{f.get('id', '')}</td>
                <td>{f.get('fecha', '')}</td>
                <td><strong style='color: {color_tipo};'>{f.get('tipo', '')}</strong></td>
                <td>{f.get('categoria', '')}</td>
                <td style='text-align: right; font-weight: bold;'>{f.get('MONTO (GS.)', '')}</td>
                <td>{f.get('descripcion', '')}</td>
            </tr>
            """

        html_reporte = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Libro Diario de Caja - PROYECTO X</title>
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
                ℹ️ <em>Se abrirá automáticamente el cuadro de impresión. Selecciona <strong>"Guardar como PDF"</strong> para archivarlo.</em>
            </div>
            <h2>💼 LIBRO DIARIO DE CAJA COMERCIAL</h2>
            <p>Emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Saldo Neto Actual: {formato_gs(saldo_neto)}</p>
            <table>
                <thead>
                    <tr>
                        <th>ID</th><th>Fecha</th><th>Tipo</th><th>Categoría</th><th>Monto</th><th>Descripción</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </body>
        </html>
        """

        with col_exp2:
            st.download_button(
                label="📕 Imprimir / PDF",
                data=html_reporte.encode('utf-8'),
                file_name=f"Reporte_Caja_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )

        st.dataframe(df_visual, use_container_width=True)
    else:
        st.info("No hay transacciones registradas en el flujo de caja aún.")

# -------------------------------------------------------------------------
# TAB 3: BALANCE & DISTRIBUCIÓN POR CATEGORÍA
# -------------------------------------------------------------------------
with tab_balance:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_tx.empty and "categoria" in df_tx.columns:
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            st.markdown("#### 📈 Ingresos por Categoría")
            df_ing = df_tx[df_tx["tipo"] == "Ingreso"]
            if not df_ing.empty:
                cat_ing = df_ing.groupby("categoria")["monto_num"].sum().reset_index()
                cat_ing.columns = ["Categoría", "Monto"]
                st.bar_chart(cat_ing.set_index("Categoría"), height=260)
            else:
                st.caption("Sin ingresos registrados.")

        with col_b2:
            st.markdown("#### 📉 Egresos por Categoría")
            df_egr = df_tx[df_tx["tipo"] == "Egreso"]
            if not df_egr.empty:
                cat_egr = df_egr.groupby("categoria")["monto_num"].sum().reset_index()
                cat_egr.columns = ["Categoría", "Monto"]
                st.bar_chart(cat_egr.set_index("Categoría"), height=260)
            else:
                st.caption("Sin egresos registrados.")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 💼 Resumen de Liquidez Operativa")
        st.write(f"• **Facturación Total Acumulada:** `{formato_gs(ingresos_total)}`")
        st.write(f"• **Costos y Egresos Operativos:** `{formato_gs(egresos_total)}`")
        st.write(f"• **Margen Neto de Rentabilidad:** `{margen:.1f}%`")
    else:
        st.info("Sin datos suficientes para calcular la distribución.")

# -------------------------------------------------------------------------
# TAB 4: MODIFICAR / ELIMINAR OPERACIÓN
# -------------------------------------------------------------------------
with tab_edicion:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if not df_tx.empty:
        st.markdown("### ⚙️ Modificar o Eliminar Transacción")
        st.caption("Selecciona cualquier asiento del libro diario para ajustar la descripción o remover registros.")
        
        opciones_caja = {
            f"ID #{row['id']} | {row.get('fecha')} | {row.get('tipo')} | {formato_gs(row.get('monto'))} - {str(row.get('descripcion'))[:40]}...": row['id']
            for _, row in df_tx.iterrows()
        }
        
        tx_sel_txt = st.selectbox("Seleccione la operación a modificar:", list(opciones_caja.keys()))
        tx_id_sel = opciones_caja[tx_sel_txt]
        fila_tx = df_tx[df_tx["id"] == tx_id_sel].iloc[0]

        with st.form("form_edit_caja"):
            ed_desc = st.text_input("Detalle / Descripción completa", value=str(fila_tx["descripcion"]))
            ed_monto = st.number_input("Monto (Gs.)", value=int(fila_tx["monto"]), format="%d", step=5000)
            st.caption(f"Monto a actualizar: **{formato_gs(ed_monto)}**")
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            c_ed1, c_ed2 = st.columns(2)
            with c_ed1:
                btn_act = c_ed1.form_submit_button("🔄 ACTUALIZAR OPERACIÓN", use_container_width=True)
            with c_ed2:
                btn_elim = c_ed2.form_submit_button("🗑️ ELIMINAR OPERACIÓN", use_container_width=True)

            if btn_act:
                try:
                    supabase.table("transacciones").update({
                        "descripcion": ed_desc.strip(), 
                        "monto": int(ed_monto)
                    }).eq("id", tx_id_sel).execute()
                    st.success("Operación actualizada en Supabase con éxito.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar: {e}")

            if btn_elim:
                try:
                    supabase.table("transacciones").delete().eq("id", tx_id_sel).execute()
                    st.success("Operación eliminada de Supabase correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")
    else:
        st.info("No hay operaciones disponibles para editar.")