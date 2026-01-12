"""2026.01.09. Este módulo inicializa streamlit y coordina todo"""
import streamlit as st
import sys
ruta_completa = r"C:\Users\criis\Documents\Coding\Repositorio-git"
sys.path.append(ruta_completa)
from xlsx_reader import leer_file ##Este es un lector de xlsx que no lee 'inlinestring'


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
    ui.graficar()
    
    
    #Tests:
    pruebas = False
    with st.sidebar:
        st.button("Datos agrupados")
    with st.sidebar:
        st.button("Datos 2")
        
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