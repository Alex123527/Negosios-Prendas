import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client

st.set_page_config(page_title="Pedidos y Precios | PROYECTO X", page_icon="🏷️", layout="wide")

# CSS Estilo Futurista Premium
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

st.title("🏷️ PEDIDOS Y PRECIOS")
st.caption("CONTROL DE CATÁLOGO, LOGÍSTICA Y CATAPULTA DE MÁRGENES")

# Métricas Superiores
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
        pedidos_pendientes = int((df_pedidos["estado"].str.contains("Pendiente", case=False, na=False)).sum())

m1, m2, m3 = st.columns(3)
m1.metric("📦 VOLUMEN TOTAL PRENDAS", f"{total_articulos} uds.")
m2.metric("💎 VALOR ESTIMADO CATÁLOGO", formato_gs(valor_inventario))
m3.metric("⏳ PEDIDOS EN ESPERA", f"{pedidos_pendientes} pedidos")

st.markdown("---")

col_form, col_calc = st.columns([1.8, 1.2])

with col_form:
    st.subheader("🛍️ REGISTRAR PEDIDOS")
    
    c1, c2 = st.columns(2)
    with c1:
        fecha_ped = st.date_input("Fecha de Registro", value=datetime.now())
        cliente_ped = st.text_input("Cliente / Destino", placeholder="Ej: María González / Consumidor Final")
        modelo_ped = st.text_input("Modelo de Prenda / Calzado", placeholder="Ej: Championes Urbanos, Calza Lycra...")
        
        categorias_lista = ["Calzados", "Remeras", "Pantalones / Jeans", "Calzas / Leggins", "Buzos / Hoodies", "Camperas", "Shorts", "Accesorios", "Otros"]
        cat_ped = st.selectbox("Categoría", categorias_lista)
        
        if cat_ped == "Calzados":
            talles_disponibles = [str(i) for i in range(1, 51)]
            talle_ped = st.selectbox("Calce / Talle", talles_disponibles, index=39)
        else:
            talles_disponibles = ["XS", "S", "M", "L", "XL", "XXL", "Único", "Surtido"]
            talle_ped = st.selectbox("Talle", talles_disponibles, index=2)
            
        tipo_pago_ped = st.selectbox("Tipo de Pago", ["Efectivo", "Transferencia Bancaria", "Billetera Zimple / Giros", "Tarjeta de Débito/Crédito", "A Crédito / Pendiente", "Otro"])

    with c2:
        cant_ped = st.number_input("Cantidad de Unidades", min_value=1, value=1, step=1)
        costo_unit = st.number_input("Costo Unitario Prenda (Gs.)", min_value=0, value=35000, step=5000, format="%d")
        st.caption(f"Costo unitario prenda: **{formato_gs(costo_unit)}**")
        
        margen_pct = st.slider("Margen Deseado (%)", min_value=5, max_value=250, value=60, step=5)
        
        precio_sugerido_calculado = int(round(costo_unit * (1 + margen_pct / 100)))
        precio_final = st.number_input("Precio de Venta Unitario (Gs.)", min_value=0, value=precio_sugerido_calculado, step=5000, format="%d")
        st.caption(f"Precio venta unitario: **{formato_gs(precio_final)}**")
        
        monto_total_prendas = cant_ped * precio_final
        st.text_input("Subtotal Prendas (Gs.)", value=formato_gs(monto_total_prendas), disabled=True)
        
        canal_ped = st.selectbox("Canal de Venta", ["Instagram", "WhatsApp", "Tienda Física", "Feria", "Otro"])
        estado_ped = st.selectbox("Estado del Pedido", ["Entregado / Pagado", "Pendiente", "En Preparación", "Cancelado"])

    st.markdown("#### 🚚 LOGÍSTICA, TRANSPORTADORA Y PACKAGING")
    cl1, cl2, cl3 = st.columns(3)
    with cl1:
        empresa_envio = st.selectbox("Transportadora / Medio", ["Retiro en Local", "AEX", "NSA Encomiendas", "Rysa", "Delivery Local (Moto)", "Otra Encomienda"])
    with cl2:
        costo_envio = st.number_input("Costo Envío / Flete (Gs.)", min_value=0, value=0, step=5000, format="%d")
        st.caption(f"Flete: **{formato_gs(costo_envio)}**")
    with cl3:
        quien_paga_envio = st.selectbox("¿Quién asume el envío?", ["Cliente (Paga al recibir / Sumado)", "Negocio (Envío Gratis / Promoción)", "Sin Costo de Envío"])

    comprobante_ped = st.file_uploader("Comprobante de Pago / Guía de Envío (Opcional)", type=["png", "jpg", "jpeg", "pdf"])
    
    btn_crear_ped = st.button("💾 ASENTAR PRENDA / PEDIDO", use_container_width=True)
    
    if btn_crear_ped:
        if modelo_ped.strip():
            nombre_doc = comprobante_ped.name if comprobante_ped is not None else ""
            
            # Detalle logístico en la información del canal para trazabilidad total
            info_canal = f"{canal_ped} | Pago: {tipo_pago_ped} | Envio: {empresa_envio} ({formato_gs(costo_envio)} - {quien_paga_envio})"
            if nombre_doc:
                info_canal += f" | Doc: {nombre_doc}"

            nuevo_pedido = {
                "fecha": str(fecha_ped),
                "cliente": cliente_ped.strip(),
                "modelo_prenda": modelo_ped.strip(),
                "categoria": cat_ped,
                "talle": talle_ped,
                "cantidad": int(cant_ped),
                "costo": int(costo_unit),
                "margen_ganancia": int(margen_pct),
                "precio_venta": int(precio_final),
                "stock_inicial": int(cant_ped),
                "canal": info_canal,
                "estado": estado_ped
            }
            try:
                supabase.table("pedidos_inventario").insert(nuevo_pedido).execute()
                
                # ASIENTO AUTOMÁTICO EN CAJA: Si el negocio cubre el envío y hay costo > 0
                if quien_paga_envio == "Negocio (Envío Gratis / Promoción)" and costo_envio > 0:
                    egreso_envio = {
                        "fecha": str(fecha_ped),
                        "tipo": "Egreso",
                        "categoria": "Packaging / Envíos",
                        "monto": int(costo_envio),
                        "descripcion": f"Flete {empresa_envio} - Pedido: {modelo_ped.strip()} ({cliente_ped.strip()})"
                    }
                    supabase.table("transacciones").insert(egreso_envio).execute()
                    st.info(f"🚚 Se registró automáticamente el egreso de {formato_gs(costo_envio)} por flete en Caja de Negocio.")

                st.success("¡Pedido y logística asentados con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al registrar: {e}")
        else:
            st.warning("Por favor ingresa el modelo o nombre de la prenda.")

