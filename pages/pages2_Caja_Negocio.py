<<<<<<< HEAD
from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(
    page_title="Control de Caja Negocio", page_icon="🌿", layout="wide"
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
    CREATE TABLE IF NOT EXISTS transacciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT, categoria TEXT, monto REAL, descripcion TEXT, fecha TEXT
    )
"""
)
conn.commit()

st.title("💰 Control de Caja: Negocio de Prendas")
st.write("Administración de entradas y salidas de dinero.")

with st.form("form_caja", clear_on_submit=True):
  col1, col2 = st.columns(2)
  with col1:
    tipo = st.selectbox(
        "Tipo", ["Entrada (Venta/Cobro)", "Salida (Gasto/Deuda)"]
    )
    categoria = st.selectbox(
        "Categoría",
        [
            "Venta de Prendas",
            "Pago a Proveedor",
            "Alquiler y Servicios",
            "Envíos",
            "Otro",
        ],
    )
  with col2:
    monto = st.number_input("Monto ($)", min_value=0.0, format="%.2f", step=10.0)
  descripcion = st.text_area("Detalles")

  if st.form_submit_button("💾 Guardar en Caja"):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO transacciones (tipo, categoria, monto, descripcion, fecha)"
        " VALUES (?, ?, ?, ?, ?)",
        (tipo, categoria, monto, descripcion, fecha_actual),
    )
    conn.commit()
    st.success("¡Movimiento guardado con éxito!")
    st.rerun()

st.markdown("---")
st.subheader("📋 Historial de Caja")
df_caja_hist = pd.read_sql_query(
    "SELECT * FROM transacciones ORDER BY id DESC", conn
)

if not df_caja_hist.empty:
  st.dataframe(df_caja_hist, use_container_width=True)

  st.markdown("### ⚙️ ADMINISTRAR REGISTRO")
  ids_caja = df_caja_hist["id"].tolist()
  sel_caja = st.selectbox("Seleccione ID de Caja a administrar:", ids_caja)
  fila_caja = df_caja_hist[df_caja_hist["id"] == sel_caja].iloc[0]

  with st.form("form_edit_caja"):
    ec_desc = st.text_input("Detalles", value=fila_caja["descripcion"])
    ec_monto = st.number_input(
        "Monto ($)", value=float(fila_caja["monto"]), format="%.2f"
    )
    c_bc1, c_bc2 = st.columns(2)
    if c_bc1.form_submit_button("🔄 Actualizar Movimiento"):
      cursor.execute(
          "UPDATE transacciones SET descripcion=?, monto=? WHERE id=?",
          (ec_desc, ec_monto, sel_caja),
      )
      conn.commit()
      st.success("¡Actualizado con éxito!")
      st.rerun()
    if c_bc2.form_submit_button("🗑️ Borrar Movimiento"):
      cursor.execute("DELETE FROM transacciones WHERE id=?", (sel_caja,))
      conn.commit()
      st.success("¡Eliminado con éxito!")
      st.rerun()
else:
  st.info("Sin transacciones registradas en caja.")
=======
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Caja Negocio | PROYECTO X", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #071426; color: #E6EDF5; }
    section[data-testid="stSidebar"] { background-color: #0b1a2f !important; }
    .stButton>button {
        background: linear-gradient(135deg, #4388FF 0%, #2f6de0 100%) !important;
        color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #0d1b30 !important; color: #E6EDF5 !important; border: 1px solid #1E365D !important;
    }
    </style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal.")
    st.stop()

conn = sqlite3.connect("negocio_prendas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT, categoria TEXT, monto REAL, descripcion TEXT, fecha TEXT
    )
""")
conn.commit()

st.title("💰 CAJA DEL NEGOCIO")
st.caption("OPERACIONES DE FLUJO DE CAJA & TESORERÍA")

with st.form("form_caja", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox("Tipo de Movimiento", ["Entrada (Venta/Cobro)", "Salida (Gasto/Deuda)"])
        categoria = st.selectbox("Clasificación Operativa", ["Venta de Prendas", "Pago a Proveedor", "Alquiler y Servicios", "Envíos", "Otro"])
    with col2:
        monto = st.number_input("Monto Efectivo ($)", min_value=0.0, format="%.2f", step=100.0)
    descripcion = st.text_area("Concepto / Detalles Adicionales")

    if st.form_submit_button("⚡ ASENTAR EN LIBRO DE CAJA"):
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO transacciones (tipo, categoria, monto, descripcion, fecha) VALUES (?, ?, ?, ?, ?)",
                       (tipo, categoria, monto, descripcion, fecha_actual))
        conn.commit()
        st.success("Transacción confirmada en base de datos.")
        st.rerun()

st.markdown("---")
st.subheader("📋 Libro Mayor de Caja")
df_caja_hist = pd.read_sql_query("SELECT * FROM transacciones ORDER BY id DESC", conn)

if not df_caja_hist.empty:
    st.dataframe(df_caja_hist, use_container_width=True)
    st.markdown("### ⚙️ GESTIÓN DE ASIENTOS CONTABLES")
    sel_caja = st.selectbox("ID de Movimiento a Administrar:", df_caja_hist['id'].tolist())
    fila_caja = df_caja_hist[df_caja_hist['id'] == sel_caja].iloc[0]

    with st.form("form_edit_caja"):
        ec_desc = st.text_input("Detalles", value=fila_caja['descripcion'])
        ec_monto = st.number_input("Monto ($)", value=float(fila_caja['monto']), format="%.2f")
        c_bc1, c_bc2 = st.columns(2)
        if c_bc1.form_submit_button("🔄 ACTUALIZAR MOVIMIENTO"):
            cursor.execute("UPDATE transacciones SET descripcion=?, monto=? WHERE id=?", (ec_desc, ec_monto, sel_caja))
            conn.commit()
            st.success("Asiento contable actualizado.")
            st.rerun()
        if c_bc2.form_submit_button("🗑️ PURGAR ASIENTO"):
            cursor.execute("DELETE FROM transacciones WHERE id=?", (sel_caja,))
            conn.commit()
            st.success("Asiento eliminado.")
            st.rerun()
else:
    st.info("Sin operaciones registradas en el libro mayor.")
>>>>>>> c919b70 (Rediseño completo estilo Futurista Premium)
