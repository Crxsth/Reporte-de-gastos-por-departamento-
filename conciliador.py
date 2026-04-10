import streamlit as st
import sys
import core
import other_ui as ui
from pathlib import Path
import pandas as pd
import time

DEV_MODE = False  # ⬅️ cambia a False cuando ya no lo quieras

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
    """
    Crea selectboxes para elegir columna del DataFrame base
    u\200B es un label invisible para evitar warnings
    """
    opciones = list(df.columns)
    return st.selectbox("\u200B", opciones, key=f"df1_col_{idx}", label_visibility="collapsed")
    # return st.selectbox(f"df1_col_{idx}", opciones, key=f"df1_col_{idx}")


def select_df2(df, idx):
    ##Crea selectbox para elegir columna de DFBanco #\200B = string invisible
    opciones = list(df.columns)
    return st.selectbox("\u200B", opciones, key=f"df2_col_{idx}", label_visibility="collapsed")
    # return st.selectbox(f"df2_col_{idx}", opciones, key=f"df2_col_{idx}")


def extra_match(idx):
    opciones = ["="]
    return st.selectbox("", opciones, key=f"extra_match_{idx}", label_visibility="collapsed")


def render_advanced_rules():
    ##Const
    ss = st.session_state
    df_base = ss.get("df_base")
    df_bank = ss.get("df_bank")
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


