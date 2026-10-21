import streamlit as st
import os
from latex_builder import compilar_estudio_latex, generar_codigo_latex
from secciones_manager import obtener_diccionario_secciones


def render(config_vars, resumen_textos, df_control_cambios, texto_supuesto_activo, usar_tabla_upme, df_supuestos_upme, archivo_or_path):
    st.subheader("🚀 Compilación del Estudio en LaTeX / PDF")
    st.write(
        "Panel de control para ensamblar y compilar el documento del **Estudio de Conexión Simplificado** "
        "(GD o Autogenerador) con todas las secciones configuradas, secciones opcionales y personalizadas."
    )

    # Asegurar que todas las secciones y subsecciones activas / opcionales estén presentes
    dict_secciones = obtener_diccionario_secciones()
    datos_sec_2_3 = st.session_state.get("datos_sec_2_3", {})
    datos_sec_4_6 = st.session_state.get("datos_sec_4_5_6", {})
    datos_sec_7 = st.session_state.get("datos_sec_7", {})
    datos_sec_8 = st.session_state.get("datos_sec_8", {})
    datos_sec_9_10 = st.session_state.get("datos_sec_9_10", {})

    params_finales = {
        **(config_vars or {}),
        **(resumen_textos or {}),
        **(datos_sec_2_3 or {}),
        **(datos_sec_4_6 or {}),
        **(datos_sec_7 or {}),
        **(datos_sec_8 or {}),
        **(datos_sec_9_10 or {}),
        **(dict_secciones or {}),
        "df_control_cambios": df_control_cambios,
        "texto_supuesto_activo": texto_supuesto_activo,
        "usar_tabla_upme": usar_tabla_upme,
        "df_supuestos_upme": df_supuestos_upme,
        "archivo_or_path": archivo_or_path
    }

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔨 Compilar Informe PDF", type="primary", use_container_width=True):
            with st.spinner("Compilando documento LaTeX con pdflatex (2 pasadas para TOC, listas y referencias)..."):
                exito, resultado = compilar_estudio_latex(params_finales)
                st.session_state["compilacion_ejecutada"] = True
                st.session_state["compilacion_exito"] = exito
                st.session_state["compilacion_resultado"] = resultado
                if exito and resultado and os.path.exists(resultado):
                    with open(resultado, "rb") as f_pdf:
                        st.session_state["compilacion_pdf_bytes"] = f_pdf.read()
                st.rerun()

    with col_b2:
        if st.button("📄 Generar Código Fuente (.tex)", type="secondary", use_container_width=True):
            codigo_tex = generar_codigo_latex(params_finales)
            with open("Estudio_Conexion.tex", "w", encoding="utf-8") as f:
                f.write(codigo_tex)
            st.session_state["tex_generado"] = True
            st.session_state["tex_contenido"] = codigo_tex
            st.success("✅ ¡Archivo Estudio_Conexion.tex generado con éxito!")
            st.rerun()

    # --- Mostrar Resultados Persistentes de la Compilación ---
    if st.session_state.get("compilacion_ejecutada"):
        exito = st.session_state.get("compilacion_exito", False)
        resultado = str(st.session_state.get("compilacion_resultado", ""))

        st.markdown("---")
        if exito:
            st.success("🎉 **¡Informe PDF compilado con éxito!** Descarga tu documento a continuación:")
            pdf_bytes = st.session_state.get("compilacion_pdf_bytes")
            if not pdf_bytes and os.path.exists("Estudio_Conexion.pdf"):
                try:
                    with open("Estudio_Conexion.pdf", "rb") as fp_read:
                        pdf_bytes = fp_read.read()
                        st.session_state["compilacion_pdf_bytes"] = pdf_bytes
                except Exception as ex_read:
                    st.error(f"Error al leer el archivo PDF: {ex_read}")

            if pdf_bytes:
                st.download_button(
                    label="📥 Descargar PDF Compilado (Estudio_Conexion.pdf)",
                    data=pdf_bytes,
                    file_name="Estudio_Conexion.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    key="btn_descarga_pdf_exito"
                )

            # Ofrecer también el .tex complementario
            if os.path.exists("Estudio_Conexion.tex"):
                with open("Estudio_Conexion.tex", "r", encoding="utf-8", errors="ignore") as f_tex:
                    tex_code_str = f_tex.read()
                st.download_button(
                    label="📄 Descargar código fuente LaTeX complementario (.tex)",
                    data=tex_code_str.encode("utf-8"),
                    file_name="Estudio_Conexion.tex",
                    mime="text/plain",
                    use_container_width=True,
                    key="btn_tex_complementario"
                )
        else:
            if "No se encontró el ejecutable 'pdflatex'" in resultado or "No se encontró el compilador" in resultado:
                st.warning("⚠️ **pdflatex no se encuentra instalado en el entorno actual del servidor.**")
                st.info(resultado)
            else:
                st.error("⚠️ **Detalle de la compilación LaTeX:**")
                st.code(resultado, language="text")

            # Si a pesar de advertencias el PDF fue generado, permitir descargarlo
            if os.path.exists("Estudio_Conexion.pdf") and os.path.getsize("Estudio_Conexion.pdf") > 1000:
                try:
                    with open("Estudio_Conexion.pdf", "rb") as fp_rec:
                        st.info("📄 Se detectó un archivo PDF generado en el directorio:")
                        st.download_button(
                            label="📥 Descargar PDF Generado (Estudio_Conexion.pdf)",
                            data=fp_rec.read(),
                            file_name="Estudio_Conexion.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True,
                            key="btn_descarga_pdf_parcial"
                        )
                except Exception:
                    pass

            # Ofrecer SIEMPRE el botón para descargar el código .tex generado
            if os.path.exists("Estudio_Conexion.tex"):
                with open("Estudio_Conexion.tex", "r", encoding="utf-8", errors="ignore") as f_tex:
                    tex_code = f_tex.read()
                st.markdown("##### 💡 Descarga directa del código fuente LaTeX (.tex)")
                st.caption("Puedes compilar este archivo `.tex` directamente en **Overleaf** o con tu distribución LaTeX local (MiKTeX/TeX Live):")
                st.download_button(
                    label="📥 Descargar Estudio_Conexion.tex (Listo para Overleaf o MiKTeX)",
                    data=tex_code.encode("utf-8"),
                    file_name="Estudio_Conexion.tex",
                    mime="text/plain",
                    use_container_width=True,
                    key="btn_error_descarga_tex"
                )

    elif st.session_state.get("tex_generado"):
        tex_data = st.session_state.get("tex_contenido", "")
        if not tex_data and os.path.exists("Estudio_Conexion.tex"):
            with open("Estudio_Conexion.tex", "r", encoding="utf-8", errors="ignore") as ft:
                tex_data = ft.read()
        st.markdown("---")
        st.download_button(
            label="📥 Descargar Estudio_Conexion.tex",
            data=tex_data.encode("utf-8"),
            file_name="Estudio_Conexion.tex",
            mime="text/plain",
            type="primary",
            use_container_width=True,
            key="btn_descarga_tex_generado"
        )

    # Si ya existe un .tex o .pdf generado en disco previamente, ofrecer descarga directa
    if os.path.exists("Estudio_Conexion.pdf") or os.path.exists("Estudio_Conexion.tex"):
        st.markdown("---")
        st.markdown("##### 📂 Archivos en Disco Disponibles para Descarga Inmediata")
        c_d1, c_d2 = st.columns(2)
        with c_d1:
            if os.path.exists("Estudio_Conexion.pdf") and os.path.getsize("Estudio_Conexion.pdf") > 1000:
                with open("Estudio_Conexion.pdf", "rb") as fp:
                    st.download_button(
                        label="📥 Descargar Estudio_Conexion.pdf (Última versión)",
                        data=fp.read(),
                        file_name="Estudio_Conexion.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="btn_descarga_directa_pdf"
                    )
        with c_d2:
            if os.path.exists("Estudio_Conexion.tex"):
                with open("Estudio_Conexion.tex", "r", encoding="utf-8", errors="ignore") as ft:
                    st.download_button(
                        label="📄 Descargar Estudio_Conexion.tex (Última versión)",
                        data=ft.read().encode("utf-8"),
                        file_name="Estudio_Conexion.tex",
                        mime="text/plain",
                        use_container_width=True,
                        key="btn_descarga_directa_tex"
                    )
