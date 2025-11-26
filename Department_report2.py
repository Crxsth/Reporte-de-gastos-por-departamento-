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
from datetime import date
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
        return self
    
class ReporteUi:
    def __init__(self, base_df: ReporteDf): ##base_df is the object we created with the class ReporteDF
        self.df = base_df.df.copy()
        self.df_ui = base_df.df.copy()
        self.log = []
        self.numeric_columns = list(getattr(base_df, "numeric_columns",[]))
        self.non_numeric_columns = list(getattr(base_df, "non_numeric_columns",[]))
    
    def _modificar_listacampos(self):
        """Cambia las listas de campos para el caso de filtrar por date"""
        lista_var = []
        self.extra_columns = []
        for dato in self.non_numeric_columns.copy():
            if "date" in dato.lower():
                self.extra_columns.append(dato)
                self.non_numeric_columns.remove(dato)
    
    def componentes_interactivos(self):
        """Crea los botones y widgets
        """
        opciones = ["Mes", "Trimestre", "Año"]
        map_periodo = {"Mes":"M", "Trimestre":"Q", "Año":"Y"}
        hoy = date.today()
        ss = st.session_state
        
        if hasattr(self, "numeric_columns") and hasattr(self, "non_numeric_columns"): ##Verifica si existen listas con las columnas...
            ##Widget para añadir 'date' como filtro adicional
            if "date_filter" not in ss:
                ss.date_filter = False
            if "name_filter" not in ss:
                ss.name_filter = False
            col_date_filter, col_name_filter = st.columns(2) ##Toggles filters
            with col_date_filter:
               periodo = st.toggle("Filtrar por fechas:", key = "date_filter")
            with col_name_filter:
               filtro_nombre = st.toggle("Especificar nombre", key = "name_filter")
               
            if ss.date_filter == True:
                self._modificar_listacampos() ##Método que crea una lista con los campos de fecha
            
            
            ##Select boxes
            group = st.selectbox("Columna de agrupación", self.non_numeric_columns, index=0) ##head.strings
            col_metric, col_agg = st.columns(2)
            with col_metric:
                metric = st.selectbox("Columna numérica", self.numeric_columns, index=0)##head.ints
            with col_agg:
                agg = st.selectbox("Métrica de agregación", ["Conteo", "Suma", "Promedio"], index=0) ##Metrics ofc
            
            ##Crea los filtros por fecha y por nombre:
            dict_names = {item:0 for item in self.df_ui[group]} ##Diccionario, key=name, item=0
            if ss.date_filter == True and ss.name_filter==True:
                col_add1, col_add2 = st.columns(2)
                with col_add1:
                    filtro = st.multiselect("Filtro", dict_names, key="multi_select_widget", placeholder=f"Seleccione {group}")
                with col_add2:
                    period = st.selectbox("Fechas", self.extra_columns, index=0)
            elif ss.date_filter == True:
                period = st.selectbox("Fechas", self.extra_columns, index=0)
            elif ss.name_filter == True:
                filtro = st.multiselect(group, dict_names, key="multi_select_widget", placeholder=f"Seleccione {group}")
            
            out_col = f"{agg} de {metric}" ##nombre de la columna 
            
            ##Aquí quiero poner que modifique group y quite "Transaction date" de las opciones del select box
            if "opt_agru" not in ss: ##Key de la agrupación por mes
                ss.opt_agru = "Mes"
            if "tgl_rango" not in ss: ##Key de 'modo' = toggle de rango
                ss.tgl_rango = False
            if "date_from" not in ss: ##Key del rango toggle date_from
                ss.date_from = date(hoy.year,1,1)
            if "date_to" not in ss: ##Key del rango toggle date to
                ss.date_to = hoy
            ##Componentes para date:
            if "toggle_name_widget" not in ss:
                    ss.toggle_name_widget = False

            if "date" in group.lower() or ss.date_filter==True: ##Si es date, agrupamos por mes.
                col1, col2 = st.columns(2)
                with col1:
                    opcion = st.radio("Seleccione agrupación:", opciones, key="opt_agru")
                    valor = map_periodo[opcion]
                    ss.valor_periodo = map_periodo[opcion]
                with col2:
                    modo = st.toggle("Especificar rango:", key="tgl_rango")
                    if modo:
                        subcol1, subcol2 = st.columns(2)
                        with subcol1:
                            start_year = date(hoy.year, 1,1)
                            ss.date_from = pd.to_datetime(st.date_input("Desde", value = ss.date_from, key="date_from_widget"))
                        with subcol2:
                            ss.date_to = pd.to_datetime(st.date_input("Hasta", value = ss.date_to, key="date_to_widget"))
            else:
                ss.tgl_rango = False
                
            self.group = group
            self.metric = metric
            self.agg = agg
            self.out_col = out_col
            if "period" in locals(): self.period = period
            
        else:
            escribir("No data to group")
        return self

    def agrupar(self):
        ss = st.session_state
        agg_map = {"Conteo": "count", "Suma": "sum", "Promedio": "mean"} ##Dict - Es para que el usuario vea "Conteo" en lugar de "count" por ejemplo
        group = self.group
        metric = self.metric
        agg = self.agg
        
        if ss.date_filter==True:
            period = self.period ##Period es nuestra variable adicional para el caso de mostrar nombre y fecha, ejemplo: period = "Transaction_date"

        out_col = self.out_col
        modo = ss.tgl_rango ##Bool que indica si se especificó fecha de datos.
        ##ss.data_filter: Filtramos con las fechas establecidas
        df_base = self.df
        if ss.name_filter == True:
            filtro = ss.multi_select_widget
            if filtro: ##Revisamos que no esté vacío; filtro 
                escribir(f"Filtro we: {filtro}")
                df_base = df_base[df_base[group].isin(filtro)]
        
        if ss.date_filter == True: ##Si tenemos group & period
            period_key = pd.to_datetime(df_base[period], format="%d-%b-%y", errors="coerce")

            if ss.date_filter ==True: ##toggle para agrupar
                if modo == True:
                    period_key = pd.to_datetime(period_key, format="%d-%b-%y", errors="coerce")
                    period_key = period_key.loc[period_key.between(ss.date_from, ss.date_to)]
            period_key = period_key.dt.to_period(ss.valor_periodo)
            period_key.name = period        
            self.df_group = (df_base.groupby(
                                [period_key, group])[metric]
                                .agg(agg_map[agg])
                                .reset_index()
                                .rename(columns={metric:out_col}))
        else: ##Caso normal
            self.df_group = (
                    df_base.groupby([group])[metric]
                    .agg(agg_map[agg])
                    .reset_index()
                    .rename(columns={metric:out_col})
                    )
        
        ##Agrupa si nuestra columna principal es 'date'
        if "date" in group.lower():
            self.df_group[group] = pd.to_datetime(self.df_group[group], format="%d-%b-%y", errors="coerce")##Convierte a fecha
            if modo ==True: ##Agrupa entre periodos en su caso
                self.df_group = self.df_group.loc[self.df_group[group].between(ss.date_from,ss.date_to)]
            self.df_group = (
                        self.df_group.groupby(self.df_group[group].dt.to_period(ss.valor_periodo),
                        dropna=False)[out_col]
                        .agg(agg_map[agg])
                        .reset_index()
                        .rename(columns={"index": group})
                        )
        
        ##Incluímos una serie con porcentajes
        self.df_group["Porcentajes"] = self.df_group[out_col] / self.df_group[out_col].sum() *100
        
        return self

    def show_data(self):
        ss = st.session_state
        out_col = self.out_col
        group = self.group
        metric = self.metric
        ##Sort
        try:
            self.df_group = self.df_group.sort_values(by=self.group, ascending=True)
        except:
            pass
        ## $ format, else = f"{:,.0f}"
        self.df_ui = self.df_group.copy()
        
        if "Porcentajes" in self.df_ui.columns:
            self.df_ui["Porcentajes"] = self.df_ui["Porcentajes"].map("{:.2f}%".format)
            
        
        if "amount" in out_col.lower():
            if "suma" in out_col.lower() or "promedio" in out_col.lower():
                try:
                    self.df_ui[out_col] = self.df_ui[out_col].apply(lambda x: f"${x:,.2f}")
                except:
                    escribir("No se pudo convertir a moneda, ni modo")
        else:
            self.df_ui[out_col] = self.df_ui[out_col].apply(
                lambda x: f"{x:,.0f}" if isinstance(x, (int,float)) else x )
        for col in self.df_ui.columns:
            if "date" in col.lower():
                if col.lower() != self.group.lower(): ##Fuerza date solo si no es nuestro valor principal
                    pass
                    # self.df_ui[col] = pd.to_datetime(self.df_ui[col], errors="ignore").dt.strftime("%d-%b-%y")
        #show:
        st.dataframe(self.df_ui)
        
        # --- Gráfica de barras ---
        df_graph = self.df_group ##no usamos df_ui ya que este tiene valores str
        graph_group_name = out_col
        st.bar_chart(
                    df_graph, x=group, y=graph_group_name, y_label = "Montos", horizontal=False,
                    ) ##Group= str as name; out_col = metric_column.name
        

