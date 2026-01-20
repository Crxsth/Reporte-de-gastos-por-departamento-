import pandas as pd
import numpy
import sys
import re
ruta_completa = r"C:\Users\criis\Documents\Coding\Repositorio-git"
sys.path.append(ruta_completa)
from xlsx_reader import leer_file ##Este es un lector de xlsx que no lee 'inlinestring'


def load_file(archivo_base):
    ##Lee un archivo, devuelve un df
    if archivo_base.name.lower().endswith(".csv"):
        archivo_leido = pd.read_csv(archivo_base, encoding="latin-1", header=0)
    else:
        archivo_leido = pd.DataFrame(leer_file(archivo_base)) ##Lo leemos con nuestro lector personalizado
    return archivo_leido