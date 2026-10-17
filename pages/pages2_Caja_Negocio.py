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