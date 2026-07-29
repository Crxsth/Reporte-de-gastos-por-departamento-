import streamlit as st
import sys
import core
import pandas as pd
import other_ui as ui
import os
import time


def unir_render():
    ss = st.session_state
    col_title1, col_title2 = st.columns(2)
    with col_title1:
        usar_ejemplo = st.toggle(
            "Cargar ejemplo",
            key="unir_cargar_ejemplo",
            help="Carga archivos de demostración para conocer el funcionamiento del módulo."
        )
    with col_title2:
        st.write(ss)
        
    print(f"Tiempo rerun: {time.time()}")
    
    ##ss cleaner:
    # lista_keep = [] ##Lista de cosas que no quiero perder al cambiar de página
    # ui.clear_page_state(keep_keys=lista_keep)
    
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
    
    ##Subimos los archivos
    archivos = st.file_uploader("Seleccionar arc<hivo(s) Excel o csv", 
        type=["csv","xlsx","xlsm"], accept_multiple_files=True,key ="unir_subir_archivos")
    
    ##Funciona con el toggle para cargar archivos de prueba
    if ss.unir_cargar_ejemplo==True:
        ruta = os.path.join(os.getcwd(), "Tests")
        archivo1 = os.path.join(ruta, "Ejemplo Datos_5000_rows.xlsm")
        archivo2 = os.path.join(ruta, "Ejemplo Datos_50_rows.xlsm")
        archivos = [archivo1, archivo2]
    # st.write(f"Toggle: {ss.unir_cargar_ejemplo}")
    
    if len(archivos) == 0:
        st.stop()
    
    
    ##Creamos dict: dataframes = {nombre:archivo_bytes}
    if archivos: ##archivos es lista [archivo_bytes] (Que es un objeto streamlit)
        dataframes = {}
        for archivo_bytes in archivos:
            if isinstance(archivo_bytes,str):
                nombre = os.path.basename(archivo_bytes)
                dataframes[nombre] = archivo_bytes
            else:
                dataframes[archivo_bytes.name] = archivo_bytes
        ss.dataframes = dataframes
    # st.write(f"Dataframes {dataframes}")
    
    ##Diccionario que almacena {"archivo_bytes":"hoja_preferida"}
    if "unir_read_config" not in ss:
        ss.unir_read_config = dataframes.copy()
        for key in ss.unir_read_config:
            ss.unir_read_config[key] = 0
    
    ##Nombres de los dataframes
    nombres_df = list(dataframes)
    ss.nombres_df = nombres_df
    ##Columnas select_boxes = [col1:archivo, col2:sheet_names]
    col1, col2 = st.columns([3,1])
    with col1:
        df_name = st.selectbox(label="See your files",options=nombres_df, 
            key = "unir_selectbox_seefiles")
        df_st_object = dataframes[df_name]
    with col2:
        if df_name.endswith((".xlsx",".xlsm")):
            hojas = core.get_sheet_names(df_st_object)
            sheet = st.selectbox(label="Select sheet", options = hojas, 
                key= "unir_selectbox_seesheets")
            ss.unir_read_config[df_name] = sheet
        else:
            sheet = 0
    
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
    ss.unir_loaded_dataframes[df_name] = df ##Esto guarda el df anterior/ visualizado en el ss, para actualizar básicamente

    st.divider()
    
    #Unimos
    if "df_unido" not in ss:
        ss.df_unido = None
    col_button1, col_button2 = st.columns(2)
    
    ##Columnas con botón Run & toggle para colocar indicador
    button_run = st.button(label="Unir Archivo", key="unir_button_run", width=200)  ##Botón que ejecuta la unión
    
    ##Bucle que hace la unión
    if button_run:
        ##Bucle que añaded a la 'ss.unir_loaded_dataframes' los df en caso dee que falte alguno
        for df_name in ss.unir_loaded_dataframes: ##Recorremos los df almacenados aquí
            if not isinstance(ss.unir_loaded_dataframes[df_name], pd.DataFrame): ##Revisamos si el valor en esta variable contiene un df
                df_st_object = dataframes[df_name] ## Obtenemos el archivo streamlit desde dataframes
                sheet = ss.unir_read_config[df_name] ## Obtenemos la hoja configurada
                ##Leemos, limpiamos df y lo colocamos en la lista de df
                df = core.load_file(df_st_object, hoja=sheet)
                core_object = core.ReporteDf(df, name=df_name).fix_header()
                core_object.fix_dates()
                core_object.fix_numbers()
                ss.unir_loaded_dataframes[df_name] = core_object.df

        ##Prepara para unir  
        dfs_para_unir = []
        for nombre_archivo, df in ss.unir_loaded_dataframes.items():
            df_temp = df.copy()
            if os.path.dirname(nombre_archivo):
                nombre_archivo = os.path.basename(nombre_archivo)
            df_temp["source_file"] = nombre_archivo ##Agregamos una columna para saber de qué archivo vino cada fila
            dfs_para_unir.append(df_temp)
        
        ##Hace la unión
        df_unido = pd.concat(dfs_para_unir, ignore_index=True) ##Une los dataframes
        ss.df_unido = df_unido
    
    if ss.df_unido is not None:
        df_unido = ss.df_unido
        ui.vista_previa(df_unido, titulo="Archivo unido", key= "df_unido", n_max=len(df_unido))
        
        archivo_csv = df_unido.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="Descargar archivo unido",
            data=archivo_csv,
            file_name="archivo_unido.csv",
            mime="text/csv",
            key="unir_download_csv", width=300
        )