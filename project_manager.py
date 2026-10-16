import json
import os
import glob
import base64
import pandas as pd
import streamlit as st

# Guardamos referencias originales de los widgets de Streamlit
_ORIG_TEXT_INPUT = st.text_input
_ORIG_TEXT_AREA = st.text_area
_ORIG_CHECKBOX = st.checkbox
_ORIG_RADIO = st.radio
_ORIG_DATA_EDITOR = st.data_editor
_PATCH_APLICADO = False

IMAGENES_EXCLUIDAS = {"encabezado.png", "piedepagina.png"}

def obtener_ver():
    return st.session_state.get("esc_ver_import", 0)

def obtener_val(clave, default):
    """Obtiene el valor guardado de un proyecto importado o devuelve el default."""
    cargados = st.session_state.get("esc_params_cargados", {})
    if isinstance(cargados, dict) and clave in cargados and cargados[clave] is not None:
        return cargados[clave]
    widgets = st.session_state.get("esc_widgets_cargados", {})
    for w_k, w_v in widgets.items():
        if w_k.endswith(f"::{clave}") or w_k.endswith(f"::{clave}:") or w_k == clave:
            if w_v is not None:
                return w_v
    return default

def _id_widget(tipo, label, key=None):
    base = str(key) if key else str(label)
    return f"{tipo}::{base.strip()}"

def activar_persistencia_automatica():
    """
    Envuelve automáticamente los componentes de Streamlit (text_input, text_area,
    checkbox, radio, data_editor) para que todas las pestañas de app-SEYEP-ESC
    puedan Guardar e Importar su estado sin necesidad de modificar cada archivo en views/.
    """
    global _PATCH_APLICADO
    if _PATCH_APLICADO:
        return

    def _wrapped_text_input(label, value="", *args, **kwargs):
        ver = st.session_state.get("esc_ver_import", 0)
        wid = _id_widget("text_input", label, kwargs.get("key"))
        cargado = st.session_state.get("esc_widgets_cargados", {})
        if wid in cargado and cargado[wid] is not None:
            value = str(cargado[wid])
        orig_key = kwargs.get("key", f"auto_ti_{abs(hash(wid))}")
        kwargs["key"] = f"{orig_key}_v{ver}"
        res = _ORIG_TEXT_INPUT(label, value=value, *args, **kwargs)
        st.session_state.setdefault("esc_widgets_actuales", {})[wid] = res
        return res

    def _wrapped_text_area(label, value="", *args, **kwargs):
        ver = st.session_state.get("esc_ver_import", 0)
        wid = _id_widget("text_area", label, kwargs.get("key"))
        cargado = st.session_state.get("esc_widgets_cargados", {})
        if wid in cargado and cargado[wid] is not None:
            value = str(cargado[wid])
        orig_key = kwargs.get("key", f"auto_ta_{abs(hash(wid))}")
        kwargs["key"] = f"{orig_key}_v{ver}"
        res = _ORIG_TEXT_AREA(label, value=value, *args, **kwargs)
        st.session_state.setdefault("esc_widgets_actuales", {})[wid] = res
        return res

    def _wrapped_checkbox(label, value=False, *args, **kwargs):
        ver = st.session_state.get("esc_ver_import", 0)
        wid = _id_widget("checkbox", label, kwargs.get("key"))
        cargado = st.session_state.get("esc_widgets_cargados", {})
        if wid in cargado and cargado[wid] is not None:
            value = bool(cargado[wid])
        orig_key = kwargs.get("key", f"auto_chk_{abs(hash(wid))}")
        kwargs["key"] = f"{orig_key}_v{ver}"
        res = _ORIG_CHECKBOX(label, value=value, *args, **kwargs)
        st.session_state.setdefault("esc_widgets_actuales", {})[wid] = res
        return res

    def _wrapped_radio(label, options, index=0, *args, **kwargs):
        ver = st.session_state.get("esc_ver_import", 0)
        wid = _id_widget("radio", label, kwargs.get("key"))
        cargado = st.session_state.get("esc_widgets_cargados", {})
        lista_opts = list(options)
        if wid in cargado and cargado[wid] in lista_opts:
            index = lista_opts.index(cargado[wid])
        orig_key = kwargs.get("key", f"auto_rad_{abs(hash(wid))}")
        kwargs["key"] = f"{orig_key}_v{ver}"
        res = _ORIG_RADIO(label, options, index=index, *args, **kwargs)
        st.session_state.setdefault("esc_widgets_actuales", {})[wid] = res
        return res

    def _wrapped_data_editor(data, *args, **kwargs):
        ver = st.session_state.get("esc_ver_import", 0)
        wid = _id_widget("data_editor", kwargs.get("key", "tabla"))
        cargado = st.session_state.get("esc_widgets_cargados", {})
        if wid in cargado and isinstance(cargado[wid], list):
            data = pd.DataFrame(cargado[wid])
        orig_key = kwargs.get("key", f"auto_de_{abs(hash(wid))}")
        kwargs["key"] = f"{orig_key}_v{ver}"
        res = _ORIG_DATA_EDITOR(data, *args, **kwargs)
        if isinstance(res, pd.DataFrame):
            st.session_state.setdefault("esc_widgets_actuales", {})[wid] = res.to_dict(orient="records")
        return res

    st.text_input = _wrapped_text_input
    st.text_area = _wrapped_text_area
    st.checkbox = _wrapped_checkbox
    st.radio = _wrapped_radio
    st.data_editor = _wrapped_data_editor
    _PATCH_APLICADO = True

