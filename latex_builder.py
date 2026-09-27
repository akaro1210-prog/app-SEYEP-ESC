import os
import subprocess
from datetime import datetime
import pandas as pd

def escapar_latex(texto):
    """Función para escapar caracteres especiales de LaTeX en celdas o variables."""
    if texto is None or (isinstance(texto, float) and pd.isna(texto)):
        return ""
    if not isinstance(texto, str):
        texto = str(texto)
    # Evitar doble escape si el usuario ya escribió \_ o \% o \& en el campo
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

def resolver_ruta_imagen(nombre_archivo):
    """
    Busca la imagen en el directorio actual o en modulos_latex/, tolerando diferencias
    de mayúsculas/minúsculas, espacios vs guiones bajos, o extensión (.png, .jpg, .jpeg).
    """
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
                    encontrada = item if carpeta == "." else f"{carpeta}/{item}"
                    return encontrada
        except Exception:
            pass
    return None

def incluir_imagen_segura(nombre_archivo, opciones="width=0.8\\textwidth"):
    """
    Si la imagen existe en disco (exacta o equivalente), inserta \\includegraphics.
    Si aún no se ha cargado, inserta un recuadro de marcador en el PDF para que pdflatex NO falle.
    """
    ruta_resuelta = resolver_ruta_imagen(nombre_archivo)
    if ruta_resuelta:
        return f"\\includegraphics[{opciones}]{{{ruta_resuelta}}}"
    nombre_limpio = escapar_latex(os.path.basename(str(nombre_archivo).strip()))
    return (
        f"\\fbox{{\\parbox{{0.85\\textwidth}}{{\\centering\\vspace{{0.5cm}}"
        f"\\small\\textbf{{[Imagen pendiente por cargar en el directorio:]}}\\\\[0.15cm]"
        f"\\texttt{{{nombre_limpio}}}\\vspace{{0.5cm}}}}}}"
    )

def incluir_csv_seguro(opciones, caption, label, nombre_csv):
    """
    Si el archivo CSV existe en disco, ejecuta la macro \\CSVTablaAuto.
    Si aún no existe, genera una tabla de respaldo con el mismo \\caption y \\label
    para que todas las referencias \\cref{label} compilen sin errores.
    """
    ruta = str(nombre_csv).strip().replace("\\", "/")
    if os.path.exists(ruta):
        return f"\\CSVTablaAuto[{opciones}]\n{{{caption}}}\n{{{label}}}\n{{{ruta}}}"
    nombre_limpio = escapar_latex(os.path.basename(ruta))
    return f"""
\\begin{{table}}[htbp]
\\centering
\\caption{{{caption}}}
\\label{{{label}}}
\\vspace{{0.2cm}}
\\fbox{{\\parbox{{0.85\\textwidth}}{{\\centering\\vspace{{0.35cm}}
\\small\\textbf{{[Archivo CSV pendiente por cargar:]}} \\texttt{{{nombre_limpio}}}
\\vspace{{0.35cm}}}}}}
\\end{{table}}
"""

def generar_tabla_control_cambios(df_cambios):
    """Construye el bloque LaTeX para la tabla de Control de Cambios (Página 2)."""
    filas_latex = []

    if df_cambios is not None:
        if isinstance(df_cambios, pd.DataFrame) and not df_cambios.empty:
            registros = df_cambios.fillna("").to_dict(orient="records")
        elif isinstance(df_cambios, list):
            registros = df_cambios
        else:
            registros = []

        for fila in registros:
            version = escapar_latex(fila.get("VERSIÓN No.", "")).strip()
            descripcion = escapar_latex(fila.get("DESCRIPCIÓN", "")).strip()
            fecha = escapar_latex(fila.get("FECHA", "")).strip()
            observaciones = escapar_latex(fila.get("OBSERVACIONES", "")).strip()

            if not any([version, descripcion, fecha, observaciones]):
                continue

            filas_latex.append(
                f"{version} & {descripcion} & {fecha} & {observaciones} \\\\ \\hline"
            )

    if not filas_latex:
        filas_latex.append("0 & Informe Inicial. & 23/09/2026 & \\\\ \\hline")

    contenido_filas = "\n".join(filas_latex)

    return f"""
% --- CONTROL DE CAMBIOS ---
\\begin{{center}}
\\section*{{CONTROL DE CAMBIOS.}}
\\vspace{{0.3cm}}
\\begingroup
\\renewcommand{{\\arraystretch}}{{1.5}}
\\setlength{{\\tabcolsep}}{{6pt}}
\\begin{{tabularx}}{{\\textwidth}}{{|P{{2.5cm}}|L|P{{3cm}}|L|}}
\\hline
\\rowcolor{{azulSeyep}}
\\textbf{{\\textcolor{{white}}{{VERSIÓN No.}}}} &
\\textbf{{\\textcolor{{white}}{{DESCRIPCIÓN}}}} &
\\textbf{{\\textcolor{{white}}{{FECHA}}}} &
\\textbf{{\\textcolor{{white}}{{OBSERVACIONES}}}} \\\\ \\hline
{contenido_filas}
\\end{{tabularx}}
\\endgroup
\\end{{center}}
"""

def generar_bloque_tabla_supuestos(usar_tabla_upme, df_supuestos_upme, archivo_or_path, titulo_tabla=None):
    """Genera el bloque LaTeX de la tabla de proyección de demanda con \\label{tab:UPME}."""
    if not titulo_tabla or not str(titulo_tabla).strip():
        titulo_tabla = (
            "Proyección de la demanda de energía eléctrica y potencia máxima, tabla de Demanda anual de Energía eléctrica por áreas SIN (GWh-año) para la región Antioquia 2026-2040 Rev 2026."
            if usar_tabla_upme
            else "Proyección de demanda suministrada por el Operador de Red"
        )
    caption_limpio = escapar_latex(str(titulo_tabla).strip())

    if usar_tabla_upme and df_supuestos_upme is not None:
        if isinstance(df_supuestos_upme, pd.DataFrame) and not df_supuestos_upme.empty:
            registros = df_supuestos_upme.fillna("").to_dict(orient="records")
        elif isinstance(df_supuestos_upme, list):
            registros = df_supuestos_upme
        else:
            registros = []

        filas = []
        for fila in registros:
            anio = escapar_latex(fila.get("Año", "")).strip()
            medio = escapar_latex(fila.get("Esc. Medio", "")).strip()
            ic_sup_95 = escapar_latex(fila.get("IC Sup. 95%", "")).strip()
            ic_inf_95 = escapar_latex(fila.get("IC Inf. 95%", "")).strip()
            ic_sup_68 = escapar_latex(fila.get("IC Sup. 68%", "")).strip()
            ic_inf_68 = escapar_latex(fila.get("IC Inf. 68%", "")).strip()
            tasa = escapar_latex(fila.get("Tasa Crec.", "")).strip()

            if not any([anio, medio, ic_sup_95, ic_inf_95, ic_sup_68, ic_inf_68, tasa]):
                continue

            filas.append(
                f"{anio} & {medio} & {ic_sup_95} & {ic_inf_95} & {ic_sup_68} & {ic_inf_68} & {tasa} \\\\ \\hline"
            )

        if not filas:
            return ""

        contenido_filas = "\n".join(filas)
        return f"""
\\vspace{{0.4cm}}
\\begin{{table}}[h!]
\\centering
\\caption{{{caption_limpio}}}
\\label{{tab:UPME}}
\\vspace{{0.2cm}}
\\begingroup
\\renewcommand{{\\arraystretch}}{{1.3}}
\\setlength{{\\tabcolsep}}{{4pt}}
\\begin{{tabularx}}{{\\textwidth}}{{|C|C|C|C|C|C|C|}}
\\hline
\\rowcolor{{azulSeyep}}
\\textbf{{\\textcolor{{white}}{{Año}}}} &
\\textbf{{\\textcolor{{white}}{{Esc. Medio}}}} &
\\textbf{{\\textcolor{{white}}{{IC Sup. 95\\%}}}} &
\\textbf{{\\textcolor{{white}}{{IC Inf. 95\\%}}}} &
\\textbf{{\\textcolor{{white}}{{IC Sup. 68\\%}}}} &
\\textbf{{\\textcolor{{white}}{{IC Inf. 68\\%}}}} &
\\textbf{{\\textcolor{{white}}{{Tasa Crec.}}}} \\\\ \\hline
{contenido_filas}
\\end{{tabularx}}
\\endgroup
\\end{{table}}
"""

    if not usar_tabla_upme and archivo_or_path and os.path.exists(archivo_or_path):
        ext = os.path.splitext(archivo_or_path)[1].lower()
        ruta_latex = archivo_or_path.replace("\\", "/")
        if ext in [".png", ".jpg", ".jpeg"]:
            return f"""
\\vspace{{0.4cm}}
\\begin{{table}}[h!]
\\centering
\\caption{{{caption_limpio}}}
\\label{{tab:UPME}}
\\vspace{{0.2cm}}
\\includegraphics[max width=\\textwidth]{{{ruta_latex}}}
\\end{{table}}
"""
        elif ext in [".xlsx", ".xls"]:
            try:
                df_or = pd.read_excel(archivo_or_path).fillna("")
                if not df_or.empty:
                    cols = list(df_or.columns)
                    col_spec = "|" + "|".join(["C"] * len(cols)) + "|"
                    encabezados = " & ".join(
                        [f"\\textbf{{\\textcolor{{white}}{{{escapar_latex(c)}}}}}" for c in cols]
                    )
                    filas_or = []
                    for _, row in df_or.iterrows():
                        celdas = [escapar_latex(row[c]).strip() for c in cols]
                        if any(celdas):
                            filas_or.append(" & ".join(celdas) + " \\\\ \\hline")
                    contenido_or = "\n".join(filas_or)
                    return f"""
\\vspace{{0.4cm}}
\\begin{{table}}[h!]
\\centering
\\caption{{{caption_limpio}}}
\\label{{tab:UPME}}
\\vspace{{0.2cm}}
\\begingroup
\\renewcommand{{\\arraystretch}}{{1.25}}
\\begin{{tabularx}}{{\\textwidth}}{{{col_spec}}}
\\hline
\\rowcolor{{azulSeyep}}
{encabezados} \\\\ \\hline
{contenido_or}
\\end{{tabularx}}
\\endgroup
\\end{{table}}
"""
            except Exception:
                return ""

    return ""

