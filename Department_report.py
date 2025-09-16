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
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from functools import partial
Timer0 = time.time()


class TablaDeDatos: ##Crea una tabla en matplotlib y le da formato de moneda
    def __init__(self, df): ##Init es un objeto que se inicializa al crear una clase.
        #Inicializamos objetos
        self.df = df ##Guardamos el dataframe.
        self.fig = None ##preparamos fig
        self.ax = None ##lugar para dibujar
        self.tabla = None ##espacio para la tabla

    def crear(self):
        fig, ax = plt.subplots(figsize=(12, 4))#ax == un eje es el lienzo donde se dibuja.
        ax.axis("off")  # contro1la la visualización de bordes, ticks, etc.
        # Crear tabla con los datos de tu DataFrame
        tabla = ax.table( ##ax.table dibuja una tabla sobre el eje y devuelve un objeto Table
            cellText=self.df.values,       #valores de la tabla, nuestro dataframe en este caso.
            colLabels=self.df.columns,     #nombres de columnas
            loc="center")                     #posición centrada
        # Ajustar formato
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(10)
        tabla.scale(1.2, 1.2) #escala (ancho, alto)
        for col in self.df.iloc[:, 1:].columns: ##Da formato de moneda, pero convierte en string.
            self.df[col] = self.df[col].map("${:,.2f}".format)
            

def on_click(event): #Acciona evento (tilt) al hacer click.
def on_click(event, ax, bars, fig):
    if event.inaxes is not ax:  # ignora clics fuera del eje
        return
    for rect in bars:
        contains, _ = rect.contains(event)  # ¿el click está dentro del rectángulo?
        if contains:
            # print(f"Click en barra: {rect._dept}")
            rect.set_linewidth(1.5)
            rect.set_edgecolor("black")
            fig.canvas.draw_idle() ##Esto pide el redibujo
            
            timer = fig.canvas.new_timer(interval=100)
            def restore_edge():
                rect.set_edgecolor("None")  # quitamos borde, para hacer como un parpadeo
                fig.canvas.draw_idle()
            timer.add_callback(restore_edge)
            timer.start()
            break

def crear_graph_bars(df): ##Esta función crea gráficas de barra
    ax = df.plot(kind="bar", x="Department", y="Monto_por_departamento", legend=False) ##Crea las gráficas
    fig = ax.figure
    bars = ax.containers[0] #todas las barras
    for rect, dept in zip(bars, df["Department"]):
        rect._dept = dept  # le cuelgas el nombre del depto a cada barra
    cid = fig.canvas.mpl_connect("button_press_event", 
        lambda event:on_click(event, ax, bars,fig))
    
    return fig, ax, bars, cid


if __name__ == "__main__":
    ruta_completa = r"C:\Users\criis\Documents\Coding\Ejemplo Transacciones por report.csv"
    df = pd.read_csv(ruta_completa, encoding="latin-1", header=0)
    serie_depto = df.groupby("Department")[df.columns[4]].sum()#.to_dict() #Agrupa y crea una serie con las sumas.
    #Medidas creando series.
    DE = df.groupby("Department")[df.columns[4]].std()
    promedio = df.groupby("Department")[df.columns[4]].mean()

    #Convertimos series a dataframe
    DE_idx = DE.to_frame(name="Standard deviation").reset_index()
    promedio_idx = promedio.to_frame(name="Average").reset_index()
    CV = ((DE_idx["Standard deviation"] / promedio_idx["Average"]) * 100) #Coeficiente de variacion = (DE/avg)*100
    CV_idx = CV.to_frame(name="CV").reset_index()

    #Armamos el dataframe
    df_report = df.groupby("Department")[df.columns[4]].agg(Monto_por_departamento="sum").reset_index()
    df_report = df_report.merge(DE_idx, on="Department", how="left")
    df_report = df_report.merge(promedio_idx, on="Department", how="left")
    # df_report = df_report.merge(CV, on="Department", how="left")
    # df_report = df.groupby("Department")[df.columns[4]].agg(amount_sum = "sum", amount_avg= "mean").reset_index()
    # tabla = TablaDeDatos(df_report)
    # tabla.crear()
    crear_graph_bars(df_report)

    
    
    
    
    
    
    


    Timer1 = time.time()
    ExecTime = Timer1-Timer0
    print(f"Tiempo de ejecución == {ExecTime}")
    plt.show()
    # print(df_report)
    # print(df_report.to_string())

    print(" --- Saliendo --- ")
    print()