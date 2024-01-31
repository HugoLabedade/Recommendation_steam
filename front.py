import requests
import streamlit as st
from streamlit_searchbox import st_searchbox
import pandas as pd
import wikipedia



# URL de l'API FastAPI
API_URL = "http://localhost:8000/run_model/"  # Mettez à jour avec votre URL si nécessaire

game_data = pd.read_csv("data/Dataset.csv", usecols=["Game"])
game_data = game_data.drop_duplicates()
game_data = game_data.reset_index(drop=True)

st.title("Interface pour le modèle de machine learning")

def search(searchterm: str) -> list[tuple[str, any]]:
    liste = []
    for i in range(len(game_data[game_data["Game"].str.contains(searchterm, case=False)].values)):
        liste.append(str(game_data[game_data["Game"].str.contains(searchterm, case=False)].values[i])[2:-2])
    return liste
 
resultat = st_searchbox(search)

if st.button("Exécuter le modèle"):
    # Appel à l'API FastAPI avec le prompt saisi par l'utilisateur
    response = requests.post(API_URL, json={"prompt": resultat})

    if response.status_code == 200:
        result = response.json()["result"]
        st.dataframe(result, hide_index=True, width=None)
    else:
        st.error("Une erreur s'est produite lors de l'exécution du modèle.")
