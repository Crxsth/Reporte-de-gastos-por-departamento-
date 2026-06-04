import time
t0 = time.time()
import sys
import os
from pathlib import Path
import pandas as pd

# Ruta actual (tests/)
CURRENT_DIR = Path(__file__).resolve().parent
# Subir un nivel → carpeta raíz del proyecto
PROJECT_ROOT = CURRENT_DIR.parent
# Agregar al sys.path
sys.path.append(str(PROJECT_ROOT))
import core
t1 = time.time()
tiempo_imports = t1-t0
# print(f"Tiempo imports en tests: {tiempo_imports:,.2f}")

if 1>0:
    """Usaremos esta sección para testear manualmente el conciliador de manera más rápida.
    """
    ##Creación de la clase, limpieza de datos
    t0 = time.time()
    ruta_banco = CURRENT_DIR / "Datos_banco.csv"
    ruta_base = CURRENT_DIR / "Datos_base.csv"
    df_bank = core.load_file(ruta_banco)
    df_base = core.load_file(ruta_base)
    banco = core.ReporteDf(df_bank).fix_header()
    # banco.fix_numbers()
    serie_converted = pd.to_datetime(banco.df["Date"],dayfirst=True)
    banco.df["dt"] = serie_converted ##dt tiene fechas con número como si fuera excel
    print(serie_converted)
    banco.df["dt"] = (
        pd.to_datetime(banco.df["dt"], errors="coerce")
        - pd.Timestamp("1899-12-30")
    ).dt.days
    print("Trabajaremos con:")
    print(banco.df)
    banco.fix_dates()
    
    ##Testearé el funcionamiento de fix_dates()
    exit()
    base = core.ReporteDf(df_base)
    base.fix_header()
    base.fix_numbers()
    base.fix_dates()
    
    df_base =base.df
    df_bank = banco.df
    
    ##Llamamos al conciliador:
    # def conciliador(df_base, df_bank, base_cols, bank_cols):
    base_list = ["R_TRANS_NO"]
    base_list = ["Date","Amount"]
    bank_list = ["Reference number"]
    bank_list = ["Date","Amount"]
    n = len(base_list)
    
    base_r = df_base[base_list]
    bank_r = df_bank[bank_list]
    
    # Ejecuta la conciliación entre base y banco
    # Devuelve:
    # - df_result: todas las combinaciones con al menos 1 match
    # - df_max: los mejores matches por cada bank_idx
    bridge = core.conciliador(
        df_base = base.df,
        df_bank = banco.df,
        base_cols = base_list,
        bank_cols = bank_list
    )
    df_result, df_max, df_conciliation = core.build_review_df(
        bridge, 
        df_bank, 
        df_base, 
        bank_cols =bank_list, 
        base_cols = base_list
    )
    
    # print(df_result)
    siesvi = "df merge test col[1].csv"
    # print(f"Cramos csv: {siesvi}")
    # df_result.to_csv(siesvi, index=False)
    

    # Une el match_score de df_max al dataframe original de base
    # Usa base_idx como llave para pegar el score a cada fila de base
    df_matches = base.df.join(
        df_max.set_index("base_idx")[["match_score"]],
        how="left"
    )

    # Número total de reglas usadas para comparar
    n = len(base_list)
    # Calcula la confianza del match en porcentaje
    # Ejemplo:
    # 2 matches de 2 reglas = 100
    # 1 match de 2 reglas = 50
    df_matches["confianza"] = (df_matches["match_score"] / n) * 100

    # Obtiene los índices de base que sí tuvieron match
    matched_idx = df_max["base_idx"].dropna().unique()
    # Filtra las filas de base que no aparecen en df_max
    # Estas son las transacciones no conciliadas
    df_unmatched = base.df.loc[
        ~base.df.index.isin(matched_idx)
    ].copy()
    
    
    # df_test = df_base.join( ##Custom, lo de arriba lo dió chatgpt
        # df_max.set_index("base_idx")[["match_score"]],
        # how="left"
    # )
    # n = 2
    # df_test["confianza"] = (df_test["match_score"] / n)*100
    
    
    ##Print
    print(" -- Imprimimos -- ")
    # print(banco.df)
    # print(base.df)
    print(f"df Result: \n{df_result}")
    print("Matches:", len(df_max))
    print("Unmatched:", len(df_unmatched))
    print()
    t1 = time.time()
    tiempo = t1-t0
    print(f"Tiempo de ejecución: {tiempo:,.4f}")