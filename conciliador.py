import streamlit as st
import sys
import core
import other_ui as ui


def select_df1(df):
    st.dataframe(df)
    
    
    
def render_conciliate():
    ss = st.session_state
    
    col_data_base, col_data_bank = st.columns(2)
    with col_data_base:
        df_base, base_id = ui.obtener_dataframe( key="base")
        if df_base is None: st.stop()
        
    with col_data_bank:
        df_bank, bank_id = ui.obtener_dataframe(key="banco")
        if df_bank is None: st.stop()

    # if df_base is None or df_bank is None:
        # st.info("Sube ambos archivos para continuar.")
        # st.stop()
    
    if "base_id" not in ss: ##Lo inicializamos si no existía
        ss.base_id = None
    if bank_id not in ss:
        ss.bank_id = None
    
    st.write("Here:")
    select_df1(df_base)
    
if __name__ == "__main__":
    render_conciliate()