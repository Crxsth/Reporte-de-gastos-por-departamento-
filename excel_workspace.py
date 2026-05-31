import streamlit as st
import sys
import core
import other_ui as ui


DEV_MODE = False

def tests():
    ##Esto hacía una limpieza temporal basada en un archivo
    if DEV_MODE == True:
        try:
            ruta_dev = r"C:\Users\criis\Documents\Coding\Report\Tests\Datos_base.csv"
            archivo_base = core.load_file(ruta_dev)
            archivo_id = "Datos_base.csv"
        except Exception as e:
            DEV_MODE = False
            pass
    
    if DEV_MODE == False:
        archivo_base, archivo_id = ui.obtener_dataframe(label="Data", key="base")
        if "last_uploaded_file_base" not in st.session_state:
            st.session_state.last_uploaded_file_base = None

        if archivo_id is not None and archivo_id != st.session_state.last_uploaded_file_base:
            st.write("Archivo añadido correctamente")
            st.session_state.last_uploaded_file_base = archivo_id
    
    ##Ejecuta la vista previa
    if archivo_base is not None:
        st.write(ss)
        with st.container(border=True):
            
            
            ##Corregimos header, date & numero en automático
            if "df_key" not in ss:
                core_obj_df_fixed = core.ReporteDf(archivo_base,name="Data_fixed").fix_header() 
                try:
                    core_obj_df_fixed.fix_dates().fix_numbers()
                except:
                    print("No se pudo convertir en fecha y número")
                df_fixed = core_obj_df_fixed.df
                ss.df_fixed = df_fixed


            ##Toggle que cambia entre archivo base y modificado
            cambiar_archivo = st.toggle(
                label="Cambiar archivo",
                key="toggle_cambiar_archivo"
            )
            if cambiar_archivo == True:
                st.write("Modo cambiar archivo activado")
                df = archivo_base
            else:
                df = ss.df_fixed
                st.write("Usando archivo actual")
    
            # vista_previa(archivo_base, titulo="Su archivo se muestra aquí", key=archivo_id)
            
            
            ui.vista_previa(df,titulo=f"Mostrando: {archivo_id}", key="data_fixed", n_max=len(df_fixed))
            
            ##Columnas que deben contener componentes interactivos que permitan manipular la tabla
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.button("My name is")
            with col2:
                st.write("My name is")
            with col3:
                st.write("My name iss")
            with col4:
                st.write("Slim shady")
    else:
        st.write("No hay archivo todavía")


def agrupar_datos():
    ss = st.session_state
    st.set_page_config(layout="centered")
    st.subheader("Agrupar")
    st.write("""Esta sección permite agrupar teniendo en cuenta dos columnas: Columna 'nombre' y columna monto.
        Es decir, si tuviera una tabla con 500 datos de 10 proveedores distintos y sus cargos, se agruparían a 10 filas con cada proveedor y sus totales.""")
    st.divider()
    
    ##Agrupación
    ui.obtener_dataframe(key="base")
    

def workspace_render():
    ##Variables iniciales
    ss = st.session_state
    st.set_page_config(layout="centered")
    
    st.write(ss)
    print("Pasamos a excel workspace, no limpiamos keys al manejarse con diversas páginas internas")
    keep_keys = []
    
    ##sesion state que indica qué 
    if "workspace_view" not in ss:
        ss.workspace_view = "menu"
    
    if ss.workspace_view == "menu":
        st.write("El objetivo de esta página es reducir el trabajo manual en archivos excel")
        st.divider()
        
        ##ChatGPT me recomendó 
        opciones = [
        {
            "boton": "Agrupar datos",
            "vista": "agrupar",
            "texto": (
                "Agrupa transacciones individuales por una o más columnas y calcula totales, "
                "conteos o promedios. Útil cuando tienes datos por línea y quieres resumirlos."
            )
        },
        {
            "boton": "Buscar datos",
            "vista": "buscar",
            "texto": (
                "Busca valores, palabras o patrones dentro de una tabla. Útil para encontrar "
                "transacciones específicas sin revisar todo manualmente."
            )
        },
        {
            "boton": "Limpiar datos",
            "vista": "limpiar",
            "texto": (
                "Permite preparar información eliminando columnas, filas vacías o datos que "
                "no necesitas antes de exportar."
            )
        }
    ]

    for opcion in opciones:
        col_btn, col_text = st.columns([1, 4], border=True)

        with col_btn:
            if st.button(opcion["boton"], width="stretch"):
                ui.clear_page_state(keep_keys=["page", "workspace_view"])
                ss.workspace_view = opcion["vista"]
                st.rerun()

        with col_text:
            st.write(opcion["texto"])
            
    ##Se llama a las funciones con tools específicas
    # elif ss.workspace_view == "agrupar":
        # agrupar_datos()
    # st.write(ss)
    ##Permite añadir un archivo
    
    
    
    st.stop()
    
    
    


if __name__ == "__main__":
    workspace_render()