import streamlit as st
import pandas as pd
from project_manager import obtener_val, obtener_ver
from cno_normativa import RANGOS_POTENCIA_CNO, obtener_datos_tablas_cno


def render(config_vars=None):
    ver = obtener_ver()
    if config_vars is None:
        config_vars = st.session_state.get("config_vars", {})

    # Detectar el rango de potencia activo y versión CNO
    norma_cno = config_vars.get("normaCNO", st.session_state.get("normaCNO", "2233"))
    clave_rango = config_vars.get("rango_potencia_cno", st.session_state.get("rango_potencia_cno", "P_025_TO_1"))
    datos_normativos = obtener_datos_tablas_cno(clave_rango, version_cno=norma_cno)
    info_rango = datos_normativos["info_rango"]
    es_menor_025 = datos_normativos["es_menor_igual_025"]

    st.subheader(f"⚡ Sección 1 y 1.1: Sistema AC (`\\sistemaAC`) y Protecciones Sistémicas CNO {norma_cno}")
    
    # Banner indicativo del rango normativo en uso
    st.info(
        f"🎯 **Régimen de Capacidad CNO {norma_cno} en uso:** **{info_rango['nombre']}**\n\n"
        f"Se aplican automáticamente los requerimientos de la **{info_rango['tabla_funciones_num']}** "
        f"(Funciones mínimas) y la **{info_rango['tabla_ajustes_num']}** (Ajustes recomendados). "
        f"Puedes cambiar el rango en la **Pestaña 1 (Variables)** si tu proyecto tiene una potencia diferente."
    )

    # =========================================================================
    # 1. COMANDO \sistemaAC (TABLA 1)
    # =========================================================================
    st.markdown("### 1. Comando `\\sistemaAC` (Tabla 1: Sistema AC)")
    plantilla_ac = st.radio(
        "Plantilla rápida de Sistema AC:",
        [
            "Configuración 0,48 kV (Intensidad 1081 A / Protección 1353* A)",
            "Configuración 0,80 kV (Intensidad 775 A / Protección 967,6 A)"
        ],
        index=0,
        horizontal=True,
        key=f"rad_ac_{ver}"
    )

    es_048 = plantilla_ac.startswith("Configuración 0,48")
    c1, c2, c3 = st.columns(3)
    with c1:
        ac_fases = st.text_input("Sistema AC:", value=obtener_val("ac_fases", r"$3~\phi$"), key=f"ac_fases_{ver}")
        ac_etiqueta_pot = st.text_input("Etiqueta fila Potencia:", value=obtener_val("ac_etiqueta_pot", "Potencia" if es_048 else "Potencia [kVA]"), key=f"ac_epot_{ver}")
    with c2:
        ac_tension_kv = st.text_input("Tensión de Línea [kV]:", value=obtener_val("ac_tension_kv", "0,48" if es_048 else "0,8"), key=f"ac_tkv_{ver}")
        ac_corriente_max = st.text_input("Intensidad máxima [A]:", value=obtener_val("ac_corriente_max", "1081" if es_048 else "775"), key=f"ac_imax_{ver}")
    with c3:
        ac_factor_carga = st.text_input(
            "Factor de carga continua (Tabla 1):",
            value=obtener_val("ac_factor_carga", "1,25"),
            key=f"ac_fc_{ver}",
            help="Factor continuo para el dimensionamiento del tablero principal (por defecto 1.25 según RETIE/NTC 2050, editable)."
        )
        ac_proteccion_tablero = st.text_input(
            f"Protección en tablero principal (Imax x {ac_factor_carga}) [A]:",
            value=obtener_val("ac_proteccion_tablero", "1353*" if es_048 else "967,6"),
            key=f"ac_ptab_{ver}",
            help=f"Valor de protección considerando la corriente máxima multiplicada por el factor {ac_factor_carga} (y ajuste comercial si aplica)."
        )

    ac_nota_pie = st.text_input(
        "Nota al pie de la tabla Sistema AC (dejar vacío si no aplica):",
        value=obtener_val("ac_nota_pie", "*Nota: Valor de protección ajustado a 1360 A." if es_048 else ""),
        key=f"ac_nota_{ver}"
    )

    st.markdown("---")
    # =========================================================================
    # 1.1 SUBSECCIÓN: PROTECCIONES SISTÉMICAS CNO 2233
    # =========================================================================
    st.markdown("### 1.1 Subsección: *Protecciones sistémicas a implementar en el proyecto*")

    if es_menor_025:
        intro_cno_default = (
            "Todo sistema de generación basados en inversores y frecuencia variable de capacidad instalada o nominal "
            "menor o igual a 0.25 MW (≤ 0.25 MW) conectado a los niveles 1, 2 y 3 deberá disponer de funciones de protección "
            f"disponibles a nivel de inversor conforme a la Tabla 6 del Acuerdo CNO {norma_cno}, coordinando oportunamente con la red del OR."
        )
    else:
        intro_cno_default = (
            "Todo sistema de generación basados en inversores y frecuencia variable conectado a los niveles 1, 2 y 3 "
            "deberán disponer de un esquema de protección para proteger la instalación del generador y su punto de conexión "
            f"con el sistema de distribución local, los cuales deberán ser selectivos y coordinar con la red existente, según el acuerdo CNO {norma_cno}."
        )

    intro_cno_txt = st.text_area(
        "Párrafo introductorio 1.1:",
        value=obtener_val("intro_cno_txt", intro_cno_default),
        height=80,
        key=f"int_cno_{ver}"
    )

    # -------------------------------------------------------------------------
    # TABLA 2 (Tabla 6 o 7 según el rango)
    # -------------------------------------------------------------------------
    col_t2_head, col_t2_btn = st.columns([3.5, 1.2])
    with col_t2_head:
        st.markdown(f"#### Tabla 2: Funciones de protección mínimas — **{info_rango['tabla_funciones_num']} CNO {norma_cno}** (`tab:funciones_proteccion`)")
    with col_t2_btn:
        if st.button("🔄 Restaurar Tabla CNO", key=f"btn_res_func_{ver}", help=f"Restablece los valores estándar del CNO {norma_cno} para este rango"):
            st.session_state["df_funciones_prot"] = pd.DataFrame(datos_normativos["df_funciones_prot"])
            st.session_state["tabla_funciones_caption"] = datos_normativos["tabla_funciones_caption"]
            st.rerun()

    caption_func_cno = st.text_input(
        "Título de la Tabla 2 en LaTeX (\\captionof{table}):",
        value=st.session_state.get("tabla_funciones_caption", datos_normativos["tabla_funciones_caption"]),
        key=f"cap_func_cno_input_{ver}_{clave_rango}",
        help="Título formal que aparecerá en el encabezado de la Tabla 2 y en el Índice de Tablas del informe."
    )
    st.session_state["tabla_funciones_caption"] = caption_func_cno

    # Obtener el DataFrame de sesión o cargar el por defecto del rango
    df_func_actual = st.session_state.get("df_funciones_prot")
    if df_func_actual is None or not isinstance(df_func_actual, pd.DataFrame):
        df_func_actual = pd.DataFrame(datos_normativos["df_funciones_prot"])

    df_funciones_prot = st.data_editor(
        df_func_actual,
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_func_prot_eacp_{ver}_{clave_rango}"
    )
    st.session_state["df_funciones_prot"] = df_funciones_prot

    # -------------------------------------------------------------------------
    # OBSERVACIONES CONFORME A LAS NOTAS DEL ACUERDO CNO
    # -------------------------------------------------------------------------
    st.markdown("#### Observaciones conforme a las notas del acuerdo CNO")
    c_obs1, c_obs2 = st.columns(2)
    with c_obs1:
        obs_cno_1 = st.text_area(
            "Viñeta 1 (Función ANSI 32 / Excedentes - Nota k):",
            value=obtener_val("obs_cno_1", datos_normativos["obs_cno_1"]),
            height=85,
            key=f"obs1_{ver}"
        )
    with c_obs2:
        obs_cno_2 = st.text_area(
            "Viñeta 2 (Verificación de Sincronismo - Nota r):",
            value=obtener_val("obs_cno_2", datos_normativos["obs_cno_2"]),
            height=85,
            key=f"obs2_{ver}"
        )

    # -------------------------------------------------------------------------
    # TABLA 3 (Tabla 11 o 12 según el rango)
    # -------------------------------------------------------------------------
    st.markdown("---")
    col_t3_head, col_t3_btn = st.columns([3.5, 1.2])
    with col_t3_head:
        st.markdown(f"#### Tabla 3: Ajuste de protecciones recomendados — **{info_rango['tabla_ajustes_num']} CNO {norma_cno}** (`tab:AjustesproteccionCNO`)")
    with col_t3_btn:
        if st.button("🔄 Restaurar Ajustes CNO", key=f"btn_res_ajust_{ver}", help=f"Restablece los ajustes recomendados del CNO {norma_cno} para este rango"):
            st.session_state["df_ajustes_cno"] = pd.DataFrame(datos_normativos["df_ajustes_cno"])
            st.session_state["tabla_ajustes_caption"] = datos_normativos["tabla_ajustes_caption"]
            st.rerun()

    caption_ajustes_cno = st.text_input(
        "Título de la Tabla 3 en LaTeX (\\captionof{table}):",
        value=st.session_state.get("tabla_ajustes_caption", datos_normativos["tabla_ajustes_caption"]),
        key=f"cap_ajustes_cno_input_{ver}_{clave_rango}",
        help="Título formal que aparecerá en el encabezado de la Tabla 3 y en el Índice de Tablas del informe."
    )
    st.session_state["tabla_ajustes_caption"] = caption_ajustes_cno

    df_ajustes_actual = st.session_state.get("df_ajustes_cno")
    if df_ajustes_actual is None or not isinstance(df_ajustes_actual, pd.DataFrame):
        df_ajustes_actual = pd.DataFrame(datos_normativos["df_ajustes_cno"])

    df_ajustes_cno = st.data_editor(
        df_ajustes_actual,
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_ajustes_cno_eacp_{ver}_{clave_rango}"
    )
    st.session_state["df_ajustes_cno"] = df_ajustes_cno

    # Cuadro resumen con lineamientos complementarios de corte, anti-isla y registros
    with st.expander(f"📌 Ver Requisitos Complementarios CNO {norma_cno} para este Rango de Potencia", expanded=True):
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.markdown("**🔌 Equipo de Interrupción o Corte:**")
            st.write(info_rango["equipo_corte"])
        with col_r2:
            st.markdown("**🏝️ Esquema de Protección Anti-Isla:**")
            st.write(info_rango["anti_isla_respaldo"])
        with col_r3:
            st.markdown("**📈 Registros Cronológicos (SOE / COMTRADE):**")
            st.write(info_rango["soe_comtrade"])

    datos = {
        "ac_fases": ac_fases,
        "ac_etiqueta_pot": ac_etiqueta_pot,
        "ac_tension_kv": ac_tension_kv,
        "ac_corriente_max": ac_corriente_max,
        "ac_factor_carga": ac_factor_carga,
        "ac_proteccion_tablero": ac_proteccion_tablero,
        "ac_nota_pie": ac_nota_pie,
        "intro_cno_txt": intro_cno_txt,
        "df_funciones_prot": df_funciones_prot,
        "obs_cno_1": obs_cno_1,
        "obs_cno_2": obs_cno_2,
        "df_ajustes_cno": df_ajustes_cno,
        "rango_potencia_cno": clave_rango,
        "tabla_funciones_num": info_rango["tabla_funciones_num"],
        "tabla_ajustes_num": info_rango["tabla_ajustes_num"],
        "tabla_funciones_caption": caption_func_cno,
        "tabla_ajustes_caption": caption_ajustes_cno,
    }
    st.session_state["datos_sistema_cno"] = datos
    return datos
