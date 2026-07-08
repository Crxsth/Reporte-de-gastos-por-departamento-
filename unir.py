import streamlit as st
import sys
import core
import pandas as pd
import other_ui as ui
import time


def unir_render():
    ss = st.session_state
    st.write(ss)
    print(f"Tiempo rerun: {time.time()}")
    
    ##ss cleaner:
    # lista_keep = [] ##Lista de cosas que no quiero perder al cambiar de página
    # ui.clear_page_state(keep_keys=lista_keep)
    
    ##Subimos los archivos
    archivos = st.file_uploader("Seleccionar archivo(s) Excel o csv", 
        type=["csv","xlsx","xlsm"], accept_multiple_files=True,key ="unir_subir_archivos")
    if len(archivos) == 0:
        st.stop()
    
    ##Comentarios e instrucciones para el usuario
    with st.expander("¿Cómo usar esta sección?", expanded=True):
        st.markdown(
            """
            1. Sube uno o varios archivos CSV o Excel.
            2. Si el archivo es Excel, selecciona la hoja que quieres leer.
            3. Revisa cada archivo antes de continuar.
            4. Cuando termines, usa el botón para unir los archivos.
            """
        )
    
    ##Creamos dict: dataframes = {nombre:archivo_bytes}
    if archivos: ##archivos es lista [archivo_bytes] (Que es un objeto streamlit)
        dataframes = {}
        for archivo_bytes in archivos:
            dataframes[archivo_bytes.name] = archivo_bytes
    # st.write(f"Dataframes {dataframes}")
    
    ##Diccionario que almacena {"archivo_bytes":"hoja_preferida"}
    if "unir_read_config" not in ss:
        ss.unir_read_config = dataframes.copy()
        for key in ss.unir_read_config:
            ss.unir_read_config[key] = 0
    
    ##Columnas select_boxes = [col1:archivo, col2:sheet_names]
    col1, col2 = st.columns([3,1])
    with col1:
        df_name = st.selectbox(label="See your files",options=list(dataframes), 
            key = "unir_selectbox_seefiles")
        df_st_object = dataframes[df_name]
    with col2:
        if df_name.endswith((".xlsx",".xlsm")):
            hojas = core.get_sheet_names(df_st_object)
            sheet = st.selectbox(label="Select sheet", options = hojas, 
                key= "unir_selectbox_seesheets")
            ss.unir_read_config[df_name] = sheet
    
    ##Diccionario que almacenará {"Nombre":df}
    if "unir_loaded_dataframes" not in ss:
        ss.unir_loaded_dataframes = dataframes.copy()
        for key in ss.unir_loaded_dataframes:
            ss.unir_loaded_dataframes[key] = 0
    
    ##Cargamos los archivos; esto varía según los componentes interactivos anteriores
    df= core.load_file(df_st_object, hoja=sheet)
    core_object = core.ReporteDf(df, name=df_name).fix_header()
    core_object.fix_dates()
    core_object.fix_numbers()
    df = core_object.df
    ui.vista_previa(df, titulo=df_name, key= "df_var_shown", n_max=len(df))
    
    ##Tratamos de actualizar loaded_dataframes
    ss.unir_loaded_dataframes[df_name] = df

    st.divider()
    
    #Unimos 
    if st.button(label="Unir Archivo", key="unir_button_run", width=200):
        for df_name in ss.unir_loaded_dataframes:
            if not isinstance(ss.unir_loaded_dataframes[df_name], pd.DataFrame):
                df_st_object = dataframes[df_name] ## Obtenemos el archivo streamlit desde dataframes
                sheet = ss.unir_read_config[df_name] ## Obtenemos la hoja configurada
                
                df = core.load_file(df_st_object, hoja=sheet)
                core_object = core.ReporteDf(df, name=df_name).fix_header()
                core_object.fix_dates()
                core_object.fix_numbers()
                ss.unir_loaded_dataframes[df_name] = core_object.df

        st.write("Día de fiesta :)")
        st.stop()
        dfs_para_unir = []
        for nombre_archivo, df in dataframes.items():
            df_temp = df.copy()
            df_temp["source_file"] = nombre_archivo
            dfs_para_unir.append(df_temp)
        
        df_unido = pd.concat(dfs_para_unir, ignore_index=True)
        ui.vista_previa(df_unido, titulo="Archivo unido", key= "df_unido", n_max=len(df_unido))