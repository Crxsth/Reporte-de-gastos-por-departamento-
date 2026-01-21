import pandas as pd
import numpy
import sys
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
                try:
                    self.df = string_to_number(self.df, [col]) ##Convertir a number.
                    s_base = self.df[col]
                    s_converted =pd.to_datetime(
                        s_base, unit="D", origin="1899-12-30", errors="coerce"
                    )
                    resultado = s_converted.where(s_converted.notna(), s_base)
                    resultado = resultado.dt.strftime("%d-%b-%y")
                    self.df[col] = resultado
                    self.log.append(f"date_change[{i}]-[{col}]")
                except:
                    pass
        self.df_ui = self.df.copy()
        return self

    def fix_numbers(self):
        """
        Detecta y convierte columnas con valores numéricos.

        - Limpia caracteres no numéricos.
        - Convierte strings a float/int cuando es posible.
        - Clasifica columnas en numéricas o no numéricas.
        - Guarda los nombres en atributos internos.1

        Returns:
            ReporteDf: devuelve self para encadenar.
        """
        self.numeric_columns = []
        self.non_numeric_columns = []
        
        # for i, col in enumerate(self.df.select_dtypes(include="object").columns): ##object = strings and all
        for i, col in enumerate(self.df.columns): ##object = strings and all
            if self.df[col].dtype == "object":
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
            else:
                if self.df[col].dtype.kind in ("i", "u", "f"):
                    self.numeric_columns.append(col)
                else:
                    self.non_numeric_columns.append(col)
        return self


def load_file(archivo_base):
    ##Lee un archivo, devuelve un df
    if archivo_base.name.lower().endswith(".csv"):
        archivo_leido = pd.read_csv(archivo_base, encoding="latin-1", header=0)
    else:
        archivo_leido = pd.DataFrame(leer_file(archivo_base)) ##Lo leemos con nuestro lector personalizado
    return archivo_leido
    