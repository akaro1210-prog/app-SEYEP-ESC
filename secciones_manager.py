import streamlit as st
from project_manager import obtener_val, obtener_ver

# Diccionario maestro de las 10 secciones estándar del informe ESC
SECCIONES_ESTANDAR = {
    "sec_1": {
        "numero": "1",
        "nombre": "Resumen Ejecutivo y Supuestos",
        "latex_sec": "RESUMEN EJECUTIVO",
        "descripcion": "Objetivo, marco CREG 174, supuestos de crecimiento UPME/OR y resumen ejecutivo.",
    },
    "sec_2": {
        "numero": "2",
        "nombre": "Descripción General del Proyecto",
        "latex_sec": "DESCRIPCIÓN GENERAL DEL PROYECTO",
        "descripcion": "Coordenadas geográficas, especificaciones generales, módulos solares e inversores.",
    },
    "sec_3": {
        "numero": "3",
        "nombre": "Parámetros Eléctricos de los Equipos y Operación Declarada",
        "latex_sec": "PARÁMETROS ELÉCTRICOS DE LOS EQUIPOS Y OPERACIÓN DECLARADA",
        "descripcion": "Modelado de red, conductores, transformador elevador y diagrama unifilar del parque.",
    },
    "sec_4": {
        "numero": "4",
        "nombre": "Información de Entrada y Supuestos de Salida",
        "latex_sec": "INFORMACIÓN DE ENTRADA Y SUPUESTOS DE SALIDA",
        "descripcion": "Zona de influencia del circuito, horizonte de análisis, curvas de demanda y producción.",
    },
    "sec_5": {
        "numero": "5",
        "nombre": "Metodología de Análisis",
        "latex_sec": "METODOLOGÍA",
        "descripcion": "Criterios normativos CREG 021 de 2022 y metodología para flujo de carga y cortocircuito.",
    },
    "sec_6": {
        "numero": "6",
        "nombre": "Descripción de los Escenarios de Análisis",
        "latex_sec": "DESCRIPCIÓN DE LOS ESCENARIOS DE ANÁLISIS",
        "descripcion": "Escenarios analizados: demanda mínima/máxima con y sin proyecto solar fotovoltaico.",
    },
    "sec_7": {
        "numero": "7",
        "nombre": "Resultados de los Análisis Eléctricos",
        "latex_sec": "RESULTADOS DE LOS ANÁLISIS ELÉCTRICOS.",
        "descripcion": "Flujo de carga AC, perfiles de tensión, contingencias N-1, pérdidas y cortocircuito.",
    },
    "sec_8": {
        "numero": "8",
        "nombre": "Verificación de Protecciones",
        "latex_sec": "VERIFICACIÓN DE PROTECCIONES",
        "descripcion": "Sistema AC, coordinación de protecciones 50/51, sobretensiones 59/27, anti-isla y tabla sistemática.",
    },
    "sec_9": {
        "numero": "9",
        "nombre": "Conclusiones",
        "latex_sec": "CONCLUSIONES",
        "descripcion": "Concepto técnico final de viabilidad de conexión del proyecto a la red del OR.",
    },
    "sec_10": {
        "numero": "10",
        "nombre": "Anexos",
        "latex_sec": "ANEXOS",
        "descripcion": "Gráficas de flujo de carga de PowerFactory, perfiles de tensión y curvas de protecciones.",
    },
}

def inicializar_estado_secciones():
    """Garantiza que las estructuras de datos de secciones existan en st.session_state."""
    if "secciones_activas" not in st.session_state:
        # Por defecto todas las 10 secciones están activas
        st.session_state["secciones_activas"] = {
            sec_id: True for sec_id in SECCIONES_ESTANDAR
        }
    if "secciones_personalizadas" not in st.session_state:
        st.session_state["secciones_personalizadas"] = []

def esta_seccion_activa(sec_id: str) -> bool:
    """Verifica si una sección estándar está marcada como activa para el informe."""
    inicializar_estado_secciones()
    cargadas = st.session_state.get("esc_params_cargados", {})
    if isinstance(cargadas, dict) and f"incluir_{sec_id}" in cargadas:
        return bool(cargadas[f"incluir_{sec_id}"])
    return bool(st.session_state["secciones_activas"].get(sec_id, True))

