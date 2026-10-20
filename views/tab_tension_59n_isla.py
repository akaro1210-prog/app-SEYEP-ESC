import streamlit as st
import pandas as pd
import os
from project_manager import obtener_val, obtener_df, obtener_ver

def guardar_archivo_subido(uploaded_file, nombre_destino):
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
    return "✅ Cargada" if os.path.exists(nombre_archivo) else "⚠️ Pendiente"

def render():
    ver = obtener_ver()
    st.subheader("🔌 Secciones 1.2, 1.3 y 1.4: Tensión (27/59), Sobretensión Residual (59N) y Anti-Isla")

    # ================= 1.2 PROTECCIONES 27 Y 59 =================
    st.markdown("### 1.2 Cálculos para las protecciones 27 y 59 (`\\protecciontensiones`)")
    modo_27_59 = st.radio(
        "Selecciona la plantilla para `\\protecciontensiones`:",
        [
            "Plantilla EPM / CEO (2 segundos para etapa 1 y 1.5 segundos para etapa 2)",
            "Plantilla EBSA (3 segundos para etapa 1 y 1.5 segundos para etapa 2)"
        ],
        index=0,
        key=f"rad_2759_{ver}"
    )

    if modo_27_59.startswith("Plantilla EPM"):
        txt_27_59_default = (
            r"Dado que en el CNO no se indican los valores de tiempo para las protecciones etapa 1 y 2 de la protección 27, "
            r"y que estos valores deben ser acordados con el operador de red, se propondrán los siguientes valores que garantizan "
            r"estar por fuera de las curvas HVRT y LVRT del acuerdo CON 1833 del 2024, Los valores propuestos son 2 segundos para la "
            r"etapa 1 y 1.5 segundos para la etapa dos. En la \cref{fig:proteccion27-59}. se verifica que estos tiempos no intervienen "
            r"con la correcta actuación de las curvas LVRT y HVRT de los inversores. Estos valores están sujetos a aceptación del OR o "
            r"en su defecto se pondrán los que el OR sugiera en caso de que intervengan con alguna función de sobretensión implementada en sus redes de distribución."
        )
    else:
        txt_27_59_default = (
            r"Dado que en el CNO no se indican los valores de tiempo para las protecciones etapa 1 y 2 de la protección 27, "
            r"y que estos valores deben ser acordados con el operador de red, se propondrán los siguientes valores que garantizan "
            r"estar por fuera de las curvas HVRT y LVRT del acuerdo CON 1833 del 2024, Los valores propuestos son 3 segundos para la "
            r"etapa 1 y 1.5 segundos para la etapa dos. En la \cref{fig:proteccion27-59} se verifica el cumplimiento de las protecciones 27 y 59. "
            r"Estos valores están sujetos a aceptación del OR o en su defecto se pondrán los que el OR sugiera en caso de que intervengan "
            r"con alguna función de sobretensión implementada en sus redes de distribución."
        )

    proteccion_tensiones_txt = st.text_area(
        "Texto de `\\protecciontensiones` (conserva `\\cref{fig:proteccion27-59}`):",
        value=obtener_val("proteccion_tensiones_txt", txt_27_59_default),
        height=120,
        key=f"txt_2759_{ver}"
    )

    incluir_img_2759 = st.checkbox(
        "✅ Incluir figura 'Proteccion27-59.png' (Verificación ajustes ANSI 27/59 con curvas HVRT y LVRT)",
        value=bool(obtener_val("incluir_img_2759", True)),
        key=f"chk_img_2759_{ver}"
    )

    if incluir_img_2759:
        up_2759 = st.file_uploader(
            f"Figura: 'Proteccion27-59.png' ({estado_archivo('Proteccion27-59.png')})",
            type=["png", "jpg", "jpeg"],
            key=f"up_prot_2759_{ver}"
        )
        if guardar_archivo_subido(up_2759, "Proteccion27-59.png"):
            st.success("✅ Proteccion27-59.png guardada.")
    else:
        st.caption("ℹ️ La figura 'Proteccion27-59.png' no se incluirá en el informe PDF.")

    # ================= 1.3 PROTECCIÓN 59N =================
    st.markdown("---")
    st.markdown("### 1.3 Cálculos para la protección 59N (`\\tablatresVcero`)")
    
    incluir_sec_59n = st.checkbox(
        "✅ Incluir sección 1.3: Cálculos para la protección 59N en el informe",
        value=bool(obtener_val("incluir_sec_59n", True)),
        key=f"chk_sec_59n_{ver}"
    )

    df_3v0_default = pd.DataFrame([
        {"Impedancia de falla [ohms]": "0", "3V0 [kV]": "10.746", "3V0 [p.u]": "1.410"},
        {"Impedancia de falla [ohms]": "5", "3V0 [kV]": "5.603", "3V0 [p.u]": "0.735"},
        {"Impedancia de falla [ohms]": "15", "3V0 [kV]": "2.842", "3V0 [p.u]": "0.373"},
    ])

    texto_59n_default = (
        r"El ajuste de la función de protección contra sobretensión residual (59N) se fundamenta en un análisis técnico que evalúa "
        r"el desplazamiento del neutro bajo escenarios críticos de falla, equilibrando la sensibilidad requerida para detectar contingencias "
        r"de alta impedancia con la seguridad operativa ante desequilibrios normales del sistema. Las simulaciones de cortocircuito monofásico "
        r"a tierra en el nivel de \NT , donde la tensión base fase-neutro es de aproximadamente 7.621 kV, arrojan un comportamiento "
        r"decreciente de la tensión residual a medida que aumenta la resistencia de contacto. En el escenario más desfavorable, correspondiente "
        r"a una falla de alta impedancia de 15 ohms, el sistema experimenta un desplazamiento de neutro que eleva la tensión residual a "
        r"\tresVceroMASALTA, lo que equivale a \tresVceroMASALTAkV\ primarios. Por otra parte, la definición del umbral de arranque está "
        r"condicionada por las asimetrías inherentes a la red de distribución, tales como desbalances permanentes por carga monofásica, y por "
        r"las tolerancias y errores de precisión intrínsecos de la cadena de medición, incluyendo tanto a los transformadores de tensión como a "
        r"las unidades de control de los reconectadores comerciales, cuyas bandas de precisión típicas rondan el 5\%. Con base en est información "
        r"y en las simnulaciones realizadas, el valor de ajuste para el umbral de la protección debería ser \ajustetresVcero, equivalente a "
        r"\magajustetresVcero\ primarios. Este valor garantiza la máxima estabilidad y seguridad de la función, ya que inmuniza al control del "
        r"reconectador frente a errores de medición y desbalances transitorios o estacionarios, evitando disparos espurios en condiciones normales "
        r"de operación. Asimismo, la temporización de esta función se fija en 2.0 segundos bajo la curva de tiempo definido. Debido a que la "
        r"tensión residual es una variable global que carece de selectividad direccional intrínseca en configuraciones radiales o de acoplamiento "
        r"simple, la función de sobretensión residual debe actuar estrictamente como un respaldo de última línea. Un retardo de 2.0 segundos asegura "
        r"la selectividad cronométrica necesaria para que otras protecciones de cabecera del circuito o dispositivos fusibles ubicados aguas abajo "
        r"del Operador de Red despejen de forma prioritaria cualquier falla transitoria o local en el sistema de distribución. De este modo, se mitiga "
        r"el riesgo de salidas intempestivas del reconectador principal, priorizando la continuidad del servicio y resguardando la disponibilidad y "
        r"evacuación de la planta de \capacidadMW\ sin sacrificar la protección efectiva del sistema ante desplazamientos críticos del neutro."
        "\n\\\\\n"
        r"Dado lo anterior, los ajustes de la función 59N es \ajustetresVcero\ de arranque con tiempo definido de 2 segundos."
    )

    if not incluir_sec_59n:
        st.info("🚫 La sección 1.3 (Cálculos para la protección 59N) está desactivada y se omitirá del documento PDF y de la tabla de contenido.")
        df_tres_vcero = obtener_df("df_tres_vcero", df_3v0_default)
        tres_vcero_mas_alta = obtener_val("tresVceroMASALTA", "0.373 p.u.")
        tres_vcero_mas_alta_kv = obtener_val("tresVceroMASALTAkV", "2.842 kV")
        ajuste_tres_vcero = obtener_val("ajustetresVcero", "0.2 p.u")
        mag_ajuste_tres_vcero = obtener_val("magajustetresVcero", "1.524 kV")
        tension_base_fn = obtener_val("tension_base_fn", "7.621 kV")
        texto_59n = obtener_val("texto_59n", texto_59n_default)
    else:
        st.caption("Edita los valores de la tabla de tensión residual 3V0 y las variables enlazadas en el párrafo de análisis:")

        df_tres_vcero = st.data_editor(
            obtener_df("df_tres_vcero", df_3v0_default),
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_3v0_eacp_{ver}"
        )

        c_v1, c_v2, c_v3, c_v4, c_v5 = st.columns(5)
        with c_v1:
            tres_vcero_mas_alta = st.text_input("\\tresVceroMASALTA (15 ohms p.u.):", value=obtener_val("tresVceroMASALTA", "0.373 p.u."), key=f"v_3v0a_{ver}")
        with c_v2:
            tres_vcero_mas_alta_kv = st.text_input("\\tresVceroMASALTAkV (15 ohms kV):", value=obtener_val("tresVceroMASALTAkV", "2.842 kV"), key=f"v_3v0kv_{ver}")
        with c_v3:
            ajuste_tres_vcero = st.text_input("\\ajustetresVcero (Umbral p.u.):", value=obtener_val("ajustetresVcero", "0.2 p.u"), key=f"v_aj3v0_{ver}")
        with c_v4:
            mag_ajuste_tres_vcero = st.text_input("\\magajustetresVcero (Umbral kV):", value=obtener_val("magajustetresVcero", "1.524 kV"), key=f"v_mag3v0_{ver}")
        with c_v5:
            tension_base_fn = st.text_input("Tensión base fase-neutro:", value=obtener_val("tension_base_fn", "7.621 kV"), key=f"v_tbfn_{ver}")

        texto_59n = st.text_area(
            "Párrafo de análisis de 59N (conserva `\\NT`, `\\tresVceroMASALTA`, `\\ajustetresVcero`, etc.):",
            value=obtener_val("texto_59n", texto_59n_default),
            height=200,
            key=f"txt_59n_{ver}"
        )

    # ================= 1.4 PROTECCIÓN ANTI-ISLA =================
    st.markdown("---")
    st.markdown("### 1.4 Cálculos para la protección Anti-isla")
    modo_anti_isla = st.radio(
        "Selecciona el controlador / filosofía para la subsección Anti-Isla:",
        [
            "Opción 1: Control ENTEC ETR300-R-600 (Compuerta ULB = (27BD) AND ((81U2AL) OR (81O2AL)))",
            "Opción 2: Control NOJA Power RC10/RC15 (Compuerta [A(UV13)] OR [A(UF2)] OR [A(OF2)])"
        ],
        index=0,
        key=f"rad_isla_{ver}"
    )

    norma_cno_val = st.session_state.get("config_vars", {}).get("normaCNO", st.session_state.get("normaCNO", "2233"))
    if modo_anti_isla.startswith("Opción 1"):
        anti_isla_default = (
            rf"En estricto cumplimiento de las directrices del Acuerdo CNO {norma_cno_val} para instalaciones de Generación Distribuida y considerando "
            r"las restricciones normativas asociadas a la aplicación aislada de las funciones de Tasa de Cambio de Frecuencia (ANSI 81R, limitada "
            r"regulatoriamente a 5.0 Hz/s durante 500 ms según la Nota 28) y Salto de Vector (ANSI 78), se diseña e implementa un Esquema Anti-Isla "
            r"de Lógica Compuesta Pasiva por Supervisión Cruzada de Tensión y Frecuencia en el control ENTEC ETR300-R-600 mediante el software ETIMS. "
            r"El esquema tiene como objetivo primario desenganchar la frontera en un tiempo rápido (t = 500 ms) ante la apertura de la cabecera o "
            r"reconectador del alimentador de \OR, previniendo la operación en isla no intencional y suprimiendo el riesgo de acoplamiento fuera de "
            r"fase durante los ciclos de reenganche automático de la red de distribución."
            "\n\\\\\n"
            r"Para no interferir con las protecciones de subtensión sistémicas del punto de conexión (ANSI 27-1 ajustada en 0.60 p.u. y ANSI 27-2 "
            r"ajustada en 0.40 p.u.), la función de detección de presencia/ausencia de tensión en la fuente (LIVE LINE / 27BD) se parametriza de forma "
            r"subordinada y jerárquica por debajo de la protección de respaldo, parametrizando en los ajustes generales del reconectador un nivel de "
            r"Live Line Lv en 0.30 p.u. y de esta forma garantiza que la bandera de estado de Línea Muerta (27BD) solo se declare tras el colapso "
            r"efectivo de la tensión de la red de \OR\ por debajo de este umbral, preservando la selectividad de los escalones 27-1 y 27-2 ante "
            r"profundizaciones o huecos de tensión ordinarios (voltage sags). y el tiempo de detección de línea muerta Live Line TD se ajustará en "
            r"0.50 s para permitir una declaración veloz de la condición 27BD sin introducir demoras críticas que comprometan la ventana de reenganche de \OR."
            "\n\\\\\n"
            r"Aprovechando que el reconectador ENTEC trae varios escalones para las funciones de freciencia, se implementarán los segundos escalores "
            r"de 81U y 81O en mnodo alarma con umbrales próximos a la frecuencia nominal para que actúen como detectores de la derivada de frecuencia "
            r"en la insla local antes de alcanzar los límites de las protecciones sistémicas, en 59.3Hz para 81U-2 y en 60.7Hz para 81O-2 ambas con un tiempo de alarma de 300ms."
            "\n\\\\\n"
            r"Dados estos umbrales, en la lógica programable del reconectador se programará una compuerta lógica (ULB) con la siguiente actuación booleana:\\"
            "\n\\\\\n"
            r"\textbf{Compuerta lógica para la protección anti isla.}\\"
            "\n"
            r"\[ ULB = (27BD) \quad AND \quad ((81U2AL) \quad OR \quad (81O2AL)) \]"
            "\n\\\\\n"
            r"El criterio operativo del esquema se fundamenta en la inmunidad ante transitorios y la velocidad de respuesta, de modo que si la red de "
            r"\OR\ experimenta un hueco de tensión pero el alimentador permanece conectado, la frecuencia se mantendrá gobernada por la inercia del "
            r"Sistema Interconectado Nacional (60.0 Hz), evitando la activación de las funciones 81U2/81O2 para que la compuerta AND prevenga disparos "
            r"falsos en el PC; asimismo, si la frecuencia del sistema oscila pero la tensión de la red de \OR\ se mantiene por encima de 0.30 p.u. la "
            r"señal 27BD permanecerá en cero, bloqueando cualquier orden intempestiva de desenganche. Por el contrario, ante una desconexión efectiva "
            r"del alimentador de \OR, la tensión colapsa (V < 0.30 p.u.) activando la condición 27BD a los 500 ms, mientras que la inmediata deriva de "
            r"frecuencia de la isla activa la alarma 81U2/81O2 a los 300 ms, lo que permite a la lógica ULB ordenar la apertura completa en un tiempo "
            r"total estimado de 500 ms a 550 ms (gobernado por la confirmación de la línea muerta). Esta velocidad de actuación garantiza que la planta "
            r"de \capacidadMW\ se desenganche de la red de manera oportuna y holgada antes del primer intento del ciclo de reenganche automático del "
            r"circuito de \OR\ , el cual, según los insumos brindados por el Operador de Red, cuenta con un esquema de recierre 1+1 con un tiempo muerto "
            r"de 15 segundos, suprimiendo formalmente cualquier riesgo de reconexión en fuera de fase. Finalmente, la señal lógica resultante ULB se "
            r"mapea directamente en la matriz de disparo principal (ETRBK = GLLOCK + DIGIGBT + DIGTRC + ULB07), ejecutando la apertura inmediata del "
            r"reconectador ENTEC, quedando la planta aislada y habilitada únicamente la reconexión manual en el control."
        )
    else:
        anti_isla_default = (
            rf"Para dar estricto cumplimiento a lo establecido en la Tabla 8 del Acuerdo CNO {norma_cno_val} sobre la implementación de funciones anti-isla "
            r"mediante Lógica Compuesta, se propone programar un automatismo en el motor de eventos (Logic Engine / ECA) del controlador NOJA Power "
            r"RC10/RC15 que procesa las banderas de alarma internas mediante la ecuación booleana [A(UV13)] OR [A(UF2)] OR [A(OF2)] asociada a una "
            r"orden de disparo trifásico con bloqueo (Trip \& Lockout) y un tiempo de sostenimiento de 500 ms. La señal de bajo voltaje A(UV13) "
            r"corresponde a la tercera etapa de la función de baja tensión fase-neutro (ANSI 27-3) ajustada a un umbral de (0,20 p.u.), la cual actúa "
            r"como alarma de entrada para capturar la caída sostenida del potencial en el lado fuente cuando abre la cabecera del alimentador del "
            r"Operador de Red (OR). Por su parte, las señales A(UF2) y A(OF2) corresponden a las etapas de alarma de baja frecuencia (56,50 Hz) y "
            r"sobre-frecuencia (63,50 Hz) respectivamente; la selección de estos umbrales otorga una banda de seguridad por fuera de las exigencias "
            r"sistémicas de soporte de red (Ride-Through entre 57,00 Hz y 63,00 Hz), garantizando la inmunidad del parque solar ante oscilaciones del "
            r"SIN y asegurando la detección efectiva de la deriva de frecuencia en la isla ante discrepancias de potencia ($P_{\text{carga}} \neq P_{\text{gen}}$). "
            r"Finalmente, el tiempo de reconocimiento de 500 ms asignado a la salida de la compuerta OR otorga un margen de seguridad de 1,5 s respecto "
            r"a la primera tentativa de reenganche del alimentador del OR (estandarizada típicamente en 2,0 s), previniendo cierres en oposición de fase "
            r"y garantizando la estabilidad del esquema ante transitorios de muy corta duración."
        )

    texto_anti_isla = st.text_area(
        "Texto de la subsección 1.4 Anti-Isla:",
        value=obtener_val("texto_anti_isla", anti_isla_default),
        height=240,
        key=f"txt_isla_{ver}"
    )

    datos = {
        "incluir_img_2759": incluir_img_2759,
        "incluir_sec_59n": incluir_sec_59n,
        "proteccion_tensiones_txt": proteccion_tensiones_txt,
        "df_tres_vcero": df_tres_vcero,
        "tresVceroMASALTA": tres_vcero_mas_alta,
        "tresVceroMASALTAkV": tres_vcero_mas_alta_kv,
        "ajustetresVcero": ajuste_tres_vcero,
        "magajustetresVcero": mag_ajuste_tres_vcero,
        "tension_base_fn": tension_base_fn,
        "texto_59n": texto_59n,
        "texto_anti_isla": texto_anti_isla,
    }
    st.session_state["datos_tension_59n_isla"] = datos
    return datos
