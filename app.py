from datetime import datetime
import io
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(
    page_title="PROYECTO X - Sistema de Gestión Integral",
    page_icon="🛍️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #f0f2f6; font-family: 'Segoe UI', sans-serif; }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #1b5e20; }
    </style>
""",
    unsafe_allow_html=True,
)

if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
  st.markdown(
      "<h2 style='text-align: center; color: #2e7d32;'>PROYECTO X - Acceso"
      " Seguro</h2>",
      unsafe_allow_html=True,
  )
  col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
  with col_l2:
    correo_ingresado = st.text_input("Correo Electrónico")
    password_ingresada = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión", use_container_width=True):
      if (
          correo_ingresado.strip().lower() == "ozunaramon22@gmail.com"
          and password_ingresada == "123456"
      ):
        st.session_state["autenticado"] = True
        st.rerun()
      else:
        st.error("Correo o contraseña incorrectos.")
  st.stop()

conn = sqlite3.connect("negocio_prendas.db", check_same_thread=False)
cursor = conn.cursor()

# Tablas actualizadas e integradas
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
    CREATE TABLE IF NOT EXISTS deudas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT, concepto TEXT, monto_deuda REAL, estado TEXT, fecha TEXT
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
conn.commit()

st.sidebar.markdown(
    "<h3 style='color: #2e7d32;'>🛍️ PROYECTO X</h3>", unsafe_allow_html=True
)
menu = st.sidebar.selectbox(
    "Menú Principal",
    [
        "Control de Gastos Personales",
        "Registrar Movimiento (Caja Negocio)",
        "Gestión de Pedidos y Precios",
        "Gestión de Deudas (Fiados)",
        "Gráficos y Finanzas",
        "Exportar Reportes (PDF / Excel)",
    ],
)

if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
  st.session_state["autenticado"] = False
  st.rerun()

if menu == "Control de Gastos Personales":
  st.title("🌿 Control de Gastos Personales")
  st.write("Organizá • Controlá • Ahorrá")

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
      "SELECT SUM(monto) as total FROM transacciones WHERE tipo='Entrada (Venta/Cobro)'",
      conn,
  )
  total_ingresos_p = (
      df_caja_ing["total"].iloc[0]
      if not df_caja_ing.empty
      and df_caja_ing["total"].iloc[0] is not None
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
        descripcion_gasto = st.text_input(
            "Descripción (Ej. Supermercado, Luz)"
        )
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
            "Cargar Factura o Transferencia (Imagen/PDF)",
            type=["png", "jpg", "jpeg", "pdf"],
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
        st.success("¡Gasto registrado correctamente!")
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Planilla de Movimientos del Mes")
    df_gp = pd.read_sql_query(
        "SELECT id, fecha, descripcion, categoria, metodo_pago, monto, comprobante_nombre FROM gastos_personales ORDER BY id DESC",
        conn,
    )
    if not df_gp.empty:
      st.dataframe(df_gp, use_container_width=True)
    else:
      st.info("Aún no hay gastos registrados.")

  with col_der:
    st.subheader("🏷️ Categorías")
    for cat in [
        "Vivienda",
        "Comida",
        "Transporte",
        "Servicios",
        "Ocio",
        "Salud",
        "Estudios",
        "Otros",
    ]:
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

elif menu == "Registrar Movimiento (Caja Negocio)":
  st.title("💰 Control de Caja: Negocio de Prendas")
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
      monto = st.number_input(
          "Monto ($)", min_value=0.0, format="%.2f", step=10.0
      )
    descripcion = st.text_area("Detalles")
    if st.form_submit_button("💾 Guardar en Caja"):
      fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      cursor.execute(
          "INSERT INTO transacciones (tipo, categoria, monto, descripcion, fecha)"
          " VALUES (?, ?, ?, ?, ?)",
          (tipo, categoria, monto, descripcion, fecha_actual),
      )
      conn.commit()
      st.success("¡Movimiento guardado en caja!")

  st.markdown("---")
  st.subheader("📋 Historial de Caja")
  df_caja_hist = pd.read_sql_query(
      "SELECT * FROM transacciones ORDER BY id DESC", conn
  )
  if not df_caja_hist.empty:
    st.dataframe(df_caja_hist, use_container_width=True)

elif menu == "Gestión de Pedidos y Precios":
  st.title("🏷️📋 Panel Unificado: Precios y Control de Pedidos")
  st.write(
      "Administra tus prendas, márgenes, stock y pedidos en un solo flujo."
  )

  with st.form("form_pedidos_precios", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
      cliente = st.text_input("Cliente")
      modelo_prenda = st.text_input("Modelo de Prenda")
      categoria = st.selectbox(
          "Categoría",
          [
              "Remeras y Tops",
              "Pantalones y Jeans",
              "Abrigos y Camperas",
              "Calzados",
              "Accesorios",
          ],
      )
    with c2:
      talle = st.selectbox("Talle", ["XS", "S", "M", "L", "XL", "Único"])
      cantidad = st.number_input("Cantidad", min_value=1, value=1)
      costo = st.number_input("Costo Unitario ($)", min_value=0.0, format="%.2f")
    with c3:
      margen_ganancia = st.number_input(
          "Margen de Ganancia (%)", min_value=0.0, value=50.0
      )
      stock_inicial = st.number_input("Stock Inicial", min_value=0, value=1)
      canal = st.selectbox("Canal de Venta", ["Online (Redes)", "Físico"])
      estado = st.selectbox(
          "Estado del Pedido",
          ["Pendiente", "Confirmado", "Entregado", "Cancelado"],
      )

    precio_venta_sugerido = costo + (costo * (margen_ganancia / 100))
    st.info(
        f"💡 Precio de Venta Sugerido: **${precio_venta_sugerido:,.2f}** por unidad"
    )

    if st.form_submit_button("💾 Guardar Pedido y Prenda"):
      fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      cursor.execute(
          """
                INSERT INTO pedidos_inventario 
                (cliente, modelo_prenda, categoria, talle, cantidad, costo, margen_ganancia, precio_venta, stock_inicial, canal, estado, fecha)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
          (
              cliente,
              modelo_prenda,
              categoria,
              talle,
              cantidad,
              costo,
              margen_ganancia,
              precio_venta_sugerido,
              stock_inicial,
              canal,
              estado,
              fecha_actual,
          ),
      )
      conn.commit()
      st.success("¡Registro unificado guardado exitosamente!")

  st.markdown("---")
  st.subheader("📋 Registro General de Pedidos y Precios")
  df_unificado = pd.read_sql_query(
      "SELECT * FROM pedidos_inventario ORDER BY id DESC", conn
  )
  if not df_unificado.empty:
    st.dataframe(df_unificado, use_container_width=True)
  else:
    st.info("Aún no hay registros en este módulo.")

