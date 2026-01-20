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
    if label is None:
        label = "Selecciona el archivo de Excel o CSV"
    archivo_base = st.file_uploader( ##Devuelve un archivo en memoria.
        label,
        type=["csv", "xlsx", "xlsm"],
        key = key
        )
    
    
    if not archivo_base:
        return None, None
    
    # archivo_id = getattr(archivo_base, "name", None)  # <- ID estable del upload
    archivo_id = archivo_base.name
    
    archivo_leido = core.load_file(archivo_base)
    return archivo_leido, archivo_id