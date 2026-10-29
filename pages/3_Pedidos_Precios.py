# VINCULACIÓN 2: Pase automático a Cuentas por Cobrar si queda saldo
                if saldo_pendiente > 0:
                    cuenta_cobrar = {
                        "fecha": str(fecha_ped),
                        "tipo": "Por Cobrar (Cliente me debe)",
                        "cliente": cliente_ped.strip(),
                        "concepto": f"Saldo Pedido #{pedido_creado_id} | {modelo_ped.strip()} ({cant_ped} uds.)",
                        "monto_deuda": int(saldo_pendiente),
                        "estado": "Pendiente"
                    }
                    supabase.table("deudas").insert(cuenta_cobrar).execute()
                    st.toast(f"💳 Cuentas por Cobrar: Saldo de {formato_gs(saldo_pendiente)} asentado.")