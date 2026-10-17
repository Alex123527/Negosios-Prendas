<<<<<<< HEAD

from datetime import datetime
import io
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(page_title="Gráficos y Finanzas", page_icon="🌿", layout="wide")

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
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS pedidos_inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT, modelo_prenda TEXT, categoria TEXT, talle TEXT, 
        cantidad INTEGER, costo REAL, margen_ganancia REAL, precio_venta REAL, 
        stock_inicial INTEGER, canal TEXT, estado TEXT, fecha TEXT
    )
"""
)
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
    CREATE TABLE IF NOT EXISTS deudas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT, concepto TEXT, monto_deuda REAL, estado TEXT, fecha TEXT
    )
"""
)
conn.commit()

st.title("📊 Análisis Financiero Global")
st.write(
    "Resumen general de entradas, salidas, balance y exportación de reportes."
)

df_trans = pd.read_sql_query(
    "SELECT * FROM transacciones ORDER BY id DESC", conn
)
df_pedidos_fin = pd.read_sql_query("SELECT * FROM pedidos_inventario", conn)

if not df_trans.empty or not df_pedidos_fin.empty:
  entradas = (
      df_trans[df_trans["tipo"] == "Entrada (Venta/Cobro)"]["monto"].sum()
      if not df_trans.empty
      else 0.0
  )
  salidas = (
      df_trans[df_trans["tipo"] == "Salida (Gasto/Deuda)"]["monto"].sum()
      if not df_trans.empty
      else 0.0
  )
  ventas_estimadas = (
      (df_pedidos_fin["cantidad"] * df_pedidos_fin["precio_venta"]).sum()
      if not df_pedidos_fin.empty
      else 0.0
  )

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("📥 Entradas Caja", f"${entradas:,.2f}")
  c2.metric("📤 Salidas Caja", f"${salidas:,.2f}")
  c3.metric("🛍️ Ventas Catálogo", f"${ventas_estimadas:,.2f}")
  c4.metric("⚖️ Balance Neto", f"${entradas - salidas:,.2f}")

  st.markdown("---")
  if not df_trans.empty:
    st.subheader("Gráfico de Movimientos")
    st.bar_chart(df_trans.groupby("tipo")["monto"].sum())
else:
  st.info("Sin datos financieros suficientes para graficar.")

st.markdown("---")
st.title("📄 Exportar Reportes (PDF y Excel)")
tab_pdf, tab_excel = st.tabs(["📄 Reporte PDF", "📊 Exportar a Excel"])

with tab_pdf:
  df_rep = pd.read_sql_query("SELECT * FROM transacciones", conn)
  if not df_rep.empty and st.button("Generar PDF de Transacciones"):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    p.drawString(
        50, height - 50, "PROYECTO X - Reporte Financiero de Transacciones"
    )
    y = height - 90
    for idx, row in df_rep.iterrows():
      p.drawString(
          50,
          y,
          f"{row['tipo']} | {row['categoria']} | ${row['monto']} |"
          f" {row['fecha']}",
      )
      y -= 20
      if y < 50:
        p.showPage()
        y = height - 50
    p.save()
    buffer.seek(0)
    st.download_button(
        "⬇️ Descargar Reporte PDF",
        data=buffer,
        file_name="reporte_financiero.pdf",
        mime="application/pdf",
    )
  else:
    st.warning("No hay transacciones registradas para exportar a PDF.")

