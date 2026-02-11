import streamlit as st
import sys
import core
import other_ui as ui

from pathlib import Path
import pandas as pd

DEV_MODE = True  # ⬅️ cambia a False cuando ya no lo quieras

DEV_PATH = Path(r"C:\Users\criis\Documents\Coding\Conciliation")
DEV_BASE = DEV_PATH / "Datos1.csv"
DEV_BANK = DEV_PATH / "Datos_banco.csv"


def init_rows():
    ss = st.session_state
    if "rows" not in ss:
        ss.rows = [0,1]  # 1 fila inicial


def add_row():
    ss = st.session_state
    # ss.rows.append(len(ss.rows))  # agrega una fila más (idx nuevo)
    ss.rows.append(max(ss.rows)+1)  # agrega una fila más (idx nuevo)


def delete_row():
    ss = st.session_state
    if len(ss.rows) >1:
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


def render_advanced_rules():
    ##Const
    ss = st.session_state
    df_base = ss.get("df_base")
    df_bank = ss.get("df_banco")
    ##Titles
    h1, h2, h3 = st.columns(3)
    h1.markdown("**Datos Base**")
    h3.markdown("**Match Type**")
    h2.markdown("**Datos bancarios**")
    
    ##Componentes
    init_rows() ##Inicializa {n} selectbox
    for idx in st.session_state.rows:
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                select_df1(df_base, idx)  # ✅ idx auto, estable
            with col2:
                extra_match(idx)
            with col3:
                select_df2(df_bank, idx)
    
    
    ##Botones añadir / delete
    space1, space2 = st.columns(2)
    with space1:
        if st.button("Agregar fila"):
            add_row()
            st.rerun()
    with space2:
        if st.button("Eliminar fila"):
            delete_row()
            st.rerun()


def render_simple_rules():
    ##Const
    ss = st.session_state
    df_base = ss.get("df_base")
    df_bank = ss.get("df_banco")
    
    ##3 buttons
    title1, title2, title3 = st.columns(3)
    with title1:
        st.button("Perfect match", key="title1_match", width="stretch")
    with title2:
        st.button("Suma",key="title2_suma", width="stretch")
    with title3:
        st.button("All", key="title3_all", width="stretch")
    
    
    ##Titles
    h1, h2 = st.columns(2)
    h1.markdown("**Datos Base**")
    h2.markdown("**Datos bancarios**")
    
    ##Componentes
    init_rows() ##Inicializa {n} selectbox
    for idx in st.session_state.rows:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                select_df1(df_base, idx)
            with col2:
                select_df2(df_bank, idx)


def render_conciliate():
    ss = st.session_state
    
    ##File uploader
    col_data_base, col_data_bank = st.columns(2)
    
    if "first_run" not in ss:
        ss.first_run = True
    
    ##Toggle para cambiar la visualización
    if "advanced_settings" not in ss:
        ss.advanced_settings = False
    st.toggle(label="Advanced settings", key="advanced_settings", help="Allows you to create specific searches")
    
    if DEV_MODE == True:## Lector de archivos
        if "df_base" not in ss:
            ss.df_base = pd.read_csv(DEV_BASE)
        if "df_banco" not in ss:
            ss.df_banco = pd.read_csv(DEV_BANK)
        
        df_base = ss.df_base
        df_bank = ss.df_banco
    
    else:
        with col_data_base:
            df_base, base_id = ui.obtener_dataframe(label="Database data", key="base")
        with col_data_bank:
            df_bank, bank_id = ui.obtener_dataframe(label="Bank data",key="banco")
            if df_bank is None: st.stop()
    st.write(ss)
    
    if df_base is None or df_bank is None:
        st.stop()
    
    if "base_id" not in ss: ##Lo inicializamos si no existía
        ss.base_id = None
    if "bank_id" not in ss:
        ss.bank_id = None
    
    ##Creamos obj para normalizar datos
    archivo_base = core.ReporteDf(df_base).fix_dates().fix_numbers()
    archivo_bank = core.ReporteDf(df_bank).fix_dates().fix_numbers()
    df_base = archivo_base.df
    df_bank = archivo_bank.df
    
    
    ##Si es la primera vez, coloca estos por default
    if ss.first_run == True: ##Esto pone por default 2 columnas, sino pues no
        try:
            
            date_col = next(x for x in df_base.columns if "date" in x.lower()) ##Obtenemos la columna con la palabra 'date'
            ss["df1_col_0"] = next(c for c in df_base.columns if "date" in c.lower())
            ss["df2_col_0"] = next(c for c in df_bank.columns if "date" in c.lower())
            
            ss["df1_col_1"] = next(c for c in df_base.columns if "amount" in c.lower())
            ss["df2_col_1"] = next(x for x in df_bank.columns if "amount" in x.lower())
            ss.first_run = False  # 🔒
        except Exception as e:
            st.write(e)
            st.write("Pues no sé we, algo salió mal")
            
    ##Aquí se llama a las funciones que renderizan todo en advanced or not
    st.divider()
    if ss.advanced_settings:
        render_advanced_rules()
    else:
        render_simple_rules()    
    
    
    

    st.button("Run", key="inicializador")
    
    ##Lógica de conciliación
    n = len(ss.rows)
    
    df_copy = df_bank.copy()
    if not "bank_copies" in ss:##Almacena los df_copy de cada iteración per amount
        ss.bank_copies = []
    ss.bank_copies.clear()
    st.divider()
    
    ##No quitar. Estos valores son obtenidos en los selectboxes y se almacenan en el 'ss'
    base_cols = [ss[f"df1_col_{i}"] for i in ss.rows]
    bank_cols = [ss[f"df2_col_{i}"] for i in ss.rows]

    if 1>0:
        result = core.conciliador(
            df_base=df_base,
            df_bank=df_bank,
            base_cols=base_cols,
            bank_cols=bank_cols
            )
    
    bool_var = False
    if bool_var ==True:
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