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
    
    
def vista_previa(df, n_default=20, titulo=None, key=None, n_max=100, n_min=5):
    """Muestra una vista previa controlada del DataFrame."""
    
    if titulo is None:
        titulo = "Vista Previa"

    st.subheader(titulo)

    total_rows = len(df)

    if total_rows == 0:
        st.info("El archivo no tiene filas para mostrar.")
        return

    min_rows = min(n_min, total_rows)
    max_rows = min(n_max, total_rows)
    default_rows = min(n_default, max_rows)

    n_rows = st.slider(
        "Número de filas a mostrar",
        min_value=min_rows,
        max_value=max_rows,
        value=default_rows,
        step=5,
        key=f"slider_preview_{key}"
    )

    st.dataframe(df.head(n_rows), hide_index=True)


def clear_page_state(keep_keys=None):
    ss = st.session_state

    if keep_keys is None:
        keep_keys = []

    # Keys globales que no se deben borrar
    keep_keys = set(keep_keys)
    keep_keys.add("page")
    keep_keys.add("last_page")

    # Página actual controlada por el router
    current_page = ss.get("page", None)

    # Si aún no hay página, no hace nada
    if current_page is None:
        print("Esto es none")
        return

    # Primera ejecución: guarda la página actual
    if "last_page" not in ss:
        print("Esto es not in")
        ss.last_page = current_page
        return

    # Si cambió de página, limpia session_state
    if ss.last_page != current_page:
        print("Pues esto otro")
        keys_to_delete = []

        # Guarda las keys que sí se van a borrar
        for key in list(ss.keys()):
            if key not in keep_keys:
                keys_to_delete.append(key)

        # Borra las keys no globales
        for key in keys_to_delete:
            del ss[key]

        # Actualiza la última página visitada
        ss.last_page = current_page