def render_control_seccion(sec_id: str, titulo: str) -> bool:
    """
    Renderiza el interruptor para marcar una sección como obligatoria u opcional.
    Permite omitir secciones existentes si el usuario lo desea.
    """
    inicializar_estado_secciones()
    ver = obtener_ver()
    
    val_default = esta_seccion_activa(sec_id)
    key_widget = f"chk_opcional_{sec_id}_{ver}"
    
    with st.container(border=True):
        col_chk, col_status = st.columns([3.5, 1.2])
        with col_chk:
            activa = st.checkbox(
                f"📄 **Incluir en el informe:** {titulo}",
                value=val_default,
                key=key_widget,
                help=f"Desmarca esta casilla si {titulo} es opcional y deseas retirarla del documento LaTeX/PDF."
            )
        with col_status:
            if activa:
                st.markdown(
                    "<span style='color: #10b981; font-weight: bold;'>✅ Sección Activa</span>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    "<span style='color: #f59e0b; font-weight: bold;'>⏸️ Omitida (Opcional)</span>",
                    unsafe_allow_html=True
                )
        
        st.session_state["secciones_activas"][sec_id] = activa
        
        if not activa:
            st.info(
                f"ℹ️ **Sección opcional omitida:** {titulo} no se generará en el archivo `.tex` ni en el `.pdf` final. "
                "Los números del resto de secciones se ajustarán automáticamente."
            )
    
    return activa

def render_boton_agregar_seccion(sec_padre: str, titulo_padre: str):
    """
    Renderiza el botón para agregar nuevas secciones o subsecciones asociadas a una sección del documento,
    así como el editor para todas las secciones adicionales agregadas a este punto.
    """
    inicializar_estado_secciones()
    ver = obtener_ver()
    
    st.markdown("---")
    col_btn, col_info = st.columns([1.5, 2])
    with col_btn:
        if st.button(
            f"➕ Agregar Nueva Sección / Subsección en {titulo_padre}",
            key=f"btn_add_sec_{sec_padre}_{ver}",
            use_container_width=True
        ):
            nuevo_id = f"custom_{sec_padre}_{len(st.session_state['secciones_personalizadas']) + 1}"
            st.session_state["secciones_personalizadas"].append({
                "id": nuevo_id,
                "padre": sec_padre,
                "titulo": f"Nueva Subsección de {titulo_padre}",
                "nivel": "Subsección (\\subsection)",
                "contenido": "Redacta aquí el contenido técnico o explicativo de esta sección adicional...",
                "incluir_tabla": False,
                "tabla_texto": "",
                "incluir_figura": False,
                "figura_nombre": "",
                "figura_caption": ""
            })
            st.rerun()
    with col_info:
        st.caption("Permite expandir el documento con secciones personalizadas (subsecciones, tablas o imágenes propias).")

    # Renderizar las secciones personalizadas existentes para este padre
    personalizadas = [
        s for s in st.session_state["secciones_personalizadas"]
        if s.get("padre") == sec_padre
    ]
    
    if personalizadas:
        st.markdown(f"#### 📑 Secciones adicionales agregadas a {titulo_padre} ({len(personalizadas)})")
        indices_a_eliminar = []
        
        for idx_local, sec_cust in enumerate(personalizadas):
            id_cust = sec_cust.get("id", f"{sec_padre}_{idx_local}")
            with st.container(border=True):
                c_top1, c_top2 = st.columns([3, 1])
                with c_top1:
                    st.markdown(f"**Sección Adicional #{idx_local + 1}**")
                with c_top2:
                    if st.button("🗑️ Quitar Sección", key=f"del_sec_{id_cust}_{ver}", type="secondary"):
                        indices_a_eliminar.append(sec_cust)
                
                col_t, col_n = st.columns([2.5, 1.5])
                with col_t:
                    nuevo_titulo = st.text_input(
                        "Título de la nueva sección/subsección:",
                        value=sec_cust.get("titulo", ""),
                        key=f"cust_tit_{id_cust}_{ver}"
                    )
                    sec_cust["titulo"] = nuevo_titulo
                with col_n:
                    niveles = [
                        "Subsección (\\subsection)",
                        "Sub-subsección (\\subsubsection)",
                        "Sección Principal (\\section)",
                    ]
                    idx_nivel = 0
                    if sec_cust.get("nivel") in niveles:
                        idx_nivel = niveles.index(sec_cust.get("nivel"))
                    nuevo_nivel = st.selectbox(
                        "Nivel jerárquico LaTeX:",
                        options=niveles,
                        index=idx_nivel,
                        key=f"cust_niv_{id_cust}_{ver}"
                    )
                    sec_cust["nivel"] = nuevo_nivel
                
                nuevo_contenido = st.text_area(
                    "Contenido / Párrafos de la sección (soporta comandos LaTeX y texto enriquecido):",
                    value=sec_cust.get("contenido", ""),
                    height=100,
                    key=f"cust_cnt_{id_cust}_{ver}"
                )
                sec_cust["contenido"] = nuevo_contenido
                
                # Opciones complementarias de tabla o imagen
                with st.expander("➕ Adjuntar Tabla o Figura opcional a esta sección"):
                    c_tab, c_img = st.columns(2)
                    with c_tab:
                        inc_tab = st.checkbox("Incluir Tabla de Datos", value=sec_cust.get("incluir_tabla", False), key=f"cust_inctab_{id_cust}_{ver}")
                        sec_cust["incluir_tabla"] = inc_tab
                        if inc_tab:
                            sec_cust["tabla_caption"] = st.text_input("Título de la tabla (Caption):", value=sec_cust.get("tabla_caption", "Tabla adicional de parámetros"), key=f"cust_tabcap_{id_cust}_{ver}")
                            sec_cust["tabla_texto"] = st.text_area("Filas LaTeX o valores separados por comas (CSV):", value=sec_cust.get("tabla_texto", "Parámetro & Valor \\\\ \\hline"), key=f"cust_tabtxt_{id_cust}_{ver}")
                    with c_img:
                        inc_img = st.checkbox("Subir Figura / Gráfica", value=sec_cust.get("incluir_figura", False), key=f"cust_incimg_{id_cust}_{ver}")
                        sec_cust["incluir_figura"] = inc_img
                        if inc_img:
                            sec_cust["figura_caption"] = st.text_input("Pie de figura (Caption):", value=sec_cust.get("figura_caption", "Gráfica complementaria"), key=f"cust_imgcap_{id_cust}_{ver}")
                            up_cust_img = st.file_uploader(f"Subir imagen para '{nuevo_titulo}':", type=["png", "jpg", "jpeg"], key=f"cust_file_{id_cust}_{ver}")
                            if up_cust_img is not None:
                                nom_img = f"custom_img_{id_cust}.png"
                                with open(nom_img, "wb") as f_img:
                                    f_img.write(up_cust_img.getbuffer())
                                sec_cust["figura_nombre"] = nom_img
                                st.success(f"✅ Imagen guardada como {nom_img}")
        
        if indices_a_eliminar:
            for item in indices_a_eliminar:
                if item in st.session_state["secciones_personalizadas"]:
                    st.session_state["secciones_personalizadas"].remove(item)
            st.rerun()

