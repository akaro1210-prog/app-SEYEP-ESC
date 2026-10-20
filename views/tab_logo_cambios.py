import streamlit as st
import pandas as pd
import os
from project_manager import obtener_df, obtener_ver

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
    ver = obtener_ver()
    st.subheader("🖼️ Portada (Logo del Cliente) y Control de Cambios")
    st.write("Sube el logo del cliente para la portada del **ANEXO EACP** y edita las filas de la tabla de Control de Cambios (`\\controlcambios`).")

    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        st.markdown("#### 1. Logo del Cliente (`Logo_Cliente.png`)")
        up_logo = st.file_uploader(
            f"Subir Logo para Portada ({estado_archivo('Logo_Cliente.png')}):",
            type=["png", "jpg", "jpeg"],
            key=f"up_logo_eacp_{ver}"
        )
        if guardar_archivo_subido(up_logo, "Logo_Cliente.png"):
            st.success("✅ Logo_Cliente.png guardado correctamente.")

    with col_l2:
        st.markdown("#### 2. Encabezado y Pie de Página Corporativos")
        st.caption("Si ya están en la carpeta del proyecto se usan automáticamente; si deseas actualizarlos puedes subirlos aquí:")
        up_enc = st.file_uploader(
            f"Encabezado.png ({estado_archivo('Encabezado.png')})",
            type=["png", "jpg", "jpeg"],
            key=f"up_enc_eacp_{ver}"
        )
        if guardar_archivo_subido(up_enc, "Encabezado.png"):
            st.success("✅ Encabezado.png actualizado.")
        up_pie = st.file_uploader(
            f"Piedepagina.png ({estado_archivo('Piedepagina.png')})",
            type=["png", "jpg", "jpeg"],
            key=f"up_pie_eacp_{ver}"
        )
        if guardar_archivo_subido(up_pie, "Piedepagina.png"):
            st.success("✅ Piedepagina.png actualizado.")

    st.markdown("---")
    st.markdown("### 📝 Tabla de Control de Cambios (`\\controlcambios`)")
    st.caption("Puedes agregar nuevas filas cuando el OR solicite ajustes sobre una revisión:")

    df_default = pd.DataFrame([
        {
            "VERSIÓN No.": "0",
            "DESCRIPCIÓN": "Análisis Estudio Coordinación de Protecciones.",
            "FECHA": "23/09/2026",
            "OBSERVACIONES": ""
        }
    ])

    df_control_cambios = st.data_editor(
        obtener_df("df_control_cambios", df_default),
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_cambios_eacp_{ver}"
    )

    st.session_state["df_control_cambios"] = df_control_cambios
    return df_control_cambios
