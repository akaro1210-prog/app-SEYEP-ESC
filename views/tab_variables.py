import streamlit as st
import pandas as pd
from project_manager import obtener_val, obtener_ver
from cno_normativa import RANGOS_POTENCIA_CNO, obtener_datos_tablas_cno


def render():
    ver = obtener_ver()
    st.subheader("📋 Variables Globales y Rango de Potencia (Acuerdo CNO 2233)")
    st.write(
        "Define las variables principales del estudio y el rango de potencia del proyecto. "
        "Al cambiar el rango de potencia, el sistema actualiza automáticamente los **títulos y contenidos de las Tablas 2, 3 y 6** "
        "así como las protecciones mínimas y ajustes recomendados según el **Acuerdo CNO 2233 de 2026**."
    )

    norma_cno_val = str(obtener_val("normaCNO", "2233")).strip() or "2233"

    # =========================================================================
    # SELECTOR DE RANGO DE POTENCIA CNO
    # =========================================================================
    contenedor_rango = st.container(border=True)
    with contenedor_rango:
        st.markdown(f"### ⚡ Rango de Potencia del Proyecto (Lineamientos CNO {norma_cno_val})")
        st.caption(
            "Selecciona el rango de capacidad instalada de generación. "
            "Cada rango determina las funciones de protección mínimas exigidas en el PC/UG, los umbrales de ajuste y los títulos formales de las tablas:"
        )

        opciones_rango = list(RANGOS_POTENCIA_CNO.keys())
        nombres_rango = [RANGOS_POTENCIA_CNO[k]["nombre"] for k in opciones_rango]

        # Determinar índice por defecto (por defecto P_025_TO_1 para proyectos típicos de ~900 kW como Arbóreo)
        val_guardado = obtener_val("rango_potencia_cno", "P_025_TO_1")
        idx_default = opciones_rango.index(val_guardado) if val_guardado in opciones_rango else 1

        rango_sel_nombre = st.radio(
            "Selecciona el rango de potencia aplicable al informe EACP:",
            options=nombres_rango,
            index=idx_default,
            key=f"rad_rango_potencia_{ver}",
            help="Selecciona el rango según la capacidad nominal del proyecto. Los títulos y contenidos de las Tablas 2, 3 y 6 cambiarán automáticamente."
        )

        # Mapear de nombre a clave
        idx_sel = nombres_rango.index(rango_sel_nombre)
        clave_rango_actual = opciones_rango[idx_sel]
        info_rango = RANGOS_POTENCIA_CNO[clave_rango_actual]

        # Detectar si cambió el rango de potencia respecto a la sesión anterior
        clave_anterior = st.session_state.get("rango_potencia_cno_anterior", None)
        if clave_anterior is None:
            # Inicialización inicial si no existían DataFrames en sesión
            st.session_state["rango_potencia_cno_anterior"] = clave_rango_actual
            datos_cno = obtener_datos_tablas_cno(clave_rango_actual, version_cno=norma_cno_val)
            if "df_funciones_prot" not in st.session_state:
                st.session_state["df_funciones_prot"] = pd.DataFrame(datos_cno["df_funciones_prot"])
                st.session_state["df_ajustes_cno"] = pd.DataFrame(datos_cno["df_ajustes_cno"])
                st.session_state["obs_cno_1"] = datos_cno["obs_cno_1"]
                st.session_state["obs_cno_2"] = datos_cno["obs_cno_2"]
            st.session_state["tabla_funciones_caption"] = datos_cno["tabla_funciones_caption"]
            st.session_state["tabla_ajustes_caption"] = datos_cno["tabla_ajustes_caption"]
            st.session_state["tabla_resumen_caption"] = datos_cno["tabla_resumen_caption"]
        elif clave_anterior != clave_rango_actual:
            # ¡El usuario cambió el selector de rango! Actualizar tablas y títulos automáticamente
            datos_cno = obtener_datos_tablas_cno(clave_rango_actual, version_cno=norma_cno_val)
            st.session_state["df_funciones_prot"] = pd.DataFrame(datos_cno["df_funciones_prot"])
            st.session_state["df_ajustes_cno"] = pd.DataFrame(datos_cno["df_ajustes_cno"])
            st.session_state["obs_cno_1"] = datos_cno["obs_cno_1"]
            st.session_state["obs_cno_2"] = datos_cno["obs_cno_2"]
            st.session_state["tabla_funciones_caption"] = datos_cno["tabla_funciones_caption"]
            st.session_state["tabla_ajustes_caption"] = datos_cno["tabla_ajustes_caption"]
            st.session_state["tabla_resumen_caption"] = datos_cno["tabla_resumen_caption"]
            st.session_state["rango_potencia_cno_anterior"] = clave_rango_actual
            st.toast(
                f"✅ Rango {clave_rango_actual} activado: Títulos de Tablas 2, 3 y 6 y tablas normativas actualizados a {info_rango['tabla_funciones_num']} y {info_rango['tabla_ajustes_num']}",
                icon="⚡"
            )

        # Tarjeta informativa del rango activo
        c_inf1, c_inf2 = st.columns([2, 1])
        with c_inf1:
            st.info(
                f"📊 **Normativa CNO {norma_cno_val} Activa:** **{info_rango['tabla_funciones_num']}** (Funciones mínimas) y "
                f"**{info_rango['tabla_ajustes_num']}** (Ajustes recomendados).\n\n"
                f"• **Título Tabla 2:** {info_rango['tabla_funciones_caption']}\n\n"
                f"• **Título Tabla 3:** {info_rango['tabla_ajustes_caption']}\n\n"
                f"• **Título Tabla 6:** {info_rango['tabla_resumen_caption']}\n\n"
                f"• **Equipo de corte:** {info_rango['equipo_corte']}\n"
                f"• **Esquema Anti-Isla:** {info_rango['anti_isla_respaldo']}"
            )
        with c_inf2:
            st.markdown(
                f"<div style='background: #0f172a; padding: 12px; border-radius: 8px; border: 1px solid #1e293b;'>"
                f"<span style='color: #38bdf8; font-weight: bold; font-size: 0.85rem;'>Rango Seleccionado:</span><br/>"
                f"<span style='color: #10b981; font-weight: bold; font-size: 1.05rem;'>{clave_rango_actual}</span><br/>"
                f"<span style='color: #94a3b8; font-size: 0.75rem;'>{info_rango['descripcion']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("### 📌 Variables Principales del Proyecto")
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre_proyecto = st.text_input("Nombre del Proyecto (\\nombreProyecto):", value=obtener_val("nombreProyecto", "Arboreo"), key=f"v_nom_{ver}")
        capacidad_mw = st.text_input("Capacidad del Proyecto (\\capacidadMW):", value=obtener_val("capacidadMW", "900kW"), key=f"v_cap_{ver}")
        mes_entrega = st.text_input("Mes y Año de Entrega Portada (\\mesentregainformemasyear):", value=obtener_val("mesentregainformemasyear", "Septiembre, 2026"), key=f"v_mes_{ver}")
        operador_red = st.text_input("Operador de Red (\\OR):", value=obtener_val("OR", "EPM"), key=f"v_or_{ver}")
        fecha_entrada = st.text_input("Fecha Entrada en Operación (\\FechaEntrada):", value=obtener_val("FechaEntrada", "marzo del 2027"), key=f"v_fent_{ver}")
        norma_cno = st.text_input(
            "Versión Acuerdo CNO (\\normaCNO):",
            value=norma_cno_val,
            key=f"v_cno_{ver}",
            help="Número o código del Acuerdo CNO aplicable (por defecto 2233). Si se modifica por una norma futura, se actualizará automáticamente en todo el documento."
        )
    with col2:
        cto = st.text_input("Circuito de Conexión (\\CTO):", value=obtener_val("CTO", "211-11"), key=f"v_cto_{ver}")
        ssee = st.text_input("Subestación (\\SSEE):", value=obtener_val("SSEE", "Doradal_13.2"), key=f"v_ssee_{ver}")
        nt = st.text_input("Nivel de Tensión (\\NT):", value=obtener_val("NT", "13.2kV"), key=f"v_nt_{ver}")
        nodo = st.text_input("Nodo de Conexión (\\nodo):", value=obtener_val("nodo", "906750"), key=f"v_nodo_{ver}")
        ubicacion = st.text_input("Ubicación (\\ubicacion):", value=obtener_val("ubicacion", "En predio del hotel Arboreo, Doradal, Antioquia"), key=f"v_ubi_{ver}")
    with col3:
        reco_cabecera = st.text_input("Reconectador de Cabecera OR (\\recocabecera):", value=obtener_val("recocabecera", "211-11"), key=f"v_rcab_{ver}")
        reco_cto = st.text_input("Protección Aguas Arriba OR (\\recoCTO):", value=obtener_val("recoCTO", "211-11"), key=f"v_rcto_{ver}")
        tipo_proteccion = st.text_input("Tipo de Elemento Protección OR (\\tipoproteccion):", value=obtener_val("tipoproteccion", "Reconectador"), key=f"v_tprot_{ver}")
        year_inicial = st.text_input("Año Inicial de Estudio (\\YearInicial):", value=obtener_val("YearInicial", "2027"), key=f"v_yi_{ver}")
        year_final = st.text_input("Año Final de Estudio (\\YearFinal):", value=obtener_val("YearFinal", "2032"), key=f"v_yf_{ver}")

    with st.expander("⚙️ Otras variables opcionales del encabezado LaTeX"):
        c_o1, c_o2, c_o3 = st.columns(3)
        with c_o1:
            latitud = st.text_input("Latitud (\\Latitud):", value=obtener_val("Latitud", '5°53\'49.8"N'), key=f"v_lat_{ver}")
            longitud = st.text_input("Longitud (\\Longitud):", value=obtener_val("Longitud", '74°45\'12.9"W'), key=f"v_lon_{ver}")
            elemento_proteccion = st.text_input("Elemento Protección (\\elementoProteccion):", value=obtener_val("elementoProteccion", "211-11"), key=f"v_elpr_{ver}")
        with c_o2:
            referencia_panel = st.text_input("Referencia Paneles (\\referenciaPanel):", value=obtener_val("referenciaPanel", "JAM66D45 625 LB"), key=f"v_rpan_{ver}")
            potencia_panel = st.text_input("Potencia Paneles (\\potenciaPanel):", value=obtener_val("potenciaPanel", "625 Wp"), key=f"v_ppan_{ver}")
            cantidad_panel = st.text_input("Cantidad Paneles (\\cantidadPanel):", value=obtener_val("cantidadPanel", "1760"), key=f"v_cpan_{ver}")
        with c_o3:
            ref_inversor_uno = st.text_input("Referencia Inversor 1 (\\refInversoruno):", value=obtener_val("refInversoruno", "Inversor 150 kW On-Grid."), key=f"v_rinv_{ver}")
            inversor_uno = st.text_input("Modelo Inversor 1 (\\Inversoruno):", value=obtener_val("Inversoruno", "Growat MAX 150KTL3-X2MV"), key=f"v_inv_{ver}")
            cantidad_inversor_uno = st.text_input("Cantidad Inversor 1 (\\cantidadInversoruno):", value=obtener_val("cantidadInversoruno", "6 Und."), key=f"v_cinv_{ver}")
            generacion_aprobada = st.text_input("Generación Aprobada (\\generacionaprobada):", value=obtener_val("generacionaprobada", "900kW"), key=f"v_gena_{ver}")

    config_vars = {
        "rango_potencia_cno": clave_rango_actual,
        "rango_nombre": info_rango["nombre"],
        "rango_desc": info_rango["descripcion"],
        "tabla_funciones_num": info_rango["tabla_funciones_num"],
        "tabla_ajustes_num": info_rango["tabla_ajustes_num"],
        "tabla_funciones_caption": st.session_state.get("tabla_funciones_caption", info_rango["tabla_funciones_caption"]),
        "tabla_ajustes_caption": st.session_state.get("tabla_ajustes_caption", info_rango["tabla_ajustes_caption"]),
        "tabla_resumen_caption": st.session_state.get("tabla_resumen_caption", info_rango["tabla_resumen_caption"]),
        "mesentregainformemasyear": mes_entrega,
        "nombreProyecto": nombre_proyecto,
        "capacidadMW": capacidad_mw,
        "OR": operador_red,
        "FechaEntrada": fecha_entrada,
        "Latitud": latitud,
        "Longitud": longitud,
        "YearInicial": year_inicial,
        "YearFinal": year_final,
        "CTO": cto,
        "SSEE": ssee,
        "NT": nt,
        "nodo": nodo,
        "elementoProteccion": elemento_proteccion,
        "referenciaPanel": referencia_panel,
        "potenciaPanel": potencia_panel,
        "cantidadPanel": cantidad_panel,
        "ubicacion": ubicacion,
        "refInversoruno": ref_inversor_uno,
        "Inversoruno": inversor_uno,
        "cantidadInversoruno": cantidad_inversor_uno,
        "generacionaprobada": generacion_aprobada,
        "recoCTO": reco_cto,
        "tipoproteccion": tipo_proteccion,
        "recocabecera": reco_cabecera,
        "normaCNO": norma_cno,
    }
    st.session_state["config_vars"] = config_vars
    st.session_state["rango_potencia_cno"] = clave_rango_actual
    st.session_state["normaCNO"] = norma_cno
    return config_vars
