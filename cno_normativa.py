"""
Módulo de definiciones normativas del Acuerdo CNO 2233 de 2026
para el Estudio de Ajuste y Coordinación de Protecciones (ANEXO EACP).
Diferencia requisitos y títulos formales de las tablas por rango de potencia
de sistemas de generación basados en inversores conectados al SDL.
"""

RANGOS_POTENCIA_CNO = {
    "P_LE_025": {
        "id": "P_LE_025",
        "nombre": "P ≤ 0.25 MW (Capacidad instalada o nominal ≤ 250 kW)",
        "descripcion": "Aplica Tabla 6 (Funciones mínimas a nivel de inversor) y Tabla 11 (Ajustes recomendados).",
        "tabla_funciones_num": "Tabla 6",
        "tabla_funciones_caption": r"Funciones de protección mínimas para sistemas de generación basados en inversores y frecuencia variable de capacidad instalada o nominal $\leq$ 0,25 MW.",
        "tabla_ajustes_num": "Tabla 11",
        "tabla_ajustes_caption": r"Ajuste de protección sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal $\leq$ 0,25 MW conectados al SDL",
        "tabla_resumen_caption": r"Resumen ajuste de protecciones sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal $\leq$ 0,25 MW conectados al SDL",
        "equipo_corte": "Interruptor termomagnético o Interruptor con unidades de disparo (Tabla 15/16, Nota v)",
        "anti_isla_respaldo": "Opcional a nivel de inversor (IEC 62116 / UL 1741, Nota q)",
        "soe_comtrade": "No obligatorio SOE ni COMTRADE (numeral 8 CNO 2233)",
        "frt_aplica": "No mandatorio soporte LVRT/HVRT dinámico para P ≤ 0.25 MW",
    },
    "P_025_TO_1": {
        "id": "P_025_TO_1",
        "nombre": "0.25 MW < P ≤ 1.0 MW (Capacidad entre 250 kW y 1000 kW)",
        "descripcion": "Aplica Tabla 7 (Funciones mínimas en PC) y Tabla 12 (Ajustes recomendados). Respaldo anti-isla opcional.",
        "tabla_funciones_num": "Tabla 7",
        "tabla_funciones_caption": r"Funciones de protección mínimas para sistemas de generación basados en inversores y frecuencia variable de capacidad instalada o nominal mayor > 0,25 MW.",
        "tabla_ajustes_num": "Tabla 12",
        "tabla_ajustes_caption": r"Ajuste de protección sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal > 0,25 MW conectados al SDL",
        "tabla_resumen_caption": r"Resumen ajuste de protecciones sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal > 0,25 MW conectados al SDL",
        "equipo_corte": "Interruptor con unidades de disparo, Reconectador o Interruptor de potencia (Tabla 15, Nota t)",
        "anti_isla_respaldo": "Principal obligatoria (Intertrip o lógica compuesta); Respaldo opcional (Nota q)",
        "soe_comtrade": "SOE obligatorio con resolución ≤ 1 ms. Registros oscilográficos COMTRADE según acuerdo con OR.",
        "frt_aplica": "Ajustes de 27/59 coordinados por fuera de curvas de inversores (Acuerdo CNO 1833 / 2233)",
    },
    "P_1_TO_5": {
        "id": "P_1_TO_5",
        "nombre": "1.0 MW < P < 5.0 MW (Capacidad entre 1 MW y 5 MW)",
        "descripcion": "Aplica Tabla 7 y Tabla 12. Requiere Anti-Isla Principal y Respaldo obligatorio, y COMTRADE a 960 Hz.",
        "tabla_funciones_num": "Tabla 7",
        "tabla_funciones_caption": r"Funciones de protección mínimas para sistemas de generación basados en inversores y frecuencia variable de capacidad instalada o nominal mayor > 0,25 MW.",
        "tabla_ajustes_num": "Tabla 12",
        "tabla_ajustes_caption": r"Ajuste de protección sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal > 0,25 MW conectados al SDL",
        "tabla_resumen_caption": r"Resumen ajuste de protecciones sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal > 0,25 MW conectados al SDL",
        "equipo_corte": "Reconectador o Interruptor de potencia en el PC (Tabla 15, Nota u)",
        "anti_isla_respaldo": "MANDATORIO: Protección Anti-isla Principal Y Respaldo (Nota q CNO 2233)",
        "soe_comtrade": "MANDATORIO: SOE (≤ 1 ms) y registros oscilográficos COMTRADE a 960 Hz en el PC (numeral 8)",
        "frt_aplica": "Curva FRT obligatoria conforme al Acuerdo CNO 1603 / Resolución CREG 101 011 de 2022",
    },
    "P_GE_5": {
        "id": "P_GE_5",
        "nombre": "P ≥ 5.0 MW (Gran Escala SDL / CREG 148 de 2021)",
        "descripcion": "Aplica Tabla 7 y Tabla 12 con respaldo ANSI 50BF en PC, servicios auxiliares propios y curva FRT CREG 148.",
        "tabla_funciones_num": "Tabla 7",
        "tabla_funciones_caption": r"Funciones de protección mínimas para sistemas de generación basados en inversores y frecuencia variable de capacidad instalada o nominal mayor > 0,25 MW.",
        "tabla_ajustes_num": "Tabla 12",
        "tabla_ajustes_caption": r"Ajuste de protección sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal > 0,25 MW conectados al SDL",
        "tabla_resumen_caption": r"Resumen ajuste de protecciones sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal > 0,25 MW conectados al SDL",
        "equipo_corte": "Interruptor de potencia en bahía de generación dedicada (numeral 6.2 y 7.4)",
        "anti_isla_respaldo": "MANDATORIO: Esquema Intertrip principal y función de respaldo asistida (Notas i y q)",
        "soe_comtrade": "MANDATORIO: SOE y COMTRADE con sincronización horaria satelital oficial colombiana (≤ ±200 ms)",
        "frt_aplica": "Curva FRT obligatoria según Resolución CREG 148 de 2021",
    }
}

