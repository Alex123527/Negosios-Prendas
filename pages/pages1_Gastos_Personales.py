<<<<<<< HEAD
from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(
    page_title="Control de Gastos Personales", page_icon="🌿", layout="wide"
)

# --- ESCUDO DE SEGURIDAD ---
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
  st.warning(
      "⚠️ Acceso denegado. Por favor, inicia sesión en la página principal"
      " (app.py)."
  )
  st.stop()
# ---------------------------

conn = sqlite3.connect("negocio_prendas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS gastos_personales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT, descripcion TEXT, categoria TEXT, metodo_pago TEXT, monto REAL, comprobante_nombre TEXT
    )
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS notas_planner (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mes TEXT, notas TEXT, meta_ahorro REAL, objetivo_monto REAL
    )
"""
)
conn.commit()

st.title("🌿 CONTROL DE GASTOS PERSONALES")
st.write("ORGANIZÁ • CONTROLÁ • AHORRÁ")

df_gastos_calc = pd.read_sql_query(
    "SELECT SUM(monto) as total FROM gastos_personales", conn
)
total_gastos_p = (
    df_gastos_calc["total"].iloc[0]
    if not df_gastos_calc.empty
    and df_gastos_calc["total"].iloc[0] is not None
    else 0.0
)

df_caja_ing = pd.read_sql_query(
    "SELECT SUM(monto) as total FROM transacciones WHERE tipo='Entrada"
    " (Venta/Cobro)'",
    conn,
)
total_ingresos_p = (
    df_caja_ing["total"].iloc[0]
    if not df_caja_ing.empty and df_caja_ing["total"].iloc[0] is not None
    else 250000.0
)
ahorro_p = max(0.0, total_ingresos_p - total_gastos_p)

m1, m2, m3 = st.columns(3)
m1.metric("💰 INGRESOS TOTALES", f"${total_ingresos_p:,.0f}")
m2.metric("🛒 GASTOS TOTALES", f"${total_gastos_p:,.0f}")
m3.metric("🐖 AHORRO", f"${ahorro_p:,.0f}")

st.markdown("---")

col_izq, col_der = st.columns([2, 1])

with col_izq:
  st.subheader("📝 Registrar Nuevo Gasto")
  with st.form("form_gasto_personal", clear_on_submit=True):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
      fecha_gasto = st.date_input("Fecha", value=datetime.now())
      descripcion_gasto = st.text_input("Descripción (Ej. Supermercado)")
      categoria_gasto = st.selectbox(
          "Categoría",
          [
              "Vivienda",
              "Comida",
              "Transporte",
              "Servicios",
              "Ocio",
              "Salud",
              "Estudios",
              "Otros",
          ],
      )
    with f_col2:
      metodo_pago = st.selectbox(
          "Método de Pago",
          [
              "Efectivo",
              "Débito",
              "Débito automático",
              "Transferencia",
              "Tarjeta de crédito",
          ],
      )
      monto_gasto = st.number_input(
          "Monto ($)", min_value=0.0, format="%.2f", step=100.0
      )
      archivo_comprobante = st.file_uploader(
          "Comprobante (Imagen/PDF)", type=["png", "jpg", "jpeg", "pdf"]
      )

    if st.form_submit_button("💾 Guardar Gasto en Planilla"):
      nombre_archivo = (
          archivo_comprobante.name if archivo_comprobante else "Sin archivo"
      )
      cursor.execute(
          """
                INSERT INTO gastos_personales (fecha, descripcion, categoria, metodo_pago, monto, comprobante_nombre)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
          (
              str(fecha_gasto),
              descripcion_gasto,
              categoria_gasto,
              metodo_pago,
              monto_gasto,
              nombre_archivo,
          ),
      )
      conn.commit()
      st.success("¡Gasto registrado con éxito!")
      st.rerun()

