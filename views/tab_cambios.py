import streamlit as st
import pandas as pd

def render():
    st.subheader("Tabla de Control de Cambios del Documento")
    st.write("Edita las versiones, descripciones, fechas y observaciones correspondientes al historial del informe.")

    datos_iniciales_cambios = pd.DataFrame([
        {"VERSIÓN No.": "0", "DESCRIPCIÓN": "Informe Inicial.", "FECHA": "23/09/2026", "OBSERVACIONES": ""},
        {"VERSIÓN No.": "1", "DESCRIPCIÓN": "Ajuste por insumos del OR", "FECHA": "06/07/2026", "OBSERVACIONES": ""}
    ])

    df_control_cambios = st.data_editor(
        datos_iniciales_cambios, 
        num_rows="dynamic", 
        key="editor_control_cambios",
        use_container_width=True
    )
    
    return df_control_cambios