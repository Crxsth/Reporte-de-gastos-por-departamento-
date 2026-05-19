import streamlit as st
import sys
import core
import other_ui as ui

   
DEV_MODE = True

   
def workspace_render():
    ss = st.session_state
    st.write("El objetivo de esta página es reducir el trabajo manual en archivos excel")
    st.divider()
    
    # st.write(ss)
    ##Permite añadir un archivo
    if DEV_MODE == True:
        ruta_dev = r"C:\Users\criis\Documents\Coding\Report\Tests\Datos_base.csv"
        archivo_base = core.load_file(ruta_dev)
        archivo_id = "Datos_base.csv"
    else:
        archivo_base, archivo_id = ui.obtener_dataframe(label="Data", key="base")
        if "last_uploaded_file_base" not in st.session_state:
            st.session_state.last_uploaded_file_base = None

        if archivo_id is not None and archivo_id != st.session_state.last_uploaded_file_base:
            st.write("Archivo añadido correctamente")
            st.session_state.last_uploaded_file_base = archivo_id
    
    ##Ejecuta la vista previa
    if archivo_base is not None:
        with st.container(border=True):
            # vista_previa(archivo_base, titulo="Su archivo se muestra aquí", key=archivo_id)
            core_obj_df_fixed = core.ReporteDf(archivo_base,name="Data_fixed").fix_header() ##Este es el archivo base, detectando header
            try:
                core_obj_df_fixed.fix_dates().fix_numbers()
            except:
                print("No se pudo convertir en fecha y número")
            df_fixed = core_obj_df_fixed.df
            ui.vista_previa(df_fixed,titulo=f"Mostrando: {archivo_id}", key="data_fixed", n_max=len(df_fixed))
    else:
        st.write("No hay archivo todavía")
    
    
    st.stop()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("My name is")
    with col2:
        st.write("My name is")
    with col3:
        st.write("My name iss")
    with col4:
        st.write("Slim shady")
    
    


if __name__ == "__main__":
    workspace_render()