with col_der:
  st.subheader("🏷️ Total por Categoría")
  categorias_lista = [
      "Vivienda",
      "Comida",
      "Transporte",
      "Servicios",
      "Ocio",
      "Salud",
      "Estudios",
      "Otros",
  ]
  for cat in categorias_lista:
    df_cat = pd.read_sql_query(
        "SELECT SUM(monto) as total FROM gastos_personales WHERE categoria = ?",
        conn,
        params=(cat,),
    )
    tot_cat = (
        df_cat["total"].iloc[0]
        if not df_cat.empty and df_cat["total"].iloc[0] is not None
        else 0.0
    )
    st.write(f"• **{cat}**: ${tot_cat:,.0f}")

st.markdown("---")

col_meta1, col_meta2 = st.columns(2)

with col_meta1:
  st.subheader("🎯 Meta de Ahorro del Mes")
  meta_objetivo = st.number_input(
      "Definir Objetivo de Ahorro ($):", min_value=1.0, value=100000.0, step=5000.0
  )
  porcentaje_ahorro = min(100, int((ahorro_p / meta_objetivo) * 100))
  st.progress(
      porcentaje_ahorro / 100,
      text=f"Progreso de Ahorro: {porcentaje_ahorro}% (Logrado: ${ahorro_p:,.0f}"
      f" / Meta: ${meta_objetivo:,.0f})",
  )
  if porcentaje_ahorro >= 100:
    st.success("¡Felicitaciones! ¡Alcanzaste tu meta de ahorro este mes! ❤️")
  else:
    st.info("¡Vos podés lograrlo! Constancia y disciplina.")

with col_meta2:
  st.subheader("📌 Notas del Mes")
  nota_personal = st.text_area(
      "Escribe tus recordatorios o metas financieras:",
      placeholder="Ej. Reducir gastos en kiosco, Ahorrar 5% más...",
  )
  if st.button("Guardar Nota"):
    st.success("¡Nota guardada en tu planner personal!")

st.markdown("---")
st.subheader("📋 Planilla General de Movimientos y Administrador")
df_gp = pd.read_sql_query(
    "SELECT * FROM gastos_personales ORDER BY id DESC", conn
)

if not df_gp.empty:
  st.dataframe(df_gp, use_container_width=True)

  st.markdown("### ⚙️ ADMINISTRAR REGISTRO")
  ids_gp = df_gp["id"].tolist()
  sel_gp = st.selectbox("Seleccione ID de Gasto a administrar:", ids_gp)
  fila_gp = df_gp[df_gp["id"] == sel_gp].iloc[0]

  with st.form("form_edit_gp"):
    eg_desc = st.text_input("Descripción", value=fila_gp["descripcion"])
    eg_monto = st.number_input(
        "Monto ($)", value=float(fila_gp["monto"]), format="%.2f"
    )
    c_bt1, c_bt2 = st.columns(2)
    if c_bt1.form_submit_button("🔄 Actualizar Gasto"):
      cursor.execute(
          "UPDATE gastos_personales SET descripcion=?, monto=? WHERE id=?",
          (eg_desc, eg_monto, sel_gp),
      )
      conn.commit()
      st.success("¡Actualizado con éxito!")
      st.rerun()
    if c_bt2.form_submit_button("🗑️ Borrar Gasto"):
      cursor.execute("DELETE FROM gastos_personales WHERE id=?", (sel_gp,))
      conn.commit()
      st.success("¡Eliminado con éxito!")
      st.rerun()
else:
  st.info("Sin registros de gastos personales.")
=======
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gastos Personales | PROYECTO X", page_icon="⚡", layout="wide")

# CSS Futurista Compartido
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

st.title("⚡ CONTROL DE GASTOS PERSONALES")
st.caption("FINANCIAL TRACKING & WEALTH BUILDING")

# Cálculos
df_gastos_calc = pd.read_sql_query("SELECT SUM(monto) as total FROM gastos_personales", conn)
total_gastos_p = df_gastos_calc['total'].iloc[0] if not df_gastos_calc.empty and df_gastos_calc['total'].iloc[0] is not None else 0.0

