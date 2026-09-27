import streamlit as st

def guardar_archivo_subido(uploaded_file, nombre_destino):
    if uploaded_file is not None:
        with open(nombre_destino, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    return False

def render():
    st.subheader("📊 Secciones 4, 5 y 6: Información de Entrada, Metodología y Escenarios")
    st.write("Personaliza la zona de influencia, curvas de demanda vs generación, normativa aplicable y escenarios de análisis.")

    st.markdown("### 4.1 Modelo de la zona de influencia")
    default_sec4_1 = r"En la \cref{fig:Unifilar} se presenta el diagrama unifilar del circuito \CTO\ suministrado por el OR."
    sec4_1_texto = st.text_area("Texto de Zona de Influencia (4.1):", value=default_sec4_1, height=70)
    up_unifilar = st.file_uploader("Subir 'UnifilarCTO.png'", type=["png", "jpg", "jpeg"], key="up_unifilar")
    if guardar_archivo_subido(up_unifilar, "UnifilarCTO.png"):
        st.success("✅ UnifilarCTO.png guardado.")

    st.markdown("---")
    st.markdown("### 4.2 y 4.3 Horizonte y Demanda de Potencia")
    default_sec4_2 = (
        r"En el numeral 7.1 de la circular CREG 021 de 2022, se establece el horizonte de análisis, "
        r"en la \cref{tab:horizonte} se presentan los años a analizar según la información suministrada."
    )
    sec4_2_texto = st.text_area("Texto Horizonte de análisis (4.2):", value=default_sec4_2, height=70)

    default_sec4_3 = (
        r"La energía demandada por el circuito fue suministrada por el OR en la \cref{tab:demandaenergia}, "
        r"en la cual se especifica la demanda del circuito por hora."
    )
    sec4_3_texto = st.text_area("Texto Demanda de potencia (4.3):", value=default_sec4_3, height=70)
    up_dem_csv = st.file_uploader("Subir 'DemandaEnergia.csv'", type=["csv"], key="up_dem_energia")
    if guardar_archivo_subido(up_dem_csv, "DemandaEnergia.csv"):
        st.success("✅ DemandaEnergia.csv guardado.")

    st.markdown("---")
    st.markdown("### 4.4 Información de energía producida Vs Energía demandada")
    default_sec4_4_intro = (
        r"Para el consumo y la generación promedio por hora, se toman los datos que se muestran en la \cref{tab:consumoVSgeneracion}."
    )
    sec4_4_intro = st.text_area("Párrafo introductorio (4.4):", value=default_sec4_4_intro, height=70)

    default_sec4_4_curva = (
        r"Por parte de EPM se suminstró el perfil de demanda del circuito 211-11 de la subestación Doradal 13.2kV, "
        r"segun la \cref{fig:curvadecarga211}, es importante destacar que de esta curva que correcponde a un día típioco mínimo "
        r"se estrajeron las horas de 9:00 am, 12:00 pm y 3:00 pm ya que son los horarios de generación máxima y donde el proyecto "
        r"fotovoltaico va a presnetar un mayor impacto."
    )
    sec4_4_curva = st.text_area("Párrafo explicativo de la curva de carga del circuito:", value=default_sec4_4_curva, height=100)
    caption_curva_cto = st.text_input(
        "Caption de la figura de curva de carga:",
        value="Demanda de circuito 211-11 suministrado por el operador de red"
    )

    default_sec4_4_comp = r"En la \cref{fig:consumoygeneracion}, se compara el consumo y la genreación por hora del circuito 211-11."
    sec4_4_comp = st.text_area("Párrafo de comparación consumo vs generación:", value=default_sec4_4_comp, height=70)

    c_up1, c_up2, c_up3 = st.columns(3)
    with c_up1:
        up_cvg_csv = st.file_uploader("Subir 'consumoVSgeneracion.csv'", type=["csv"], key="up_cvg_csv")
        if guardar_archivo_subido(up_cvg_csv, "consumoVSgeneracion.csv"):
            st.success("✅ consumoVSgeneracion.csv guardado.")
    with c_up2:
        up_curva_png = st.file_uploader("Subir 'curva de carga cto211.png'", type=["png", "jpg", "jpeg"], key="up_curva211")
        if guardar_archivo_subido(up_curva_png, "curva de carga cto211.png"):
            st.success("✅ curva de carga cto211.png guardado.")
    with c_up3:
        up_cygen_png = st.file_uploader("Subir 'consumoygeneracion.png'", type=["png", "jpg", "jpeg"], key="up_cygen")
        if guardar_archivo_subido(up_cygen_png, "consumoygeneracion.png"):
            st.success("✅ consumoygeneracion.png guardado.")

    st.markdown("---")
    st.markdown("### 5. Metodología y 6. Descripción de los escenarios de análisis")
    default_sec5_intro = (
        r"Para el desarrollo del presente informe se emplea la información suministrada por \OR, esta base de datos contiene el sistema "
        r"de distribución local desde el nodo de conexión de la S/E \SSEE, en un circuito radial de \NT. Los análisis se realizan para el circuito \CTO."
    )
    sec5_intro = st.text_area("Párrafo introductorio Sección 5 (Metodología):", value=default_sec5_intro, height=80)

    default_sec6_despacho = (
        r"Para la demanda se consideró la información suminstrada por EPM y de acuerdo con el OR y el Consejo Nacional de Operación (CNO) "
        r"con los lineamientos para estudios de conexión simplificado en el marco de la resolución CREG 174 de 2021, el estudio se realizó bajo los siguientes escenarios:"
    )
    sec6_despacho = st.text_area("Descripción del despacho de demanda (Sección 6):", value=default_sec6_despacho, height=90)

    default_sec6_gen_max = (
        r"Para proyectos de generación fotovoltaico se presenta la generación máxima del proyecto a las 9:00 am, 12:00 pm y 3:00 pm, "
        r"ya que la generación no es controlable y el único cambio presentado es la demanda, adicionalmente se considera el caso de demanda mínima "
        r"(suministrada por el operador de red) para considerar las peores condiciones posibles donde la energía demandada por el circuito es la menor "
        r"por lo que la disponibilidad de capacidad de transmisión es menor."
    )
    sec6_gen_max = st.text_area("Detalle de generación máxima y demanda coincidente (Sección 6):", value=default_sec6_gen_max, height=110)

    datos = {
        "sec4_1_texto": sec4_1_texto,
        "sec4_2_texto": sec4_2_texto,
        "sec4_3_texto": sec4_3_texto,
        "sec4_4_intro": sec4_4_intro,
        "sec4_4_curva": sec4_4_curva,
        "caption_curva_cto": caption_curva_cto,
        "sec4_4_comp": sec4_4_comp,
        "sec5_intro": sec5_intro,
        "sec6_despacho": sec6_despacho,
        "sec6_gen_max": sec6_gen_max
    }
    st.session_state["datos_sec_4_5_6"] = datos
    return datos
