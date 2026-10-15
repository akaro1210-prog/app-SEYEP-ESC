import streamlit as st
import os

def guardar_archivo_subido(uploaded_file, nombre_destino):
    if uploaded_file is not None:
        try:
            from PIL import Image
            img = Image.open(uploaded_file)
            img = img.convert("RGBA") if img.mode in ("RGBA", "P") else img.convert("RGB")
            img.save(nombre_destino, "PNG")
        except Exception:
            with open(nombre_destino, "wb") as f:
                f.write(uploaded_file.getbuffer())
        return True
    return False

def estado_archivo(nombre_archivo):
    return "✅ Cargado" if os.path.exists(nombre_archivo) else "⚠️ Pendiente"

def render():
    st.subheader("📑 Formato Institucional del Documento (SEYEP S.A.S.)")
    st.write(
        "Configura los encabezados, pies de página corporativos y estilos base que se aplican a todo el informe "
        "de Estudio de Conexión Simplificado (ESC)."
    )

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("#### 1. Encabezado Institucional (`Encabezado.png`)")
        st.caption("Aparece en la parte superior de cada página del informe técnico.")
        st.info(f"Estado actual: **{estado_archivo('Encabezado.png')}**")
        up_enc = st.file_uploader(
            "Subir o actualizar Encabezado.png:",
            type=["png", "jpg", "jpeg"],
            key="up_formato_encabezado"
        )
        if guardar_archivo_subido(up_enc, "Encabezado.png"):
            st.success("✅ Encabezado.png actualizado con éxito.")

    with col_f2:
        st.markdown("#### 2. Pie de Página Corporativo (`Piedepagina.png`)")
        st.caption("Aparece en la parte inferior de cada página con los datos de contacto y membrete SEYEP.")
        st.info(f"Estado actual: **{estado_archivo('Piedepagina.png')}**")
        up_pie = st.file_uploader(
            "Subir o actualizar Piedepagina.png:",
            type=["png", "jpg", "jpeg"],
            key="up_formato_piedepagina"
        )
        if guardar_archivo_subido(up_pie, "Piedepagina.png"):
            st.success("✅ Piedepagina.png actualizado con éxito.")

    st.markdown("---")
    st.markdown("#### 📐 Configuración de Página y Tipografía LaTeX")
    st.markdown(
        "- **Tamaño de Papel:** Carta (Letterpaper)\n"
        "- **Márgenes:** Izquierda 2.5 cm, Derecha 2.5 cm, Superior 2.8 cm, Inferior 2.8 cm\n"
        "- **Tipografía:** Normal / 12pt con espaciado de 1.15 líneas\n"
        "- **Referencias cruzadas:** Paquete `cleveref` en español (`\\cref{fig:...}`, `\\cref{tab:...}`)"
    )
