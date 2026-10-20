import os
import subprocess
import pandas as pd

def escapar_latex(texto):
    """Función para escapar caracteres especiales de LaTeX en celdas o variables."""
    if texto is None or (isinstance(texto, float) and pd.isna(texto)):
        return ""
    if not isinstance(texto, str):
        texto = str(texto)
    texto = texto.replace('\\_', '_').replace('\\%', '%').replace('\\&', '&')
    texto = texto.replace('\\', '\\textbackslash{}')
    texto = texto.replace('&', '\\&')
    texto = texto.replace('%', '\\%')
    texto = texto.replace('$', '\\$')
    texto = texto.replace('#', '\\#')
    texto = texto.replace('_', '\\_')
    texto = texto.replace('{', '\\{')
    texto = texto.replace('}', '\\}')
    texto = texto.replace('~', '\\textasciitilde{}')
    texto = texto.replace('^', '\\textasciicircum{}')
    return texto

def normalizar_clave(k):
    return str(k).strip().lstrip("\\").lower().replace("_", "").replace("-", "").replace(" ", "")

def es_escalar_no_vacio(v):
    return isinstance(v, (str, int, float)) and not isinstance(v, bool) and str(v).strip() != ""

def buscar_param(params, candidatos, default=""):
    for c in candidatos:
        if c in params and es_escalar_no_vacio(params[c]):
            return params[c]

    mapa_norm = {}
    for k, v in params.items():
        if isinstance(k, str) and es_escalar_no_vacio(v):
            mapa_norm[normalizar_clave(k)] = v

    try:
        import streamlit as st
        for k, v in st.session_state.items():
            if isinstance(k, str) and es_escalar_no_vacio(v):
                nk = normalizar_clave(k)
                if nk not in mapa_norm:
                    mapa_norm[nk] = v
    except Exception:
        pass

    for c in candidatos:
        nc = normalizar_clave(c)
        if nc in mapa_norm:
            return mapa_norm[nc]

    return default

def resolver_ruta_imagen(nombre_archivo):
    ruta_original = str(nombre_archivo).strip().replace("\\", "/")
    if os.path.exists(ruta_original):
        return ruta_original

    base_buscada = os.path.splitext(os.path.basename(ruta_original))[0]
    clave_buscada = base_buscada.lower().replace(" ", "").replace("_", "").replace("-", "")

    for carpeta in [".", "modulos_latex"]:
        if not os.path.isdir(carpeta):
            continue
        try:
            for item in os.listdir(carpeta):
                nombre_item, ext_item = os.path.splitext(item)
                if ext_item.lower() not in (".png", ".jpg", ".jpeg"):
                    continue
                clave_item = nombre_item.lower().replace(" ", "").replace("_", "").replace("-", "")
                if clave_item == clave_buscada:
                    return item if carpeta == "." else f"{carpeta}/{item}"
        except Exception:
            pass
    return None

def incluir_imagen_segura(nombre_archivo, opciones="width=0.95\\textwidth", usar_resizebox=False, ancho_resize="1\\textwidth"):
    ruta_resuelta = resolver_ruta_imagen(nombre_archivo)
    if ruta_resuelta:
        if usar_resizebox:
            return f"\\resizebox{{{ancho_resize}}}{{!}}{{\\includegraphics{{{ruta_resuelta}}}}}"
        return f"\\includegraphics[{opciones}]{{{ruta_resuelta}}}"
    nombre_limpio = escapar_latex(os.path.basename(str(nombre_archivo).strip()))
    return (
        f"\\fbox{{\\parbox{{0.85\\textwidth}}{{\\centering\\vspace{{0.5cm}}"
        f"\\small\\textbf{{[Imagen pendiente por cargar en el directorio:]}}\\\\[0.15cm]"
        f"\\texttt{{{nombre_limpio}}}\\vspace{{0.5cm}}}}}}"
    )

def generar_preambulo():
    enc_path = resolver_ruta_imagen("Encabezado.png")
    pie_path = resolver_ruta_imagen("Piedepagina.png")

    cmd_enc = f"\\includegraphics[width=\\paperwidth,height=5cm]{{{enc_path}}}" if enc_path else "\\vspace*{2cm}"
    cmd_pie = f"\\includegraphics[width=\\paperwidth]{{{pie_path}}}" if pie_path else "\\vspace*{1cm}"

    return f"""\\documentclass[12pt,letterpaper,spanish]{{article}}

% ---------- Idioma y acentos (pdfLaTeX) ----------
\\usepackage[spanish]{{babel}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{microtype}}
\\usepackage{{tocloft}}
\\usepackage{{makecell}}
\\renewcommand{{\\cfttoctitlefont}}{{\\hfill\\Large\\bfseries}}
\\renewcommand{{\\cftaftertoctitle}}{{\\hfill}}
\\renewcommand{{\\contentsname}}{{TABLA DE CONTENIDO}}

% ---------- Tipografía ----------
\\usepackage{{mathpazo}}
\\RequirePackage{{fix-cm}}
\\usepackage{{anyfontsize}}
\\usepackage{{pdflscape}}
\\usepackage{{float}}
\\usepackage{{etoolbox}}
\\IfFileExists{{placeins.sty}}{{
  \\usepackage[section]{{placeins}}
}}{{
  \\providecommand{{\\FloatBarrier}}{{\\relax}}
}}

% ---------- Control estricto de retención de tablas y figuras en su sección ----------
\\pretocmd{{\\section}}{{\\FloatBarrier}}{{}}{{}}
\\pretocmd{{\\subsection}}{{\\FloatBarrier}}{{}}{{}}
\\pretocmd{{\\subsubsection}}{{\\FloatBarrier}}{{}}{{}}
\\renewcommand{{\\topfraction}}{{0.85}}
\\renewcommand{{\\bottomfraction}}{{0.85}}
\\renewcommand{{\\textfraction}}{{0.15}}
\\renewcommand{{\\floatpagefraction}}{{0.80}}
\\setcounter{{topnumber}}{{4}}
\\setcounter{{bottomnumber}}{{4}}
\\setcounter{{totalnumber}}{{6}}
\\setlength{{\\floatsep}}{{10pt plus 2pt minus 2pt}}
\\setlength{{\\textfloatsep}}{{14pt plus 2pt minus 3pt}}
\\setlength{{\\intextsep}}{{10pt plus 2pt minus 2pt}}
\\usepackage[strict]{{changepage}}
\\setlength{{\\headheight}}{{147pt}}
\\addtolength{{\\topmargin}}{{-17pt}}
\\setlength{{\\footskip}}{{119pt}}

% ---------- Gráficos y tablas ----------
\\usepackage{{graphicx}}
\\usepackage{{array}}
\\usepackage{{multirow}}
\\usepackage[table]{{xcolor}}
\\usepackage{{colortbl}}
\\usepackage{{booktabs}}
\\usepackage{{tabularx}}
\\usepackage{{etoolbox}}
\\usepackage{{amsmath}}
\\usepackage{{pgfplotstable}}
\\usepackage{{adjustbox}}
\\usepackage{{longtable}}

% --- Parche obligatorio para el error \\tbl_gdecr_row_count ---
\\usepackage{{expl3}}
\\ExplSyntaxOn
\\cs_if_exist:NF \\tbl_gdecr_row_count: {{ \\cs_set_eq:NN \\tbl_gdecr_row_count: \\relax }}
\\cs_if_exist:NF \\tag_mc_end: {{ \\cs_set_eq:NN \\tag_mc_end: \\relax }}
\\ExplSyntaxOff
\\pgfplotsset{{compat=1.18}}
\\usepackage{{caption}}
\\usepackage{{pgfplots}}

\\DeclareCaptionType{{ilustracion}}[Ilustración][Índice de ilustraciones]

% ---------- Encabezado, pie y márgenes ----------
\\usepackage{{fancyhdr}}
\\usepackage[
  letterpaper,
  top=5cm,
  headheight=110pt,
  bottom=3.5cm,
  left=2.5cm,
  right=2.5cm
]{{geometry}}

% ---------- Hipervínculos y referencias ----------
\\usepackage[hidelinks]{{hyperref}}
\\usepackage[spanish]{{cleveref}}

% ---------- Captions ----------
\\addto\\captionsspanish{{\\renewcommand{{\\tablename}}{{TABLA}}}}
\\addto\\captionsspanish{{\\renewcommand{{\\figurename}}{{FIGURA}}}}
\\captionsetup{{
  labelfont=bf,
  textfont=bf,
  labelsep=period,
  justification=centering,
  singlelinecheck=false,
  font={{stretch=1}},
  skip=0pt
}}

% ---------- Nombres de referencias ----------
\\crefname{{table}}{{TABLA}}{{TABLAS}}
\\crefname{{figure}}{{FIGURA}}{{FIGURAS}}
\\crefformat{{table}}{{\\textbf{{TABLA~#2#1#3}}}}
\\crefrangeformat{{table}}{{\\textbf{{TABLAS~#3#1#4~a~#5#2#6}}}}
\\crefmultiformat{{table}}{{\\textbf{{TABLAS~#2#1#3}}}}{{ y \\textbf{{#2#1#3}}}}{{, \\textbf{{#2#1#3}}}}{{ y \\textbf{{#2#1#3}}}}
\\crefformat{{figure}}{{\\textbf{{FIGURA~#2#1#3}}}}
\\crefrangeformat{{figure}}{{\\textbf{{FIGURAS~#3#1#4~a~#5#2#6}}}}
\\crefmultiformat{{figure}}{{\\textbf{{FIGURAS~#2#1#3}}}}{{ y \\textbf{{#2#1#3}}}}{{, \\textbf{{#2#1#3}}}}{{ y \\textbf{{#2#1#3}}}}

% ---------- Encabezado y pie con imágenes ----------
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}

\\fancyhead[C]{{%
  \\makebox[\\textwidth][c]{{%
    {cmd_enc}%
  }}%
}}
\\fancyfoot[C]{{%
  \\makebox[\\textwidth][c]{{%
    {cmd_pie}%
  }}%
}}

\\fancypagestyle{{plain}}{{%
  \\fancyhf{{}}%
  \\renewcommand{{\\headrulewidth}}{{0pt}}%
  \\renewcommand{{\\footrulewidth}}{{0pt}}%
  \\fancyhead[C]{{%
    \\makebox[\\textwidth][c]{{%
      {cmd_enc}%
    }}%
  }}%
  \\fancyfoot[C]{{%
    \\makebox[\\textwidth][c]{{%
      {cmd_pie}%
    }}%
  }}%
}}

% ---------- Columnas personalizadas ----------
\\newcolumntype{{L}}{{>{{\\raggedright\\arraybackslash}}X}}
\\newcolumntype{{C}}{{>{{\\centering\\arraybackslash}}X}}
\\newcolumntype{{P}}[1]{{>{{\\raggedright\\arraybackslash}}p{{#1}}}}

% ---------- Color corporativo ----------
\\definecolor{{azulSeyep}}{{RGB}}{{0,103,254}}

% ---------- \\ref en negrita ----------
\\let\\oldref\\ref
\\renewcommand{{\\ref}}[1]{{\\textbf{{\\oldref{{#1}}}}}}

% ---------- Ajustes finos de tablas ----------
\\setlength{{\\tabcolsep}}{{3pt}}
\\renewcommand{{\\arraystretch}}{{1.05}}
"""

