import streamlit as st
from secciones_manager import render_control_seccion, render_control_subseccion, render_boton_agregar_seccion

def render(config_vars=None):
    if config_vars is None:
        config_vars = st.session_state.get("config_vars", {})
    tipo_estudio = config_vars.get("tipo_estudio", st.session_state.get("tipo_estudio", "GD"))
    es_autogen = ("autogenerador" in str(tipo_estudio).lower() or bool(config_vars.get("es_autogenerador", False)))
    tag = "Autogenerador" if es_autogen else "GD"

    st.subheader(f"📝 Sección 1: Resumen Ejecutivo y Resultados ({tag})")
    
    # Control de Sección Opcional
    render_control_seccion("sec_1", f"Sección 1: Resumen Ejecutivo y Supuestos ({tag})")

    # Controles de Subsecciones Opcionales para Sección 1
    render_control_subseccion("subsec_1_1", f"Subsección 1.1: Objetivo y alcance ({tag})")
    render_control_subseccion("subsec_1_3", "Subsección 1.3: Resumen de los principales resultados (\\resumen)")
    st.write(
        f"Personaliza los párrafos de introducción, los puntos técnicos del resumen (`\\resumen`) y el párrafo de cierre "
        f"para el régimen de **{tag}**. Puedes usar comandos LaTeX como `\\nombreProyecto` y `\\FechaEntrada`."
    )

    default_intro = (
        r"Para el presente documento se han realizado los siguientes estudios técnicos con el propósito de evaluar la viabilidad del proyecto:"
    )

    # Textos por defecto adaptados dinámicamente a GD o Autogenerador
    default_flujo = (
        r"Se realizó un análisis de flujo de carga considerando una fecha de entrada en operación para \FechaEntrada. "
        r"La demanda configurada se estableció en los horarios de 07:00 a 18:00 horas. "
        r"Se constató que la conexión del proyecto en el punto de conexión (en adelante PC) presenta un perfil de tensión "
        r"en las barras de influencia del proyecto acorde a lo establecido por la regulación colombiana. "
        rf"En relación con la cargabilidad del sistema de distribución local en el área de operación del proyecto {tag} \nombreProyecto\ "
        r"se determinó que no presenta sobrecarga en ningún de los elementos, lo que atribuye a la entrada del proyecto."
    )

    default_cortocircuito = (
        r"Se llevó a cabo un análisis de cortocircuito considerando fallas monofásicas y trifásicas, "
        r"basadas en la norma IEC 60909 de 2016. El objetivo fue observar la contribución de corrientes "
        r"de cortocircuito en parques de generación fotovoltaica. Este análisis demostró que no se presentan "
        rf"cambios mayores al 10\% con la entrada en operación del {tag} en ningún punto del circuito."
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

    # Botón para agregar nuevas secciones o subsecciones
    render_boton_agregar_seccion("sec_1", "Sección 1 (Resumen Ejecutivo)")

    # Retornar todos los textos (se desempaquetan automáticamente en tab_compilacion.py)
    return {
        "resumen_intro": texto_intro,
        "resumen_flujo": texto_flujo,
        "resumen_cortocircuito": texto_cortocircuito,
        "resumen_protecciones": texto_protecciones,
        "resumen_cierre": texto_cierre
    }
