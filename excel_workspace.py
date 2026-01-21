import streamlit as st
import sys
import core
import other_ui as ui

    
def vista_previa(df, n_default=20, titulo=None, key=None):
    """
    Muestra una vista previa de los datos en Streamlit.

    Args:
        df (pd.DataFrame): conjunto de datos a visualizar.
        n_default (int): número inicial de filas a mostrar (default=20).
    """
    col_dict = {}
    if titulo is None: titulo="Vista Previa"
    st.subheader(titulo)
    for col in df.columns:
        if "amount" in col.lower():
            col_dict[col] = st.column_config.NumberColumn(col, format="$%.2f")
    
    key_flag = f"show_preview_{key}" ##Clave de estado
    if key_flag not in st.session_state: ##Inicializa la key
        st.session_state[key_flag] = True
    
    if st.button("Vista previa"): ##Alterna el valor al presionar
        st.session_state[key_flag] = not st.session_state[key_flag]
    
    if st.session_state[key_flag] == True: ##Decide que mostrar, ejemplo if st.ss.key_flag = True: muestra lo de abajo.
        n_rows = st.slider("Número de filas a mostrar",5,100,n_default,5)
        st.dataframe(df.head(n_rows), column_config=col_dict, hide_index=True)
        
def workspace_render():
    archivo_base, archivo_id = ui.obtener_dataframe() ##Lee un [csv, xlsx, xlsm] y retorna un dataframe con los datos
    ss = st.session_state
    
    if archivo_base is None:
        st.stop()
    if "archivo_id" not in ss: ##Lo inicializamos si no existía
        ss.archivo_id = None
    resultado = archivo_id.rsplit(".", 1)[0] #Obtener el name sin .xlsx
    
    # st.dataframe(archivo_base)

    vista_previa(archivo_base, n_default=20, titulo=resultado,key=archivo_id)
    
    


if __name__ == "__main__":
    workspace_render()