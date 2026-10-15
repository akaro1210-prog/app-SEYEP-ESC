import streamlit as st

def render():
    st.subheader(f"📑 Secciones del Informe - {st.session_state.tipo_informe}")
    st.write(
        "Edite el contenido de las secciones, elija con el selector si cada una se imprimirá en el PDF "
        "y agregue nuevas secciones personalizadas donde lo requiera."
    )

    secciones = st.session_state.secciones

    # Contador rápido de secciones en PDF
    incluidas = sum(1 for s in secciones if s.get("imprimir_pdf", True))
    col_info, col_acc1, col_acc2 = st.columns([3, 1, 1])
    with col_info:
        st.info(f"📊 **Estado para PDF:** Se imprimirán **{incluidas} de {len(secciones)}** secciones.")
    with col_acc1:
        if st.button("✅ Incluir Todas en PDF"):
            for s in secciones:
                s["imprimir_pdf"] = True
            st.rerun()
    with col_acc2:
        if st.button("❌ Excluir Todas de PDF"):
            for s in secciones:
                s["imprimir_pdf"] = False
            st.rerun()

    st.markdown("---")

    # Renderizar cada sección con sus controles
    for idx, sec in enumerate(secciones):
        with st.container():
            # Encabezado visual de la sección
            col_t1, col_t2 = st.columns([4, 1.5])
            with col_t1:
                sec["titulo"] = st.text_input(
                    f"Título de Sección #{idx + 1}",
                    value=sec["titulo"],
                    key=f"titulo_{sec['id']}_{idx}"
                )
            
            with col_t2:
                # REQUISITO 2: Selector para imprimir en PDF
                sec["imprimir_pdf"] = st.checkbox(
                    "🖨️ Imprimir en PDF",
                    value=sec.get("imprimir_pdf", True),
                    key=f"chk_pdf_{sec['id']}_{idx}",
                    help="Active o desactive para incluir u omitir esta sección en el informe PDF final."
                )

            # Subtítulo y contenido editable
            sec["subtitulo"] = st.text_input(
                "Subtítulo / Objetivo",
                value=sec.get("subtitulo", ""),
                key=f"subtitulo_{sec['id']}_{idx}"
            )

            sec["contenido"] = st.text_area(
                "Contenido Técnico",
                value=sec["contenido"],
                rows=4,
                key=f"contenido_{sec['id']}_{idx}"
            )

            # Botones de acción de la sección
            col_b1, col_b2, col_b3 = st.columns([2, 1, 1])
            with col_b1:
                # REQUISITO 3: Botón para agregar nueva sección debajo de esta
                if st.button(f"➕ Agregar nueva sección aquí", key=f"btn_add_{sec['id']}_{idx}"):
                    nueva_seccion = {
                        "id": f"custom_{idx + 1}_{len(secciones)}",
                        "titulo": f"Nueva Sección Personalizada",
                        "subtitulo": "Objetivo técnico definido por el usuario",
                        "contenido": "Redacte aquí la memoria de cálculo, supuestos o tablas técnicas...",
                        "imprimir_pdf": True,
                        "es_personalizada": True
                    }
                    secciones.insert(idx + 1, nueva_seccion)
                    st.success(f"Sección agregada después de #{idx + 1}")
                    st.rerun()

            with col_b2:
                if sec.get("es_personalizada", False):
                    if st.button("🗑️ Eliminar Sección", key=f"btn_del_{sec['id']}_{idx}"):
                        secciones.pop(idx)
                        st.rerun()

            st.markdown("<hr style='margin: 15px 0; border: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
