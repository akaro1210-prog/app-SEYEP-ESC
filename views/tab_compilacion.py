import streamlit as st
import os
from latex_builder import compilar_estudio_latex

def render(
    config_vars=None,
    df_control_cambios=None,
    datos_sistema_cno=None,
    datos_tension_59n_isla=None,
    datos_sobrecorriente=None,
    datos_anexos_eacp=None,
):
    st.subheader("🚀 Compilar Documento ANEXO EACP")
    st.write("Haz clic en el botón para generar el documento **ANEXO EACP** en formato PDF (y su código fuente `.tex`) con todas las definiciones y tablas configuradas.")

    params_finales = {}
    for bloque in [
        config_vars,
        datos_sistema_cno,
        datos_tension_59n_isla,
        datos_sobrecorriente,
        datos_anexos_eacp,
    ]:
        if isinstance(bloque, dict):
            params_finales.update(bloque)

    if df_control_cambios is not None:
        params_finales["df_control_cambios"] = df_control_cambios

    if st.button("🔨 Compilar PDF (ANEXO EACP)", type="primary"):
        with st.spinner("Compilando documento LaTeX (2 pasadas para Tabla de Contenido, Índices y Referencias Cruzadas)..."):
            exito, resultado = compilar_estudio_latex(params_finales)
            if exito:
                st.success("✅ ¡PDF del ANEXO EACP generado exitosamente!")
                if os.path.exists(resultado):
                    with open(resultado, "rb") as f_pdf:
                        st.download_button(
                            label="📥 Descargar PDF (Anexo_EACP.pdf)",
                            data=f_pdf.read(),
                            file_name="Anexo_EACP.pdf",
                            mime="application/pdf"
                        )
                if os.path.exists("Anexo_EACP.tex"):
                    with open("Anexo_EACP.tex", "rb") as f_tex:
                        st.download_button(
                            label="📄 Descargar código fuente LaTeX (.tex)",
                            data=f_tex.read(),
                            file_name="Anexo_EACP.tex",
                            mime="text/plain"
                        )
            else:
                if "No se encontró el compilador 'pdflatex'" in resultado:
                    st.warning(resultado)
                else:
                    st.error(resultado)

                if os.path.exists("Anexo_EACP.tex"):
                    with open("Anexo_EACP.tex", "rb") as f_tex:
                        st.download_button(
                            label="📄 Descargar código fuente LaTeX (Anexo_EACP.tex)",
                            data=f_tex.read(),
                            file_name="Anexo_EACP.tex",
                            mime="text/plain",
                            help="Puedes descargar este archivo .tex y abrirlo en Overleaf o en tu editor LaTeX favorito para compilarlo directamente a PDF."
                        )
