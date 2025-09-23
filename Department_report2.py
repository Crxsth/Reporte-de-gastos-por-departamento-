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
import sys


def select_file(): ##Function that reads csv or excel file.
    root = tk.Tk()
    root.withdraw()
    ruta_completa = filedialog.askopenfilename(
        initialdir=r"C:\Users\criis\Documents\Coding",
        title="Selecciona el archivo de Excel",
        filetypes=[("Archivos de Excel", "*.xlsm *.xlsx *.csv"), ("Todos los archivos", "*.*")]
    )
    if not ruta_completa:
        ruta_completa = none


def main():
    Timer0 = time.time()
    ruta_completa = r"C:\Users\criis\Documents\Coding\Repositorio-git"
    sys.path.append(ruta_completa)
    from xlsx_reader import leer_file ##Este es un lector de xlsx que no lee 'inlinestring'
    archivo = select_file()
    
    
    Timer1 = time.time()
    ExecTime = Timer1 - Timer0
    print(f"Execution time: {ExecTime:,.2f}s")
    
if __name__ == "__main__":
    main()
    
