import streamlit as st
import os

def guardar_archivo_subido(uploaded_file, nombre_destino):
    """Guarda cualquier imagen subida convirtiéndola a PNG limpio si es necesario."""
    if uploaded_file is not None:
        try:
            from PIL import Image
            img = Image.open(uploaded_file)
            img = img.convert("RGBA") if img.mode in ("RGBA", "P") else img.convert("RGB")
            img.save(nombre_destino, "PNG")
        except Exception:
            with open(nombre_destino, "wb") as f:
                f.write(uploaded_file.getbuffer())
        return True
    return False

def estado_archivo(nombre_archivo):
    return "✅ En carpeta" if os.path.exists(nombre_archivo) else "⚠️ Pendiente"

def render():
    st.subheader("⚡ Sección 7: Resultados de los Análisis Eléctricos")
    st.write("Edita los textos de análisis y sube todas las imágenes de resultados y convenciones de la Sección 7.")

    st.markdown("### 7.1 Flujo de carga AC en estado estable")
    default_cargabilidad_txt = (
        r"Como se puede apreciar en la \cref{tab:Cargabilidad} la cargabilidad en la zona de influencia se encuentra acorde "
        r"lo requerido en la normativa CREG 025 de 1995 con valores aceptable menores del 100\%."
    )
    sec7_cargabilidad_txt = st.text_area("Análisis de Cargabilidad:", value=default_cargabilidad_txt, height=80)

    default_conclusion_perfiles = (
        r"Al presentar los casos de estudio bajo el area de influencia del proyecto asociado a la simulación presentado por el OR "
        r"en la \cref{fig:Unifilar} se analiza que los perfiles de tensión se mantienen dentro de los límites establecidos por la "
        r"resolución CREG 024 del 2005 aplicables en los servicios de distribución de energía eléctrica."
    )
    conclusion_perfiles_carga = st.text_area(
        "Comando \\CONCLUSIONFERFILESCARGA (Conclusión perfiles de tensión):",
        value=default_conclusion_perfiles,
        height=90
    )

    st.markdown("#### Imágenes de Convenciones y Resultados de Flujo de Carga (7.1)")
    col_conv1, col_conv2 = st.columns(2)
    with col_conv1:
        up_conv_flujo = st.file_uploader(
            f"Tabla 10: 'convencionesflujos.png' ({estado_archivo('convencionesflujos.png')})",
            type=["png", "jpg", "jpeg"],
            key="up_conv_flujos"
        )
        if guardar_archivo_subido(up_conv_flujo, "convencionesflujos.png"):
            st.success("✅ convencionesflujos.png guardado.")
    with col_conv2:
        up_cod_col = st.file_uploader(
            f"Figura 7: 'codigocoloresflujo.png' ({estado_archivo('codigocoloresflujo.png')})",
            type=["png", "jpg", "jpeg"],
            key="up_cod_colores"
        )
        if guardar_archivo_subido(up_cod_col, "codigocoloresflujo.png"):
            st.success("✅ codigocoloresflujo.png guardado.")

    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        up_carg = st.file_uploader(
            f"Tabla 11: 'Cargabilidad.png' ({estado_archivo('Cargabilidad.png')})",
            type=["png", "jpg", "jpeg"],
            key="up_carg"
        )
        if guardar_archivo_subido(up_carg, "Cargabilidad.png"):
            st.success("✅ Cargabilidad.png guardado.")
    with c_f2:
        up_tens = st.file_uploader(
            f"Tabla 12: 'TensionesPU.png' ({estado_archivo('TensionesPU.png')})",
            type=["png", "jpg", "jpeg"],
            key="up_tens"
        )
        if guardar_archivo_subido(up_tens, "TensionesPU.png"):
            st.success("✅ TensionesPU.png guardado.")
    with c_f3:
        up_perf = st.file_uploader(
            f"Figura 8: 'perfiltensionCTO.png' ({estado_archivo('perfiltensionCTO.png')})",
            type=["png", "jpg", "jpeg"],
            key="up_perf"
        )
        if guardar_archivo_subido(up_perf, "perfiltensionCTO.png"):
            st.success("✅ perfiltensionCTO.png guardado.")

    st.markdown("---")
    st.markdown("### 7.2 Análisis de contingencia (`\\CONTINGENCIA`)")
    incluir_contingencia = st.checkbox("Incluir subsección de Análisis de Contingencia en el informe", value=True)
    default_contingencia_p1 = (
        r"El análisis de contingencias N-1 demuestra que la integración del proyecto \nombreProyecto\ no compromete la seguridad "
        r"ni la confiabilidad del sistema regional. Ante eventos simples en la red adyacente, los perfiles de tensión se mantienen "
        r"en el rango normativo con un valor máximo de 1,01 p.u., mientras que los tramos de línea operan holgadamente con cargabilidades "
        r"inferiores al 28,7\%. Adicionalmente, la Subestación Doradal absorbe las contingencias de forma estable."
    )
    contingencia_p1 = st.text_area("Párrafo principal de Contingencia N-1:", value=default_contingencia_p1, height=100)

    default_contingencia_p2 = (
        r"Como se evidencia en la \cref{fig:cargabilidadConti} el sistema incrementa su capacidad para soportar contingencias "
        r"sin superar los límites operativos establecidos, mejorando las condiciones de confiabilidad y flexibilidad operativa del circuito."
    )
    contingencia_p2 = st.text_area("Párrafo de cierre de Contingencia:", value=default_contingencia_p2, height=80)

    c_ct1, c_ct2, c_ct3 = st.columns(3)
    with c_ct1:
        up_ccmax = st.file_uploader(
            f"Tabla 13: 'Cont_Cargmax.png' ({estado_archivo('Cont_Cargmax.png')})",
            type=["png", "jpg", "jpeg"],
            key="up_ccmax"
        )
        if guardar_archivo_subido(up_ccmax, "Cont_Cargmax.png"):
            st.success("✅ Cont_Cargmax.png guardado.")
    with c_ct2:
        up_pumax = st.file_uploader(
            f"Tabla 14: 'pumax.png' ({estado_archivo('pumax.png')})",
            type=["png", "jpg", "jpeg"],
            key="up_pumax"
        )
        if guardar_archivo_subido(up_pumax, "pumax.png"):
            st.success("✅ pumax.png guardado.")
    with c_ct3:
        up_diagc = st.file_uploader(
            f"Figura 9: 'Diagrama_Contingencia.png' ({estado_archivo('Diagrama_Contingencia.png')})",
            type=["png", "jpg", "jpeg"],
            key="up_diagc"
        )
        if guardar_archivo_subido(up_diagc, "Diagrama_Contingencia.png"):
            st.success("✅ Diagrama_Contingencia.png guardado.")

    st.markdown("---")
    st.markdown("### 7.3 Cálculo de pérdidas")
    default_perdidas_analisis = (
        r"El análisis técnico de los escenarios proyectados para \YearInicial\ y \YearFinal\, se evidencia que el incremento más significativo "
        r"se presenta en el escenario de Hora 12, alcanzando deltas de 25,97 kW (\YearInicial) y 25,90 kW (\YearFinal); este comportamiento "
        r"responde a la condición técnica donde los Generadores Distribuidos (GD) inyectan su máxima capacidad de energía mientras la demanda "
        r"del circuito es mínima, lo que ocasiona flujos inversos de potencia a través de la red de distribución. Por el contrario, en los escenarios "
        r"con coincidencia entre la generación y la carga, las pérdidas se mantienen en niveles bajos e impactan de manera marginal al sistema "
        r"destacando variaciones de apenas approx 11 kW en el escenario de Hora 9, lo que demuestra que la absorción local de la energía producida "
        r"evita el transporte prolongado de corriente y confirma que la integración de los proyectos no genera un impacto negativo ni degradante sobre la operación habitual del SDL."
    )
    sec7_perdidas_texto = st.text_area("Párrafo de análisis de pérdidas:", value=default_perdidas_analisis, height=140)
    up_perd = st.file_uploader(
        f"Tabla 15: 'perdidas.png' ({estado_archivo('perdidas.png')})",
        type=["png", "jpg", "jpeg"],
        key="up_perd"
    )
    if guardar_archivo_subido(up_perd, "perdidas.png"):
        st.success("✅ perdidas.png guardado.")

    st.markdown("---")
    st.markdown("### 7.4 Cortocircuito y 7.6 Funcionamiento en Isla")
    col_cc1, col_cc2 = st.columns(2)
    with col_cc1:
        up_ley_cortos = st.file_uploader(
            f"Tabla 16: 'Leyendascortos.png' ({estado_archivo('Leyendascortos.png')})",
            type=["png", "jpg", "jpeg"],
            key="up_ley_cortos"
        )
        if guardar_archivo_subido(up_ley_cortos, "Leyendascortos.png"):
            st.success("✅ Leyendascortos.png guardado.")
    with col_cc2:
        up_cortos = st.file_uploader(
            f"Tabla 17: 'cortos.png' ({estado_archivo('cortos.png')})",
            type=["png", "jpg", "jpeg"],
            key="up_cortos"
        )
        if guardar_archivo_subido(up_cortos, "cortos.png"):
            st.success("✅ cortos.png guardado.")

    default_isla_conclusion = (
        r"La Ecuación \eqref{eq:balance_potencia} arroja un resultado donde la potencia instalada acumulada más la capacidad del proyecto "
        r"supera la demanda mínima del circuito, confirmando la existencia de riesgo de funcionamiento en isla no intencional ante contingencias "
        r"o aperturas del elemento de maniobra del Operador de Red. Para mitigar este riesgo y garantizar la seguridad de la red y del personal, "
        r"la planta implementará un esquema de protección anti-isla activo y coordinado conforme a las disposiciones normativas del Acuerdo CNO 2233 de 2026; "
        r"los detalles de la filosofía de operación, la parametrización de las funciones intrínsecas del inversor, las funciones de respaldo y la coordinación "
        r"de tiempos de despeje para evitar la operación en isla se presentan de manera detallada en el Estudio de Ajuste de Protecciones (EACP) entregado adjunto al presente estudio de conexión."
    )
    sec7_isla_conclusion = st.text_area("Conclusión del análisis Anti-Isla (7.6):", value=default_isla_conclusion, height=130)

    datos = {
        "sec7_cargabilidad_txt": sec7_cargabilidad_txt,
        "conclusion_perfiles_carga": conclusion_perfiles_carga,
        "incluir_contingencia": incluir_contingencia,
        "contingencia_p1": contingencia_p1,
        "contingencia_p2": contingencia_p2,
        "sec7_perdidas_texto": sec7_perdidas_texto,
        "sec7_isla_conclusion": sec7_isla_conclusion
    }
    st.session_state["datos_sec_7"] = datos
    return datos