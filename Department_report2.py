"""2025.09.22. El propósito de este código es analizar un grupo de datos, obtener sus totales y graficarlos.
Se busca:
    1.- Crear un reporte de gastos por departamento, mostrar en qué departamentos hay más gastos. Graficar.
        Crear un reporte de gastos por empleado.
        
    1.- Gastos por departamento.
        Crear un módulo principal el cual abre una pantalla en matplotlib.
        Dentro de la figura, debe haber un mensaje: "Seleccionar archivo a leer"
        El módulo principal debe leer un archivo y tener funciones para hacer distintas acciones:
        • Crear un dataframe y darle formato (main).
        • def: Crear gráfico de barras / de pastel y cambiarlo uno con otro.
        • def: Crear tabla de datos y mostrar figura.
        • def: Añadir CV y actualizar figura
    
Header: ["Report ID", "Department", "Employee", "Report Type", "Amount", "Transaction date", "Report Date"]
"""
import time
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import zipfile
from functools import partial
import tkinter as tk
from tkinter import filedialog
import streamlit as st
import sys
import os
import re
ruta_completa = r"C:\Users\criis\Documents\Coding\Repositorio-git"
sys.path.append(ruta_completa)
from xlsx_reader import leer_file ##Este es un lector de xlsx que no lee 'inlinestring'


class ReporteDf:
    def __init__(self,df):
        self.df_original =df.copy()
        self.df = df.copy()
        self.log = []

    def fix_header(self): ##If the header is empty or are numbers, fixes it.
        cols = self.df.columns.astype(str)
        if (
        all(str(c).startswith("Unnamed") for c in cols)
        or all(c.isdigit() for c in cols)
        ): ##Si un dataframe no tiene header, este viene como "unamed"
            self.df.columns = self.df.iloc[0] ##Primera fila como encabezado
            self.df = self.df.drop(self.df.index[0]) ##Elimina primera fila.
        return self
    
    def fix_dates(self):
        for i, col in enumerate(self.df.columns):
            if "date" in col.lower():
                self.df = string_to_number(self.df, [col]) ##Convertir a number.
                s_base = self.df[col]
                s_converted =pd.to_datetime(
                    s_base, unit="D", origin="1899-12-30", errors="coerce"
                )
                resultado = s_converted.where(s_converted.notna(), s_base)
                resultado = resultado.dt.strftime("%d-%b-%y")
                self.df[col] = resultado
                self.log.append(f"date_change[{i}]-[{col}]")
        return self
        
    def fix_numbers(self):
        for i, col in enumerate(self.df.select_dtypes(include="object").columns): ##object = strings and all
            serie_base = self.df[col]
            serie_converted = pd.to_numeric(serie_base.str.replace(
            r"[^\d\.-]", "", regex=True), errors="coerce")
            number_percent = serie_converted.notna().mean()  #% de valores numbers.
            if number_percent>=0.95 or "amount" in col.lower():
                self.df[col] = serie_converted
                self.log.append(f"number_change[{i}]-[{col}]")
        return self

    
def vista_previa(df, n_default=20): #Vista previa de los datos.
    col_dict = {}
    st.subheader("Vista previa")
    for col in df.columns:
        if "amount" in col.lower():
            col_dict[col] = st.column_config.NumberColumn(col, format="${:,.2f")
    n_rows = st.slider(5,100,n_default,5)
    st.dataframe(df.head(n_rows), column_config=col_dict, hide_index=True)
    
    
def string_to_number(df, columnas):##Convierte columnas a número
    pattern1 = r"^-?\d{1,3}(?:,\d{3})+\.\d{2}$" # format: "#,##0.00"
    pattern2 = r"^-?\d+\.\d{2}$" # format: "#,##0.00"
    for col in columnas:
        if col in df.columns:
            s_base = df[col].astype(str).str.strip() #Forzamos a string, evitando errores.
            mask1 = s_base.str.contains(pattern1, na=False)
            mask2 = s_base.str.contains(pattern2, na=False)
            # resultado = s_base.str.contains(pattern1 + "|" + pattern2, na=False) 
            lista_var = []
            for valor in s_base: ##Convierte dependiendo del patrón.
                if re.fullmatch(pattern1,valor):
                    lista_var.append(float(valor.replace(",","")))
                elif re.fullmatch(pattern2, valor):
                    lista_var.append(float(valor))
                else: ##Try to see if it's an integer:
                    try: 
                        valor = int(valor)
                    except:
                        pass
                    lista_var.append(valor)
            df[col] = lista_var
    return df


def obtener_dataframe(): ##Function that selects a file to work with. 
    #Using streamlit as it crashed.
    archivo_base = st.file_uploader( ##Devuelve un archivo en memoria.
        "Selecciona el archivo de Excel o CSV",
        type=["csv", "xlsx", "xlsm"]
        )
    st.info("Sube un archivo para continuar.")
    if archivo_base is None:
        st.stop()
    if archivo_base.name.lower().endswith(".csv"):
        archivo_leido = pd.read_csv(archivo_base, encoding="latin-1", header=0)
    else:
        archivo_leido = pd.DataFrame(leer_file(archivo_base))
    return archivo_leido
    

def main():
    Timer0 = time.time()
    archivo_base = obtener_dataframe() ##Lee un [csv, xlsx, xlsm] y retorna un dataframe con los datos.
    
    archivo_completo = ReporteDf(archivo_base) ##Es una instancia con propiedades.
    archivo_completo.fix_header() ##if header = none or int, header = iloc[0]
    archivo_completo.fix_dates()
    archivo_completo.fix_numbers()
    # archivo_completo.df.style.format({"Amount": "${:,.2f}"})
    # df.style.format("${:,.2f}")
    
    # archivo_completo.fix_dates() ##if string:"date" in columns, entirecolumn = date.
    columnas_nonumericas = []

    st.title("Reporte de gastos")
    st.subheader("Vista previa de:"); st.dataframe(archivo_completo.df.head(20))
    st.write(archivo_completo.log)
    st.write(f"La columna amount es: {type(archivo_completo.df["Amount"][2])}")
    
    columnas_numericas = archivo_completo.df.select_dtypes(include="number").columns.to_list() ##Obtenemos las columnas numéricas
    # st.write("Tipos de datos:",archivo_completo.head(5))
    
    
    for columna in archivo_completo.df.columns:
        if columna not in columnas_numericas:
            columnas_nonumericas.append(columna)
    group = st.selectbox("Columna de agrupación", columnas_nonumericas, index=0)
    metrics = st.selectbox("Columnas numericas", columnas_numericas, index=0)
    st.success(f"La información está agrupada por: **{group}** | Métrica: **{metrics}**")
    
    
    # df_vista, col_cfg = archivo_completo.vista_formateada(N_ROWS)
    # st.dataframe(df_vista, column_config=col_cfg, hide_index=True)
    
    
    # Slider para elegir cuántas filas mostrar
    # N_ROWS = st.slider(
        # "Número de filas a mostrar",
        # min_value=5,     # mínimo
        # max_value=100,   # máximo
        # value=20,        # valor por defecto
        # step=5           # de cuánto en cuánto sube
    # )
    # st.dataframe(
        # archivo_completo.df.head(N_ROWS),
        # column_config={
            # "Amount": st.column_config.NumberColumn("Amount", format="$%.2f")
        # },
        # hide_index=True
    # )
    
    
    Timer1 = time.time()
    ExecTime = Timer1 - Timer0
    print(f"Execution time: {ExecTime:,.2f}s")
    
if __name__ == "__main__":
    main()