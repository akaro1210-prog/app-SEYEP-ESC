import streamlit as st
import pandas as pd
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
    st.markdown("### 📌 1. Datos Generales del Proyecto y Ubicación")
    st.caption("Variables de identificación, fechas, coordenadas geográficas y horizonte temporal de análisis.")

    col1, col2, col3 = st.columns(3)
    with col1:
        nombre_proyecto = st.text_input(
            "Nombre del Proyecto (\\nombreProyecto):",
            value=obtener_val("nombreProyecto", "Perla Sinú 5"),
            key=f"esc_v_nom_{ver}",
            help="%nombre del proyecto"
        )
        capacidad_mw = st.text_input(
            "Capacidad del Proyecto (\\capacidadMW):",
            value=obtener_val("capacidadMW", "990kW"),
            key=f"esc_v_cap_{ver}",
            help="%Capacidad del proyecto (ej: 990kW o 1MW)"
        )
        mes_entrega = st.text_input(
            "Mes y Año Entrega Informe (\\mesentregainformemasyear):",
            value=obtener_val("mesentregainformemasyear", "Julio, 2026"),
            key=f"esc_v_mes_{ver}",
            help="%Mes y año entrega del informe"
        )
        fecha_entrada = st.text_input(
            "Fecha Entrada en Operación FPO (\\FechaEntrada):",
            value=obtener_val("FechaEntrada", "febrero del 2027"),
            key=f"esc_v_fent_{ver}",
            help="%Fecha entrada en operación"
        )

    with col2:
        ubicacion = st.text_input(
            "Ubicación del Proyecto (\\ubicacion):",
            value=obtener_val("ubicacion", "Montería, entre los corregimientos Aguas negras y Los Venados"),
            key=f"esc_v_ubi_{ver}",
            help="%Ubicación del proyecto"
        )
        latitud = st.text_input(
            "Latitud Coordenadas (\\Latitud):",
            value=obtener_val("Latitud", "8.809128°"),
            key=f"esc_v_lat_{ver}",
            help="%Latitud"
        )
        longitud = st.text_input(
            "Longitud Coordenadas (\\Longitud):",
            value=obtener_val("Longitud", "-75.801456°"),
            key=f"esc_v_lon_{ver}",
            help="%Longitud"
        )

    with col3:
        year_inicial = st.text_input(
            "Año Inicial de Estudio (\\YearInicial):",
            value=obtener_val("YearInicial", "2027"),
            key=f"esc_v_yi_{ver}",
            help="%Año inicial de estudio"
        )
        year_final = st.text_input(
            "Año Final de Estudio (\\YearFinal):",
            value=obtener_val("YearFinal", "2030"),
            key=f"esc_v_yf_{ver}",
            help="%Año final de estudio"
        )
        norma_cno = st.text_input(
            "Versión Acuerdo CNO (\\normaCNO):",
            value=obtener_val("normaCNO", "2233"),
            key=f"esc_v_norma_cno_{ver}",
            help="Número del Acuerdo CNO aplicable al estudio (por defecto 2233). Si se modifica por una norma futura, se actualizará automáticamente en todo el documento."
        )

    st.markdown("---")
    st.markdown("### 🔌 2. Red Eléctrica y Operador de Red (OR)")
    st.caption("Variables de la subestación, circuito, niveles de tensión y elementos de protección aguas arriba.")

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        operador_red = st.text_input(
            "Nombre del OR (\\OR):",
            value=obtener_val("OR", "Caribemar de la Costa S.A.S. E.S.P. (AFINIA)"),
            key=f"esc_v_or_{ver}",
            help="%Nombre del OR"
        )
        cto = st.text_input(
            "Circuito de Conexión (\\CTO):",
            value=obtener_val("CTO", "Nueva Montería 2"),
            key=f"esc_v_cto_{ver}",
            help="%Circuito de conexión"
        )
        ssee = st.text_input(
            "Subestación (\\SSEE):",
            value=obtener_val("SSEE", "Nueva Montería"),
            key=f"esc_v_ssee_{ver}",
            help="%Subestación"
        )

    with col_r2:
        nt = st.text_input(
            "Nivel de Tensión (\\NT):",
            value=obtener_val("NT", "13.8kV"),
            key=f"esc_v_nt_{ver}",
            help="%Nivel de tensión"
        )
        nodo = st.text_input(
            "Nodo de Conexión (\\nodo):",
            value=obtener_val("nodo", "1051545"),
            key=f"esc_v_nodo_{ver}",
            help="%Nodo de conexión"
        )
        elemento_proteccion = st.text_input(
            "Elemento de Protección (\\elementoProteccion):",
            value=obtener_val("elementoProteccion", "R3014"),
            key=f"esc_v_elpr_{ver}",
            help="%Elemento de protección"
        )

    with col_r3:
        reco_cto = st.text_input(
            "Protección OR Aguas Arriba (\\recoCTO):",
            value=obtener_val("recoCTO", "R-3014"),
            key=f"esc_v_rcto_{ver}",
            help="%Protección del OR aguas arriba"
        )
        tipo_proteccion = st.text_input(
            "Tipo Elemento Protección (\\tipoproteccion):",
            value=obtener_val("tipoproteccion", "Reconectador"),
            key=f"esc_v_tprot_{ver}",
            help="%Tipo de elemento que protege aguas arriba"
        )
        reco_cabecera = st.text_input(
            "Protección Cabecera OR (\\recocabecera):",
            value=obtener_val("recocabecera", "Nueva Monteria 2"),
            key=f"esc_v_rcab_{ver}",
            help="%Protección del OR cabecera si tiene dos elementos"
        )

    st.markdown("---")
    st.markdown("### 🔋 3. Paneles Fotovoltaicos del Proyecto")
    st.caption("Especificaciones técnicas de los módulos solares fotovoltaicos instalados.")

    col_pan1, col_pan2, col_pan3 = st.columns(3)
    with col_pan1:
        referencia_panel = st.text_input(
            "Referencia Paneles (\\referenciaPanel):",
            value=obtener_val("referenciaPanel", "LR8-66HGD 595~625M"),
            key=f"esc_v_rpan_{ver}",
            help="%Referencia paneles"
        )
    with col_pan2:
        potencia_panel = st.text_input(
            "Potencia Paneles (\\potenciaPanel):",
            value=obtener_val("potenciaPanel", "615 Wp"),
            key=f"esc_v_ppan_{ver}",
            help="%Potencia paneles"
        )
    with col_pan3:
        cantidad_panel = st.text_input(
            "Cantidad Paneles (\\cantidadPanel):",
            value=obtener_val("cantidadPanel", "2088"),
            key=f"esc_v_cpan_{ver}",
            help="%Cantidad paneles"
        )

    st.markdown("---")
    st.markdown("### ⚡ 4. Horas de Despacho, Pérdidas y Parámetros del Sistema")
    st.caption("Variables horarias de simulación, pérdidas máximas y capacidades de red.")

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        cp_hora = st.text_input(
            "Hora Carga Pura (\\CP):",
            value=obtener_val("CP", "23:00"),
            key=f"esc_v_cp_{ver}",
            help="%Hora Carga Pura"
        )
        dmi_hora = st.text_input(
            "Hora Demanda Mínima (\\Dmi):",
            value=obtener_val("Dmi", "11:00"),
            key=f"esc_v_dmi_{ver}",
            help="%Hora demanda mínima"
        )
    with col_s2:
        dmx_hora = st.text_input(
            "Hora Demanda Máxima (\\DMx):",
            value=obtener_val("DMx", "15:00"),
            key=f"esc_v_dmx_{ver}",
            help="%Hora demanda máxima"
        )
        escenario_max_perd = st.text_input(
            "Escenario Máx. Pérdidas (\\escenariomaxPerdidas):",
            value=obtener_val("escenariomaxPerdidas", "CP del 2030"),
            key=f"esc_v_escmaxp_{ver}",
            help="%Escenario donde se dan las perdidas mas altas"
        )
    with col_s3:
        perdidas_maximas = st.text_input(
            "Pérdidas Más Altas (\\perdidasmaximas):",
            value=obtener_val("perdidasmaximas", "410 kW"),
            key=f"esc_v_pmax_{ver}",
            help="%Pérdidas más altas del circuito"
        )
        generacion_aprobada = st.text_input(
            "Generación Aprobada en SE (\\generacionaprobada):",
            value=obtener_val("generacionaprobada", "4950kW"),
            key=f"esc_v_gena_{ver}",
            help="%Generación ya aprobada en la SE"
        )
    with col_s4:
        potencia_minima = st.text_input(
            "Demanda Mínima Circuito (\\potenciaminima):",
            value=obtener_val("potenciaminima", "3400kW"),
            key=f"esc_v_potmin_{ver}",
            help="%Demanda mínima del circuito"
        )

    st.markdown("---")
    st.markdown("### ☀️ 5. Inversores Fotovoltaicos del Proyecto (Módulo Exclusivo de Edición)")
    st.info(
        "💡 **Edición Centralizada de Inversores:** Aquí se configuran, agregan o eliminan todas las referencias de inversores del proyecto. "
        "En la pestaña **7. Proyecto y Equipos** se muestran de manera sincronizada en modo **solo lectura** para evitar discrepancias."
    )

    if "inv_items_esc" not in st.session_state:
        inv1_ref = obtener_val("refInversoruno", "Inversor 330 kW On-Grid.")
        inv1_mod = obtener_val("Inversoruno", "Huawei Sun2000 330KTL-H1")
        inv1_cant = obtener_val("cantidadInversoruno", "3 Und.")
        st.session_state["inv_items_esc"] = [
            {"ref": inv1_ref, "modelo": inv1_mod, "cantidad": inv1_cant}
        ]
        if "inv_items" in st.session_state and isinstance(st.session_state["inv_items"], list) and len(st.session_state["inv_items"]) > 0:
            st.session_state["inv_items_esc"] = [dict(x) for x in st.session_state["inv_items"]]

    palabras_num = ["uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"]
    inversores_actuales = st.session_state.get("inv_items_esc", [])
    if not inversores_actuales:
        inversores_actuales = [{"ref": "Inversor 330 kW On-Grid.", "modelo": "Huawei Sun2000 330KTL-H1", "cantidad": "3 Und."}]

    nuevos_inv_items = []
    for idx, inv in enumerate(inversores_actuales):
        pal = palabras_num[idx] if idx < len(palabras_num) else f"_{idx+1}"
        num_mostrar = idx + 1
        st.markdown(f"**Inversor {num_mostrar}:**")
        if len(inversores_actuales) > 1:
            ci1, ci2, ci3, ci4 = st.columns([4, 4, 3, 1])
        else:
            ci1, ci2, ci3 = st.columns([4, 4, 3])

        with ci1:
            r_val = st.text_input(
                f"Referencia Inversor {num_mostrar} (\\refInversor{pal}):",
                value=inv.get("ref", f"Inversor {num_mostrar}"),
                key=f"esc_v_rinv_{idx}_{ver}",
                help=f"%Referencia inversor {num_mostrar}"
            )
        with ci2:
            m_val = st.text_input(
                f"Modelo Inversor {num_mostrar} (\\Inversor{pal}):",
                value=inv.get("modelo", f"Modelo {num_mostrar}"),
                key=f"esc_v_inv_{idx}_{ver}",
                help=f"%Inversor {num_mostrar}"
            )
        with ci3:
            c_val = st.text_input(
                f"Cantidad Inversor {num_mostrar} (\\cantidadInversor{pal}):",
                value=inv.get("cantidad", "1 Und."),
                key=f"esc_v_cinv_{idx}_{ver}",
                help=f"%Cantidad inversor {num_mostrar}"
            )
        if len(inversores_actuales) > 1:
            with ci4:
                st.write("")
                st.write("")
                if st.button("🗑️", key=f"btn_del_inv_{idx}_{ver}", help=f"Eliminar Inversor {num_mostrar}"):
                    st.session_state["inv_items_esc"].pop(idx)
                    st.session_state["inv_items"] = list(st.session_state["inv_items_esc"])
                    st.rerun()
        nuevos_inv_items.append({"ref": r_val, "modelo": m_val, "cantidad": c_val})

    st.session_state["inv_items_esc"] = nuevos_inv_items
    st.session_state["inv_items"] = nuevos_inv_items

    if st.button("➕ Agregar Inversor", key=f"btn_add_inv_esc_{ver}", type="secondary"):
        n_num = len(nuevos_inv_items) + 1
        pal_sig = palabras_num[len(nuevos_inv_items)] if len(nuevos_inv_items) < len(palabras_num) else f"_{n_num}"
        st.session_state["inv_items_esc"].append({
            "ref": f"Inversor {pal_sig} On-Grid.",
            "modelo": f"Inversor {n_num}",
            "cantidad": "1 Und."
        })
        st.session_state["inv_items"] = list(st.session_state["inv_items_esc"])
        st.rerun()

    ref_inversor_uno = nuevos_inv_items[0]["ref"] if nuevos_inv_items else "Inversor 330 kW On-Grid."
    inversor_uno = nuevos_inv_items[0]["modelo"] if nuevos_inv_items else "Huawei Sun2000 330KTL-H1"
    cantidad_inversor_uno = nuevos_inv_items[0]["cantidad"] if nuevos_inv_items else "3 Und."

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
        "CP": cp_hora,
        "Dmi": dmi_hora,
        "DMx": dmx_hora,
        "escenariomaxPerdidas": escenario_max_perd,
        "perdidasmaximas": perdidas_maximas,
        "generacionaprobada": generacion_aprobada,
        "potenciaminima": potencia_minima,
        "normaCNO": norma_cno,
        "refInversoruno": ref_inversor_uno,
        "Inversoruno": inversor_uno,
        "cantidadInversoruno": cantidad_inversor_uno,
        "inv_items": nuevos_inv_items,
    }

    for idx, item in enumerate(nuevos_inv_items):
        pal = palabras_num[idx] if idx < len(palabras_num) else f"_{idx+1}"
        config_vars[f"refInversor{pal}"] = item["ref"]
        config_vars[f"Inversor{pal}"] = item["modelo"]
        config_vars[f"cantidadInversor{pal}"] = item["cantidad"]
        config_vars[f"refInversor{idx+1}"] = item["ref"]
        config_vars[f"Inversor{idx+1}"] = item["modelo"]
        config_vars[f"cantidadInversor{idx+1}"] = item["cantidad"]

    # Sincronizar en session_state para acceso universal en todas las pestañas
    for k, v in config_vars.items():
        if k != "inv_items":
            st.session_state[k] = v

    # --- Resumen y Verificación de las 31 Variables de LaTeX ---
    with st.expander("📋 Ver Lista Completa de las 31 Variables LaTeX del Proyecto (% ---------- Variables del proyecto ----------)", expanded=True):
        st.caption("Verificación de correspondencia exacta 1:1 con el fragmento de código LaTeX:")
        
        datos_tabla_latex = [
            {"No.": 1, "Comando LaTeX": "\\mesentregainformemasyear", "Concepto / Comentario": "Mes y año entrega del informe", "Valor Actual": mes_entrega},
            {"No.": 2, "Comando LaTeX": "\\nombreProyecto", "Concepto / Comentario": "Nombre del proyecto", "Valor Actual": nombre_proyecto},
            {"No.": 3, "Comando LaTeX": "\\capacidadMW", "Concepto / Comentario": "Capacidad del proyecto", "Valor Actual": capacidad_mw},
            {"No.": 4, "Comando LaTeX": "\\OR", "Concepto / Comentario": "Nombre del OR", "Valor Actual": operador_red},
            {"No.": 5, "Comando LaTeX": "\\FechaEntrada", "Concepto / Comentario": "Fecha entrada en operación (FPO)", "Valor Actual": fecha_entrada},
            {"No.": 6, "Comando LaTeX": "\\Latitud", "Concepto / Comentario": "Latitud geográfica", "Valor Actual": latitud},
            {"No.": 7, "Comando LaTeX": "\\Longitud", "Concepto / Comentario": "Longitud geográfica", "Valor Actual": longitud},
            {"No.": 8, "Comando LaTeX": "\\YearInicial", "Concepto / Comentario": "Año inicial de estudio", "Valor Actual": year_inicial},
            {"No.": 9, "Comando LaTeX": "\\YearFinal", "Concepto / Comentario": "Año final de estudio", "Valor Actual": year_final},
            {"No.": 10, "Comando LaTeX": "\\CTO", "Concepto / Comentario": "Circuito de conexión", "Valor Actual": cto},
            {"No.": 11, "Comando LaTeX": "\\SSEE", "Concepto / Comentario": "Subestación", "Valor Actual": ssee},
            {"No.": 12, "Comando LaTeX": "\\NT", "Concepto / Comentario": "Nivel de tensión", "Valor Actual": nt},
            {"No.": 13, "Comando LaTeX": "\\nodo", "Concepto / Comentario": "Nodo de conexión", "Valor Actual": nodo},
            {"No.": 14, "Comando LaTeX": "\\elementoProteccion", "Concepto / Comentario": "Elemento de protección", "Valor Actual": elemento_proteccion},
            {"No.": 15, "Comando LaTeX": "\\referenciaPanel", "Concepto / Comentario": "Referencia paneles solares", "Valor Actual": referencia_panel},
            {"No.": 16, "Comando LaTeX": "\\potenciaPanel", "Concepto / Comentario": "Potencia paneles solares", "Valor Actual": potencia_panel},
            {"No.": 17, "Comando LaTeX": "\\cantidadPanel", "Concepto / Comentario": "Cantidad paneles solares", "Valor Actual": cantidad_panel},
            {"No.": 18, "Comando LaTeX": "\\ubicacion", "Concepto / Comentario": "Ubicación del proyecto", "Valor Actual": ubicacion},
            {"No.": 19, "Comando LaTeX": "\\CP", "Concepto / Comentario": "Hora Demanda de Carga Pura", "Valor Actual": cp_hora},
            {"No.": 20, "Comando LaTeX": "\\Dmi", "Concepto / Comentario": "Hora Demanda Mínima", "Valor Actual": dmi_hora},
            {"No.": 21, "Comando LaTeX": "\\DMx", "Concepto / Comentario": "Hora Demanda Máxima", "Valor Actual": dmx_hora},
            {"No.": 22, "Comando LaTeX": "\\escenariomaxPerdidas", "Concepto / Comentario": "Escenario pérdidas más altas", "Valor Actual": escenario_max_perd},
            {"No.": 23, "Comando LaTeX": "\\perdidasmaximas", "Concepto / Comentario": "Pérdidas más altas del circuito", "Valor Actual": perdidas_maximas},
            {"No.": 24, "Comando LaTeX": "\\refInversoruno", "Concepto / Comentario": "Referencia inversor 1", "Valor Actual": ref_inversor_uno},
            {"No.": 25, "Comando LaTeX": "\\Inversoruno", "Concepto / Comentario": "Modelo inversor 1", "Valor Actual": inversor_uno},
            {"No.": 26, "Comando LaTeX": "\\cantidadInversoruno", "Concepto / Comentario": "Cantidad inversor 1", "Valor Actual": cantidad_inversor_uno},
            {"No.": 27, "Comando LaTeX": "\\generacionaprobada", "Concepto / Comentario": "Generación ya aprobada en la SE", "Valor Actual": generacion_aprobada},
            {"No.": 28, "Comando LaTeX": "\\potenciaminima", "Concepto / Comentario": "Demanda mínima del circuito", "Valor Actual": potencia_minima},
            {"No.": 29, "Comando LaTeX": "\\recoCTO", "Concepto / Comentario": "Protección del OR aguas arriba", "Valor Actual": reco_cto},
            {"No.": 30, "Comando LaTeX": "\\tipoproteccion", "Concepto / Comentario": "Tipo de elemento protege aguas arriba", "Valor Actual": tipo_proteccion},
            {"No.": 31, "Comando LaTeX": "\\recocabecera", "Concepto / Comentario": "Protección OR cabecera si tiene 2 elementos", "Valor Actual": reco_cabecera},
            {"No.": 32, "Comando LaTeX": "\\normaCNO", "Concepto / Comentario": "Versión del Acuerdo CNO aplicable", "Valor Actual": norma_cno},
        ]
        df_vars_summary = pd.DataFrame(datos_tabla_latex)
        st.dataframe(df_vars_summary, use_container_width=True, hide_index=True)

    st.markdown("---")
    render_resumen_estructura_documento()

    st.session_state["config_vars"] = config_vars
    st.session_state["tipo_estudio"] = tipo_estudio_clave
    st.session_state["es_autogenerador"] = es_autogenerador
    st.session_state["normaCNO"] = norma_cno
    return config_vars
