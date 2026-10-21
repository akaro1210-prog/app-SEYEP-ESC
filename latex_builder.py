import os
import subprocess
from datetime import datetime
import pandas as pd

try:
    import streamlit as st
except ImportError:
    st = None

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
    Normaliza claves como 'max width' y 'max height' a claves nativas de graphicx (width, height)
    para evitar el error de xkeyval / Gin si adjustbox no tiene la opción [export].
    """
    opciones_norm = (
        str(opciones)
        .replace("max width=", "width=")
        .replace("max height=", "height=")
    )
    ruta_resuelta = resolver_ruta_imagen(nombre_archivo)
    if ruta_resuelta:
        return f"\\includegraphics[{opciones_norm}]{{{ruta_resuelta}}}"
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
\\begin{{table}}[H]
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
        filas_latex.append("        0 & Informe Inicial. & 23/09/2026 & \\\\ \\hline")

    contenido_filas = "\n".join(filas_latex)

    return f"""    \\begin{{tabular}}{{|c|l|c|l|}}
        \\hline
        \\rowcolor{{azulSeyep}} 
        \\textbf{{\\textcolor{{white}}{{VERSIÓN No.}}}} & 
        \\textbf{{\\textcolor{{white}}{{DESCRIPCIÓN}}}} & 
        \\textbf{{\\textcolor{{white}}{{FECHA}}}} & 
        \\textbf{{\\textcolor{{white}}{{OBSERVACIONES}}}} \\\\
        \\hline
{contenido_filas}
    \\end{{tabular}}"""

def generar_bloque_tabla_supuestos(usar_tabla_upme, df_supuestos_upme, archivo_or_path, titulo_tabla=None):
    """Genera el bloque LaTeX de la tabla de proyección de demanda con \\label{tab:UPME}."""
    if not titulo_tabla or not str(titulo_tabla).strip():
        titulo_tabla = (
            "Proyección de la demanda de energía eléctrica y potencia máxima, tabla de Demanda anual de Energía eléctrica por áreas SIN (GWh-año) para la región Antioquia 2026-2040 Rev 2026."
            if usar_tabla_upme
            else "Proyección de demanda suministrada por el Operador de Red"
        )
    caption_limpio = escapar_latex(str(titulo_tabla).strip())

    if usar_tabla_upme:
        if df_supuestos_upme is not None:
            if isinstance(df_supuestos_upme, pd.DataFrame) and not df_supuestos_upme.empty:
                registros = df_supuestos_upme.fillna("").to_dict(orient="records")
            elif isinstance(df_supuestos_upme, list):
                registros = df_supuestos_upme
            else:
                registros = []
        else:
            # Datos predeterminados oficiales UPME Región Antioquia 2026-2040
            registros = [
                {"Año": "2026", "Esc. Medio": "12.010", "IC Sup. 95%": "12.324", "IC Inf. 95%": "11.698", "IC Sup. 68%": "12.179", "IC Inf. 68%": "11.842", "Tasa Crec.": "--"},
                {"Año": "2027", "Esc. Medio": "12.404", "IC Sup. 95%": "13.134", "IC Inf. 95%": "11.678", "IC Sup. 68%": "12.795", "IC Inf. 68%": "12.015", "Tasa Crec.": "1,033"},
                {"Año": "2028", "Esc. Medio": "12.490", "IC Sup. 95%": "13.459", "IC Inf. 95%": "11.528", "IC Sup. 68%": "13.009", "IC Inf. 68%": "11.974", "Tasa Crec.": "1,007"},
                {"Año": "2029", "Esc. Medio": "12.669", "IC Sup. 95%": "13.842", "IC Inf. 95%": "11.505", "IC Sup. 68%": "13.298", "IC Inf. 68%": "12.045", "Tasa Crec.": "1,014"},
                {"Año": "2030", "Esc. Medio": "12.888", "IC Sup. 95%": "14.248", "IC Inf. 95%": "11.541", "IC Sup. 68%": "13.617", "IC Inf. 68%": "12.166", "Tasa Crec.": "1,017"},
                {"Año": "2031", "Esc. Medio": "13.163", "IC Sup. 95%": "14.704", "IC Inf. 95%": "11.639", "IC Sup. 68%": "13.989", "IC Inf. 68%": "12.345", "Tasa Crec.": "1,021"},
                {"Año": "2032", "Esc. Medio": "13.428", "IC Sup. 95%": "15.141", "IC Inf. 95%": "11.735", "IC Sup. 68%": "14.347", "IC Inf. 68%": "12.520", "Tasa Crec.": "1,02"},
                {"Año": "2033", "Esc. Medio": "13.700", "IC Sup. 95%": "15.580", "IC Inf. 95%": "11.842", "IC Sup. 68%": "14.708", "IC Inf. 68%": "12.703", "Tasa Crec.": "1,02"},
                {"Año": "2034", "Esc. Medio": "14.006", "IC Sup. 95%": "16.055", "IC Inf. 95%": "11.984", "IC Sup. 68%": "15.105", "IC Inf. 68%": "12.921", "Tasa Crec.": "1,022"},
                {"Año": "2035", "Esc. Medio": "14.302", "IC Sup. 95%": "16.517", "IC Inf. 95%": "12.118", "IC Sup. 68%": "15.490", "IC Inf. 68%": "13.130", "Tasa Crec.": "1,021"},
                {"Año": "2036", "Esc. Medio": "14.614", "IC Sup. 95%": "16.996", "IC Inf. 95%": "12.267", "IC Sup. 68%": "15.892", "IC Inf. 68%": "13.354", "Tasa Crec.": "1,022"},
                {"Año": "2037", "Esc. Medio": "14.951", "IC Sup. 95%": "17.503", "IC Inf. 95%": "12.438", "IC Sup. 68%": "16.320", "IC Inf. 68%": "13.602", "Tasa Crec.": "1,023"},
                {"Año": "2038", "Esc. Medio": "15.266", "IC Sup. 95%": "17.985", "IC Inf. 95%": "12.591", "IC Sup. 68%": "16.725", "IC Inf. 68%": "13.829", "Tasa Crec.": "1,021"},
                {"Año": "2039", "Esc. Medio": "15.593", "IC Sup. 95%": "18.480", "IC Inf. 95%": "12.755", "IC Sup. 68%": "17.142", "IC Inf. 68%": "14.069", "Tasa Crec.": "1,021"},
                {"Año": "2040", "Esc. Medio": "15.887", "IC Sup. 95%": "18.939", "IC Inf. 95%": "12.889", "IC Sup. 68%": "17.525", "IC Inf. 68%": "14.277", "Tasa Crec.": "1,019"}
            ]

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
        return f"""\\begin{{table}}[H]
   \\centering
   \\caption{{{caption_limpio}}}
   \\label{{tab:UPME}}
   \\resizebox{{\\textwidth}}{{!}}{{% 
        \\renewcommand{{\\arraystretch}}{{1.3}} 
        \\begin{{tabular}}{{|c|c|c|c|c|c|c|}}
          \\hline
            \\rowcolor{{azulSeyep}} 
            \\textbf{{\\textcolor{{white}}{{Año}}}} & \\textbf{{\\textcolor{{white}}{{Esc. Medio}}}} & \\textbf{{\\textcolor{{white}}{{IC Sup. 95\\%}}}} & \\textbf{{\\textcolor{{white}}{{IC Inf. 95\\%}}}} & \\textbf{{\\textcolor{{white}}{{IC Sup. 68\\%}}}} & \\textbf{{\\textcolor{{white}}{{IC Inf. 68\\%}}}} & \\textbf{{\\textcolor{{white}}{{Tasa Crec.}}}} \\\\ \\hline
{contenido_filas}
        \\end{{tabular}}%
   }}
\\end{{table}}"""

    if not usar_tabla_upme and archivo_or_path and os.path.exists(archivo_or_path):
        ext = os.path.splitext(archivo_or_path)[1].lower()
        ruta_latex = archivo_or_path.replace("\\", "/")
        if ext in [".png", ".jpg", ".jpeg"]:
            return f"""
\\vspace{{0.4cm}}
\\begin{{table}}[H]
\\centering
\\caption{{{caption_limpio}}}
\\label{{tab:UPME}}
\\vspace{{0.2cm}}
\\includegraphics[width=\\textwidth, height=0.65\\textheight, keepaspectratio]{{{ruta_latex}}}
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
\\begin{{table}}[H]
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
\usepackage{etoolbox}
\IfFileExists{placeins.sty}{
  \usepackage[section]{placeins}
}{
  \providecommand{\FloatBarrier}{\relax}
}

% ---------- Control estricto de retención de tablas y figuras en su sección ----------
\pretocmd{\section}{\FloatBarrier}{}{}
\pretocmd{\subsection}{\FloatBarrier}{}{}
\pretocmd{\subsubsection}{\FloatBarrier}{}{}
\renewcommand{\topfraction}{0.85}
\renewcommand{\bottomfraction}{0.85}
\renewcommand{\textfraction}{0.15}
\renewcommand{\floatpagefraction}{0.80}
\setcounter{topnumber}{4}
\setcounter{bottomnumber}{4}
\setcounter{totalnumber}{6}
\setlength{\floatsep}{10pt plus 2pt minus 2pt}
\setlength{\textfloatsep}{14pt plus 2pt minus 3pt}
\setlength{\intextsep}{10pt plus 2pt minus 2pt}
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
\usepackage[export]{adjustbox}      
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
      \begin{table}[H]
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

