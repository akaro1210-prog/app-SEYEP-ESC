import streamlit as st

def cambiar_tipo_informe():
    nuevo_tipo = st.session_state.tipo_selector
    st.session_state.tipo_informe = nuevo_tipo
    
    # REQUISITO 1: Actualizar dinámicamente el contenido del informe según la elección
    from app import inicializar_secciones
    st.session_state.secciones = inicializar_secciones(nuevo_tipo)
    
    # Ajustar variables según régimen
    if nuevo_tipo == "GD":
        st.session_state.variables["demanda_interna_kw"] = 0.0
        st.session_state.variables["limite_export_kw"] = st.session_state.variables.get("capacidad_ac_kw", 990.0)
    else:
        st.session_state.variables["demanda_interna_kw"] = 350.0
        st.session_state.variables["limite_export_kw"] = 250.0

def render():
    st.subheader("1. Selección del Tipo de Informe (Régimen CREG 174)")
    st.write(
        "Seleccione si el informe técnico es para un **Generador Distribuido (GD)** "
        "o un **Autogenerador**. Al cambiar la opción, el informe actualizará automáticamente "
        "todos sus textos, normativas y supuestos técnicos."
    )

    # REQUISITO 1: Botón selector de GD vs Autogenerador
    col1, col2 = st.columns([1, 2])
    with col1:
        st.radio(
            "Tipo de Proyecto:",
            options=["GD", "Autogenerador"],
            index=0 if st.session_state.tipo_informe == "GD" else 1,
            key="tipo_selector",
            on_change=cambiar_tipo_informe,
            horizontal=True
        )

    with col2:
        if st.session_state.tipo_informe == "GD":
            st.info("⚡ **GD (Generación Distribuida):** Inyección 100% a la red del OR. Demanda interna = 0 kW. Aplica CREG 174 Art. 4.")
        else:
            st.success("🏭 **Autogenerador (AGPE):** Con autoconsumo interno y eventual entrega de excedentes. Aplica CREG 174 Art. 10/11.")

    st.markdown("---")
    st.subheader("2. Parámetros Generales del Proyecto")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.variables["nombre_proyecto"] = st.text_input(
            "Nombre del Proyecto", 
            value=st.session_state.variables.get("nombre_proyecto", "Parque Solar Sol del Llano")
        )
        st.session_state.variables["codigo_esc"] = st.text_input(
            "Código de Radicación ESC", 
            value=st.session_state.variables.get("codigo_esc", "ESC-2025-001")
        )

    with c2:
        st.session_state.variables["capacidad_ac_kw"] = st.number_input(
            "Capacidad Nominal AC (kW)", 
            value=float(st.session_state.variables.get("capacidad_ac_kw", 990.0)),
            step=10.0
        )
        st.session_state.variables["tension_kv"] = st.number_input(
            "Tensión en PCC (kV)", 
            value=float(st.session_state.variables.get("tension_kv", 13.2)),
            step=0.1
        )

    with c3:
        # Demanda interna bloqueada para GD, editable para Autogenerador
        es_gd = st.session_state.tipo_informe == "GD"
        st.session_state.variables["demanda_interna_kw"] = st.number_input(
            "Demanda Interna / Autoconsumo (kW)",
            value=float(st.session_state.variables.get("demanda_interna_kw", 0.0)),
            disabled=es_gd,
            help="En GD la demanda interna en el nodo es 0 kW." if es_gd else "Demanda de carga propia de la instalación."
        )
        st.session_state.variables["limite_export_kw"] = st.number_input(
            "Límite de Exportación (kW)", 
            value=float(st.session_state.variables.get("limite_export_kw", 990.0)),
            step=10.0
        )
