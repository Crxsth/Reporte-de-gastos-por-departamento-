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
        type=["csv","xlsx","xlsm"], accept_multiple_files=True,key ="unir_archivos")
    if len(archivos) == 0:
        st.stop()
    
    ##Leemos y almacenamos en un diccionario los archivos subidos
    if archivos:
        dataframes = {}

    for archivo in archivos:
        # hojas = core.get_sheet_names(archivo)
        # st.write(f"Usando: {archivo}")
        # st.write(hojas)
        # st.stop()
        df = core.load_file(archivo)
        core_object = core.ReporteDf(df, name=archivo.name).fix_header()
        core_object.fix_dates()
        core_object.fix_numbers()
        df = core_object.df
        dataframes[archivo.name] = df ##Este es un diccionario que guarda {texto:dataframe}, útil
    
    ##Componente para revisar los archivos subidos
    st.divider()
    df_name = st.selectbox(label="See your files",options=list(dataframes.keys()), 
        key="unir_button_selectbox_dataframesBase")
    df = dataframes[df_name]

    ui.vista_previa(df, titulo=df_name, key= "df_var_shown", n_max=len(df))
    
    ##Unimos 
    if st.button(label="Unir Archivo", key="button_run", width=200):
        dfs_para_unir = []
        for nombre_archivo, df in dataframes.items():
            df_temp = df.copy()
            df_temp["source_file"] = nombre_archivo
            dfs_para_unir.append(df_temp)
        
        df_unido = pd.concat(dfs_para_unir, ignore_index=True)
        ui.vista_previa(df_unido, titulo="Archivo unido", key= "df_unido", n_max=len(df_unido))