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
    
    
def conciliador(df_base, df_bank, base_cols, bank_cols):
    """Concilia datos: Busca en df_bank y encuentra en df_base el dato más acertado
    Se revisan varias condiciones en los dataframes, cada condición añade 1 puntos
    
    
        a. Cada match son 1 puntos.
		b. Se elige el que {n} puntos == {n} matching_rules = perfect_match
		c. Si hay varios perfect_match, se debe guardar más no resolver
			i. Si ninguno hace match perfecto, es importante guardar el que tenga más puntos, pero no tratarlo como perfect match.
		d. Se guardan todos los que tienen 1 o más puntos en un df
		e. Se dropean los demás
        f. Si hubo match perfecto, se dropea del diccionario bool.
    
    """
    ##convierte los rows en una lista
    
    
    df_base["prob"] = 0
    for col in base_cols: ##Crea columnas para añadir puntos del match
        df_base[f"{col} match"] = 0
    df_bank["total matches"] = 0
    df_base["available"] = True ##Serie utilizada para saber si la transacción ha sido o no utilizada
    print("df_bank:")
    print(df_base)
    print(base_cols)
    print(bank_cols)
    # print(bank_cols)
    # if bool_var ==True:
    
    for idx_bank in df_bank.index: ##por cada transacción
        df_var = df_base[df_base["available"] == True].copy() ##Creamos copia de los available
        print(f"Valor buscado: {df_bank.loc[idx_bank, "Amount"]}")
        count = 0
        for idx_base in df_var.index: ##por cada dato del ERP
            # print(df_var.loc[idx_base,"Amount"])
            ##Iteramos las listas con los valores de los componentes interactivos
            for i, dato in enumerate(bank_cols):
                banco_matching_rule_n = bank_cols[i] ##Nombres de las columnas de las listas
                base_matching_rule_n = base_cols[i]
                
                valor_bank = df_bank.loc[idx_bank, banco_matching_rule_n] ##Valor del índice & list.value
                valor_base = df_base.loc[idx_base, base_matching_rule_n] 
            
                if valor_bank == valor_base:
                    print(f"Found: {valor_bank} == {valor_base}")
                    df_base.loc[idx_base, f"{dato} match"] = 1
                else:
                    count = count +1
        print(f"Contador: {count}")
        # print("Valor buscado:")
        # print(df_bank.loc[idx_bank])
        df_var.to_csv("Datos_test.csv")
        exit() ##Detenmos pq sí we
    
    # for i, dato in enumerate(bank_cols): ##por cada matching_rules
            # banco_matching_rule_n = bank_cols[i] 
            # base_matching_rule_n = base_cols[i]
    
    
    df_bank.to_csv("Datos del banco jan 31, 2026.csv")
    if 1>2:
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
                st.write(valor)
            break