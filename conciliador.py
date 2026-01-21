import streamlit as st
import sys
import core
import other_ui as ui


def init_rows():
    ss = st.session_state
    if "rows" not in ss:
        ss.rows = [0]  # 1 fila inicial


def add_row():
    ss = st.session_state
    ss.rows.append(len(ss.rows))  # agrega una fila más (idx nuevo)


def delete_row():
    ss = st.session_state
    ss.rows.pop()


def select_df1(df, idx):
    opciones = list(df.columns)
    return st.selectbox("", opciones, key=f"df1_col_{idx}", label_visibility="collapsed")


def select_df2(df, idx):
    opciones = list(df.columns)
    return st.selectbox("", opciones, key=f"df2_col_{idx}", label_visibility="collapsed")


def extra_match(idx):
    opciones = ["="]
    return st.selectbox("", opciones, key=f"extra_match_{idx}", label_visibility="collapsed")


def render_conciliate():
    ss = st.session_state

    ##File uploader
    col_data_base, col_data_bank = st.columns(2)
    with col_data_base:
        df_base, base_id = ui.obtener_dataframe( key="base")
    with col_data_bank:
        df_bank, bank_id = ui.obtener_dataframe(key="banco")
        if df_bank is None: st.stop()

    if df_base is None or df_bank is None:
        st.stop()
    
    if "base_id" not in ss: ##Lo inicializamos si no existía
        ss.base_id = None
    if bank_id not in ss:
        ss.bank_id = None
    
    ##Creamos obj para normalizar datos
    archivo_base = core.ReporteDf(df_base).fix_dates().fix_numbers()
    archivo_bank = core.ReporteDf(df_bank).fix_dates().fix_numbers()
    df_base = archivo_base.df
    df_bank = archivo_bank.df
    
    ##Componentes interactivos
    st.divider()
    init_rows() ##Inicializa {n} selectbox
    space1, space2 = st.columns(2)
    
    ##Botones
    with space1:
        if st.button("Agregar fila"):
            add_row()
    with space2:
        if st.button("Eliminar fila"):
            delete_row()

    
    ##Esto crea los selectboxes
    h1, h2, h3 = st.columns(3)
    h1.markdown("**Datos Base**")
    h3.markdown("**Match Type**")
    h2.markdown("**Datos bancarios**")
    
    for idx in st.session_state.rows:
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                select_df1(df_base, idx)  # ✅ idx auto, estable
            with col2:
                extra_match(idx)
            with col3:
                select_df2(df_bank, idx)
            

    st.button("Run", key="inicializador")
    
    ##Lógica de conciliación
    n = len(ss.rows)
    df_bank["prob"] = 0
    df_copy = df_bank.copy()
    if not "bank_copies" in ss:##Almacena los df_copy de cada iteración per amount
        ss.bank_copies = []
    ss.bank_copies.clear()
    
    
    st.write(f"Ene we : {n}")
    for row in ss.rows:
        
        base_col = ss.get(f"df1_col_{row}")
        bank_col = ss.get(f"df2_col_{row}")
        st.write(f"{base_col} - {bank_col} & {row}")
        
        # st.write(f"{archivo_base.df[base_col]}")
        st.write("Empezamos bucle")
        
        for i in range(0, len(df_base[base_col])):
            df_var = df_copy.copy()
            df_var["base_index"] = i ##una serie con el número {i} para no perdernos
            valor = df_base.loc[i, base_col]
            # print(f"valor buscado: {valor}")
            st.write(f"valor buscado: {valor}")
            ss.bank_copies.append(df_var)
            count = 0
            for j in range(0, len(df_var[bank_col])):
                valor_posible = df_var.loc[j, bank_col]
                if valor == valor_posible:
                    df_var.loc[j,"prob"] = df_var.loc[j, "prob"] + 1
                    st.write(f"Matches: {valor_posible}")
            for i, dato in enumerate(df_var["prob"]):
                if dato>0:
                    print(f"{i} - {dato}")
            if count ==0:
                print("NADA WE")
            
            break
            # st.write(valor)
            # break
        
        
        break
        

if __name__ == "__main__":
    render_conciliate()