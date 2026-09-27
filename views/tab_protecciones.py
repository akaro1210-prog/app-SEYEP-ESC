import streamlit as st
import pandas as pd

def render():
    st.subheader("🛡️ Sección 8: Verificación de Protecciones")
    st.write("Edita las tablas del Sistema AC (`\\sistemaAC`), las protecciones del proyecto/OR y el resumen de ajustes ANSI.")

    st.markdown("### 8.1 Parámetros del Sistema AC (`\\sistemaAC`)")
    col_ac1, col_ac2, col_ac3 = st.columns(3)
    with col_ac1:
        ac_fases = st.text_input("Sistema AC:", value=r"$3~\phi$")
        ac_tension_kv = st.text_input("Tensión de Línea [kV]:", value="0,48")
    with col_ac2:
        ac_corriente_max = st.text_input("Intensidad máxima [A]:", value="1081")
        ac_factor_carga = st.text_input("Factor de carga continua:", value="1,25")
    with col_ac3:
        ac_proteccion_tablero = st.text_input("Protección en tablero principal [A]:", value="1353*")
        ac_nota_pie = st.text_input("Nota al pie de tabla:", value="*Nota: Valor de protección ajustado a 1360 A.")

    st.markdown("---")
    st.markdown("### 8.2 Tablas de Equipos de Protección")

    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1:
        st.markdown("**Tabla: Protección GD Proyecto**")
        gd_protege = st.text_input("Protege (GD):", value="Transformador 1.25MVA")
        gd_tipo = st.text_input("TIPO (GD):", value="Reconectador")
        gd_ref = st.text_input("REFERENCIA (GD):", value="ENTEC EPR-1 ETR300-R-600")
        gd_tctp = st.text_input("TC / TP (GD):", value="Sensores elecrónicos")
    with c_p2:
        st.markdown("**Tabla: Protección Inversores**")
        inv_protege = st.text_input("Protege (Inversores):", value="TSF - Inversores")
        inv_tipo = st.text_input("TIPO (Inversores):", value="Interruptor")
        inv_ajuste = st.text_input("Ajuste (Inversores):", value="3 X 1360")
    with c_p3:
        st.markdown("**Tabla: Protección del Circuito (OR)**")
        or_protege = st.text_input("Protege (Circuito OR):", value="Circuito completo")
        or_tipo_desc = st.text_input("TIPO (Circuito OR):", value="Se supondrá que es un reconectador")

    st.markdown("---")
    st.markdown("### 8.3 Ajustes de Protección para el Reconectador del Proyecto (`tab:ajustesrecoProyecto`)")
    df_reco_default = pd.DataFrame([
        {"Parámetro": "ANSI 51", "Pick Up [Aprim]": "44", "DIAL [s]": "0,05", "Curva": "IEC - EI"},
        {"Parámetro": "ANSI 50", "Pick Up [Aprim]": "200", "DIAL [s]": "0,0", "Curva": "DT"},
        {"Parámetro": "ANSI 51N", "Pick Up [Aprim]": "16", "DIAL [s]": "0,05", "Curva": "IEC - EI"},
        {"Parámetro": "ANSI 50N", "Pick Up [Aprim]": "1100", "DIAL [s]": "0,00", "Curva": "DT"},
    ])
    df_ajustes_reco_proy = st.data_editor(
        df_reco_default,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_ajustes_reco_proy"
    )

    st.markdown("---")
    st.markdown("### 8.4 Resumen Ajuste de Protecciones Sistemáticas (`tab:resumenajustestotales`)")
    df_sist_default = pd.DataFrame([
        {"Función": "Etapa 1: Baja tensión (ANSI 27)", "Ajustes": "0.6 p.u", "Temporización": "2 s"},
        {"Función": "Etapa 2: Baja tensión (ANSI 27)", "Ajustes": "0.4 p.u", "Temporización": "1.5 s"},
        {"Función": "Etapa 1: Sobretensión (ANSI 59)", "Ajustes": "1.22 p.u", "Temporización": "2.5 s"},
        {"Función": "Etapa 2: Sobretensión (ANSI 59)", "Ajustes": "1.25 p.u", "Temporización": "0.5 s"},
        {"Función": "Sobretensión de neutro (ANSI 59N)", "Ajustes": "0.3 p.u", "Temporización": "2 s"},
        {"Función": "Bajafrecuencia (ANSI 81U)", "Ajustes": "57 Hz", "Temporización": "0.2 s"},
        {"Función": "Sobrefrecuencia (ANSI 81O)", "Ajustes": "63 Hz", "Temporización": "0.2 s"},
        {"Función": "Anti-Isla", "Ajustes": "Lógica combinada de ausencia de tensión y frecuencia", "Temporización": "500 ms"},
        {"Función": "Verificación de sincronismo (ANSI 25)", "Ajustes": "Barra viva OR - Línea Muerta PV a 0.8 p.u de tensión", "Temporización": "NA"},
    ])
    df_ajustes_sistematicos = st.data_editor(
        df_sist_default,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_ajustes_sistematicos"
    )

    datos = {
        "ac_fases": ac_fases,
        "ac_tension_kv": ac_tension_kv,
        "ac_corriente_max": ac_corriente_max,
        "ac_factor_carga": ac_factor_carga,
        "ac_proteccion_tablero": ac_proteccion_tablero,
        "ac_nota_pie": ac_nota_pie,
        "gd_protege": gd_protege,
        "gd_tipo": gd_tipo,
        "gd_ref": gd_ref,
        "gd_tctp": gd_tctp,
        "inv_protege": inv_protege,
        "inv_tipo": inv_tipo,
        "inv_ajuste": inv_ajuste,
        "or_protege": or_protege,
        "or_tipo_desc": or_tipo_desc,
        "df_ajustes_reco_proy": df_ajustes_reco_proy,
        "df_ajustes_sistematicos": df_ajustes_sistematicos
    }
    st.session_state["datos_sec_8"] = datos
    return datos
