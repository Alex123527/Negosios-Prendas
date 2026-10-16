from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(
    page_title="PROYECTO X - Sistema de Gestión y Gastos",
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
    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT, categoria TEXT, talla TEXT, costo REAL, porcentaje_ganancia REAL, precio_venta REAL, stock INTEGER, fecha TEXT
    )
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT, prenda TEXT, cantidad INTEGER, estado TEXT, tipo_venta TEXT, fecha TEXT
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
        "Calculadora y Precios",
        "Control de Pedidos",
        "Gestión de Deudas (Fiados)",
        "Gráficos y Finanzas",
        "Exportar Reportes (PDF)",
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

      btn_guardar_gasto = st.form_submit_button(
          "💾 Guardar Gasto en Planilla"
      )

      if btn_guardar_gasto:
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
      st.markdown(
          f"<h4 style='text-align: right; background-color: #2e7d32;"
          f" padding: 10px; border-radius: 5px;'>TOTAL GASTOS: ${total_gastos_p:,.2f}</h4>",
          unsafe_allow_html=True,
      )
    else:
      st.info("Aún no hay gastos registrados en la planilla.")

  with col_der:
    st.subheader("🏷️ Categorías")
    categorias_lista = [
        ("🏠 Vivienda", "Vivienda"),
        ("🛒 Comida", "Comida"),
        ("🚗 Transporte", "Transporte"),
        ("💡 Servicios", "Servicios"),
        ("🎟️ Ocio", "Ocio"),
        ("❤️ Salud", "Salud"),
        ("📚 Estudios", "Estudios"),
        ("🟢 Otros", "Otros"),
    ]

    for label_cat, cat_nombre in categorias_lista:
      df_cat = pd.read_sql_query(
          "SELECT SUM(monto) as total FROM gastos_personales WHERE categoria = ?",
          conn,
          params=(cat_nombre,),
      )
      tot_cat = (
          df_cat["total"].iloc[0]
          if not df_cat.empty and df_cat["total"].iloc[0] is not None
          else 0.0
      )
      st.write(f"**{label_cat}**: ${tot_cat:,.0f}")

    st.markdown("---")
    st.subheader("📝 Notas del Mes")
    st.text_input("Nota 1", value="Reducir gastos de kiosco")
    st.text_input("Nota 2", value="Ahorrar 5% más")
    st.text_input("Nota 3", value="")

  st.markdown("---")

  col_inf1, col_inf2 = st.columns(2)
  with col_inf1:
    st.subheader("📊 Resumen del Mes")
    st.write(f"• Ingresos totales: **${total_ingresos_p:,.2f}**")
    st.write(f"• Gastos totales: **${total_gastos_p:,.2f}**")
    st.write(f"• Ahorro neto: **${ahorro_p:,.2f}**")

  with col_inf2:
    st.subheader("🎯 Meta de Ahorro")
    objetivo_ahorro = st.number_input(
        "Mi objetivo de ahorro este mes ($):",
        min_value=1.0,
        value=100000.0,
        step=10000.0,
    )
    porcentaje_meta = min(
        100.0, (ahorro_p / objetivo_ahorro) * 100 if objetivo_ahorro > 0 else 0
    )
    st.progress(int(porcentaje_meta))
    st.write(f"¡Vas al **{porcentaje_meta:.1f}%** de tu objetivo! 💚")

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
      st.success("¡Movimiento guardado!")

elif menu == "Calculadora y Precios":
  st.title("🏷️ Planilla de Precios y Margen Automático")
  with st.form("form_prendas", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      nombre_prenda = st.text_input("Modelo de Prenda")
      cat_prenda = st.selectbox(
          "Categoría",
          [
              "Remeras y Tops",
              "Pantalones y Jeans",
              "Abrigos y Camperas",
              "Calzados",
              "Accesorios",
          ],
      )
      talla = st.selectbox("Talle", ["XS", "S", "M", "L", "XL", "Único"])
    with col2:
      costo = st.number_input("Costo ($)", min_value=0.0, format="%.2f")
      porcentaje = st.number_input(
          "Margen Ganancia (%)", min_value=0.0, value=50.0
      )
      stock_inicial = st.number_input("Stock Inicial", min_value=1, value=1)
    precio_sugerido = costo + (costo * (porcentaje / 100))
    st.info(f"💡 Precio Sugerido: **${precio_sugerido:,.2f}**")
    if st.form_submit_button("💾 Guardar Prenda"):
      fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      cursor.execute(
          "INSERT INTO inventario (nombre, categoria, talla, costo,"
          " porcentaje_ganancia, precio_venta, stock, fecha) VALUES (?, ?, ?,"
          " ?, ?, ?, ?, ?)",
          (
              nombre_prenda,
              cat_prenda,
              talla,
              costo,
              porcentaje,
              precio_sugerido,
              stock_inicial,
              fecha_actual,
          ),
      )
      conn.commit()
      st.success("¡Prenda guardada!")
  df_inv = pd.read_sql_query("SELECT * FROM inventario ORDER BY id DESC", conn)
  if not df_inv.empty:
    st.dataframe(df_inv, use_container_width=True)

elif menu == "Control de Pedidos":
  st.title("📋 Gestión de Pedidos")
  with st.form("form_pedido", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      cliente = st.text_input("Cliente")
      prenda = st.text_input("Prenda")
      cantidad = st.number_input("Cantidad", min_value=1, value=1)
    with col2:
      tipo_venta = st.selectbox("Canal", ["Online (Redes)", "Físico"])
      estado = st.selectbox(
          "Estado", ["Pendiente", "Confirmado", "Entregado", "Cancelado"]
      )
    if st.form_submit_button("📥 Registrar Pedido"):
      fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      cursor.execute(
          "INSERT INTO pedidos (cliente, prenda, cantidad, estado, tipo_venta,"
          " fecha) VALUES (?, ?, ?, ?, ?, ?)",
          (cliente, prenda, cantidad, estado, tipo_venta, fecha_actual),
      )
      conn.commit()
      st.success("¡Pedido registrado!")
  df_pedidos = pd.read_sql_query("SELECT * FROM pedidos ORDER BY id DESC", conn)
  if not df_pedidos.empty:
    st.dataframe(df_pedidos, use_container_width=True)

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
  st.title("📊 Análisis Financiero Global")
  df = pd.read_sql_query(
      "SELECT * FROM transacciones ORDER BY id DESC", conn
  )
  if not df.empty:
    entradas = df[df["tipo"] == "Entrada (Venta/Cobro)"]["monto"].sum()
    salidas = df[df["tipo"] == "Salida (Gasto/Deuda)"]["monto"].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Entradas", f"${entradas:,.2f}")
    c2.metric("Salidas", f"${salidas:,.2f}")
    c3.metric("Balance", f"${entradas - salidas:,.2f}")
    st.bar_chart(df.groupby("tipo")["monto"].sum())
  else:
    st.info("Sin movimientos financieros registrados.")

elif menu == "Exportar Reportes (PDF)":
  st.title("📄 Generador de Reportes PDF")
  df = pd.read_sql_query("SELECT * FROM transacciones", conn)
  if not df.empty and st.button("Generar PDF de Caja"):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    p.drawString(50, height - 50, "PROYECTO X - Reporte Financiero")
    y = height - 90
    for idx, row in df.iterrows():
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
        file_name="reporte.pdf",
        mime="application/pdf",
    )
  else:
    st.warning("No hay suficientes datos para exportar.")