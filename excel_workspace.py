import streamlit as st
import sys
import core
import other_ui as ui
import time


DEV_MODE = False
DEV_BASE = r"C:\Users\criis\Documents\Coding\Conciliation\Datos1.csv"


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
    """Función que muestracomponentes interactivos a través de los cuales el usuario puede elegir cómo agrupar los datos
    
    """
    t0 = time.time()
    ss = st.session_state
    ss.layout="wide"
    st.set_page_config(layout=ss.layout)
    st.write(ss)
    
    st.subheader("Agrupar")
    st.write("""Esta sección permite agrupar teniendo en cuenta dos columnas: Columna 'nombre' y columna monto.
        Es decir, si tuviera una tabla con 500 datos de 10 proveedores distintos y sus cargos, se agruparían a 10 filas con cada proveedor y sus totales.""")
    st.divider()
    
    ##Obtención de datos
    if DEV_MODE == True:
        df_base = core.load_file(DEV_BASE)
    else:
        df_base, base_id = ui.obtener_dataframe(label="Database data", key="base")
        
    if df_base is None:
        st.stop()
    ss.df_base = "df_base"
    ##Arreglos
    core_object = core.ReporteDf(df_base).fix_header()
    core_object.fix_dates()
    core_object.fix_numbers()
    df = core_object.df
    ui.vista_previa(df, titulo="Archivo base", key= "base", n_max=len(df_base))
    # st.divider()
    
    """Aquí se seleccionan las columnas:
        -Agregacion es numérico, ya que con ello se hacen operaciones.
        -Categórico es fecha o texto, ya que podemos agrupar por mes, año, etc, o texto.
    """
    toggle_numeric = st.toggle(label = "Group all numbers", value=True, key="toggle_metrics")
    
    columnas_agregacion = core_object.numeric_columns
    columnas_categoricas = list(dict.fromkeys(core_object.non_numeric_columns))
    
    col_1, col_2 = st.columns([1, 4], border=True)
    with col_1:
        st.write("Elija la columna de texto a agrupar")
        col_nombre = st.selectbox(label="Elija columna de texto a agrupar", options=columnas_categoricas,
            key="col_nombre", placeholder="Select a column", label_visibility ="collapsed")
    
    with col_2:
        st.write("Elija la columna numérica o de fecha a agrupar")
        col_numero = st.multiselect(label="Elija columna numérica a agrupar", options=columnas_agregacion,
            key="col_numero",placeholder="Select a column",label_visibility="collapsed",
            disabled=toggle_numeric
        )
        if toggle_numeric == True:
            col_numero = columnas_agregacion
        
    ##Agrupamos
    st.divider()
    if "df_group" not in ss:
        ss.df_group = None
    if st.button(label="Run",key="button_run"):
        st.write("Hi")
        
    
    # st.selectbox(label, options, index=0, format_func=special_internal_function, 
    # key=None, help=None, on_change=None, args=None, kwargs=None, *, placeholder=None, 
    # disabled=False, label_visibility="visible", accept_new_options=False, filter_mode="fuzzy", width="stretch", bind=None)
    
    
    

def workspace_render():
    ##Variables iniciales
    ss = st.session_state
    
    ##Contiene si la página es ancha o centrada
    if "layout" not in ss: 
        ss.layout = "centered"
    lista_keep = ["page","workspace_view","layout"] ##Lista de cosas que no quiero perder al cambiar de página
    
    st.set_page_config(layout=ss.layout)
    
    
    print("Pasamos a excel workspace, no limpiamos keys al manejarse con diversas páginas internas")
    keep_keys = []
    
    ##sesion state que indica qué 
    if "workspace_view" not in ss:
        ss.workspace_view = "menu"
    
    if ss.workspace_view == "menu":
        ui.clear_page_state(keep_keys=lista_keep)
        st.write(ss)
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
    ##Muestra los botones con su texto en la página principal del excel workspace
        for opcion in opciones:
            col_btn, col_text = st.columns([1, 4], border=True)
            with col_btn:
                if st.button(opcion["boton"], width="stretch"):
                    ui.clear_page_state(keep_keys=lista_keep)
                    ss.workspace_view = opcion["vista"]
                    st.rerun()
            with col_text:
                st.write(opcion["texto"])
            
    ##Se llama a las funciones con tools específicas
    elif ss.workspace_view == "agrupar":
        agrupar_datos()
    
    
    
    st.stop()
    
    
    


if __name__ == "__main__":
    workspace_render()