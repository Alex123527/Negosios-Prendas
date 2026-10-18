import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Pedidos & Precios | PROYECTO X", page_icon="🏷️", layout="wide")

# CSS Estilo Futurista
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #071426; color: #E6EDF5; }
    section[data-testid="stSidebar"] { background-color: #0b1a2f !important; }
    .stButton>button {
        background: linear-gradient(135deg, #4388FF 0%, #2f6de0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] { color: #21D4C4 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #9FB2C8 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #0d1b30 !important;
        color: #E6EDF5 !important;
        border: 1px solid #1E365D !important;
    }
    </style>
""", unsafe_allow_html=True)

# Escudo de seguridad
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso restringido. Por favor autentíquese en app.py.")
    st.stop()

# Conexión a Supabase
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

def formato_gs(valor):
    try:
        val_int = int(round(float(valor or 0)))
        return f"Gs. {val_int:,}".replace(",", ".")
    except Exception:
        return "Gs. 0"

# Cargar pedidos e inventario desde Supabase
def cargar_pedidos():
    try:
        res = supabase.table("pedidos_inventario").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        return pd.DataFrame()

df_pedidos = cargar_pedidos()

st.title("🏷️ GESTIÓN DE PEDIDOS, PRECIOS E INVENTARIO")
st.caption("CONTROL DE CATÁLOGO Y CATAPULTA DE MÁRGENES")

# Métricas Generales
total_articulos = 0
valor_inventario = 0.0
pedidos_pendientes = 0

if not df_pedidos.empty:
    if "cantidad" in df_pedidos.columns:
        df_pedidos["cantidad_num"] = pd.to_numeric(df_pedidos["cantidad"], errors="coerce").fillna(0)
        total_articulos = int(df_pedidos["cantidad_num"].sum())
    
    if "precio_venta" in df_pedidos.columns and "cantidad_num" in df_pedidos.columns:
        df_pedidos["precio_num"] = pd.to_numeric(df_pedidos["precio_venta"], errors="coerce").fillna(0)
        valor_inventario = float((df_pedidos["precio_num"] * df_pedidos["cantidad_num"]).sum())
        
    if "estado" in df_pedidos.columns:
        pedidos_pendientes = int((df_pedidos["estado"] == "Pendiente").sum())

m1, m2, m3 = st.columns(3)
m1.metric("📦 VOLUMEN TOTAL PRENDAS", f"{total_articulos} uds.")
m2.metric("💎 VALOR ESTIMADO CATÁLOGO", formato_gs(valor_inventario))
m3.metric("⏳ PEDIDOS EN ESPERA", f"{pedidos_pendientes} pedidos")

st.markdown("---")

col_form, col_calc = st.columns([2, 1])

with col_form:
    st.subheader("🛍️ Registrar Pedido / Stock de Prenda")
    
    with st.form("form_pedido", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_ped = st.date_input("Fecha de Registro", value=datetime.now())
            cliente_ped = st.text_input("Cliente / Destino", placeholder="Ej: Venta Local, María González...")
            modelo_ped = st.text_input("Modelo de Prenda / Descripción", placeholder="Ej: Remera Oversize Estampada")
            cat_ped = st.selectbox("Categoría", ["Remeras", "Pantalones / Jeans", "Buzos / Hoodies", "Camperas", "Shorts", "Accesorios", "Otros"])
            talle_ped = st.selectbox("Talle", ["XS", "S", "M", "L", "XL", "XXL", "Único", "Surtido"])
        
        with c2:
            cant_ped = st.number_input("Cantidad de Unidades", min_value=1, value=1, step=1)
            costo_unit = st.number_input("Costo Unitario (Gs.)", min_value=0, value=35000, step=5000, format="%d")
            margen_pct = st.slider("Margen de Ganancia Deseado (%)", min_value=10, max_value=200, value=60, step=5)
            
            # Cálculo sugerido en tiempo real
            precio_sugerido = int(costo_unit * (1 + margen_pct / 100))
            precio_final = st.number_input("Precio de Venta Final (Gs.)", min_value=0, value=precio_sugerido, step=5000, format="%d")
            
            canal_ped = st.selectbox("Canal de Distribución", ["Instagram", "WhatsApp", "Tienda Física", "Feria", "Otro"])
            estado_ped = st.selectbox("Estado del Pedido", ["Entregado / Pagado", "Pendiente", "En Preparación", "Cancelado"])
        
        btn_crear_ped = st.form_submit_button("💾 ASENTAR PRENDA / PEDIDO (ENTER)")
        
        if btn_crear_ped:
            if modelo_ped.strip():
                nuevo_pedido = {
                    "fecha": str(fecha_ped),
                    "cliente": cliente_ped,
                    "modelo_prenda": modelo_ped,
                    "categoria": cat_ped,
                    "talle": talle_ped,
                    "cantidad": int(cant_ped),
                    "costo": int(costo_unit),
                    "margen_ganancia": int(margen_pct),
                    "precio_venta": int(precio_final),
                    "stock_inicial": int(cant_ped),
                    "canal": canal_ped,
                    "estado": estado_ped
                }
                try:
                    supabase.table("pedidos_inventario").insert(nuevo_pedido).execute()
                    st.success("Prenda / Pedido registrado exitosamente en la nube.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Por favor, ingresa el modelo o nombre de la prenda.")

with col_calc:
    st.subheader("💡 Calculadora de Rentabilidad")
    st.info(f"Con un costo base de `{formato_gs(costo_unit)}` y margen del `{margen_pct}%`, tu ganancia bruta unitaria estimada es de `{formato_gs(precio_final - costo_unit)}`.")

st.markdown("---")
st.subheader("📋 Catálogo y Registro Maestro de Pedidos")

if not df_pedidos.empty:
    cols_ver = [c for c in ["id", "fecha", "cliente", "modelo_prenda", "categoria", "talle", "cantidad", "costo", "precio_venta", "canal", "estado"] if c in df_pedidos.columns]
    st.dataframe(df_pedidos[cols_ver], use_container_width=True)

    st.markdown("### ⚙️ Modificar o Actualizar Pedido / Prenda")
    sel_ped_id = st.selectbox("Seleccione ID de registro:", df_pedidos["id"].tolist())
    fila_ped = df_pedidos[df_pedidos["id"] == sel_ped_id].iloc[0]

    with st.form("form_edit_pedido"):
        e_modelo = st.text_input("Modelo", value=str(fila_ped.get("modelo_prenda", "")))
        e_precio = st.number_input("Precio de Venta (Gs.)", value=int(fila_ped.get("precio_venta", 0)), step=5000, format="%d")
        estados_opts = ["Entregado / Pagado", "Pendiente", "En Preparación", "Cancelado"]
        idx_estado = estados_opts.index(fila_ped["estado"]) if fila_ped.get("estado") in estados_opts else 0
        e_estado = st.selectbox("Estado", estados_opts, index=idx_estado)

        c_bt1, c_bt2 = st.columns(2)
        if c_bt1.form_submit_button("🔄 ACTUALIZAR (ENTER)"):
            try:
                supabase.table("pedidos_inventario").update({
                    "modelo_prenda": e_modelo,
                    "precio_venta": int(e_precio),
                    "estado": e_estado
                }).eq("id", sel_ped_id).execute()
                st.success("Registro actualizado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar: {e}")

        if c_bt2.form_submit_button("🗑️ ELIMINAR REGISTRO"):
            try:
                supabase.table("pedidos_inventario").delete().eq("id", sel_ped_id).execute()
                st.success("Registro eliminado de Supabase.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")
else:
    st.info("Sin prendas o pedidos cargados todavía en la nube.")