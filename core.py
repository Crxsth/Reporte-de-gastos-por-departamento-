import time
import csv
import io
import numpy
import pandas as pd
from pathlib import Path
import re
import sys
import warnings


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
    def __init__(self,df,name=None):
        """
        Inicializa la instancia con una copia del DataFrame original.

        Args:
            df (pd.DataFrame): conjunto de datos cargado desde archivo.
        """
        # self.df_original =df.copy()
        self.df = df.copy()
        df = self.df
        self.data_list = [df.columns.tolist()] + df.values.tolist()
        self.log = []
        self.numeric_columns = []
        self.non_numeric_columns = []
        self.empty_columns = []
        self.date_columns = []
        

    def fix_header(self):
        """
        Corrige encabezados vacíos o numéricos.

        Si todas las columnas son 'Unnamed' o son numéricas, o desigual
        usa la primera fila como encabezado y la elimina del cuerpo.

        Returns:
            ReporteDf: devuelve self para permitir encadenamiento.
        """
        matrix = self.data_list
        dict_idx = {}
        PLUS_WORDS = [
                "date","posting","transaction","value",
                "description","details","memo","narrative","reference","ref","id","txn id",
                "amount","debit","credit","balance","running balance",
                "currency","fx","exchange rate",
                "vendor","payee","merchant","customer","name",
                "account","account number","iban","swift",
                "category","type","status",
                "invoice","bill","receipt","report",
                "department","project","cost center","cc","gl","ledger","code"
            ]
        MINUS_WORDS = [
            "bank statement","statement","account summary","summary",
            "bank of","citibank","hsbc","bbva","santander","banamex","banorte",
            "generated","printed","page","period","from","to",
            "as of","as at",
            "febrero","enero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre",
            "a:","de:","para:","cliente","titular","sucursal"
        ]
        for i, fila in enumerate(matrix[:30]):
            if (len(fila) == len(self.df.columns) ##Lógica que revisa si 
            and sum(not str(x).startswith("Unnamed") for x in fila) > len(fila) *0.5): 
                dict_idx[i] = 0 ##Si se cumplen las condiciones, se guarda.
        
        if len(dict_idx)>=1:
            for i in dict_idx:
                fila = matrix[i]
                score = 0
                score = -sum(
                    isinstance(x, int) or (isinstance(x, str) and x.isdigit())
                    for x in fila)
                fila_norm =[str(x).strip().lower() for x in fila]
                ##Puntajes para asignar y decidir column
                score += sum(any(x in cell for x in PLUS_WORDS) for cell in fila_norm)
                score -= sum(any(x in cell for x in MINUS_WORDS) for cell in fila_norm)
                score -= sum(cell == "" for cell in fila_norm)
                dict_idx[i] = score
                # print(f"{i}: {score}")
        best_i = max(dict_idx, key=dict_idx.get)
        # print(f"Mejor: {best_i}:: {matrix[best_i]}")
        matrix = matrix[best_i:]
        df = pd.DataFrame(matrix)
        
        # Asigna column names al df
        headers = [str(x) for x in df.iloc[0]]
        df = pd.DataFrame(df.iloc[1:].values, columns = headers)
        
        self.log.append(f"Firstrow corrected to {best_i}. Largo de dict_idx (filas revisadas): {len(dict_idx)}")
        self.data_list = matrix
        self.df = df
        return self

    def fix_dates(self, col_name=None,formato=None):
        """
        Convierte columnas que contengan la palabra 'date' a formato de fecha legible.

        Intenta convertir desde formato Excel (días desde 1899-12-30).
        Registra los cambios en self.log.
        
        Returns:
            ReporteDf: devuelve self para encadenar.
        """
        converted = False
        if col_name == None:
            for i, col in enumerate(self.df.columns):
                if "date" in col.lower():
                    serie_base = self.df[col]
                    serie_numeric = pd.to_numeric(serie_base, errors="coerce")
                    percent = serie_numeric.notna().mean()
                    if percent>0.90:
                        self.df[col] = pd.to_datetime(
                            serie_base, unit="D", origin="1899-12-30", errors="coerce"
                        )
                        converted =True
                    else:
                        serie_converted = pd.to_datetime(serie_base,format=formato,errors="coerce")
                        percent_date = serie_converted.notna().mean()
                        if percent_date>0.90:
                            self.df[col] = serie_converted
                            converted = True
                        else:
                            print(f"No convertimos {col}")
                        
                    if converted == True:
                        # print(f"Convertimos a fecha: [{i}]-[{col}]")
                        self.log.append(f"date_change[{i}]-[{col}]")
                        self.non_numeric_columns.append(col)
                        self.date_columns.append(col)
        else:
            col = col_name
            i = self.df.columns.get_loc(col)
            serie_base = self.df[col]
            try: ##Si viene con formato excel, convertimos a fecha
                serie_converted = pd.to_numeric(serie_base, errors="coerce")
                percent = serie_converted.notna().mean()
                if percent>0.95:
                    serie_converted = pd.to_datetime(
                        serie_converted, unit="D", origin="1899-12-30", errors="coerce"
                    )
                    # print("Serie convertida de excel")
                    self.df[col] = serie_converted
                    self.log.append(f"date_change[{i}]-[{col}]")
                    self.non_numeric_columns.append(col)
                    self.date_columns.append(col)
            except Exception as e:
                print("Serie convertida de texto")
                serie_converted = pd.to_datetime(serie_base, errors="coerce", format=formato)
                self.log.append(f"date_change[{i}]-[{col}]")
                self.non_numeric_columns.append(col)
                self.date_columns.append(col)
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
        
        ##Sacamos las empty_columns
        for i,col in enumerate(self.df.columns):
            serie = self.df[col]
            serie = serie[serie !=""].dropna()
            if serie.empty:
                self.empty_columns.append(col)
                self.log.append(f"Empty column skip:[{i}]-[{col}]")
        
        ##Convertimos columnas a número de ser posible
        for i,col in enumerate(self.df.columns):
            if col in self.empty_columns or col in self.non_numeric_columns:
                continue
            serie_converted = pd.to_numeric(self.df[col], errors="coerce")
            
            porcentaje_numerico = serie_converted.notna().mean()
            serie = self.df[col].dropna().astype(str).str.strip()
            serie = serie[serie != ""]
            avg_len = serie.str.len().mean()
            if "Bank" in col:
                # print(avg_len)
                pass
            
            if porcentaje_numerico>0.95 and avg_len< 15:
                self.df[col] = serie_converted
                self.log.append(f"number_change[{i}]-[{col}]")
                self.numeric_columns.append(col)
                if "Bank" in col:
                    # print("Aquí")
                    pass

        ##Los restantes, los tratamos de convertir
        for i, col in enumerate(self.df.columns): ##object = not defined data type
            if col in self.numeric_columns or col in self.empty_columns: ##Si es numérico o empty, no va aquí
                continue
            ##Si los datos son muy grandes, dejamos string
            serie_str = self.df[col].astype(str)
            avg_len = serie_str.str.len().mean()
            
            if avg_len > 10:
                self.df[col] = (
                    serie_str.str.strip().astype("string")
                )
                self.non_numeric_columns.append(col)
                continue
            
            ##Si es algún ID como "bank ref", igual va as 'string'
            col_clean = col.lower().strip()
            ID_EXACT = ["r_trans_no", "reference number"] ##exact match
            ID_HINTS = ["reference"] ##any
            if (
                col_clean in ID_EXACT or
                any(hint in col_clean for hint in ID_HINTS)
            ):
                self.df[col] = self.df[col].astype(str).str.strip()
                self.non_numeric_columns.append(col)
                continue
            
            
            if self.df[col].dtype == "object" and ("amount" in col.lower() or "monto" in col.lower()):
                serie_converted = pd.to_numeric(
                self.df[col].str.replace(
                r"[^\d\.-]", "", regex=True), errors="coerce"
                )
                number_percent = serie_converted.notna().mean()  #% de valores numbers.
                if number_percent>=0.95:
                    self.df[col] = serie_converted
                    self.numeric_columns.append(col)
                    self.log.append(f"number_change[{i}]-[{col}]")
                    if "Bank" in col:
                        print("Here")
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
    if isinstance(archivo_base, Path):
        nombre = str(archivo_base.name)
    elif isinstance(archivo_base, str):
        nombre = archivo_base
    else:
        nombre = str(archivo_base.name)
    
    if nombre.lower().endswith(".csv"):
        escsv = True
    elif (nombre.lower().endswith(".xlsx")) or (nombre.lower().endswith(".xlsm")):
        escsv = False
    
   
    ##Esto normalmente recibe Bytes, pero puede recibir string or Path
    # if archivo_base.name.lower().endswith(".csv"): ##Si es csv no usamos pandas, pues pandas me dió error muchas veces
    if escsv==True:
        archivo_leido = []
        decodificador = "utf-8"
        if isinstance(archivo_base,(str,Path)):
            with open(archivo_base, newline='', encoding=decodificador) as f:
                reader = csv.reader(f)
                for fila in reader:
                    archivo_leido.append(fila)
        else:##This exist when the program receives not a string or Path to read a file, but an object in memory.
            contenido = io.StringIO(archivo_base.getvalue().decode(decodificador)) ##pasa de bytes a texto según chatgpt
            reader = csv.reader(contenido)
            for fila in reader:
                archivo_leido.append(fila)
        archivo_leido = pd.DataFrame(archivo_leido)
    else:
        try:
            archivo_leido = pd.DataFrame(leer_file(archivo_base)) ##Lo leemos con nuestro lector personalizado
        except:
            archivo_leido = pd.read_excel(archivo_base)
    
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
    timer1 = time.time()
    
    df_base = df_base.copy()
    df_bank = df_bank.copy()
    df_bank["bank_idx"] = df_bank.index
    df_base["base_idx"] = df_base.index
    df_bank["valor buscado"] = df_bank.apply(
        lambda row: ", ".join(f"{col}: {row[col]}" for col in bank_cols), axis=1
    )
    
    merges = []
    ##Se hace 1:1 a las columnas, se iteran, se hace un merge para unir matches, se crea una columna con puntajes
    for col1, col2 in zip(bank_cols, base_cols): ##Creamos variable 1:1 con las columnas de los 'df' a comparar
        print(f"Matching: {col1} - {col2}")
        temp = df_bank.merge(df_base, left_on=col1, right_on=col2, how="inner")  ##Hacemos un merge, donde los datos sean iguales
        temp = temp[temp[col1].notna()] ##Drop na temporal, para evitar valores vacíos...
        temp = temp[temp[col1] != ""]
        temp[f"{col1} match"] = 1 ##Columna con puntos
        merges.append(temp[["bank_idx","base_idx","valor buscado",f"{col1} match"]])
    
    ##Se unen los merges 
    match_cols = [f"{col} match" for col in bank_cols] ##cols matching as ['Date match','Amount match']
    """Cada df de 'merges' contiene la columna de puntajes, as ["Date match"] 
    por ello si las unimos, nos queda un dataframe con los puntajes unidos donde corresponda
    """
    bridge = merges[0] 
    for df_var in merges[1:]: ##Une los diversos merge que hicimos anteriormente con puntos 
        bridge = bridge.merge(df_var, on=["bank_idx","base_idx", "valor buscado"], how="outer")
    bridge = bridge.fillna(0)
    
    ##Score: colocamos la columna con suma, y dropeamos dejamos solo los >0
    bridge["match_score"] = bridge[match_cols].sum(axis=1)
    bridge = bridge[bridge["match_score"] > 0]
    ##bridge es como un bridge. Contiene los índices, valor buscado y los puntos
    ##df_base["bank_idx", "base_idx", "valor buscado", "Date match", "Amount match", "match_score"]
    timer2 = time.time()
    tiempo = timer2-timer1
    print(f"Tiempo de ejecución: {tiempo:.4f}")
    return bridge

