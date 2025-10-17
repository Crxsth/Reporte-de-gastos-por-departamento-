"""2025.09.23. Módulo que inicializa el streamlit
"""
import os
os.system("streamlit run Department_report2.py")



    # st.title("Reporte de gastos")
    # st.subheader("Vista previa"); st.dataframe(archivo_completo.head(5))
    # num_cols = archivo_completo.select_dtypes(include="number").columns.tolist()
    # group_candidates = [c for c in archivo_completo.columns if c not in num_cols] or archivo_completo.columns.tolist()

    # grp = st.selectbox("Columna de agrupación", group_candidates, index=0)
    # met = st.selectbox("Columna numérica", num_cols or archivo_completo.columns.tolist(), index=0)

    # st.success(f"Seleccionaste → Agrupar por: **{grp}** | Métrica: **{met}**")