with tab_excel:
  st.write("Descarga tus bases de datos completas en Excel (.xlsx).")
  if st.button("📥 Generar Archivo Excel"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
      pd.read_sql_query("SELECT * FROM transacciones", conn).to_excel(
          writer, index=False, sheet_name="Caja Negocio"
      )
      pd.read_sql_query("SELECT * FROM pedidos_inventario", conn).to_excel(
          writer, index=False, sheet_name="Pedidos e Inventario"
      )
      pd.read_sql_query("SELECT * FROM gastos_personales", conn).to_excel(
          writer, index=False, sheet_name="Gastos Personales"
      )
      pd.read_sql_query("SELECT * FROM deudas", conn).to_excel(
          writer, index=False, sheet_name="Deudas y Fiados"
      )
    output.seek(0)
    st.download_button(
        label="⬇️ Descargar Excel Completo (PROYECTO X)",
        data=output,
        file_name="ProyectoX_Reporte_Completo.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
=======

import streamlit as st
import sqlite3
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import openpyxl

st.set_page_config(page_title="Analítica Financiera | PROYECTO X", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #071426; color: #E6EDF5; }
    section[data-testid="stSidebar"] { background-color: #0b1a2f !important; }
    [data-testid="stMetricValue"] { color: #21D4C4 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #9FB2C8 !important; }
    .stButton>button {
        background: linear-gradient(135deg, #4388FF 0%, #2f6de0 100%) !important;
        color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal.")
    st.stop()

conn = sqlite3.connect("negocio_prendas.db", check_same_thread=False)
cursor = conn.cursor()

# Verificación de integridad de tablas
cursor.execute("CREATE TABLE IF NOT EXISTS transacciones (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, categoria TEXT, monto REAL, descripcion TEXT, fecha TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS pedidos_inventario (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, modelo_prenda TEXT, categoria TEXT, talle TEXT, cantidad INTEGER, costo REAL, margen_ganancia REAL, precio_venta REAL, stock_inicial INTEGER, canal TEXT, estado TEXT, fecha TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS gastos_personales (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, descripcion TEXT, categoria TEXT, metodo_pago TEXT, monto REAL, comprobante_nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS deudas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, concepto TEXT, monto_deuda REAL, estado TEXT, fecha TEXT)")
conn.commit()

st.title("📊 ANALÍTICA FINANCIERA & REPORTES")
st.caption("INTELLIGENCE ENGINE & GLOBAL DATA EXPORT")

df_trans = pd.read_sql_query("SELECT * FROM transacciones ORDER BY id DESC", conn)
df_pedidos_fin = pd.read_sql_query("SELECT * FROM pedidos_inventario", conn)

if not df_trans.empty or not df_pedidos_fin.empty:
    entradas = df_trans[df_trans['tipo'] == 'Entrada (Venta/Cobro)']['monto'].sum() if not df_trans.empty else 0.0
    salidas = df_trans[df_trans['tipo'] == 'Salida (Gasto/Deuda)']['monto'].sum() if not df_trans.empty else 0.0
    ventas_estimadas = (df_pedidos_fin['cantidad'] * df_pedidos_fin['precio_venta']).sum() if not df_pedidos_fin.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📥 ENTRADAS CAJA", f"${entradas:,.2f}")
    c2.metric("📤 SALIDAS CAJA", f"${salidas:,.2f}")
    c3.metric("🛍️ VENTAS CATÁLOGO", f"${ventas_estimadas:,.2f}")
    c4.metric("⚖️ BALANCE NETO", f"${entradas - salidas:,.2f}")

    st.markdown("---")
    if not df_trans.empty:
        st.subheader("📈 Flujo de Caja por Tipo")
        st.bar_chart(df_trans.groupby("tipo")["monto"].sum(), color="#9670FF")
else:
    st.info("Sin registros suficientes para graficar.")

st.markdown("---")
st.subheader("📄 Exportación de Informes Ejecutivos")
tab_pdf, tab_excel = st.tabs(["📄 Exportar PDF", "📊 Exportar Excel"])

with tab_pdf:
    df_rep = pd.read_sql_query("SELECT * FROM transacciones", conn)
    if not df_rep.empty and st.button("⚡ GENERAR REPORTE PDF"):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        p.drawString(50, height - 50, "PROYECTO X - INFORME FINANCIERO DE OPERACIONES")
        y = height - 90
        for idx, row in df_rep.iterrows():
            p.drawString(50, y, f"{row['tipo']} | {row['categoria']} | ${row['monto']} | {row['fecha']}")
            y -= 20
            if y < 50:
                p.showPage()
                y = height - 50
        p.save()
        buffer.seek(0)
        st.download_button("⬇️ Descargar Reporte PDF", data=buffer, file_name="reporte_financiero.pdf", mime="application/pdf")
    else:
        st.warning("No hay transacciones registradas para compilar en PDF.")

with tab_excel:
    st.caption("Extracción integral de todas las entidades en libro Excel (.xlsx).")
    if st.button("⚡ GENERAR LIBRO EXCEL MULTIHOJA"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.read_sql_query("SELECT * FROM transacciones", conn).to_excel(writer, index=False, sheet_name="Caja Negocio")
            pd.read_sql_query("SELECT * FROM pedidos_inventario", conn).to_excel(writer, index=False, sheet_name="Pedidos e Inventario")
            pd.read_sql_query("SELECT * FROM gastos_personales", conn).to_excel(writer, index=False, sheet_name="Gastos Personales")
            pd.read_sql_query("SELECT * FROM deudas", conn).to_excel(writer, index=False, sheet_name="Deudas y Fiados")
        output.seek(0)
        st.download_button(
            label="⬇️ Descargar Libro Contable Completo",
            data=output,
            file_name="ProyectoX_Reporte_Completo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
>>>>>>> c919b70 (Rediseño completo estilo Futurista Premium)