df_caja_ing = pd.read_sql_query("SELECT SUM(monto) as total FROM transacciones WHERE tipo='Entrada (Venta/Cobro)'", conn)
total_ingresos_p = df_caja_ing['total'].iloc[0] if not df_caja_ing.empty and df_caja_ing['total'].iloc[0] is not None else 250000.0
ahorro_p = max(0.0, total_ingresos_p - total_gastos_p)

# Métricas Futuristas
m1, m2, m3 = st.columns(3)
m1.metric("💰 INGRESOS COMPUTADOS", f"${total_ingresos_p:,.0f}")
m2.metric("🛒 GASTOS REGISTRADOS", f"${total_gastos_p:,.0f}")
m3.metric("✨ CAPACIDAD DE AHORRO", f"${ahorro_p:,.0f}")

st.markdown("---")

col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("📝 Nuevo Registro de Egreso")
    with st.form("form_gasto_personal", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            fecha_gasto = st.date_input("Fecha", value=datetime.now())
            descripcion_gasto = st.text_input("Concepto / Descripción")
            categoria_gasto = st.selectbox("Categoría", ["Vivienda", "Comida", "Transporte", "Servicios", "Ocio", "Salud", "Estudios", "Otros"])
        with f_col2:
            metodo_pago = st.selectbox("Canal de Pago", ["Efectivo", "Débito", "Débito automático", "Transferencia", "Tarjeta de crédito"])
            monto_gasto = st.number_input("Monto ($)", min_value=0.0, format="%.2f", step=100.0)
            archivo_comprobante = st.file_uploader("Documento de Respaldo", type=["png", "jpg", "jpeg", "pdf"])
        
        if st.form_submit_button("💾 ASENTAR GASTO"):
            nombre_archivo = archivo_comprobante.name if archivo_comprobante else "Sin archivo"
            cursor.execute("""
                INSERT INTO gastos_personales (fecha, descripcion, categoria, metodo_pago, monto, comprobante_nombre)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (str(fecha_gasto), descripcion_gasto, categoria_gasto, metodo_pago, monto_gasto, nombre_archivo))
            conn.commit()
            st.success("Operación registrada en base de datos.")
            st.rerun()

with col_der:
    st.subheader("📊 Distribución")
    categorias_lista = ["Vivienda", "Comida", "Transporte", "Servicios", "Ocio", "Salud", "Estudios", "Otros"]
    for cat in categorias_lista:
        df_cat = pd.read_sql_query("SELECT SUM(monto) as total FROM gastos_personales WHERE categoria = ?", conn, params=(cat,))
        tot_cat = df_cat['total'].iloc[0] if not df_cat.empty and df_cat['total'].iloc[0] is not None else 0.0
        st.write(f"• **{cat}**: `${tot_cat:,.0f}`")

st.markdown("---")

col_meta1, col_meta2 = st.columns(2)
with col_meta1:
    st.subheader("🎯 Objetivo de Capitalización")
    meta_objetivo = st.number_input("Meta de Ahorro Activo ($):", min_value=1.0, value=100000.0, step=5000.0)
    porcentaje_ahorro = min(100, int((ahorro_p / meta_objetivo) * 100))
    st.progress(porcentaje_ahorro / 100, text=f"Rendimiento: {porcentaje_ahorro}% (${ahorro_p:,.0f} /${meta_objetivo:,.0f})")
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
        eg_monto = st.number_input("Monto ($)", value=float(fila_gp['monto']), format="%.2f")
        c_bt1, c_bt2 = st.columns(2)
        if c_bt1.form_submit_button("🔄 ACTUALIZAR"):
            cursor.execute("UPDATE gastos_personales SET descripcion=?, monto=? WHERE id=?", (eg_desc, eg_monto, sel_gp))
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
>>>>>>> c919b70 (Rediseño completo estilo Futurista Premium)
