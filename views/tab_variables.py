import streamlit as st
from project_manager import obtener_val, obtener_ver
from secciones_manager import render_resumen_estructura_documento

def render():
    ver = obtener_ver()
    st.subheader("📋 Variables Globales y Régimen del Proyecto (ESC)")
    st.write(
        "Define el régimen del estudio (**Generación Distribuida** o **Autogenerador**) y las variables principales. "
        "Todo el documento (portada, introducción regulatoria CREG 174, textos de análisis, tablas y conclusiones) "
        "se adaptará automáticamente a la opción seleccionada."
    )

    # --- Selector Principal: GD vs Autogenerador ---
    contenedor_regimen = st.container(border=True)
    with contenedor_regimen:
        st.markdown("### 🔘 Régimen del Proyecto para el Estudio de Conexión")
        
        # Recuperar valor previo si existe
        val_previo = obtener_val("tipo_estudio", "Generación Distribuida (GD)")
        idx_default = 1 if "autogenerador" in str(val_previo).lower() else 0

        opciones_tipo = ["Generación Distribuida (GD)", "Autogenerador"]
        tipo_estudio_sel = st.radio(
            "Selecciona el régimen de conexión aplicable al informe:",
            options=opciones_tipo,
            index=idx_default,
            horizontal=True,
            key=f"tipo_estudio_radio_{ver}",
            help="Selecciona si el estudio técnico corresponde a un Generador Distribuido (GD) o a un Autogenerador."
        )

        es_autogenerador = ("autogenerador" in tipo_estudio_sel.lower())
        tipo_estudio_clave = "Autogenerador" if es_autogenerador else "GD"
        etiqueta_desc = "Autogeneración (Autogenerador)" if es_autogenerador else "Generación Distribuida (GD)"
        titulo_portada = "AUTOGENERACIÓN" if es_autogenerador else "GENERACIÓN DISTRIBUIDA"

        if es_autogenerador:
            st.success(
                f"🔄 **Modo Activo: Autogenerador**. Todo el informe se compilará con terminología de **Autogenerador / Autogeneración**, "
                f"incluyendo la Portada ('ESTUDIO DE CONEXIÓN SIMPLIFICADO {titulo_portada} SOLAR FV'), el objetivo CREG 174 de 2021, "
                f"las tablas de coordenadas, inversores, protecciones y conclusiones técnicas."
            )
        else:
            st.info(
                f"⚡ **Modo Activo: Generación Distribuida (GD)**. Todo el informe se compilará con terminología de **GD / Generadores Distribuidos**, "
                f"incluyendo la Portada ('ESTUDIO DE CONEXIÓN SIMPLIFICADO {titulo_portada} SOLAR FV'), el objetivo CREG 174 de 2021, "
                f"las tablas y conclusiones técnicas."
            )

    st.markdown("---")
    st.markdown("### 📌 Variables Principales del Proyecto")

    col1, col2, col3 = st.columns(3)
    with col1:
        nombre_proyecto = st.text_input(
            "Nombre del Proyecto (\\nombreProyecto):",
            value=obtener_val("nombreProyecto", "Arboreo"),
            key=f"esc_v_nom_{ver}"
        )
        capacidad_mw = st.text_input(
            "Capacidad del Proyecto (\\capacidadMW):",
            value=obtener_val("capacidadMW", "900kW"),
            key=f"esc_v_cap_{ver}"
        )
        mes_entrega = st.text_input(
            "Mes y Año de Entrega Portada (\\mesentregainformemasyear):",
            value=obtener_val("mesentregainformemasyear", "Septiembre, 2026"),
            key=f"esc_v_mes_{ver}"
        )
        operador_red = st.text_input(
            "Operador de Red (\\OR):",
            value=obtener_val("OR", "EPM"),
            key=f"esc_v_or_{ver}"
        )
        fecha_entrada = st.text_input(
            "Fecha Entrada en Operación FPO (\\FechaEntrada):",
            value=obtener_val("FechaEntrada", "marzo del 2027"),
            key=f"esc_v_fent_{ver}"
        )

    with col2:
        cto = st.text_input(
            "Circuito de Conexión (\\CTO):",
            value=obtener_val("CTO", "211-11"),
            key=f"esc_v_cto_{ver}"
        )
        ssee = st.text_input(
            "Subestación (\\SSEE):",
            value=obtener_val("SSEE", "Doradal_13.2"),
            key=f"esc_v_ssee_{ver}"
        )
        nt = st.text_input(
            "Nivel de Tensión (\\NT):",
            value=obtener_val("NT", "13.2kV"),
            key=f"esc_v_nt_{ver}"
        )
        nodo = st.text_input(
            "Nodo de Conexión (\\nodo):",
            value=obtener_val("nodo", "906750"),
            key=f"esc_v_nodo_{ver}"
        )
        ubicacion = st.text_input(
            "Ubicación (\\ubicacion):",
            value=obtener_val("ubicacion", "En predio del hotel Arboreo, Doradal, Antioquia"),
            key=f"esc_v_ubi_{ver}"
        )

    with col3:
        reco_cabecera = st.text_input(
            "Reconectador de Cabecera OR (\\recocabecera):",
            value=obtener_val("recocabecera", "211-11"),
            key=f"esc_v_rcab_{ver}"
        )
        reco_cto = st.text_input(
            "Protección Aguas Arriba OR (\\recoCTO):",
            value=obtener_val("recoCTO", "211-11"),
            key=f"esc_v_rcto_{ver}"
        )
        tipo_proteccion = st.text_input(
            "Tipo de Elemento Protección OR (\\tipoproteccion):",
            value=obtener_val("tipoproteccion", "Reconectador"),
            key=f"esc_v_tprot_{ver}"
        )
        year_inicial = st.text_input(
            "Año Inicial de Estudio (\\YearInicial):",
            value=obtener_val("YearInicial", "2027"),
            key=f"esc_v_yi_{ver}"
        )
        year_final = st.text_input(
            "Año Final de Estudio (\\YearFinal):",
            value=obtener_val("YearFinal", "2032"),
            key=f"esc_v_yf_{ver}"
        )

    with st.expander("⚙️ Parámetros Adicionales y Opcionales de Encabezado LaTeX"):
        c_o1, c_o2, c_o3 = st.columns(3)
        with c_o1:
            latitud = st.text_input("Latitud (\\Latitud):", value=obtener_val("Latitud", '5°53\'49.8"N'), key=f"esc_v_lat_{ver}")
            longitud = st.text_input("Longitud (\\Longitud):", value=obtener_val("Longitud", '74°45\'12.9"W'), key=f"esc_v_lon_{ver}")
            elemento_proteccion = st.text_input("Elemento Protección (\\elementoProteccion):", value=obtener_val("elementoProteccion", "211-11"), key=f"esc_v_elpr_{ver}")
        with c_o2:
            referencia_panel = st.text_input("Referencia Paneles (\\referenciaPanel):", value=obtener_val("referenciaPanel", "JAM66D45 625 LB"), key=f"esc_v_rpan_{ver}")
            potencia_panel = st.text_input("Potencia Paneles (\\potenciaPanel):", value=obtener_val("potenciaPanel", "625 Wp"), key=f"esc_v_ppan_{ver}")
            cantidad_panel = st.text_input("Cantidad Paneles (\\cantidadPanel):", value=obtener_val("cantidadPanel", "1760"), key=f"esc_v_cpan_{ver}")
        with c_o3:
            ref_inversor_uno = st.text_input("Referencia Inversor 1 (\\refInversoruno):", value=obtener_val("refInversoruno", "Inversor 150 kW On-Grid."), key=f"esc_v_rinv_{ver}")
            inversor_uno = st.text_input("Modelo Inversor 1 (\\Inversoruno):", value=obtener_val("Inversoruno", "Growat MAX 150KTL3-X2MV"), key=f"esc_v_inv_{ver}")
            cantidad_inversor_uno = st.text_input("Cantidad Inversor 1 (\\cantidadInversoruno):", value=obtener_val("cantidadInversoruno", "6 Und."), key=f"esc_v_cinv_{ver}")
            generacion_aprobada = st.text_input("Generación Aprobada (\\generacionaprobada):", value=obtener_val("generacionaprobada", "900kW"), key=f"esc_v_gena_{ver}")

    config_vars = {
        "tipo_estudio": tipo_estudio_clave,
        "es_autogenerador": es_autogenerador,
        "etiqueta_desc": etiqueta_desc,
        "nombreProyecto": nombre_proyecto,
        "capacidadMW": capacidad_mw,
        "mesentregainformemasyear": mes_entrega,
        "OR": operador_red,
        "FechaEntrada": fecha_entrada,
        "CTO": cto,
        "SSEE": ssee,
        "NT": nt,
        "nodo": nodo,
        "ubicacion": ubicacion,
        "recocabecera": reco_cabecera,
        "recoCTO": reco_cto,
        "tipoproteccion": tipo_proteccion,
        "YearInicial": year_inicial,
        "YearFinal": year_final,
        "Latitud": latitud,
        "Longitud": longitud,
        "elementoProteccion": elemento_proteccion,
        "referenciaPanel": referencia_panel,
        "potenciaPanel": potencia_panel,
        "cantidadPanel": cantidad_panel,
        "refInversoruno": ref_inversor_uno,
        "Inversoruno": inversor_uno,
        "cantidadInversoruno": cantidad_inversor_uno,
        "generacionaprobada": generacion_aprobada,
    }

    st.markdown("---")
    render_resumen_estructura_documento()

    st.session_state["config_vars"] = config_vars
    st.session_state["tipo_estudio"] = tipo_estudio_clave
    st.session_state["es_autogenerador"] = es_autogenerador
    return config_vars
