"""2025.08.28. El propósito de este código es analizar un grupo de datos, obtener sus totales y graficarlos.
Se busca:
    1.- Crear un reporte de gastos por departamento, mostrar en qué departamentos hay más gastos. Graficar.
        Crear un reporte de gastos por empleado.
        
    2.- Calculamos el tiempo que se tardan en reportar cada departamento/ employee.
        Marcamos a los empleados que superen la media + 1 desviación estándar.
        Crear un histograma.

    3.- 3 KPI's útiles; definirlas y presentarlas:
        Total de gastos, % de gastos reportados fuera de tiempo, departamento más costoso, empleados con mayor monto acumulado.
        
    4.- Bonus de mi compa el chatgpt
        Mostrar que el archivo Python funciona.
        Guardar el archivo en un excel.
        Graficar directamente.
    
Header: ["Report ID", "Department", "Employee", "Report Type", "Amount", "Transaction date", "Report Date"]
"""
import time
Timer0 = time.time()
import pandas as pd
ruta_completa = r"C:\Users\criis\Documents\Coding\Ejemplo Transacciones por report.csv"
df = pd.read_csv(ruta_completa, encoding="latin-1", header=0)
#2.- Almacenar en un diccionario los departamentos.
dict_depto = {}
for valor in df.iloc[:,1]:
    if valor not in dict_depto:
        dict_depto[valor] = None
#3.- Crea un diccionario por departamento con los montos.
serie_depto =  df.groupby("Department")[df.columns[4]].sum()#.to_dict() #Agrupa y crea una serie con las sumas.
serie_depto.name = "Amount sum" 
print(serie_depto)

dict_depto = serie_depto.to_dict() ##Convierte la serie a diccionario.


Timer1 = time.time()
ExecTime = Timer1-Timer0
print(f"Tiempo de ejecución == {ExecTime}")