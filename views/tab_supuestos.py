import streamlit as st
import pandas as pd
import os

TEXTO_ESTANDAR_1_2 = (
    "\\subsection{\\textit{Supuestos y herramienta de modelación}}\n"
    "La información requerida para el modelamiento del área de influencia fue suministrada por el cliente y el OR "
    "comprendiendo el diagrama unifilar con sus respectivos nodos asociados al proyecto y sus respectivas cargas "
    "con el comportamiento en potencia activa y reactiva. El modelamiento de dicho diagrama unifilar se realizó "
    "en el software Digsilent Power Factory.\\\\\n"
    "\\\\\n"
    "\\supuestos"
)

def render():
    st.subheader("Sección 1.2: Supuestos y herramienta de modelación")
    st.write("Selecciona o edita los párrafos descriptivos y la procedencia de la tabla de crecimiento de demanda.")

    with st.expander("📄 Ver texto estándar fijo de la Sección 1.2", expanded=True):
        st.code(TEXTO_ESTANDAR_1_2, language="latex")

    tipo_escenario = st.radio(
        "Seleccionar tipo de redacción para el comando \\supuestos:",
        [
            "Escenario 1: Tasa de crecimiento suministrada directamente por el OR",
            "Escenario 2: Horizonte no definido por el OR (Uso de valor estándar UPME, t+x de 5 años)"
        ]
    )

    if tipo_escenario.startswith("Escenario 1"):
        texto_supuesto_default = (
            "Según la información suministrada por el OR se tiene que el horizonte de análisis del proyecto es \\YearInicial\\ y (t+3) \\YearFinal\\, "
            "los valores de tasa de crecimiento para escalar la demanda equivalente de la subestación se tomaron de los datos suministrados por el OR. % donde "
            "se sugiere un aumento del 1.04\\% de la demanda\\\\"
        )
    else:
        texto_supuesto_default = (
            "En la información suministrada por el OR no se definió el escenario de análisis (t+x), por lo tanto se tomó un valor de 5 años, que es un "
            "dato utilizado por otros OR para este tipo de análisis, de esta forma se tiene que el horizonte de análisis del proyecto es \\YearInicial\\ y (t+5) "
            "\\YearFinal\\, los valores de tasa de crecimiento para escalar la demanda equivalente de la subestación se tomaron de los datos suministrados por la UPME, en la \\cref{tab:UPME}\\\\"
        )

    texto_supuesto_activo = st.text_area(
        "Contenido del comando \\supuestos (editable):",
        value=texto_supuesto_default,
        height=110
    )

    st.markdown("---")
    st.markdown("#### Fuente de Datos de Proyección de Demanda")
    
    usar_tabla_upme = st.checkbox("Usar la tabla predeterminada de la UPME", value=True)

    # Campo editable para el título (\caption) de la tabla en el PDF
    titulo_default = (
        "Proyección de demanda de energía eléctrica (GWh) - UPME"
        if usar_tabla_upme
        else "Proyección de demanda suministrada por el Operador de Red"
    )
    titulo_tabla_supuestos = st.text_input(
        "Título de la tabla en el informe (Caption):",
        value=titulo_default,
        key="input_titulo_tabla_supuestos"
    )
    st.session_state["titulo_tabla_supuestos"] = titulo_tabla_supuestos

    df_supuestos_upme = None
    archivo_or_path = None

    if usar_tabla_upme:
        st.write("Editando tabla estándar de la UPME (Región Antioquia):")
        datos_iniciales_upme = pd.DataFrame([
            {"Año": 2026, "Esc. Medio": 12.010, "IC Sup. 95%": 12.324, "IC Inf. 95%": 11.698, "IC Sup. 68%": 12.179, "IC Inf. 68%": 11.842, "Tasa Crec.": "-"},
            {"Año": 2027, "Esc. Medio": 12.404, "IC Sup. 95%": 13.134, "IC Inf. 95%": 11.678, "IC Sup. 68%": 12.795, "IC Inf. 68%": 12.015, "Tasa Crec.": "1,033"},
            {"Año": 2028, "Esc. Medio": 12.490, "IC Sup. 95%": 13.459, "IC Inf. 95%": 11.528, "IC Sup. 68%": 13.009, "IC Inf. 68%": 11.974, "Tasa Crec.": "1,007"},
            {"Año": 2029, "Esc. Medio": 12.669, "IC Sup. 95%": 13.842, "IC Inf. 95%": 11.505, "IC Sup. 68%": 13.298, "IC Inf. 68%": 12.045, "Tasa Crec.": "1,014"},
            {"Año": 2030, "Esc. Medio": 12.888, "IC Sup. 95%": 14.248, "IC Inf. 95%": 11.541, "IC Sup. 68%": 13.617, "IC Inf. 68%": 12.166, "Tasa Crec.": "1,017"},
            {"Año": 2031, "Esc. Medio": 13.163, "IC Sup. 95%": 14.704, "IC Inf. 95%": 11.639, "IC Sup. 68%": 13.989, "IC Inf. 68%": 12.345, "Tasa Crec.": "1,021"},
            {"Año": 2032, "Esc. Medio": 13.428, "IC Sup. 95%": 15.141, "IC Inf. 95%": 11.735, "IC Sup. 68%": 14.347, "IC Inf. 68%": 12.520, "Tasa Crec.": "1,02"}
        ])
        df_supuestos_upme = st.data_editor(
            datos_iniciales_upme,
            num_rows="dynamic",
            key="editor_tabla_upme",
            use_container_width=True
        )
    else:
        st.info("Has desactivado la tabla UPME. Sube a continuación la tabla personalizada suministrada por el Operador de Red (OR).")
        col_img_or, col_excel_or = st.columns(2)
        
        with col_img_or:
            up_img = st.file_uploader("Subir tabla del OR como Imagen (PNG, JPG)", type=["png", "jpg", "jpeg"])
            if up_img is not None:
                os.makedirs("modulos_latex", exist_ok=True)
                archivo_or_path = "modulos_latex/tabla_or_custom.png"
                with open(archivo_or_path, "wb") as f:
                    f.write(up_img.getbuffer())
                st.success("✅ Imagen de tabla del OR cargada correctamente.")

        with col_excel_or:
            up_xlsx = st.file_uploader("Subir tabla del OR en Excel (XLSX, XLS)", type=["xlsx", "xls"])
            if up_xlsx is not None:
                os.makedirs("modulos_latex", exist_ok=True)
                archivo_or_path = "modulos_latex/tabla_or_custom.xlsx"
                with open(archivo_or_path, "wb") as f:
                    f.write(up_xlsx.getbuffer())
                st.success("✅ Archivo Excel del OR cargado correctamente.")

    return texto_supuesto_activo, usar_tabla_upme, df_supuestos_upme, archivo_or_path
