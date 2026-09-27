import os
import streamlit as st

def render():
    st.subheader("🎨 Formato y Estética del Documento")
    st.write("Carga los recursos visuales oficiales para el encabezado y el pie de página que se aplicarán en el PDF corporativo.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### **Encabezado Institucional**")
        st.write("Dimensiones recomendadas orientadas al ancho de página con altura proporcional.")
        archivo_encabezado = st.file_uploader("Subir imagen de Encabezado (PNG)", type=["png", "jpg", "jpeg"], key="up_encabezado")
        
        if archivo_encabezado is not None:
            # Guardar con el nombre exacto que espera LaTeX
            with open("Encabezado.png", "wb") as f:
                f.write(archivo_encabezado.getbuffer())
            st.success("¡Encabezado guardado correctamente como `Encabezado.png`!")

        if os.path.exists("Encabezado.png"):
            st.image("Encabezado.png", caption="Encabezado actual activo", use_container_width=True)
        else:
            st.warning("⚠️ No hay imagen de encabezado activa en el directorio.")

    with col2:
        st.markdown("### **Pie de Página Institucional**")
        st.write("Imagen corporativa para la parte inferior de las páginas del informe.")
        archivo_pie = st.file_uploader("Subir imagen de Pie de Página (PNG)", type=["png", "jpg", "jpeg"], key="up_pie")
        
        if archivo_pie is not None:
            # Guardar con el nombre exacto que espera LaTeX
            with open("Piedepagina.png", "wb") as f:
                f.write(archivo_pie.getbuffer())
            st.success("¡Pie de página guardado correctamente como `Piedepagina.png`!")

        if os.path.exists("Piedepagina.png"):
            st.image("Piedepagina.png", caption="Pie de página actual activo", use_container_width=True)
        else:
            st.warning("⚠️ No hay imagen de pie de página activa en el directorio.")

    return os.path.exists("Encabezado.png") and os.path.exists("Piedepagina.png")