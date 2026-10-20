import streamlit as st
import pandas as pd
from datetime import datetime
import io
from supabase import create_client, Client

st.set_page_config(page_title="Gastos Personales | PROYECTO X", page_icon="👤", layout="wide")

# Estilo visual moderno y limpio
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
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

# Validación de sesión
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso restringido. Inicie sesión en app.py.")
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

st.title("👤 GESTIÓN DE GASTOS PERSONALES")
st.caption("CONTROL INDEPENDIENTE DE EGRESOS PRIVADOS (SEPARADO DEL CAPITAL DEL NEGOCIO)")

# --- BARRA DE FILTROS Y MÉTRICAS DINÁMICAS ---
mes_actual = datetime.now().strftime("%Y-%m")

if not df_gastos.empty and "periodo" in df_gastos.columns:
    periodos_disponibles = sorted([p for p in df_gastos["periodo"].dropna().unique()], reverse=True)
    if mes_actual not in periodos_disponibles:
        periodos_disponibles.insert(0, mes_actual)
    
    col_f1, col_f2 = st.columns([1.5, 2.5])
    with col_f1:
        filtro_periodo = st.selectbox("📅 Filtrar por Mes/Año:", ["Todos"] + periodos_disponibles)
    
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

m1, m2, m3 = st.columns(3)
m1.metric("💸 GASTO DEL PERÍODO", formato_gs(total_filtrado), f"{cant_movimientos} movimientos")
m2.metric("📦 TOTAL HISTÓRICO ACUMULADO", formato_gs(total_acumulado), f"{len(df_gastos)} registros totales")
m3.metric("🛡️ ESTADO PATRIMONIAL", "Cuentas Separadas", "Protegiendo capital de giro")

st.markdown("---")

# --- REGISTRO Y DISTRIBUCIÓN ---
col_form, col_cat = st.columns([1.7, 1.3])

with col_form:
    st.subheader("📝 REGISTRAR NUEVO GASTO")
    with st.form("form_nuevo_gasto", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_g = st.date_input("Fecha", value=datetime.now())
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
            monto_g = st.number_input("Monto (Gs.)", min_value=0, value=50000, step=5000, format="%d")
            st.caption(f"Equivalente: **{formato_gs(monto_g)}**")
            descripcion_g = st.text_input("Descripción / Motivo", placeholder="Ej: Supermercado semanal, combustible")

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
                    st.success("¡Gasto registrado con éxito!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar en Supabase: {e}")
            else:
                st.warning("Ingrese un monto válido y una breve descripción.")

with col_cat:
    st.subheader("📊 DISTRIBUCIÓN POR CATEGORÍA")
    if not df_filtrado.empty and "categoria" in df_filtrado.columns:
        resumen_cat = df_filtrado.groupby("categoria")["monto_num"].sum().reset_index()
        resumen_cat.columns = ["Categoría", "Monto"]
        resumen_cat = resumen_cat.sort_values(by="Monto", ascending=False)
        
        # Gráfico de barras nativo de Streamlit
        st.bar_chart(resumen_cat.set_index("Categoría"), height=260)
    else:
        st.info("Sin registros en este período para graficar.")

st.markdown("---")

# --- HISTORIAL Y EXPORTACIÓN ---
col_t1, col_t2 = st.columns([2.5, 1.5])
with col_t1:
    st.subheader(f"📋 HISTORIAL DE GASTOS ({filtro_periodo})")

if not df_filtrado.empty:
    cols_mostrar = ["id", "fecha", "categoria", "descripcion", "monto"]
    cols_existentes = [c for c in cols_mostrar if c in df_filtrado.columns]
    
    df_visual = df_filtrado[cols_existentes].copy()
    if "monto" in df_visual.columns:
        df_visual["MONTO (GS.)"] = df_visual["monto"].apply(formato_gs)

    # Botón de exportación a Excel
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df_visual.to_excel(writer, index=False, sheet_name='Gastos_Personales')
    excel_data = buf.getvalue()

    with col_t2:
        st.download_button(
            label="📗 Descargar Lista en Excel (.xlsx)",
            data=excel_data,
            file_name=f"Gastos_Personales_{filtro_periodo}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.dataframe(df_visual, use_container_width=True)

    # --- EDICIÓN / ELIMINACIÓN DE REGISTROS ---
    st.markdown("### ⚙️ MODIFICAR O ELIMINAR GASTO")
    
    # Mapeo de opciones para el selector
    opciones_dict = {}
    for _, row in df_filtrado.iterrows():
        etiqueta = f"ID #{row['id']} | {row.get('fecha')} | {row.get('categoria')} | {formato_gs(row.get('monto'))} - {row.get('descripcion')}"
        opciones_dict[etiqueta] = row

    sel_etiqueta = st.selectbox("Seleccione el registro a modificar o eliminar:", list(opciones_dict.keys()))
    fila_sel = opciones_dict[sel_etiqueta]
    id_sel = fila_sel["id"]

    with st.form("form_edit_gasto"):
        ce1, ce2 = st.columns(2)
        with ce1:
            e_desc = st.text_input("Descripción", value=str(fila_sel.get("descripcion", "")))
            e_monto = st.number_input("Monto (Gs.)", value=int(fila_sel.get("monto", 0)), step=5000, format="%d")
        with ce2:
            e_cat = st.selectbox("Categoría", [
                "Alimentación / Supermercado",
                "Combustible / Transporte",
                "Servicios (Luz, Agua, Internet)",
                "Salud / Farmacia",
                "Ocio / Salidas",
                "Educación / Cursos",
                "Ropa / Uso Propio",
                "Otros Gastos"
            ], index=0 if fila_sel.get("categoria") not in [
                "Alimentación / Supermercado", "Combustible / Transporte", "Servicios (Luz, Agua, Internet)",
                "Salud / Farmacia", "Ocio / Salidas", "Educación / Cursos", "Ropa / Uso Propio", "Otros Gastos"
            ] else [
                "Alimentación / Supermercado", "Combustible / Transporte", "Servicios (Luz, Agua, Internet)",
                "Salud / Farmacia", "Ocio / Salidas", "Educación / Cursos", "Ropa / Uso Propio", "Otros Gastos"
            ].index(fila_sel.get("categoria")))
            e_fecha = st.date_input("Fecha", value=pd.to_datetime(fila_sel.get("fecha")).date() if fila_sel.get("fecha") else datetime.now())

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
                st.success("Gasto actualizado exitosamente.")
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
    st.info("No se encontraron registros de gastos personales para el período seleccionado.")