# --- TABLA 6: Funciones de protección mínimas para P ≤ 0.25 MW ---
TABLA_6_DEFAULT = [
    {"Función de protección": "Bajatensión (ANSI 27)", "PC": "", "UG": "X", "Notas": "m"},
    {"Función de protección": "Sobrepotencia adelante (ANSI 32)", "PC": "X", "UG": "", "Notas": "k"},
    {"Función de protección": "Sobrecorriente de fases y tierra", "PC": "", "UG": "", "Notas": "l"},
    {"Función de protección": "Sobretensión (ANSI 59)", "PC": "", "UG": "X", "Notas": "m"},
    {"Función de protección": "Frecuencia (ANSI 81U/O)", "PC": "", "UG": "X", "Notas": "p"},
    {"Función de protección": "Anti - isla", "PC": "", "UG": "X", "Notas": "q"},
    {"Función de protección": "Verificación de sincronismo", "PC": "", "UG": "", "Notas": "r"},
]

# --- TABLA 7: Funciones de protección mínimas para P > 0.25 MW ---
TABLA_7_DEFAULT = [
    {"Función de protección": "Bajatensión (ANSI 27)", "PC": "X", "UG": "", "Notas": "m"},
    {"Función de protección": "Sobrepotencia adelante (ANSI 32)", "PC": "X", "UG": "", "Notas": "k"},
    {"Función de protección": "Sobrecorriente de fases y tierra", "PC": "X", "UG": "", "Notas": "l"},
    {"Función de protección": "Sobretensión (ANSI 59)", "PC": "X", "UG": "", "Notas": "m"},
    {"Función de protección": "Sobretensión de secuencia cero (ANSI 59N)", "PC": "X", "UG": "", "Notas": "n"},
    {"Función de protección": "Frecuencia (ANSI 81U/O)", "PC": "", "UG": "", "Notas": "p"},
    {"Función de protección": "Anti - isla", "PC": "X", "UG": "", "Notas": "q"},
    {"Función de protección": "Verificación sincronismo/Chequeo energización", "PC": "X", "UG": "", "Notas": "r"},
]

# --- TABLA 11: Ajuste de protecciones sistémicas para P ≤ 0.25 MW ---
TABLA_11_DEFAULT = [
    {"Función": "Etapa 1: Bajatensión (ANSI 27)", "Ajustes": r"$\leq$ 0.85 p.u.", "Temporización": r"$\geq$ 2 s", "Observaciones": "Coordinada con protecciones sobrecorriente OR"},
    {"Función": "Etapa 2: Bajatensión (ANSI 27)*", "Ajustes": r"$\leq$ 0.5 p.u.", "Temporización": r"$\geq$ 0.2 s", "Observaciones": "Garantiza protección del inversor"},
    {"Función": "Etapa 1: Sobretensión (ANSI 59)", "Ajustes": r"$\geq$ 1.15 p.u.", "Temporización": r"$\geq$ 2 s", "Observaciones": "Actuación trifásica"},
    {"Función": "Etapa 2: Sobretensión (ANSI 59)", "Ajustes": r"$\geq$ 1.2 p.u.", "Temporización": r"$\geq$ 0.2 s", "Observaciones": "Actuación trifásica"},
    {"Función": "Bajafrecuencia (ANSI 81 U)", "Ajustes": "57 Hz", "Temporización": r"$\geq$ 0.2 s", "Observaciones": "Actuación en inversores (F-T o F-F)"},
    {"Función": "Sobrefrecuencia (ANSI 81 O)", "Ajustes": "63 Hz", "Temporización": r"$\geq$ 0.2 s", "Observaciones": "Actuación en inversores (F-T o F-F)"},
]

