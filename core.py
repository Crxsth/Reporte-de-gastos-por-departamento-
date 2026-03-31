import time
import csv
import io
import numpy
import pandas as pd
from pathlib import Path
import re
import sys
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
        for i, fila in enumerate(matrix[:11]):
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
        
        ##Convertimos columnas a número de ser posible
        for i,col in enumerate(self.df.columns):
            serie_converted = pd.to_numeric(self.df[col], errors="coerce")
            porcentaje_numerico = serie_converted.notna().mean()
            if porcentaje_numerico>0.95:
                self.df[col] = serie_converted
                self.log.append(f"number_change[{i}]-[{col}]")
        
        ##Los restantes, los tratamos de convertir
        for i, col in enumerate(self.df.columns): ##object = strings and all
            if self.df[col].dtype == "object":
                serie_converted = pd.to_numeric(
                self.df[col].str.replace(
                r"[^\d\.-]", "", regex=True), errors="coerce"
                )
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
    ##convierte los rows en una lista
    timer1 = time.time()
    df_base = df_base.copy()
    df_bank = df_bank.copy()
    df_base["match_score"] = 0
    for col in base_cols: ##Crea columnas para añadir puntos del match
        df_base[f"{col} match"] = 0
    df_bank["total matches"] = 0
    df_base["available"] = True ##Serie utilizada para saber si la transacción ha sido o no utilizada
    df_base["valor buscado"] = ""
    df_base["original_idx"] = 0
    df_base["bank_idx"] = 0
    n = len(base_cols)
    df_result = df_base.copy() ##df_result almacenará todos los valores que df_var haya creado
    
    chunks = [] ##Contendrá referencias a df_var.copy() en cada bucle para evitar lag 
    objetivo = []
    
    col_var = 0 ##int que nos dice la columna con la que testeamos
    base_dict = (
        df_base.groupby(base_cols[col_var]).groups)
    bank_dict = (
        df_bank.groupby(bank_cols[col_var]).groups)
    matches_dict = {}
    i = 0
    # CHATGPT:
    # input:
    # for key in bank_dict:
        # base_idx = base_dict.get(key,[]) ##Si key existe en base_dict, devuelve índices
        # bank_idx = bank_dict[key]
        # if len(base_idx)>0:
            # matches_dict[key] = {
                # "bank":list(bank_idx),
                # "base":list(base_idx
            # }
    # Mine:
    print(f"Test col: >{bank_cols[col_var]}<")
    for key in bank_dict:
        bank_idx = bank_dict[key]
        if key in base_dict:
            base_idx = base_dict[key]
            i = i +1
            matches_dict[key] = {
                "bank":list(bank_idx),
                "base":list(base_idx)
            }
            print(f">{matches_dict[key]}<")
            if i>10:
                break
    
    
    print("")
    ##Convierte diccionario a DF con dos columnas: "bank","base" con su respectiva data
    df_matches = pd.DataFrame.from_dict(matches_dict, orient="index").reset_index()
    df_matches = df_matches.rename(columns={"index":"match_key"})
    
    ##Guardamos las filas que formarán la tabla puente
    
    
    exit()
    
    
    # print(df)
    bridge = (
        df_matches.reset_index(names="match_key")
        .apply(
            lambda row:pd.DataFrame({
                "match_key": row["match_key"],
                "bank_idx": row["bank"],
                "base_idx": [row["base"]] * len(row["bank"])
            }),
            axis=1
        )
    )
    bridge = pd.concat(bridge.to_list(), ignore_index=True)
    bridge = bridge.explode("base_idx")
    result = (
        bridge.merge(
            df_bank.reset_index(names="bank_idx"),
            on="bank_idx",
            how="left"
        )
        .merge(
            df_base.reset_index(names="base_idx"),
            on="base_idx",
            how="left",
            suffixes=("_bank","_base")
        )
    )
    for col in result.columns:
        print(col)
    
    
    if 1>2:
        rows = []
        print("Here:")
        for match_value, match_info in matches_dict.items():
            # print(f"{match_value} , {match_info}")
            bank_idx = match_info.get("bank", [])
            base_idx = match_info.get("base", [])
            # print(f"Bank: {bank_idx}, base: {base_idx}")

            
            
            if not bank_idx or not base_idx:
                continue
            for idx in bank_idx:
                for idx2 in base_idx:
                    base_row = df_base.loc[idx2].to_dict()
                row_var = {
                    "bank_idx": bank_idx,
                    "bank_monto": match_value,
                    "base_idx":base_idx
                }   
                row_var.update(base_row)
                rows.append(row_var)
        
    
   
    # output:
    # {
        # 1000:{
            # "bank":[1,5,10],
            # "base":[2,8]
        # }
        # 2500:{
            # "bank":[3],
            # "base":[7,9]
        # }
    # }
    
        # print(f"Buscado: {base_cols[1]}")
        # print(f">{key}<>{base_idx}<")
        # if i>10:
            # break
        # bank_idx = bank_dict[key]
    
    # for key in base_dict:
        # item = base_dict[key]
        # if key in bank_dict:
        # print(f"{key} - {item}")
    
    bool_original = False
    for idx_bank in df_bank.index: ##por cada transacción
        if bool_original ==False:
            break
        df_var = df_base[df_base["available"] == True].copy() ##Creamos copia de los available

        count = 0
        ##Contiene un string: "objetivo:valor", example: "Date:123, Amount:456"
        objetivo = ", ".join([f"{col}:{df_bank.loc[idx_bank, col]}" for col in bank_cols]) 
        
        for idx_base in df_var.index: ##por cada dato del ERP
            # print(df_var.loc[idx_base,"Amount"])
            ##Iteramos las listas con los valores de los componentes interactivos
            for i, dato in enumerate(bank_cols):
                banco_matching_rule_n = bank_cols[i] ##Nombres de las columnas de las listas
                base_matching_rule_n = base_cols[i]
                valor_bank = df_bank.loc[idx_bank, banco_matching_rule_n] ##Valor del índice & list.value
                valor_base = df_base.loc[idx_base, base_matching_rule_n] 
                
                if valor_bank == valor_base: ##Compara si hacen match nuestros valores
                    df_var.loc[idx_base, f"{dato} match"] = 1 ##Punto
                    df_var.loc[idx_base, "valor buscado"] = objetivo
                # else:
                    # count = count +1
            match_cols = [f"{dato} match" for dato in base_cols] ##Crea una lista: ["Date match","Amount match"]
        count = count + 1
        
        ##df_var almacena aquellos con >0 matches
        df_var["match_score"] = df_var[match_cols].sum(axis=1) ##Suma de los datos
        df_var = df_var[df_var["match_score"]!=0] ##Es un drop para filtrar solo los que tengan valor
        df_var["original_idx"] = df_var.index ##Guarda el índice original para no perderlo después, en caso de necesitar búsquedas
        df_var["bank_idx"] = idx_bank ##Guarda el índice de la transacción bancaria con la que lo comparamos
        chunks.append(df_var.copy()) ##2 tabs de identación. chunks almacenará cada uno
    
    if bool_original==True:
        df_result = pd.concat(chunks, ignore_index=True) ##Contiene todos los 'df_var', sus puntos y datos
        df_max = df_result[
            df_result["Amount match"] == 
            df_result.groupby("bank_idx")["Amount match"].transform("max")
        ]
    else:
        df_max = df_base.copy()
    # print("creamos un csv del banco, el idx no me convence")
    # df_bank.to_csv("df_bank_py.csv")
    # print(df_base)
    # print(df_max)
    
    timer2 = time.time()
    tiempo = timer2-timer1
    print(f"Tiempo de ejecución: {tiempo:.4f}")
    # print(f"Contador de matches: {count}")

    # df_result.to_csv("df_result.csv")
    # print("Se ha hecho df_result.csv, contiene todos los puntajes")
    # df_max.to_csv("df_max.csv")
    # print("Se ha creado df_max.csv, contiene solo los máximos")
    return df_result, df_max