def boton_escala():
    """
    Crea un botón en Streamlit para cambiar la escala del gráfico.

    Actualmente es un marcador de posición (pendiente de implementar).
    """
    st.subheader("Escala de visualización")
    if st.button("Cambiar escala (pendiente)"):
        pass  # aquí luego conectamos la lógica


def vista_previa(df, n_default=20, titulo=None, key=None):
    """
    Muestra una vista previa de los datos en Streamlit.

    Args:
        df (pd.DataFrame): conjunto de datos a visualizar.
        n_default (int): número inicial de filas a mostrar (default=20).
    """
    col_dict = {}
    if titulo is None: titulo="Vista Previa"
    st.subheader(titulo)
    for col in df.columns:
        if "amount" in col.lower():
            col_dict[col] = st.column_config.NumberColumn(col, format="$%.2f")
    
    key_flag = f"show_preview_{key}" ##Clave de estado
    if key_flag not in st.session_state: ##Inicializa la key
        st.session_state[key_flag] = True
    
    if st.button("Vista previa"): ##Alterna el valor al presionar
        st.session_state[key_flag] = not st.session_state[key_flag]
    
    if st.session_state[key_flag] == True: ##Decide que mostrar, ejemplo if st.ss.key_flag = True: muestra lo de abajo.
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
        Datos cargados desde el archivo.
    """
    archivo_base = st.file_uploader( ##Devuelve un archivo en memoria.
        "Selecciona el archivo de Excel o CSV",
        type=["csv", "xlsx", "xlsm"]
        )
    st.info("Sube un archivo para continuar.")
    
    if not archivo_base:
        return None, None
    
    archivo_id = getattr(archivo_base, "name", None)  # <- ID estable del upload
    
    if archivo_base.name.lower().endswith(".csv"):
        archivo_leido = pd.read_csv(archivo_base, encoding="latin-1", header=0)
    else:
        archivo_leido = pd.DataFrame(leer_file(archivo_base)) ##Lo leemos con nuestro lector personalizado
    return archivo_leido, archivo_id


def escribir(texto):
    st.write(texto)
    print(texto)

def show_button(nombre):
    key_flag = f"show_preview_{titulo}" ##Creamos variable true/false
    if key_flag not in st.session_state:
        st.session_state[key_flag] = True
    if st.button("Vista previa"): ##Alterna el valor al presionar
        st.session_state[key_flag] = not st.session_state[key_flag]
    if st.session_state[key_flag]:
        print("A")


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
    ss = st.session_state
    
    ##Execution.count(), por temas de revisión
    if "contador_main" not in ss:
        ss.contador_main = 1
    else:
        ss.contador_main +=1
        # escribir(f"contador we: {ss.contador_main}")
        st.write(f"ejecuciones we: {ss.contador_main}")

    archivo_base, archivo_id = obtener_dataframe() ##Lee un [csv, xlsx, xlsm] y retorna un dataframe con los datos.
    if archivo_base is None:
        st.stop()

    if "archivo_id" not in ss: ##Lo inicializamos si no existía
        ss.archivo_id = None
    
    if "reporte" not in ss or ss.get("archivo_id") != archivo_id: ##Evita re-ejecuciones cada que actualicemos el st
        ##Es decir, si no han subido archivo lo calculamos
        reporte = ReporteDf(archivo_base) ##Es una instancia con propiedades.
        reporte.fix_header() ##if header = none or int, header = iloc[0]
        reporte.fix_dates()
        reporte.fix_numbers()
        ss.reporte = reporte
        # ss.archivo_id = archivo_id
    else:
        st.write(f"Else1: usando archivo previo → {ss.archivo_id}") ##Si el archivo no ha sido modificado, pues usamos el existente.
        reporte = ss.reporte
    
    if "reporte" not in st.session_state: ##Si no hemos ejecutado el formatting, stop.
        st.stop()

    st.title("Reporte de gastos")
    vista_previa(reporte.df, 20, "Datos generales", key="datos_generales_0")
    
    ##Datos agrupados
    ui = ReporteUi(reporte)
    ui.componentes_interactivos()
    ui.agrupar()
    ui.show_data()
    
    
    #Tests:
    pruebas = False
    if pruebas == True:
        with st.sidebar:
            depto = st.selectbox(
                "Selecciona un departamento",
                ["Ventas", "Finanzas", "Recursos Humanos"]
            )
            st.write(f"Departamento elegido: {depto}")
        contenedor = st.container()

        with contenedor:
            st.subheader("Sección agrupada")
            st.write("Este texto y este slider están en el mismo container.")
            valor = st.slider("Elige un valor", 0, 100, 50)
            st.write(f"Valor seleccionado: {valor}")




    
    # ui.set_group_df()
    # ui.porcentajes()
    # ss.ui = ui
    
    
    # Timer1 = time.time()
    # ExecTime = Timer1 - Timer0
    # print(f"Execution time: {ExecTime:,.2f}s")
    
if __name__ == "__main__":
    main()