elif menu == "Gestión de Deudas (Fiados)":
  st.title("🤝 Control de Cuentas Corrientes (Fiados)")
  with st.form("form_deuda", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      cliente_deudor = st.text_input("Cliente Deudor")
      concepto = st.text_input("Concepto")
    with col2:
      monto_deuda = st.number_input("Monto Pendiente ($)", min_value=0.0)
      estado_deuda = st.selectbox(
          "Estado", ["Pendiente de Pago", "Pagado Total"]
      )
    if st.form_submit_button("💾 Registrar Deuda"):
      fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      cursor.execute(
          "INSERT INTO deudas (cliente, concepto, monto_deuda, estado, fecha)"
          " VALUES (?, ?, ?, ?, ?)",
          (
              cliente_deudor,
              concepto,
              monto_deuda,
              estado_deuda,
              fecha_actual,
          ),
      )
      conn.commit()
      st.success("¡Deuda registrada!")
  df_deudas = pd.read_sql_query("SELECT * FROM deudas ORDER BY id DESC", conn)
  if not df_deudas.empty:
    st.dataframe(df_deudas, use_container_width=True)

elif menu == "Gráficos y Finanzas":
  st.title("📊 Análisis Financiero Global del Negocio")
  df_trans = pd.read_sql_query(
      "SELECT * FROM transacciones ORDER BY id DESC", conn
  )
  df_pedidos_fin = pd.read_sql_query(
      "SELECT * FROM pedidos_inventario", conn
  )

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

    # Ingresos estimados por pedidos registrados
    ventas_estimadas = (
        (
            df_pedidos_fin["cantidad"] * df_pedidos_fin["precio_venta"]
        ).sum()
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
      st.subheader("Gráfico de Movimientos de Caja")
      st.bar_chart(df_trans.groupby("tipo")["monto"].sum())
  else:
    st.info("Sin datos financieros suficientes para graficar.")

elif menu == "Exportar Reportes (PDF / Excel)":
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
    st.write(
        "Descarga tus bases de datos completas en formato Excel (.xlsx) con"
        " un solo clic."
    )
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