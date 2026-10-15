import streamlit as st
import os
from latex_builder import compilar_estudio_latex, generar_codigo_latex

def render(config_vars, resumen_textos, df_control_cambios, texto_supuesto_activo, usar_tabla_upme, df_supuestos_upme, archivo_or_path):
    st.subheader("🚀 Compilación del Estudio en LaTeX / PDF")
    st.write(
        "Panel de control para ensamblar y compilar el documento del **Estudio de Conexión Simplificado** "
        "(GD o Autogenerador) con todas las secciones configuradas, secciones opcionales y personalizadas."
    )

    params_finales = {
        **(config_vars or {}),
        **(resumen_textos or {}),
        "df_control_cambios": df_control_cambios,
        "texto_supuesto_activo": texto_supuesto_activo,
        "usar_tabla_upme": usar_tabla_upme,
        "df_supuestos_upme": df_supuestos_upme,
        "archivo_or_path": archivo_or_path
    }

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔨 Compilar Informe PDF", type="primary", use_container_width=True):
            with st.spinner("Compilando documento LaTeX con pdflatex..."):
                exito, resultado = compilar_estudio_latex(params_finales)
                if exito:
                    st.success("✅ ¡Informe PDF compilado con éxito!")
                    try:
                        if resultado and os.path.exists(resultado):
                            with open(resultado, "rb") as f:
                                pdf_bytes = f.read()
                            file_name = os.path.basename(resultado)
                            st.download_button(
                                label="📥 Descargar PDF Compilado (Estudio_Conexion.pdf)",
                                data=pdf_bytes,
                                file_name=file_name,
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.error(f"No se encontró el archivo PDF en la ruta: {resultado}")
                    except Exception as ex:
                        st.error(f"Error al leer el archivo PDF para descarga: {ex}")
                else:
                    st.error(f"Error en la compilación: {resultado}")

    with col_b2:
        if st.button("📄 Generar Código Fuente (.tex)", type="secondary", use_container_width=True):
            codigo_tex = generar_codigo_latex(params_finales)
            with open("Estudio_Conexion.tex", "w", encoding="utf-8") as f:
                f.write(codigo_tex)
            st.success("✅ ¡Archivo Estudio_Conexion.tex generado con éxito!")
            st.download_button(
                label="📥 Descargar Estudio_Conexion.tex",
                data=codigo_tex.encode("utf-8"),
                file_name="Estudio_Conexion.tex",
                mime="text/plain",
                use_container_width=True
            )

    # Si ya existe un .tex o .pdf generado, ofrecer botones directos de descarga
    if os.path.exists("Estudio_Conexion.pdf") or os.path.exists("Estudio_Conexion.tex"):
        st.markdown("---")
        st.markdown("##### 📂 Archivos Compilados Disponibles")
        c_d1, c_d2 = st.columns(2)
        with c_d1:
            if os.path.exists("Estudio_Conexion.pdf"):
                with open("Estudio_Conexion.pdf", "rb") as fp:
                    st.download_button(
                        label="📥 Descargar Estudio_Conexion.pdf",
                        data=fp.read(),
                        file_name="Estudio_Conexion.pdf",
                        mime="application/pdf",
                        key="btn_descarga_directa_pdf"
                    )
        with c_d2:
            if os.path.exists("Estudio_Conexion.tex"):
                with open("Estudio_Conexion.tex", "r", encoding="utf-8", errors="ignore") as ft:
                    st.download_button(
                        label="📄 Descargar Estudio_Conexion.tex",
                        data=ft.read().encode("utf-8"),
                        file_name="Estudio_Conexion.tex",
                        mime="text/plain",
                        key="btn_descarga_directa_tex"
                    )
