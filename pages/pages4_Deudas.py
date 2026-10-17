<<<<<<< HEAD
from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(
    page_title="Gestión de Deudas (Fiados)", page_icon="🌿", layout="wide"
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
    CREATE TABLE IF NOT EXISTS deudas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT, concepto TEXT, monto_deuda REAL, estado TEXT, fecha TEXT
    )
"""
)
conn.commit()

st.title("🤝 Control de Cuentas Corrientes (Fiados)")
st.write("Gestión de créditos y cuentas pendientes de clientes.")

with st.form("form_deuda", clear_on_submit=True):
  col1, col2 = st.columns(2)
  with col1:
    cliente_deudor = st.text_input("Cliente Deudor")
    concepto = st.text_input("Concepto")
  with col2:
    monto_deuda = st.number_input("Monto Pendiente ($)", min_value=0.0)
    estado_deuda = st.selectbox("Estado", ["Pendiente de Pago", "Pagado Total"])

  if st.form_submit_button("💾 Registrar Deuda"):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO deudas (cliente, concepto, monto_deuda, estado, fecha)"
        " VALUES (?, ?, ?, ?, ?)",
        (cliente_deudor, concepto, monto_deuda, estado_deuda, fecha_actual),
    )
    conn.commit()
    st.success("¡Deuda registrada con éxito!")
    st.rerun()

st.markdown("---")
st.subheader("📋 Registro de Deudas")
df_deudas = pd.read_sql_query("SELECT * FROM deudas ORDER BY id DESC", conn)

if not df_deudas.empty:
  st.dataframe(df_deudas, use_container_width=True)

  st.markdown("### ⚙️ ADMINISTRAR REGISTRO")
  ids_deuda = df_deudas["id"].tolist()
  sel_deuda = st.selectbox("Seleccione ID de Deuda a administrar:", ids_deuda)
  fila_deuda = df_deudas[df_deudas["id"] == sel_deuda].iloc[0]

  with st.form("form_edit_deuda"):
    ed_monto = st.number_input(
        "Monto ($)", value=float(fila_deuda["monto_deuda"]), format="%.2f"
    )
    ed_estado = st.selectbox("Estado", ["Pendiente de Pago", "Pagado Total"])
    c_bd1, c_bd2 = st.columns(2)
    if c_bd1.form_submit_button("🔄 Actualizar Deuda"):
      cursor.execute(
          "UPDATE deudas SET monto_deuda=?, estado=? WHERE id=?",
          (ed_monto, ed_estado, sel_deuda),
      )
      conn.commit()
      st.success("¡Actualizado con éxito!")
      st.rerun()
    if c_bd2.form_submit_button("🗑️ Borrar Deuda"):
      cursor.execute("DELETE FROM deudas WHERE id=?", (sel_deuda,))
      conn.commit()
      st.success("¡Eliminado con éxito!")
      st.rerun()
else:
  st.info("Sin deudas registradas.")
=======
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestión de Deudas | PROYECTO X", page_icon="⚡", layout="wide")

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
    CREATE TABLE IF NOT EXISTS deudas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT, concepto TEXT, monto_deuda REAL, estado TEXT, fecha TEXT
    )
""")
conn.commit()

st.title("🤝 CONTROL DE CUENTAS CORRIENTES")
st.caption("CREDIT MANAGEMENT & PENDING BALANCES")

with st.form("form_deuda", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        cliente_deudor = st.text_input("Titular de la Cuenta")
        concepto = st.text_input("Concepto / Prenda Fiada")
    with col2:
        monto_deuda = st.number_input("Saldo Pendiente ($)", min_value=0.0, format="%.2f")
        estado_deuda = st.selectbox("Estado Contable", ["Pendiente de Pago", "Pagado Total"])

    if st.form_submit_button("⚡ ASENTAR DEUDA"):
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO deudas (cliente, concepto, monto_deuda, estado, fecha) VALUES (?, ?, ?, ?, ?)",
                       (cliente_deudor, concepto, monto_deuda, estado_deuda, fecha_actual))
        conn.commit()
        st.success("Crédito registrado exitosamente.")
        st.rerun()

st.markdown("---")
st.subheader("📋 Libro de Deudas y Fiados")
df_deudas = pd.read_sql_query("SELECT * FROM deudas ORDER BY id DESC", conn)

if not df_deudas.empty:
    st.dataframe(df_deudas, use_container_width=True)
    st.markdown("### ⚙️ ADMINISTRACIÓN DE CRÉDITOS")
    sel_deuda = st.selectbox("ID de Deuda:", df_deudas['id'].tolist())
    fila_deuda = df_deudas[df_deudas['id'] == sel_deuda].iloc[0]

    with st.form("form_edit_deuda"):
        ed_monto = st.number_input("Saldo ($)", value=float(fila_deuda['monto_deuda']), format="%.2f")
        ed_estado = st.selectbox("Estado", ["Pendiente de Pago", "Pagado Total"])
        c_bd1, c_bd2 = st.columns(2)
        if c_bd1.form_submit_button("🔄 ACTUALIZAR"):
            cursor.execute("UPDATE deudas SET monto_deuda=?, estado=? WHERE id=?", (ed_monto, ed_estado, sel_deuda))
            conn.commit()
            st.success("Estado de crédito actualizado.")
            st.rerun()
        if c_bd2.form_submit_button("🗑️ PURGAR DEUDA"):
            cursor.execute("DELETE FROM deudas WHERE id=?", (sel_deuda,))
            conn.commit()
            st.success("Registro purgado.")
            st.rerun()
else:
    st.info("Sin registros de deudas vigentes.")
>>>>>>> c919b70 (Rediseño completo estilo Futurista Premium)
