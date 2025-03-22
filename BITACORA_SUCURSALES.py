import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
import pytz 
from datetime import datetime 

# Definir la zona horaria de Culiacán, Sinaloa (UTC -7)
culiacan_tz = pytz.timezone("America/Mazatlan")  # Zona horaria correcta para Sinaloa

# Obtener la fecha y hora actual en la zona horaria especificada
fecha_actual = datetime.now(culiacan_tz).date()

# Usar la fecha con la zona horaria en Streamlit


# Configurar la conexión a SQL Server usando pymssql
DATABASE_URL = "mssql+pymssql://credito:Cr3d$.23xme@52.167.231.145:51433/CreditoyCobranza"

# Crear el engine de SQLAlchemy
engine = create_engine(DATABASE_URL)

def get_connection():
    """Obtiene la conexión a la base de datos."""
    try:
        conn = engine.connect()
        return conn
    except Exception as e:
        st.error(f"Error en la conexión con la base de datos: {e}")
        return None

# ========== INTERFAZ STREAMLIT ==========
st.title("BITACORA SUCURSALES")

# Sidebar para navegar entre secciones
st.sidebar.title("Menú")
pagina = st.sidebar.radio("Selecciona una opción", ["BITACORA SUCURSALES", "Indicadores"])

# ========== PÁGINA DE BITÁCORA ==========
if pagina == "BITACORA SUCURSALES":

    st.markdown("### ⚠️ **NO DAR ENTER O SE GUARDARÁ EL REGISTRO** ⚠️")
    st.markdown("Por favor, utilice el botón **'Guardar Registro'** para enviar el formulario.")

    # ========== FORMULARIO ==========
    with st.form("registro_form", clear_on_submit=True):  
        col1, col2, col3 = st.columns(3)

        with col1:
            fecha_reporte = st.date_input("Fecha reporte", fecha_actual)
            nombre_cliente = st.text_input("Nombre del cliente")
            num_cliente = st.number_input("Número de cliente")
            tel_cliente = st.number_input("Número teléfonico")
            
            
        with col2:
            sucursal_venta = st.selectbox("Sucursal de venta", list(range(1, 101)))
            sucursal_reporte = st.selectbox("Sucursal de reporte", list(range(1, 101)))
            quien_reporta = st.selectbox("Quien reporta",["Ejecutivo 1","Ejecutivo 2"])
            detalle_reporte = st.text_area("Detalle reporte")
            quien_atendio = st.selectbox("Quien atendió",["Ejecutivo 1","Ejecutivo 2"])
          

        with col3:
            num_ticket_reporte = st.number_input("Número ticket de reporte")
            factura_remision = st.text_input("Factura / Remisión")
            estatus = st.selectbox("Estatus",["Atendido","Cerrado","Pendiente"])
            fecha_solucion = st.date_input("Fecha de solución", fecha_actual)
            detalle_solucion = st.text_area("Detalle solución")
            articulo = st.selectbox("Articulo", ["SALA","COMEDOR","TELEFONO","MOTO","OTROS"])


    
    # ✅ IMPORTANTE: Botón de envío dentro del `st.form()`
        submit_button = st.form_submit_button("Guardar Registro")

    # ========== GUARDAR REGISTRO ==========
    if submit_button:
        conn = get_connection()
        if conn:
            try:
                query = text("""
                    INSERT INTO BITACORA_SUCURSALES (
                        FECHA_REPORTE, NOMBRE_CLIENTE, NUM_CLIENTE, NUM_TICKET_REPORTE,
                        TEL_CLIENTE, SUCURSAL_VENTA, SUCURSAL_REPORTE, QUIEN_REPORTA,
                        FACTURA_REMISION, ARTICULO, DETALLE_REPORTE, QUIEN_ATENDIO
                        ESTATUS, FECHA_SOLUCION, DETALLE_SOLUCION
                    ) 
                    VALUES (:fecha_reporte,:nombre_cliente, :num_cliente, :num_ticket_reporte,
                             :tel_cliente, :sucursal_venta, :sucursal_reporte, :quien_reporta,
                             :factura_remision, :articulo, :detalle_reporte, :quien_atendio, :estatus,
                             :fecha_solucion, :detalle_solucion )
                """)

                conn.execute(query, {
                    "fecha_reporte": fecha_reporte.strftime('%Y-%m-%d'),
                    "nombre_cliente": nombre_cliente,
                    "num_cliente": num_cliente,
                    "num_ticket_reporte": num_ticket_reporte,
                    "tel_cliente": tel_cliente,
                    "sucursal_venta": sucursal_venta,
                    "sucursal_reporte": sucursal_reporte,
                    "quien_reporta": quien_reporta,
                    "factura_remision": factura_remision,
                    "articulo": articulo,
                    "detalle_reporte": detalle_reporte,
                    "quien_atendio": quien_atendio,
                    "estatus": estatus,
                    "fecha_solucion": fecha_solucion.strftime('%Y-%m-%d'),
                    "detalle_solucion": detalle_solucion
                })
                conn.commit()
                st.success("Registro guardado exitosamente en la base de datos.")
            except Exception as e:
                st.error(f"Error al guardar el registro: {e}")
            finally:
                conn.close()

    # ========== VISUALIZADOR EN TIEMPO REAL ==========
    st.header("📊 Registros en tiempo real")

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_cliente = st.text_input("Filtrar por ID Cliente", "")
    with col2:
        filtro_fecha = st.date_input("Filtrar por fecha", fecha_actual)
    with col3:
        filtro_ejecutivo = st.selectbox("Filtrar por Ejecutivo", ["Todos"] + ["Ejecutivo 1","Ejecutivo 2"])

    # Función para obtener registros desde SQL Server
    def fetch_records():
        conn = get_connection()
        if conn:
            try:
                query = text("SELECT ID_REPORTE AS '#Registro', * FROM BITACORA_SUCURSALES WHERE FECHA_REPORTE = :fecha_reporte ORDER BY ID_REPORTE ASC")
                params = {"fecha_reporte": filtro_fecha.strftime('%Y-%m-%d')}

                if filtro_ejecutivo != "Todos":
                    query = text("SELECT ID_REPORTE AS '#Registro', * FROM BITACORA_SUCURSALES WHERE FECHA_REPORTE = :fecha_reporte AND QUIEN_REPORTA = :ejecutivo ORDER BY ID_REPORTE ASC")
                    params["ejecutivo"] = filtro_ejecutivo

                df = pd.read_sql(query, conn, params=params)
                conn.close()
                return df
            except Exception as e:
                st.error(f"Error al obtener los registros: {e}")
                return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error
        return pd.DataFrame()

    # Mostrar registros en tiempo real
    df_records = fetch_records()

    if not df_records.empty:
        st.dataframe(df_records)
    else:
        st.warning("No hay registros para mostrar con los filtros seleccionados.")

 # ========== ✏️ EDITAR UN REGISTRO ==========
    st.subheader("✏️ Editar un registro")

    if not df_records.empty:
        registros_disponibles = df_records["#Registro"].tolist()
        registro_seleccionado = st.selectbox("Seleccione el número de registro a editar:", registros_disponibles)

        # Lista de columnas editables
        columnas_editables = ["FECHA_REPORTE", "NOMBRE_CLIENTE", "NUM_CLIENTE", "NUM_TICKET_REPORTE",
                        "TEL_CLIENTE", "SUCURSAL_VENTA", "SUCURSAL_REPORTE", "QUIEN_REPORTA",
                        "FACTURA_REMISION", "ARTICULO", "DETALLE_REPORTE", "QUIEN_ATENDIO",
                        "ESTATUS", "FECHA_SOLUCION", "DETALLE_SOLUCION"]

        campo_seleccionado = st.selectbox("Seleccione el campo a editar:", columnas_editables)
        nuevo_valor = st.text_input(f"Ingrese el nuevo valor para {campo_seleccionado}:")

        if st.button("Actualizar Registro"):
            conn = get_connection()
            if conn:
                try:
                    update_query = text(f"UPDATE BITACORA_SUCURSALES SET {campo_seleccionado} = :nuevo_valor WHERE Registro = :registro")
                    conn.execute(update_query, {"nuevo_valor": nuevo_valor, "registro": registro_seleccionado})
                    conn.commit()
                    st.success(f"Registro #{registro_seleccionado} actualizado exitosamente.")
                except Exception as e:
                    st.error(f"Error al actualizar el registro: {e}")
                finally:
                    conn.close()
                st.rerun()  # Recargar la página para reflejar los cambios



