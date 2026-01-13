"""2025.09.23. Módulo que inicializa el streamlit
"""
import os
import sys
from streamlit.web import cli as stcli
import webbrowser
import multiprocessing

# os.system("streamlit run Department_report2.py")

##Lo de abajo funcionó para un archivo.exe 
def main():
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    app_path = os.path.join(base_dir, "app.py")
    
    sys.argv = [
    "streamlit",
    "run",
    app_path,
    "--server.headless=true",
    "--server.port=8501",
    "--server.address=127.0.0.1",
    "--global.developmentMode=false",
    ]

    webbrowser.open("http://localhost:8501")
    stcli.main()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
    
    # st.title("Reporte de gastos")
    # st.subheader("Vista previa"); st.dataframe(archivo_completo.head(5))
    # num_cols = archivo_completo.select_dtypes(include="number").columns.tolist()
    # group_candidates = [c for c in archivo_completo.columns if c not in num_cols] or archivo_completo.columns.tolist()

    # grp = st.selectbox("Columna de agrupación", group_candidates, index=0)
    # met = st.selectbox("Columna numérica", num_cols or archivo_completo.columns.tolist(), index=0)

    # st.success(f"Seleccionaste → Agrupar por: **{grp}** | Métrica: **{met}**")
input("")