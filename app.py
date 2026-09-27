import streamlit as st

# Importar todas las vistas modulares (existentes + 5 pestañas nuevas de secciones 2 a 10)
from views import (
    tab_formato,
    tab_variables,
    tab_resumen,
    tab_cambios,
    tab_supuestos,
    tab_descripcion_equipos,
    tab_entrada_metodologia,
    tab_resultados_electricos,
    tab_protecciones,
    tab_conclusiones_anexos,
    tab_logo,
    tab_compilacion
)

st.set_page_config(
    page_title="Generador de Informes SEYEP",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Generador de Informes de Conexión — SEYEP S.A.S.")
st.write("Control centralizado de comandos LaTeX, recursos estéticos, tablas y secciones completas del estudio de conexión.")

# Definir todas las pestañas en orden lógico del documento
(
    t_formato,
    t_vars,
    t_cambios,
    t_supuestos,
    t_resumen,
    t_desc_eq,
    t_ent_met,
    t_res_elec,
    t_prot,
    t_conc_anex,
    t_logo,
    t_compilacion
) = st.tabs([
    "🎨 Formato y Estética",
    "📋 Variables",
    "🔄 Control de Cambios",
    "📈 1.2 Supuestos",
    "📝 1.3 Resumen Resultados",
    "🏗️ 2-3. Proyecto y Equipos",
    "📊 4-6. Entradas y Metodología",
    "⚡ 7. Resultados Eléctricos",
    "🛡️ 8. Protecciones",
    "📌 9-10. Conclusiones y Anexos",
    "🖼️ Logotipo Cliente",
    "🚀 Compilación"
])

with t_formato:
    recursos_listos = tab_formato.render()

with t_vars:
    config_vars = tab_variables.render()

with t_cambios:
    df_control_cambios = tab_cambios.render()

with t_supuestos:
    texto_supuesto_activo, usar_tabla_upme, df_supuestos_upme, archivo_or_path = tab_supuestos.render()

with t_resumen:
    resumen_textos = tab_resumen.render(config_vars)

with t_desc_eq:
    datos_sec_2_3 = tab_descripcion_equipos.render()

with t_ent_met:
    datos_sec_4_5_6 = tab_entrada_metodologia.render()

with t_res_elec:
    datos_sec_7 = tab_resultados_electricos.render()

with t_prot:
    datos_sec_8 = tab_protecciones.render()

with t_conc_anex:
    datos_sec_9_10 = tab_conclusiones_anexos.render(config_vars)

with t_logo:
    logo_cliente_path = tab_logo.render()

# Unificar los diccionarios de las secciones editables dentro de resumen_textos
# para que tab_compilacion.py los desempaquete automáticamente en params_finales
resumen_textos_completo = {
    **(resumen_textos or {}),
    **(datos_sec_2_3 or {}),
    **(datos_sec_4_5_6 or {}),
    **(datos_sec_7 or {}),
    **(datos_sec_8 or {}),
    **(datos_sec_9_10 or {})
}

with t_compilacion:
    tab_compilacion.render(
        config_vars=config_vars,
        resumen_textos=resumen_textos_completo,
        df_control_cambios=df_control_cambios,
        texto_supuesto_activo=texto_supuesto_activo,
        usar_tabla_upme=usar_tabla_upme,
        df_supuestos_upme=df_supuestos_upme,
        archivo_or_path=archivo_or_path
    )
