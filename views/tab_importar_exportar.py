import io
import csv
import json
from datetime import date, datetime
import streamlit as st
import pandas as pd

EXCLUDED_PREFIXES = (
    "_",
    "FormSubmitter:",
    "io_uploader_",
    "io_select_",
    "io_confirm_",
    "io_editor_",
    "io_table_select_",
    "btn_",
    "sb_",
)

def _is_exportable_key(key: str, value) -> bool:
    if not isinstance(key, str) or key.startswith(EXCLUDED_PREFIXES):
        return False
    if type(value).__name__ in ("UploadedFile", "BytesIO", "BufferedReader"):
        return False
    return True

def _serialize_value(val):
    if isinstance(val, pd.DataFrame):
        return {
            "__seyep_type__": "DataFrame",
            "columns": list(val.columns),
            "records": val.to_dict(orient="records"),
        }
    if isinstance(val, (datetime, date)):
        return {"__seyep_type__": "date", "iso": val.isoformat()}
    if isinstance(val, set):
        return list(val)
    return val

def _deserialize_value(val):
    if isinstance(val, dict) and "__seyep_type__" in val:
        kind = val["__seyep_type__"]
        if kind == "DataFrame":
            records = val.get("records", [])
            columns = val.get("columns", None)
            return pd.DataFrame(records, columns=columns) if columns else pd.DataFrame(records)
        if kind == "date":
            try:
                return date.fromisoformat(val["iso"][:10])
            except Exception:
                return val["iso"]
    return val

def export_session_to_json() -> str:
    export_data = {}
    for k, v in st.session_state.items():
        if not _is_exportable_key(k, v):
            continue
        try:
            serialized = _serialize_value(v)
            json.dumps(serialized, default=str)
            export_data[k] = serialized
        except Exception:
            continue

    payload = {
        "_metadata": {
            "app": "app-SEYEP-ESC",
            "format_version": "2.0",
            "exported_at": datetime.now().isoformat(),
        },
        "data": export_data,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)

def export_session_to_csv() -> str:
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["clave", "tipo_dato", "valor"])

    for k, v in sorted(st.session_state.items()):
        if not _is_exportable_key(k, v):
            continue
        try:
            if isinstance(v, pd.DataFrame):
                writer.writerow([k, "dataframe", json.dumps(_serialize_value(v), ensure_ascii=False, default=str)])
            elif isinstance(v, (list, dict)):
                writer.writerow([k, type(v).__name__, json.dumps(v, ensure_ascii=False, default=str)])
            elif isinstance(v, bool):
                writer.writerow([k, "bool", "true" if v else "false"])
            elif isinstance(v, int):
                writer.writerow([k, "int", str(v)])
            elif isinstance(v, float):
                writer.writerow([k, "float", str(v)])
            elif isinstance(v, (date, datetime)):
                writer.writerow([k, "date", v.isoformat()])
            else:
                writer.writerow([k, "str", str(v if v is not None else "")])
        except Exception:
            continue
    return output.getvalue()

def parse_uploaded_file(uploaded_file) -> tuple[dict, list[str]]:
    warnings = []
    parsed_data = {}
    filename = uploaded_file.name.lower()
    raw_text = uploaded_file.getvalue().decode("utf-8-sig")

    if filename.endswith(".json"):
        raw_json = json.loads(raw_text)
        source_dict = raw_json.get("data", raw_json) if isinstance(raw_json, dict) else {}
        for k, v in source_dict.items():
            if not str(k).startswith("_"):
                parsed_data[k] = _deserialize_value(v)

    elif filename.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(raw_text))
        fieldnames = [f.strip().lower() for f in (reader.fieldnames or [])]
        if "clave" in fieldnames and "valor" in fieldnames:
            for row in reader:
                norm_row = {k.strip().lower(): v for k, v in row.items() if k}
                key = norm_row.get("clave", "").strip()
                if not key or key.startswith("_"):
                    continue
                val_str = norm_row.get("valor", "")
                dtype = norm_row.get("tipo_dato", "str").strip().lower()
                try:
                    if dtype == "dataframe":
                        raw_obj = json.loads(val_str)
                        parsed_data[key] = _deserialize_value(raw_obj) if isinstance(raw_obj, dict) else pd.DataFrame(raw_obj)
                    elif dtype in ("list", "dict", "json"):
                        parsed_data[key] = json.loads(val_str)
                    elif dtype in ("bool", "boolean"):
                        parsed_data[key] = val_str.strip().lower() in ("true", "1", "sí", "si")
                    elif dtype == "int":
                        parsed_data[key] = int(float(val_str))
                    elif dtype in ("float", "number"):
                        parsed_data[key] = float(val_str)
                    elif dtype == "date":
                        parsed_data[key] = date.fromisoformat(val_str[:10])
                    else:
                        parsed_data[key] = val_str
                except Exception as exc:
                    parsed_data[key] = val_str
                    warnings.append(f"Clave '{key}' importada como texto ({exc}).")
        else:
            df_tabular = pd.read_csv(io.StringIO(raw_text))
            table_key = f"tabla_{uploaded_file.name.rsplit('.', 1)[0]}"
            parsed_data[table_key] = df_tabular
            warnings.append(f"CSV tabular detectado ({len(df_tabular)} filas). Clave asignada: '{table_key}'.")

    return parsed_data, warnings