def render_simple_rules():
    ##Const
    ss = st.session_state
    df_base = ss.get("df_base")
    df_bank = ss.get("df_bank")
    st.write(f"Columnas del banco: {df_bank}")
    
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
    print()
    t0 = time.time()
    hora = time.strftime("%H:%M:%S", time.localtime(t0))
    print(f"Rerun starts here: {hora}")
    
    ##File uploader
    col_data_base, col_data_bank = st.columns(2)
    
    if "first_run" not in ss:
        ss.first_run = True
    
    ##Toggle para cambiar la visualización
    if "advanced_settings" not in ss:
        ss.advanced_settings = False
    st.toggle(label="Advanced settings", key="advanced_settings", help="Allows you to create specific searches")
    st.write(ss)
    
    ## Lector de archivos
    if DEV_MODE == True:
        # if "base" not in ss:
            # ss.base = core.load_file(DEV_BASE)
        df_base_raw = core.load_file(DEV_BASE)
        # if "banco" not in ss:
            # ss.banco = core.load_file(DEV_BANK)
        df_bank_raw = core.load_file(DEV_BANK)
        # df_base_raw = ss.base 
        # df_bank_raw = ss.banco
    else:
        with col_data_base:
            df_base_raw, base_id = ui.obtener_dataframe(label="Database data", key="base")
        with col_data_bank:
            df_bank_raw, bank_id = ui.obtener_dataframe(label="Bank data",key="banco")
            if df_bank_raw is None: st.stop()
    
    
    if df_base_raw is None or df_bank_raw is None:
        st.stop()
    
    if "base_id" not in ss: ##Lo inicializamos si no existía
        ss.base_id = None
    if "bank_id" not in ss:
        ss.bank_id = None
    
    ##Creamos obj para normalizar datos
    # print(df_base_raw)
    archivo_base = core.ReporteDf(df_base_raw).fix_header().fix_dates().fix_numbers()
    df_base = archivo_base.df    
    archivo_bank = core.ReporteDf(df_bank_raw).fix_header().fix_dates().fix_numbers()
    df_base = archivo_base.df
    df_bank = archivo_bank.df
    ss.df_base = df_base
    ss.df_bank = df_bank
    
    
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
    # st.stop()
    if ss.advanced_settings:
        render_advanced_rules()
    else:
        render_simple_rules()    
    
    ##Botones añadir / eliminar componentes interactivos
    col_add, col_del = st.columns(2)
    ancho = "stretch"
    with col_add:
        if st.button("Agregar fila", key="add_rule_row", width=ancho):
            add_row()
            st.rerun()
    with col_del:
        if st.button("Eliminar fila", key="delete_rule_row", width=ancho):
            delete_row()
            st.rerun()
    
    ##Esto llama al conciliador
    # Inicializar estado
    if "conciliado" not in ss:
        ss.conciliado = False
    if "df_max_result" not in ss:
        ss.df_max_result = None
    if "df_result_full" not in ss:
        ss.df_result_full = None
    st.divider()
    if st.button("Run", key="inicializador", width=200):
        
        ss.conciliado = True
        ##Columnas a comparar 
        base_cols = [ss[f"df1_col_{i}"] for i in ss.rows]
        bank_cols = [ss[f"df2_col_{i}"] for i in ss.rows]
        ##Llamada al conciliador
        with st.spinner("Conciliando datos... "):
            df_result, df_max = core.conciliador(
                df_base=df_base,
                df_bank=df_bank,
                base_cols=base_cols,
                bank_cols=bank_cols
            )
        """Merge los df: 
            df_result: bank[bank_cols], bridge, base[base_cols]
            df_max: df_result[match_score].max()
            df_conciliation: bank, bridge, base"""
        df_result, df_max, df_conciliation = core.build_review_df(bridge, df_bank, df_base, bank_cols, base_cols)
        
        df_matches = df_base.join(
            df_max.set_index("base_idx")[["match_score"]],
            how="left"
        )
        df_unmatched = df_matches[
            df_matches["match_score"].isna() | (df_matches["match_score"] == 0)
        ]
        
        ss.df_result = df_result ##all match >0
        ss.df_max = df_max ##max (match)
        ss.df_matches = df_matches
        ss.df_unmatched = df_unmatched
        
    ##Hacemos un merge de banco > ERP
    
    if ss.conciliado==True and ss.df_max is not None:
        st.dataframe(ss.df_max)
        
        st.success("Se han hecho conciliaciones, elija los archivos que desee descargar")
        st.info(
        """Para hacer la conciliación se revisan y comparan las transacciones basado en las columnas seleccionadas.
        Luego se eligen las transacciones con puntajes más altos.
        """)
        df_result = ss.df_result
        df_matches = ss.df_matches
        df_unmatched = ss.df_unmatched
        df_result_bytes = df_result.to_csv(index=False).encode("utf-8")
        df_matches_bytes = df_matches.to_csv(index=False).encode("utf-8")
        df_unmatched_bytes = df_unmatched.to_csv(index=False).encode("utf-8")
        
        st.divider()
        result1, result2, result3 = st.columns(3)
        # result1, result2 = st.columns(2)
        with result1:
            clicked = st.download_button(
                label= "Descargar archivo 'Possible_matches' / 'df_result'",
                data= df_result_bytes, 
                file_name = "Possible_matches.csv",
                mime= "text/csv",
                key="download_df_result",
                help= "Archivo que contiene todas las posibles coincidencias",
                width="stretch"
            )
            st.info("Este archivo contiene las posibles coincidencias entre el ERP y el banco.")
            if clicked:
                st.success("Descargando...")
        with result2:
            clicked2 = st.download_button(
                label = "Descargar 'Archivo base con matches'",
                data = df_matches_bytes,
                file_name = "Matched file.csv",
                key="download_df_matches",
                help="Archivo base con el añadido del match más probable",
                width="stretch"
            )
            st.info("Este archivo contiene su archivo 'base' y tendrá columna con valores a la derecha del mismo")
            if clicked2:
                st.success("Descargando...")
        with result3:
            clicked3 = st.download_button(
                label = "Descargar 'Unmatched' data",
                data = df_unmatched_bytes,
                file_name = "Unmatched data.csv",
                mime= "text/csv",
                key = "download_df_unmatched",
                help = "Archivo que contiene datos que no tuvieron match",
                width = "stretch"
            )
            st.info("Este archivo contiene los datos que no se pudieron conciliar ni recibieron puntajes.")
            if clicked3:
                st.success("Descargando")

if __name__ == "__main__":
    render_conciliate()