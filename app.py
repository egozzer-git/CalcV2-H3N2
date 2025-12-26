import streamlit as st
import math

# Configuración de la interfaz
st.set_page_config(page_title="PRUEBA: Calculadora Influenza", layout="centered")

# TÍTULO SOLICITADO
st.title("PRUEBA: Calculadora de Riesgo de Contagio Influenza")
st.markdown("---")

# --- ENTRADA DE DATOS: 1. CÁLCULO ESPACIAL ---
st.subheader("1. Dimensiones del Espacio")
col_dim1, col_dim2, col_dim3 = st.columns(3)
with col_dim1:
    largo = st.number_input("Largo (m)", value=5.0, min_value=1.0)
with col_dim2:
    ancho = st.number_input("Ancho (m)", value=4.0, min_value=1.0)
with col_dim3:
    alto = st.number_input("Alto (m)", value=3.0, min_value=1.0)

volumen = largo * ancho * alto
st.info(f"**Volumen Total:** {volumen:.2f} m³")

# --- ENTRADA DE DATOS: 2. VENTILACIÓN Y AMBIENTE ---
st.subheader("2. Condiciones Ambientales y Temporales")
col_env1, col_env2 = st.columns(2)

with col_env1:
    nivel_vent = st.selectbox(
        "Nivel de Ventilación",
        ["Nulo (Aire estancado)", "Bajo (Poca renovación)", "Medio (Estándar)", "Alto (Salud/Filtrado)"]
    )
    temporada = st.radio("Estación del año", ["Invierno", "Verano"])

with col_env2:
    humedad_cat = st.select_slider(
        "Nivel de Humedad",
        options=["Seco", "Media", "Alta", "Muy Alta"],
        value="Media"
    )
    tiempo_exp = st.number_input("Tiempo de estancia (Horas)", value=2.0, min_value=0.5, step=0.5)

# --- ENTRADA DE DATOS: 3. OCUPACIÓN ---
st.subheader("3. Personas")
n_personas = st.number_input("Número total de personas presentes", value=5, min_value=2)

# --- LÓGICA DEL MODELO WELLS-RILEY ---

# A. Mapeo de Ventilación (ACH - Cambios de aire por hora)
ach_map = {
    "Nulo (Aire estancado)": 0.1,
    "Bajo (Poca renovación)": 1.0,
    "Medio (Estándar)": 3.0,
    "Alto (Salud/Filtrado)": 8.0
}
ach = ach_map[nivel_vent]

# B. Mapeo de Decaimiento Biológico (Lambda) por Humedad
lambda_map = {
    "Seco": 0.2,       # Máxima supervivencia del virus
    "Media": 0.6,      # Estándar
    "Alta": 1.1,       # Inactivación rápida
    "Muy Alta": 1.8    # El virus cae/muere rápidamente
}
lambda_bio = lambda_map[humedad_cat]

# C. Factor de Estacionalidad (Carga viral emitida 'q')
if temporada == "Invierno":
    q = 45  # Quanta/h (Mayor emisión/agresividad en pico invernal)
else:
    q = 12  # Quanta/h (Menor carga en verano)

# D. Constantes Fisiológicas
p = 0.52  # Tasa respiratoria promedio (m3/h) para actividad sedentaria
I = 1     # Se asume la presencia de 1 individuo infectado

# E. CÁLCULO DE PROBABILIDAD (Fórmula Maestra)
# Tasa de eliminación total k = Ventilación + Decaimiento Natural
k = ach + lambda_bio
exponente = (I * q * p * tiempo_exp) / (volumen * k)
probabilidad_individual = (1 - math.exp(-exponente)) * 100

# F. CÁLCULO DE CASOS SECUNDARIOS
casos_secundarios = (probabilidad_individual / 100) * (n_personas - 1)

# --- RESULTADOS ---
st.markdown("---")
col_res1, col_res2 = st.columns(2)

with col_res1:
    st.markdown("### Riesgo Individual")
    color_risk = "red" if probabilidad_individual > 20 else "orange" if probabilidad_individual > 5 else "green"
    st.markdown(f"<h2 style='color:{color_risk};'>{probabilidad_individual:.2f}%</h2>", unsafe_allow_html=True)
    st.caption("Riesgo para una persona sana expuesta.")

with col_res2:
    st.markdown("### Casos Secundarios")
    st.markdown(f"<h2>{math.ceil(casos_secundarios)}</h2>", unsafe_allow_html=True)
    st.caption(f"Probables nuevos contagios entre los {n_personas - 1} presentes.")

# --- DETALLES ---
with st.expander("Ver desglose del cálculo"):
    st.write(f"**Tasa de renovación (ACH):** {ach} renovaciones/hora")
    st.write(f"**Tasa de decaimiento biológico:** {lambda_bio}/h (Ajustado por humedad {humedad_cat})")
    st.write(f"**Emisión viral (q):** {q} quanta/h (Ajustado por temporada {temporada})")