def formatear_celda_cambio(val):
    """Si la celda inicia con '*', le aplica \\cellcolor{yellow}."""
    txt = str(val).strip()
    if txt.startswith("*"):
        limpio = escapar_latex(txt[1:].strip())
        return f"\\cellcolor{{yellow}}{limpio}"
    return escapar_latex(txt)

def compilar_estudio_latex(params):
    if params is None:
        params = {}

    try:
        import streamlit as st
        for k_sess in [
            "config_vars",
            "datos_sistema_cno",
            "datos_tension_59n_isla",
            "datos_sobrecorriente",
            "datos_anexos_eacp",
        ]:
            if k_sess in st.session_state and isinstance(st.session_state[k_sess], dict):
                for sub_k, sub_v in st.session_state[k_sess].items():
                    if sub_k not in params:
                        params[sub_k] = sub_v
    except Exception:
        pass

    # 1. Variables principales del proyecto
    nombre_proyecto = escapar_latex(buscar_param(params, ["nombreProyecto", "nombre_proyecto"], "Arboreo"))
    capacidad_mw = escapar_latex(buscar_param(params, ["capacidadMW", "capacidad_mw"], "900kW"))
    operador_red = escapar_latex(buscar_param(params, ["OR", "operadorRed"], "EPM"))
    fecha_entrada = escapar_latex(buscar_param(params, ["FechaEntrada", "fecha_entrada"], "marzo del 2027"))
    mes_entrega = escapar_latex(
        buscar_param(
            params,
            [
                "mesentregainformemasyear",
                "mes_entrega",
                "mesEntrega",
                "fecha_entrega",
                "mes_informe",
                "mes_anio",
            ],
            "Septiembre, 2026",
        )
    )
    latitud = escapar_latex(buscar_param(params, ["Latitud", "latitud"], '5°53\'49.8"N'))
    longitud = escapar_latex(buscar_param(params, ["Longitud", "longitud"], '74°45\'12.9"W'))
    year_inicial = escapar_latex(buscar_param(params, ["YearInicial", "year_inicial"], "2027"))
    year_final = escapar_latex(buscar_param(params, ["YearFinal", "year_final"], "2032"))
    cto = escapar_latex(buscar_param(params, ["CTO", "cto"], "211-11"))
    ssee = escapar_latex(buscar_param(params, ["SSEE", "ssee"], "Doradal_13.2"))
    nt = escapar_latex(buscar_param(params, ["NT", "nt"], "13.2kV"))
    nodo = escapar_latex(buscar_param(params, ["nodo"], "906750"))
    elemento_proteccion = escapar_latex(buscar_param(params, ["elementoProteccion"], "211-11"))
    referencia_panel = escapar_latex(buscar_param(params, ["referenciaPanel"], "JAM66D45 625 LB"))
    potencia_panel = escapar_latex(buscar_param(params, ["potenciaPanel"], "625 Wp"))
    cantidad_panel = escapar_latex(buscar_param(params, ["cantidadPanel"], "1760"))
    ubicacion = escapar_latex(buscar_param(params, ["ubicacion"], "En predio del hotel Arboreo, Doradal, Antioquia"))
    ref_inv_1 = escapar_latex(buscar_param(params, ["refInversoruno"], "Inversor 150 kW On-Grid."))
    mod_inv_1 = escapar_latex(buscar_param(params, ["Inversoruno"], "Growat MAX 150KTL3-X2MV"))
    cant_inv_1 = escapar_latex(buscar_param(params, ["cantidadInversoruno"], "6 Und."))
    generacion_aprobada = escapar_latex(buscar_param(params, ["generacionaprobada"], "900kW"))
    reco_cto = escapar_latex(buscar_param(params, ["recoCTO", "reco_cto"], "211-11"))
    tipo_proteccion = escapar_latex(buscar_param(params, ["tipoproteccion", "tipo_proteccion"], "Reconectador"))
    reco_cabecera = escapar_latex(buscar_param(params, ["recocabecera", "reco_cabecera"], "211-11"))
    norma_cno = escapar_latex(buscar_param(params, ["normaCNO", "norma_cno", "norma_CNO"], "2233"))

    # Variables 59N
    tres_vcero_mas_alta = escapar_latex(buscar_param(params, ["tresVceroMASALTA"], "0.373 p.u."))
    tres_vcero_mas_alta_kv = escapar_latex(buscar_param(params, ["tresVceroMASALTAkV"], "2.842 kV"))
    ajuste_tres_vcero = escapar_latex(buscar_param(params, ["ajustetresVcero"], "0.2 p.u"))
    mag_ajuste_tres_vcero = escapar_latex(buscar_param(params, ["magajustetresVcero"], "1.524 kV"))

    # 2. Control de Cambios (\controlcambios)
    df_cambios = params.get("df_control_cambios", None)
    filas_cambios = []
    if df_cambios is not None and isinstance(df_cambios, pd.DataFrame) and not df_cambios.empty:
        for _, row in df_cambios.iterrows():
            v_num = escapar_latex(row.get("VERSIÓN No.", row.get("Versión", "0")))
            v_desc = escapar_latex(row.get("DESCRIPCIÓN", row.get("Descripción", "")))
            v_fec = escapar_latex(row.get("FECHA", row.get("Fecha", "")))
            v_obs = escapar_latex(row.get("OBSERVACIONES", row.get("Observaciones", "")))
            filas_cambios.append(f"        {v_num} & {v_desc} & {v_fec} & {v_obs} \\\\ \\hline")
    if not filas_cambios:
        filas_cambios.append("        0 & Análisis Estudio Coordinación de Protecciones. & 23/09/2026 & \\\\ \\hline")
    contenido_filas_cambios = "\n".join(filas_cambios)

    # 3. Sistema AC y Tablas CNO
    ac_fases = params.get("ac_fases", r"$3~\phi$")
    ac_etiqueta_pot = escapar_latex(params.get("ac_etiqueta_pot", "Potencia"))
    ac_tension_kv = escapar_latex(params.get("ac_tension_kv", "0,48"))
    ac_corriente_max = escapar_latex(params.get("ac_corriente_max", "1081"))
    ac_factor_carga = escapar_latex(params.get("ac_factor_carga", "1,25"))
    ac_proteccion_tablero = escapar_latex(params.get("ac_proteccion_tablero", "1353*"))
    ac_nota_pie = escapar_latex(params.get("ac_nota_pie", "*Nota: Valor de protección ajustado a 1360 A."))

    bloque_nota_ac = ""
    if ac_nota_pie.strip():
        bloque_nota_ac = f"""
        \\vspace{{2mm}}\\\\
        {{\\centering\\footnotesize
        \\textbf{{\\textit{{{ac_nota_pie}}}}}\\par
        }}"""

    clave_rango_cno = params.get("rango_potencia_cno", "P_025_TO_1")
    es_menor_025 = (clave_rango_cno == "P_LE_025")

    default_caption_func = (
        r"Funciones de protección mínimas para sistemas de generación basados en inversores y frecuencia variable de capacidad instalada o nominal $\leq$ 0,25 MW."
        if es_menor_025 else
        r"Funciones de protección mínimas para sistemas de generación basados en inversores y frecuencia variable de capacidad instalada o nominal mayor > 0,25 MW."
    )
    caption_func_cno = str(params.get("tabla_funciones_caption") or default_caption_func).strip()

    default_caption_ajustes = (
        r"Ajuste de protección sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal $\leq$ 0,25 MW conectados al SDL"
        if es_menor_025 else
        r"Ajuste de protección sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal > 0,25 MW conectados al SDL"
    )
    caption_ajustes_cno = str(params.get("tabla_ajustes_caption") or default_caption_ajustes).strip()

    texto_intro_ajustes = (
        rf"A continuación, se presenta el ajuste de protecciones de tensión y frecuencia con los respectivos tiempos de disparo recomendados por el acuerdo CNO {norma_cno} para los sistemas de generación basados en inversores menores o iguales a 0.25 MW (Tabla 11):\\"
        if es_menor_025 else
        rf"A continuación, se presenta el ajuste de protecciones de tensión y frecuencia con los respectivos tiempos de disparo recomendados por el acuerdo CNO {norma_cno} para los sistemas de generación basados en inversores mayores a 0.25 MW (Tabla 12):\\"
    )

    default_caption_resumen = (
        r"Resumen ajuste de protecciones sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal $\leq$ 0,25 MW conectados al SDL"
        if es_menor_025 else
        r"Resumen ajuste de protecciones sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal > 0,25 MW conectados al SDL"
    )
    caption_resumen_totales = str(params.get("tabla_resumen_caption") or params.get("caption_resumen_totales") or default_caption_resumen).strip()

    default_intro_cno = (
        f"Todo sistema de generación basados en inversores y frecuencia variable de capacidad instalada o nominal menor o igual a 0.25 MW (≤ 0.25 MW) conectado a los niveles 1, 2 y 3 deberá disponer de funciones de protección disponibles a nivel de inversor conforme a la Tabla 6 del Acuerdo CNO {norma_cno}, coordinando oportunamente con la red del OR."
        if es_menor_025 else
        f"Todo el sistema de generación basados en inversores y frecuencia variable conectado a los niveles 1, 2 y 3 deberán disponer de un esquema de protección para proteger la instalación del generador y su punto de conexión con el sistema de distribución local, los cuales deberán ser selectivos y coordinar con la red existente, según el acuerdo CNO {norma_cno}."
    )
    raw_intro = params.get("intro_cno_txt", default_intro_cno)
    if "Acuerdo CNO 2233" in raw_intro and norma_cno != "2233":
        raw_intro = raw_intro.replace("Acuerdo CNO 2233", f"Acuerdo CNO {norma_cno}")
    if "acuerdo CNO 2233" in raw_intro and norma_cno != "2233":
        raw_intro = raw_intro.replace("acuerdo CNO 2233", f"acuerdo CNO {norma_cno}")
    intro_cno_txt = raw_intro

    df_func_prot = params.get("df_funciones_prot", None)
    filas_func_prot = []
    if df_func_prot is not None and isinstance(df_func_prot, pd.DataFrame) and not df_func_prot.empty:
        for _, r in df_func_prot.iterrows():
            c1 = escapar_latex(r.get("Función de protección", ""))
            c2 = escapar_latex(r.get("PC", ""))
            c3 = escapar_latex(r.get("UG", ""))
            c4 = escapar_latex(r.get("Notas", ""))
            filas_func_prot.append(f"            {c1} & {c2} & {c3} & {c4} \\\\ \\hline")
    if not filas_func_prot:
        if es_menor_025:
            filas_func_prot = [
                "            Bajatensión (ANSI 27) & & X & m \\\\ \\hline",
                "            Sobrepotencia adelante (ANSI 32) & X & & k \\\\ \\hline",
                "            Sobrecorriente de fases y tierra & & & l \\\\ \\hline",
                "            Sobretensión (ANSI 59) & & X & m \\\\ \\hline",
                "            Frecuencia (ANSI 81U/O) & & X & p \\\\ \\hline",
                "            Anti - isla & & X & q \\\\ \\hline",
                "            Verificación de sincronismo & & & r \\\\ \\hline",
            ]
        else:
            filas_func_prot = [
                "            Bajatensión (ANSI 27) & X & & m \\\\ \\hline",
                "            Sobrepotencia adelante (ANSI 32) & X & & k \\\\ \\hline",
                "            Sobrecorriente de fases y tierra & X & & l \\\\ \\hline",
                "            Sobretensión (ANSI 59) & X & & m \\\\ \\hline",
                "            Sobretensión de secuencia cero (ANSI 59N) & X & & n \\\\ \\hline",
                "            Frecuencia (ANSI 81U/O) & & & p \\\\ \\hline",
                "            Anti - isla & X & & q \\\\ \\hline",
                "            Verificación sincronismo/Chequeo energización & X & & r \\\\ \\hline",
            ]
    contenido_filas_func_prot = "\n".join(filas_func_prot)

    obs_cno_1 = params.get(
        "obs_cno_1",
        "La protección ANSI 32 no aplica, dado que el proyecto es un generador distribuido, y esta función aplicará solo para autogeneradores con o sin entregar excedentes a la red."
    )
    obs_cno_2 = params.get(
        "obs_cno_2",
        "Para la verificación de sincronismo, conforme a la nota “r” del acuerdo se implementará en el PC la función 25 configurando solamente la condición de Barra viva OR - Línea muerta PV, con un umbral mínimo de tensión de 0.8 p.u que garantice que el sistema no permitirá energización cuando el sistema del OR se encuentre sin tensión"
    )

    df_ajustes_cno = params.get("df_ajustes_cno", None)
    filas_ajustes_cno = []
    if df_ajustes_cno is not None and isinstance(df_ajustes_cno, pd.DataFrame) and not df_ajustes_cno.empty:
        for _, r in df_ajustes_cno.iterrows():
            f_nom = escapar_latex(r.get("Función", ""))
            f_aj = str(r.get("Ajustes", "")).strip()
            if "\\leq" not in f_aj and "\\geq" not in f_aj:
                f_aj = escapar_latex(f_aj)
            f_tmp = str(r.get("Temporización", "")).strip()
            if "\\leq" not in f_tmp and "\\geq" not in f_tmp:
                f_tmp = escapar_latex(f_tmp)
            f_obs = escapar_latex(r.get("Observaciones", ""))
            filas_ajustes_cno.append(f"            {f_nom} & {f_aj} & {f_tmp} & {f_obs} \\\\ \\hline")
    if not filas_ajustes_cno:
        if es_menor_025:
            filas_ajustes_cno = [
                r"            Etapa 1: Bajatensión (ANSI 27) & $\leq$ 0.85 p.u. & $\geq$ 2 s & Coordinada con protecciones sobrecorriente OR \\ \hline",
                r"            Etapa 2: Bajatensión (ANSI 27)* & $\leq$ 0.5 p.u. & $\geq$ 0.2 s & Garantiza protección del inversor \\ \hline",
                r"            Etapa 1: Sobretensión (ANSI 59) & $\geq$ 1.15 p.u. & $\geq$ 2 s & Actuación trifásica \\ \hline",
                r"            Etapa 2: Sobretensión (ANSI 59) & $\geq$ 1.2 p.u. & $\geq$ 0.2 s & Actuación trifásica \\ \hline",
                r"            Bajafrecuencia (ANSI 81 U) & 57 Hz & $\geq$ 0.2 s & Actuación en inversores (F-T o F-F) \\ \hline",
                r"            Sobrefrecuencia (ANSI 81 O) & 63 Hz & $\geq$ 0.2 s & Actuación en inversores (F-T o F-F) \\ \hline",
            ]
        else:
            filas_ajustes_cno = [
                r"            Etapa 1: Baja tensión (ANSI 27) & $\leq$ 0.6 p.u & Ver nota & Actuación segregada por fase o trifásica \\ \hline",
                r"            Etapa 2: Baja tensión (ANSI 27) & $\leq$ 0.4 p.u & Ver nota & Actuación segregada por fase o trifásica \\ \hline",
                r"            Etapa 1: Sobretensión (ANSI 59) & $\geq$ 1.22 p.u & $\geq$ 2.5 s & Actuación trifásica \\ \hline",
                r"            Etapa 2: Sobretensión (ANSI 59) & $\geq$ 1.25 p.u & $\geq$ 0.5 s & Actuación trifásica \\ \hline",
                r"            Bajafrecuencia (ANSI 81U) & 57 Hz & $\geq$ 0.2 s & Actuación tensiones F-T \\ \hline",
                r"            Sobrefrecuencia (ANSI 81O) & 63 Hz & $\geq$ 0.2 s & Actuación tensiones F-T \\ \hline",
            ]
    contenido_filas_ajustes_cno = "\n".join(filas_ajustes_cno)

    # 4. Secciones 1.2 (27/59), 1.3 (59N) y 1.4 (Anti-Isla)
    incluir_img_2759 = params.get("incluir_img_2759", True)
    incluir_sec_59n = params.get("incluir_sec_59n", True)
    proteccion_tensiones_txt = params.get("proteccion_tensiones_txt", "")

    if incluir_img_2759:
        cmd_img_2759 = incluir_imagen_segura("Proteccion27-59.png", "max width=\\textwidth, max height=0.55\\textheight, keepaspectratio")
        bloque_fig_2759 = f"""
\\begin{{figure}}[H]
    \\centering
    {cmd_img_2759}
    \\caption{{Verificación ajustes ANSI 27/59 con curvas HVRT y LVRT}}
    \\label{{fig:proteccion27-59}}
\\end{{figure}}
"""
    else:
        bloque_fig_2759 = "\\phantomsection\\label{fig:proteccion27-59}%\n"

    df_3v0 = params.get("df_tres_vcero", None)
    filas_3v0 = []
    if df_3v0 is not None and isinstance(df_3v0, pd.DataFrame) and not df_3v0.empty:
        for _, r in df_3v0.iterrows():
            imp = escapar_latex(r.get("Impedancia de falla [ohms]", ""))
            kv = escapar_latex(r.get("3V0 [kV]", ""))
            pu = escapar_latex(r.get("3V0 [p.u]", ""))
            filas_3v0.append(f"            {imp} & {kv} & {pu} \\\\ \\hline")
    if not filas_3v0:
        filas_3v0 = [
            "            0 & 10.746 & 1.410 \\\\ \\hline",
            "            5 & 5.603 & 0.735 \\\\ \\hline",
            "            15 & 2.842 & 0.373 \\\\ \\hline",
        ]
    contenido_filas_3v0 = "\n".join(filas_3v0)

    texto_59n = params.get("texto_59n", "")
    texto_anti_isla = params.get("texto_anti_isla", "")

    if incluir_sec_59n:
        bloque_sec_59n = f"""
\\newpage
\\subsection{{\\textit{{Cálculos para la protección 59N}}}}
Para la definición del umbral de operación de la función de sobretensión de neutro (59N), se realizaron simulaciones de cortocircuito monofásico en el Punto de Conexión (PC), variando la impedancia de falla para evaluar la respuesta de la tensión residual (3V0) del sistema. En la siguiente tabla se observan los valores de 3V0 para cada tipo de falla:

\\tablatresVcero

{texto_59n}
"""
    else:
        bloque_sec_59n = ""

    # 5. Sección 1.5 (Sobrecorriente 51/50 y 51N/50N)
    incluir_reco_cabecera = params.get("incluir_reco_cabecera", True)
    incluir_reco_cto = params.get("incluir_reco_cto", False)
    df_reco_cab = params.get("df_reco_cabecera", None)
    df_reco_cto = params.get("df_reco_cto", None)
    txt_recierre_or = escapar_latex(params.get("txt_recierre_or", "El equipo cuentan con esquema de recierre de 1+1 ambos recierres con un tiempo muerto de 15 segundos."))

    bloques_recos_or = []
    if incluir_reco_cabecera:
        filas_cab = []
        if df_reco_cab is not None and isinstance(df_reco_cab, pd.DataFrame) and not df_reco_cab.empty:
            for _, r in df_reco_cab.iterrows():
                p1 = escapar_latex(r.get("Parámetro", ""))
                p2 = escapar_latex(r.get("Pick Up [Aprim]", ""))
                p3 = escapar_latex(r.get("DIAL [s]", ""))
                p4 = escapar_latex(r.get("Curva", ""))
                filas_cab.append(f"            {p1} & {p2} & {p3} & {p4} \\\\ \\hline")
        if not filas_cab:
            filas_cab = [
                "            ANSI 51 & 250 & 0,09 & IEC - EI \\\\ \\hline",
                "            ANSI 50 & 250 & 0,15 & DT \\\\ \\hline",
                "            ANSI 50-2 & 2400 & 0,0 & DT \\\\ \\hline",
                "            ANSI 51N & 120 & 0,38 & IEC - EI \\\\ \\hline",
                "            ANSI 50N & 2400 & 0,0 & DT \\\\ \\hline",
            ]
        str_filas_cab = "\n".join(filas_cab)
        bloques_recos_or.append(f"""
\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionof{{table}}{{Ajustes de protección para el Reconectador \\recocabecera.}}
        \\label{{tab:ajustesrecoCabecera}}
        \\begingroup
        \\adjustbox{{max width=\\textwidth}}{{%
        \\setlength{{\\tabcolsep}}{{8pt}}
        \\renewcommand{{\\arraystretch}}{{1.3}}
        \\begin{{tabular}}{{|l|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{1}}{{|c|}}{{\\color{{white}}\\textbf{{Parámetro}}}} & \\color{{white}}\\textbf{{Pick Up [Aprim]}} & \\color{{white}}\\textbf{{DIAL [s]}} & \\color{{white}}\\textbf{{Curva}} \\\\ \\hline
{str_filas_cab}
        \\end{{tabular}}%
        }}
        \\endgroup
    \\end{{minipage}}
\\end{{center}}
""")

    if incluir_reco_cto:
        filas_cto = []
        if df_reco_cto is not None and isinstance(df_reco_cto, pd.DataFrame) and not df_reco_cto.empty:
            for _, r in df_reco_cto.iterrows():
                p1 = escapar_latex(r.get("Parámetro", ""))
                p2 = escapar_latex(r.get("Pick Up [Aprim]", ""))
                p3 = escapar_latex(r.get("DIAL [s]", ""))
                p4 = escapar_latex(r.get("Curva", ""))
                filas_cto.append(f"            {p1} & {p2} & {p3} & {p4} \\\\ \\hline")
        if not filas_cto:
            filas_cto = [
                "            ANSI 51 & 65 & 0,1 & IEC - NI \\\\ \\hline",
                "            ANSI 50 & 117 & 0,05 & DT \\\\ \\hline",
                "            ANSI 51N & 22 & 0,1 & IEC - NI \\\\ \\hline",
                "            ANSI 50N & 63,8 & 0,05 & DT \\\\ \\hline",
            ]
        str_filas_cto = "\n".join(filas_cto)
        bloques_recos_or.append(f"""
\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionof{{table}}{{Ajustes de protección para el Reconectador \\recoCTO.}}
        \\label{{tab:ajustesrecoCTO}}
        \\begingroup
        \\adjustbox{{max width=\\textwidth}}{{%
        \\setlength{{\\tabcolsep}}{{8pt}}
        \\renewcommand{{\\arraystretch}}{{1.3}}
        \\begin{{tabular}}{{|l|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{1}}{{|c|}}{{\\color{{white}}\\textbf{{Parámetro}}}} & \\color{{white}}\\textbf{{Pick Up [Aprim]}} & \\color{{white}}\\textbf{{DIAL [s]}} & \\color{{white}}\\textbf{{Curva}} \\\\ \\hline
{str_filas_cto}
        \\end{{tabular}}%
        }}
        \\endgroup
    \\end{{minipage}}
\\end{{center}}
""")

    equipos_or_extra = params.get("equipos_or_extra", [])
    if isinstance(equipos_or_extra, list):
        for idx_ex, eq_ex in enumerate(equipos_or_extra):
            nom_ex = escapar_latex(eq_ex.get("nombre", f"Equipo OR {idx_ex + 1}"))
            lbl_ex = eq_ex.get("label", f"tab:ajustesrecoExtra{idx_ex + 1}")
            df_ex = eq_ex.get("df", None)
            filas_ex = []
            if df_ex is not None and isinstance(df_ex, pd.DataFrame) and not df_ex.empty:
                for _, r in df_ex.iterrows():
                    p1 = escapar_latex(r.get("Parámetro", ""))
                    p2 = escapar_latex(r.get("Pick Up [Aprim]", ""))
                    p3 = escapar_latex(r.get("DIAL [s]", ""))
                    p4 = escapar_latex(r.get("Curva", ""))
                    filas_ex.append(f"            {p1} & {p2} & {p3} & {p4} \\\\ \\hline")
            if filas_ex:
                str_filas_ex = "\n".join(filas_ex)
                bloques_recos_or.append(f"""
\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionof{{table}}{{Ajustes de protección para {nom_ex}.}}
        \\label{{{lbl_ex}}}
        \\begingroup
        \\adjustbox{{max width=\\textwidth}}{{%
        \\setlength{{\\tabcolsep}}{{8pt}}
        \\renewcommand{{\\arraystretch}}{{1.3}}
        \\begin{{tabular}}{{|l|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{1}}{{|c|}}{{\\color{{white}}\\textbf{{Parámetro}}}} & \\color{{white}}\\textbf{{Pick Up [Aprim]}} & \\color{{white}}\\textbf{{DIAL [s]}} & \\color{{white}}\\textbf{{Curva}} \\\\ \\hline
{str_filas_ex}
        \\end{{tabular}}%
        }}
        \\endgroup
    \\end{{minipage}}
\\end{{center}}
""")

    bloques_recos_or.append(txt_recierre_or)
    contenido_parametros_recos_or = "\n".join(bloques_recos_or)

    tipo_proteccion_principal = params.get("tipo_proteccion_principal", "Relé o Reconectador")
    es_modo_breaker = "Breaker" in str(tipo_proteccion_principal)

    calc_potencia = escapar_latex(params.get("calc_potencia", "900kW"))
    calc_tension = escapar_latex(params.get("calc_tension", "13.2kV" if not es_modo_breaker else "0.48kV"))
    calc_cosphi = escapar_latex(params.get("calc_cosphi", "1"))
    calc_in_val = escapar_latex(params.get("calc_in_val", "39.36" if not es_modo_breaker else "1081"))
    calc_i51p_exact = escapar_latex(params.get("calc_i51p_exact", "43.296"))
    calc_i51p_aprox = escapar_latex(params.get("calc_i51p_aprox", "44"))
    calc_i51n_exact = escapar_latex(params.get("calc_i51n_exact", "15.744"))
    calc_i51n_aprox = escapar_latex(params.get("calc_i51n_aprox", "16"))

    calc_factor_termico = escapar_latex(params.get("calc_factor_termico", "1.25"))
    calc_itermica_exact = escapar_latex(params.get("calc_itermica_exact", "1351.25"))
    calc_itermica_aprox = escapar_latex(params.get("calc_itermica_aprox", "1360"))
    calc_factor_magnetico = escapar_latex(params.get("calc_factor_magnetico", "2.5"))
    calc_imagnetica_exact = escapar_latex(params.get("calc_imagnetica_exact", "2702.5"))
    calc_imagnetica_aprox = escapar_latex(params.get("calc_imagnetica_aprox", "2720"))

    parrafo_calculo_50 = params.get("parrafo_calculo_50", "")

    caption_tabla_proy_raw = params.get("caption_tabla_proy", "")
    if not caption_tabla_proy_raw:
        if es_modo_breaker:
            caption_tabla_proy = r"Ajustes de protección para el Breaker \nombreProyecto."
        else:
            caption_tabla_proy = r"Ajustes de protección para el Reconectador \nombreProyecto."
    else:
        caption_tabla_proy = caption_tabla_proy_raw

    df_reco_proy = params.get("df_ajustes_reco_proy", None)
    filas_reco_proy = []
    if df_reco_proy is not None and isinstance(df_reco_proy, pd.DataFrame) and not df_reco_proy.empty:
        for _, r in df_reco_proy.iterrows():
            cols = list(r.index)
            p1 = escapar_latex(r.iloc[0]) if len(cols) > 0 else ""
            p2 = escapar_latex(r.iloc[1]) if len(cols) > 1 else ""
            p3 = escapar_latex(r.iloc[2]) if len(cols) > 2 else ""
            p4 = escapar_latex(r.iloc[3]) if len(cols) > 3 else ""
            filas_reco_proy.append(f"            {p1} & {p2} & {p3} & {p4} \\\\ \\hline")
    if not filas_reco_proy:
        if not es_modo_breaker:
            filas_reco_proy = [
                "            ANSI 51 & 44 & 0,05 & IEC - EI \\\\ \\hline",
                "            ANSI 50 & 200 & 0 & DT \\\\ \\hline",
                "            ANSI 51N & 16 & 0,05 & IEC - NI \\\\ \\hline",
                "            ANSI 50N & 1100 & 0 & DT \\\\ \\hline",
            ]
        else:
            filas_reco_proy = [
                "            Protección Térmica (L - Sobrecarga) & 1360 & Curva Térmica & Inversa \\\\ \\hline",
                "            Protección Magnética (I - Instantáneo) & 2720 & 0,0 & DT \\\\ \\hline",
                "            Protección Cortocircuito (S - Temporizado) & 2000 & 0,1 & DT \\\\ \\hline",
                "            Protección Falla a Tierra (G - Opcional) & 400 & 0,1 & DT \\\\ \\hline",
            ]
    contenido_filas_reco_proy = "\n".join(filas_reco_proy)

    if es_modo_breaker:
        encabezados_tabla_proy = r"\multicolumn{1}{|c|}{\color{white}\textbf{Parámetro / Función}} & \color{white}\textbf{Ajuste [A]} & \color{white}\textbf{Temporización} & \color{white}\textbf{Curva / Característica} \\ \hline"
    else:
        encabezados_tabla_proy = r"\multicolumn{1}{|c|}{\color{white}\textbf{Parámetro}} & \color{white}\textbf{Pick Up [Aprim]} & \color{white}\textbf{DIAL [s]} & \color{white}\textbf{Curva} \\ \hline"

    if not es_modo_breaker:
        bloque_formulas_sobrecorriente = f"""Los ajustes de protección de la función ANSI 51 del proyecto se calcularon con base en la corriente nominal del sistema por un factor de 1.1 según lo establecido en el acuerdo CNO {norma_cno}, para la función 51N se realiza el ajuste al 40\\% de la corriente nominal. A continuación se muestran las fórmulas para dichos cálculos:\\\\

\\textbf{{Cálculo de arranque 51P.}}\\\\
\\[ I_n = \\frac{{P}}{{\\sqrt{{3}} \\cdot V_L \\cdot \\cos(\\phi)}} \\quad ; \\quad I_{{51P}} = I_n \\cdot 1.1 \\]

\\vspace{{0.5cm}}
\\noindent Donde:
\\begin{{itemize}}
    \\item $I_{{n}}$: Corriente nominal.
    \\item $V_{{L}}$: Tensión del sistema.
    \\item $\\cos(\\phi)$: Factor de potencia.
    \\item $I_{{51P}}$: Corriente de la función 51P.
\\end{{itemize}}

Dado esto:

\\[ I_n = \\frac{{{calc_potencia}}}{{\\sqrt{{3}} \\cdot {calc_tension} \\cdot {calc_cosphi}}} \\]
\\[ I_n = {calc_in_val} \\quad ; \\quad I_{{51P}} = {calc_in_val} \\cdot 1.1 = {calc_i51p_exact} \\approx {calc_i51p_aprox} \\]

\\textbf{{Cálculo de arranque 51N.}}\\\\
\\[ I_{{51N}} = I_n \\cdot 0.4 \\]

\\vspace{{0.5cm}}
\\noindent \\textbf{{Donde:}}
\\begin{{itemize}}
    \\item $I_{{n}}$: Corriente nominal.
    \\item $I_{{51N}}$: Corriente de la función 51N.
\\end{{itemize}}

Dado esto, la corriente de la función 51N:

\\[ I_{{51N}} = {calc_in_val} \\cdot 0.4 = {calc_i51n_exact} \\approx {calc_i51n_aprox} \\]"""
    else:
        criterio_normativo_termomagnetico = params.get("criterio_normativo_termomagnetico", "")
        txt_normativo_tm = ""
        if criterio_normativo_termomagnetico and str(criterio_normativo_termomagnetico).strip():
            txt_normativo_tm = f"{str(criterio_normativo_termomagnetico).strip()}\n\\vspace{{0.4cm}}\n\n"
        bloque_formulas_sobrecorriente = f"""{txt_normativo_tm}Los ajustes de protección para el interruptor termomagnético / Breaker del proyecto se determinaron a partir de la corriente nominal de la instalación y los requerimientos de protección contra sobrecarga continua (función térmica) y cortocircuito (función magnética). A continuación se muestran las fórmulas para dichos cálculos:\\\\

\\textbf{{Cálculo de corriente nominal ($I_n$).}}\\\\
\\[ I_n = \\frac{{P}}{{\\sqrt{{3}} \\cdot V_L \\cdot \\cos(\\phi)}} \\]

\\vspace{{0.5cm}}
\\noindent Donde:
\\begin{{itemize}}
    \\item $I_{{n}}$: Corriente nominal.
    \\item $P$: Potencia del sistema.
    \\item $V_{{L}}$: Tensión del sistema.
    \\item $\\cos(\\phi)$: Factor de potencia.
\\end{{itemize}}

Dado esto:

\\[ I_n = \\frac{{{calc_potencia}}}{{\\sqrt{{3}} \\cdot {calc_tension} \\cdot {calc_cosphi}}} = {calc_in_val} \\]

\\vspace{{0.3cm}}
\\textbf{{Cálculo de la protección térmica de sobrecarga ($I_{{\\text{{t\\'ermica}}}}$ / Función L).}}\\\\
\\[ I_{{\\text{{t\\'ermica}}}} = I_n \\cdot {calc_factor_termico} \\]

\\vspace{{0.5cm}}
\\noindent \\textbf{{Donde:}}
\\begin{{itemize}}
    \\item $I_{{n}}$: Corriente nominal calculada.
    \\item $I_{{\\text{{t\\'ermica}}}}$: Corriente de ajuste térmico de sobrecarga o calibre del Breaker.
\\end{{itemize}}

Dado esto:

\\[ I_{{\\text{{t\\'ermica}}}} = {calc_in_val} \\cdot {calc_factor_termico} = {calc_itermica_exact} \\approx {calc_itermica_aprox} \\]

\\vspace{{0.3cm}}
\\textbf{{Cálculo de la protección magnética de cortocircuito ($I_{{\\text{{magn\\'etica}}}}$ / Función I/S).}}\\\\
\\[ I_{{\\text{{magn\\'etica}}}} = I_n \\cdot {calc_factor_magnetico} \\]

\\vspace{{0.5cm}}
\\noindent \\textbf{{Donde:}}
\\begin{{itemize}}
    \\item $I_{{n}}$: Corriente nominal.
    \\item $I_{{\\text{{magn\\'etica}}}}$: Corriente de disparo magnético instantáneo / temporizado.
\\end{{itemize}}

Dado esto:

\\[ I_{{\\text{{magn\\'etica}}}} = {calc_in_val} \\cdot {calc_factor_magnetico} = {calc_imagnetica_exact} \\approx {calc_imagnetica_aprox} \\]"""

    df_resumen_tot = params.get("df_resumen_totales", None)
    filas_resumen_tot = []
    if df_resumen_tot is not None and isinstance(df_resumen_tot, pd.DataFrame) and not df_resumen_tot.empty:
        for _, r in df_resumen_tot.iterrows():
            f1 = escapar_latex(r.get("Función", ""))
            f2 = escapar_latex(r.get("Ajustes", ""))
            f3 = escapar_latex(r.get("Temporización", ""))
            filas_resumen_tot.append(f"            {f1} & {f2} & {f3} \\\\ \\hline")
    if not filas_resumen_tot:
        filas_resumen_tot = [
            "            Etapa 1: Baja tensión (ANSI 27) & 0.6 p.u & 2 s \\\\ \\hline",
            "            Etapa 2: Baja tensión (ANSI 27) & 0.4 p.u & 1.5 s \\\\ \\hline",
            "            Etapa 1: Sobretensión (ANSI 59) & 1.22 p.u & 2.5 s \\\\ \\hline",
            "            Etapa 2: Sobretensión (ANSI 59) & 1.25 p.u & 0.5 s \\\\ \\hline",
            "            Sobretensión de neutro (ANSI 59N) & 0.3 p.u & 2 s \\\\ \\hline",
            "            Bajafrecuencia (ANSI 81U) & 57 Hz & 0.2 s \\\\ \\hline",
            "            Sobrefrecuencia (ANSI 81O) & 63 Hz & 0.2 s \\\\ \\hline",
            "            Anti-isla & Lógica compuesta con señales de tensión y frecuencia & 500ms \\\\ \\hline",
            "            Verificación de sincronismo & Condición barra viva OR - Línea muerta PV umbral de tensión 0.8p.u & NA \\\\ \\hline",
        ]
    contenido_filas_resumen_tot = "\n".join(filas_resumen_tot)

    es_con_cambio = params.get("es_con_cambio", False)
    conclusion_coord_txt = str(params.get("conclusion_coord_txt", "")).replace("\\cref{,tab:", "\\cref{tab:")
    bloques_tablas_cambio = []
    if es_con_cambio:
        if params.get("incluir_tabla_cambio_cab", False):
            df_ccab = params.get("df_cambio_cab", None)
            f_ccab = []
            if df_ccab is not None and isinstance(df_ccab, pd.DataFrame) and not df_ccab.empty:
                for _, r in df_ccab.iterrows():
                    par = escapar_latex(r.get("Parámetro", ""))
                    pa = escapar_latex(r.get("Pick Up Actual", ""))
                    da = escapar_latex(r.get("Dial Actual", ""))
                    ca = escapar_latex(r.get("Curva Actual", ""))
                    pp = formatear_celda_cambio(r.get("Pick Up Propuesto", ""))
                    dp = formatear_celda_cambio(r.get("Dial Propuesto", ""))
                    cp = formatear_celda_cambio(r.get("Curva Propuesta", ""))
                    f_ccab.append(f"            {par} & {pa} & {da} & {ca} & {pp} & {dp} & {cp} \\\\ \\hline")
            str_f_ccab = "\n".join(f_ccab)
            bloques_tablas_cambio.append(f"""
\\begin{{table}}[H]
    \\centering
    \\captionsetup{{hypcap=false}}
    \\captionof{{table}}{{Ajustes de protección propuestos para el Reconectador \\recocabecera.}}
    \\label{{tab:cambioAjustescabecera}}
    \\begingroup
    \\adjustbox{{max width=\\textwidth}}{{%
        \\renewcommand{{\\arraystretch}}{{1.5}}
        \\begin{{tabular}}{{|c|c|c|c|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\textbf{{\\color{{white}} }} & \\multicolumn{{3}}{{c|}}{{\\textbf{{\\color{{white}}Ajuste Actual}}}} & \\multicolumn{{3}}{{c|}}{{\\textbf{{\\color{{white}}Ajuste Propuesto}}}} \\\\ \\cline{{2-7}}
            \\rowcolor{{azulSeyep}}
            \\textbf{{\\color{{white}}\\smash{{\\raisebox{{2.2ex}}{{Parámetro}}}}}} & \\textbf{{\\color{{white}}Pick Up [A\\_prim]}} & \\textbf{{\\color{{white}}Dial [s]}} & \\textbf{{\\color{{white}}Curva}} & \\textbf{{\\color{{white}}Pick Up [A\\_prim]}} & \\textbf{{\\color{{white}}Dial [s]}} & \\textbf{{\\color{{white}}Curva}} \\\\ \\hline
{str_f_ccab}
        \\end{{tabular}}
    }}
    \\endgroup
\\end{{table}}
""")

        if params.get("incluir_tabla_cambio_cto", False):
            df_ccto = params.get("df_cambio_cto", None)
            f_ccto = []
            if df_ccto is not None and isinstance(df_ccto, pd.DataFrame) and not df_ccto.empty:
                for _, r in df_ccto.iterrows():
                    par = escapar_latex(r.get("Parámetro", ""))
                    pa = escapar_latex(r.get("Pick Up Actual", ""))
                    da = escapar_latex(r.get("Dial Actual", ""))
                    ca = escapar_latex(r.get("Curva Actual", ""))
                    pp = formatear_celda_cambio(r.get("Pick Up Propuesto", ""))
                    dp = formatear_celda_cambio(r.get("Dial Propuesto", ""))
                    cp = formatear_celda_cambio(r.get("Curva Propuesta", ""))
                    f_ccto.append(f"            {par} & {pa} & {da} & {ca} & {pp} & {dp} & {cp} \\\\ \\hline")
            str_f_ccto = "\n".join(f_ccto)
            bloques_tablas_cambio.append(f"""
\\begin{{table}}[H]
    \\centering
    \\captionsetup{{hypcap=false}}
    \\captionof{{table}}{{Ajustes de protección propuestos para el Reconectador \\recoCTO.}}
    \\label{{tab:cambioAjustes}}
    \\begingroup
    \\adjustbox{{max width=\\textwidth}}{{%
        \\renewcommand{{\\arraystretch}}{{1.5}}
        \\begin{{tabular}}{{|c|c|c|c|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\textbf{{\\color{{white}} }} & \\multicolumn{{3}}{{c|}}{{\\textbf{{\\color{{white}}Ajuste Actual}}}} & \\multicolumn{{3}}{{c|}}{{\\textbf{{\\color{{white}}Ajuste Propuesto}}}} \\\\ \\cline{{2-7}}
            \\rowcolor{{azulSeyep}}
            \\textbf{{\\color{{white}}\\smash{{\\raisebox{{2.2ex}}{{Parámetro}}}}}} & \\textbf{{\\color{{white}}Pick Up [A\\_prim]}} & \\textbf{{\\color{{white}}Dial [s]}} & \\textbf{{\\color{{white}}Curva}} & \\textbf{{\\color{{white}}Pick Up [A\\_prim]}} & \\textbf{{\\color{{white}}Dial [s]}} & \\textbf{{\\color{{white}}Curva}} \\\\ \\hline
{str_f_ccto}
        \\end{{tabular}}
    }}
    \\endgroup
\\end{{table}}
""")

        cambios_or_extra = params.get("cambios_or_extra", [])
        if isinstance(cambios_or_extra, list):
            for idx_cex, c_ex in enumerate(cambios_or_extra):
                nom_cex = escapar_latex(c_ex.get("nombre", f"Equipo OR {idx_cex + 1}"))
                lbl_cex = c_ex.get("label", f"tab:cambioAjustesExtra{idx_cex + 1}")
                df_cex = c_ex.get("df", None)
                f_cex = []
                if df_cex is not None and isinstance(df_cex, pd.DataFrame) and not df_cex.empty:
                    for _, r in df_cex.iterrows():
                        par = escapar_latex(r.get("Parámetro", ""))
                        pa = escapar_latex(r.get("Pick Up Actual", ""))
                        da = escapar_latex(r.get("Dial Actual", ""))
                        ca = escapar_latex(r.get("Curva Actual", ""))
                        pp = formatear_celda_cambio(r.get("Pick Up Propuesto", ""))
                        dp = formatear_celda_cambio(r.get("Dial Propuesto", ""))
                        cp = formatear_celda_cambio(r.get("Curva Propuesta", ""))
                        f_cex.append(f"            {par} & {pa} & {da} & {ca} & {pp} & {dp} & {cp} \\\\ \\hline")
                if f_cex:
                    str_f_cex = "\n".join(f_cex)
                    bloques_tablas_cambio.append(f"""
\\begin{{table}}[H]
    \\centering
    \\captionsetup{{hypcap=false}}
    \\captionof{{table}}{{Ajustes de protección propuestos para {nom_cex}.}}
    \\label{{{lbl_cex}}}
    \\begingroup
    \\adjustbox{{max width=\\textwidth}}{{%
        \\renewcommand{{\\arraystretch}}{{1.5}}
        \\begin{{tabular}}{{|c|c|c|c|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\textbf{{\\color{{white}} }} & \\multicolumn{{3}}{{c|}}{{\\textbf{{\\color{{white}}Ajuste Actual}}}} & \\multicolumn{{3}}{{c|}}{{\\textbf{{\\color{{white}}Ajuste Propuesto}}}} \\\\ \\cline{{2-7}}
            \\rowcolor{{azulSeyep}}
            \\textbf{{\\color{{white}}\\smash{{\\raisebox{{2.2ex}}{{Parámetro}}}}}} & \\textbf{{\\color{{white}}Pick Up [A\\_prim]}} & \\textbf{{\\color{{white}}Dial [s]}} & \\textbf{{\\color{{white}}Curva}} & \\textbf{{\\color{{white}}Pick Up [A\\_prim]}} & \\textbf{{\\color{{white}}Dial [s]}} & \\textbf{{\\color{{white}}Curva}} \\\\ \\hline
{str_f_cex}
        \\end{{tabular}}
    }}
    \\endgroup
\\end{{table}}
""")

        nota_dt = str(params.get("nota_disparo_transferido", "")).strip()
        if nota_dt:
            bloques_tablas_cambio.append(f"\n{nota_dt}\n")

    contenido_tablas_cambio = "\n".join(bloques_tablas_cambio)

    # 6. Sección 2: ANEXOS
    incluir_anexos = params.get("incluir_anexos", True)
    omitir_no_cargados = params.get("omitir_no_cargados", False)
    incluir_fallas_30ohms = params.get("incluir_fallas_30ohms", False)
    incluir_cortos_anexo = params.get("incluir_cortos_anexo", False)
    intro_anexos_txt = params.get("intro_anexos_txt", "")

    def bloque_ilustracion(archivo_img, caption_tex, label_tex, ancho_box="1\\textwidth"):
        if omitir_no_cargados and not resolver_ruta_imagen(archivo_img):
            return ""
        cmd = incluir_imagen_segura(archivo_img, usar_resizebox=True, ancho_resize=ancho_box)
        return f"""
\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionsetup{{hypcap=false}}
        {cmd}
        \\vspace{{0.0cm}}
        \\captionof{{ilustracion}}{{{caption_tex}}}
        \\label{{{label_tex}}}
    \\end{{minipage}}
\\end{{center}}
"""

    bloques_anexos_total = []
    if incluir_anexos:
        if incluir_cortos_anexo:
            for anio_c in [year_inicial, year_final]:
                items_c = [
                    bloque_ilustracion("ICC 1F GCP.png", "Corriente de cortocircuito monofásica con GD .", f"ilus:ICC1FGCP{anio_c}", "0.9\\textwidth"),
                    bloque_ilustracion("ICC 1F GSP.png", "Corriente de cortocircuito monofásica sin GD .", f"ilus:ICC1FGSP{anio_c}", "0.9\\textwidth"),
                    bloque_ilustracion("ICC 3F GCP.png", "Corriente de cortocircuito trifásica con GD .", f"ilus:ICC3FGCP{anio_c}", "0.9\\textwidth"),
                    bloque_ilustracion("ICC 3F GSP.png", "Corriente de cortocircuito trifásica sin GD .", f"ilus:ICC3FGSP{anio_c}", "0.9\\textwidth"),
                ]
                items_c = [x for x in items_c if x.strip()]
                if items_c:
                    bloques_anexos_total.append(f"""
\\newpage
\\begin{{center}}
    \\vspace*{{\\fill}}
    \\Huge \\textbf{{CORTO {anio_c}}}
    \\vspace*{{\\fill}}
\\end{{center}}
\\newpage
""" + "\n".join(items_c))

        # Bloque PROTECCIONES
        items_alta = [
            bloque_ilustracion("Protecciones falla lado alta proyecto.png", "Falla Barra en lado de alta trafo GD \\nombreProyecto .", "ilus:Pfallaladoalta"),
            bloque_ilustracion("Protecciones falla 1F franca lado alta proyecto.png", "Falla monofásica franca barra en lado de alta trafo GD \\nombreProyecto .", "ilus:Pfalla1Ffrancaladoalta"),
            bloque_ilustracion("Protecciones falla 1F 5ohms lado alta proyecto.png", "Falla monofásica 5ohms barra en lado de alta trafo GD \\nombreProyecto .", "ilus:Pfalla1F5ohmsladoalta"),
            bloque_ilustracion("Protecciones falla 1F 15ohms lado alta proyecto.png", "Falla monofásica 15ohms barra en lado de alta trafo GD \\nombreProyecto .", "ilus:Pfalla1F15ohmsladoalta"),
        ]
        if incluir_fallas_30ohms:
            items_alta.append(bloque_ilustracion("Protecciones falla 1F 30ohms lado alta proyecto.png", "Falla monofásica 30ohms barra en lado de alta trafo GD \\nombreProyecto .", "ilus:Pfalla1F30ohmsladoalta", "0.9\\textwidth"))
        items_alta.extend([
            bloque_ilustracion("Protecciones falla 3F franca lado alta proyecto.png", "Falla trifásica franca barra en lado de alta trafo GD \\nombreProyecto .", "ilus:Pfalla3Ffrancaladoalta"),
            bloque_ilustracion("Protecciones falla 3F 5ohms lado alta proyecto.png", "Falla trifásica 5ohms barra en lado de alta trafo GD \\nombreProyecto .", "ilus:Pfalla3F5ohmsladoalta"),
            bloque_ilustracion("Protecciones falla 3F 15ohms lado alta proyecto.png", "Falla trifásica 15ohms barra en lado de alta trafo GD \\nombreProyecto .", "ilus:Pfalla3F15ohmsladoalta"),
        ])
        if incluir_fallas_30ohms:
            items_alta.append(bloque_ilustracion("Protecciones falla 3F 30ohms lado alta proyecto.png", "Falla trifásica 30ohms barra en lado de alta trafo GD \\nombreProyecto .", "ilus:Pfalla3F30ohmsladoalta", "0.9\\textwidth"))
        items_alta = [x for x in items_alta if x.strip()]

        items_baja = [
            bloque_ilustracion("Protecciones falla lado baja proyecto.png", "Falla Barra en lado de baja trafo GD \\nombreProyecto .", "ilus:Pfallaladobaja"),
            bloque_ilustracion("Protecciones falla 1F franca lado baja proyecto.png", "Falla monofásica franca barra en lado de baja trafo GD \\nombreProyecto .", "ilus:Pfalla1Ffrancaladobaja"),
            bloque_ilustracion("Protecciones falla 3F franca lado baja proyecto.png", "Falla trifásica franca barra en lado de baja trafo GD \\nombreProyecto .", "ilus:Pfalla3Ffrancaladobaja"),
        ]
        items_baja = [x for x in items_baja if x.strip()]

        items_nodo = [
            bloque_ilustracion("Protecciones falla nodo conexión proyecto.png", "Falla en nodo conexión del circuito \\CTO .", "ilus:Pfallanodoconexion"),
            bloque_ilustracion("Protecciones falla 1F franca nodo conexión proyecto.png", "Falla monofásica franca nodo conexión del circuito \\CTO .", "ilus:Pfalla1Ffrancanodoconexion"),
            bloque_ilustracion("Protecciones falla 1F 5ohms nodo conexión proyecto.png", "Falla monofásica 5ohms nodo conexión del circuito \\CTO .", "ilus:Pfalla1F10ohmsnodoconexion"),
            bloque_ilustracion("Protecciones falla 1F 15ohms nodo conexión proyecto.png", "Falla monofásica 15ohms nodo conexión del circuito \\CTO .", "ilus:Pfalla1F15ohmsnodoconexion"),
        ]
        if incluir_fallas_30ohms:
            items_nodo.append(bloque_ilustracion("Protecciones falla 1F 30ohms nodo conexión proyecto.png", "Falla monofásica 30ohms nodo conexión del circuito \\CTO .", "ilus:Pfalla1F30ohmsnodoconexion", "0.9\\textwidth"))
        items_nodo.extend([
            bloque_ilustracion("Protecciones falla 3F franca nodo conexión proyecto.png", "Falla trifásica franca nodo conexión del circuito \\CTO .", "ilus:Pfalla13francanodoconexion"),
            bloque_ilustracion("Protecciones falla 3F 5ohms nodo conexión proyecto.png", "Falla trifásica 5ohms nodo conexión del circuito \\CTO .", "ilus:Pfalla3F5ohmsnodoconexion"),
            bloque_ilustracion("Protecciones falla 3F 15ohms nodo conexión proyecto.png", "Falla trifásica 15ohms nodo conexión del circuito \\CTO .", "ilus:Pfalla3F15ohmsnodoconexion"),
        ])
        if incluir_fallas_30ohms:
            items_nodo.append(bloque_ilustracion("Protecciones falla 3F 30ohms nodo conexión proyecto.png", "Falla trifásica 30ohms nodo conexión del circuito \\CTO .", "ilus:Pfalla3F30ohmsnodoconexion", "0.9\\textwidth"))
        items_nodo = [x for x in items_nodo if x.strip()]

        if items_alta or items_baja or items_nodo:
            bloques_anexos_total.append("""
\\newpage
\\begin{center}
    \\vspace*{\\fill}
    \\Huge \\textbf{PROTECCIONES}
    \\vspace*{\\fill}
\\end{center}
""")
            if items_alta:
                bloques_anexos_total.append("\\newpage\n" + "\n".join(items_alta))
            if items_baja:
                bloques_anexos_total.append("\\newpage\n" + "\n".join(items_baja))
            if items_nodo:
                bloques_anexos_total.append("\\newpage\n" + "\n".join(items_nodo))

    if incluir_anexos:
        cuerpo_anexos = "\n".join(bloques_anexos_total)
        bloque_seccion_anexos = f"""
\\clearpage
\\section{{ANEXOS}}
{intro_anexos_txt}
\\clearpage
\\renewcommand{{\\listilustracionname}}{{Índice de Ilustraciones}}
\\listofilustraciones
\\vspace{{1cm}}
{cuerpo_anexos}
"""
    else:
        bloque_seccion_anexos = ""

    # Logo de Portada
    logo_resuelto = resolver_ruta_imagen("Logo_Cliente.png")
    if logo_resuelto:
        bloque_logo = f"\\includegraphics[width=0.3\\textwidth]{{{logo_resuelto}}} \\\\[2cm]"
    else:
        bloque_logo = "\\vspace*{2cm}"

    comandos_definiciones = f"""
% ---------- Variables del proyecto ----------
\\newcommand{{\\mesentregainformemasyear}}{{{mes_entrega}}}
\\newcommand{{\\nombreProyecto}}{{{nombre_proyecto}}}
\\newcommand{{\\capacidadMW}}{{{capacidad_mw}}}
\\newcommand{{\\OR}}{{{operador_red}}}
\\newcommand{{\\FechaEntrada}}{{{fecha_entrada}}}
\\newcommand{{\\Latitud}}{{{latitud}}}
\\newcommand{{\\Longitud}}{{{longitud}}}
\\newcommand{{\\YearInicial}}{{{year_inicial}}}
\\newcommand{{\\YearFinal}}{{{year_final}}}
\\newcommand{{\\CTO}}{{{cto}}}
\\newcommand{{\\SSEE}}{{{ssee}}}
\\newcommand{{\\NT}}{{{nt}}}
\\newcommand{{\\nodo}}{{{nodo}}}
\\newcommand{{\\elementoProteccion}}{{{elemento_proteccion}}}
\\newcommand{{\\referenciaPanel}}{{{referencia_panel}}}
\\newcommand{{\\potenciaPanel}}{{{potencia_panel}}}
\\newcommand{{\\cantidadPanel}}{{{cantidad_panel}}}
\\newcommand{{\\ubicacion}}{{{ubicacion}}}
\\newcommand{{\\refInversoruno}}{{{ref_inv_1}}}
\\newcommand{{\\Inversoruno}}{{{mod_inv_1}}}
\\newcommand{{\\cantidadInversoruno}}{{{cant_inv_1}}}
\\newcommand{{\\generacionaprobada}}{{{generacion_aprobada}}}
\\newcommand{{\\recoCTO}}{{{reco_cto}}}
\\newcommand{{\\tipoproteccion}}{{{tipo_proteccion}}}
\\newcommand{{\\recocabecera}}{{{reco_cabecera}}}
\\newcommand{{\\normaCNO}}{{{norma_cno}}}

% ---------- Variables 59N ----------
\\newcommand{{\\tresVceroMASALTA}}{{{tres_vcero_mas_alta}}}
\\newcommand{{\\tresVceroMASALTAkV}}{{{tres_vcero_mas_alta_kv}}}
\\newcommand{{\\ajustetresVcero}}{{{ajuste_tres_vcero}}}
\\newcommand{{\\magajustetresVcero}}{{{mag_ajuste_tres_vcero}}}

%=============================Tabla control cambios===============================================
\\newcommand{{\\controlcambios}}{{%
    \\begingroup
    \\adjustbox{{max width=\\textwidth}}{{%
    \\renewcommand{{\\arraystretch}}{{1.2}}
    \\begin{{tabular}}{{|c|l|c|l|}}
        \\hline
        \\rowcolor{{azulSeyep}}
        \\textbf{{\\textcolor{{white}}{{VERSIÓN No.}}}} &
        \\textbf{{\\textcolor{{white}}{{DESCRIPCIÓN}}}} &
        \\textbf{{\\textcolor{{white}}{{FECHA}}}} &
        \\textbf{{\\textcolor{{white}}{{OBSERVACIONES}}}} \\\\
        \\hline
{contenido_filas_cambios}
    \\end{{tabular}}%
    }}
    \\endgroup
}}

%============================ SISTEMA AC ============================
\\newcommand{{\\sistemaAC}}{{%
Para el cálculo de la protección general de los inversores, se tuvieron en cuenta los siguientes parámetros:
\\begin{{center}}
    \\begin{{minipage}}{{0.9\\textwidth}}
        \\centering
        \\captionof{{table}}{{Sistema AC}}
        \\label{{tab:sistema_AC}}
        \\begingroup
        \\adjustbox{{max width=\\linewidth}}{{%
        \\setlength{{\\tabcolsep}}{{10pt}}
        \\renewcommand{{\\arraystretch}}{{1.3}}
        \\begin{{tabular}}{{|l|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{2}}{{|c|}}{{\\color{{white}}\\textbf{{Sistema AC}}}} \\\\ \\hline
            \\multicolumn{{2}}{{|c|}}{{Protección arreglo de inversores AC}} \\\\ \\hline
            Sistema AC & {ac_fases} \\\\ \\hline
            {ac_etiqueta_pot} & \\capacidadMW \\\\ \\hline
            Tensión de Línea [kV] & {ac_tension_kv} \\\\ \\hline
            Intensidad máxima [A] & {ac_corriente_max} \\\\ \\hline
            Factor de carga continua & {ac_factor_carga} \\\\ \\hline
            Protección en tablero principal ($\\text{{I}}_{{\\text{{max}}}} \\times {ac_factor_carga}$) [A] & {ac_proteccion_tablero} \\\\ \\hline
        \\end{{tabular}}%
        }}
        \\endgroup{bloque_nota_ac}
    \\end{{minipage}}
\\end{{center}}
}}

%============= EQUIPOS PROTECCIÓN RECO OR ===================
\\newcommand{{\\ParametrosRECOSOR}}{{%
{contenido_parametros_recos_or}
}}

%============= PROTECCIÓN TENSIONES ===================
\\newcommand{{\\protecciontensiones}}{{%
{proteccion_tensiones_txt}
}}

%============= AJUSTES 59N ===================
\\newcommand{{\\tablatresVcero}}{{%
\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionof{{table}}{{Verificación tensión 3V0 ante fallas monofásicas en el PC}}
        \\label{{tab:tresVcero}}
        \\begingroup
        \\adjustbox{{max width=0.9\\textwidth}}{{%
        \\setlength{{\\tabcolsep}}{{8pt}}
        \\renewcommand{{\\arraystretch}}{{1.2}}
        \\begin{{tabular}}{{|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{1}}{{|c|}}{{\\color{{white}}\\textbf{{Impedancia de falla [ohms]}}}} & \\color{{white}}\\textbf{{3V0 [kV]}} & \\color{{white}}\\textbf{{3V0 [p.u]}} \\\\ \\hline
{contenido_filas_3v0}
        \\end{{tabular}}%
        }}
        \\endgroup
    \\end{{minipage}}
\\end{{center}}
}}

%============= AJUSTES PROTECCIONES PROYECTO ===================
\\newcommand{{\\Ajustessobrecorrienteproyecto}}{{%
{bloque_formulas_sobrecorriente}

{parrafo_calculo_50}

\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionof{{table}}{{{caption_tabla_proy}}}
        \\label{{tab:ajustesrecoProyecto}}
        \\begingroup
        \\adjustbox{{max width=\\textwidth}}{{%
        \\setlength{{\\tabcolsep}}{{8pt}}
        \\renewcommand{{\\arraystretch}}{{1.3}}
        \\begin{{tabular}}{{|l|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            {encabezados_tabla_proy}
{contenido_filas_reco_proy}
        \\end{{tabular}}%
        }}
        \\endgroup
    \\end{{minipage}}
\\end{{center}}

\\begin{{table}}[H]
    \\centering
    \\caption{{{caption_resumen_totales}}}
    \\label{{tab:resumenajustestotales}}
    \\begingroup
    \\adjustbox{{max width=\\textwidth}}{{%
        \\renewcommand{{\\arraystretch}}{{1.3}}
        \\begin{{tabular}}{{|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\textbf{{\\color{{white}}Función}} & \\textbf{{\\color{{white}}Ajustes}} & \\textbf{{\\color{{white}}Temporización}} \\\\ \\hline
{contenido_filas_resumen_tot}
        \\end{{tabular}}
    }}
    \\endgroup
\\end{{table}}

{conclusion_coord_txt}

{contenido_tablas_cambio}
}}
"""

    cuerpo_documento = f"""
\\begin{{document}}

% --- PORTADA ---
\\begin{{titlepage}}
    \\thispagestyle{{fancy}}
    \\centering
    \\vspace*{{4cm}}
    {{\\fontsize{{20}}{{30}}\\selectfont \\textbf{{ANEXO EACP}}}} \\\\[0.1cm]

    {{\\fontsize{{22}}{{30}}\\selectfont \\textbf{{\\nombreProyecto{{}} - \\capacidadMW}}}} \\\\[3cm]
    {bloque_logo}

    \\vfill
    {{\\Large \\textbf{{Versión: 0}}}} \\\\[0.8cm]
    {{\\Large Medellín, Colombia.}} \\\\
    {{\\Large \\mesentregainformemasyear}}\\\\[0.5cm]
\\end{{titlepage}}
\\newpage

% --- CONTROL DE CAMBIOS ---
\\begin{{center}}
\\section*{{CONTROL DE CAMBIOS.}}
    \\definecolor{{azulSeyep}}{{RGB}}{{0, 103, 254}}
    \\renewcommand{{\\arraystretch}}{{1.5}}
    \\controlcambios
\\end{{center}}
\\newpage

% --- CONFIGURACIÓN DE LA TABLA DE CONTENIDO ---
\\renewcommand{{\\contentsname}}{{TABLA DE CONTENIDO}}
\\tableofcontents
\\newpage

% --- CONFIGURACIÓN DEL ÍNDICE DE TABLAS ---
\\renewcommand{{\\listtablename}}{{ÍNDICE DE TABLAS}}
\\begin{{center}}
    \\listoftables
\\end{{center}}
\\newpage

% --- CONFIGURACIÓN DEL ÍNDICE DE FIGURAS ---
\\renewcommand{{\\listfigurename}}{{ÍNDICE DE FIGURAS}}
\\begin{{center}}
    \\listoffigures
\\end{{center}}
\\newpage

\\section{{EACP}}
Con el fin de verificar las protecciones se presenta la siguiente información técnica de los elementos a tener en cuenta en el proyecto.
\\\\

\\sistemaAC

\\subsection{{\\textit{{Protecciones sistémicas a implementar en el proyecto}}}}

{intro_cno_txt}

\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionof{{table}}{{{caption_func_cno}}}
        \\label{{tab:funciones_proteccion}}
        \\begingroup
        \\adjustbox{{max width=\\textwidth}}{{%
        \\setlength{{\\tabcolsep}}{{8pt}}
        \\renewcommand{{\\arraystretch}}{{1.2}}
        \\begin{{tabular}}{{|l|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{1}}{{|c|}}{{\\color{{white}}\\textbf{{Función de protección}}}} & \\color{{white}}\\textbf{{PC}} & \\color{{white}}\\textbf{{UG}} & \\color{{white}}\\textbf{{Notas}} \\\\ \\hline
{contenido_filas_func_prot}
        \\end{{tabular}}%
        }}
        \\endgroup
    \\end{{minipage}}
\\end{{center}}

Conforme a las notas del acuerdo CNO, se tienen las siguientes observaciones sobre las protecciones a implementar:
\\begin{{itemize}}
    \\item {{{obs_cno_1}}}
    \\item {{{obs_cno_2}}}
\\end{{itemize}}

{texto_intro_ajustes}

\\begin{{table}}[H]
    \\centering
    \\caption{{{caption_ajustes_cno}}}
    \\label{{tab:AjustesproteccionCNO}}
    \\begingroup
    \\adjustbox{{max width=\\textwidth}}{{%
        \\renewcommand{{\\arraystretch}}{{1.3}}
        \\begin{{tabular}}{{|c|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\textbf{{\\color{{white}}Función}} & \\textbf{{\\color{{white}}Ajustes}} & \\textbf{{\\color{{white}}Temporización}} & \\textbf{{\\color{{white}}Observaciones}} \\\\ \\hline
{contenido_filas_ajustes_cno}
        \\end{{tabular}}
    }}
    \\endgroup
\\end{{table}}

\\newpage
\\subsection{{\\textit{{Cálculos para las protecciones 27 y 59}}}}
\\protecciontensiones
{bloque_fig_2759}
{bloque_sec_59n}
\\subsection{{\\textit{{Cálculos para la protección Anti-isla}}}}
{texto_anti_isla}

\\subsection{{\\textit{{Cálculos para las protecciones 51/50 y 51N/50N}}}}
Antes de calcular las protecciones del reconectador del punto de conexión, es importante conocer los ajustes de los elementos de protección aguas arriba del equipo, los cuales fueron suministrados por el OR, en la \\cref{{tab:ajustesrecoCabecera}} se muestran los ajustes de los elementos de protección de sobrecorriente existentes en el circuito:

\\ParametrosRECOSOR

\\Ajustessobrecorrienteproyecto

{bloque_seccion_anexos}

\\end{{document}}
"""

    contenido_latex = generar_preambulo() + comandos_definiciones + cuerpo_documento
    tex_filename = "Anexo_EACP.tex"
    pdf_filename = "Anexo_EACP.pdf"

    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write(contenido_latex)

    import shutil
    import glob

    def buscar_ejecutable_pdflatex():
        # 1. Probar en PATH del sistema
        ejecutable = shutil.which("pdflatex") or shutil.which("pdflatex.exe")
        if ejecutable:
            return ejecutable

        # 2. Rutas conocidas en Windows (MiKTeX y TeX Live)
        rutas_windows = [
            r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
            r"C:\Program Files (x86)\MiKTeX\miktex\bin\pdflatex.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"),
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"),
        ]
        # Búsqueda comodín en TeX Live Windows (ej. C:\texlive\2024\bin\windows\pdflatex.exe)
        rutas_windows.extend(glob.glob(r"C:\texlive\*\bin\windows\pdflatex.exe"))
        rutas_windows.extend(glob.glob(r"C:\texlive\*\bin\win32\pdflatex.exe"))

        # 3. Rutas conocidas en Linux / Mac
        rutas_unix = [
            "/usr/bin/pdflatex",
            "/usr/local/bin/pdflatex",
            "/Library/TeX/texbin/pdflatex",
            "/usr/texbin/pdflatex"
        ]
        rutas_unix.extend(glob.glob("/usr/local/texlive/*/bin/*/pdflatex"))

        todas_rutas = rutas_windows if os.name == 'nt' else rutas_unix
        for r in todas_rutas:
            if os.path.isfile(r) and os.access(r, os.X_OK):
                return r

        return None

    pdflatex_bin = buscar_ejecutable_pdflatex()

    if not pdflatex_bin:
        return False, (
            "⚠️ No se encontró el ejecutable 'pdflatex' en el sistema.\n\n"
            "El archivo fuente 'Anexo_EACP.tex' fue generado y guardado correctamente.\n\n"
            "¿Por qué ocurre esto?\n"
            "• Si estás en Streamlit Cloud: Asegúrate de tener el archivo 'packages.txt' en la raíz de tu repositorio de GitHub con los paquetes de texlive (texlive-latex-base, texlive-lang-spanish, etc.) y dale 'Reboot App' en el menú de Streamlit.\n"
            "• Si estás en tu computador local: pdflatex no está en el PATH de la terminal o sesión donde abriste Streamlit. Reinicia tu terminal o verifica la instalación de MiKTeX / TeX Live.\n"
            "• Opción Rápida: Puedes descargar el 'Anexo_EACP.tex' generado abajo y compilarlo en segundos en Overleaf."
        )

    try:
        cmd = [pdflatex_bin, "-interaction=nonstopmode", "-halt-on-error", tex_filename]
        # En Windows probar también shell=True si es necesario
        proceso1 = subprocess.run(cmd, capture_output=True, text=True, timeout=50, shell=(os.name == 'nt'))
        if proceso1.returncode != 0:
            log_contenido = ""
            if os.path.exists("Anexo_EACP.log"):
                with open("Anexo_EACP.log", "r", encoding="utf-8", errors="ignore") as log_file:
                    log_contenido = log_file.read()
            todas_lineas = log_contenido.splitlines()
            bloques_error = []
            for idx, line in enumerate(todas_lineas):
                if line.startswith("!"):
                    bloques_error.append("\n".join(todas_lineas[idx:idx + 4]))
            detalle = "\n---\n".join(bloques_error[:3]) if bloques_error else "Error desconocido en LaTeX."
            return False, f"Fallo de compilación de LaTeX:\n{detalle}"

        subprocess.run(cmd, capture_output=True, text=True, timeout=50, shell=(os.name == 'nt'))

        if os.path.exists(pdf_filename):
            return True, pdf_filename
        return False, "No se encontró el PDF resultante tras la compilación."
    except FileNotFoundError:
        return False, (
            "⚠️ Error al invocar 'pdflatex'. No se encuentra el comando ejecutable en las rutas del sistema."
        )
    except subprocess.TimeoutExpired:
        return False, "La compilación tardó demasiado y fue interrumpida (timeout de 50s)."
    except Exception as e:
        return False, f"Error inesperado durante la compilación: {str(e)}"
