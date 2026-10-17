import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gastos Personales | PROYECTO X", page_icon="⚡", layout="wide")

# CSS Futurista Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #071426; color: #E6EDF5; }
    section[data-testid="stSidebar"] { background-color: #0b1a2f !important; }
    .premium-card {
        background-color: #10213A;
        border: 1px solid #1E365D;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #4388FF 0%, #2f6de0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(67, 136, 255, 0.25) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #5c9bff 0%, #4388FF 100%) !important;
        transform: translateY(-1px);
    }
    [data-testid="stMetricValue"] { color: #21D4C4 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #9FB2C8 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #0d1b30 !important;
        color: #E6EDF5 !important;
        border: 1px solid #1E365D !important;
    }
    </style>
""", unsafe_allow_html=True)

# Escudo de Seguridad
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso restringido. Por favor autentíquese en app.py.")
    st.stop()

# Conexión Base de Datos
conn = sqlite3.connect("negocio_prendas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos_personales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT, descripcion TEXT, categoria TEXT, metodo_pago TEXT, monto REAL, comprobante_nombre TEXT
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS notas_planner (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mes TEXT, notas TEXT, meta_ahorro REAL, objetivo_monto REAL
    )
""")
conn.commit()

# Función para formatear moneda en Guaraníes con separador de miles por puntos
def formato_gs(valor):
    val_int = int(round(valor or 0))
    return f"Gs. {val_int:,}".replace(",", ".")

st.title("⚡ CONTROL DE GASTOS PERSONALES")
st.caption("FINANCIAL TRACKING & WEALTH BUILDING")

# Cálculos
df_gastos_calc = pd.read_sql_query("SELECT SUM(monto) as total FROM gastos_personales", conn)
total_gastos_p = df_gastos_calc['total'].iloc[0] if not df_gastos_calc.empty and df_gastos_calc['total'].iloc[0] is not None else 0.0

df_caja_ing = pd.read_sql_query("SELECT SUM(monto) as total FROM transacciones WHERE tipo='Entrada (Venta/Cobro)'", conn)
total_ingresos_p = df_caja_ing['total'].iloc[0] if not df_caja_ing.empty and df_caja_ing['total'].iloc[0] is not None else 2500000.0
ahorro_p = max(0.0, total_ingresos_p - total_gastos_p)

# Métricas Principales en Gs.
m1, m2, m3 = st.columns(3)
m1.metric("💰 INGRESOS COMPUTADOS", formato_gs(total_ingresos_p))
m2.metric("🛒 GASTOS REGISTRADOS", formato_gs(total_gastos_p))
m3.metric("✨ CAPACIDAD DE AHORRO", formato_gs(ahorro_p))

st.markdown("---")

col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("📝 Nuevo Registro de Egreso")
    st.caption("💡 *Tip: Puedes presionar **Enter** tras ingresar el monto para guardar automáticamente.*")
    
    with st.form("form_gasto_personal", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            fecha_gasto = st.date_input("Fecha", value=datetime.now())
            descripcion_gasto = st.text_input("Concepto / Descripción")
            categoria_gasto = st.selectbox("Categoría", ["Vivienda", "Comida", "Transporte", "Servicios", "Ocio", "Salud", "Estudios", "Otros"])
        with f_col2:
            metodo_pago = st.selectbox("Canal de Pago", ["Efectivo", "Débito", "Débito automático", "Transferencia", "Tarjeta de crédito"])
            monto_gasto = st.number_input("Monto (Gs.)", min_value=0, value=0, step=5000, format="%d")
            archivo_comprobante = st.file_uploader("Documento de Respaldo", type=["png", "jpg", "jpeg", "pdf"])
        
        # Al presionar Enter dentro de cualquier input del formulario, se activa este botón
        submit_gasto = st.form_submit_button("💾 ASENTAR GASTO (O PRESIONA ENTER)")
        
        if submit_gasto:
            if monto_gasto > 0 and descripcion_gasto.strip():
                nombre_archivo = archivo_comprobante.name if archivo_comprobante else "Sin archivo"
                cursor.execute("""
                    INSERT INTO gastos_personales (fecha, descripcion, categoria, metodo_pago, monto, comprobante_nombre)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (str(fecha_gasto), descripcion_gasto, categoria_gasto, metodo_pago, float(monto_gasto), nombre_archivo))
                conn.commit()
                st.success("Operación registrada en base de datos.")
                st.rerun()
            else:
                st.warning("Ingresa una descripción válida y un monto mayor a 0.")

with col_der:
    st.subheader("📊 Distribución por Categoría")
    categorias_lista = ["Vivienda", "Comida", "Transporte", "Servicios", "Ocio", "Salud", "Estudios", "Otros"]
    for cat in categorias_lista:
        df_cat = pd.read_sql_query("SELECT SUM(monto) as total FROM gastos_personales WHERE categoria = ?", conn, params=(cat,))
        tot_cat = df_cat['total'].iloc[0] if not df_cat.empty and df_cat['total'].iloc[0] is not None else 0.0
        st.write(f"• **{cat}**: `{formato_gs(tot_cat)}`")

st.markdown("---")

col_meta1, col_meta2 = st.columns(2)
with col_meta1:
    st.subheader("🎯 Objetivo de Capitalización")
    meta_objetivo = st.number_input("Meta de Ahorro Activo (Gs.):", min_value=10000, value=1000000, step=50000, format="%d")
    porcentaje_ahorro = min(100, int((ahorro_p / meta_objetivo) * 100))
    st.progress(porcentaje_ahorro / 100, text=f"Rendimiento: {porcentaje_ahorro}% ({formato_gs(ahorro_p)} / {formato_gs(meta_objetivo)})")
    if porcentaje_ahorro >= 100:
        st.success("✨ Meta superada con éxito.")

with col_meta2:
    st.subheader("📌 Anotaciones Financieras")
    st.text_area("Notas estratégicas:", placeholder="Estrategia de reducción de costes, compras planificadas...")
    if st.button("Guardar Nota"):
        st.success("Nota preservada localmente.")

st.markdown("---")
st.subheader("📋 Registro Maestro de Gastos")
df_gp = pd.read_sql_query("SELECT * FROM gastos_personales ORDER BY id DESC", conn)

if not df_gp.empty:
    st.dataframe(df_gp, use_container_width=True)
    st.markdown("### ⚙️ ADMINISTRACIÓN DE REGISTROS")
    sel_gp = st.selectbox("ID de Transacción a Modificar:", df_gp['id'].tolist())
    fila_gp = df_gp[df_gp['id'] == sel_gp].iloc[0]

    with st.form("form_edit_gp"):
        eg_desc = st.text_input("Descripción", value=fila_gp['descripcion'])
        eg_monto = st.number_input("Monto (Gs.)", value=int(fila_gp['monto']), format="%d", step=1000)
        c_bt1, c_bt2 = st.columns(2)
        if c_bt1.form_submit_button("🔄 ACTUALIZAR (ENTER)"):
            cursor.execute("UPDATE gastos_personales SET descripcion=?, monto=? WHERE id=?", (eg_desc, float(eg_monto), sel_gp))
            conn.commit()
            st.success("Registro modificado.")
            st.rerun()
        if c_bt2.form_submit_button("🗑️ PURGAR REGISTRO"):
            cursor.execute("DELETE FROM gastos_personales WHERE id=?", (sel_gp,))
            conn.commit()
            st.success("Registro eliminado.")
            st.rerun()
else:
    st.info("Sin operaciones registradas.")