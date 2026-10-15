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
    st.subheader("🖼️ Logotipo del Cliente para Portada")
    st.write(
        "Sube el logotipo del cliente o promotor del proyecto. Este logo se insertará automáticamente "
        "en la portada principal del **Estudio de Conexión Simplificado (ESC)** con escalado proporcional."
    )

    col_l1, col_l2 = st.columns([1.2, 1])
    with col_l1:
        st.markdown("#### Archivo: `Logo_Cliente.png`")
        st.info(f"Estado en carpeta de trabajo: **{estado_archivo('Logo_Cliente.png')}**")
        up_logo = st.file_uploader(
            "Seleccionar imagen del Logo:",
            type=["png", "jpg", "jpeg"],
            key="up_logo_cliente_esc"
        )
        if guardar_archivo_subido(up_logo, "Logo_Cliente.png"):
            st.success("✅ ¡Logo_Cliente.png guardado con éxito! Se utilizará en la compilación de la Portada.")

    with col_l2:
        st.markdown("#### Vista previa en Portada")
        if os.path.exists("Logo_Cliente.png"):
            st.image("Logo_Cliente.png", caption="Logo del Cliente para Portada", width=240)
        else:
            st.caption("Aún no se ha cargado ningún logo. Si no se sube, la portada se compilará sin bloque de logotipo.")