def _serializar_valor(v):
    if isinstance(v, pd.DataFrame):
        return v.to_dict(orient="records")
    return v

def exportar_proyecto_esc(params_totales):
    """
    Empaqueta en un archivo .json todos los campos, tablas editables,
    archivos CSV de modulos_latex/ e imágenes PNG del proyecto ESC.
    """
    paquete = {
        "formato": "SEYEP_ESC_V1",
        "widgets": st.session_state.get("esc_widgets_actuales", {}),
        "params": {k: _serializar_valor(v) for k, v in (params_totales or {}).items()},
        "secciones_activas": st.session_state.get("secciones_activas", {}),
        "subsecciones_activas": st.session_state.get("subsecciones_activas", {}),
        "secciones_personalizadas": st.session_state.get("secciones_personalizadas", []),
        "csv_files": {},
        "imagenes_b64": {}
    }

    # Guardar todos los CSV generados en modulos_latex/ y raíz
    patrones_csv = ["*.csv", "modulos_latex/*.csv", "modulos_latex/*/*.csv"]
    for pat in patrones_csv:
        for ruta_csv in glob.glob(pat):
            ruta_norm = ruta_csv.replace("\\", "/")
            try:
                with open(ruta_csv, "r", encoding="utf-8", errors="ignore") as fc:
                    paquete["csv_files"][ruta_norm] = fc.read()
            except Exception:
                pass

    # Guardar todas las imágenes PNG/JPG del estudio (excepto Encabezado y Piedepagina fijos)
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        for ruta_img in glob.glob(ext):
            nombre_base = os.path.basename(ruta_img)
            if nombre_base.lower() in IMAGENES_EXCLUIDAS:
                continue
            try:
                with open(ruta_img, "rb") as fi:
                    paquete["imagenes_b64"][nombre_base] = base64.b64encode(fi.read()).decode("utf-8")
            except Exception:
                pass

    return json.dumps(paquete, ensure_ascii=False, indent=2).encode("utf-8")

def importar_proyecto_esc(uploaded_json_file):
    """
    Restaura todos los campos, tablas, archivos CSV e imágenes desde un archivo .json guardado.
    """
    contenido = json.loads(uploaded_json_file.getvalue().decode("utf-8"))

    st.session_state["esc_widgets_cargados"] = contenido.get("widgets", {})
    st.session_state["esc_params_cargados"] = contenido.get("params", {})
    if "secciones_activas" in contenido:
        st.session_state["secciones_activas"] = contenido.get("secciones_activas", {})
    if "subsecciones_activas" in contenido:
        st.session_state["subsecciones_activas"] = contenido.get("subsecciones_activas", {})
    if "secciones_personalizadas" in contenido:
        st.session_state["secciones_personalizadas"] = contenido.get("secciones_personalizadas", [])

    # Restaurar archivos CSV en modulos_latex/
    for ruta_norm, texto_csv in contenido.get("csv_files", {}).items():
        carpeta = os.path.dirname(ruta_norm)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        try:
            with open(ruta_norm, "w", encoding="utf-8") as fc:
                fc.write(texto_csv)
        except Exception:
            pass

    # Restaurar imágenes PNG/JPG
    for nombre_img, b64_str in contenido.get("imagenes_b64", {}).items():
        if b64_str:
            try:
                with open(os.path.basename(nombre_img), "wb") as fi:
                    fi.write(base64.b64decode(b64_str))
            except Exception:
                pass

    st.session_state["esc_ver_import"] = st.session_state.get("esc_ver_import", 0) + 1
