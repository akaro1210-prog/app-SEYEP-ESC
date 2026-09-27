import streamlit as st

def render(config_vars):
    st.subheader("📝 Sección 1.3: Resumen de los principales resultados")
    st.write("Personaliza los párrafos de introducción, los puntos técnicos del resumen (`\\resumen`) y el párrafo de cierre. Puedes usar comandos LaTeX como `\\nombreProyecto` y `\\FechaEntrada`.")

    default_intro = (
        r"Para el presente documento se han realizado los siguientes estudios técnicos con el propósito de evaluar la viabilidad del proyecto:"
    )

    # Textos por defecto usando los comandos oficiales de LaTeX
    default_flujo = (
        r"Se realizó un análisis de flujo de carga considerando una fecha de entrada en operación para \FechaEntrada. "
        r"La demanda configurada se estableció en los horarios de 07:00 a 18:00 horas. "
        r"Se constató que la conexión del proyecto en el punto de conexión (en adelante PC) presenta un perfil de tensión "
        r"en las barras de influencia del proyecto acorde a lo establecido por la regulación colombiana. "
        r"En relación con la cargabilidad del sistema de distribución local en el área de operación del proyecto GD \nombreProyecto\ "
        r"se determinó que no presenta sobrecarga en ningún de los elementos, lo que atribuye a la entrada del proyecto."
    )

    default_cortocircuito = (
        r"Se llevó a cabo un análisis de cortocircuito considerando fallas monofásicas y trifásicas, "
        r"basadas en la norma IEC 60909 de 2016. El objetivo fue observar la contribución de corrientes "
        r"de cortocircuito en parques de generación fotovoltaica. Este análisis demostró que no se presentan "
        r"cambios mayores al 10\% con la entrada en operación del GD en ningún punto del circuito."
    )

    default_protecciones = (
        r"Se realizó un estudio de coordinación de protecciones, también considerando fallas monofásicas y trifásicas, "
        r"basado en la norma IEC 60909 de 2016. El objetivo fue garantizar la adecuada operación y coordinación "
        r"de los dispositivos de protección en el sistema eléctrico. Se diseñaron estrategias selectivas y rápidas "
        r"para aislar solo la parte afectada en caso de fallo, minimizando así las zonas desconectadas y asegurando "
        r"la continuidad del servicio eléctrico."
    )

    default_cierre = (
        r"Finalmente, estos estudios proporcionan una sólida base técnica para afirmar la viabilidad del proyecto, asegurando su integración segura y eficiente en la red eléctrica existente."
    )

    # Párrafo introductorio editable
    texto_intro = st.text_area(
        "Párrafo introductorio (antes de \\resumen):",
        value=default_intro,
        height=70
    )

    st.markdown("##### Ítems del comando `\\resumen`")
    # Campos editables en Streamlit para los 3 ítems de \resumen
    texto_flujo = st.text_area("Punto 1: Flujo de Carga", value=default_flujo, height=140)
    texto_cortocircuito = st.text_area("Punto 2: Cortocircuito", value=default_cortocircuito, height=100)
    texto_protecciones = st.text_area("Punto 3: Coordinación de Protecciones", value=default_protecciones, height=100)

    # Párrafo de cierre editable
    texto_cierre = st.text_area(
        "Párrafo de conclusión / cierre (después de \\resumen):",
        value=default_cierre,
        height=70
    )

    # Retornar todos los textos (se desempaquetan automáticamente en tab_compilacion.py)
    return {
        "resumen_intro": texto_intro,
        "resumen_flujo": texto_flujo,
        "resumen_cortocircuito": texto_cortocircuito,
        "resumen_protecciones": texto_protecciones,
        "resumen_cierre": texto_cierre
    }
