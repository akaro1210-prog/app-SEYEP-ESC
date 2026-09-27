import streamlit as st
import os

def guardar_archivo_subido(uploaded_file, nombre_destino):
    """Guarda un archivo subido en la raíz del proyecto para que pdflatex lo encuentre."""
    if uploaded_file is not None:
        with open(nombre_destino, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    return False

def render():
    st.subheader("🏗️ Secciones 2 y 3: Descripción del Proyecto, Equipos e Insumos OR")
    st.write("Configura los textos, tablas de equipos, inversores, hojas técnicas e insumos del Operador de Red.")

    st.markdown("### 2.1 Información del proyecto")
    default_sec2_intro = (
        r"El proyecto \nombreProyecto\ de GD \capacidadMW, se conectará al SIN a través del circuito \CTO\ "
        r"de la S/E \SSEE\ al nivel de tensión \NT, propiedad del operador de red \OR, La ubicación del proyecto es \ubicacion. "
        r"En la \cref{tab:coordenadas} se detallan las coordenadas geográficas para la ubicación del proyecto GD \nombreProyecto. "
        r"El proyecto cuenta con una fecha en puesta de operación (en adelante FPO) para \FechaEntrada. "
        r"En la \cref{tab:descripcion_proyecto} se resumen las especificaciones técnicas de los equipos que conforman el proyecto."
    )
    sec2_intro = st.text_area("Párrafo introductorio (Sección 2.1):", value=default_sec2_intro, height=110)

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        vida_util = st.text_input("Vida Útil (Tabla 2):", value="30 años.")
    with col_d2:
        tipo_fuente = st.text_input("Tipo Fuente de Energía:", value="Energía Solar")
    with col_d3:
        tipo_panel_etiqueta = st.text_input("Etiqueta tipo de panel:", value="Panel Solar Bifacial")

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        prot_item = st.text_input("Ítem protección principal:", value="Protección – Interruptor")
    with col_p2:
        prot_desc = st.text_input("Descripción interruptor:", value="Interruptor LSI 3 x 1360A")
    with col_p3:
        prot_cant = st.text_input("Cantidad interruptor:", value="1 Und.")

    st.markdown("#### Configuración de Inversores (1 a 3 referencias)")
    num_inversores = st.selectbox("Cantidad de referencias de inversores en el proyecto:", [1, 2, 3], index=0)

    inv_items = []
    defaults_inv = [
        ("Inversor 150 kW On-Grid.", "Growat MAX 150KTL3-X2MV", "6 Und."),
        ("Inversor 50 kW On-Grid.", "Huawei Sun2000 50KTL-M3", "1 Und."),
        ("Inversor 40 kW On-Grid.", "Huawei Sun2000 40KTL-M3", "1 Und.")
    ]
    for i in range(num_inversores):
        c1, c2, c3 = st.columns(3)
        with c1:
            ref_i = st.text_input(f"Referencia Inversor {i+1}:", value=defaults_inv[i][0], key=f"ref_inv_{i}")
        with c2:
            mod_i = st.text_input(f"Modelo Inversor {i+1}:", value=defaults_inv[i][1], key=f"mod_inv_{i}")
        with c3:
            cant_i = st.text_input(f"Cantidad Inversor {i+1}:", value=defaults_inv[i][2], key=f"cant_inv_{i}")
        inv_items.append({"ref": ref_i, "modelo": mod_i, "cantidad": cant_i})

    default_sec2_cierre = (
        r"Finalmente, para la contextualización general del proyecto se presenta la \cref{fig:ubicacion}, donde se resalta la ubicación de este."
    )
    sec2_cierre = st.text_area("Párrafo de contextualización de ubicación:", value=default_sec2_cierre, height=70)

    incluir_geoespacial = st.checkbox("Incluir figura de Diagrama Eléctrico Geoespacial (Diagrama Geoespacial.png)", value=False)

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        up_ubicacion = st.file_uploader("Subir imagen 'Ubicacion Geográfica.png'", type=["png", "jpg", "jpeg"], key="up_ubic")
        if guardar_archivo_subido(up_ubicacion, "Ubicacion Geográfica.png"):
            st.success("✅ Ubicacion Geográfica.png guardada.")
    with col_u2:
        if incluir_geoespacial:
            up_geo = st.file_uploader("Subir 'Diagrama Geoespacial.png'", type=["png", "jpg", "jpeg"], key="up_geo")
            if guardar_archivo_subido(up_geo, "Diagrama Geoespacial.png"):
                st.success("✅ Diagrama Geoespacial.png guardada.")

    st.markdown("---")
    st.markdown("### 3.1 Equipos (`\\equipos` y `\\figinversores`)")
    default_sec3_intro = (
        r"En la \cref{fig:fichapanel}, se puede apreciar las características técnicas de los paneles fotovoltaicos seleccionados para el proyecto."
    )
    sec3_intro = st.text_area("Párrafo introductorio (Sección 3.1):", value=default_sec3_intro, height=70)

    default_equipos = (
        r"Sumado a \cantidadInversoruno\ inversores de 150 kW, 4 de ellos con 300 paneles cada uno y los otros dos con 280 cada uno, "
        r"su tensión de salida es de 800 V – 60 Hz respectivamente. "
        r"En la \cref{fig:fichainversoruno}, se aprecia las características operativas de los inversores instalados en el sistema de generación."
    )
    texto_equipos = st.text_area("Contenido del comando \\equipos:", value=default_equipos, height=100)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        up_panel = st.file_uploader("Subir 'Ficha panel.png'", type=["png", "jpg", "jpeg"], key="up_fpanel")
        if guardar_archivo_subido(up_panel, "Ficha panel.png"):
            st.success("✅ Ficha panel.png guardada.")
    with col_f2:
        for i, inv in enumerate(inv_items):
            nombre_ficha = f"Ficha {inv['modelo']}.png"
            up_finv = st.file_uploader(f"Subir '{nombre_ficha}'", type=["png", "jpg", "jpeg"], key=f"up_finv_{i}")
            if guardar_archivo_subido(up_finv, nombre_ficha):
                st.success(f"✅ {nombre_ficha} guardada.")

    st.markdown("---")
    st.markdown("### 3.2 Información OR (`\\informacionOR`)")
    default_sec3_or_texto = (
        r"El proyecto GD \nombreProyecto\ se conectará al circuito \CTO\, por tanto, el OR suministro a través de los insumos "
        r"datos de red de todo el circuito y ajuste de coordinación de protecciones."
    )
    sec3_or_texto = st.text_area("Párrafo introductorio Sección 3.2 (Información OR):", value=default_sec3_or_texto, height=80)

    modo_equivalente = st.radio(
        "Formato de la tabla 'Parámetros Equivalente de RED':",
        ["Imagen (equivalentered.png)", "Archivo CSV (equivalentered.csv)"],
        index=0
    )

    col_or1, col_or2, col_or3 = st.columns(3)
    with col_or1:
        if modo_equivalente.startswith("Imagen"):
            up_eq = st.file_uploader("Subir 'equivalentered.png'", type=["png", "jpg", "jpeg"], key="up_eq_png")
            if guardar_archivo_subido(up_eq, "equivalentered.png"):
                st.success("✅ equivalentered.png guardado.")
        else:
            up_eq_csv = st.file_uploader("Subir 'equivalentered.csv'", type=["csv"], key="up_eq_csv")
            if guardar_archivo_subido(up_eq_csv, "equivalentered.csv"):
                st.success("✅ equivalentered.csv guardado.")
    with col_or2:
        up_cargas_ini = st.file_uploader("Subir CSV cargas Año Inicial (ej. cargascto2027.csv)", type=["csv"], key="up_c_ini")
        if up_cargas_ini is not None:
            guardar_archivo_subido(up_cargas_ini, up_cargas_ini.name)
            st.success(f"✅ {up_cargas_ini.name} guardado.")
    with col_or3:
        up_cargas_fin = st.file_uploader("Subir CSV cargas Año Final (ej. cargascto2032.csv)", type=["csv"], key="up_c_fin")
        if up_cargas_fin is not None:
            guardar_archivo_subido(up_cargas_fin, up_cargas_fin.name)
            st.success(f"✅ {up_cargas_fin.name} guardado.")

    datos = {
        "sec2_intro": sec2_intro,
        "vida_util": vida_util,
        "tipo_fuente": tipo_fuente,
        "tipo_panel_etiqueta": tipo_panel_etiqueta,
        "prot_item": prot_item,
        "prot_desc": prot_desc,
        "prot_cant": prot_cant,
        "inv_items": inv_items,
        "sec2_cierre": sec2_cierre,
        "incluir_geoespacial": incluir_geoespacial,
        "sec3_intro": sec3_intro,
        "texto_equipos": texto_equipos,
        "sec3_or_texto": sec3_or_texto,
        "usar_equivalente_png": modo_equivalente.startswith("Imagen")
    }
    st.session_state["datos_sec_2_3"] = datos
    return datos
