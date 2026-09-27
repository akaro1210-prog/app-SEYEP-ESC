import streamlit as st
import os

def render(config_vars, resumen_textos, df_control_cambios, texto_supuesto_activo, usar_tabla_upme, df_supuestos_upme, archivo_or_path):
    st.subheader("🚀 Compilación del Estudio en LaTeX")
    st.write("Panel de control para ensamblar y compilar el documento PDF final utilizando todos los datos configurados en las pestañas anteriores.")

    if st.button("Compilar Informe PDF", type="primary"):
        with st.spinner("Compilando documento LaTeX..."):
            from latex_builder import compilar_estudio_latex
            
            params_finales = {
                **(config_vars or {}),
                **(resumen_textos or {}),
                "df_control_cambios": df_control_cambios,
                "texto_supuesto_activo": texto_supuesto_activo,
                "usar_tabla_upme": usar_tabla_upme,
                "df_supuestos_upme": df_supuestos_upme,
                "archivo_or_path": archivo_or_path
            }
            
            exito, resultado = compilar_estudio_latex(params_finales)
            
            if exito:
                st.success("¡Informe compilado con éxito!")
                try:
                    if resultado and os.path.exists(resultado):
                        with open(resultado, "rb") as f:
                            pdf_bytes = f.read()
                        
                        file_name = os.path.basename(resultado)
                        st.download_button(
                            label="📥 Descargar PDF Compilado",
                            data=pdf_bytes,
                            file_name=file_name,
                            mime="application/pdf"
                        )
                    else:
                        st.error(f"No se encontró el archivo PDF en la ruta: {resultado}")
                except Exception as ex:
                    st.error(f"Error al leer el archivo PDF para descarga: {ex}")
            else:
                st.error(f"Error en la compilación: {resultado}")