with col_calc:
    st.subheader("💡 CALCULADORA DE RENTABILIDAD & DEMANDA")
    
    # Impacto del envío en la ganancia real
    gasto_envio_negocio = costo_envio if quien_paga_envio == "Negocio (Envío Gratis / Promoción)" else 0
    ganancia_neta_total_pedido = (monto_total_prendas - (costo_unit * cant_ped)) - gasto_envio_negocio
    
    st.info(f"Ganancia bruta estimada: **{formato_gs(ganancia_neta_total_pedido)}** en este pedido (descontando mercadería y flete asumido).")

    # Demanda y liquidez
    hoy = datetime.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    primer_dia_mes = hoy.replace(day=1)
    
    pedidos_dia = 0
    pedidos_semana = 0
    pedidos_mes = 0
    capital_semana_requerido = 0.0
    venta_semana_proyectada = 0.0
    
    if not df_pedidos.empty and "fecha" in df_pedidos.columns:
        df_temp = df_pedidos.copy()
        df_temp["fecha_dt"] = pd.to_datetime(df_temp["fecha"], errors="coerce").dt.date
        df_temp["cant_n"] = pd.to_numeric(df_temp.get("cantidad", 0), errors="coerce").fillna(0)
        df_temp["costo_n"] = pd.to_numeric(df_temp.get("costo", 0), errors="coerce").fillna(0)
        df_temp["precio_n"] = pd.to_numeric(df_temp.get("precio_venta", 0), errors="coerce").fillna(0)
        
        df_dia = df_temp[df_temp["fecha_dt"] == hoy]
        pedidos_dia = int(df_dia["cant_n"].sum())
        
        df_sem = df_temp[df_temp["fecha_dt"] >= hace_7_dias]
        pedidos_semana = int(df_sem["cant_n"].sum())
        capital_semana_requerido = float((df_sem["cant_n"] * df_sem["costo_n"]).sum())
        venta_semana_proyectada = float((df_sem["cant_n"] * df_sem["precio_n"]).sum())
        
        df_mes = df_temp[df_temp["fecha_dt"] >= primer_dia_mes]
        pedidos_mes = int(df_mes["cant_n"].sum())
    
    st.markdown("#### 📅 VOLUMEN DE PEDIDOS")
    cd1, cd2, cd3 = st.columns(3)
    cd1.metric("HOY", f"{pedidos_dia} uds.")
    cd2.metric("SEMANA", f"{pedidos_semana} uds.")
    cd3.metric("MES", f"{pedidos_mes} uds.")
    
    st.markdown("#### 💼 CAPITAL Y LIQUIDEZ SEMANAL")
    st.write(f"• **Capital Requerido Semanal (Costo):** `{formato_gs(capital_semana_requerido)}`")
    st.write(f"• **Facturación Estimada Semanal:** `{formato_gs(venta_semana_proyectada)}`")
    st.write(f"• **Retorno Semanal Estimado:** `{formato_gs(venta_semana_proyectada - capital_semana_requerido)}`")

