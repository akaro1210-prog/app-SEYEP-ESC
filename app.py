import streamlit as st
from views import (
    tab_variables,
    tab_resumen,
    tab_supuestos,
    tab_entrada_metodologia,
    tab_descripcion_equipos,
    tab_resultados_electricos,
    tab_protecciones,
    tab_conclusiones_anexos,
    tab_formato,
    tab_cambios,
    tab_compilacion,
    tab_importar_exportar,
)

st.set_page_config(
    page_title="SEYEP - Estudios Simplificados de Conexión (ESC)",
    page_icon="⚡",
    layout="wide"
)

# --- PLANTILLAS PREDETERMINADAS (GD vs AUTOGENERADOR) ---
TEXTOS_GD = {
    "subtitulo": "Generador Distribuido (GD ≤ 1 MW) - Inyección 100% a la Red MT/BT",
    "resumen": (
        "El presente Estudio Simplificado de Conexión (ESC) tiene como objetivo evaluar la viabilidad "
        "técnica de conexión del proyecto de Generación Distribuida (GD), con una capacidad de inyección "
        "total a la red de Media Tensión del Operador de Red (OR). Conforme a la Res. CREG 174 de 2021, "
        "el proyecto no cuenta con demanda interna asociada en el punto de conexión (PCC), por lo cual "
        "se modela el escenario crítico de Demanda Mínima del circuito con Máxima Inyección."
    ),
    "normativa": "Res. CREG 174/2021 (Art. 4), CREG 075/2021, CREG 101-026/2022, RETIE y NTC 2050.",
    "protecciones": (
        "Esquema de interfaz con relé multifunción ANSI 50/51, 50N/51N, 27/59, 81O/81U y "
        "protección anti-isla activa (IEEE 1547 / ANSI 78/81R) con desconexión en t < 0.5 s."
    ),
    "conclusiones": (
        "Se concluye concepto FAVORABLE para la interconexión de la planta de Generación Distribuida (GD). "
        "La elevación de tensión en el PCC no supera el límite de ±3.0% y la cargabilidad del alimentador "
        "se mantiene en rangos seguros para el Operador de Red."
    )
}

TEXTOS_AUTOGENERADOR = {
    "subtitulo": "Autogenerador a Pequeña Escala (AGPE) con Entrega de Excedentes",
    "resumen": (
        "El presente Estudio Simplificado de Conexión (ESC) evalúa la integración del sistema de "
        "Autogeneración a Pequeña Escala (AGPE). El sistema está dimensionado primordialmente para atender "
        "la demanda interna de la instalación (autoconsumo promedio), entregando excedentes de energía "
        "a la red del Operador de Red bajo las condiciones de la Resolución CREG 174 de 2021."
    ),
    "normativa": "Ley 1715/2014, Ley 2099/2021, Res. CREG 174/2021 (Art. 10 y 11), CREG 030/2018 y RETIE.",
    "protecciones": (
        "Protección integrada en inversores bajo norma IEEE 1547 / UL 1741 SA, desconexión anti-isla "
        "en t < 0.2 s y medidor de energía bidireccional cuatro cuadrantes homologado por el OR."
    ),
    "conclusiones": (
        "La conexión del sistema de Autogeneración (AGPE) es TÉCNICAMENTE VIABLE. El nivel de autoconsumo "
        "cubre prioritariamente la carga interna y los excedentes inyectados no causan sobretensiones "
        "inadmisibles en el circuito de distribución."
    )
}

def inicializar_secciones(tipo):
    textos = TEXTOS_GD if tipo == "GD" else TEXTOS_AUTOGENERADOR
    return [
        {
            "id": "resumen",
            "titulo": f"1.0 Resumen Ejecutivo y Objeto ({tipo})",
            "subtitulo": textos["subtitulo"],
            "contenido": textos["resumen"],
            "imprimir_pdf": True,  # Requisito 2
            "es_personalizada": False
        },
        {
            "id": "normativa",
            "titulo": "2.0 Marco Regulatorio y Normas Técnicas",
            "subtitulo": "Normativa CREG y RETIE aplicable",
            "contenido": textos["normativa"],
            "imprimir_pdf": True,
            "es_personalizada": False
        },
        {
            "id": "equipos",
            "titulo": "3.0 Descripción de Equipos e Instalación",
            "subtitulo": "Módulos solares, inversores y transformador",
            "contenido": "Módulos fotovoltaicos monocristalinos e inversores de red certificados IEEE 1547.",
            "imprimir_pdf": True,
            "es_personalizada": False
        },
        {
            "id": "protecciones",
            "titulo": "4.0 Coordinación de Protecciones e Interfaz",
            "subtitulo": "Ajustes de sobrecorriente, tensión, frecuencia y anti-isla",
            "contenido": textos["protecciones"],
            "imprimir_pdf": True,
            "es_personalizada": False
        },
        {
            "id": "conclusiones",
            "titulo": f"5.0 Conclusiones y Dictamen de Conexión ({tipo})",
            "subtitulo": "Concepto técnico final",
            "contenido": textos["conclusiones"],
            "imprimir_pdf": True,
            "es_personalizada": False
        }
    ]

# Inicializar sesión
if "tipo_informe" not in st.session_state:
    st.session_state.tipo_informe = "GD"

if "secciones" not in st.session_state:
    st.session_state.secciones = inicializar_secciones(st.session_state.tipo_informe)

if "variables" not in st.session_state:
    st.session_state.variables = {
        "nombre_proyecto": "Proyecto Solar SEYEP",
        "codigo_esc": "ESC-2025-001",
        "operador_red": "Empresas Públicas de Medellín (EPM)",
        "capacidad_ac_kw": 990.0,
        "tension_kv": 13.2,
        "demanda_interna_kw": 0.0,
        "limite_export_kw": 990.0,
    }

# Banner superior
st.title("⚡ SEYEP - Generador de Informes ESC")
st.caption(f"Estudio Simplificado de Conexión CREG 174 | Modo Actual: **{st.session_state.tipo_informe}**")

# Pestañas principales
tabs = st.tabs([
    "📋 Variables",
    "📑 Secciones del Informe",
    "⚙️ Formato y Logos",
    "🕒 Control de Cambios",
    "📄 Compilación y PDF",
    "💾 Importar / Exportar"
])

with tabs[0]:
    tab_variables.render()
with tabs[1]:
    tab_resumen.render()  # Renderiza el editor dinámico con los requisitos 2 y 3
with tabs[2]:
    tab_formato.render()
with tabs[3]:
    tab_cambios.render()
with tabs[4]:
    tab_compilacion.render()
with tabs[5]:
    tab_importar_exportar.render()
