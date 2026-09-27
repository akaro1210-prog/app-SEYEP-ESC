import streamlit as st

def crear_fila_variable(key_name, label_text, default_val):
    cols = st.columns([0.08, 0.42, 0.5])
    with cols[0]:
        activo = st.checkbox("Usar", value=True, key=f"chk_{key_name}")
    with cols[1]:
        st.markdown(f"**`\\{key_name}`**")
        st.caption(label_text)
    with cols[2]:
        valor = st.text_input("Valor", value=default_val, key=f"val_{key_name}", label_visibility="collapsed")
    return activo, valor

def render():
    st.subheader("Listado Maestro de Variables del Proyecto (`\\newcommand`)")
    st.write("Selecciona cuáles comandos deseas incluir y edita sus valores respectivos:")
    st.markdown("---")

    config_vars = {}

    _, config_vars["mesentregaiformemasyear"] = crear_fila_variable("mesentregaiformemasyear", "Mes y año entrega del informe", "Septiembre, 2026")
    _, config_vars["nombreProyecto"] = crear_fila_variable("nombreProyecto", "Nombre del proyecto", "Arboreo")
    _, config_vars["capacidadMW"] = crear_fila_variable("capacidadMW", "Capacidad del proyecto", "900kW")
    _, config_vars["OR"] = crear_fila_variable("OR", "Nombre del OR", "EPM")
    _, config_vars["FechaEntrada"] = crear_fila_variable("FechaEntrada", "Fecha entrada en operación", "marzo del 2027")
    _, config_vars["Latitud"] = crear_fila_variable("Latitud", "Latitud", "5°53'49.8\"N")
    _, config_vars["Longitud"] = crear_fila_variable("Longitud", "Longitud", "74°45'12.9\"W")
    _, config_vars["YearInicial"] = crear_fila_variable("YearInicial", "Año inicial de estudio", "2027")
    _, config_vars["YearFinal"] = crear_fila_variable("YearFinal", "Año final de estudio", "2032")
    _, config_vars["CTO"] = crear_fila_variable("CTO", "Circuito de conexión", "211-11")
    _, config_vars["SSEE"] = crear_fila_variable("SSEE", "Subestación", "Doradal\\_13.2")
    _, config_vars["NT"] = crear_fila_variable("NT", "Nivel de tensión", "13.2 kV")
    _, config_vars["nodo"] = crear_fila_variable("nodo", "Nodo de conexión", "906750")
    _, config_vars["elementoProteccion"] = crear_fila_variable("elementoProteccion", "Elemento de protección", "211-11")
    _, config_vars["referenciaPanel"] = crear_fila_variable("referenciaPanel", "Referencia paneles", "JAM66D45 625 LB")
    _, config_vars["potenciaPanel"] = crear_fila_variable("potenciaPanel", "Potencia paneles", "625 Wp")
    _, config_vars["cantidadPanel"] = crear_fila_variable("cantidadPanel", "Cantidad paneles", "1760")
    _, config_vars["ubicacion"] = crear_fila_variable("ubicacion", "Ubicación del proyecto", "En predio del hotel Arboreo, Doradal, Antioquia")
    _, config_vars["CP"] = crear_fila_variable("CP", "Hora Carga Pura", "-----")
    _, config_vars["Dmi"] = crear_fila_variable("Dmi", "Hora demanda mínima", "-----")
    _, config_vars["DMx"] = crear_fila_variable("DMx", "Hora demanda máxima", "-----")
    _, config_vars["escenariomaxPerdidas"] = crear_fila_variable("escenariomaxPerdidas", "Escenario pérdidas más altas", "-----")
    _, config_vars["perdidasmaximas"] = crear_fila_variable("perdidasmaximas", "Pérdidas más altas del circuito", "----- kW")
    _, config_vars["refInversoruno"] = crear_fila_variable("refInversoruno", "Referencia inversor 1", "Inversor 150 kW On-Grid.")
    _, config_vars["refInversordos"] = crear_fila_variable("refInversordos", "Referencia inversor 2", "Inversor XX kW On-Grid.")
    _, config_vars["refInversortres"] = crear_fila_variable("refInversortres", "Referencia inversor 3", "Inversor XX kW On-Grid.")
    _, config_vars["Inversoruno"] = crear_fila_variable("Inversoruno", "Inversor 1", "Growat MAX 150KTL3-X2MV")
    _, config_vars["Inversordos"] = crear_fila_variable("Inversordos", "Inversor 2", "Huawei Sun2000 50KTL-M3")
    _, config_vars["Inversortres"] = crear_fila_variable("Inversortres", "Inversor 3", "Huawei Sun2000 40KTL-M3")
    _, config_vars["cantidadInversoruno"] = crear_fila_variable("cantidadInversoruno", "Cantidad inversor 1", "6 Und.")
    _, config_vars["cantidadInversordos"] = crear_fila_variable("cantidadInversordos", "Cantidad inversor 2", "1 Und.")
    _, config_vars["cantidadInversortres"] = crear_fila_variable("cantidadInversortres", "Cantidad inversor 3", "1 Und.")
    _, config_vars["generacionaprobada"] = crear_fila_variable("generacionaprobada", "Generación ya aprobada en la SE", "900kW")
    _, config_vars["potenciaminima"] = crear_fila_variable("potenciaminima", "Demanda mínima del circuito", "90 kW")
    _, config_vars["recoCTO"] = crear_fila_variable("recoCTO", "Protección del OR aguas arriba", "211-11")
    _, config_vars["tipoproteccion"] = crear_fila_variable("tipoproteccion", "Tipo de elemento que protege", "Reconectador")
    _, config_vars["recocabecera"] = crear_fila_variable("recocabecera", "Protección del OR cabecera", "")

    return config_vars