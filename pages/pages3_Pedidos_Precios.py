<<<<<<< HEAD
from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(
    page_title="Precios y Control de Pedidos", page_icon="🌿", layout="wide"
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
    CREATE TABLE IF NOT EXISTS pedidos_inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT, modelo_prenda TEXT, categoria TEXT, talle TEXT, 
        cantidad INTEGER, costo REAL, margen_ganancia REAL, precio_venta REAL, 
        stock_inicial INTEGER, canal TEXT, estado TEXT, fecha TEXT
    )
"""
)
conn.commit()

st.title("🏷️ PRECIOS Y CONTROL DE PEDIDOS")
st.write(
    "Gestión unificada de cálculo de precios, inventario y flujo de pedidos."
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
        "Estado del Pedido", ["Pendiente", "Confirmado", "Entregado", "Cancelado"]
    )

  precio_venta_sugerido = costo + (costo * (margen_ganancia / 100))
  st.markdown(
      f"<h3 style='color: #4f6f52;'>💵 PRECIO DE VENTA CALCULADO:"
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
    e_modelo = st.text_input("Modelo de Prenda", value=fila_sel["modelo_prenda"])
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
=======
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Precios y Pedidos | PROYECTO X", page_icon="⚡", layout="wide")

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
    CREATE TABLE IF NOT EXISTS pedidos_inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT, modelo_prenda TEXT, categoria TEXT, talle TEXT, 
        cantidad INTEGER, costo REAL, margen_ganancia REAL, precio_venta REAL, 
        stock_inicial INTEGER, canal TEXT, estado TEXT, fecha TEXT
    )
""")
conn.commit()

st.title("🏷️ PRECIOS & GESTIÓN DE PEDIDOS")
st.caption("ENGINEERING PRICING & INVENTORY PIPELINE")

with st.form("form_pedidos_precios", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        cliente = st.text_input("Cliente Destinatario")
        modelo_prenda = st.text_input("Modelo / Prenda")
        categoria = st.selectbox("Categoría Textil", ["Remeras y Tops", "Pantalones y Jeans", "Abrigos y Camperas", "Calzados", "Accesorios"])
    with c2:
        talle = st.selectbox("Talla", ["XS", "S", "M", "L", "XL", "Único"])
        cantidad = st.number_input("Cantidad de Unidades", min_value=1, value=1)
        costo = st.number_input("Costo Unitario ($)", min_value=0.0, format="%.2f")
    with c3:
        margen_ganancia = st.number_input("Margen Comercial (%)", min_value=0.0, value=50.0)
        stock_inicial = st.number_input("Inventario Inicial", min_value=0, value=1)
        canal = st.selectbox("Canal de Distribución", ["Online (Redes)", "Físico"])
        estado = st.selectbox("Estado del Pedido", ["Pendiente", "Confirmado", "Entregado", "Cancelado"])

    precio_venta_sugerido = costo + (costo * (margen_ganancia / 100))
    st.markdown(f"""
        <div style="background-color: #10213A; border: 1px solid #1E365D; border-radius: 10px; padding: 15px; margin: 15px 0;">
            <p style="color: #9FB2C8; margin: 0; font-size: 0.85rem;">PRECIO DE VENTA PROYECTADO</p>
            <h2 style="color: #21D4C4; margin: 0; font-size: 2rem;">${precio_venta_sugerido:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

    if st.form_submit_button("⚡ GENERAR PEDIDO / ALTA DE PRENDA"):
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO pedidos_inventario 
            (cliente, modelo_prenda, categoria, talle, cantidad, costo, margen_ganancia, precio_venta, stock_inicial, canal, estado, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cliente, modelo_prenda, categoria, talle, cantidad, costo, margen_ganancia, precio_venta_sugerido, stock_inicial, canal, estado, fecha_actual))
        conn.commit()
        st.success("Pedido y precio sincronizados en inventario.")
        st.rerun()

st.markdown("---")
st.subheader("📋 Pipeline de Pedidos & Precios")
df_unificado = pd.read_sql_query("SELECT * FROM pedidos_inventario ORDER BY id DESC", conn)

if not df_unificado.empty:
    st.dataframe(df_unificado, use_container_width=True)
    st.markdown("### ⚙️ CONTROL Y MODIFICACIÓN DE REGISTROS")
    id_seleccionado = st.selectbox("ID de Registro a Modificar:", df_unificado['id'].tolist())
    fila_sel = df_unificado[df_unificado['id'] == id_seleccionado].iloc[0]

    with st.form("form_editar_pedido"):
        e_cliente = st.text_input("Cliente", value=fila_sel['cliente'])
        e_modelo = st.text_input("Modelo", value=fila_sel['modelo_prenda'])
        e_costo = st.number_input("Costo ($)", min_value=0.0, value=float(fila_sel['costo']), format="%.2f")
        e_margen = st.number_input("Margen (%)", min_value=0.0, value=float(fila_sel['margen_ganancia']))
        e_estado = st.selectbox("Estado", ["Pendiente", "Confirmado", "Entregado", "Cancelado"])

        nuevo_precio_calc = e_costo + (e_costo * (e_margen / 100))
        st.info(f"💡 Precio recalculado: ${nuevo_precio_calc:,.2f}")

        col_b1, col_b2 = st.columns(2)
        if col_b1.form_submit_button("🔄 ACTUALIZAR DATOS"):
            cursor.execute("""
                UPDATE pedidos_inventario 
                SET cliente=?, modelo_prenda=?, costo=?, margen_ganancia=?, precio_venta=?, estado=?
                WHERE id=?
            """, (e_cliente, e_modelo, e_costo, e_margen, nuevo_precio_calc, e_estado, id_seleccionado))
            conn.commit()
            st.success("Datos actualizados correctamente.")
            st.rerun()

        if col_b2.form_submit_button("🗑️ PURGAR ITEM"):
            cursor.execute("DELETE FROM pedidos_inventario WHERE id=?", (id_seleccionado,))
            conn.commit()
            st.success("Item eliminado del registro.")
            st.rerun()
else:
    st.info("No existen registros de pedidos activos.")
>>>>>>> c919b70 (Rediseño completo estilo Futurista Premium)
