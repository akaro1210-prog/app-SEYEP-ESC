import streamlit as st
from project_manager import exportar_proyecto_json, importar_proyecto_json
from views import (
    tab_variables,
    tab_logo_cambios,
    tab_sistema_cno,
    tab_tension_59n_isla,
    tab_sobrecorriente,
    tab_anexos_eacp,
    tab_compilacion,
)

st.set_page_config(
    page_title="Generador ANEXO EACP - SEYEP S.A.S.",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Generador Automático de Informes: ANEXO EACP (SEYEP S.A.S.)")
st.markdown(
    "Herramienta modular para estructurar y compilar el **Estudio de Ajuste y Coordinación de Protecciones (ANEXO EACP)** "
    "conservando todas las definiciones, referencias cruzadas (`\\cref`) y formato corporativo LaTeX."
)

# --- Barra Superior para Guardar e Importar Proyectos (.json) ---
contenedor_proy = st.container(border=True)

(
    t_vars,
    t_portada,
    t_sist_cno,
    t_tens_isla,
    t_sobrecorr,
    t_anexos,
    t_compilar,
) = st.tabs([
    "1. Variables",
    "2. Portada y Cambios",
    "3. Sistema AC y CNO 2233",
    "4. Tensión (27/59), 59N y Anti-Isla",
    "5. Sobrecorriente (51/50) y Coordinación",
    "6. Anexos (Curvas de Falla)",
    "7. Compilar PDF",
])

with t_vars:
    config_vars = tab_variables.render()

with t_portada:
    df_control_cambios = tab_logo_cambios.render()

with t_sist_cno:
    datos_sistema_cno = tab_sistema_cno.render()

with t_tens_isla:
    datos_tension_59n_isla = tab_tension_59n_isla.render()

with t_sobrecorr:
    datos_sobrecorriente = tab_sobrecorriente.render()

with t_anexos:
    datos_anexos_eacp = tab_anexos_eacp.render()

with t_compilar:
    tab_compilacion.render(
        config_vars=config_vars,
        df_control_cambios=df_control_cambios,
        datos_sistema_cno=datos_sistema_cno,
        datos_tension_59n_isla=datos_tension_59n_isla,
        datos_sobrecorriente=datos_sobrecorriente,
        datos_anexos_eacp=datos_anexos_eacp,
    )

# Reunir todos los parámetros actuales para el botón de Guardar Proyecto
params_proyecto_actual = {}
for bloque in [
    config_vars,
    datos_sistema_cno,
    datos_tension_59n_isla,
    datos_sobrecorriente,
    datos_anexos_eacp,
]:
    if isinstance(bloque, dict):
        params_proyecto_actual.update(bloque)
if df_control_cambios is not None:
    params_proyecto_actual["df_control_cambios"] = df_control_cambios

nombre_proy_limpio = str(params_proyecto_actual.get("nombreProyecto", "Proyecto")).strip().replace(" ", "_")
bytes_proyecto = exportar_proyecto_json(params_proyecto_actual)

with contenedor_proy:
    col_g1, col_g2 = st.columns([1, 1.4])
    with col_g1:
        st.markdown("##### 💾 Guardar Proyecto Actual")
        st.caption("Descarga un archivo `.json` con todas las variables, tablas, equipos del OR e imágenes cargadas para retomar o ajustar el estudio más adelante:")
        st.download_button(
            label=f"💾 Guardar Proyecto ({nombre_proy_limpio}_EACP.json)",
            data=bytes_proyecto,
            file_name=f"{nombre_proy_limpio}_EACP.json",
            mime="application/json",
            use_container_width=True,
            type="primary"
        )
    with col_g2:
        st.markdown("##### 📂 Importar Proyecto Guardado")
        c_imp_file, c_imp_btn = st.columns([2, 1])
        with c_imp_file:
            archivo_proy = st.file_uploader(
                "Selecciona un archivo `.json` de proyecto EACP:",
                type=["json"],
                label_visibility="collapsed",
                key="uploader_proyecto_json"
            )
        with c_imp_btn:
            if st.button("📂 Importar Proyecto", use_container_width=True, disabled=(archivo_proy is None)):
                try:
                    importar_proyecto_json(archivo_proy)
                    st.success("✅ ¡Proyecto importado! Todos los campos, tablas e imágenes fueron restaurados.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al importar el proyecto: {e}")