def adaptar_texto_regimen(texto, es_autogen):
    """
    Adapta automáticamente textos y párrafos del informe según el régimen
    seleccionado: Generación Distribuida (GD) o Autogenerador.
    Garantiza que todo el documento quede completamente relacionado a esa opción.
    """
    if not isinstance(texto, str) or not texto.strip():
        return texto
    t = texto
    if es_autogen:
        t = t.replace(r"GD \nombreProyecto", r"Autogenerador \nombreProyecto")
        t = t.replace(r"GD\nombreProyecto", r"Autogenerador \nombreProyecto")
        t = t.replace(r"GD \capacidadMW", r"Autogenerador \capacidadMW")
        t = t.replace(r"de GD \capacidadMW", r"de Autogeneración \capacidadMW")
        t = t.replace(r"del GD \nombreProyecto", r"del Autogenerador \nombreProyecto")
        t = t.replace(r"al GD \nombreProyecto", r"al Autogenerador \nombreProyecto")
        t = t.replace(r"el GD \nombreProyecto", r"el Autogenerador \nombreProyecto")
        t = t.replace(r"proyecto GD", r"proyecto Autogenerador")
        t = t.replace(r"Proyecto GD", r"Proyecto Autogenerador")
        t = t.replace(r"estable con GD", r"estable con Autogenerador")
        t = t.replace(r"operación del GD", r"operación del Autogenerador")
        t = t.replace(r"instalación del GD", r"instalación del Autogenerador")
        t = t.replace(r"donde los Generadores Distribuidos (GD)", r"donde los Autogeneradores")
        t = t.replace(r"Generadores Distribuidos (GD)", r"Autogeneradores")
        t = t.replace(r"Protección GD", r"Protección Autogenerador")
        t = t.replace(r"protección GD", r"protección Autogenerador")
    else:
        t = t.replace(r"Autogenerador \nombreProyecto", r"GD \nombreProyecto")
        t = t.replace(r"de Autogeneración \capacidadMW", r"de GD \capacidadMW")
        t = t.replace(r"del Autogenerador \nombreProyecto", r"del GD \nombreProyecto")
        t = t.replace(r"al Autogenerador \nombreProyecto", r"al GD \nombreProyecto")
        t = t.replace(r"el Autogenerador \nombreProyecto", r"el GD \nombreProyecto")
        t = t.replace(r"proyecto Autogenerador", r"proyecto GD")
        t = t.replace(r"Proyecto Autogenerador", r"Proyecto GD")
        t = t.replace(r"estable con Autogenerador", r"estable con GD")
        t = t.replace(r"operación del Autogenerador", r"operación del GD")
        t = t.replace(r"instalación del Autogenerador", r"instalación del GD")
        t = t.replace(r"donde los Autogeneradores", r"donde los Generadores Distribuidos (GD)")
        t = t.replace(r"Protección Autogenerador", r"Protección GD")
        t = t.replace(r"protección Autogenerador", r"protección GD")
    return t


def generar_latex_secciones_personalizadas(sec_padre, params, es_autogen):
    secciones_pers = params.get("secciones_personalizadas", [])
    if not isinstance(secciones_pers, list):
        try:
            import streamlit as st
            secciones_pers = st.session_state.get("secciones_personalizadas", [])
        except Exception:
            secciones_pers = []
    
    bloques = []
    for s in secciones_pers:
        if s.get("padre") == sec_padre:
            tit = s.get("titulo", "Sección Personalizada").strip()
            tit_escapado = escapar_latex(tit)
            nivel_str = s.get("nivel", "\subsection")
            if "\subsubsection" in nivel_str:
                cmd_nivel = f"\subsubsection{{{tit_escapado}}}"
            elif "\section" in nivel_str:
                cmd_nivel = f"\clearpage\section{{{tit_escapado}}}"
            else:
                cmd_nivel = f"\subsection{{{tit_escapado}}}"
            
            raw_contenido = s.get("contenido", "")
            contenido_adaptado = adaptar_texto_regimen(raw_contenido, es_autogen)
            
            bloque_s = rf"""

{cmd_nivel}
{contenido_adaptado}
"""
            
            # Tabla adicional si fue activada
            if s.get("incluir_tabla"):
                cap_tab = escapar_latex(s.get("tabla_caption", "Tabla de Parámetros Adicionales"))
                tab_txt = s.get("tabla_texto", "").strip()
                if "&" not in tab_txt and "," in tab_txt:
                    filas = []
                    for linea in tab_txt.splitlines():
                        if linea.strip():
                            filas.append(" & ".join([escapar_latex(c.strip()) for c in linea.split(",")]) + r" \ \hline")
                    cuerpo_tab = "\\n".join(filas)
                    num_cols = max([len(linea.split(",")) for linea in tab_txt.splitlines() if linea.strip()] or [2])
                    spec_cols = "|" + "c|" * num_cols
                else:
                    cuerpo_tab = tab_txt
                    spec_cols = "|c|c|"
                
                bloque_s += f"""
\begin{{table}}[H]
    \centering
    \caption{{{cap_tab}}}
    \begingroup
    \adjustbox{{max width=\textwidth}}{{%
        \renewcommand{{\arraystretch}}{{1.3}}
        \begin{{tabular}}{{{spec_cols}}}
            \hline
            {cuerpo_tab}
        \end{{tabular}}
    }}
    \endgroup
\end{{table}}
"""
            # Figura adicional si fue cargada
            if s.get("incluir_figura") and s.get("figura_nombre"):
                nom_fig = s.get("figura_nombre")
                cap_fig = escapar_latex(s.get("figura_caption", "Figura Adicional"))
                bloque_s += f"""
\begin{{figure}}[H]
    \centering
    \adjustbox{{max width=\textwidth, max height=0.45\textheight}}{{%
        \includegraphics[keepaspectratio]{{{nom_fig}}}
    }}
    \caption{{{cap_fig}}}
\end{{figure}}
"""
            bloques.append(bloque_s)
    return "\n\n".join(bloques)