def generar_preambulo():
    return r"""
\documentclass[12pt,letterpaper,spanish]{article}

% ---------- Idioma y acentos (pdfLaTeX) ----------
\usepackage[spanish]{babel}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{microtype}
\usepackage{tocloft}
\usepackage{makecell}
\renewcommand{\cfttoctitlefont}{\hfill\Large\bfseries}
\renewcommand{\cftaftertoctitle}{\hfill}
\renewcommand{\contentsname}{TABLA DE CONTENIDO}

% ---------- Tipografía ----------
\usepackage{mathpazo}
\RequirePackage{fix-cm}
\usepackage{anyfontsize}
\usepackage{pdflscape}
\usepackage{float}
\usepackage[strict]{changepage}
\setlength{\headheight}{147pt}
\addtolength{\topmargin}{-17pt}
\setlength{\footskip}{119pt}

% ---------- Gráficos y tablas ----------
\usepackage{graphicx}
\usepackage{array}
\usepackage{multirow}
\usepackage[table]{xcolor}
\usepackage{colortbl}
\usepackage{booktabs}       
\usepackage{tabularx}
\usepackage{etoolbox}
\usepackage{amsmath}
\usepackage{pgfplotstable}
\usepackage{adjustbox}      
\usepackage{longtable}

% --- Parche obligatorio completo para errores de expl3, array y colortbl ---
\usepackage{expl3}
\ExplSyntaxOn
\cs_if_exist:NF \tbl_gdecr_row_count: { \cs_set_eq:NN \tbl_gdecr_row_count: \relax }
\cs_if_exist:NF \tag_mc_end: { \cs_set_eq:NN \tag_mc_end: \relax }
\cs_if_exist:NF \tag_mc_begin:n { \cs_set_eq:NN \tag_mc_begin:n \use_none:n }
\cs_if_exist:NF \tag_struct_begin:n { \cs_set_eq:NN \tag_struct_begin:n \use_none:n }
\cs_if_exist:NF \tag_struct_end: { \cs_set_eq:NN \tag_struct_end: \relax }
\ExplSyntaxOff

\makeatletter
\providecommand{\do@row@strut}{}
\@ifundefined{insert@pcolumn}{\let\insert@pcolumn\insert@column}{}
\makeatother

\pgfplotsset{compat=1.18}
\usepackage{caption}
\usepackage{pgfplots}

\DeclareCaptionType{ilustracion}[Ilustración][Índice de ilustraciones]

% ---------- Encabezado, pie y márgenes ----------
\usepackage{fancyhdr}
\usepackage[
  letterpaper,
  top=5cm,
  headheight=110pt,
  bottom=3.5cm,
  left=2.5cm,
  right=2.5cm
]{geometry}

% ---------- Hipervínculos y referencias ----------
\usepackage[hidelinks]{hyperref}   
\usepackage[spanish]{cleveref}

% ---------- Captions ----------
\addto\captionsspanish{\renewcommand{\tablename}{TABLA}}
\addto\captionsspanish{\renewcommand{\figurename}{FIGURA}}
\captionsetup{
  labelfont=bf,
  textfont=bf,
  labelsep=period,
  justification=centering,
  singlelinecheck=false,
  font={stretch=1},
  skip=0pt
}

% ---------- Nombres de referencias ----------
\crefname{table}{TABLA}{TABLAS}
\crefname{figure}{FIGURA}{FIGURAS}
\crefformat{table}{\textbf{TABLA~#2#1#3}}
\crefrangeformat{table}{\textbf{TABLAS~#3#1#4~a~#5#2#6}}
\crefmultiformat{table}{\textbf{TABLAS~#2#1#3}}{ y \textbf{#2#1#3}}{, \textbf{#2#1#3}}{ y \textbf{#2#1#3}}
\crefformat{figure}{\textbf{FIGURA~#2#1#3}}
\crefrangeformat{figure}{\textbf{FIGURAS~#3#1#4~a~#5#2#6}}
\crefmultiformat{figure}{\textbf{FIGURAS~#2#1#3}}{ y \textbf{#2#1#3}}{, \textbf{#2#1#3}}{ y \textbf{#2#1#3}}

% ---------- Encabezado y pie con imágenes ----------
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\fancyhead[C]{%
  \makebox[\textwidth][c]{%
    \includegraphics[width=\paperwidth,height=5cm]{Encabezado.png}%
  }%
}
\fancyfoot[C]{%
  \makebox[\textwidth][c]{%
    \includegraphics[width=\paperwidth]{Piedepagina.png}%
  }%
}

\fancypagestyle{plain}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\footrulewidth}{0pt}%
  \fancyhead[C]{%
    \makebox[\textwidth][c]{%
      \includegraphics[width=\paperwidth,height=5cm]{Encabezado.png}%
    }%
  }%
  \fancyfoot[C]{%
    \makebox[\textwidth][c]{%
      \includegraphics[width=\paperwidth]{Piedepagina.png}%
    }%
  }%
}

% ---------- Columnas personalizadas ----------
\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\newcolumntype{C}{>{\centering\arraybackslash}X}
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}

% ---------- Color corporativo ----------
\definecolor{azulSeyep}{RGB}{0,103,254}

% ----------  \ref en negrita ----------
\let\oldref\ref
\renewcommand{\ref}[1]{\textbf{\oldref{#1}}}

% ---------- Ajustes finos de tablas ----------
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.05}

% ====== MACROS CSV ROBUSTAS (SEYEP) — AJUSTE DINÁMICO UNIVERSAL ======
\makeatletter

\newcount\CSV@cols
\newcount\CSV@rows
\newif\ifCSV@twolevelhead

\newcommand{\CSVTablaAuto}[4][]{%
  \begingroup
    \pgfplotstableread[comment chars={!},#1]{#4}\CSV@table%

    \pgfplotstablegetrowsof{\CSV@table}\let\CSV@tempRows\pgfplotsretval%
    \pgfmathtruncatemacro{\CSV@tmpB}{\CSV@tempRows}\relax%
    \CSV@rows=\CSV@tmpB\relax%
    \pgfplotstablegetcolsof{\CSV@table}\let\CSV@tempCols\pgfplotsretval%
    \pgfmathtruncatemacro{\CSV@tmpA}{\CSV@tempCols}\relax%
    \CSV@cols=\CSV@tmpA\relax%

    \CSV@twolevelheadfalse
    \ifnum\CSV@cols=5\relax
      \CSV@twolevelheadtrue
    \fi

    \ifnum\CSV@cols>5\relax
      \fontsize{8pt}{10pt}\selectfont
      \setlength{\tabcolsep}{1.2pt}%
    \else\ifnum\CSV@cols>7\relax
      \scriptsize
      \setlength{\tabcolsep}{2.5pt}%
    \else
      \footnotesize
      \setlength{\tabcolsep}{4pt}%
    \fi\fi

    \renewcommand{\arraystretch}{1.15}%

    \ifnum\CSV@rows>10
      \begingroup
      \setlength{\LTcapwidth}{\textwidth}%
      \setlength{\LTleft}{\fill}%
      \setlength{\LTright}{\fill}%
      \pgfplotstabletypeset[
        begin table=\begin{longtable},
        end table=\end{longtable},
        string type,
        empty cells with={},
        column type={c|},
        every first column/.style={column type={|c|}},
        assign column name/.style={/pgfplots/table/column name={\textbf{\textcolor{white}{\detokenize{##1}}}}},
        postproc cell content/.append code={%
          \ifx\pgfkeysnovalue##1\relax
            \pgfkeyssetvalue{/pgfplots/table/@cell content}{}%
          \fi
        },
        every head row/.style={
          before row={%
            \caption{#2}\label{#3}\\
            \hline
            \rowcolor{azulSeyep}%
          },
          after row={%
            \hline
            \endfirsthead
            \multicolumn{\the\CSV@cols}{c}{\small\textbf{Continuación de la tabla \ref{#3}}}\\
            \hline
            \rowcolor{azulSeyep}%
            \endhead
            \hline
            \multicolumn{\the\CSV@cols}{r}{\scriptsize\textit{Continúa en la siguiente página\dots}}\\
            \endfoot
            \hline
            \endlastfoot
            \rowcolor{white}%
          }
        },
        every row/.style={after row=\hline},
        every last row/.style={after row=\hline}
      ]{\CSV@table}
      \endgroup
    \else
      \begin{table}[htbp]
        \centering
        \caption{#2}\label{#3}
        \begin{adjustbox}{max width=\textwidth,center}
          \pgfplotstabletypeset[
            string type,
            empty cells with={},
            assign column name/.style={/pgfplots/table/column name={\textbf{\textcolor{white}{\detokenize{##1}}}}},
            column type={c|},
            every first column/.style={column type={|c|}},
            postproc cell content/.append code={%
              \ifx\pgfkeysnovalue##1\relax
                \pgfkeyssetvalue{/pgfplots/table/@cell content}{}%
              \fi
            },
            every head row/.style={before row={\hline\rowcolor{azulSeyep}}, after row={\hline}},
            every row/.style={after row=\hline},
            every last row/.style={after row=\hline}
          ]{\CSV@table}
        \end{adjustbox}
      \end{table}
    \fi
  \endgroup
}
\makeatother
% ====== FIN MACROS ======
"""

def normalizar_clave(k):
    """Normaliza el nombre de una llave quitando barras, guiones, espacios y pasando a minúsculas."""
    return str(k).strip().lstrip("\\").lower().replace("_", "").replace("-", "").replace(" ", "")

def es_escalar_no_vacio(v):
    """Verifica de forma segura si un valor es texto o número no vacío (ignorando DataFrames/listas)."""
    return isinstance(v, (str, int, float)) and not isinstance(v, bool) and str(v).strip() != ""

def buscar_param(params, candidatos, default=""):
    """
    Busca una variable escalar en params (y en st.session_state) comparando tanto el nombre exacto
    como su versión normalizada (sin guiones bajos, espacios ni mayúsculas).
    """
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

