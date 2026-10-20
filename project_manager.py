import json
import os
import base64
import pandas as pd
import streamlit as st

IMAGENES_PROYECTO = [
    "Logo_Cliente.png",
    "Proteccion27-59.png",
    "ICC 1F GCP.png",
    "ICC 1F GSP.png",
    "ICC 3F GCP.png",
    "ICC 3F GSP.png",
    "Protecciones falla lado alta proyecto.png",
    "Protecciones falla 1F franca lado alta proyecto.png",
    "Protecciones falla 1F 5ohms lado alta proyecto.png",
    "Protecciones falla 1F 15ohms lado alta proyecto.png",
    "Protecciones falla 1F 30ohms lado alta proyecto.png",
    "Protecciones falla 3F franca lado alta proyecto.png",
    "Protecciones falla 3F 5ohms lado alta proyecto.png",
    "Protecciones falla 3F 15ohms lado alta proyecto.png",
    "Protecciones falla 3F 30ohms lado alta proyecto.png",
    "Protecciones falla lado baja proyecto.png",
    "Protecciones falla 1F franca lado baja proyecto.png",
    "Protecciones falla 3F franca lado baja proyecto.png",
    "Protecciones falla nodo conexión proyecto.png",
    "Protecciones falla 1F franca nodo conexión proyecto.png",
    "Protecciones falla 1F 5ohms nodo conexión proyecto.png",
    "Protecciones falla 1F 15ohms nodo conexión proyecto.png",
    "Protecciones falla 1F 30ohms nodo conexión proyecto.png",
    "Protecciones falla 3F franca nodo conexión proyecto.png",
    "Protecciones falla 3F 5ohms nodo conexión proyecto.png",
    "Protecciones falla 3F 15ohms nodo conexión proyecto.png",
    "Protecciones falla 3F 30ohms nodo conexión proyecto.png",
]

def obtener_ver():
    return st.session_state.get("ver_import", 0)

def obtener_val(clave, default):
    """Obtiene el valor guardado de un proyecto importado o devuelve el valor por defecto."""
    proy = st.session_state.get("proyecto_cargado", {})
    if isinstance(proy, dict) and clave in proy and proy[clave] is not None:
        return proy[clave]
    return default

def obtener_df(clave, df_default):
    """Obtiene un DataFrame guardado de un proyecto importado o devuelve el DataFrame por defecto."""
    proy = st.session_state.get("proyecto_cargado", {})
    if isinstance(proy, dict) and clave in proy:
        val = proy[clave]
        if isinstance(val, list):
            return pd.DataFrame(val)
        if isinstance(val, pd.DataFrame):
            return val
    return df_default

def serializar_objeto(obj):
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    if isinstance(obj, list):
        nueva_lista = []
        for item in obj:
            if isinstance(item, dict):
                nuevo_item = {}
                for k, v in item.items():
                    nuevo_item[k] = serializar_objeto(v)
                nueva_lista.append(nuevo_item)
            else:
                nueva_lista.append(item)
        return nueva_lista
    return obj

def exportar_proyecto_json(params_totales):
    """Empaqueta todas las variables, tablas, equipos adicionales del OR e imágenes en un JSON."""
    paquete = {
        "formato": "SEYEP_EACP_V1",
        "datos": {},
        "imagenes_b64": {}
    }

    for k, v in params_totales.items():
        paquete["datos"][k] = serializar_objeto(v)

    paquete["datos"]["num_equipos_or_extra"] = st.session_state.get("num_equipos_or_extra", 0)
    paquete["datos"]["num_cambios_or_extra"] = st.session_state.get("num_cambios_or_extra", 0)

    for img_name in IMAGENES_PROYECTO:
        if os.path.exists(img_name):
            try:
                with open(img_name, "rb") as f_img:
                    paquete["imagenes_b64"][img_name] = base64.b64encode(f_img.read()).decode("utf-8")
            except Exception:
                pass

    return json.dumps(paquete, ensure_ascii=False, indent=2).encode("utf-8")

def importar_proyecto_json(uploaded_json_file):
    """Restaura todas las variables, tablas e imágenes desde un archivo JSON de proyecto."""
    contenido = json.loads(uploaded_json_file.getvalue().decode("utf-8"))
    datos = contenido.get("datos", contenido)
    imagenes_b64 = contenido.get("imagenes_b64", {})

    st.session_state["proyecto_cargado"] = datos
    st.session_state["num_equipos_or_extra"] = int(datos.get("num_equipos_or_extra", len(datos.get("equipos_or_extra", []))))
    st.session_state["num_cambios_or_extra"] = int(datos.get("num_cambios_or_extra", len(datos.get("cambios_or_extra", []))))

    # Restaurar imágenes adjuntas en el archivo del proyecto
    for img_name, b64_str in imagenes_b64.items():
        if img_name in IMAGENES_PROYECTO and b64_str:
            try:
                with open(img_name, "wb") as f_out:
                    f_out.write(base64.b64decode(b64_str))
            except Exception:
                pass

    st.session_state["ver_import"] = st.session_state.get("ver_import", 0) + 1
