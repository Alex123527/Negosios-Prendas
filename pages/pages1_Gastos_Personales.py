from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(
    page_title="Control de Gastos Personales", page_icon="🌿", layout="wide"
)

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
conn.commit()

st.title("🌿 Control de Gastos Personales")
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

  if st.form_submit_button("💾 Guardar Gasto"):
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

st.markdown("---")
st.subheader("📋 Planilla de Gastos")
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