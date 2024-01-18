import requests
import streamlit as st

# URL de l'API FastAPI
API_URL = "http://localhost:8000/run_model/"  # Mettez à jour avec votre URL si nécessaire

st.title("Interface pour le modèle de machine learning")

# Saisie du prompt par l'utilisateur
user_input = st.text_area("Entrez votre prompt :")

if st.button("Exécuter le modèle"):
    # Appel à l'API FastAPI avec le prompt saisi par l'utilisateur
    response = requests.post(API_URL, json={"prompt": user_input})

    if response.status_code == 200:
        result = response.json()["result"]
        st.success(f"Résultat du modèle : {result}")
    else:
        st.error("Une erreur s'est produite lors de l'exécution du modèle.")
