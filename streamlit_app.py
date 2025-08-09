"""Interfaz Streamlit para el sistema de RRHH.

Esta aplicación actúa únicamente como cliente del backend Flask
expuesto en ``BASE_URL``. No se importan módulos de ``hr_system`` para
evitar dependencias directas y errores de importación.
"""

import streamlit as st
import requests
import streamlit.components.v1 as components

BASE_URL = "http://localhost:5000"

st.title("Sistema de Recursos Humanos")

option = st.sidebar.selectbox(
    "Módulos disponibles",
    (
        "Inicio",
        "Registrar incidencia",
        "Ver incidencias",
        "Calcular nómina",
    ),
)

if option == "Inicio":
    st.write("Seleccione un módulo en la barra lateral para comenzar.")
elif option == "Registrar incidencia":
    st.header("Registrar incidencia")
    worker_id = st.number_input("ID de trabajador", min_value=1, step=1)
    incident_type = st.text_input("Tipo de incidencia")
    description = st.text_area("Descripción")
    if st.button("Enviar"):
        data = {
            "worker_id": int(worker_id),
            "incident_type": incident_type,
            "description": description,
        }
        resp = requests.post(f"{BASE_URL}/incidents/new", data=data)
        if resp.status_code == 200:
            st.success("Incidencia registrada")
        else:
            st.error(f"Error: {resp.text}")
elif option == "Ver incidencias":
    st.header("Listado de incidencias")
    resp = requests.get(f"{BASE_URL}/incidents")
    if resp.status_code == 200:
        components.html(resp.text, height=500, scrolling=True)
    else:
        st.error("No se pudo obtener el listado")
elif option == "Calcular nómina":
    st.header("Cálculo de nómina semanal")
    worker_id = st.number_input("ID de trabajador", min_value=1, step=1)
    week_start = st.date_input("Fecha de inicio de semana")
    if st.button("Calcular"):
        data = {
            "worker_id": int(worker_id),
            "week_start": week_start.isoformat(),
        }
        resp = requests.post(f"{BASE_URL}/payroll/calculate", data=data)
        if resp.status_code == 200:
            components.html(resp.text, height=500, scrolling=True)
        else:
            st.error(f"No se pudo calcular: {resp.text}")
