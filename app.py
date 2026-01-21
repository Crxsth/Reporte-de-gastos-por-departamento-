"""2026.01.09. Este módulo inicializa streamlit y coordina todo"""
import time
import csv
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import sys
from datetime import datetime
##Libraries:
ruta_completa = r"C:\Users\criis\Documents\Coding\Repositorio-git"
sys.path.append(ruta_completa)
# import core
import excel_workspace #1
import report_visual #2
import conciliador #8
from xlsx_reader import leer_file ##Este es un lector de xlsx que no lee 'inlinestring'

def save_exec_times_to_csv(csv_path="exec_time.csv"):
    ##Yes, timers by chatgpt as idc enough
    ss = st.session_state
    date_col = datetime.now().strftime("%Y.%m.%d")

    # Caso 1: archivo no existe → crear
    if not os.path.exists(csv_path):
        with open(csv_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([date_col])
            for t in ss.render_times:
                writer.writerow([t])
        return

    # Caso 2: archivo existe → leer
    with open(csv_path, mode="r", newline="") as f:
        rows = list(csv.reader(f))

    headers = rows[0]
    data_rows = rows[1:]

    # Ver si la fecha ya existe
    if date_col in headers:
        col_idx = headers.index(date_col)
    else:
        headers.append(date_col)
        col_idx = len(headers) - 1

        # extender filas existentes
        for row in data_rows:
            row.append("")

    # asegurar suficientes filas
    while len(data_rows) < len(ss.render_times):
        data_rows.append([""] * len(headers))

    # insertar valores
    for i, t in enumerate(ss.render_times):
        data_rows[i][col_idx] = t

    # escribir de vuelta
    with open(csv_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data_rows)


def fade_in_func(text):
    """Esto hace una animación Fade-in en 'css' según, yo realmente no sé
    """
    st.markdown("""
        <style>
        .fade-in {
          animation: fadeIn 0.6s ease-in-out;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<div class="fade-in">Hola, aparezco suave</div>', unsafe_allow_html=True)


def render_client_timer(_key: str):
    ##Yes, timerx2 by ChatGPT as idc enough x2
    nonce = int(time.time() * 1000)  # cambia en cada rerun
    components.html(
        f"""
        <div id="client-timer"
             style="font-size:12px;opacity:0.85;color:#FFFFFF;font-family:sans-serif;">
        </div>
        <script>
          // cache-buster nonce: {nonce}
          const t0 = performance.now();
          requestAnimationFrame(() => {{
            requestAnimationFrame(() => {{
              const t1 = performance.now();
              document.getElementById("client-timer").textContent =
                `⏱️ Render cliente (aprox): ${{(t1 - t0).toFixed(1)}} ms`;
            }});
          }});
        </script>
        """,
        height=30,
    )


def log_render_time(t):
    st.session_state.render_times.append(t)


def pagina_menu():
    st.title("Bienvenido")
    st.set_page_config(
    page_title="Dashboard Contable", layout = "centered", initial_sidebar_state="expanded")
    st.markdown(
    """
    ### 👋 ¿Qué es este dashboard?

    Este proyecto está diseñado para **profesionistas que trabajan con datos**  
    —contadores, managers, contralores, analistas—  
    que realizan **tareas repetitivas** con archivos Excel, CSV y documentos.

    ---
    ### 🎯 ¿Qué podrás hacer aquí?

    - Visualizar archivos muy grandes sin lag  
    - Analizar y resumir información rápidamente  
    - Automatizar tareas repetitivas  
    - Preparar reportes visuales listos para presentar  

    ---
    ### 🧭 ¿Cómo se usa?

    Utiliza el **menú lateral** para navegar entre las distintas herramientas.
    Cada sección está pensada para resolver un problema específico de forma clara
    y directa.

    ---
    ### 🚀 Enfoque del proyecto

    - Interfaz simple y clara  
    - Herramientas prácticas, no complejas  
    - Pensado para el día a día profesional  

    """)


def obtener_dataframe(): ##Function that selects a file to work with. 
    """
    Abre un selector de archivos en Streamlit y llama al core para cargar el archivo.

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
    archivo_leido = core.load_file(archivo_base)
    return archivo_leido, archivo_id


def main():
    ss = st.session_state
    start = time.perf_counter()
    ##Almacenaremos los tiempos de ejecución
    if "render_times" not in ss: 
        ss.render_times = []
    if "page" not in ss:
        ss.page = "menu"
    
    

    ##Contador 
    ss.contador_main = ss.get("contador_main", 0) + 1
    render_client_timer("timer_data")
    if ss.contador_main %10 ==0:
        save_exec_times_to_csv()
    
    st.write(f"ejecuciones we: {ss.contador_main}")

    with st.sidebar:
        st.title("Herramientas", text_alignment="center")

        st.divider()
        if st.button("Main Menu", width="stretch"):
            ss.page="menu"
        st.divider()
        if st.button("Excel workspace", width="stretch"):
            ss.page="Excel workspace"
        if st.button("Reporte visual", width="stretch"):
            ss.page="report"
        if st.button("Separar archivos", width="stretch"):
            ss.page="separar"
        if st.button("Unir archivos", width="stretch"):
            ss.page="unir"
        if st.button("OCR", width="stretch"):
            ss.page="ocr"
        if st.button("7 i forgot", width = "stretch"):
            ss.page="7"
        if st.button("Conciliate", width = "stretch"):
            ss.page="conciliate"
    
    
    if ss.page not in ss:
        page="menu"
    page = ss.page
    
    if page=="menu":
        pagina_menu()
    elif page=="Excel workspace": ##1
        st.title("Excel Workspace")
        excel_workspace.workspace_render()
    
    elif page=="report": ##2
        st.title("Reporte visual")
        report_visual.report_render()
    elif page=="conciliate": ##8
        st.title("Conciliar")
        conciliador.render_conciliate()
    
    
    else:
        st.write("JAJAJA NO LE SALIÓ")
    
    # st.write("ss")
    # st.write(ss)
    log_render_time(time.perf_counter() - start)

if __name__ == "__main__":
    main()