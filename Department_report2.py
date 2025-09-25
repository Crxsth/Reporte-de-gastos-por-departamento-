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
                self.df[col] = pd.to_datetime(self.df[col], errors="coerce") 
                self.log.append(f"date_change[{i}]")
        return self
        
    def fix_numbers(self):
        for i, col in enumerate(self.df.select_dtypes(include="object").columns): ##object = strings and all
            serie_base = self.df[col]
            serie_converted = pd.to_numeric(serie_base.str.replace(
            r"[^\d\.-]", "", regex=True), errors="coerce")
            number_percent = serie_converted.notna().mean()  #% de valores numbers.
            if number_percent>=0.95:
                self.df[col] = serie_converted
                self.log.append(f"number_change[{i}]")
        return self

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
    archivo_completo.fix_dates() ##if string:"date" in columns, entirecolumn = date.
    dataframe = archivo_completo.df.copy()
    # exceldate_todate(archivo_completo)
    lista_var = []
    for dato in archivo_completo.df.iloc[1]:
        valorvar = type(dato)
        lista_var.append(valorvar)
    st.write("Datos de fila 1:", lista_var)
    columnas_nonumericas = []
    
    st.title("Reporte de gastos")
    st.subheader("Vista previa"); st.archivo_completo(archivo_completo.head(5))
    columnas_numericas = archivo_completo.df.select_dtypes(include="number").columns.to_list() ##Obtenemos las columnas numéricas
    # st.write("Tipos de datos:",archivo_completo.head(5))
    
    for columna in archivo_completo.df.columns:
        if columna not in columnas_numericas:
            columnas_nonumericas.append(columna)
    group = st.selectbox("Columna de agrupación", columnas_nonumericas, index=0)
    metrics = st.selectbox("Columnas numericas", columnas_numericas, index=0)
    st.success(f"La información está agrupada por: **{group}** | Métrica: **{metrics}**")
    
    
    
    Timer1 = time.time()
    ExecTime = Timer1 - Timer0
    print(f"Execution time: {ExecTime:,.2f}s")
    
if __name__ == "__main__":
    main()