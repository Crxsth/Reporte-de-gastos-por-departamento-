import streamlit as st
import core


def obtener_dataframe(texto= None, key=None, label=None): ##Function that selects a file to work with. 
    """
    Abre un selector de archivos en Streamlit y llama al core para cargar el archivo.

    Soporta archivos .csv, .xlsx y .xlsm.  
    Si es CSV, lo lee con codificación 'latin-1'.  
    Si es Excel, usa la función personalizada `leer_file()`.
    Returns:
        Datos cargados desde el archivo.
    """
    ss = st.session_state
    if label is None:
        label = "Selecciona el archivo de Excel o CSV"
    archivo_base = st.file_uploader( ##Devuelve un archivo en memoria.
        label,
        type=["csv", "xlsx", "xlsm"],
        key = key
        )
    
    
    if not archivo_base:
        st.info("Sube un archivo para continuar") 
        return None, None
    
    archivo_id = getattr(archivo_base, "file_id", None) or getattr(archivo_base, "name", None)

    ##Keys:
    df_key = f"df_{key}"
    id_key = f"id_{key}"
    
    ##Si existe el archivo, no se reele
    if (df_key in ss) and (ss.get(id_key) == archivo_id):
        return ss[df_key], archivo_id
    
    ##Lectura
    archivo_leido = core.load_file(archivo_base)
    archivo_id = archivo_base.name
    
    ss[df_key] = archivo_leido
    ss[id_key] = archivo_id
    
    return archivo_leido, archivo_id