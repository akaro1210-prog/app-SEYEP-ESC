import streamlit as st
import pandas as pd
import os

def guardar_archivo_subido(uploaded_file, nombre_destino):
    """Guarda la imagen subida con el nombre exacto esperado por LaTeX (convirtiendo a PNG válido)."""
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
    return "✅ Cargada" if os.path.exists(nombre_archivo) else "⚠️ Pendiente"

def render(config_vars=None):
    if config_vars is None:
        config_vars = {}

    year_ini = str(config_vars.get("YearInicial", config_vars.get("year_inicial", "2027"))).strip() or "2027"
    year_fin = str(config_vars.get("YearFinal", config_vars.get("year_final", "2032"))).strip() or "2032"

    st.subheader("📌 Secciones 9 y 10: Conclusiones y Anexos (Flujos de Carga)")
    st.write("Edita las viñetas de conclusiones del estudio (`\\CONCLUSIONES`) y configura o desactiva la sección de Anexos.")

    st.markdown("### 9. Conclusiones (`\\CONCLUSIONES`)")
    st.caption("Puedes agregar, editar o eliminar filas. Cada fila se convertirá en un `\\item` dentro de la sección de Conclusiones.")

    conclusiones_default = pd.DataFrame([
        {"Conclusión": r"Los equipos empleados en el proyecto (Paneles Solares, Protecciones) cumplen con la certificación de conformidad RETIE."},
        {"Conclusión": r"Las simulaciones de flujo en estado estable con GD se evidencian tensiones que se mantienen en los valores establecidos."},
        {"Conclusión": r"Los niveles de perdidasse mantienen con la introducción del proyecto."},
        {"Conclusión": r"Las simulaciones de cortocircuito no presentan cambios mayores al 10\% con la entrada en operación del GD en ningún punto del circuito"},
        {"Conclusión": r"Los ajustes propuestos para el proyecto coordinan correctamente con las protecciones existentes, por lo tanto no se requiere cambios de ajustes en los elementos existentes."},
        {"Conclusión": r"Los inversores cumplen con las normas de equivalencia internacionales como lo son la IEEE1547 y la UL 1741 para la integración a la red. Su nivel de distorsión armónica de corriente según ficha técnica es <3\%."},
        {"Conclusión": r"El Sistema propuesto de 900 kWac no afecta de manera significativa la red de distribución y la potencia inyectada de los excedentes será consumida por la red."}
    ])

    df_conclusiones = st.data_editor(
        conclusiones_default,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_conclusiones"
    )

    st.markdown("---")
    st.markdown("### 10. Anexos: Gráficas de Perfiles y Flujos de Carga (`\\Flujosdecarga`)")

    # Opción principal para activar o desactivar (omitir) por completo los Anexos en el PDF
    incluir_anexos = st.checkbox(
        "✅ Incluir sección de Anexos (Flujos de Carga) en el informe PDF",
        value=True,
        key="chk_incluir_anexos"
    )

    modo_anexos = "H9_H12_H15"
    archivos_libres_anexos = st.session_state.get("archivos_libres_anexos", [])
    omitir_no_cargados = False

    if not incluir_anexos:
        st.warning("🚫 La sección de Anexos está desactivada. Se omitirá por completo del informe PDF y de la Tabla de Contenido.")
    else:
        omitir_no_cargados = st.checkbox(
            "Omitir automáticamente del PDF las gráficas de anexos que aún no tengan imagen cargada",
            value=False,
            key="chk_omitir_anexos_vacios"
        )

        modo_anexos_label = st.radio(
            "Selecciona la plantilla de gráficas para la sección de Anexos:",
            [
                "Plantilla Horaria H9, H12 y H15 Sin/Con Proyecto (EPM / EBSA)",
                "Plantilla Carga Pura (CP), Demanda Mínima (DMI) y Demanda Máxima (DMX) (CEO)",
                "Modo Libre: Mostrar todas las imágenes de flujo de carga que subas a continuación"
            ],
            index=0
        )

        if modo_anexos_label.startswith("Plantilla Horaria"):
            modo_anexos = "H9_H12_H15"
        elif modo_anexos_label.startswith("Plantilla Carga Pura"):
            modo_anexos = "CP_DMI_DMX"
        else:
            modo_anexos = "LIBRE"

        if modo_anexos in ("H9_H12_H15", "CP_DMI_DMX"):
            st.info(
                f"📅 Años detectados desde la pestaña Variables: **Año Inicial = {year_ini}** | **Año Final = {year_fin}**. "
                "Al subir una imagen en cualquiera de las casillas de abajo, la aplicación la renombra automáticamente al nombre exacto que requiere LaTeX."
            )

            col_y1, col_y2 = st.columns(2)

            if modo_anexos == "H9_H12_H15":
                slots_ini = [
                    (f"H9_SP_{year_ini}.png", f"Hora 9 Sin Proyecto ({year_ini})"),
                    (f"H9_CP_{year_ini}.png", f"Hora 9 Con Proyecto ({year_ini})"),
                    (f"H12_SP_{year_ini}.png", f"Hora 12 Sin Proyecto ({year_ini})"),
                    (f"H12_CP_{year_ini}.png", f"Hora 12 Con Proyecto ({year_ini})"),
                    (f"H15_SP_{year_ini}.png", f"Hora 15 Sin Proyecto ({year_ini})"),
                    (f"H15_CP_{year_ini}.png", f"Hora 15 Con Proyecto ({year_ini})"),
                ]
                slots_fin = [
                    (f"H9_SP_{year_fin}.png", f"Hora 9 Sin Proyecto ({year_fin})"),
                    (f"H9_CP_{year_fin}.png", f"Hora 9 Con Proyecto ({year_fin})"),
                    (f"H12_SP_{year_fin}.png", f"Hora 12 Sin Proyecto ({year_fin})"),
                    (f"H12_CP_{year_fin}.png", f"Hora 12 Con Proyecto ({year_fin})"),
                    (f"H15_SP_{year_fin}.png", f"Hora 15 Sin Proyecto ({year_fin})"),
                    (f"H15_CP_{year_fin}.png", f"Hora 15 Con Proyecto ({year_fin})"),
                ]
            else:
                slots_ini = [
                    (f"Flujo CP_{year_ini}.png", f"1. Carga Pura CP ({year_ini})"),
                    (f"Flujo DMI GCP_{year_ini}.png", f"2. Demanda Mínima Con Proyecto DMI GCP ({year_ini})"),
                    (f"Flujo DMI GSP_{year_ini}.png", f"3. Demanda Mínima Sin Proyecto DMI GSP ({year_ini})"),
                    (f"Flujo DMX GCP_{year_ini}.png", f"4. Demanda Máxima Con Proyecto DMX GCP ({year_ini})"),
                    (f"Flujo DMX GSP_{year_ini}.png", f"5. Demanda Máxima Sin Proyecto DMX GSP ({year_ini})"),
                ]
                slots_fin = [
                    (f"Flujo CP_{year_fin}.png", f"1. Carga Pura CP ({year_fin})"),
                    (f"Flujo DMI GCP_{year_fin}.png", f"2. Demanda Mínima Con Proyecto DMI GCP ({year_fin})"),
                    (f"Flujo DMI GSP_{year_fin}.png", f"3. Demanda Mínima Sin Proyecto DMI GSP ({year_fin})"),
                    (f"Flujo DMX GCP_{year_fin}.png", f"4. Demanda Máxima Con Proyecto DMX GCP ({year_fin})"),
                    (f"Flujo DMX GSP_{year_fin}.png", f"5. Demanda Máxima Sin Proyecto DMX GSP ({year_fin})"),
                ]

            with col_y1:
                st.markdown(f"#### 📂 Gráficas Año Inicial ({year_ini})")
                for arch_dest, etiqueta in slots_ini:
                    up_f = st.file_uploader(
                        f"{etiqueta} → '{arch_dest}' ({estado_archivo(arch_dest)})",
                        type=["png", "jpg", "jpeg"],
                        key=f"up_anexo_{arch_dest}"
                    )
                    if guardar_archivo_subido(up_f, arch_dest):
                        st.success(f"✅ Guardada como {arch_dest}")

            with col_y2:
                st.markdown(f"#### 📂 Gráficas Año Final ({year_fin})")
                for arch_dest, etiqueta in slots_fin:
                    up_f = st.file_uploader(
                        f"{etiqueta} → '{arch_dest}' ({estado_archivo(arch_dest)})",
                        type=["png", "jpg", "jpeg"],
                        key=f"up_anexo_{arch_dest}"
                    )
                    if guardar_archivo_subido(up_f, arch_dest):
                        st.success(f"✅ Guardada como {arch_dest}")

        else:
            st.info("Sube todas las imágenes de flujo de carga que quieras incluir en Anexos; se insertarán en el orden en que las subas.")
            up_libres = st.file_uploader(
                "Subir imágenes de flujo de carga para Anexos:",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="up_anexos_libres"
            )
            if up_libres:
                nuevos = []
                for idx, arch in enumerate(up_libres):
                    nombre_seguro = f"Anexo_Flujo_{idx+1}.png"
                    guardar_archivo_subido(arch, nombre_seguro)
                    titulo_limpio = os.path.splitext(arch.name)[0].replace("_", " ")
                    nuevos.append({"archivo": nombre_seguro, "caption": f"Diagrama unifilar flujo de carga - {titulo_limpio}"})
                archivos_libres_anexos = nuevos
                st.session_state["archivos_libres_anexos"] = archivos_libres_anexos
                st.success(f"✅ {len(archivos_libres_anexos)} imágenes listas para los Anexos.")

    datos = {
        "df_conclusiones": df_conclusiones,
        "incluir_anexos": incluir_anexos,
        "omitir_no_cargados": omitir_no_cargados,
        "modo_anexos": modo_anexos,
        "archivos_libres_anexos": archivos_libres_anexos
    }
    st.session_state["datos_sec_9_10"] = datos
    return datos
