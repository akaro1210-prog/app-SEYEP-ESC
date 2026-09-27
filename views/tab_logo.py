import os
import streamlit as st
from PIL import Image

def render():
    st.subheader("Logotipo del Cliente")
    st.markdown("Sube la imagen del logotipo del cliente (formatos permitidos: **PNG, JPG, JPEG**).")

    logo_filename = "Logo_Cliente.png"

    # Componente para subir archivo
    uploaded_file = st.file_uploader(
        "Seleccionar archivo de imagen", 
        type=["png", "jpg", "jpeg"],
        key="logo_uploader"
    )

    if uploaded_file is not None:
        try:
            # Abrimos la imagen con PIL para verificar que sea válida y convertirla a RGB/PNG estándar
            image = Image.open(uploaded_file)
            
            # Si tiene transparencia (RGBA) o paleta, la guardamos asegurando compatibilidad total
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGBA")
            else:
                image = image.convert("RGB")
                
            # Guardamos la imagen procesada de forma limpia en disco
            image.save(logo_filename, "PNG")
            st.success("¡Logotipo cargado y procesado exitosamente!")
        except Exception as e:
            st.error(f"El archivo seleccionado no es una imagen válida o está corrupto. Error: {e}")

    # Si ya existe un logo guardado (ya sea de antes o recién subido), lo mostramos
    if os.path.exists(logo_filename):
        try:
            st.markdown("---")
            st.markdown("**Logotipo actual en uso para la portada:**")
            # Mostramos usando la ruta en texto plano (string) para evitar el error de BytesIO
            st.image(logo_filename, width=250)
            return logo_filename
        except Exception as e:
            st.warning(f"No se pudo previsualizar la imagen actual: {e}")
            return logo_filename
            
    return None