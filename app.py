from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

st.set_page_config(
    page_title="PROYECTO X - Estilo Planner", page_icon="🌿", layout="wide"
)

# Estética Planner (Tonos Verdes Claros y Limpios)
st.markdown(
    """
    <style>
    .main { background-color: #f7f9f6; color: #2c3e2d; }
    h1, h2, h3 { color: #3b533c !important; font-family: 'Segoe UI', sans-serif; }
    .planner-card {
        background-color: #ffffff;
        border: 1px solid #d4e0d2;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(59, 83, 60, 0.05);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #4f6f52;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #3b533c; }
    </style>
""",
    unsafe_allow_html=True,
)

if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
  st.markdown(
      "<h2 style='text-align: center; color: #4f6f52;'>PROYECTO X - Acceso"
      " Seguro</h2>",
      unsafe_allow_html=True,
  )
  col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
  with col_l2:
    correo_ingresado = st.text_input("Correo Electrónico")
    password_ingresada = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión", use_container_width=True):
      # Leer credenciales seguras desde los secrets de Streamlit
      correo_valido = st.secrets["auth"]["correo"]
      password_valida = st.secrets["auth"]["password"]

      if (
          correo_ingresado.strip().lower() == correo_valido.lower()
          and password_ingresada == password_valida
      ):
        st.session_state["autenticado"] = True
        st.rerun()
      else:
        st.error("Correo o contraseña incorrectos.")
  st.stop()

st.sidebar.markdown(
    "<h3 style='color: #4f6f52;'>🌿 PROYECTO X</h3>", unsafe_allow_html=True
)
st.sidebar.write("Selecciona una sección arriba en el menú de páginas.")

if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
  st.session_state["autenticado"] = False
  st.rerun()

st.title("🌿 Bienvenido a PROYECTO X")
st.write(
    "Sistema de gestión integral organizado por módulos independientes."
)
st.info(
    "👉 Utiliza el menú lateral izquierdo para navegar entre los diferentes"
    " paneles (Gastos, Caja, Pedidos, Deudas y Reportes)."
)