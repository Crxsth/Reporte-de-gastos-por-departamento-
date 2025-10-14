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
    """
    Clase que encapsula un DataFrame y provee métodos para limpiar,
    formatear y agrupar los datos de reportes financieros.
    
    Atributos:
        df_ui (pd.DataFrame): version con formato del DataFrame.
        df (pd.DataFrame): versión editable del DataFrame.
        log (list): lista con las transformaciones aplicadas.
        numeric_columns (list): columnas numéricas detectadas.
        non_numeric_columns (list): columnas no numéricas detectadas.
    """
    def __init__(self,df):
        """
        Inicializa la instancia con una copia del DataFrame original.

        Args:
            df (pd.DataFrame): conjunto de datos cargado desde archivo.
        """
        # self.df_original =df.copy()
        self.df = df.copy()
        self.df_ui = df.copy()
        self.log = []

    def fix_header(self): 
        """
        Corrige encabezados vacíos o numéricos.

        Si todas las columnas son 'Unnamed' o son numéricas,
        usa la primera fila como encabezado y la elimina del cuerpo.

        Returns:
            ReporteDf: devuelve self para permitir encadenamiento.
        """
        cols = self.df.columns.astype(str)
        if (
        all(str(c).startswith("Unnamed") for c in cols)
        or all(c.isdigit() for c in cols)
        ): ##Si un dataframe no tiene header, este viene como "unamed"
            self.df.columns = self.df.iloc[0] ##Primera fila como encabezado
            self.df = self.df.drop(self.df.index[0]) ##Elimina primera fila.
            self.df_ui = self.df.copy()
        return self

    def fix_dates(self):
        """
        Convierte columnas que contengan la palabra 'date' a formato de fecha legible.

        Intenta convertir desde formato Excel (días desde 1899-12-30).
        Registra los cambios en self.log.
        
        Returns:
            ReporteDf: devuelve self para encadenar.
        """
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
        self.df_ui = self.df.copy()
        return self

    def fix_numbers(self):
        """
        Detecta y convierte columnas con valores numéricos.

        - Limpia caracteres no numéricos.
        - Convierte strings a float/int cuando es posible.
        - Clasifica columnas en numéricas o no numéricas.
        - Guarda los nombres en atributos internos.

        Returns:
            ReporteDf: devuelve self para encadenar.
        """
        self.numeric_columns = []
        self.non_numeric_columns = []
        
        for i, col in enumerate(self.df.select_dtypes(include="object").columns): ##object = strings and all
            serie_base = self.df[col]
            serie_converted = pd.to_numeric(serie_base.str.replace(
            r"[^\d\.-]", "", regex=True), errors="coerce")
            number_percent = serie_converted.notna().mean()  #% de valores numbers.
            if number_percent>=0.95 or "amount" in col.lower():
                self.df[col] = serie_converted
                self.numeric_columns.append(col)
                self.log.append(f"number_change[{i}]-[{col}]")
            else:
                self.non_numeric_columns.append(col)
        self.df_ui = self.df.copy()
        return self
    
    
    def group_data(self): 
        """
        Crea un agrupamiento dinámico con Streamlit.

        Permite seleccionar:
            - Columna de agrupación (no numérica)
            - Columna de métrica (numérica)
            - Tipo de agregación (conteo, suma o promedio)

        Muestra el DataFrame resultante y lo formatea si contiene montos.
        """
        if hasattr(self, "numeric_columns") and hasattr(self, "non_numeric_columns"): ##Verifica si existen listas con las columnas...
            group = st.selectbox("Columna de agrupación", self.non_numeric_columns, index=0) ##head.strings
            metric = st.selectbox("Columna numérica", self.numeric_columns, index=0)##head.ints
            agg = st.selectbox("Métrica de agregación", ["Conteo", "Suma", "Promedio"], index=0) ##Metrics ofc

            agg_map = {"Conteo": "count", "Suma": "sum", "Promedio": "mean"} ##Dict - Es para que el usuario vea "Conteo" en lugar de "count" por ejemplo
            out_col = f"{agg} de {metric}" ## Crea un texto usando agg y metric para ponerlo de header

            df_group = (
                self.df.groupby(group, dropna=False)[metric]
                       .agg(agg_map[agg])
                       .reset_index()
                       .rename(columns={metric: out_col})
            )
            ##Cambiamos el formato dependiendo del caso
            self.df_ui = df_group.copy()
            for col in self.df_ui.columns:
                col_low = col.lower()  # para no llamar .lower() varias veces
                if (("amount" in col_low) and ("suma" in col_low)) or (("amount" in col_low) and ("promedio" in col_low)):
                    self.df_ui[col] = self.df_ui[col].apply(lambda x: f"${x:,.2f}")
                else:
                    self.df_ui[col] = self.df_ui[col].apply(
                        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x
                        )

            st.subheader("Resultado agrupado")
            st.dataframe(self.df_ui, hide_index=True)
        else:
            st.warning("Ejecuta primero fix_numbers() para detectar columnas.")
            return