def generar_codigo_latex(params=None):
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
        if "tipo_estudio" in st.session_state and "tipo_estudio" not in params:
            params["tipo_estudio"] = st.session_state["tipo_estudio"]
        if "es_autogenerador" in st.session_state and "es_autogenerador" not in params:
            params["es_autogenerador"] = st.session_state["es_autogenerador"]
        sec_activas = st.session_state.get("secciones_activas", {})
        for sec_id in ["sec_1", "sec_2", "sec_3", "sec_4", "sec_5", "sec_6", "sec_7", "sec_8", "sec_9", "sec_10"]:
            k_inc = f"incluir_{sec_id}"
            if k_inc not in params and sec_id in sec_activas:
                params[k_inc] = sec_activas[sec_id]

        subsec_activas = st.session_state.get("subsecciones_activas", {})
        for sub_id in [
            "subsec_1_1", "subsec_1_2", "subsec_1_3",
            "subsec_2_1", "subsec_3_1", "subsec_3_2",
            "subsec_4_1", "subsec_4_2", "subsec_4_3", "subsec_4_4",
            "subsec_5_1", "subsec_5_2", "subsec_6_1",
            "subsec_7_1", "subsec_7_2", "subsec_7_3", "subsec_7_4", "subsec_7_5", "subsec_7_6",
            "subsec_8_1", "subsec_8_2", "subsec_8_3", "subsec_8_4",
            "subsec_9_1", "subsec_10_1"
        ]:
            k_sub = f"incluir_{sub_id}"
            if k_sub not in params and sub_id in subsec_activas:
                params[k_sub] = subsec_activas[sub_id]

        if "secciones_personalizadas" not in params and "secciones_personalizadas" in st.session_state:
            params["secciones_personalizadas"] = st.session_state["secciones_personalizadas"]
    except Exception:
        pass

    # 0. Determinación del régimen: Generación Distribuida (GD) vs Autogenerador
    tipo_estudio_raw = str(buscar_param(params, ["tipo_estudio", "tipoEstudio", "regimen", "tipo_proyecto", "tipoProyecto"], "GD"))
    norma_cno = escapar_latex(buscar_param(params, ["normaCNO", "norma_cno"], "2233"))
    es_autogenerador = ("autogenerador" in tipo_estudio_raw.lower() or bool(params.get("es_autogenerador", False)))

    sigla_proyecto = "Autogenerador" if es_autogenerador else "GD"
    nombre_regimen = "autogeneración" if es_autogenerador else "generación distribuida"
    nombre_regimen_cap = "Autogeneración" if es_autogenerador else "Generación Distribuida"
    titulo_portada_regimen = "AUTOGENERACIÓN" if es_autogenerador else "GENERACIÓN DISTRIBUIDA"
    plural_generadores = "Autogeneradores" if es_autogenerador else "Generadores Distribuidos (GD)"
    regimen_normativo = "Autogeneradores" if es_autogenerador else "Generadores Distribuidos"

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

    palabras_num = ["uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"]

    # Inversores configurados en Variables / Sección 2-3
    inv_items = params.get("inv_items", None)
    if not inv_items or not isinstance(inv_items, list):
        inv_items = [
            {"ref": params.get("refInversoruno", "Inversor 150 kW On-Grid."),
             "modelo": params.get("Inversoruno", "Growat MAX 150KTL3-X2MV"),
             "cantidad": params.get("cantidadInversoruno", "6 Und.")}
        ]
        for idx_chk in range(1, len(palabras_num)):
            pal_chk = palabras_num[idx_chk]
            k_ref = f"refInversor{pal_chk}"
            k_mod = f"Inversor{pal_chk}"
            k_cant = f"cantidadInversor{pal_chk}"
            if k_ref in params or k_mod in params or f"refInversor{idx_chk+1}" in params:
                inv_items.append({
                    "ref": params.get(k_ref, params.get(f"refInversor{idx_chk+1}", f"Inversor {idx_chk+1}")),
                    "modelo": params.get(k_mod, params.get(f"Inversor{idx_chk+1}", f"Modelo {idx_chk+1}")),
                    "cantidad": params.get(k_cant, params.get(f"cantidadInversor{idx_chk+1}", "1 Und."))
                })

    ref_inv_1 = escapar_latex(inv_items[0].get("ref", "Inversor 150 kW On-Grid."))
    mod_inv_1 = escapar_latex(inv_items[0].get("modelo", "Growat MAX 150KTL3-X2MV"))
    cant_inv_1 = escapar_latex(inv_items[0].get("cantidad", "6 Und."))

    items_ref_inv = "\n".join([f"\\item {escapar_latex(x.get('ref', ''))}" for x in inv_items])
    items_mod_inv = "\n".join([f"\\item {escapar_latex(x.get('modelo', ''))}" for x in inv_items])
    items_cant_inv = "\n".join([f"\\item {escapar_latex(x.get('cantidad', ''))}" for x in inv_items])
    filas_inversores_tabla = "\n".join([
        f"        {escapar_latex(x.get('modelo', ''))} & {escapar_latex(x.get('ref', ''))} & {escapar_latex(x.get('cantidad', ''))} \\\\ \\hline"
        for x in inv_items
    ])

    bloques_fig_inv = []
    for idx, inv in enumerate(inv_items):
        modelo_raw = str(inv.get("modelo", "")).strip()
        modelo_esc = escapar_latex(modelo_raw)
        pal_fig = palabras_num[idx] if idx < len(palabras_num) else f"_{idx+1}"
        lbl = f"fig:fichainversor{pal_fig}"
        img_cmd = incluir_imagen_segura(f"Ficha {modelo_raw}.png", "max height=0.68\\textheight, max width=\\textwidth, keepaspectratio")
        bloques_fig_inv.append(f"""
\\begin{{figure}}[H]
    \\centering
    {img_cmd}
    \\caption{{Hoja técnica {modelo_esc}}}
    \\label{{{lbl}}}
\\end{{figure}}
""")
    codigo_fig_inversores = "\n".join(bloques_fig_inv)

    comandos_inversores_def = []
    for idx_i, inv in enumerate(inv_items):
        pal = palabras_num[idx_i] if idx_i < len(palabras_num) else f"_{idx_i+1}"
        r_esc = escapar_latex(inv.get("ref", ""))
        m_esc = escapar_latex(inv.get("modelo", ""))
        c_esc = escapar_latex(inv.get("cantidad", ""))
        comandos_inversores_def.append(f"\\providecommand{{\\refInversor{pal}}}{{{r_esc}}}")
        comandos_inversores_def.append(f"\\providecommand{{\\Inversor{pal}}}{{{m_esc}}}")
        comandos_inversores_def.append(f"\\providecommand{{\\cantidadInversor{pal}}}{{{c_esc}}}")
        if idx_i > 0:
            comandos_inversores_def.append(f"\\providecommand{{\\refInversor{idx_i+1}}}{{{r_esc}}}")
            comandos_inversores_def.append(f"\\providecommand{{\\Inversor{idx_i+1}}}{{{m_esc}}}")
            comandos_inversores_def.append(f"\\providecommand{{\\cantidadInversor{idx_i+1}}}{{{c_esc}}}")
    txt_comandos_inversores = "\n".join(comandos_inversores_def)

    if len(inv_items) <= 1:
        fila_inversores_specs = r"        Inversores & \refInversoruno\ \\ \hline"
    else:
        lineas_inv_specs = []
        for idx_i, inv in enumerate(inv_items):
            pal = palabras_num[idx_i] if idx_i < len(palabras_num) else f"_{idx_i+1}"
            lineas_inv_specs.append(rf"\refInversor{pal}\ (\cantidadInversor{pal})")
        str_makecell = r" \\ ".join(lineas_inv_specs)
        fila_inversores_specs = rf"        Inversores & \makecell[l]{{{str_makecell}}} \\ \hline"

    # 2. Textos de Resumen Ejecutivo (Sección 1.2 y 1.3)
    resumen_intro = params.get(
        "resumen_intro",
        "Para el presente documento se han realizado los siguientes estudios técnicos con el propósito de evaluar la viabilidad del proyecto:"
    )
    resumen_flujo = adaptar_texto_regimen(params.get("resumen_flujo", ""), es_autogenerador)
    resumen_cortocircuito = adaptar_texto_regimen(params.get("resumen_cortocircuito", ""), es_autogenerador)
    resumen_protecciones = params.get("resumen_protecciones", "")
    resumen_cierre = params.get(
        "resumen_cierre",
        "Finalmente, estos estudios proporcionan una sólida base técnica para afirmar la viabilidad del proyecto, asegurando su integración segura y eficiente en la red eléctrica existente."
    )

    default_texto_supuestos = (
        r"En la información suministrada por el OR no se definió el escenario de análisis (t+x), "
        r"por lo tanto se tomó un valor de 5 años, que es un dato utilizado por otros OR para este tipo de análisis, "
        r"de esta forma se tiene que el horizonte de análisis del proyecto es \YearInicial\ y (t+5) \YearFinal, "
        r"los valores de tasa de crecimiento para escalar la demanda equivalente de la subestación se tomaron de los "
        r"datos suministrados por la UPME, en la \cref{tab:UPME}\\"
    )
    texto_supuesto_activo = params.get("texto_supuesto_activo", default_texto_supuestos)
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
    default_sec2_intro = (
        rf"El proyecto \nombreProyecto\ de {nombre_regimen_cap} \capacidadMW, se conectará al SIN a través del circuito \CTO\ de la S/E \SSEE\ al nivel de tensión \NT, propiedad del operador de red \OR, La ubicación del proyecto es \ubicacion. En la \cref{{tab:coordenadas}} se detallan las coordenadas geográficas para la ubicación del proyecto {sigla_proyecto} \nombreProyecto. El proyecto cuenta con una fecha en puesta de operación (en adelante FPO) para \FechaEntrada. En la \cref{{tab:descripcion_proyecto}} se resumen las especificaciones técnicas de los equipos que conforman el proyecto."
    )
    sec2_intro = adaptar_texto_regimen(params.get("sec2_intro", default_sec2_intro), es_autogenerador)
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
        img_geo = incluir_imagen_segura("Diagrama Geoespacial.png", "max width=14cm, max height=0.45\\textheight, keepaspectratio")
        bloque_geoespacial = rf"""
En la \cref{{fig:georeferencia}}, se presenta el diagrama eléctrico geoespacial del circuito \CTO\\ en el cual se conecta el proyecto.\\
\begin{{figure}}[H]
    \centering
    {img_geo}
    \caption{{Diagrama eléctrico geoespacial CTO \CTO}}
    \label{{fig:georeferencia}}
\end{{figure}}
"""
    img_ubicacion = incluir_imagen_segura("Ubicacion Geográfica.png", "max width=15cm, max height=0.45\\textheight, keepaspectratio")

    sec3_intro = params.get(
        "sec3_intro",
        r"En la \cref{fig:fichapanel}, se puede apreciar las características técnicas de los paneles fotovoltaicos seleccionados para el proyecto."
    )
    if "texto_equipos" in params and params["texto_equipos"] and str(params["texto_equipos"]).strip():
        texto_equipos = params["texto_equipos"]
    else:
        if len(inv_items) <= 1:
            texto_equipos = r"Sumado a \cantidadInversoruno\ inversores de 150 kW, 4 de ellos con 300 paneles cada uno y los otros dos con 280 cada uno, su tensión de salida es de 800 V – 60 Hz respectivamente. En la \cref{fig:fichainversoruno}, se aprecia las características operativas de los inversores instalados en el sistema de generación."
        else:
            menciones_inv = []
            menciones_figs = []
            for idx_i in range(len(inv_items)):
                pal = palabras_num[idx_i] if idx_i < len(palabras_num) else f"_{idx_i+1}"
                menciones_inv.append(rf"\cantidadInversor{pal}\ inversores modelo \Inversor{pal}\ (\refInversor{pal})")
                menciones_figs.append(rf"\cref{{fig:fichainversor{pal}}}")
            str_invs = " y ".join(menciones_inv)
            str_figs = ", ".join(menciones_figs)
            texto_equipos = rf"Sumado a {str_invs}, con su tensión y frecuencia de operación nominal para integración al sistema. En las {str_figs}, se aprecian las características operativas de los inversores instalados en el sistema de generación."
    img_ficha_panel = incluir_imagen_segura("Ficha panel.png", "max width=\\textwidth, max height=0.65\\textheight, keepaspectratio")
    default_sec3_or_texto = (
        rf"El proyecto {sigla_proyecto} \nombreProyecto\ se conectará al circuito \CTO, por tanto, el OR suministro a través de los insumos datos de red de todo el circuito y ajuste de coordinación de protecciones."
    )
    sec3_or_texto = adaptar_texto_regimen(params.get("sec3_or_texto", default_sec3_or_texto), es_autogenerador)
    usar_equivalente_png = params.get("usar_equivalente_png", True)
    if usar_equivalente_png:
        img_eq_red = incluir_imagen_segura("equivalentered.png", "height=0.28\\textheight, width=\\textwidth, keepaspectratio")
        bloque_eq_red = rf"""
\begin{{table}}[H]
    \centering
    \caption{{Parámetros Equivalente de RED}}
    \label{{tab:equivalentered}}
    {img_eq_red}
\end{{table}}
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
        f"Demandas consideradas en el circuito {year_inicial} - Calculada con la información entregada por el OR y la proyección de la UPME en la Tabla~\\ref{{tab:UPME}}",
        f"tab:cargascto{year_inicial}",
        f"cargascto{year_inicial}.csv"
    )
    csv_cargas_fin = incluir_csv_seguro(
        "col sep=semicolon, skip rows between index={500}{5000}",
        f"Demandas consideradas en el circuito {year_final} - Calculada con la información entregada por el OR y la proyección de la UPME en la Tabla~\\ref{{tab:UPME}}",
        f"tab:cargascto{year_final}",
        f"cargascto{year_final}.csv"
    )

    bloque_informacion_or = rf"\cref{{tab:equivalentered,tab:cargascto{year_inicial},tab:cargascto{year_final}}}"

    # 5. Datos Secciones 4, 5 y 6
    sec4_1_texto = params.get("sec4_1_texto", r"En la \cref{fig:Unifilar} se presenta el diagrama unifilar del circuito \CTO\ suministrado por el OR.")
    img_unifilar = incluir_imagen_segura("UnifilarCTO.png", "max width=15cm, max height=0.50\\textheight, keepaspectratio")
    sec4_2_texto = params.get(
        "sec4_2_texto",
        r"En el numeral 7.1 de la circular CREG 021 de 2022, se establece el horizonte de análisis, en la \cref{tab:horizonte} se presentan los años a analizar según la información suministrada."
    )
    bloque_tabla_horizonte = r"""
\begin{table}[H]
    \centering
    \caption{Horizonte de análisis.}
    \label{tab:horizonte}
    \footnotesize
    \setlength{\tabcolsep}{20pt}
    \begin{tabular}{|c|c|}
        \hline
        \rowcolor{azulSeyep}
        \multicolumn{2}{|c|}{\textbf{\textcolor{white}{Horizonte}}} \\ \hline
        \YearInicial & \YearFinal \\ \hline
    \end{tabular}
    \setlength{\tabcolsep}{3pt}