def compilar_estudio_latex(params):
    if params is None:
        params = {}

    # Recuperar también diccionarios desde st.session_state como respaldo
    try:
        import streamlit as st
        for k_sess in ["datos_sec_2_3", "datos_sec_4_5_6", "datos_sec_7", "datos_sec_8", "datos_sec_9_10"]:
            if k_sess in st.session_state and isinstance(st.session_state[k_sess], dict):
                for sub_k, sub_v in st.session_state[k_sess].items():
                    if sub_k not in params:
                        params[sub_k] = sub_v
    except Exception:
        pass

    # 1. Variables principales del proyecto (con búsqueda flexible de llaves de tab_variables.py)
    nombre_proyecto = escapar_latex(buscar_param(params, ["nombreProyecto", "nombre_proyecto", "proyecto"], "Arboreo"))
    capacidad_mw = escapar_latex(buscar_param(params, ["capacidadMW", "capacidad_mw", "capacidad", "potencia"], "900kW"))
    operador_red = escapar_latex(buscar_param(params, ["OR", "operadorRed", "operador_red"], "EPM"))
    fecha_entrada = escapar_latex(buscar_param(params, ["FechaEntrada", "fecha_entrada", "fpo"], "marzo del 2027"))

    # Búsqueda exhaustiva para el mes y año de entrega del informe (Portada)
    mes_entrega_raw = buscar_param(
        params,
        [
            "mesentregainformemasyear",
            "mes_entrega_informe_mas_year",
            "mesentregainforme",
            "mes_entrega_informe",
            "mes_entrega",
            "mesEntrega",
            "fecha_entrega",
            "fechaEntrega",
            "fecha_entrega_informe",
            "mes_informe",
            "fecha_informe",
            "mes_anio_entrega",
            "mes_anio",
            "mes_year",
            "fecha_portada",
            "mes_portada"
        ],
        ""
    )
    if not mes_entrega_raw:
        # Si en tab_variables tiene otro nombre que contenga 'entrega' (distinto de FechaEntrada) o 'informe'
        for k, v in params.items():
            nk = normalizar_clave(k)
            if isinstance(v, (str, int, float)) and str(v).strip():
                if ("entrega" in nk and nk != "fechaentrada") or ("mes" in nk and "year" in nk) or ("mes" in nk and "anio" in nk):
                    mes_entrega_raw = v
                    break
    mes_entrega = escapar_latex(mes_entrega_raw if mes_entrega_raw else "Septiembre, 2026")

    latitud = escapar_latex(buscar_param(params, ["Latitud", "latitud"], '5°53\'49.8"N'))
    longitud = escapar_latex(buscar_param(params, ["Longitud", "longitud"], '74°45\'12.9"W'))
    year_inicial = escapar_latex(buscar_param(params, ["YearInicial", "year_inicial", "anio_inicial"], "2027"))
    year_final = escapar_latex(buscar_param(params, ["YearFinal", "year_final", "anio_final"], "2032"))
    cto = escapar_latex(buscar_param(params, ["CTO", "cto", "circuito"], "211-11"))
    ssee = escapar_latex(buscar_param(params, ["SSEE", "ssee", "subestacion"], "Doradal_13.2"))
    nt = escapar_latex(buscar_param(params, ["NT", "nt", "nivel_tension", "nivelTension"], "13.2kV"))
    nodo = escapar_latex(buscar_param(params, ["nodo", "nodo_conexion", "nodoConexion"], "906750"))
    elemento_proteccion = escapar_latex(buscar_param(params, ["elementoProteccion", "elemento_proteccion"], "211-11"))
    referencia_panel = escapar_latex(buscar_param(params, ["referenciaPanel", "referencia_panel"], "JAM66D45 625 LB"))
    potencia_panel = escapar_latex(buscar_param(params, ["potenciaPanel", "potencia_panel"], "625 Wp"))
    cantidad_panel = escapar_latex(buscar_param(params, ["cantidadPanel", "cantidad_panel"], "1760"))
    ubicacion = escapar_latex(buscar_param(params, ["ubicacion", "Ubicacion"], "En predio del hotel Arboreo, Doradal, Antioquia"))
    cp_hora = escapar_latex(buscar_param(params, ["CP", "cp", "hora_cp"], "------"))
    dmi_hora = escapar_latex(buscar_param(params, ["Dmi", "dmi", "hora_dmi"], "------"))
    dmx_hora = escapar_latex(buscar_param(params, ["DMx", "dmx", "hora_dmx"], "------"))
    escenario_max_perd = escapar_latex(buscar_param(params, ["escenariomaxPerdidas", "escenario_max_perdidas"], "----"))
    perdidas_maximas = escapar_latex(buscar_param(params, ["perdidasmaximas", "perdidas_maximas"], "----- kW"))
    generacion_aprobada = escapar_latex(buscar_param(params, ["generacionaprobada", "generacion_aprobada"], "900kW"))
    potencia_minima = escapar_latex(buscar_param(params, ["potenciaminima", "potencia_minima"], "90 kW"))
    reco_cto = escapar_latex(buscar_param(params, ["recoCTO", "reco_cto"], "211-11"))
    tipo_proteccion = escapar_latex(buscar_param(params, ["tipoproteccion", "tipo_proteccion"], "Reconectador"))
    reco_cabecera = escapar_latex(buscar_param(params, ["recocabecera", "reco_cabecera"], " "))

    # Inversores configurados en Sección 2-3
    inv_items = params.get("inv_items", [
        {"ref": params.get("refInversoruno", "Inversor 150 kW On-Grid."),
         "modelo": params.get("Inversoruno", "Growat MAX 150KTL3-X2MV"),
         "cantidad": params.get("cantidadInversoruno", "6 Und.")}
    ])
    if not inv_items:
        inv_items = [{"ref": "Inversor 150 kW On-Grid.", "modelo": "Growat MAX 150KTL3-X2MV", "cantidad": "6 Und."}]

    ref_inv_1 = escapar_latex(inv_items[0].get("ref", "Inversor 150 kW On-Grid."))
    mod_inv_1 = escapar_latex(inv_items[0].get("modelo", "Growat MAX 150KTL3-X2MV"))
    cant_inv_1 = escapar_latex(inv_items[0].get("cantidad", "6 Und."))

    items_ref_inv = "\n".join([f"\\item {escapar_latex(x.get('ref', ''))}" for x in inv_items])
    items_mod_inv = "\n".join([f"\\item {escapar_latex(x.get('modelo', ''))}" for x in inv_items])
    items_cant_inv = "\n".join([f"\\item {escapar_latex(x.get('cantidad', ''))}" for x in inv_items])

    etiquetas_fig_inv = ["fig:fichainversoruno", "fig:fichainversordos", "fig:fichainversortres"]
    bloques_fig_inv = []
    for idx, inv in enumerate(inv_items[:3]):
        modelo_raw = str(inv.get("modelo", "")).strip()
        modelo_esc = escapar_latex(modelo_raw)
        lbl = etiquetas_fig_inv[idx]
        img_cmd = incluir_imagen_segura(f"Ficha {modelo_raw}.png", "height=0.85\\textheight, keepaspectratio")
        bloques_fig_inv.append(f"""
\\begin{{figure}}[htbp]
    \\centering
    {img_cmd}
    \\caption{{Hoja técnica {modelo_esc}}}
    \\label{{{lbl}}}
\\end{{figure}}
""")
    codigo_fig_inversores = "\n".join(bloques_fig_inv)

    # 2. Textos de Resumen Ejecutivo (Sección 1.2 y 1.3)
    resumen_intro = params.get(
        "resumen_intro",
        "Para el presente documento se han realizado los siguientes estudios técnicos con el propósito de evaluar la viabilidad del proyecto:"
    )
    resumen_flujo = params.get("resumen_flujo", "")
    resumen_cortocircuito = params.get("resumen_cortocircuito", "")
    resumen_protecciones = params.get("resumen_protecciones", "")
    resumen_cierre = params.get(
        "resumen_cierre",
        "Finalmente, estos estudios proporcionan una sólida base técnica para afirmar la viabilidad del proyecto, asegurando su integración segura y eficiente en la red eléctrica existente."
    )

    texto_supuesto_activo = params.get("texto_supuesto_activo", "")
    usar_tabla_upme = params.get("usar_tabla_upme", True)
    df_supuestos_upme = params.get("df_supuestos_upme", None)
    archivo_or_path = params.get("archivo_or_path", None)
    titulo_tabla_supuestos = params.get("titulo_tabla_supuestos", None)
    if not titulo_tabla_supuestos:
        try:
            import streamlit as st
            titulo_tabla_supuestos = st.session_state.get("titulo_tabla_supuestos", None)
        except Exception:
            titulo_tabla_supuestos = None

    bloque_tabla_supuestos = generar_bloque_tabla_supuestos(
        usar_tabla_upme=usar_tabla_upme,
        df_supuestos_upme=df_supuestos_upme,
        archivo_or_path=archivo_or_path,
        titulo_tabla=titulo_tabla_supuestos
    )

    df_control_cambios = params.get("df_control_cambios", None)
    bloque_tabla_cambios = generar_tabla_control_cambios(df_control_cambios)

    # 3. Logotipo Portada
    logo_path = params.get("logo_cliente", params.get("logoCliente", "Logo_Cliente.png"))
    if not logo_path or not os.path.exists(logo_path):
        logo_path = "Logo_Cliente.png"

    bloque_logo = ""
    if os.path.exists(logo_path):
        try:
            from PIL import Image
            img = Image.open(logo_path)
            img.verify()
            img = Image.open(logo_path)
            img = img.convert("RGBA") if img.mode in ("RGBA", "P") else img.convert("RGB")
            clean_logo_name = "Logo_Cliente_clean.png"
            img.save(clean_logo_name, "PNG")
            bloque_logo = f"\\includegraphics[width=0.3\\textwidth]{{{clean_logo_name}}} \\\\[2cm]"
        except Exception:
            bloque_logo = ""

    # 4. Datos Secciones 2 y 3
    sec2_intro = params.get(
        "sec2_intro",
        r"El proyecto \nombreProyecto\ de GD \capacidadMW, se conectará al SIN a través del circuito \CTO\ de la S/E \SSEE\ al nivel de tensión \NT, propiedad del operador de red \OR, La ubicación del proyecto es \ubicacion. En la \cref{tab:coordenadas} se detallan las coordenadas geográficas para la ubicación del proyecto GD \nombreProyecto. El proyecto cuenta con una fecha en puesta de operación (en adelante FPO) para \FechaEntrada. En la \cref{tab:descripcion_proyecto} se resumen las especificaciones técnicas de los equipos que conforman el proyecto."
    )
    vida_util = escapar_latex(params.get("vida_util", "30 años."))
    tipo_fuente = escapar_latex(params.get("tipo_fuente", "Energía Solar"))
    tipo_panel_etiqueta = escapar_latex(params.get("tipo_panel_etiqueta", "Panel Solar Bifacial"))
    prot_item = escapar_latex(params.get("prot_item", "Protección – Interruptor"))
    prot_desc = escapar_latex(params.get("prot_desc", "Interruptor LSI 3 x 1360A"))
    prot_cant = escapar_latex(params.get("prot_cant", "1 Und."))
    sec2_cierre = params.get(
        "sec2_cierre",
        r"Finalmente, para la contextualización general del proyecto se presenta la \cref{fig:ubicacion}, donde se resalta la ubicación de este."
    )
    incluir_geoespacial = params.get("incluir_geoespacial", False)
    bloque_geoespacial = ""
    if incluir_geoespacial:
        img_geo = incluir_imagen_segura("Diagrama Geoespacial.png", "width=10cm")
        bloque_geoespacial = f"""
En la \\cref{{fig:georeferencia}}, se presenta el diagrama eléctrico geoespacial del circuito \\CTO\\ en el cual se conecta el proyecto.\\\\
\\begin{{figure}}[htbp]
    \\centering
    {img_geo}
    \\caption{{Diagrama eléctrico geoespacial CTO \\CTO}}
    \\label{{fig:georeferencia}}
\\end{{figure}}
"""
    img_ubicacion = incluir_imagen_segura("Ubicacion Geográfica.png", "width=15cm")

    sec3_intro = params.get(
        "sec3_intro",
        r"En la \cref{fig:fichapanel}, se puede apreciar las características técnicas de los paneles fotovoltaicos seleccionados para el proyecto."
    )
    texto_equipos = params.get(
        "texto_equipos",
        r"Sumado a \cantidadInversoruno\ inversores de 150 kW, 4 de ellos con 300 paneles cada uno y los otros dos con 280 cada uno, su tensión de salida es de 800 V – 60 Hz respectivamente. En la \cref{fig:fichainversoruno}, se aprecia las características operativas de los inversores instalados en el sistema de generación."
    )
    img_ficha_panel = incluir_imagen_segura("Ficha panel.png", "width=17cm")
    sec3_or_texto = params.get(
        "sec3_or_texto",
        r"El proyecto GD \nombreProyecto\ se conectará al circuito \CTO\, por tanto, el OR suministro a través de los insumos datos de red de todo el circuito y ajuste de coordinación de protecciones."
    )
    usar_equivalente_png = params.get("usar_equivalente_png", True)
    if usar_equivalente_png:
        img_eq_red = incluir_imagen_segura("equivalentered.png", "height=0.23\\textheight, keepaspectratio")
        bloque_eq_red = f"""
\\begin{{table}}[htbp]
    \\centering
    \\caption{{Parámetros Equivalente de RED}}
    \\label{{tab:equivalentered}}
    {img_eq_red}
\\end{{table}}
"""
    else:
        bloque_eq_red = incluir_csv_seguro(
            "col sep=semicolon, skip rows between index={500}{5000}",
            "Parámetros Equivalente de RED",
            "tab:equivalentered",
            "equivalentered.csv"
        )

    csv_cargas_ini = incluir_csv_seguro(
        "col sep=semicolon, skip rows between index={500}{5000}",
        f"Demandas consideradas en el circuito {year_inicial} - Calculada con la información entregada por el OR y la proyección de la UPME en la \\cref{{tab:UPME}}",
        f"tab:cargascto{year_inicial}",
        f"cargascto{year_inicial}.csv"
    )
    csv_cargas_fin = incluir_csv_seguro(
        "col sep=semicolon, skip rows between index={500}{5000}",
        f"Demandas consideradas en el circuito {year_final} - Calculada con la información entregada por el OR y la proyección de la UPME en la \\cref{{tab:UPME}}",
        f"tab:cargascto{year_final}",
        f"cargascto{year_final}.csv"
    )

    bloque_informacion_or = f"""\\cref{{tab:equivalentered,tab:cargascto{year_inicial},tab:cargascto{year_final}}}
{bloque_eq_red}
{csv_cargas_ini}
{csv_cargas_fin}
"""

    # 5. Datos Secciones 4, 5 y 6
    sec4_1_texto = params.get("sec4_1_texto", r"En la \cref{fig:Unifilar} se presenta el diagrama unifilar del circuito \CTO\ suministrado por el OR.")
    img_unifilar = incluir_imagen_segura("UnifilarCTO.png", "width=15cm")
    sec4_2_texto = params.get(
        "sec4_2_texto",
        r"En el numeral 7.1 de la circular CREG 021 de 2022, se establece el horizonte de análisis, en la \cref{tab:horizonte} se presentan los años a analizar según la información suministrada."
    )
    sec4_3_texto = params.get(
        "sec4_3_texto",
        r"La energía demandada por el circuito fue suministrada por el OR en la \cref{tab:demandaenergia}, en la cual se especifica la demanda del circuito por hora."
    )
    csv_demanda_energia = incluir_csv_seguro(
        "col sep=semicolon, skip rows between index={500}{5000}",
        "Demanda de energía suministrada por el OR.",
        "tab:demandaenergia",
        "DemandaEnergia.csv"
    )
    sec4_4_intro = params.get(
        "sec4_4_intro",
        r"Para el consumo y la generación promedio por hora, se toman los datos que se muestran en la \cref{tab:consumoVSgeneracion}."
    )
    csv_consumo_vs_gen = incluir_csv_seguro(
        "col sep=semicolon, skip rows between index={500}{5000}",
        "Consumo de energía en el punto de instalación del GD y generación de energía proyectada.",
        "tab:consumoVSgeneracion",
        "consumoVSgeneracion.csv"
    )
    sec4_4_curva = params.get(
        "sec4_4_curva",
        r"Por parte de EPM se suminstró el perfil de demanda del circuito 211-11 de la subestación Doradal 13.2kV, segun la \cref{fig:curvadecarga211}, es importante destacar que de esta curva que correcponde a un día típioco mínimo se estrajeron las horas de 9:00 am, 12:00 pm y 3:00 pm ya que son los horarios de generación máxima y donde el proyecto fotovoltaico va a presnetar un mayor impacto."
    )
    caption_curva_cto = escapar_latex(params.get("caption_curva_cto", "Demanda de circuito 211-11 suministrado por el operador de red"))
    img_curva_cto = incluir_imagen_segura("curva de carga cto211.png", "width=17cm")
    sec4_4_comp = params.get("sec4_4_comp", r"En la \cref{fig:consumoygeneracion}, se compara el consumo y la genreación por hora del circuito 211-11.")
    img_consumo_gen = incluir_imagen_segura("consumoygeneracion.png", "width=17cm")

    sec5_intro = params.get(
        "sec5_intro",
        r"Para el desarrollo del presente informe se emplea la información suministrada por \OR, esta base de datos contiene el sistema de distribución local desde el nodo de conexión de la S/E \SSEE, en un circuito radial de \NT. Los análisis se realizan para el circuito \CTO."
    )
    sec6_despacho = params.get(
        "sec6_despacho",
        r"Para la demanda se consideró la información suminstrada por EPM y de acuerdo con el OR y el Consejo Nacional de Operación (CNO) con los lineamientos para estudios de conexión simplificado en el marco de la resolución CREG 174 de 2021, el estudio se realizó bajo los siguientes escenarios:"
    )
    sec6_gen_max = params.get(
        "sec6_gen_max",
        r"Para proyectos de generación fotovoltaico se presenta la generación máxima del proyecto a las 9:00 am, 12:00 pm y 3:00 pm, ya que la generación no es controlable y el único cambio presentado es la demanda, adicionalmente se considera el caso de demanda mínima (suministrada por el operador de red) para considerar las peores condiciones posibles donde la energía demandada por el circuito es la menor por lo que la disponibilidad de capacidad de transmisión es menor."
    )

    # 6. Datos Sección 7 (Resultados Eléctricos)
    img_conv_flujos = incluir_imagen_segura("convencionesflujos.png", "width=0.5\\linewidth")
    img_cod_colores = incluir_imagen_segura("codigocoloresflujo.png", "width=3cm")
    img_cargabilidad = incluir_imagen_segura("Cargabilidad.png", "height=0.45\\textheight, keepaspectratio")
    img_tensiones_pu = incluir_imagen_segura("TensionesPU.png", "height=0.38\\textheight, keepaspectratio")
    img_perfil_cto = incluir_imagen_segura("perfiltensionCTO.png", "width=15cm")

    sec7_cargabilidad_txt = params.get(
        "sec7_cargabilidad_txt",
        r"Como se puede apreciar en la \cref{tab:Cargabilidad} la cargabilidad en la zona de influencia se encuentra acorde lo requerido en la normativa CREG 025 de 1995 con valores aceptable menores del 100\%."
    )
    conclusion_perfiles_carga = params.get(
        "conclusion_perfiles_carga",
        r"Al presentar los casos de estudio bajo el area de influencia del proyecto asociado a la simulación presentado por el OR en la \cref{fig:Unifilar} se analiza que los perfiles de tensión se mantienen dentro de los límites establecidos por la resolución CREG 024 del 2005 aplicables en los servicios de distribución de energía eléctrica."
    )

    incluir_contingencia = params.get("incluir_contingencia", True)
    contingencia_p1 = params.get(
        "contingencia_p1",
        r"El análisis de contingencias N-1 demuestra que la integración del proyecto \nombreProyecto\ no compromete la seguridad ni la confiabilidad del sistema regional. Ante eventos simples en la red adyacente, los perfiles de tensión se mantienen en el rango normativo con un valor máximo de 1,01 p.u., mientras que los tramos de línea operan holgadamente con cargabilidades inferiores al 28,7\%. Adicionalmente, la Subestación Doradal absorbe las contingencias de forma estable."
    )
    contingencia_p2 = params.get(
        "contingencia_p2",
        r"Como se evidencia en la \cref{fig:cargabilidadConti} el sistema incrementa su capacidad para soportar contingencias sin superar los límites operativos establecidos, mejorando las condiciones de confiabilidad y flexibilidad operativa del circuito."
    )
    img_cont_cargmax = incluir_imagen_segura("Cont_Cargmax.png", "width=0.6\\linewidth")
    img_pumax = incluir_imagen_segura("pumax.png", "width=0.6\\linewidth")
    img_diag_cont = incluir_imagen_segura("Diagrama_Contingencia.png", "width=15cm")

    if incluir_contingencia:
        bloque_contingencia = f"""
\\subsection{{\\textit{{Análisis de contingencia}}}}
{contingencia_p1}\\\\
\\leavevmode\\\\
En la \\cref{{tab:cargabilidadMax,tab:PUMax_conting}} se presenta los valores maximos alcanzados en el analisis de cargabilidad y perfiles de tensión.

\\begin{{table}}[h!]
    \\centering
    \\caption{{Cargabilidad Maxima En Contingencia \\YearInicial\\ para el \\CTO}}
    \\label{{tab:cargabilidadMax}}
    {img_cont_cargmax}
\\end{{table}}

\\begin{{table}}[h!]
    \\centering
    \\caption{{Perfil De Tension Maxima En Contingencia \\YearInicial\\ para el \\CTO}}
    \\label{{tab:PUMax_conting}}
    {img_pumax}
\\end{{table}}

\\newpage
{contingencia_p2}

\\begin{{figure}}[h]
    \\centering
    {img_diag_cont}
    \\caption{{Diagrama Contingencia \\YearInicial}}
    \\label{{fig:cargabilidadConti}}
\\end{{figure}}
"""
    else:
        bloque_contingencia = ""

    img_perdidas = incluir_imagen_segura("perdidas.png", "height=0.25\\textheight, keepaspectratio")
    sec7_perdidas_texto = params.get(
        "sec7_perdidas_texto",
        r"El análisis técnico de los escenarios proyectados para \YearInicial\ y \YearFinal\, se evidencia que el incremento más significativo se presenta en el escenario de Hora 12, alcanzando deltas de 25,97 kW (\YearInicial) y 25,90 kW (\YearFinal); este comportamiento responde a la condición técnica donde los Generadores Distribuidos (GD) inyectan su máxima capacidad de energía mientras la demanda del circuito es mínima, lo que ocasiona flujos inversos de potencia a través de la red de distribución. Por el contrario, en los escenarios con coincidencia entre la generación y la carga, las pérdidas se mantienen en niveles bajos e impactan de manera marginal al sistema destacando variaciones de apenas approx 11 kW en el escenario de Hora 9, lo que demuestra que la absorción local de la energía producida evita el transporte prolongado de corriente y confirma que la integración de los proyectos no genera un impacto negativo ni degradante sobre la operación habitual del SDL."
    )
    img_leyendas_cortos = incluir_imagen_segura("Leyendascortos.png", "width=1.0\\linewidth")
    img_cortos = incluir_imagen_segura("cortos.png", "width=1.075\\linewidth")
    sec7_isla_conclusion = params.get(
        "sec7_isla_conclusion",
        r"La Ecuación \eqref{eq:balance_potencia} arroja un resultado donde la potencia instalada acumulada más la capacidad del proyecto supera la demanda mínima del circuito, confirmando la existencia de riesgo de funcionamiento en isla no intencional ante contingencias o aperturas del elemento de maniobra del Operador de Red. Para mitigar este riesgo y garantizar la seguridad de la red y del personal, la planta implementará un esquema de protección anti-isla activo y coordinado conforme a las disposiciones normativas del Acuerdo CNO 2233 de 2026; los detalles de la filosofía de operación, la parametrización de las funciones intrínsecas del inversor, las funciones de respaldo y la coordinación de tiempos de despeje para evitar la operación en isla se presentan de manera detallada en el Estudio de Ajuste de Protecciones (EACP) entregado adjunto al presente estudio de conexión."
    )

    # 7. Datos Sección 8 (Protecciones)
    ac_fases = params.get("ac_fases", r"$3~\phi$")
    ac_tension_kv = escapar_latex(params.get("ac_tension_kv", "0,48"))
    ac_corriente_max = escapar_latex(params.get("ac_corriente_max", "1081"))
    ac_factor_carga = escapar_latex(params.get("ac_factor_carga", "1,25"))
    ac_proteccion_tablero = escapar_latex(params.get("ac_proteccion_tablero", "1353*"))
    ac_nota_pie = escapar_latex(params.get("ac_nota_pie", "*Nota: Valor de protección ajustado a 1360 A."))

    gd_protege = escapar_latex(params.get("gd_protege", "Transformador 1.25MVA"))
    gd_tipo = escapar_latex(params.get("gd_tipo", "Reconectador"))
    gd_ref = escapar_latex(params.get("gd_ref", "ENTEC EPR-1 ETR300-R-600"))
    gd_tctp = escapar_latex(params.get("gd_tctp", "Sensores elecrónicos"))

    inv_protege = escapar_latex(params.get("inv_protege", "TSF - Inversores"))
    inv_tipo = escapar_latex(params.get("inv_tipo", "Interruptor"))
    inv_ajuste = escapar_latex(params.get("inv_ajuste", "3 X 1360"))

    or_protege = escapar_latex(params.get("or_protege", "Circuito completo"))
    or_tipo_desc = escapar_latex(params.get("or_tipo_desc", "Se supondrá que es un reconectador"))

    df_ajustes_reco = params.get("df_ajustes_reco_proy", None)
    filas_reco = []
    if isinstance(df_ajustes_reco, pd.DataFrame) and not df_ajustes_reco.empty:
        for _, r in df_ajustes_reco.fillna("").iterrows():
            p_nom = escapar_latex(r.get("Parámetro", "")).strip()
            p_pk = escapar_latex(r.get("Pick Up [Aprim]", "")).strip()
            p_dl = escapar_latex(r.get("DIAL [s]", "")).strip()
            p_cv = escapar_latex(r.get("Curva", "")).strip()
            if any([p_nom, p_pk, p_dl, p_cv]):
                filas_reco.append(f"{p_nom} & {p_pk} & {p_dl} & {p_cv} \\\\ \\hline")
    if not filas_reco:
        filas_reco = [
            "ANSI 51 & 44 & 0,05 & IEC - EI \\\\ \\hline",
            "ANSI 50 & 200 & 0,0 & DT \\\\ \\hline",
            "ANSI 51N & 16 & 0,05 & IEC - EI \\\\ \\hline",
            "ANSI 50N & 1100 & 0,00 & DT \\\\ \\hline"
        ]
    contenido_filas_reco = "\n".join(filas_reco)

    df_sist = params.get("df_ajustes_sistematicos", None)
    filas_sist = []
    if isinstance(df_sist, pd.DataFrame) and not df_sist.empty:
        for _, r in df_sist.fillna("").iterrows():
            f_nom = escapar_latex(r.get("Función", "")).strip()
            f_aj = escapar_latex(r.get("Ajustes", "")).strip()
            f_tm = escapar_latex(r.get("Temporización", "")).strip()
            if any([f_nom, f_aj, f_tm]):
                filas_sist.append(f"{f_nom} & {f_aj} & {f_tm} \\\\ \\hline")
    if not filas_sist:
        filas_sist = [
            "Etapa 1: Baja tensión (ANSI 27) & 0.6 p.u & 2 s \\\\ \\hline",
            "Etapa 2: Baja tensión (ANSI 27) & 0.4 p.u & 1.5 s \\\\ \\hline",
            "Etapa 1: Sobretensión (ANSI 59) & 1.22 p.u & 2.5 s \\\\ \\hline",
            "Etapa 2: Sobretensión (ANSI 59) & 1.25 p.u & 0.5 s \\\\ \\hline",
            "Sobretensión de neutro (ANSI 59N) & 0.3 p.u & 2 s \\\\ \\hline",
            "Bajafrecuencia (ANSI 81U) & 57 Hz & 0.2 s \\\\ \\hline",
            "Sobrefrecuencia (ANSI 81O) & 63 Hz & 0.2 s \\\\ \\hline",
            "Anti-Isla & Lógica combinada de ausencia de tensión y frecuencia & 500 ms \\\\ \\hline",
            "Verificación de sincronismo (ANSI 25) & Barra viva OR - Línea Muerta PV a 0.8 p.u de tensión & NA \\\\ \\hline"
        ]
    contenido_filas_sist = "\n".join(filas_sist)

    # 8. Datos Secciones 9 y 10 (Conclusiones y Anexos)
    df_conc = params.get("df_conclusiones", None)
    items_conclusiones = []
    if isinstance(df_conc, pd.DataFrame) and not df_conc.empty:
        for _, r in df_conc.fillna("").iterrows():
            txt_c = str(r.get("Conclusión", "")).strip()
            if txt_c:
                items_conclusiones.append(f"\\item {{{txt_c}}}")
    if not items_conclusiones:
        items_conclusiones = [
            r"\item {Los equipos empleados en el proyecto (Paneles Solares, Protecciones) cumplen con la certificación de conformidad RETIE.}",
            r"\item {Las simulaciones de flujo en estado estable con GD se evidencian tensiones que se mantienen en los valores establecidos.}",
            r"\item {Los niveles de perdidasse mantienen con la introducción del proyecto.}",
            r"\item {Las simulaciones de cortocircuito no presentan cambios mayores al 10\% con la entrada en operación del GD en ningún punto del circuito}",
            r"\item {Los ajustes propuestos para el proyecto coordinan correctamente con las protecciones existentes, por lo tanto no se requiere cambios de ajustes en los elementos existentes.}",
            r"\item {Los inversores cumplen con las normas de equivalencia internacionales como lo son la IEEE1547 y la UL 1741 para la integración a la red. Su nivel de distorsión armónica de corriente según ficha técnica es <3\%.}",
            r"\item {El Sistema propuesto de 900 kWac no afecta de manera significativa la red de distribución y la potencia inyectada de los excedentes será consumida por la red.}"
        ]
    bloque_items_conclusiones = "\n".join(items_conclusiones)

    incluir_anexos = params.get("incluir_anexos", True)
    omitir_no_cargados = params.get("omitir_no_cargados", False)
    modo_anexos = params.get("modo_anexos", "H9_H12_H15")
    archivos_libres_anexos = params.get("archivos_libres_anexos", [])

    # Autodetección inteligente: si la plantilla elegida no tiene imágenes en carpeta pero la otra sí, usar la que tenga imágenes
    if modo_anexos == "CP_DMI_DMX" and not resolver_ruta_imagen(f"Flujo CP_{year_inicial}.png"):
        if resolver_ruta_imagen(f"H9_SP_{year_inicial}.png"):
            modo_anexos = "H9_H12_H15"
    elif modo_anexos == "H9_H12_H15" and not resolver_ruta_imagen(f"H9_SP_{year_inicial}.png"):
        if resolver_ruta_imagen(f"Flujo CP_{year_inicial}.png"):
            modo_anexos = "CP_DMI_DMX"

    bloques_anexos = []
    if incluir_anexos:
        if modo_anexos == "LIBRE" and archivos_libres_anexos:
            bloques_anexos.append(f"""
\\newpage
\\begin{{center}}
    \\vspace*{{\\fill}}
    \\Huge \\textbf{{ANEXOS DE FLUJO DE CARGA}}
    \\vspace*{{\\fill}}
\\end{{center}}
""")
            for idx, item_anexo in enumerate(archivos_libres_anexos):
                arch_img = item_anexo.get("archivo", f"Anexo_Flujo_{idx+1}.png")
                if omitir_no_cargados and not resolver_ruta_imagen(arch_img):
                    continue
                cap_ilus = escapar_latex(item_anexo.get("caption", f"Diagrama unifilar de flujo de carga {idx+1}."))
                lbl_ilus = f"ilus:anexoLibre{idx+1}"
                cmd_ilus = incluir_imagen_segura(arch_img, "width=0.95\\textwidth")
                bloques_anexos.append(f"""
\\newpage
\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionsetup{{hypcap=false}}
        {cmd_ilus}
        \\vspace{{0.2cm}}
        \\captionof{{ilustracion}}{{{cap_ilus}}}
        \\label{{{lbl_ilus}}}
    \\end{{minipage}}
\\end{{center}}
""")
        else:
            for anio_actual in [year_inicial, year_final]:
                if modo_anexos == "H9_H12_H15":
                    casos_h = [
                        (f"H9_SP_{anio_actual}.png", "Diagrama unifilar equivalente de red sin generación H9.", f"ilus:flujoH9SP{anio_actual}"),
                        (f"H9_CP_{anio_actual}.png", "Diagrama unifilar equivalente de red con generación H9.", f"ilus:flujoH9CP{anio_actual}"),
                        (f"H12_SP_{anio_actual}.png", "Diagrama unifilar equivalente de red sin generación H12.", f"ilus:flujoH12SP{anio_actual}"),
                        (f"H12_CP_{anio_actual}.png", "Diagrama unifilar equivalente de red con generación H12.", f"ilus:flujoH12CP{anio_actual}"),
                        (f"H15_SP_{anio_actual}.png", "Diagrama unifilar equivalente de red sin generación H15.", f"ilus:flujoH15SP{anio_actual}"),
                        (f"H15_CP_{anio_actual}.png", "Diagrama unifilar equivalente de red con generación H15.", f"ilus:flujoH15CP{anio_actual}")
                    ]
                else:
                    casos_h = [
                        (f"Flujo CP_{anio_actual}.png", "Diagrama unifilar equivalente de red con carga pura hora \\CP.", f"ilus:flujoCP{anio_actual}"),
                        (f"Flujo DMI GCP_{anio_actual}.png", "Diagrama unifilar equivalente de red con demanda mínima hora \\Dmi\\ con proyecto.", f"ilus:flujoDmigcp{anio_actual}"),
                        (f"Flujo DMI GSP_{anio_actual}.png", "Diagrama unifilar equivalente de red con demanda mínima hora \\Dmi\\ sin proyecto.", f"ilus:flujoDmigsp{anio_actual}"),
                        (f"Flujo DMX GCP_{anio_actual}.png", "Diagrama unifilar equivalente de red con demanda máxima hora \\DMx\\ con proyecto.", f"ilus:flujoDmxgcp{anio_actual}"),
                        (f"Flujo DMX GSP_{anio_actual}.png", "Diagrama unifilar equivalente de red con demanda máxima hora \\DMx\\ sin proyecto.", f"ilus:flujoDmxgsp{anio_actual}")
                    ]

                if omitir_no_cargados:
                    casos_h = [c for c in casos_h if resolver_ruta_imagen(c[0]) is not None]

                if not casos_h:
                    continue

                bloques_anexos.append(f"""
\\newpage
\\begin{{center}}
    \\vspace*{{\\fill}}
    \\Huge \\textbf{{FLUJO DE CARGA {anio_actual}}}
    \\vspace*{{\\fill}}
\\end{{center}}
""")
                for arch_img, cap_ilus, lbl_ilus in casos_h:
                    cmd_ilus = incluir_imagen_segura(arch_img, "width=0.95\\textwidth")
                    bloques_anexos.append(f"""
\\newpage
\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionsetup{{hypcap=false}}
        {cmd_ilus}
        \\vspace{{0.2cm}}
        \\captionof{{ilustracion}}{{{cap_ilus}}}
        \\label{{{lbl_ilus}}}
    \\end{{minipage}}
\\end{{center}}
""")

    codigo_flujos_carga = "\n".join(bloques_anexos)
    if incluir_anexos and codigo_flujos_carga.strip():
        bloque_seccion_anexos = f"""
\\clearpage
\\section{{ANEXOS}}
{codigo_flujos_carga}
"""
    else:
        bloque_seccion_anexos = ""

    # 9. Declaración automática de variables adicionales de config_vars
    comandos_extra = []
    llaves_reservadas = {
        "nombreProyecto", "capacidadMW", "OR", "FechaEntrada", "mesentregainformemasyear",
        "Latitud", "Longitud", "YearInicial", "YearFinal", "CTO", "SSEE", "NT", "nodo",
        "elementoProteccion", "referenciaPanel", "potenciaPanel", "cantidadPanel", "ubicacion",
        "CP", "Dmi", "DMx", "escenariomaxPerdidas", "perdidasmaximas", "refInversoruno",
        "Inversoruno", "cantidadInversoruno", "generacionaprobada", "potenciaminima",
        "recoCTO", "tipoproteccion", "recocabecera"
    }
    for k, v in params.items():
        if k not in llaves_reservadas and isinstance(k, str) and k.isalpha() and k.isascii():
            if isinstance(v, (str, int, float)):
                comandos_extra.append(f"\\providecommand{{\\{k}}}{{{escapar_latex(v)}}}")

    bloque_comandos_extra = "\n".join(comandos_extra)

    comandos_variables = f"""
% ---------- Variables del proyecto ----------
\\providecommand{{\\mesentregainformemasyear}}{{{mes_entrega}}}
\\providecommand{{\\nombreProyecto}}{{{nombre_proyecto}}}
\\providecommand{{\\capacidadMW}}{{{capacidad_mw}}}
\\providecommand{{\\OR}}{{{operador_red}}}
\\providecommand{{\\FechaEntrada}}{{{fecha_entrada}}}
\\providecommand{{\\Latitud}}{{{latitud}}}
\\providecommand{{\\Longitud}}{{{longitud}}}
\\providecommand{{\\YearInicial}}{{{year_inicial}}}
\\providecommand{{\\YearFinal}}{{{year_final}}}
\\providecommand{{\\CTO}}{{{cto}}}
\\providecommand{{\\SSEE}}{{{ssee}}}
\\providecommand{{\\NT}}{{{nt}}}
\\providecommand{{\\nodo}}{{{nodo}}}
\\providecommand{{\\elementoProteccion}}{{{elemento_proteccion}}}
\\providecommand{{\\referenciaPanel}}{{{referencia_panel}}}
\\providecommand{{\\potenciaPanel}}{{{potencia_panel}}}
\\providecommand{{\\cantidadPanel}}{{{cantidad_panel}}}
\\providecommand{{\\ubicacion}}{{{ubicacion}}}
\\providecommand{{\\CP}}{{{cp_hora}}}
\\providecommand{{\\Dmi}}{{{dmi_hora}}}
\\providecommand{{\\DMx}}{{{dmx_hora}}}
\\providecommand{{\\escenariomaxPerdidas}}{{{escenario_max_perd}}}
\\providecommand{{\\perdidasmaximas}}{{{perdidas_maximas}}}
\\providecommand{{\\refInversoruno}}{{{ref_inv_1}}}
\\providecommand{{\\Inversoruno}}{{{mod_inv_1}}}
\\providecommand{{\\cantidadInversoruno}}{{{cant_inv_1}}}
\\providecommand{{\\generacionaprobada}}{{{generacion_aprobada}}}
\\providecommand{{\\potenciaminima}}{{{potencia_minima}}}
\\providecommand{{\\recoCTO}}{{{reco_cto}}}
\\providecommand{{\\tipoproteccion}}{{{tipo_proteccion}}}
\\providecommand{{\\recocabecera}}{{{reco_cabecera}}}
{bloque_comandos_extra}

\\newcommand{{\\supuestos}}{{%
{texto_supuesto_activo}
}}

\\newcommand{{\\resumen}}{{%
\\begin{{itemize}}
\\item \\textbf{{Flujo de carga:}} {resumen_flujo}\\\\
\\item \\textbf{{Cortocircuito.}} {resumen_cortocircuito}\\\\
\\item \\textbf{{Coordinación de protecciones:}} {resumen_protecciones}\\\\
\\end{{itemize}}
}}

\\newcommand{{\\refInversores}}{{\\begin{{itemize}}
{items_ref_inv}
\\end{{itemize}}}}

\\newcommand{{\\Inversores}}{{\\begin{{itemize}}
{items_mod_inv}
\\end{{itemize}}}}

\\newcommand{{\\cantidadInversores}}{{\\begin{{itemize}}
{items_cant_inv}
\\end{{itemize}}}}

\\newcommand{{\\CONCLUSIONFERFILESCARGA}}{{%
{conclusion_perfiles_carga}
}}

\\newcommand{{\\equipos}}{{%
{texto_equipos}
}}

\\newcommand{{\\sistemaAC}}{{%
Para el cálculo de la protección general de los inversores, se tuvieron en cuenta los siguientes parámetros:
\\begin{{center}}
    \\begin{{minipage}}{{0.9\\textwidth}}
        \\centering
        \\captionof{{table}}{{Sistema AC}}
        \\label{{tab:sistema_AC}}
        \\begingroup
        \\setlength{{\\tabcolsep}}{{10pt}}
        \\renewcommand{{\\arraystretch}}{{1.3}}
        \\begin{{tabular}}{{|l|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{2}}{{|c|}}{{\\color{{white}}\\textbf{{Sistema AC}}}} \\\\ \\hline
            \\multicolumn{{2}}{{|c|}}{{Protección arreglo de inversores AC}} \\\\ \\hline
            Sistema AC & {ac_fases} \\\\ \\hline
            Potencia & \\capacidadMW \\\\ \\hline
            Tensión de Línea [kV] & {ac_tension_kv} \\\\ \\hline
            Intensidad máxima [A] & {ac_corriente_max} \\\\ \\hline
            Factor de carga continua & {ac_factor_carga} \\\\ \\hline
            Protección en tablero principal ($\\text{{I}}_{{\\text{{max}}}} \\times 1,25$) [A] & {ac_proteccion_tablero} \\\\ \\hline
        \\end{{tabular}}
        \\endgroup
        \\vspace{{2mm}}\\\\
        {{\\centering\\footnotesize
        \\textbf{{\\textit{{{ac_nota_pie}}}}}\\par
        }}
    \\end{{minipage}}
\\end{{center}}
}}

\\newcommand{{\\CONCLUSIONES}}{{%
\\begin{{itemize}}
{bloque_items_conclusiones}
\\end{{itemize}}
}}
"""

    cuerpo_documento = f"""
\\begin{{document}}

% --- PORTADA ---
\\begin{{titlepage}}
    \\thispagestyle{{fancy}}
    \\centering
    \\vspace*{{4cm}}
    {{\\fontsize{{20}}{{30}}\\selectfont \\textbf{{ESTUDIO DE CONEXIÓN SIMPLIFICADO GENERACIÓN DISTRIBUIDA SOLAR FV}}}} \\\\[0.1cm]

    {{\\fontsize{{22}}{{30}}\\selectfont \\textbf{{\\nombreProyecto{{}} - \\capacidadMW}}}} \\\\[3cm]
    {bloque_logo}

    \\vfill
    {{\\Large \\textbf{{Versión: 0}}}} \\\\[0.8cm]
    {{\\Large Medellín, Colombia.}} \\\\[0.5cm]
    {{\\Large \\mesentregainformemasyear}}\\\\[0.5cm]
\\end{{titlepage}}
\\newpage

% --- PÁGINA 2: CONTROL DE CAMBIOS ---
\\thispagestyle{{fancy}}
{bloque_tabla_cambios}
\\newpage %

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

% =====================================================================
% SECCIÓN 1: RESUMEN EJECUTIVO
% =====================================================================
\\newpage
\\section{{RESUMEN EJECUTIVO}}
\\subsection{{\\textit{{Objetivo y alcance}}}}
El presente documento tiene como objetivo principal analizar la viabilidad técnica del desarrollo del proyecto generación distribuida (GD) solar fotovoltaico \\nombreProyecto\\ en la red eléctrica de distribución de \\OR\\ en adelante OR (Operador de Red). El siguiente estudio se enfoca en proporcionar un análisis detallado de la conexión simplificada del sistema de generación distribuida a la red eléctrica existente. En tal estudio se resalta los parámetros eléctricos claves que garantizan la operación segura y eficiente del proyecto solar fotovoltaico GD \\nombreProyecto\\ con una potencia nominal de \\capacidadMW\\ , Este documento hace parte de lo establecido en el anexo 2 de la circular CREG 021 de 2022 y en el Capítulo 3 de la Resolución CREG 174 de 2021, la cual define el procedimiento de conexión para Generadores Distribuidos, y considerando los lineamientos de reporte de información de la Circular CREG 021 de 2022.\\\\

\\subsection{{\\textit{{Supuestos y herramienta de modelación}}}}
La información requerida para el modelamiento del área de influencia fue suministrada por el cliente y el OR comprendiendo el diagrama unifilar con sus respectivos nodos asociados al proyecto y sus respectivas cargas con el comportamiento en potencia activa y reactiva. El modelamiento de dicho diagrama unifilar se realizó en el software Digsilent Power Factory.\\\\
\\leavevmode\\\\
\\supuestos
{bloque_tabla_supuestos}

\\subsection{{\\textit{{Resumen de los principales resultados}}}}
{resumen_intro}\\\\
\\resumen
{resumen_cierre}

% =====================================================================
% SECCIÓN 2: DESCRIPCIÓN GENERAL DEL PROYECTO
% =====================================================================
\\section{{DESCRIPCIÓN GENERAL DEL PROYECTO}}
\\subsection{{\\textit{{información del proyecto}}}}

{sec2_intro}\\\\

\\begin{{table}}[h!]
    \\centering
    \\caption{{Coordenadas geográficas del Proyecto.}}
    \\label{{tab:coordenadas}}
    \\renewcommand{{\\arraystretch}}{{1.8}}
    \\begin{{tabular}}{{|c|c|c|}}
        \\hline
        \\rowcolor{{azulSeyep}}
        \\textbf{{\\textcolor{{white}}{{Nombre}}}} &
        \\textbf{{\\textcolor{{white}}{{Latitud}}}} &
        \\textbf{{\\textcolor{{white}}{{Longitud}}}} \\\\ \\hline
        \\nombreProyecto\\ & \\Latitud\\ & \\Longitud\\ \\\\ \\hline
    \\end{{tabular}}
\\end{{table}}
\\bigskip

\\begin{{table}}[h!]
    \\centering
    \\caption{{Descripción general del proyecto.}}
    \\label{{tab:descripcion_proyecto}}
    \\resizebox{{\\textwidth}}{{!}}{{%
        \\renewcommand{{\\arraystretch}}{{1.5}}
        \\begin{{tabular}}{{|c|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\textbf{{\\textcolor{{white}}{{ÍTEM}}}} & \\multicolumn{{3}}{{c|}}{{\\textbf{{\\textcolor{{white}}{{DESCRIPCIÓN}}}}}} \\\\ \\hline
            Proyecto. & \\multicolumn{{3}}{{c|}}{{GD \\nombreProyecto}} \\\\ \\hline
            Vida Útil & \\multicolumn{{3}}{{c|}}{{{vida_util}}} \\\\ \\hline
            Nodo y/o circuito de Conexión & \\multicolumn{{3}}{{c|}}{{\\nodo\\ / \\CTO{{}}}} \\\\ \\hline
            Potencia. & \\multicolumn{{3}}{{c|}}{{\\capacidadMW}} \\\\ \\hline
            Tipo Fuente de Energía & \\multicolumn{{3}}{{c|}}{{{tipo_fuente}}} \\\\ \\hline
            \\multirow{{3}}{{*}}{{Equipos.}}
                & {tipo_panel_etiqueta} \\potenciaPanel{{}} & \\referenciaPanel{{}} & \\cantidadPanel{{}} \\\\ \\cline{{2-4}}
                & \\begin{{minipage}}[t]{{6.5cm}}
                    \\refInversores
                    \\vspace{{1pt}}
                  \\end{{minipage}}
                & \\begin{{minipage}}[t]{{6.5cm}}
                    \\Inversores
                    \\vspace{{1pt}}
                  \\end{{minipage}}
                & \\begin{{minipage}}[t]{{3.5cm}}
                    \\cantidadInversores
                    \\vspace{{1pt}}
                  \\end{{minipage}} \\\\ \\cline{{2-4}}
                & {prot_item} & {prot_desc} & {prot_cant} \\\\ \\hline
        \\end{{tabular}}
    }}
\\end{{table}}

{bloque_geoespacial}
\\newpage
{sec2_cierre}
\\smallskip

\\begin{{figure}}[H]
    \\centering
    {img_ubicacion}
    \\caption{{Ubicación Geográfica GD \\nombreProyecto\\ - \\capacidadMW\\ , Google Earth}}
    \\label{{fig:ubicacion}}
\\end{{figure}}

% =====================================================================
% SECCIÓN 3: PARÁMETROS ELÉCTRICOS DE LOS EQUIPOS Y OPERACIÓN DECLARADA
% =====================================================================
\\newpage
\\section{{PARÁMETROS ELÉCTRICOS DE LOS EQUIPOS Y OPERACIÓN DECLARADA}}
\\subsection{{\\textit{{Equipos}}}}

{sec3_intro}
\\\\
\\equipos

\\begin{{figure}}[h]
    \\centering
    {img_ficha_panel}
    \\caption{{Hoja técnica del panel fotovoltaico}}
    \\label{{fig:fichapanel}}
\\end{{figure}}
\\smallskip

{codigo_fig_inversores}

\\subsection{{\\textit{{Información OR}}}}
{sec3_or_texto}\\\\
\\leavevmode\\\\
Dado lo anterior, la información suministrada se puede apreciar en las {bloque_informacion_or}

% =====================================================================
% SECCIÓN 4: INFORMACIÓN DE ENTRADA Y SUPUESTOS DE SALIDA
% =====================================================================
\\section{{INFORMACIÓN DE ENTRADA Y SUPUESTOS DE SALIDA}}
\\subsection{{\\textit{{Modelo de la zona de influencia}}}}
{sec4_1_texto}

\\begin{{figure}}[h]
    \\centering
    {img_unifilar}
    \\caption{{Diagrama Unifilar del cto \\CTO}}
    \\label{{fig:Unifilar}}
\\end{{figure}}

\\subsection{{\\textit{{Horizonte de análisis}}}}
{sec4_2_texto}

\\begin{{table}}[h!]
    \\centering
    \\caption{{Horizonte de análisis.}}
    \\label{{tab:horizonte}}
    \\footnotesize
    \\setlength{{\\tabcolsep}}{{20pt}}
    \\begin{{tabular}}{{|c|c|}}
        \\hline
        \\rowcolor{{azulSeyep}}
        \\multicolumn{{2}}{{|c|}}{{\\textbf{{\\textcolor{{white}}{{Horizonte}}}}}} \\\\ \\hline
        \\YearInicial & \\YearFinal \\\\ \\hline
    \\end{{tabular}}
    \\setlength{{\\tabcolsep}}{{3pt}}
\\end{{table}}
\\vspace{{-10pt}}

\\subsection{{\\textit{{Información de la demanda de potencia}}}}
{sec4_3_texto}

{csv_demanda_energia}

\\subsection{{\\textit{{Información de energía producida Vs Energía demandada.}}}}
{sec4_4_intro}

{csv_consumo_vs_gen}

{sec4_4_curva}

\\begin{{figure}}[H]
    \\centering
    {img_curva_cto}
    \\caption{{{caption_curva_cto}}}
    \\label{{fig:curvadecarga211}}
\\end{{figure}}

{sec4_4_comp}

\\begin{{figure}}[H]
    \\centering
    {img_consumo_gen}
    \\caption{{Curva de consumo y generación.}}
    \\label{{fig:consumoygeneracion}}
\\end{{figure}}

% =====================================================================
% SECCIÓN 5: METODOLOGÍA
% =====================================================================
\\newpage
\\section{{METODOLOGÍA}}
{sec5_intro}\\\\

\\subsection{{\\textit{{Criterios técnicos}}}}
Para garantizar una conexión y operación que cumpla los criterios técnicos de calidad, seguridad y confiabilidad, en el diseño, ejecución y mantenimiento del proyecto se realiza este estudio bajo las siguientes normativas colombianas.
\\begin{{itemize}}
\\item Reglamento técnico de instalaciones eléctricas (RETIE).
\\item Circular CREG 021 de 2022.
\\item Circular CREG 174 de 2021.
\\item Circular CREG 015 de 2018.
\\item Circular CREG 025 de 1995.
\\end{{itemize}}
Teniendo en cuenta las anteriores normativas se establece algunos de los criterios y límites para tener en cuenta dentro de este documento.\\\\

\\begin{{itemize}}
\\item CREG 025 de 1995, “El STN se planeará de tal forma que permita, en conjunto con la generación, los sistemas de transmisión regionales y los sistemas de distribución local, Asegurar que la tensión en las barras de carga a nivel de 220 kV y superiores no sea inferior al 90\\% del valor nominal, ni superior al 110\\%”.
\\item Circular CREG 174 de 2021, en caso de implementar inversores en los proyectos, la capacidad del proyecto corresponde a la sumatoria de las capacidades nominales de los inversores, en el lado con conexión al SIN, la capacidad se deberá asumir con un factor de potencia unitario.
\\item Circular CREG 025 de 1995, Para las líneas de transmisión se consideran flujos aceptables, en condiciones normales de operación, cuando sean iguales o menores del 100\\% de su capacidad nominal. En contingencia se admiten sobrecargas hasta el valor máximo permitido para el elemento bajo condiciones de emergencia y que se encuentra declarado por el agente propietario en el PARATEC.
\\item Para transformadores se consideran flujos aceptables en condiciones normales de operación, cuando sean iguales o menores del 100\\% de su capacidad nominal. En contingencia se admiten sobrecargas hasta el valor máximo permitido para el elemento bajo condiciones de emergencia y que se encuentra declarado por el agente propietario en el PARATEC.
\\item Artículo 5 de la resolución CREG 030 de 2018, Literal a, Literal c, “La Cantidad de energía en una hora se pueden entregar los GD o AGEP que entregan energía a la red, cuyo sistema de producción de energía sea el compuesto por fotovoltaico sin capacidad de almacenamiento, conectados al mismo circuito o transformador del nivel de tensión 1, no debe superar el 50\\% de promedio anual de las horas de mínima demandad diaria de energía registradas para el año anterior al de solicitud de conexión en la franja horaria comprometida entre 6 am y 6 pm.”
\\end{{itemize}}

\\subsection{{\\textit{{Descripción de los análisis a realizar}}}}
En el presente estudio de conexión se realizan los siguientes análisis técnicos del proyecto solar fotovoltaico de generación y consumo:\\\\
A continuación, se instalan los estudios realizados:

\\begin{{itemize}}
    \\item \\textbf{{Generación de energía eléctrica:}} proyección de la máxima generación del proyecto solar a la red de distribución de energía eléctrica propiedad OR.
    \\item \\textbf{{Consumo de la instalación eléctrica:}} Estimado de la energía requerida por el cliente OR.
    \\item \\textbf{{Estudio de flujo de carga:}} Monitorear los niveles de tensión en las barras; así como la cargabilidad en transformadores y líneas de transmisión para que no sobrepasen los límites permitidos.
    \\item \\textbf{{Estudio de pérdidas:}} Analizar las pérdidas del sistema de distribución locas (SDL) con la inclusión del proyecto de generación.
    \\item \\textbf{{Estudio de cortocircuito:}} Monitorear los aportes de corriente de cortocircuito en las subestaciones, así como monitorear que estas no se sobrepasen los niveles máximos de corto en las subestaciones del sistema.
    \\item \\textbf{{Estudio de protecciones:}} Analizar el comportamiento de las protecciones del OR en conjunto con las del proyecto de generación para diferentes eventos en el SDL, buscando garantizar selectividad y confiabilidad.
\\end{{itemize}}

% =====================================================================
% SECCIÓN 6: DESCRIPCIÓN DE LOS ESCENARIOS DE ANÁLISIS
% =====================================================================
\\section{{DESCRIPCIÓN DE LOS ESCENARIOS DE ANÁLISIS}}
Para clasificar cada uno de los resultados entregados en este estudio, se seleccionaron tres variables que describen cada uno de los escenarios de análisis. Estas variables son:
\\begin{{itemize}}
  \\item Año
    \\begin{{itemize}}
        \\item \\textbf{{\\YearInicial}}
        \\item \\textbf{{\\YearFinal}}
    \\end{{itemize}}
  \\item Despacho de demanda
    \\begin{{itemize}}
        \\item {sec6_despacho}
        \\begin{{itemize}}
            \\item \\textbf{{Generación máxima de la planta solar y demanda coincidente suministrada:}} {sec6_gen_max}
        \\end{{itemize}}
    \\end{{itemize}}
\\end{{itemize}}

% =====================================================================
% SECCIÓN 7: RESULTADOS DE LOS ANÁLISIS ELÉCTRICOS
% =====================================================================
\\newpage
\\section{{RESULTADOS DE LOS ANÁLISIS ELÉCTRICOS.}}
\\subsection{{\\textit{{Flujo de carga AC en estado estable para condiciones normales de operación (Sistema Des-balanceado)}}}}

A continuación, se presenta la leyenda que contiene todos los parámetros presentados en cada una de las cajas de resultados de la simulación, para el estudio de flujo de carga.
\\begin{{table}}[htbp]
    \\centering
    \\caption{{Convenciones de los cuadros de resultados de las simulaciones}}
    \\label{{tab:convencionesflujos}}
    {img_conv_flujos}
\\end{{table}}

Además, para todas las simulaciones de flujo, se cuenta con la siguiente paleta de colores, en ella se puede ver como las líneas que no cuentan con un color negro están por debajo del 100\\% de cargabilidad, y las barras con un color verde, se encuentran cercanas a 1 p.u. en tensión.

\\begin{{figure}}[h]
    \\centering
    {img_cod_colores}
    \\caption{{Código de colores en las simulaciones}}
    \\label{{fig:codigocoloresflujo}}
\\end{{figure}}
\\smallskip

\\newpage
A continuación, se presenta el resumen de los resultados de cargabilidad y perfil de tensión de los años y escenarios de demanda y generación analizados para el circuito \\CTO.

\\begin{{table}}[H]
    \\centering
    \\caption{{Flujo de Cargabilidad}}
    \\label{{tab:Cargabilidad}}
    {img_cargabilidad}
\\end{{table}}

{sec7_cargabilidad_txt}\\\\
\\leavevmode\\\\
En la \\cref{{tab:TensionesPU}} se muestran los resultados de los perfiles de tensión del circuito con y sin proyecto de generación.\\\\

\\begin{{table}}[htbp]
    \\centering
    \\caption{{Tensión de barras}}
    \\label{{tab:TensionesPU}}
    {img_tensiones_pu}
\\end{{table}}

\\CONCLUSIONFERFILESCARGA \\\\
\\leavevmode\\\\
Con el fin de evaluar el cambio en el perfil de tensión de los nodos de la zona de interés del proyecto GD \\nombreProyecto, se presentan los valores p.u. de las tensiones del circuito la \\cref{{fig:perfiltensionCTO}}

\\begin{{figure}}[h]
    \\centering
    {img_perfil_cto}
    \\caption{{Perfil de tensión de la totalidad del circuito \\CTO}}
    \\label{{fig:perfiltensionCTO}}
\\end{{figure}}

\\clearpage
{bloque_contingencia}

\\clearpage
\\subsection{{\\textit{{Cálculo de pérdidas}}}}
Para determinar las pérdidas del sistema se realizan simulaciones de flujo de carga en los tres horarios, con y sin proyecto, con su respectivo despacho de acuerdo con la hora. Evaluando los cambios de perdida en los horizontes de tiempo.

\\begin{{table}}[htbp]
    \\centering
    \\caption{{Pérdidas SDL [kW]}}
    \\label{{tab:Perdidas}}
    {img_perdidas}
\\end{{table}}

{sec7_perdidas_texto}

\\subsection{{\\textit{{Verificación del nivel de cortocircuito (Monofásico y Trifásico con la NORMA IEC60909)}}}}
Según el sistema modelado se presentan los siguientes análisis propuestos, en base a la IEC 60909 versión 2016, la cual incorpora el aporte de corriente de cortocircuito de las tecnologías de generación basadas en inversores como la solar fotovoltaica.
\\\\
Se tienen las siguientes convenciones:
\\begin{{itemize}}
    \\item Skss = Potencia de cortocircuito inicial.
    \\item Ikss = Corriente de corto circuito simétrica inicial.
    \\item Ip = Corriente de corto circuito máxima instantánea.
\\end{{itemize}}

En la \\cref{{tab:convencionescortos}} se puede apreciar la leyenda de las imágenes de los estudios, la cual representa el contenido de las cajas de resultados. Tanto para un corto trifásico como para un monofásico. \\\\
\\begin{{table}}[H]
    \\centering
    \\caption{{Convenciones de los cuadros de resultados de las simulaciones de corto}}
    \\label{{tab:convencionescortos}}
    {img_leyendas_cortos}
\\end{{table}}

En la \\cref{{tab:cortos}} se muestran los niveles de corto en los tres escenarios, con proyecto y sin proyecto, para los años del horizonte de análisis, en las tablas se muestran los resultados de los elementos de la zona de influencia, los resultados de todos los nodos se encuentran en el archivo de Excel anexado al estudio.

\\begin{{table}}[htbp]
    \\centering
    \\caption{{Resultados de cortocircuito}}
    \\label{{tab:cortos}}
    {img_cortos}
\\end{{table}}

\\newpage
\\subsection{{\\textit{{Calidad de potencia}}}}
Declaración técnica del equipo en cuanto al cumplimiento de los parámetros establecidos en la IEEE 1547 y de estándares en cuanto a la calidad de la potencia (inyección de armónicos a la red y fluctuaciones de tensión, etc) sujetos a la verificación con medidas en campo antes y después de la instalación del proyecto.
\\\\
La IEEE 1547 provee especificaciones y requerimientos técnicos referente al desempeño, operación, ensayos, consideraciones de seguridad y mantenimiento de los generadores que se integran al SIN. \\\\

Los siguientes inversores propuestos para el proyecto GD \\nombreProyecto.

\\Inversores

Cumplen con los estándares de las siguientes normativas que pueden ser consultadas en la ficha técnica del equipo, donde la distorsión armónica total inyectada del equipo es <3\\% y cumple con su función ANTI-ISLA en caso de faltar onda de tensión del operador:

\\begin{{itemize}}
     \\item \\textbf{{IEEE 1574}}
     \\item \\textbf{{UL1747}}
     \\item \\textbf{{Resolución CREG 024 de 2005}}
\\end{{itemize}}

\\subsection{{\\textit{{Análisis para evitar el funcionamiento en isla}}}}
Con base a lo estipulado en la circular 021 del 2022 del CNO, en específico en el apartado 8.5 que dice “El funcionamiento en isla de una red de distribución consiste en la posible alimentación temporal del sistema de generación a usuarios en ausencia de la red principal. Este funcionamiento debe ser evitado con el fin de mantener la seguridad de la operación y la calidad de suministro dentro los límites establecidos. En los casos donde la generación es capaz de mantener autónomamente los valores de tensión y frecuencia, existirá riesgo de funcionamiento en isla cunado cumpla la siguiente relación”

\\begin{{equation}}
    \\left( \\sum_{{i=1 \\text{{ a }} N}} P_{{maxgi}} \\right) + P_{{gnuevo}} \\geq P_{{mindem}}
\\end{{equation}}

\\newpage
\\vspace{{0.5cm}}
\\noindent \\textbf{{Donde:}}
\\begin{{itemize}}
    \\item $P_{{maxgi}}$: Potencia Instalada del generador $i$.
    \\item $P_{{gnuevo}}$: Potencia Máxima del generador a estudiar.
    \\item $P_{{mindem}}$: Potencia demanda mínima.
\\end{{itemize}}
De esta forma se presenta que:

\\begin{{equation}}
    \\label{{eq:balance_potencia}}
    \\text{{\\generacionaprobada}} + \\text{{\\capacidadMW}} \\geq \\text{{\\potenciaminima}}
\\end{{equation}}

{sec7_isla_conclusion}

% =====================================================================
% SECCIÓN 8: VERIFICACIÓN DE PROTECCIONES
% =====================================================================
\\section{{VERIFICACIÓN DE PROTECCIONES}}
La verificación de protecciones se realiza en el documento ``EACP'' suministrado como anexo. Con el objetivo de plasmar en este documento la información básica de los elementos que componen el sistema de porotecciones, se citan las tablas resumen a continuación:
\\\\

\\sistemaAC

En el sistema fotovoltaico y tablero principal existen las siguientes protecciones:

\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionof{{table}}{{Protección GD \\nombreProyecto}}
        \\label{{tab:SEL}}
        \\begingroup
        \\setlength{{\\tabcolsep}}{{8pt}}
        \\renewcommand{{\\arraystretch}}{{1.2}}
        \\small
        \\begin{{tabular}}{{|l|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{1}}{{|c|}}{{\\color{{white}}\\textbf{{Protege}}}} & \\color{{white}}\\textbf{{TIPO}} & \\color{{white}}\\textbf{{REFERENCIA}} & \\color{{white}}\\textbf{{TC / TP}} \\\\ \\hline
            {gd_protege} & {gd_tipo} & {gd_ref} & {gd_tctp} \\\\ \\hline
        \\end{{tabular}}
        \\endgroup
    \\end{{minipage}}
\\end{{center}}

\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionof{{table}}{{Protección Inversores}}
        \\label{{tab:LSI}}
        \\begingroup
        \\setlength{{\\tabcolsep}}{{8pt}}
        \\renewcommand{{\\arraystretch}}{{1.2}}
        \\small
        \\begin{{tabular}}{{|l|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{1}}{{|c|}}{{\\color{{white}}\\textbf{{Protege}}}} & \\color{{white}}\\textbf{{TIPO}} & \\color{{white}}\\textbf{{Ajuste}} \\\\ \\hline
            {inv_protege} & {inv_tipo} & {inv_ajuste} \\\\ \\hline
        \\end{{tabular}}
        \\endgroup
    \\end{{minipage}}
\\end{{center}}

En el circuito se tienen la siguientes protecciones por parte del OR:

\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionof{{table}}{{Protección del circuito \\recoCTO}}
        \\label{{tab:SEL_OR}}
        \\begingroup
        \\setlength{{\\tabcolsep}}{{8pt}}
        \\renewcommand{{\\arraystretch}}{{1.2}}
        \\small
        \\begin{{tabular}}{{|l|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{1}}{{|c|}}{{\\color{{white}}\\textbf{{Protege}}}} & \\color{{white}}\\textbf{{TIPO}} \\\\ \\hline
            {or_protege} & {or_tipo_desc} \\\\ \\hline
        \\end{{tabular}}
        \\endgroup
    \\end{{minipage}}
\\end{{center}}

El resto de consideraciones en cuanto a protecciones se dejan plasmados en el anexo ``Anexo EACP''. El resumen de los ajustes establecidos en dicho documento se muestra en las \\cref{{tab:ajustesrecoProyecto,tab:resumenajustestotales}}.

\\begin{{center}}
    \\begin{{minipage}}{{1\\textwidth}}
        \\centering
        \\captionof{{table}}{{Ajustes de protección para el Reconectador \\nombreProyecto.}}
        \\label{{tab:ajustesrecoProyecto}}
        \\begingroup
        \\setlength{{\\tabcolsep}}{{12pt}}
        \\renewcommand{{\\arraystretch}}{{1.3}}
        \\small
        \\begin{{tabular}}{{|l|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\multicolumn{{1}}{{|c|}}{{\\color{{white}}\\textbf{{Parámetro}}}} & \\color{{white}}\\textbf{{Pick Up [Aprim]}} & \\color{{white}}\\textbf{{DIAL [s]}} & \\color{{white}}\\textbf{{Curva}} \\\\ \\hline
            {contenido_filas_reco}
        \\end{{tabular}}
        \\endgroup
    \\end{{minipage}}
\\end{{center}}

\\begin{{table}}[H]
    \\centering
    \\captionof{{table}}{{Resumen ajuste de protecciones sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal > 0,25 MW conectados al SDL}}
    \\label{{tab:resumenajustestotales}}
    \\begingroup
    \\resizebox{{\\textwidth}}{{!}}{{%
        \\renewcommand{{\\arraystretch}}{{1.3}}
        \\begin{{tabular}}{{|c|c|c|}}
            \\hline
            \\rowcolor{{azulSeyep}}
            \\textbf{{\\color{{white}}Función}} & \\textbf{{\\color{{white}}Ajustes}} & \\textbf{{\\color{{white}}Temporización}} \\\\ \\hline
            {contenido_filas_sist}
        \\end{{tabular}}
    }}
    \\endgroup
\\end{{table}}

% =====================================================================
% SECCIÓN 9: CONCLUSIONES Y SECCIÓN 10: ANEXOS
% =====================================================================
\\clearpage
\\section{{CONCLUSIONES}}
\\CONCLUSIONES
{bloque_seccion_anexos}
\\end{{document}}
"""

    contenido_latex = (
        generar_preambulo()
        + comandos_variables
        + cuerpo_documento
    )

    tex_filename = "Estudio_Conexion.tex"
    pdf_filename = "Estudio_Conexion.pdf"

    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write(contenido_latex)

    try:
        cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_filename]
        
        proceso1 = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if proceso1.returncode != 0:
            log_contenido = ""
            if os.path.exists("Estudio_Conexion.log"):
                with open("Estudio_Conexion.log", "r", encoding="utf-8", errors="ignore") as log_file:
                    log_contenido = log_file.read()

            todas_lineas = log_contenido.splitlines()
            bloques_error = []
            for idx, line in enumerate(todas_lineas):
                if line.startswith("!"):
                    fragmento = "\n".join(todas_lineas[idx:idx + 4])
                    bloques_error.append(fragmento)

            detalle = "\n---\n".join(bloques_error[:3]) if bloques_error else "Error desconocido en LaTeX."
            return False, f"Fallo de compilación:\n{detalle}"

        proceso2 = subprocess.run(cmd, capture_output=True, text=True, timeout=45)

        if os.path.exists(pdf_filename):
            return True, pdf_filename
        else:
            return False, "No se encontró el PDF resultante tras la compilación."

    except subprocess.TimeoutExpired:
        return False, "La compilación tardó demasiado y fue interrumpida (timeout de 45s)."
    except subprocess.CalledProcessError as e:
        return False, f"Error en el proceso LaTeX: {str(e)}"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"