def boton_escala():
    """
    Crea un botón en Streamlit para cambiar la escala del gráfico.

    Actualmente es un marcador de posición (pendiente de implementar).
    """
    st.subheader("Escala de visualización")
    if st.button("Cambiar escala (pendiente)"):
        pass  # aquí luego conectamos la lógica


def vista_previa(df, n_default=20):
    """
    Muestra una vista previa de los datos en Streamlit.

    Args:
        df (pd.DataFrame): conjunto de datos a visualizar.
        n_default (int): número inicial de filas a mostrar (default=20).
    """
    col_dict = {}
    st.subheader("Vista previa")
    for col in df.columns:
        if "amount" in col.lower():
            col_dict[col] = st.column_config.NumberColumn(col, format="$%.2f")
    n_rows = st.slider("Número de filas a mostrar",5,100,n_default,5)
    st.dataframe(df.head(n_rows), column_config=col_dict, hide_index=True)
    
    
def string_to_number(df, columnas):##Convierte columnas a número
    """
    Convierte las columnas especificadas de un DataFrame a formato numérico.

    Usa expresiones regulares para detectar formatos como:
        - "#,###.00"
        - "###.00"
    Si no coincide, intenta convertir a entero.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        columnas (list): nombres de las columnas a convertir.

    Returns:
        pd.DataFrame: DataFrame con columnas convertidas.
    """
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
    """
    Abre un selector de archivos en Streamlit y carga el archivo seleccionado.

    Soporta archivos .csv, .xlsx y .xlsm.  
    Si es CSV, lo lee con codificación 'latin-1'.  
    Si es Excel, usa la función personalizada `leer_file()`.

    Returns:
        pd.DataFrame: datos cargados desde el archivo.
    """
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
    """
    Función principal del módulo.

    - Pide al usuario seleccionar un archivo.
    - Crea una instancia de `ReporteDf`.
    - Corrige encabezados, fechas y números.
    - Muestra vista previa y agrupaciones.
    - Calcula y muestra el tiempo total de ejecución.

    Esta función se ejecuta solo si el módulo es invocado directamente.
    """
    Timer0 = time.time()
    archivo_base = obtener_dataframe() ##Lee un [csv, xlsx, xlsm] y retorna un dataframe con los datos.
    
    archivo_completo = ReporteDf(archivo_base) ##Es una instancia con propiedades.
    archivo_completo.fix_header() ##if header = none or int, header = iloc[0]
    archivo_completo.fix_dates()
    archivo_completo.fix_numbers()
    
    st.title("Reporte de gastos")
    vista_previa(archivo_completo.df, 20)
    archivo_completo.group_data()
    
    ##Elegir tipo de agrupación
    # group = st.selectbox("Columna de agrupación", archivo_completo.non_numeric_columns, index=0)
    # metrics = st.selectbox("Columnas numericas", archivo_completo.numeric_columns, index=0)
    # agg = st.selectbox("Métrica de agregación", ["Conteo", "Suma", "Promedio"], index=0)
    # agg_map = {"Conteo": "count", "Suma": "sum", "Promedio": "mean"}
    
    
    Timer1 = time.time()
    ExecTime = Timer1 - Timer0
    print(f"Execution time: {ExecTime:,.2f}s")
    
if __name__ == "__main__":
    main()