\end{table}
\vspace{-10pt}
"""
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
        f"Consumo de energía en el punto de instalación del {sigla_proyecto} y generación de energía proyectada.",
        "tab:consumoVSgeneracion",
        "consumoVSgeneracion.csv"
    )
    sec4_4_curva = params.get(
        "sec4_4_curva",
        r"Por parte de EPM se suminstró el perfil de demanda del circuito 211-11 de la subestación Doradal 13.2kV, segun la \cref{fig:curvadecarga211}, es importante destacar que de esta curva que correcponde a un día típioco mínimo se estrajeron las horas de 9:00 am, 12:00 pm y 3:00 pm ya que son los horarios de generación máxima y donde el proyecto fotovoltaico va a presnetar un mayor impacto."
    )
    caption_curva_cto = escapar_latex(params.get("caption_curva_cto", "Demanda de circuito 211-11 suministrado por el operador de red"))
    img_curva_cto = incluir_imagen_segura("curva de carga cto211.png", "max width=\\textwidth, max height=0.45\\textheight, keepaspectratio")
    sec4_4_comp = params.get("sec4_4_comp", r"En la \cref{fig:consumoygeneracion}, se compara el consumo y la genreación por hora del circuito 211-11.")
    img_consumo_gen = incluir_imagen_segura("consumoygeneracion.png", "max width=\\textwidth, max height=0.45\\textheight, keepaspectratio")

    sec5_intro = params.get(
        "sec5_intro",
        r"Para el desarrollo del presente informe se emplea la información suministrada por \OR, esta base de datos contiene el sistema de distribución local desde el nodo de conexión de la S/E \SSEE, en un circuito radial de \NT. Los análisis se realizan para el circuito \CTO."
    )
    default_sec5_1 = (
        r"Para garantizar una conexión y operación que cumpla los criterios técnicos de calidad, seguridad y confiabilidad, en el diseño, ejecución y mantenimiento del proyecto se realiza este estudio bajo las siguientes normativas colombianas. \begin{itemize} \item Reglamento técnico de instalaciones eléctricas (RETIE).\item Circular CREG 021 de 2022.\item Circular CREG 174 de 2021.\item Circular CREG 015 de 2018.\item Circular CREG 025 de 1995.\\\end{itemize}Teniendo en cuenta las anteriores normativas se establece algunos de los criterios y límites para tener en cuenta dentro de este documento.\\\begin{itemize} \item CREG 025 de 1995, “El STN se planeará de tal forma que permita, en conjunto con la generación, los sistemas de transmisión regionales y los sistemas de distribución local, Asegurar que la tensión en las barras de carga a nivel de 220 kV y superiores no sea inferior al 90\% del valor nominal, ni superior al 110\%”.\item Circular CREG 174 de 2021, en caso de implementar inversores en los proyectos, la capacidad del proyecto corresponde a la sumatoria de las capacidades nominales de los inversores, en el lado con conexión al SIN, la capacidad se deberá asumir con un factor de potencia unitario. \item Circular CREG 025 de 1995, Para las líneas de transmisión se consideran flujos aceptables, en condiciones normales de operación, cuando sean iguales o menores del 100\% de su capacidad nominal. En contingencia se admiten sobrecargas hasta el valor máximo permitido para el elemento bajo condiciones de emergencia y que se encuentra declarado por el agente propietario en el PARATEC. \item Para transformadores se consideran flujos aceptables en condiciones normales de operación, cuando sean iguales o menores del 100\% de su capacidad nominal. En contingencia se admiten sobrecargas hasta el valor máximo permitido para el elemento bajo condiciones de emergencia y que se encuentra declarado por el agente propietario en el PARATEC.\item Artículo 5 de la resolución CREG 030 de 2018, Literal a, Literal c, “La Cantidad de energía en una hora se pueden entregar los GD o AGEP que entregan energía a la red, cuyo sistema de producción de energía sea el compuesto por fotovoltaico sin capacidad de almacenamiento, conectados al mismo circuito o transformador del nivel de tensión 1, no debe superar el 50\% de promedio anual de las horas de mínima demandad diaria de energía registradas para el año anterior al de solicitud de conexión en la franja horaria comprometida entre 6 am y 6 pm.”\end{itemize}"
    )
    sec5_1_texto = params.get("sec5_1_texto", default_sec5_1)

    default_sec5_2 = (
        r"En el presente estudio de conexión se realizan los siguientes análisis técnicos del proyecto solar fotovoltaico de generación y consumo:\\"
        r"A continuación, se instalan los estudios realizados: \begin{itemize}"
        r"    \item \textbf{Generación de energía eléctrica:} proyección de la máxima generación del proyecto solar a la red de distribución de energía eléctrica propiedad OR."
        r"    \item \textbf{Consumo de la instalación eléctrica:} Estimado de la energía requerida por el cliente OR."
        r"    \item \textbf{Estudio de flujo de carga:} Monitorear los niveles de tensión en las barras; así como la cargabilidad en transformadores y líneas de transmisión para que no sobrepasen los límites permitidos."
        r"    \item \textbf{Estudio de pérdidas:} Analizar las pérdidas del sistema de distribución locas (SDL) con la inclusión del proyecto de generación."
        r"    \item \textbf{Estudio de cortocircuito:} Monitorear los aportes de corriente de cortocircuito en las subestaciones, así como monitorear que estas no se sobrepasen los niveles máximos de corto en las subestaciones del sistema."
        r"    \item \textbf{Estudio de protecciones:} Analizar el comportamiento de las protecciones del OR en conjunto con las del proyecto de generación para diferentes eventos en el SDL, buscando garantizar selectividad y confiabilidad."
        r"\end{itemize}"
    )
    sec5_2_texto = params.get("sec5_2_texto", default_sec5_2)

    sec6_despacho = params.get(
        "sec6_despacho",
        r"Para la demanda se consideró la información suminstrada por EPM y de acuerdo con el OR y el Consejo Nacional de Operación (CNO) con los lineamientos para estudios de conexión simplificado en el marco de la resolución CREG 174 de 2021, el estudio se realizó bajo los siguientes escenarios:"
    )
    sec6_gen_max = params.get(
        "sec6_gen_max",
        r"Para proyectos de generación fotovoltaico se presenta la generación máxima del proyecto a las 9:00 am, 12:00 pm y 3:00 pm, ya que la generación no es controlable y el único cambio presentado es la demanda, adicionalmente se considera el caso de demanda mínima (suministrada por el operador de red) para considerar las peores condiciones posibles donde la energía demandada por el circuito es la menor por lo que la disponibilidad de capacidad de transmisión es menor."
    )
    default_sec6_contenido = rf"""Para clasificar cada uno de los resultados entregados en este estudio, se seleccionaron tres variables que describen cada uno de los escenarios de análisis. Estas variables son: \begin{{itemize}}
    \item Año
	\begin{{itemize}}
      \item \textbf{{\YearInicial}}
		\item \textbf{{\YearFinal}}
	\end{{itemize}}
  \item Despacho de demanda
	 \begin{{itemize}}
    \item {sec6_despacho}
          \begin{{itemize}}
            \item \textbf{{Generación máxima de la planta solar y demanda coincidente suministrada:}}{sec6_gen_max}
           \end{{itemize}}
   \end{{itemize}}
\end{{itemize}}"""
    sec6_contenido = params.get("sec6_contenido", default_sec6_contenido)

    # 6. Datos Sección 7 (Resultados Eléctricos)
    img_conv_flujos = incluir_imagen_segura("convencionesflujos.png", "max width=0.6\\linewidth, max height=0.30\\textheight, keepaspectratio")
    img_cod_colores = incluir_imagen_segura("codigocoloresflujo.png", "max width=4cm, max height=0.25\\textheight, keepaspectratio")
    img_cargabilidad = incluir_imagen_segura("Cargabilidad.png", "max width=\\textwidth, max height=0.42\\textheight, keepaspectratio")
    img_tensiones_pu = incluir_imagen_segura("TensionesPU.png", "max width=\\textwidth, max height=0.38\\textheight, keepaspectratio")
    img_perfil_cto = incluir_imagen_segura("perfiltensionCTO.png", "max width=\\textwidth, max height=0.45\\textheight, keepaspectratio")

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
        r"Como se evidencia en la \cref{fig:cargabilidadConti} el sistema incrementa su capacidad y no presenta ninguna sobrecarga por encima del 100\% en sus líneas ni en sus transformadores."
    )
    img_cont_cargmax = incluir_imagen_segura("Cont_Cargmax.png", "width=0.6\\linewidth")
    img_pumax = incluir_imagen_segura("pumax.png", "width=0.6\\linewidth")
    img_carg_conti = incluir_imagen_segura("cargabilidadConti.png", "height=0.45\\textheight, keepaspectratio")
    if resolver_ruta_imagen("cargabilidadConti.png") is None and resolver_ruta_imagen("Diagrama_Contingencia.png") is not None:
        img_carg_conti = incluir_imagen_segura("Diagrama_Contingencia.png", "height=0.45\\textheight, keepaspectratio")
    img_perfil_conti = incluir_imagen_segura("perfilConti.png", "height=0.45\\textheight, keepaspectratio")

    if incluir_contingencia:
        bloque_contingencia = rf"""
\subsection{{\textit{{Análisis de contingencia}}}}
{contingencia_p1}\\[0.3cm]
En la \cref{{tab:cargabilidadMax,tab:PUMax_conting}} se presenta los valores maximos alcanzados en el analisis de cargabilidad y perfiles de tensión.
\begin{{table}}[h!]
    \centering
    \caption{{Cargabilidad Maxima En Contingencia \YearInicial\ para el \CTO}}
    \label{{tab:cargabilidadMax}}
    {img_cont_cargmax}
\end{{table}}
\begin{{table}}[h!]
    \centering
    \caption{{Perfil De Tension Maxima En Contingencia \YearInicial\ para el \CTO}}
    \label{{tab:PUMax_conting}}
    {img_pumax}
\end{{table}}
\newpage
{contingencia_p2}
\begin{{figure}}[h]
    \centering
    {img_carg_conti}
    \caption{{Cargabilidad en contingencia para el circuito \CTO }}
    \label{{fig:cargabilidadConti}}
\end{{figure}}
\begin{{figure}}[h]
    \centering
    {img_perfil_conti}
    \caption{{Perfil de tensión en contingencia para el circuito \CTO }}
    \label{{fig:perfilConti}}
\end{{figure}}
"""
    else:
        bloque_contingencia = ""

    img_perdidas = incluir_imagen_segura("perdidas.png", "max width=\\textwidth, max height=0.30\\textheight, keepaspectratio")
    default_sec7_perdidas = (
        rf"El análisis técnico de los escenarios proyectados para \YearInicial\ y \YearFinal\, se evidencia que el incremento más significativo se presenta en el escenario de Hora 12, alcanzando deltas de 25,97 kW (\YearInicial) y 25,90 kW (\YearFinal); este comportamiento responde a la condición técnica donde los {plural_generadores} inyectan su máxima capacidad de energía mientras la demanda del circuito es mínima, lo que ocasiona flujos inversos de potencia a través de la red de distribución. Por el contrario, en los escenarios con coincidencia entre la generación y la carga, las pérdidas se mantienen en niveles bajos e impactan de manera marginal al sistema destacando variaciones de apenas approx 11 kW en el escenario de Hora 9, lo que demuestra que la absorción local de la energía producida evita el transporte prolongado de corriente y confirma que la integración de los proyectos no genera un impacto negativo ni degradante sobre la operación habitual del SDL."
    )
    sec7_perdidas_texto = adaptar_texto_regimen(
        params.get("sec7_perdidas_texto", default_sec7_perdidas),
        es_autogenerador
    )
    img_leyendas_cortos = incluir_imagen_segura("Leyendascortos.png", "max width=\\linewidth, max height=0.35\\textheight, keepaspectratio")
    img_cortos = incluir_imagen_segura("cortos.png", "max width=\\linewidth, max height=0.45\\textheight, keepaspectratio")
    sec7_isla_conclusion = params.get(
        "sec7_isla_conclusion",
        r"La Ecuación \eqref{eq:balance_potencia} arroja un resultado donde la potencia instalada acumulada más la capacidad del proyecto supera la demanda mínima del circuito, confirmando la existencia de riesgo de funcionamiento en isla no intencional ante contingencias o aperturas del elemento de maniobra del Operador de Red. Para mitigar este riesgo y garantizar la seguridad de la red y del personal, la planta implementará un esquema de protección anti-isla activo y coordinado conforme a las disposiciones normativas del Acuerdo CNO \normaCNO{}; los detalles de la filosofía de operación, la parametrización de las funciones intrínsecas del inversor, las funciones de respaldo y la coordinación de tiempos de despeje para evitar la operación en isla se presentan de manera detallada en el Estudio de Ajuste de Protecciones (EACP) entregado adjunto al presente estudio de conexión."
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
                items_conclusiones.append(f"\\item {{{adaptar_texto_regimen(txt_c, es_autogenerador)}}}")
    if not items_conclusiones:
        items_conclusiones = [
            r"\item {Los equipos empleados en el proyecto (Paneles Solares, Protecciones) cumplen con la certificación de conformidad RETIE.}",
            rf"\item {{Las simulaciones de flujo en estado estable con {sigla_proyecto} se evidencian tensiones que se mantienen en los valores establecidos.}}",
            r"\item {Los niveles de perdidasse mantienen con la introducción del proyecto.}",
            rf"\item {{Las simulaciones de cortocircuito no presentan cambios mayores al 10\% con la entrada en operación del {sigla_proyecto} en ningún punto del circuito}}",
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
        bloque_seccion_anexos = rf"""