def _format_preview_summary(val) -> str:
    if isinstance(val, pd.DataFrame):
        return f"DataFrame ({len(val)} filas × {len(val.columns)} cols)"
    if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
        return f"Tabla ({len(val)} registros)"
    text = str(val if val is not None else "—")
    return text if len(text) <= 85 else text[:82] + "..."

def render_import_export_section(location_key: str = "main"):
    st.markdown("### 📦 Exportar e Importar Datos del Informe (JSON / CSV)")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Exportar Datos (.JSON)",
            data=export_session_to_json().encode("utf-8"),
            file_name="informe_SEYEP_ESC.json",
            mime="application/json",
            use_container_width=True,
            key=f"btn_export_json_{location_key}",
        )
    with col2:
        st.download_button(
            label="⬇️ Exportar Datos (.CSV)",
            data=export_session_to_csv().encode("utf-8-sig"),
            file_name="informe_SEYEP_ESC.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"btn_export_csv_{location_key}",
        )

    st.divider()
    uploaded_file = st.file_uploader(
        "Cargar archivo JSON o CSV (con Vista Previa antes de aplicar)",
        type=["json", "csv"],
        key=f"io_uploader_{location_key}",
    )

    if uploaded_file is not None:
        try:
            parsed_data, warnings = parse_uploaded_file(uploaded_file)
            for w in warnings:
                st.warning(w)

            preview_rows = []
            tables_detected = {}
            for key, inc_val in parsed_data.items():
                has_current = key in st.session_state
                cur_val = st.session_state.get(key, None)
                estado = "Nuevo" if not has_current else ("Sin cambios" if str(cur_val) == str(inc_val) else "Modificado")

                if isinstance(inc_val, pd.DataFrame):
                    tables_detected[key] = inc_val
                elif isinstance(inc_val, list) and len(inc_val) > 0 and isinstance(inc_val[0], dict):
                    tables_detected[key] = pd.DataFrame(inc_val)

                preview_rows.append({
                    "Importar": estado != "Sin cambios",
                    "Clave": key,
                    "Tipo": type(inc_val).__name__,
                    "Estado": estado,
                    "Valor Actual": _format_preview_summary(cur_val) if has_current else "(No existe)",
                    "Valor a Importar (Vista Previa)": _format_preview_summary(inc_val),
                })

            st.markdown("#### 🔍 Vista Previa del Archivo Antes de Finalizar la Carga")
            edited_df = st.data_editor(
                pd.DataFrame(preview_rows),
                disabled=["Clave", "Tipo", "Estado", "Valor Actual", "Valor a Importar (Vista Previa)"],
                hide_index=True,
                use_container_width=True,
                key=f"io_editor_{location_key}_{uploaded_file.name}",
            )

            if tables_detected:
                with st.expander(f"📊 Previsualizar Tablas del Archivo ({len(tables_detected)})", expanded=True):
                    sel_tab = st.selectbox("Tabla:", list(tables_detected.keys()), key=f"io_table_select_{location_key}")
                    if sel_tab:
                        st.dataframe(tables_detected[sel_tab], use_container_width=True)

            selected_keys = edited_df.loc[edited_df["Importar"] == True, "Clave"].tolist()
            if st.button(
                f"✅ Confirmar y Finalizar Carga ({len(selected_keys)} campos)",
                type="primary",
                disabled=len(selected_keys) == 0,
                use_container_width=True,
                key=f"io_confirm_{location_key}",
            ):
                for k in selected_keys:
                    st.session_state[k] = parsed_data[k]
                st.success(f"Se cargaron {len(selected_keys)} parámetros en el informe.")
                st.rerun()
        except Exception as err:
            st.error(f"Error al previsualizar el archivo: {err}")