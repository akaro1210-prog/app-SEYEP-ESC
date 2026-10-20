import streamlit as st
import os
from project_manager import obtener_val, obtener_ver

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
    return "✅ Cargada" if os.path.exists(nombre_archivo) else "⚠️ Pendiente"

def render():
    ver = obtener_ver()
    st.subheader("📂 Sección 2: Anexos (Curvas de Coordinación de Protecciones y Cortocircuito)")
    st.write(
        "Configura el texto introductorio de Anexos y sube las gráficas de coordinación de protecciones. "
        "Puedes desactivar toda la sección de Anexos o pedir que omita automáticamente las gráficas que no subas."
    )

    incluir_anexos = st.checkbox(
        "✅ Incluir la sección 2 (ANEXOS) en el informe PDF",
        value=bool(obtener_val("incluir_anexos", True)),
        key=f"chk_incluir_anexos_eacp_{ver}"
    )

    if not incluir_anexos:
        st.warning("🚫 La sección de Anexos está desactivada y se omitirá del PDF y de la Tabla de Contenido.")
        datos = {
            "incluir_anexos": False,
            "omitir_no_cargados": False,
            "incluir_fallas_30ohms": False,
            "incluir_cortos_anexo": False,
            "intro_anexos_txt": ""
        }
        st.session_state["datos_anexos_eacp"] = datos
        return datos

    c_opt1, c_opt2, c_opt3 = st.columns(3)
    with c_opt1:
        omitir_no_cargados = st.checkbox(
            "Omitir gráficas que no tengan imagen cargada",
            value=bool(obtener_val("omitir_no_cargados", False)),
            key=f"chk_omitir_vacios_eacp_{ver}"
        )
    with c_opt2:
        incluir_fallas_30ohms = st.checkbox(
            "Incluir también curvas de falla de 30 ohms",
            value=bool(obtener_val("incluir_fallas_30ohms", False)),
            key=f"chk_30ohms_eacp_{ver}"
        )
    with c_opt3:
        incluir_cortos_anexo = st.checkbox(
            "Incluir sub-bloque de Cortocircuito (ICC 1F/3F)",
            value=bool(obtener_val("incluir_cortos_anexo", False)),
            key=f"chk_cortos_anexo_eacp_{ver}"
        )

    intro_anexos_default = (
        r"Adicional a las imágenes de este anexo, se adjunta en los anexos entregados con el informe la simulación "
        r"de la red completa en un archivo .PFD y un archivo en PDF con el repositorio de los resultados para todas las "
        r"líneas y nodos trifásicos del circuito."
        "\n"
        r"Los resultados de las tablas del informe y el repositorio del anexo en PDF se realizó con el modelo equivalente "
        r"de red suministrado por el OR, al igual que las simulaciones para la coordinación de protecciones.\\"
    )
    intro_anexos_txt = st.text_area(
        "Párrafo introductorio de la sección 2 (ANEXOS):",
        value=obtener_val("intro_anexos_txt", intro_anexos_default),
        height=90,
        key=f"int_anex_{ver}"
    )

    if incluir_cortos_anexo:
        st.markdown("---")
        st.markdown("### ⚡ Gráficas Opcionales de Cortocircuito (`CORTO \\YearInicial` y `CORTO \\YearFinal`)")
        c_cc1, c_cc2 = st.columns(2)
        slots_corto = [
            ("ICC 1F GCP.png", "Corriente de cortocircuito monofásica con GD"),
            ("ICC 1F GSP.png", "Corriente de cortocircuito monofásica sin GD"),
            ("ICC 3F GCP.png", "Corriente de cortocircuito trifásica con GD"),
            ("ICC 3F GSP.png", "Corriente de cortocircuito trifásica sin GD"),
        ]
        for idx, (arch_c, etiq_c) in enumerate(slots_corto):
            with (c_cc1 if idx % 2 == 0 else c_cc2):
                up_c = st.file_uploader(
                    f"{etiq_c} → '{arch_c}' ({estado_archivo(arch_c)})",
                    type=["png", "jpg", "jpeg"],
                    key=f"up_eacp_corto_{arch_c}_{ver}"
                )
                if guardar_archivo_subido(up_c, arch_c):
                    st.success(f"✅ Guardada como {arch_c}")

    st.markdown("---")
    st.markdown("### 🛡️ Gráficas de Coordinación de Protecciones (`PROTECCIONES`)")
    st.info("Cualquier imagen que subas en cada casilla se renombra automáticamente al nombre exacto que usa el documento LaTeX.")

    with st.expander("📌 Grupo 1: Fallas en Barra Lado de Alta Trafo GD (\\nombreProyecto)", expanded=True):
        slots_alta = [
            ("Protecciones falla lado alta proyecto.png", "1. Diagrama Falla Barra en lado de alta trafo GD"),
            ("Protecciones falla 1F franca lado alta proyecto.png", "2. Falla 1F franca barra lado de alta"),
            ("Protecciones falla 1F 5ohms lado alta proyecto.png", "3. Falla 1F 5 ohms barra lado de alta"),
            ("Protecciones falla 1F 15ohms lado alta proyecto.png", "4. Falla 1F 15 ohms barra lado de alta"),
        ]
        if incluir_fallas_30ohms:
            slots_alta.append(("Protecciones falla 1F 30ohms lado alta proyecto.png", "5. Falla 1F 30 ohms barra lado de alta"))
        slots_alta.extend([
            ("Protecciones falla 3F franca lado alta proyecto.png", "6. Falla 3F franca barra lado de alta"),
            ("Protecciones falla 3F 5ohms lado alta proyecto.png", "7. Falla 3F 5 ohms barra lado de alta"),
            ("Protecciones falla 3F 15ohms lado alta proyecto.png", "8. Falla 3F 15 ohms barra lado de alta"),
        ])
        if incluir_fallas_30ohms:
            slots_alta.append(("Protecciones falla 3F 30ohms lado alta proyecto.png", "9. Falla 3F 30 ohms barra lado de alta"))

        ca1, ca2 = st.columns(2)
        for idx, (arch_dest, etiqueta) in enumerate(slots_alta):
            with (ca1 if idx % 2 == 0 else ca2):
                up_f = st.file_uploader(
                    f"{etiqueta} → '{arch_dest}' ({estado_archivo(arch_dest)})",
                    type=["png", "jpg", "jpeg"],
                    key=f"up_alta_{arch_dest}_{ver}"
                )
                if guardar_archivo_subido(up_f, arch_dest):
                    st.success(f"✅ {arch_dest}")

    with st.expander("📌 Grupo 2: Fallas en Barra Lado de Baja Trafo GD (\\nombreProyecto)", expanded=True):
        slots_baja = [
            ("Protecciones falla lado baja proyecto.png", "1. Diagrama Falla Barra en lado de baja trafo GD"),
            ("Protecciones falla 1F franca lado baja proyecto.png", "2. Falla 1F franca barra lado de baja"),
            ("Protecciones falla 3F franca lado baja proyecto.png", "3. Falla 3F franca barra lado de baja"),
        ]
        cb1, cb2, cb3 = st.columns(3)
        cols_b = [cb1, cb2, cb3]
        for idx, (arch_dest, etiqueta) in enumerate(slots_baja):
            with cols_b[idx % 3]:
                up_f = st.file_uploader(
                    f"{etiqueta} → '{arch_dest}' ({estado_archivo(arch_dest)})",
                    type=["png", "jpg", "jpeg"],
                    key=f"up_baja_{arch_dest}_{ver}"
                )
                if guardar_archivo_subido(up_f, arch_dest):
                    st.success(f"✅ {arch_dest}")

    with st.expander("📌 Grupo 3: Fallas en Nodo de Conexión del Circuito (\\CTO)", expanded=True):
        slots_nodo = [
            ("Protecciones falla nodo conexión proyecto.png", "1. Diagrama Falla en nodo conexión del circuito"),
            ("Protecciones falla 1F franca nodo conexión proyecto.png", "2. Falla 1F franca nodo conexión"),
            ("Protecciones falla 1F 5ohms nodo conexión proyecto.png", "3. Falla 1F 5 ohms nodo conexión"),
            ("Protecciones falla 1F 15ohms nodo conexión proyecto.png", "4. Falla 1F 15 ohms nodo conexión"),
        ]
        if incluir_fallas_30ohms:
            slots_nodo.append(("Protecciones falla 1F 30ohms nodo conexión proyecto.png", "5. Falla 1F 30 ohms nodo conexión"))
        slots_nodo.extend([
            ("Protecciones falla 3F franca nodo conexión proyecto.png", "6. Falla 3F franca nodo conexión"),
            ("Protecciones falla 3F 5ohms nodo conexión proyecto.png", "7. Falla 3F 5 ohms nodo conexión"),
            ("Protecciones falla 3F 15ohms nodo conexión proyecto.png", "8. Falla 3F 15 ohms nodo conexión"),
        ])
        if incluir_fallas_30ohms:
            slots_nodo.append(("Protecciones falla 3F 30ohms nodo conexión proyecto.png", "9. Falla 3F 30 ohms nodo conexión"))

        cn1, cn2 = st.columns(2)
        for idx, (arch_dest, etiqueta) in enumerate(slots_nodo):
            with (cn1 if idx % 2 == 0 else cn2):
                up_f = st.file_uploader(
                    f"{etiqueta} → '{arch_dest}' ({estado_archivo(arch_dest)})",
                    type=["png", "jpg", "jpeg"],
                    key=f"up_nodo_{arch_dest}_{ver}"
                )
                if guardar_archivo_subido(up_f, arch_dest):
                    st.success(f"✅ {arch_dest}")

    datos = {
        "incluir_anexos": incluir_anexos,
        "omitir_no_cargados": omitir_no_cargados,
        "incluir_fallas_30ohms": incluir_fallas_30ohms,
        "incluir_cortos_anexo": incluir_cortos_anexo,
        "intro_anexos_txt": intro_anexos_txt,
    }
    st.session_state["datos_anexos_eacp"] = datos
    return datos