st.markdown("---")

st.subheader("📋 CATÁLOGO Y REGISTRO MAESTRO DE PEDIDOS")

if not df_pedidos.empty:
    cols_base = ["id", "fecha", "cliente", "modelo_prenda", "categoria", "talle", "cantidad", "costo", "precio_venta", "canal", "estado"]
    cols_existentes = [c for c in cols_base if c in df_pedidos.columns]
    
    df_mostrar = df_pedidos[cols_existentes].copy()
    
    if "cantidad" in df_mostrar.columns and "precio_venta" in df_mostrar.columns:
        c_num = pd.to_numeric(df_mostrar["cantidad"], errors="coerce").fillna(0)
        p_num = pd.to_numeric(df_mostrar["precio_venta"], errors="coerce").fillna(0)
        cost_num = pd.to_numeric(df_mostrar.get("costo", 0), errors="coerce").fillna(0)
        
        df_mostrar["TOTAL PEDIDO (GS.)"] = (c_num * p_num).apply(formato_gs)
        df_mostrar["costo"] = cost_num.apply(formato_gs)
        df_mostrar["precio_venta"] = p_num.apply(formato_gs)
    
    st.dataframe(df_mostrar, use_container_width=True)

    st.markdown("#### 📊 TOTAL DE UNIDADES PEDIDAS POR MODELO")
    if "modelo_prenda" in df_pedidos.columns and "cantidad_num" in df_pedidos.columns:
        agrupado_prod = df_pedidos.groupby("modelo_prenda")["cantidad_num"].sum().reset_index()
        agrupado_prod.columns = ["MODELO DE PRENDA", "CANTIDAD TOTAL PEDIDA (UDS)"]
        st.dataframe(agrupado_prod, use_container_width=True)

    st.markdown("### ⚙️ MODIFICAR O ACTUALIZAR PEDIDO / PRENDA")
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