def build_review_df(bridge, df_bank, df_base, bank_cols, base_cols):
    """Construye los dataframes usados para el conciliador:
    
    df_result: Es un merge con los df: banco & bridge & base; mantiene solo las columnas especificadas
        Este existe para cuando se solicite ver la información de todo lo que se hizo
    df_matched: Es df_result pero solo con los máximos valores de la columna ["match_score"]
        Matches con más puntos, es ideal
    df_conciliation: Se unen los dataframes de manera bruta con el mejor candidato
        Conciliación completa, para presentar
    """
    df_bank = df_bank.copy()
    df_base = df_base.copy()
    bridge = bridge.copy()
    df_bank.insert(0, "bank_idx", df_bank.index)
    df_base.insert(0,"base_idx",df_base.index)
    base_cols = base_cols.copy()
    base_cols.insert(0,"base_idx")
    bank_cols_use = ["bank_idx"] + bank_cols
    
    
    ##Cambiamos posicion de 'base_idx' en bridge
    serie_var = bridge["base_idx"]
    bridge = bridge.drop("base_idx", axis=1)
    bridge["base_idx"] = serie_var

    ##Se crea df_result:
    df_result = df_bank[bank_cols_use].merge(bridge, how="left", on="bank_idx")
    df_result = df_result.merge(df_base[base_cols],how="left",on="base_idx", suffixes=(" Bank"," Base"))
    
    ##Se crea df_matched / df_max
    df_max = df_result[
        df_result["match_score"] == 
        df_result.groupby("bank_idx")["match_score"].transform("max")
    ].copy()
    n = len(base_cols)-1
    df_max["confianza"] = (df_max["match_score"] / n)*100

    

    ##Se crea df_conciliation
    df_conciliation = df_bank.merge(bridge,how="left", on="bank_idx")
    df_conciliation = df_conciliation.merge(df_base,how="left",on="base_idx",suffixes=(" Bank"," Base"))
    # df_conciliation = df_conciliation.groupby("bank_idx")["match_score"].transform("max")
    df_conciliation = df_conciliation[
        df_conciliation["match_score"] ==
        df_conciliation.groupby("bank_idx")["match_score"].transform("max")
    ].copy()
    
    # df_result.to_csv("df_result.csv")
    return df_result, df_max, df_conciliation