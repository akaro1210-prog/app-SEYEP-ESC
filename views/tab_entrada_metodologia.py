import streamlit as st
from secciones_manager import (
    render_control_seccion,
    render_control_subseccion,
    render_boton_agregar_seccion,
)


def guardar_archivo_subido(uploaded_file, nombre_destino):
    if uploaded_file is not None:
        with open(nombre_destino, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    return False


def render():
    st.subheader("📊 Secciones 4, 5 y 6: Información de Entrada, Metodología y Escenarios")
    st.write("Personaliza la zona de influencia, curvas de demanda vs generación, normativa aplicable y escenarios de análisis.")

    # =========================================================================
    # SECCIÓN 4: INFORMACIÓN DE ENTRADA Y SUPUESTOS DE SALIDA
    # =========================================================================
    render_control_seccion("sec_4", "Sección 4: Información de Entrada y Supuestos de Salida")

    st.markdown("### 4.1 Modelo de la Zona de Influencia")
    render_control_subseccion("subsec_4_1", "Modelo de la zona de influencia (Diagrama Unifilar)")

    default_sec4_1 = r"En la \cref{fig:Unifilar} se presenta el diagrama unifilar del circuito \CTO\ suministrado por el OR."
    sec4_1_texto = st.text_area("Texto de Zona de Influencia (4.1):", value=default_sec4_1, height=70)
    up_unifilar = st.file_uploader("Subir 'UnifilarCTO.png'", type=["png", "jpg", "jpeg"], key="up_unifilar")
    if guardar_archivo_subido(up_unifilar, "UnifilarCTO.png"):
        st.success("✅ UnifilarCTO.png guardado.")

    st.markdown("---")
    st.markdown("### 4.2 Horizonte de Análisis")
    render_control_subseccion("subsec_4_2", "Horizonte de análisis (Tabla CREG 021)")

    default_sec4_2 = (
        r"En el numeral 7.1 de la circular CREG 021 de 2022, se establece el horizonte de análisis, "
        r"en la \cref{tab:horizonte} se presentan los años a analizar según la información suministrada."
    )
    sec4_2_texto = st.text_area("Texto Horizonte de análisis (4.2):", value=default_sec4_2, height=70)

    st.markdown("---")
    st.markdown("### 4.3 Demanda de Potencia del Circuito")
    render_control_subseccion("subsec_4_3", "Demanda de potencia del circuito (Tabla y CSV)")

    default_sec4_3 = (
        r"La energía demandada por el circuito fue suministrada por el OR en la \cref{tab:demandaenergia}, "
        r"en la cual se especifica la demanda del circuito por hora."
    )
    sec4_3_texto = st.text_area("Texto Demanda de potencia (4.3):", value=default_sec4_3, height=70)
    up_dem_csv = st.file_uploader("Subir 'DemandaEnergia.csv'", type=["csv"], key="up_dem_energia")
    if guardar_archivo_subido(up_dem_csv, "DemandaEnergia.csv"):
        st.success("✅ DemandaEnergia.csv guardado.")

    st.markdown("---")
    st.markdown("### 4.4 Información de Energía Producida Vs Energía Demandada")
    render_control_subseccion("subsec_4_4", "Información de energía producida vs. Energía demandada")

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

    # Botón para agregar secciones adicionales en Sección 4
    render_boton_agregar_seccion("sec_4", "Sección 4 (Información de Entrada)")

    st.markdown("---")

    # =========================================================================
    # SECCIÓN 5: METODOLOGÍA DE ANÁLISIS
    # =========================================================================
    render_control_seccion("sec_5", "Sección 5: Metodología de Análisis")

    st.markdown("### 5.1 Criterios Técnicos Normativos")
    render_control_subseccion("subsec_5_1", "Criterios técnicos normativos (Resolución CREG 021 de 2022)")

    default_sec5_intro = (
        r"Para el desarrollo del presente informe se emplea la información suministrada por \OR, esta base de datos contiene el sistema "
        r"de distribución local desde el nodo de conexión de la S/E \SSEE, en un circuito radial de \NT. Los análisis se realizan para el circuito \CTO."
    )
    sec5_intro = st.text_area("Párrafo introductorio Sección 5 (Metodología):", value=default_sec5_intro, height=80)

    with st.expander("Ver / Editar Criterios Técnicos Normativos (5.1)", expanded=False):
        default_sec5_1 = (
            r"Para garantizar una conexión y operación que cumpla los criterios técnicos de calidad, seguridad y confiabilidad, en el diseño, ejecución y mantenimiento del proyecto se realiza este estudio bajo las siguientes normativas colombianas. \begin{itemize} \item Reglamento técnico de instalaciones eléctricas (RETIE).\item Circular CREG 021 de 2022.\item Circular CREG 174 de 2021.\item Circular CREG 015 de 2018.\item Circular CREG 025 de 1995.\\\end{itemize}Teniendo en cuenta las anteriores normativas se establece algunos de los criterios y límites para tener en cuenta dentro de este documento.\\\begin{itemize} \item CREG 025 de 1995, “El STN se planeará de tal forma que permita, en conjunto con la generación, los sistemas de transmisión regionales y los sistemas de distribución local, Asegurar que la tensión en las barras de carga a nivel de 220 kV y superiores no sea inferior al 90\% del valor nominal, ni superior al 110\%”.\item Circular CREG 174 de 2021, en caso de implementar inversores en los proyectos, la capacidad del proyecto corresponde a la sumatoria de las capacidades nominales de los inversores, en el lado con conexión al SIN, la capacidad se deberá asumir con un factor de potencia unitario. \item Circular CREG 025 de 1995, Para las líneas de transmisión se consideran flujos aceptables, en condiciones normales de operación, cuando sean iguales o menores del 100\% de su capacidad nominal. En contingencia se admiten sobrecargas hasta el valor máximo permitido para el elemento bajo condiciones de emergencia y que se encuentra declarado por el agente propietario en el PARATEC. \item Para transformadores se consideran flujos aceptables en condiciones normales de operación, cuando sean iguales o menores del 100\% de su capacidad nominal. En contingencia se admiten sobrecargas hasta el valor máximo permitido para el elemento bajo condiciones de emergencia y que se encuentra declarado por el agente propietario en el PARATEC.\item Artículo 5 de la resolución CREG 030 de 2018, Literal a, Literal c, “La Cantidad de energía en una hora se pueden entregar los GD o AGEP que entregan energía a la red, cuyo sistema de producción de energía sea el compuesto por fotovoltaico sin capacidad de almacenamiento, conectados al mismo circuito o transformador del nivel de tensión 1, no debe superar el 50\% de promedio anual de las horas de mínima demandad diaria de energía registradas para el año anterior al de solicitud de conexión en la franja horaria comprometida entre 6 am y 6 pm.”\end{itemize}"
        )
        sec5_1_texto = st.text_area("Texto normativo CREG/RETIE (5.1):", value=default_sec5_1, height=140)

    st.markdown("### 5.2 Descripción de los Análisis a Realizar")
    render_control_subseccion("subsec_5_2", "Descripción de los análisis a realizar (Flujo, Cortocircuito, Protecciones)")

    with st.expander("Ver / Editar Descripción de los Análisis Técnicos (5.2)", expanded=False):
        default_sec5_2 = (
            r"En el presente estudio de conexión se realizan los siguientes análisis técnicos del proyecto solar fotovoltaico de generación y consumo:\\"
            r"A continuación, se instalan los estudios realizados: \begin{itemize}"
            r"    \item \textbf{Generación de energía eléctrica:} proyección de la máxima generación del proyecto solar a la red de distribución de energía eléctrica propiedad OR."
            r"    \item \textbf{Consumo de la instalación eléctrica:} Estimado de la energía requerida por el cliente OR."
            r"    \item \textbf{Estudio de flujo de carga:} Monitorear los niveles de tensión en las barras; así como la cargabilidad en transformadores y líneas de transmisión para que no sobrepasen los límites permitidos."
            r"    \item \textbf{Estudio de pérdidas:} Analizar las pérdidas del sistema de distribución locas (SDL) con la inclusión del proyecto de generación."
            r"    \item \textbf{Estudio de cortocircuito:} Monitorear los aportes de corriente de cortocircuito en las subestaciones, así como monitorear que estas no se sobrepasen los niveles máximos de corto en las subestaciones del sistema."
            r"    \item \textbf{Estudio de protecciones:} Analizar el comportamiento de las protecciones del OR en conjunto con las del proyecto de generación para diferentes eventos en el SDL, buscando garantizar selectividad y confiabilidad."
            r"\end{itemize}"
        )
        sec5_2_texto = st.text_area("Texto de estudios técnicos a realizar (5.2):", value=default_sec5_2, height=140)

    # Botón para agregar secciones adicionales en Sección 5
    render_boton_agregar_seccion("sec_5", "Sección 5 (Metodología)")

    st.markdown("---")

    # =========================================================================
    # SECCIÓN 6: ESCENARIOS DE ANÁLISIS
    # =========================================================================
    render_control_seccion("sec_6", "Sección 6: Descripción de los Escenarios de Análisis")

    st.markdown("### 6.1 Variables y Escenarios de Análisis")
    render_control_subseccion("subsec_6_1", "Variables y escenarios de análisis (Demanda y Generación)")

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

    # Botón para agregar secciones adicionales en Sección 6
    render_boton_agregar_seccion("sec_6", "Sección 6 (Escenarios de Análisis)")

    datos = {
        "sec4_1_texto": sec4_1_texto,
        "sec4_2_texto": sec4_2_texto,
        "sec4_3_texto": sec4_3_texto,
        "sec4_4_intro": sec4_4_intro,
        "sec4_4_curva": sec4_4_curva,
        "caption_curva_cto": caption_curva_cto,
        "sec4_4_comp": sec4_4_comp,
        "sec5_intro": sec5_intro,
        "sec5_1_texto": sec5_1_texto,
        "sec5_2_texto": sec5_2_texto,
        "sec6_despacho": sec6_despacho,
        "sec6_gen_max": sec6_gen_max
    }
    st.session_state["datos_sec_4_5_6"] = datos
    return datos
