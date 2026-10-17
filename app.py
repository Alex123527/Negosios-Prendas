from datetime import datetime
import io
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(
    page_title="PROYECTO X - Sistema Futurista", page_icon="⚡", layout="wide"
)

# Selector de Tema / Paleta de Colores en la barra lateral
st.sidebar.markdown(
    "<h3 style='color: #00ffcc; text-shadow: 0 0 10px rgba(0,255,204,0.5);'>"
    "⚡ PROYECTO X</h3>",
    unsafe_allow_html=True,
)
estilo_visual = st.sidebar.selectbox(
    "🎨 Paleta Futurista / Tema",
    [
        "Cyberpunk Neón (Oscuro & Cyan)",
        "Matrix Dark (Negro & Verde Esmeralda)",
        "Minimalista Titanio (Plata & Azul)",
    ],
)

# Definición de estilos CSS según el tema elegido
if estilo_visual == "Cyberpunk Neón (Oscuro & Cyan)":
  bg_color = "#080c14"
  card_bg = "#111827"
  text_color = "#f3f4f6"
  accent_color = "#00ffcc"
  secondary_accent = "#ff007f"
elif estilo_visual == "Matrix Dark (Negro & Verde Esmeralda)":
  bg_color = "#020403"
  card_bg = "#0c1713"
  text_color = "#e6f4ea"
  accent_color = "#00e676"
  secondary_accent = "#00b0ff"
else:  # Minimalista Titanio
  bg_color = "#0f172a"
  card_bg = "#1e293b"
  text_color = "#f8fafc"
  accent_color = "#38bdf8"
  secondary_accent = "#818cf8"

st.markdown(
    f"""
    <style>
    .main {{ background-color: {bg_color}; color: {text_color}; }}
    h1, h2, h3 {{ color: {accent_color} !important; font-family: 'Segoe UI', Roboto, sans-serif; text-shadow: 0 0 12px rgba(0,255,204,0.2); }}
    .stButton>button {{
        background: linear-gradient(135deg, {accent_color}, {secondary_accent});
        color: #000000;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
        box-shadow: 0 0 10px rgba(0,255,204,0.3);
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        opacity: 0.85;
        box-shadow: 0 0 20px rgba(0,255,204,0.6);
    }}
    </style>
""",
    unsafe_allow_html=True,
)

if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
  st.markdown(
      f"<h2 style='text-align: center; color: {accent_color};'>PROYECTO X -"
      " Acceso Seguro</h2>",
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

menu = st.sidebar.selectbox(
    "Menú Principal",
    [
        "Control de Gastos Personales",
        "Registrar Movimiento (Caja Negocio)",
        "PRECIOS Y CONTROL DE PEDIDOS",
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
  st.write("Gestión inteligente y automatizada de finanzas.")

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
  m1.metric("💰 INGRESOS", f"${total_ingresos_p:,.0f}")
  m2.metric("🛒 GASTOS", f"${total_gastos_p:,.0f}")
  m3.metric("🐖 AHORRO", f"${ahorro_p:,.0f}")

  st.markdown("---")
  with st.form("form_gasto_personal", clear_on_submit=True):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
      fecha_gasto = st.date_input("Fecha", value=datetime.now())
      descripcion_gasto = st.text_input("Descripción")
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
      st.success("¡Gasto registrado!")
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
    st.info("Sin registros de gastos.")

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
    st.info("Sin transacciones registradas.")

elif menu == "PRECIOS Y CONTROL DE PEDIDOS":
  st.title("🏷️ PRECIOS Y CONTROL DE PEDIDOS")
  st.write(
      "Sistema integrado de cálculo de precios, inventario y flujo de pedidos."
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
    st.markdown(
        f"<h3 style='color: {accent_color}; text-shadow: 0 0 10px rgba(0,255,204,0.3);'>💵 PRECIO DE VENTA CALCULADO:"
        f" ${precio_venta_sugerido:,.2f}</h3>",
        unsafe_allow_html=True,
    )

    if st.form_submit_button("💾 Guardar Nuevo Pedido / Prenda"):
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
      st.success("¡Registro guardado exitosamente!")
      st.rerun()

  st.markdown("---")
  st.subheader("📋 Registro General de Pedidos y Precios")

  df_unificado = pd.read_sql_query(
      "SELECT * FROM pedidos_inventario ORDER BY id DESC", conn
  )

  if not df_unificado.empty:
    st.dataframe(df_unificado, use_container_width=True)

    st.markdown("### ⚙️ ADMINISTRAR REGISTRO")
    ids_disponibles = df_unificado["id"].tolist()
    id_seleccionado = st.selectbox(
        "Seleccione ID de Pedido/Prenda a administrar:", ids_disponibles
    )
    fila_sel = df_unificado[df_unificado["id"] == id_seleccionado].iloc[0]

    with st.form("form_editar_pedido"):
      e_cliente = st.text_input("Cliente", value=fila_sel["cliente"])
      e_modelo = st.text_input(
          "Modelo de Prenda", value=fila_sel["modelo_prenda"]
      )
      e_costo = st.number_input(
          "Costo Unitario ($)",
          min_value=0.0,
          value=float(fila_sel["costo"]),
          format="%.2f",
      )
      e_margen = st.number_input(
          "Margen de Ganancia (%)",
          min_value=0.0,
          value=float(fila_sel["margen_ganancia"]),
      )
      e_estado = st.selectbox(
          "Estado del Pedido",
          ["Pendiente", "Confirmado", "Entregado", "Cancelado"],
      )

      nuevo_precio_calc = e_costo + (e_costo * (e_margen / 100))
      st.info(f"💡 Nuevo Precio Calculado: ${nuevo_precio_calc:,.2f}")

      col_b1, col_b2 = st.columns(2)
      if col_b1.form_submit_button("🔄 Actualizar Registro"):
        cursor.execute(
            """
                UPDATE pedidos_inventario 
                SET cliente=?, modelo_prenda=?, costo=?, margen_ganancia=?, precio_venta=?, estado=?
                WHERE id=?
            """,
            (
                e_cliente,
                e_modelo,
                e_costo,
                e_margen,
                nuevo_precio_calc,
                e_estado,
                id_seleccionado,
            ),
        )
        conn.commit()
        st.success("¡Registro actualizado!")
        st.rerun()

      if col_b2.form_submit_button("🗑️ Borrar Registro"):
        cursor.execute(
            "DELETE FROM pedidos_inventario WHERE id=?", (id_seleccionado,)
        )
        conn.commit()
        st.success("¡Registro eliminado!")
        st.rerun()
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
      st.rerun()

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
      ed_estado = st.selectbox(
          "Estado", ["Pendiente de Pago", "Pagado Total"]
      )
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

elif menu == "Gráficos y Finanzas":
  st.title("📊 Análisis Financiero Global")
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
      st.subheader("Gráfico de Movimientos")
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