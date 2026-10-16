import streamlit as st
from project_manager import (
    activar_persistencia_automatica,
    exportar_proyecto_esc,
    importar_proyecto_esc,
)
from secciones_manager import obtener_diccionario_secciones

# Activar persistencia automática para todas las pestañas de views/
activar_persistencia_automatica()

from views import (
    tab_formato,
    tab_variables,
    tab_logo,
    tab_cambios,
    tab_supuestos,
    tab_resumen,
    tab_descripcion_equipos,
    tab_entrada_metodologia,
    tab_resultados_electricos,
    tab_protecciones,
    tab_conclusiones_anexos,
    tab_compilacion,
)

st.set_page_config(
    page_title="Generador de Estudios de Conexión - SEYEP S.A.S.",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Generador Automático de Informes Técnicos - SEYEP S.A.S.")
st.markdown("Herramienta modular para estructurar y compilar el **Estudio de Conexión Simplificado** completo en formato LaTeX / PDF.")

# --- Barra Superior para Guardar e Importar Proyecto (.json) ---
contenedor_proy = st.container(border=True)

(
    tab1,
    tab2,
    tab3,
    tab4,
    tab5,
    tab6,
    tab7,
    tab8,
    tab9,
    tab10,
    tab11,
    tab12,
) = st.tabs([
    "1. Formato",
    "2. Variables",
    "3. Logo Cliente",
    "4. Control Cambios",
    "5. Supuestos (1.2)",
    "6. Resumen (1.3)",
    "7. Proyecto y Equipos (2-3)",
    "8. Entrada y Metodología (4-6)",
    "9. Resultados Eléctricos (7)",
    "10. Protecciones (8)",
    "11. Conclusiones y Anexos (9-10)",
    "12. Compilar PDF",
])

with tab1:
    tab_formato.render()

with tab2:
    config_vars = tab_variables.render()

with tab3:
    tab_logo.render()

with tab4:
    df_control_cambios = tab_cambios.render()

with tab5:
    texto_supuesto_activo, usar_tabla_upme, df_supuestos_upme, archivo_or_path = tab_supuestos.render()

with tab6:
    resumen_textos = tab_resumen.render(config_vars)

with tab7:
    datos_sec_2_3 = tab_descripcion_equipos.render(config_vars)

with tab8:
    datos_sec_4_6 = tab_entrada_metodologia.render()

with tab9:
    datos_sec_7 = tab_resultados_electricos.render(config_vars)

with tab10:
    datos_sec_8 = tab_protecciones.render(config_vars)

with tab11:
    datos_sec_9_10 = tab_conclusiones_anexos.render(config_vars)

# Unificar todos los diccionarios de las secciones 2 a 10 y el gestor de secciones en config_vars
dict_secciones = obtener_diccionario_secciones()
if isinstance(config_vars, dict):
    config_vars.update(dict_secciones)
    for d_sec in (datos_sec_2_3, datos_sec_4_6, datos_sec_7, datos_sec_8, datos_sec_9_10):
        if isinstance(d_sec, dict):
            config_vars.update(d_sec)

with tab12:
    tab_compilacion.render(
        config_vars,
        resumen_textos,
        df_control_cambios,
        texto_supuesto_activo,
        usar_tabla_upme,
        df_supuestos_upme,
        archivo_or_path,
    )

# --- Renderizar los botones de Guardar e Importar Proyecto en la barra superior ---
params_totales_esc = {
    **(config_vars if isinstance(config_vars, dict) else {}),
    **(resumen_textos if isinstance(resumen_textos, dict) else {}),
    "df_control_cambios": df_control_cambios,
    "texto_supuesto_activo": texto_supuesto_activo,
    "usar_tabla_upme": usar_tabla_upme,
    "df_supuestos_upme": df_supuestos_upme,
    "archivo_or_path": archivo_or_path,
}
nombre_proy = str(
    params_totales_esc.get("nombreProyecto", params_totales_esc.get("nombre_proyecto", "Proyecto"))
).strip().replace(" ", "_")
bytes_json_esc = exportar_proyecto_esc(params_totales_esc)

with contenedor_proy:
    col_g1, col_g2 = st.columns([1, 1.4])
    with col_g1:
        st.markdown("##### 💾 Guardar Proyecto Actual")
        st.caption("Descarga un archivo `.json` con todas las variables, tablas CSV e imágenes cargadas para retomar o ajustar el estudio más adelante:")
        st.download_button(
            label=f"💾 Guardar Proyecto ({nombre_proy}_ESC.json)",
            data=bytes_json_esc,
            file_name=f"{nombre_proy}_ESC.json",
            mime="application/json",
            use_container_width=True,
            type="primary"
        )
    with col_g2:
        st.markdown("##### 📂 Importar Proyecto Guardado")
        c_imp_file, c_imp_btn = st.columns([2, 1])
        with c_imp_file:
            archivo_proy_esc = st.file_uploader(
                "Selecciona un archivo `.json` de proyecto ESC:",
                type=["json"],
                label_visibility="collapsed",
                key="uploader_proyecto_esc_json"
            )
        with c_imp_btn:
            if st.button("📂 Importar Proyecto", use_container_width=True, disabled=(archivo_proy_esc is None)):
                try:
                    importar_proyecto_esc(archivo_proy_esc)
                    st.success("✅ ¡Proyecto importado! Todos los campos, tablas CSV e imágenes fueron restaurados.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al importar el proyecto: {e}")