def obtener_diccionario_secciones():
    """Retorna el estado completo de secciones para exportar el proyecto o pasarlo a latex_builder."""
    inicializar_estado_secciones()
    res = {}
    for sec_id, activa in st.session_state["secciones_activas"].items():
        res[f"incluir_{sec_id}"] = activa
    res["secciones_personalizadas"] = list(st.session_state["secciones_personalizadas"])
    return res

def render_resumen_estructura_documento():
    """Panel global para visualizar y configurar rápidamente toda la estructura de secciones del informe."""
    inicializar_estado_secciones()
    ver = obtener_ver()
    with st.expander("📚 Configuración y Gestión de Todas las Secciones del Documento", expanded=False):
        st.write(
            "Aquí puedes activar o desactivar secciones completas de forma opcional, "
            "o verificar qué secciones adicionales has agregado al informe."
        )
        c_a1, c_a2 = st.columns(2)
        items = list(SECCIONES_ESTANDAR.items())
        mitad = len(items) // 2
        
        with c_a1:
            for sec_id, info in items[:mitad]:
                act = st.session_state["secciones_activas"].get(sec_id, True)
                nuevo_act = st.checkbox(
                    f"Sección {info['numero']}: {info['nombre']}",
                    value=act,
                    key=f"chk_master_{sec_id}_{ver}"
                )
                st.session_state["secciones_activas"][sec_id] = nuevo_act
        with c_a2:
            for sec_id, info in items[mitad:]:
                act = st.session_state["secciones_activas"].get(sec_id, True)
                nuevo_act = st.checkbox(
                    f"Sección {info['numero']}: {info['nombre']}",
                    value=act,
                    key=f"chk_master_{sec_id}_{ver}"
                )
                st.session_state["secciones_activas"][sec_id] = nuevo_act
