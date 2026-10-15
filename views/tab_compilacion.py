import streamlit as st
from latex_builder import generar_codigo_latex

def render():
    st.subheader("📄 Compilación y Exportación a PDF")
    
    secciones_activas = [s for s in st.session_state.secciones if s.get("imprimir_pdf", True)]
    secciones_omitidas = [s for s in st.session_state.secciones if not s.get("imprimir_pdf", True)]

    st.write(f"Se incluirán **{len(secciones_activas)} secciones** en el informe final.")
    if secciones_omitidas:
        st.warning(f"⚠️ Se omitirán {len(secciones_omitidas)} secciones desmarcadas en el selector de PDF.")

    # Generar código LaTeX filtrado
    codigo_tex = generar_codigo_latex(st.session_state.variables, st.session_state.secciones)

    # Vista previa del texto
    with st.expander("👁️ Vista Previa del Código LaTeX"):
        st.code(codigo_tex, language="latex")

    # Botón para descargar el archivo compilable
    st.download_button(
        label="📥 Descargar Archivo LaTeX (.tex)",
        data=codigo_tex,
        file_name=f"{st.session_state.variables.get('codigo_esc', 'informe')}_{st.session_state.tipo_informe}.tex",
        mime="text/plain"
    )
