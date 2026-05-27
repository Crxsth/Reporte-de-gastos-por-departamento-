import streamlit as st
import sys
import core
import other_ui as ui

   
def workspace_render():
    ss = st.session_state
    st.set_page_config(layout="wide")
    st.write("El objetivo de esta página es reducir el trabajo manual en archivos excel")
    
    print("Limpiamos keys, pasamos a excel workspace")
    keep_keys = []
    ui.clear_page_state()
    # ui.clear_page_state(
        # current_page="excel_workspace",
        # keep_keys=["page", "current_page"]
    # )
    DEV_MODE = False
    
    # st.divider()
    
    # st.write(ss)
    ##Permite añadir un archivo
    st.write(f"Dev mode bro: {DEV_MODE}")
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
    
    
    st.stop()
    
    
    


if __name__ == "__main__":
    workspace_render()