\clearpage
\section{{ANEXOS}}
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
        "recoCTO", "tipoproteccion", "recocabecera", "normaCNO", "norma_cno", "norma_CNO"
    }
    for k, v in params.items():
        if k not in llaves_reservadas and isinstance(k, str) and k.isalpha() and k.isascii():
            if isinstance(v, (str, int, float)):
                comandos_extra.append(f"\\providecommand{{\\{k}}}{{{escapar_latex(v)}}}")

    bloque_comandos_extra = "\n".join(comandos_extra)

    comandos_variables = rf"""
% ---------- Variables del proyecto ----------
\providecommand{{\mesentregainformemasyear}}{{{mes_entrega}}}
\providecommand{{\nombreProyecto}}{{{nombre_proyecto}}}
\providecommand{{\capacidadMW}}{{{capacidad_mw}}}
\providecommand{{\OR}}{{{operador_red}}}
\providecommand{{\FechaEntrada}}{{{fecha_entrada}}}
\providecommand{{\Latitud}}{{{latitud}}}
\providecommand{{\Longitud}}{{{longitud}}}
\providecommand{{\YearInicial}}{{{year_inicial}}}
\providecommand{{\YearFinal}}{{{year_final}}}
\providecommand{{\CTO}}{{{cto}}}
\providecommand{{\SSEE}}{{{ssee}}}
\providecommand{{\NT}}{{{nt}}}
\providecommand{{\nodo}}{{{nodo}}}
\providecommand{{\elementoProteccion}}{{{elemento_proteccion}}}
\providecommand{{\referenciaPanel}}{{{referencia_panel}}}
\providecommand{{\potenciaPanel}}{{{potencia_panel}}}
\providecommand{{\cantidadPanel}}{{{cantidad_panel}}}
\providecommand{{\ubicacion}}{{{ubicacion}}}
\providecommand{{\CP}}{{{cp_hora}}}
\providecommand{{\Dmi}}{{{dmi_hora}}}
\providecommand{{\DMx}}{{{dmx_hora}}}
\providecommand{{\escenariomaxPerdidas}}{{{escenario_max_perd}}}
\providecommand{{\perdidasmaximas}}{{{perdidas_maximas}}}
{txt_comandos_inversores}
\providecommand{{\generacionaprobada}}{{{generacion_aprobada}}}
\providecommand{{\potenciaminima}}{{{potencia_minima}}}
\providecommand{{\recoCTO}}{{{reco_cto}}}
\providecommand{{\tipoproteccion}}{{{tipo_proteccion}}}
\providecommand{{\normaCNO}}{{{norma_cno}}}
\providecommand{{\recocabecera}}{{{reco_cabecera}}}
{bloque_comandos_extra}

\newcommand{{\controlcambios}}{{%
{bloque_tabla_cambios}
}}

\newcommand{{\supuestos}}{{%
{texto_supuesto_activo}
\newpage
{bloque_tabla_supuestos}
}}

\newcommand{{\resumen}}{{%
\begin{{itemize}}
\item \textbf{{Flujo de carga:}} {resumen_flujo}
\item \textbf{{Cortocircuito:}} {resumen_cortocircuito}
\item \textbf{{Coordinación de protecciones:}} {resumen_protecciones}
\end{{itemize}}
}}

\newcommand{{\refInversores}}{{\begin{{itemize}}
{items_ref_inv}
\end{{itemize}}}}

\newcommand{{\Inversores}}{{\begin{{itemize}}
{items_mod_inv}
\end{{itemize}}}}

\newcommand{{\cantidadInversores}}{{\begin{{itemize}}
{items_cant_inv}
\end{{itemize}}}}

\newcommand{{\CONCLUSIONFERFILESCARGA}}{{%
{conclusion_perfiles_carga}
}}

\newcommand{{\equipos}}{{%
{texto_equipos}
}}

\newcommand{{\figinversores}}{{%
{codigo_fig_inversores}
}}

\newcommand{{\informacionOR}}{{%
{bloque_informacion_or}
}}

\newcommand{{\CONTINGENCIA}}{{%
{bloque_contingencia}
}}

\newcommand{{\sistemaAC}}{{%
Para el cálculo de la protección general de los inversores, se tuvieron en cuenta los siguientes parámetros:
\begin{{center}}
    \begin{{minipage}}{{0.9\textwidth}}
        \centering
        \captionof{{table}}{{Sistema AC}}
        \label{{tab:sistema_AC}}
        \begingroup
        \setlength{{\tabcolsep}}{{10pt}}
        \renewcommand{{\arraystretch}}{{1.3}}
        \adjustbox{{max width=\textwidth}}{{%
        \begin{{tabular}}{{|l|c|}}
            \hline
            \rowcolor{{azulSeyep}}
            \multicolumn{{2}}{{|c|}}{{\color{{white}}\textbf{{Sistema AC}}}} \\ \hline
            \multicolumn{{2}}{{|c|}}{{Protección arreglo de inversores AC}} \\ \hline
            Sistema AC & {ac_fases} \\ \hline
            Potencia & \capacidadMW \\ \hline
            Tensión de Línea [kV] & {ac_tension_kv} \\ \hline
            Intensidad máxima [A] & {ac_corriente_max} \\ \hline
            Factor de carga continua & {ac_factor_carga} \\ \hline
            Protección en tablero principal ($\text{{I}}_{{\text{{max}}}} \times {ac_factor_carga}$) [A] & {ac_proteccion_tablero} \\ \hline
        \end{{tabular}}%
        }}
        \endgroup
        \vspace{{2mm}}\\
        {{\centering\footnotesize
        \textbf{{\textit{{{ac_nota_pie}}}}}\par
        }}
    \end{{minipage}}
\end{{center}}
}}

\newcommand{{\CONCLUSIONES}}{{%
\begin{{itemize}}
{bloque_items_conclusiones}
\end{{itemize}}
}}

\newcommand{{\Flujosdecarga}}{{%
{codigo_flujos_carga}
}}
"""

    
    # --- Lectura de Secciones y Subsecciones Activas u Opcionales ---
    incluir_sec_1 = bool(params.get("incluir_sec_1", True))
    incluir_sec_2 = bool(params.get("incluir_sec_2", True))
    incluir_sec_3 = bool(params.get("incluir_sec_3", True))
    incluir_sec_4 = bool(params.get("incluir_sec_4", True))
    incluir_sec_5 = bool(params.get("incluir_sec_5", True))
    incluir_sec_6 = bool(params.get("incluir_sec_6", True))
    incluir_sec_7 = bool(params.get("incluir_sec_7", True))
    incluir_sec_8 = bool(params.get("incluir_sec_8", True))
    incluir_sec_9 = bool(params.get("incluir_sec_9", True))
    incluir_sec_10 = bool(params.get("incluir_sec_10", True))

    incluir_subsec_1_1 = bool(params.get("incluir_subsec_1_1", True))
    incluir_subsec_1_2 = bool(params.get("incluir_subsec_1_2", True))
    incluir_subsec_1_3 = bool(params.get("incluir_subsec_1_3", True))

    incluir_subsec_2_1 = bool(params.get("incluir_subsec_2_1", True))

    incluir_subsec_3_1 = bool(params.get("incluir_subsec_3_1", True))
    incluir_subsec_3_2 = bool(params.get("incluir_subsec_3_2", True))

    incluir_subsec_4_1 = bool(params.get("incluir_subsec_4_1", True))
    incluir_subsec_4_2 = bool(params.get("incluir_subsec_4_2", True))
    incluir_subsec_4_3 = bool(params.get("incluir_subsec_4_3", True))
    incluir_subsec_4_4 = bool(params.get("incluir_subsec_4_4", True))

    incluir_subsec_5_1 = bool(params.get("incluir_subsec_5_1", True))
    incluir_subsec_5_2 = bool(params.get("incluir_subsec_5_2", True))

    incluir_subsec_6_1 = bool(params.get("incluir_subsec_6_1", True))

    incluir_subsec_7_1 = bool(params.get("incluir_subsec_7_1", True))
    incluir_subsec_7_2 = bool(params.get("incluir_subsec_7_2", True))
    incluir_subsec_7_3 = bool(params.get("incluir_subsec_7_3", True))
    incluir_subsec_7_4 = bool(params.get("incluir_subsec_7_4", True))
    incluir_subsec_7_5 = bool(params.get("incluir_subsec_7_5", True))
    incluir_subsec_7_6 = bool(params.get("incluir_subsec_7_6", True))

    incluir_subsec_8_1 = bool(params.get("incluir_subsec_8_1", True))
    incluir_subsec_8_2 = bool(params.get("incluir_subsec_8_2", True))
    incluir_subsec_8_3 = bool(params.get("incluir_subsec_8_3", True))
    incluir_subsec_8_4 = bool(params.get("incluir_subsec_8_4", True))
    incluir_subsec_9_1 = bool(params.get("incluir_subsec_9_1", True))
    incluir_subsec_10_1 = bool(params.get("incluir_subsec_10_1", True))

    bloque_intro = rf"""\begin{{document}}

% --- PORTADA ---
\begin{{titlepage}}
    \thispagestyle{{fancy}}
    \centering
    \vspace*{{4cm}}
    {{\fontsize{{20}}{{30}}\selectfont \textbf{{ESTUDIO DE CONEXIÓN SIMPLIFICADO {titulo_portada_regimen} SOLAR FV}}}} \\[0.1cm]

    {{\fontsize{{22}}{{30}}\selectfont \textbf{{\nombreProyecto{{}} - \capacidadMW}}}} \\[3cm]
    {bloque_logo}

    \vfill
    {{\Large \textbf{{Versión: 0}}}} \\[0.8cm]
    {{\Large Medellín, Colombia.}} \\
    {{\Large \mesentregainformemasyear}}\\[0.5cm]
\end{{titlepage}}
\newpage

% --- CONTROL DE CAMBIOS ---
\begin{{center}}
\section*{{CONTROL DE CAMBIOS.}}

    \definecolor{{azulSeyep}}{{RGB}}{{0, 103, 254}}
    \renewcommand{{\arraystretch}}{{1.5}}
    \controlcambios

\end{{center}}
\newpage %

% --- CONFIGURACIÓN DE LA TABLA DE CONTENIDO ---
\renewcommand{{\contentsname}}{{TABLA DE CONTENIDO}}
\tableofcontents
\newpage

\newpage
% --- CONFIGURACIÓN DEL ÍNDICE DE TABLAS ---
\renewcommand{{\listtablename}}{{ÍNDICE DE TABLAS}}
\begin{{center}}
    \listoftables
\end{{center}}

\newpage
% --- CONFIGURACIÓN DEL ÍNDICE DE FIGURAS ---
\renewcommand{{\listfigurename}}{{ÍNDICE DE FIGURAS}}
\begin{{center}}
    \listoffigures
\end{{center}}
\newpage
"""

    # --- SECCIÓN 1: RESUMEN EJECUTIVO Y SUBSECCIONES ---
    subsec_1_1_tex = rf"""\subsection{{\textit{{Objetivo y alcance}}}}
El presente documento tiene como objetivo principal analizar la viabilidad técnica del desarrollo del proyecto {nombre_regimen} {f"({sigla_proyecto}) " if not es_autogenerador else ""}solar fotovoltaico \nombreProyecto\ en la red eléctrica de distribución de \OR\ en adelante OR (Operador de Red). El siguiente estudio se enfoca en proporcionar un análisis detallado de la conexión simplificada del sistema de {nombre_regimen} a la red eléctrica existente. En tal estudio se resalta los parámetros eléctricos claves que garantizan la operación segura y eficiente del proyecto solar fotovoltaico {sigla_proyecto} \nombreProyecto\ con una potencia nominal de \capacidadMW\ , Este documento hace parte de lo establecido en el anexo 2 de la circular CREG 021 de 2022 y en el Capítulo 3 de la Resolución CREG 174 de 2021, la cual define el procedimiento de conexión para {regimen_normativo}, y considerando los lineamientos de reporte de información de la Circular CREG 021 de 2022.\\
""" if incluir_subsec_1_1 else ""

    subsec_1_2_tex = rf"""\subsection{{\textit{{Supuestos y herramienta de modelación}}}}
La información requerida para el modelamiento del área de influencia fue suministrada por el cliente y el OR comprendiendo el diagrama unifilar con sus respectivos nodos asociados al proyecto y sus respectivas cargas con el comportamiento en potencia activa y reactiva. El modelamiento de dicho diagrama unifilar se realizó en el software Digsilent Power Factory.\\[0.3cm]
\supuestos
""" if incluir_subsec_1_2 else ""

    subsec_1_3_tex = rf"""\subsection{{\textit{{Resumen de los principales resultados}}}}
{resumen_intro}\\
\resumen
{resumen_cierre}
""" if incluir_subsec_1_3 else ""

    bloque_s1 = rf"""% =====================================================================
% SECCIÓN 1: RESUMEN EJECUTIVO
% =====================================================================
\section{{RESUMEN EJECUTIVO}}
{subsec_1_1_tex}
{subsec_1_2_tex}
{subsec_1_3_tex}
""" if (incluir_sec_1 and (incluir_subsec_1_1 or incluir_subsec_1_2 or incluir_subsec_1_3)) else ""
    bloque_s1 += generar_latex_secciones_personalizadas("sec_1", params, es_autogenerador)

    # --- SECCIÓN 2: DESCRIPCIÓN GENERAL DEL PROYECTO Y SUBSECCIONES ---
    subsec_2_1_tex = rf"""\subsection{{\textit{{información del proyecto}}}}
{sec2_intro} \\
%\newpage

\begin{{table}}[h!]
    \centering
    \caption{{Coordenadas geográficas del Proyecto.}}
    \label{{tab:coordenadas}}
    \renewcommand{{\arraystretch}}{{1.8}}
    \begin{{tabular}}{{|c|c|c|}}
        \hline
        \rowcolor{{azulSeyep}}
        \textbf{{\textcolor{{white}}{{Nombre}}}} &
        \textbf{{\textcolor{{white}}{{Latitud}}}} &
        \textbf{{\textcolor{{white}}{{Longitud}}}} \\ \hline
        \nombreProyecto\ & \Latitud\ & \Longitud\ \\ \hline
    \end{{tabular}}
\end{{table}}
\bigskip

\begin{{table}}[h!]
    \centering
    \caption{{Descripción general del proyecto.}}
    \label{{tab:descripcion_proyecto}}
    \resizebox{{\textwidth}}{{!}}{{%
        \renewcommand{{\arraystretch}}{{1.5}}
        \begin{{tabular}}{{|c|c|c|c|}}
            \hline
            \rowcolor{{azulSeyep}}
            \textbf{{\textcolor{{white}}{{ÍTEM}}}} & \multicolumn{{3}}{{c|}}{{\textbf{{\textcolor{{white}}{{DESCRIPCIÓN}}}}}} \\ \hline
            Proyecto. & \multicolumn{{3}}{{c|}}{{{sigla_proyecto} \nombreProyecto}} \\ \hline
            Vida Útil & \multicolumn{{3}}{{c|}}{{{vida_util}}} \\ \hline
            Nodo y/o circuito de Conexión & \multicolumn{{3}}{{c|}}{{\nodo\ / \CTO{{}}}} \\ \hline
            Potencia. & \multicolumn{{3}}{{c|}}{{\capacidadMW}} \\ \hline
            Tipo Fuente de Energía & \multicolumn{{3}}{{c|}}{{{tipo_fuente}}} \\ \hline
            \multirow{{3}}{{*}}{{Equipos.}}
                & {tipo_panel_etiqueta} \potenciaPanel{{}} & \referenciaPanel{{}} & \cantidadPanel{{}} \\ \cline{{2-4}}
                & \begin{{minipage}}[t]{{6.5cm}}
                    \refInversores
                    \vspace{{1pt}}
                  \end{{minipage}}
                & \begin{{minipage}}[t]{{6.5cm}}
                    \Inversores
                    \vspace{{1pt}}
                  \end{{minipage}}
                & \begin{{minipage}}[t]{{3.5cm}}
                    \cantidadInversores
                    \vspace{{1pt}}
                  \end{{minipage}} \\ \cline{{2-4}}
                & {prot_item} & {prot_desc} & {prot_cant} \\ \hline
        \end{{tabular}}%
    }}
\end{{table}}

\newpage
Finalmente, para la contextualización general del proyecto se presenta la \cref{{fig:ubicacion}}, donde se resalta la ubicación de este.
{bloque_geoespacial}
\begin{{figure}}[H]
    \centering
    {img_ubicacion}
    \caption{{Ubicación Geográfica {sigla_proyecto} \nombreProyecto\ - \capacidadMW\ , Google Earth }}
    \label{{fig:ubicacion}}
\end{{figure}}
\newpage
""" if incluir_subsec_2_1 else ""

    bloque_s2 = rf"""% =====================================================================
% SECCIÓN 2: DESCRIPCIÓN GENERAL DEL PROYECTO
% =====================================================================
\section{{DESCRIPCIÓN GENERAL DEL PROYECTO}}
{subsec_2_1_tex}
""" if (incluir_sec_2 and incluir_subsec_2_1) else ""
    bloque_s2 += generar_latex_secciones_personalizadas("sec_2", params, es_autogenerador)

    # --- SECCIÓN 3: PARÁMETROS ELÉCTRICOS DE LOS EQUIPOS Y SUBSECCIONES ---
    subsec_3_1_tex = rf"""\subsection{{\textit{{Equipos}}}}
En la \cref{{fig:fichapanel}}, se puede apreciar las características técnicas de los paneles fotovoltaicos seleccionados para el proyecto. \\
\equipos

\begin{{figure}}[h]
    \centering
    {img_ficha_panel}
    \caption{{Hoja técnica del panel fotovoltaico }}
    \label{{fig:fichapanel}}
\end{{figure}}
\smallskip

\figinversores
""" if incluir_subsec_3_1 else ""

    subsec_3_2_tex = rf"""\subsection{{\textit{{Información OR}}}}
{sec3_or_texto}\\[0.3cm]
Dado lo anterior, la información suministrada se puede apreciar en las \informacionOR.

{bloque_eq_red}

{csv_cargas_ini}

{csv_cargas_fin}
""" if incluir_subsec_3_2 else ""

    bloque_s3 = rf"""% =====================================================================
% SECCIÓN 3: PARÁMETROS ELÉCTRICOS DE LOS EQUIPOS Y OPERACIÓN DECLARADA
% =====================================================================
\section{{PARÁMETROS ELÉCTRICOS DE LOS EQUIPOS Y OPERACIÓN DECLARADA}}
{subsec_3_1_tex}
{subsec_3_2_tex}
""" if (incluir_sec_3 and (incluir_subsec_3_1 or incluir_subsec_3_2)) else ""
    bloque_s3 += generar_latex_secciones_personalizadas("sec_3", params, es_autogenerador)

    # --- SECCIÓN 4: INFORMACIÓN DE ENTRADA Y SUPUESTOS DE SALIDA Y SUBSECCIONES ---
    subsec_4_1_tex = rf"""\subsection{{\textit{{Modelo de la zona de influencia}}}}
{sec4_1_texto}
\begin{{figure}}[h]
    \centering
    {img_unifilar}
    \caption{{Diagrama Unifilar del cto \CTO\ }}
    \label{{fig:Unifilar}}
\end{{figure}}
""" if incluir_subsec_4_1 else ""

    subsec_4_2_tex = rf"""\subsection{{\textit{{Horizonte de análisis}}}}
{sec4_2_texto}
{bloque_tabla_horizonte}
\vspace{{-10pt}}
""" if incluir_subsec_4_2 else ""

    subsec_4_3_tex = rf"""\subsection{{\textit{{Información de la demanda de potencia}}}}
{sec4_3_texto}
{csv_demanda_energia}
""" if incluir_subsec_4_3 else ""

    subsec_4_4_tex = rf"""\subsection{{\textit{{Información de energía producida Vs Energía demandada.}}}}
{sec4_4_intro}
{csv_consumo_vs_gen}

{sec4_4_curva}

\begin{{figure}}[H]
    \centering
    {img_curva_cto}
    \caption{{{caption_curva_cto}}}
    \label{{fig:curvadecarga211}}
\end{{figure}}

{sec4_4_comp}

\begin{{figure}}[H]
    \centering
    {img_consumo_gen}
    \caption{{Curva de consumo y generación. }}
    \label{{fig:consumoygeneracion}}
\end{{figure}}
\newpage
""" if incluir_subsec_4_4 else ""

    bloque_s4 = rf"""% =====================================================================
% SECCIÓN 4: INFORMACIÓN DE ENTRADA Y SUPUESTOS DE SALIDA
% =====================================================================
\section{{INFORMACIÓN DE ENTRADA Y SUPUESTOS DE SALIDA}}
{subsec_4_1_tex}
{subsec_4_2_tex}
{subsec_4_3_tex}
{subsec_4_4_tex}
""" if (incluir_sec_4 and (incluir_subsec_4_1 or incluir_subsec_4_2 or incluir_subsec_4_3 or incluir_subsec_4_4)) else ""
    bloque_s4 += generar_latex_secciones_personalizadas("sec_4", params, es_autogenerador)

    # --- SECCIÓN 5: METODOLOGÍA Y SUBSECCIONES ---
    subsec_5_1_tex = rf"""\subsection{{\textit{{Criterios técnicos}}}}
{sec5_1_texto}
""" if incluir_subsec_5_1 else ""

    subsec_5_2_tex = rf"""\subsection{{\textit{{Descripción de los análisis a realizar}}}}
{sec5_2_texto}
""" if incluir_subsec_5_2 else ""

    bloque_s5 = rf"""% =====================================================================
% SECCIÓN 5: METODOLOGÍA
% =====================================================================
\section{{METODOLOGÍA}}
{sec5_intro}\\

{subsec_5_1_tex}
{subsec_5_2_tex}
""" if (incluir_sec_5 and (incluir_subsec_5_1 or incluir_subsec_5_2)) else ""
    bloque_s5 += generar_latex_secciones_personalizadas("sec_5", params, es_autogenerador)

    # --- SECCIÓN 6: ESCENARIOS DE ANÁLISIS ---
    subsec_6_1_tex = rf"""{sec6_contenido}
\newpage
""" if incluir_subsec_6_1 else ""

    bloque_s6 = rf"""% =====================================================================
% SECCIÓN 6: DESCRIPCIÓN DE LOS ESCENARIOS DE ANÁLISIS
% =====================================================================
\section{{DESCRIPCIÓN DE LOS ESCENARIOS DE ANÁLISIS}}
{subsec_6_1_tex}
""" if (incluir_sec_6 and incluir_subsec_6_1) else ""
    bloque_s6 += generar_latex_secciones_personalizadas("sec_6", params, es_autogenerador)

    # --- SECCIÓN 7: RESULTADOS DE ANÁLISIS ELÉCTRICOS Y SUBSECCIONES ---
    subsec_7_1_tex = rf"""\subsection{{\textit{{Flujo de carga AC en estado estable para condiciones normales de operación (Sistema Des-balanceado)}}}}
A continuación, se presenta la leyenda que contiene todos los parámetros presentados en cada una de las cajas de resultados de la simulación, para el estudio de flujo de carga.
\begin{{table}}[htbp]
    \centering
    \caption{{Convenciones de los cuadros de resultados de las simulaciones}}
    \label{{tab:convencionesflujos}}
    {img_conv_flujos}
\end{{table}}
\\
Además, para todas las simulaciones de flujo, se cuenta con la siguiente paleta de colores, en ella se puede ver como las líneas que no cuentan con un color negro están por debajo del 100\% de cargabilidad, y las barras con un color verde, se encuentran cercanas a 1 p.u. en tensión.

\begin{{figure}}[h]
    \centering
    {img_cod_colores}
    \caption{{Código de colores en las simulaciones }}
    \label{{fig:codigocoloresflujo}}
\end{{figure}}
\smallskip

\newpage
A continuación, se presenta el resumen de los resultados de cargabilidad y perfil de tensión de los años y escenarios de demanda y generación analizados para el circuito \CTO.
\begin{{table}}[H]
    \centering
    \caption{{Flujo de Cargabilidad}}
    \label{{tab:Cargabilidad}}
    {img_cargabilidad}
\end{{table}}

{sec7_cargabilidad_txt}

En la \cref{{tab:TensionesPU}} se muestran los resultados de los perfiles de tensión del circuito con y sin proyecto de generación.\\

\begin{{table}}[htbp]
    \centering
    \caption{{Tensión de barras}}
    \label{{tab:TensionesPU}}
    {img_tensiones_pu}
\end{{table}}

\CONCLUSIONFERFILESCARGA\\[0.3cm]
Con el fin de evaluar el cambio en el perfil de tensión de los nodos de la zona de interés del proyecto {sigla_proyecto} \nombreProyecto, se presentan los valores p.u. de las tensiones del circuito la \cref{{fig:perfiltensionCTO}}
\begin{{figure}}[h]
    \centering
    {img_perfil_cto}
    \caption{{Perfil de tensión de la totalidad del circuito \CTO}}
    \label{{fig:perfiltensionCTO}}
\end{{figure}}
""" if incluir_subsec_7_1 else ""

    subsec_7_2_tex = rf"""\clearpage
\CONTINGENCIA
\clearpage
""" if (incluir_subsec_7_2 and incluir_contingencia) else ""

    subsec_7_3_tex = rf"""\subsection{{\textit{{Cálculo de pérdidas}}}}
Para determinar las pérdidas del sistema se realizan simulaciones de flujo de carga en los tres horarios, con y sin proyecto, con su respectivo despacho de acuerdo con la hora. Evaluando los cambios de perdida en los horizontes de tiempo.
\begin{{table}}[htbp]
    \centering
    \caption{{Pérdidas SDL [kW] }}
    \label{{tab:Perdidas}}
    {img_perdidas}
\end{{table}}
{sec7_perdidas_texto}
""" if incluir_subsec_7_3 else ""

    subsec_7_4_tex = rf"""\subsection{{\textit{{Verificación del nivel de cortocircuito (Monofásico y Trifásico con la NORMA IEC60909)}}}}
Según el sistema modelado se presentan los siguientes análisis propuestos, en base a la IEC 60909 versión 2016, la cual incorpora el aporte de corriente de cortocircuito de las tecnologías de generación basadas en inversores como la solar fotovoltaica.\\
Se tienen las siguientes convenciones:
\begin{{itemize}}
    \item Skss = Potencia de cortocircuito inicial.
    \item Ikss = Corriente de corto circuito simétrica inicial.
    \item Ip = Corriente de corto circuito máxima instantánea.
\end{{itemize}}
En la \cref{{tab:convencionescortos}} se puede apreciar la leyenda de las imágenes de los estudios, la cual representa el contenido de las cajas de resultados. Tanto para un corto trifásico como para un monofásico. \\
\begin{{table}}[H]
    \centering
    \caption{{Convenciones de los cuadros de resultados de las simulaciones de corto}}
    \label{{tab:convencionescortos}}
    {img_leyendas_cortos}
\end{{table}}
En la \cref{{tab:cortos}} se muestran los niveles de corto en los tres escenarios, con proyecto y sin proyecto, para los años del horizonte de análisis, en las tablas se muestran los resultados de los elementos de la zona de influencia, los resultados de todos los nodos se encuentran en el archivo de Excel anexado al estudio.
\begin{{table}}[htbp]
    \centering
    \caption{{Resultados de cortocircuito}}
    \label{{tab:cortos}}
    {img_cortos}
\end{{table}}
\newpage
""" if incluir_subsec_7_4 else ""

    subsec_7_5_tex = rf"""\subsection{{\textit{{Calidad de potencia}}}}
Declaración técnica del equipo en cuanto al cumplimiento de los parámetros establecidos en la IEEE 1547 y de estándares en cuanto a la calidad de la potencia (inyección de armónicos a la red y fluctuaciones de tensión, etc) sujetos a la verificación con medidas en campo antes y después de la instalación del proyecto.\\
La IEEE 1547 provee especificaciones y requerimientos técnicos referente al desempeño, operación, ensayos, consideraciones de seguridad y mantenimiento de los generadores que se integran al SIN. \\
Los siguientes inversores propuestos para el proyecto {sigla_proyecto} \nombreProyecto.
\Inversores
Cumplen con los estándares de las siguientes normativas que pueden ser consultadas en la ficha técnica del equipo, donde la distorsión armónica total inyectada del equipo es <3\% y cumple con su función ANTI-ISLA en caso de faltar onda de tensión del operador:
\begin{{itemize}}
     \item \textbf{{IEEE 1574}}
     \item \textbf{{UL1747}}
     \item \textbf{{Resolución CREG 024 de 2005}}
\end{{itemize}}
""" if incluir_subsec_7_5 else ""

    subsec_7_6_tex = rf"""\subsection{{\textit{{Análisis para evitar el funcionamiento en isla}}}}
Con base a lo estipulado en la circular 021 del 2022 del CNO, en específico en el apartado 8.5 que dice “El funcionamiento en isla de una red de distribución consiste en la posible alimentación temporal del sistema de generación a usuarios en ausencia de la red principal. Este funcionamiento debe ser evitado con el fin de mantener la seguridad de la operación y la calidad de suministro dentro los límites establecidos. En los casos donde la generación es capaz de mantener autónomamente los valores de tensión y frecuencia, existirá riesgo de funcionamiento en isla cunado cumpla la siguiente relación”
\begin{{equation}}
    \left( \sum_{{i=1 \text{{ a }} N}} P_{{maxgi}} \right) + P_{{gnuevo}} \geq P_{{mindem}}
\end{{equation}}
\newpage
\vspace{{0.5cm}}
\noindent \textbf{{Donde:}}
\begin{{itemize}}
    \item $P_{{maxgi}}$: Potencia Instalada del generador $i$.
    \item $P_{{gnuevo}}$: Potencia Máxima del generador a estudiar.
    \item $P_{{mindem}}$: Potencia demanda mínima.
\end{{itemize}}
De esta forma se presenta que:
\begin{{equation}}
    \label{{eq:balance_potencia}}
    \generacionaprobada + \capacidadMW \geq \potenciaminima
\end{{equation}}\\
{sec7_isla_conclusion}
""" if incluir_subsec_7_6 else ""

    bloque_s7 = rf"""% =====================================================================
% SECCIÓN 7: RESULTADOS DE LOS ANÁLISIS ELÉCTRICOS
% =====================================================================
\section{{RESULTADOS DE LOS ANÁLISIS ELÉCTRICOS.}}
{subsec_7_1_tex}
{subsec_7_2_tex}
{subsec_7_3_tex}
{subsec_7_4_tex}
{subsec_7_5_tex}
{subsec_7_6_tex}
""" if (incluir_sec_7 and (incluir_subsec_7_1 or incluir_subsec_7_2 or incluir_subsec_7_3 or incluir_subsec_7_4 or incluir_subsec_7_5 or incluir_subsec_7_6)) else ""
    bloque_s7 += generar_latex_secciones_personalizadas("sec_7", params, es_autogenerador)

    # --- SECCIÓN 8: VERIFICACIÓN DE PROTECCIONES ---
    txt_s8_ac = rf"""\sistemaAC
""" if incluir_subsec_8_1 else ""

    txt_s8_equipos = rf"""En el sistema fotovoltaico y tablero principal existen las siguientes protecciones:

\begin{{center}}
    \begin{{minipage}}{{1\textwidth}}
        \centering
        \captionof{{table}}{{Protección {sigla_proyecto}\nombreProyecto }}
        \label{{tab:SEL}}
        \begingroup
        \setlength{{\tabcolsep}}{{8pt}}
        \renewcommand{{\arraystretch}}{{1.2}}
        \small
        \begin{{tabular}}{{|l|c|c|c|}}
            \hline
            \rowcolor{{azulSeyep}}
            \multicolumn{{1}}{{|c|}}{{\color{{white}}\textbf{{Protege}}}} & \color{{white}}\textbf{{TIPO}} & \color{{white}}\textbf{{REFERENCIA}} &  \color{{white}}\textbf{{TC / TP}} \\ \hline
            {gd_protege} & {gd_tipo} & {gd_ref} & {gd_tctp} \\ \hline
        \end{{tabular}}
        \endgroup
    \end{{minipage}}
\end{{center}}

\begin{{center}}
    \begin{{minipage}}{{1\textwidth}}
        \centering
        \captionof{{table}}{{Protección Inversores }}
        \label{{tab:LSI}}
        \begingroup
        \setlength{{\tabcolsep}}{{8pt}}
        \renewcommand{{\arraystretch}}{{1.2}}
        \small
        \begin{{tabular}}{{|l|c|c|}}
            \hline
            \rowcolor{{azulSeyep}}
            \multicolumn{{1}}{{|c|}}{{\color{{white}}\textbf{{Protege}}}} & \color{{white}}\textbf{{TIPO}} & \color{{white}}\textbf{{Ajuste}} \\ \hline
            {inv_protege} & {inv_tipo} & {inv_ajuste} \\ \hline
        \end{{tabular}}
        \endgroup
    \end{{minipage}}
\end{{center}}

En el circuito se tienen la siguientes protecciones por parte del OR:

\begin{{center}}
    \begin{{minipage}}{{1\textwidth}}
        \centering
        \captionof{{table}}{{Protección del circuito \recoCTO }}
        \label{{tab:SEL_OR}}
        \begingroup
        \setlength{{\tabcolsep}}{{8pt}}
        \renewcommand{{\arraystretch}}{{1.2}}
        \small
        \begin{{tabular}}{{|l|c|}}
            \hline
            \rowcolor{{azulSeyep}}
            \multicolumn{{1}}{{|c|}}{{\color{{white}}\textbf{{Protege}}}} & \color{{white}}\textbf{{TIPO}} \\ \hline
            {or_protege} & {or_tipo_desc} \\ \hline
        \end{{tabular}}
        \endgroup
    \end{{minipage}}
\end{{center}}
""" if incluir_subsec_8_2 else ""

    txt_s8_reco = rf"""El resto de consideraciones en cuanto a protecciones se dejan plasmados en el anexo ``Anexo EACP''. El resumen de los ajustes establecidos en dicho documento se muestra en las \cref{{tab:ajustesrecoProyecto,tab:resumenajustestotales}}.
\begin{{center}}
    \begin{{minipage}}{{1\textwidth}}
        \centering
        \captionof{{table}}{{Ajustes de protección para el Reconectador \nombreProyecto.}}
        \label{{tab:ajustesrecoProyecto}}
        \begingroup
        \setlength{{\tabcolsep}}{{12pt}}
        \renewcommand{{\arraystretch}}{{1.3}}
        \small
        \begin{{tabular}}{{|l|c|c|c|}}
            \hline
            \rowcolor{{azulSeyep}} 
            \multicolumn{{1}}{{|c|}}{{\color{{white}}\textbf{{Parámetro}}}} & \color{{white}}\textbf{{Pick Up [Aprim]}} & \color{{white}}\textbf{{DIAL [s]}} & \color{{white}}\textbf{{Curva}} \\ \hline
            {contenido_filas_reco}
        \end{{tabular}}
        \endgroup
    \end{{minipage}}
\end{{center}}
""" if incluir_subsec_8_3 else ""

    txt_s8_sist = rf"""    \renewcommand{{\arraystretch}}{{0}} 
\begin{{table}}[H]
    \centering
    \captionof{{table}}{{Resumen ajuste de protecciones sistemáticas para generadores basados en inversores y frecuencia variable de capacidad instalada o nominal > 0,25 MW conectados al SDL}}
    \label{{tab:resumenajustestotales}}
    \begingroup    
    \resizebox{{\textwidth}}{{!}}{{%
        \renewcommand{{\arraystretch}}{{1.3}} 
        \begin{{tabular}}{{|c|c|c|}}
            \hline
            \rowcolor{{azulSeyep}} 
            \textbf{{\color{{white}}Función}} & \textbf{{\color{{white}}Ajustes}} & \textbf{{\color{{white}}Temporización}} \\ \hline
            {contenido_filas_sist}
        \end{{tabular}}
    }}
    \endgroup
\end{{table}}
""" if incluir_subsec_8_4 else ""

    bloque_s8 = rf"""% =====================================================================
% SECCIÓN 8: VERIFICACIÓN DE PROTECCIONES
% =====================================================================
%\newpage
\section{{VERIFICACIÓN DE PROTECCIONES}}  
La verificación de protecciones se realiza en el documento ``EACP'' suministrado como anexo. Con el objetivo de plasmar en este documento la información básica de los elementos que componen el sistema de porotecciones, se citan las tablas resumen a continuación:
\\

{txt_s8_ac}
{txt_s8_equipos}
{txt_s8_reco}
{txt_s8_sist}
""" if (incluir_sec_8 and (incluir_subsec_8_1 or incluir_subsec_8_2 or incluir_subsec_8_3 or incluir_subsec_8_4)) else ""
    bloque_s8 += generar_latex_secciones_personalizadas("sec_8", params, es_autogenerador)

    # --- SECCIÓN 9: CONCLUSIONES ---
    bloque_s9 = rf"""% =====================================================================
% SECCIÓN 9: CONCLUSIONES
% =====================================================================
\clearpage
\section{{CONCLUSIONES}}  
\CONCLUSIONES
""" if incluir_sec_9 else ""
    bloque_s9 += generar_latex_secciones_personalizadas("sec_9", params, es_autogenerador)

    # --- SECCIÓN 10: ANEXOS ---
    bloque_s10 = rf"""% =====================================================================
% SECCIÓN 10: ANEXOS
% =====================================================================
\clearpage
\section{{ANEXOS}}
\Flujosdecarga
""" if incluir_sec_10 else ""
    bloque_s10 += generar_latex_secciones_personalizadas("sec_10", params, es_autogenerador)

    bloque_sglobal = generar_latex_secciones_personalizadas("sec_global", params, es_autogenerador)

    cuerpo_documento = (
        bloque_intro
        + bloque_s1
        + bloque_s2
        + bloque_s3
        + bloque_s4
        + bloque_s5
        + bloque_s6
        + bloque_s7
        + bloque_s8
        + bloque_s9
        + bloque_s10
        + bloque_sglobal
        + f"""
\\end{{document}}
"""
    )


    contenido_latex = (
        generar_preambulo()
        + comandos_variables
        + cuerpo_documento
    )
    return contenido_latex