# --- TABLA 12: Ajuste de protecciones sistémicas para P > 0.25 MW ---
TABLA_12_DEFAULT = [
    {"Función": "Etapa 1: Bajatensión (ANSI 27)", "Ajustes": r"$\leq$ 0.6 p.u.", "Temporización": "Ver nota", "Observaciones": "Actuación segregada por fase o trifásica"},
    {"Función": "Etapa 2: Bajatensión (ANSI 27)", "Ajustes": r"$\leq$ 0.4 p.u.", "Temporización": "Ver nota", "Observaciones": "Actuación segregada por fase o trifásica"},
    {"Función": "Etapa 1: Sobretensión (ANSI 59)", "Ajustes": r"$\geq$ 1.22 p.u.", "Temporización": r"$\geq$ 2.5 s", "Observaciones": "Actuación trifásica"},
    {"Función": "Etapa 2: Sobretensión (ANSI 59)", "Ajustes": r"$\geq$ 1.25 p.u.", "Temporización": r"$\geq$ 0.5 s", "Observaciones": "Actuación trifásica"},
    {"Función": "Bajafrecuencia (ANSI 81 U)", "Ajustes": "57 Hz", "Temporización": r"$\geq$ 0.2 s", "Observaciones": "Actuación tensiones F-T"},
    {"Función": "Sobrefrecuencia (ANSI 81 O)", "Ajustes": "63 Hz", "Temporización": r"$\geq$ 0.2 s", "Observaciones": "Actuación tensiones F-T"},
]


def obtener_datos_tablas_cno(clave_rango: str, version_cno: str = "2233"):
    """Retorna las tablas por defecto, textos, notas y títulos según el rango seleccionado y la versión CNO."""
    import copy
    es_menor_igual_025 = (clave_rango == "P_LE_025")
    info_base = RANGOS_POTENCIA_CNO.get(clave_rango, RANGOS_POTENCIA_CNO["P_025_TO_1"])
    info_rango = copy.deepcopy(info_base)

    cno_str = str(version_cno).strip() if version_cno else "2233"
    if cno_str != "2233":
        for k in ["descripcion", "soe_comtrade", "anti_isla_respaldo", "frt_aplica"]:
            if k in info_rango and isinstance(info_rango[k], str):
                info_rango[k] = info_rango[k].replace("2233", cno_str)

    if es_menor_igual_025:
        df_func = list(TABLA_6_DEFAULT)
        df_ajustes = list(TABLA_11_DEFAULT)
        obs_1 = (
            "La protección ANSI 32 aplica para autogeneradores con o sin entrega de excedentes a la red (Nota k). "
            "En caso de que el proyecto sea Generador Distribuido (GD) o declare entrega total de excedentes, no se requiere."
        )
        obs_2 = (
            "Para capacidades menores o iguales a 0.25 MW (≤ 250 kW), las protecciones principales operan a nivel de inversor (UG) "
            "según la Tabla 6 y normas UL 1741 / IEC 62116. La función de sincronismo se valida en el inversor (Nota r)."
        )
    else:
        df_func = list(TABLA_7_DEFAULT)
        df_ajustes = list(TABLA_12_DEFAULT)
        obs_1 = (
            "La protección ANSI 32 no aplica, dado que el proyecto es un generador distribuido (o autogenerador con entrega "
            "total autorizada de excedentes a la red), y esta función aplicará solo para autogeneradores con o sin entregar excedentes a la red."
        )
        obs_2 = (
            f"Para la verificación de sincronismo, conforme a la nota “r” del acuerdo CNO {cno_str} se implementará en el PC la función ANSI 25 "
            "configurando solamente la condición de Barra viva OR - Línea muerta PV, con un umbral mínimo de tensión de 0.8 p.u "
            "que garantice que el sistema no permitirá energización cuando el sistema del OR se encuentre sin tensión."
        )

    return {
        "info_rango": info_rango,
        "es_menor_igual_025": es_menor_igual_025,
        "df_funciones_prot": df_func,
        "df_ajustes_cno": df_ajustes,
        "obs_cno_1": obs_1,
        "obs_cno_2": obs_2,
        "tabla_funciones_num": info_rango["tabla_funciones_num"],
        "tabla_funciones_caption": info_rango["tabla_funciones_caption"],
        "tabla_ajustes_num": info_rango["tabla_ajustes_num"],
        "tabla_ajustes_caption": info_rango["tabla_ajustes_caption"],
        "tabla_resumen_caption": info_rango["tabla_resumen_caption"],
    }
