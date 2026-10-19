import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from supabase import create_client, Client

st.set_page_config(page_title="Deudas | PROYECTO X", page_icon="💳", layout="wide")

# CSS Estilo Futurista Coherente
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #071426; color: #E6EDF5; }
    section[data-testid="stSidebar"] { background-color: #0b1a2f !important; }
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(135deg, #4388FF 0%, #2f6de0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] { color: #21D4C4 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #9FB2C8 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input {
        background-color: #0d1b30 !important;
        color: #E6EDF5 !important;
        border: 1px solid #1E365D !important;
    }
    </style>
""", unsafe_allow_html=True)

# Validación de seguridad
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso restringido. Por favor autentíquese en app.py.")
    st.stop()

# Conexión Supabase
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

# Cargar Cuentas y Deudas desde Supabase
def cargar_deudas():
    try:
        res = supabase.table("deudas").select("*").order("id", desc=True).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con tabla deudas: {e}")
        return pd.DataFrame()

df_deudas = cargar_deudas()

st.title("💳 GESTIÓN DE DEUDAS Y CUENTAS POR COBRAR")
st.caption("CONTROL DE SALDOS PENDIENTES, VENCIMIENTOS Y LIQUIDACIONES")

# Métricas Principales
total_por_cobrar = 0
total_por_pagar = 0
cuentas_pendientes_cobro = 0
cuentas_pendientes_pago = 0

if not df_deudas.empty:
    df_temp = df_deudas.copy()
    df_temp["monto_num"] = pd.to_numeric(df_temp.get("monto_deuda", 0), errors="coerce").fillna(0)
    
    pendientes = df_temp[df_temp.get("estado", "").str.contains("Pendiente|Parcial", case=False, na=False)]
    
    por_cobrar_df = pendientes[~pendientes.get("tipo", "").str.contains("Pagar|Proveedor", case=False, na=False)]
    por_pagar_df = pendientes[pendientes.get("tipo", "").str.contains("Pagar|Proveedor", case=False, na=False)]
    
    total_por_cobrar = int(por_cobrar_df["monto_num"].sum())
    total_por_pagar = int(por_pagar_df["monto_num"].sum())
    cuentas_pendientes_cobro = len(por_cobrar_df)
    cuentas_pendientes_pago = len(por_pagar_df)

m1, m2, m3 = st.columns(3)
m1.metric("💰 CAPITAL EN LA CALLE (POR COBRAR)", formato_gs(total_por_cobrar), f"{cuentas_pendientes_cobro} cuentas activas")
m2.metric("🧾 COMPROMISOS (POR PAGAR)", formato_gs(total_por_pagar), f"{cuentas_pendientes_pago} compromisos", delta_color="inverse")
m3.metric("⚖️ SALDO NETO", formato_gs(total_por_cobrar - total_por_pagar))

st.markdown("---")

col_form, col_resumen = st.columns([1.8, 1.2])

with col_form:
    st.subheader("📝 ASENTAR NUEVA CUENTA / DEUDA")

    c1, c2 = st.columns(2)
    with c1:
        tipo_deuda = st.selectbox("Tipo de Operación", ["Por Cobrar (Cliente me debe)", "Por Pagar (Debo a Proveedor/Taller)"])
        fecha_reg = st.date_input("Fecha de Registro", value=datetime.now())
        cliente_contacto = st.text_input("Nombre de la Persona / Cliente / Proveedor", placeholder="Ej: Juan Pérez / Proveedor")
        forma_pago = st.selectbox("Forma de Pago Acordada", ["Efectivo", "Transferencia Bancaria", "Billetera Zimple / Giros", "Cheque / Pagaré", "Otro"])

    with c2:
        monto_cuenta = st.number_input("Monto de la Deuda (Gs.)", min_value=0, value=100000, step=10000, format="%d")
        st.caption(f"Monto: **{formato_gs(monto_cuenta)}**")
        
        fecha_vencimiento = st.date_input("Fecha Límite / Vencimiento", value=datetime.now() + timedelta(days=15))
        estado_inicial = st.selectbox("Estado Actual", ["Pendiente", "Abono Parcial", "Cancelado / Pagado"])
        concepto_det = st.text_input("Concepto / Prenda entregada / Motivo", placeholder="Ej: Pantalón Cargo talle 42")

    asentar_en_caja = st.checkbox("Asentar automáticamente en Caja de Negocio si ya se abonó / canceló", value=False)
    
    btn_guardar_deuda = st.button("💾 ASENTAR REGISTRO", use_container_width=True)

    if btn_guardar_deuda:
        if cliente_contacto.strip() and concepto_det.strip() and monto_cuenta > 0:
            nueva_deuda = {
                "fecha": str(fecha_reg),
                "cliente": cliente_contacto.strip(),
                "concepto": concepto_det.strip(),
                "monto_deuda": int(monto_cuenta),
                "estado": estado_inicial,
                "tipo": tipo_deuda,
                "forma_pago": forma_pago,
                "fecha_vencimiento": str(fecha_vencimiento)
            }
            try:
                supabase.table("deudas").insert(nueva_deuda).execute()

                if asentar_en_caja and estado_inicial == "Cancelado / Pagado":
                    tipo_trans = "Ingreso" if "Cobrar" in tipo_deuda else "Egreso"
                    categoria_trans = "Ventas / Cobros" if tipo_trans == "Ingreso" else "Proveedores / Costos"
                    
                    transaccion_caja = {
                        "fecha": str(fecha_reg),
                        "tipo": tipo_trans,
                        "categoria": categoria_trans,
                        "monto": int(monto_cuenta),
                        "descripcion": f"Cobro/Pago Deuda: {cliente_contacto.strip()} - {concepto_det.strip()} ({forma_pago})"
                    }
                    supabase.table("transacciones").insert(transaccion_caja).execute()
                    st.info(f"✅ Se registró automáticamente el {tipo_trans} de {formato_gs(monto_cuenta)} en Caja de Negocio.")

                st.success("¡Cuenta asentada exitosamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al registrar en Supabase: {e}")
        else:
            st.warning("Completa el nombre, concepto y verifica que el monto sea mayor a 0 Gs.")

with col_resumen:
    st.subheader("💡 RESUMEN Y VENCIMIENTOS")
    
    if not df_deudas.empty and "fecha_vencimiento" in df_deudas.columns:
        hoy = datetime.now().date()
        df_p = df_deudas[df_deudas.get("estado", "").str.contains("Pendiente|Parcial", case=False, na=False)].copy()
        
        if not df_p.empty:
            df_p["venc_dt"] = pd.to_datetime(df_p["fecha_vencimiento"], errors="coerce").dt.date
            
            vencidas = df_p[df_p["venc_dt"] < hoy]
            vence_hoy = df_p[df_p["venc_dt"] == hoy]
            al_dia = df_p[df_p["venc_dt"] > hoy]
            
            if not vencidas.empty:
                st.error(f"⚠️ **{len(vencidas)} cuenta(s) vencida(s) / en mora:**")
                for _, r in vencidas.iterrows():
                    st.write(f"- {r.get('cliente')}: **{formato_gs(r.get('monto_deuda', 0))}** | Venció: {r.get('fecha_vencimiento')}")
            
            if not vence_hoy.empty:
                st.warning(f"🔔 **{len(vence_hoy)} cuenta(s) vencen hoy:**")
                for _, r in vence_hoy.iterrows():
                    st.write(f"- {r.get('cliente')}: **{formato_gs(r.get('monto_deuda', 0))}**")
                    
            if not al_dia.empty:
                st.success(f"✅ **{len(al_dia)} cuenta(s) al día y vigentes.**")
        else:
            st.success("¡Al día! No hay cuentas pendientes.")
    else:
        st.info("Sin cuentas pendientes activas.")

st.markdown("---")

# TABLA Y EXPORTACIÓN EN EXCEL
col_t_tab, col_btn_exp = st.columns([2.5, 1.5])
with col_t_tab:
    st.subheader("📋 REGISTRO MAESTRO DE CUENTAS")

if not df_deudas.empty:
    cols_base = ["id", "fecha", "tipo", "cliente", "concepto", "monto_deuda", "forma_pago", "fecha_vencimiento", "estado"]
    cols_existentes = [c for c in cols_base if c in df_deudas.columns]
    df_mostrar = df_deudas[cols_existentes].copy()
    
    if "monto_deuda" in df_mostrar.columns:
        m_num = pd.to_numeric(df_mostrar["monto_deuda"], errors="coerce").fillna(0)
        df_mostrar["TOTAL (GS.)"] = m_num.apply(formato_gs)

    # Descarga directa en Excel
    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
        df_mostrar.to_excel(writer, index=False, sheet_name='Deudas')
    excel_data = buffer_excel.getvalue()

    with col_btn_exp:
        st.download_button(
            label="📗 Descargar Cuentas en Excel (.xlsx)",
            data=excel_data,
            file_name=f"Cuentas_Deudas_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.dataframe(df_mostrar, use_container_width=True)

    # GESTIÓN Y ACTUALIZACIÓN
    st.markdown("### ⚙️ ACTUALIZAR O LIQUIDAR CUENTA")
    opciones_deudas = {f"ID #{r['id']} - {r.get('cliente', '')} ({r.get('concepto', '')}) - {formato_gs(r.get('monto_deuda', 0))}": r['id'] for _, r in df_deudas.iterrows()}
    sel_deuda_txt = st.selectbox("Seleccione registro:", list(opciones_deudas.keys()))
    sel_deuda_id = opciones_deudas[sel_deuda_txt]
    
    fila_d = df_deudas[df_deudas["id"] == sel_deuda_id].iloc[0]

    with st.form("form_editar_deuda"):
        ed1, ed2 = st.columns(2)
        with ed1:
            ed_cliente = st.text_input("Cliente / Contacto", value=str(fila_d.get("cliente", "")))
            ed_monto = st.number_input("Saldo / Monto (Gs.)", value=int(fila_d.get("monto_deuda", 0)), step=10000, format="%d")
            st.caption(f"Monto: **{formato_gs(ed_monto)}**")
        with ed2:
            estados_d = ["Pendiente", "Abono Parcial", "Cancelado / Pagado"]
            idx_est = estados_d.index(fila_d["estado"]) if fila_d.get("estado") in estados_d else 0
            ed_estado_d = st.selectbox("Estado", estados_d, index=idx_est)
            liquidar_caja = st.checkbox("Asentar saldo en Caja de Negocio al cancelar", value=False)

        b_act, b_elim = st.columns(2)
        if b_act.form_submit_button("🔄 GUARDAR CAMBIOS"):
            try:
                supabase.table("deudas").update({
                    "cliente": ed_cliente.strip(),
                    "monto_deuda": int(ed_monto),
                    "estado": ed_estado_d
                }).eq("id", sel_deuda_id).execute()

                if liquidar_caja and ed_estado_d == "Cancelado / Pagado":
                    tipo_trans = "Ingreso" if "Cobrar" in str(fila_d.get("tipo", "")) else "Egreso"
                    supabase.table("transacciones").insert({
                        "fecha": str(datetime.now().date()),
                        "tipo": tipo_trans,
                        "categoria": "Liquidación Deuda",
                        "monto": int(ed_monto),
                        "descripcion": f"Liquidación: {ed_cliente.strip()} - {fila_d.get('concepto', '')}"
                    }).execute()
                    st.info("Liquidación registrada en Caja.")

                st.success("Cuenta actualizada exitosamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar: {e}")

        if b_elim.form_submit_button("🗑️ ELIMINAR CUENTA"):
            try:
                supabase.table("deudas").delete().eq("id", sel_deuda_id).execute()
                st.success("Cuenta eliminada de la base de datos.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")
else:
    st.info("Sin registros de deudas o cuentas por cobrar por el momento.")