def compilar_estudio_latex(params=None):
    """
    Genera el código LaTeX completo, escribe el archivo 'Estudio_Conexion.tex'
    y ejecuta pdflatex para producir 'Estudio_Conexion.pdf'.
    Retorna una tupla (éxito: bool, ruta_pdf_o_error: str).
    """
    contenido_latex = generar_codigo_latex(params)
    tex_filename = "Estudio_Conexion.tex"
    pdf_filename = "Estudio_Conexion.pdf"

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
            if os.path.isfile(r) and (os.name == 'nt' or os.access(r, os.X_OK)):
                return r
        return None

    pdflatex_bin = buscar_ejecutable_pdflatex()
    if not pdflatex_bin:
        return False, (
            "⚠️ No se encontró el ejecutable 'pdflatex' en las rutas del sistema.\n\n"
            "El archivo fuente 'Estudio_Conexion.tex' fue generado y guardado correctamente.\n\n"
            "• Si estás en Streamlit Cloud: Asegúrate de tener el archivo 'packages.txt' en la raíz de tu repositorio de GitHub con los paquetes de TeX Live:\n"
            "    texlive-latex-base\n"
            "    texlive-latex-recommended\n"
            "    texlive-latex-extra\n"
            "    texlive-fonts-recommended\n"
            "    texlive-science\n"
            "    texlive-lang-spanish\n"
            "  y reinicia la app ('Reboot App' en el menú de Streamlit Cloud).\n\n"
            "• Si estás en tu computador local: Verifica que MiKTeX o TeX Live esté instalado y agregado a la variable PATH del sistema.\n\n"
            "• Opción Rápida: Puedes descargar el archivo fuente 'Estudio_Conexion.tex' generado con el botón de abajo y compilarlo directamente en Overleaf o en tu editor TeX favorito."
        )

    try:
        cmd = [pdflatex_bin, "-interaction=nonstopmode", "-halt-on-error", tex_filename]
        proceso1 = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=(os.name == 'nt'))
        if proceso1.returncode != 0:
            log_contenido = ""
            if os.path.exists("Estudio_Conexion.log"):
                with open("Estudio_Conexion.log", "r", encoding="utf-8", errors="ignore") as log_file:
                    log_contenido = log_file.read()

            todas_lineas = log_contenido.splitlines()
            bloques_error = []
            for idx, line in enumerate(todas_lineas):
                if line.startswith("!"):
                    fragmento = "\n".join(todas_lineas[idx:idx + 5])
                    bloques_error.append(fragmento)

            detalle = "\n---\n".join(bloques_error[:3]) if bloques_error else "Error desconocido en pdflatex."
            return False, f"Fallo de compilación en LaTeX:\n{detalle}"

        # Segunda pasada para generar TOC y referencias cruzadas
        subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=(os.name == 'nt'))

        if os.path.exists(pdf_filename):
            return True, pdf_filename
        else:
            return False, "No se encontró el PDF resultante tras la compilación."
    except subprocess.TimeoutExpired:
        return False, "La compilación tardó demasiado y fue interrumpida (timeout de 60s)."
    except Exception as e:
        return False, f"Error inesperado al ejecutar pdflatex: {str(e)}"
