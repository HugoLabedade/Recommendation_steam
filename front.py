import requests
import streamlit as st
from streamlit_searchbox import st_searchbox
import pandas as pd
from css import display_image_on_hover

st.set_page_config(layout="wide")

# URL de l'API FastAPI
API_URL = "http://localhost:8000/run_model/"  # Mettez à jour avec votre URL si nécessaire
API_URL2 = "http://localhost:8000/choose_categories/"
API_URL3 = "http://localhost:8000/dataset_catego/"

game_data = pd.read_csv("data/Dataset.csv", usecols=["Game"])
game_data = game_data.drop_duplicates()
game_data = game_data.reset_index(drop=True)

st.markdown("<h1 style='text-align: center; color: white;'>Sur quel jeu voulez-vous une recommandation ?</h1>", unsafe_allow_html=True)
st.header("", divider="rainbow")



model = st.radio("Sélectionner le type de recommandation que vous souhaitez",
                 ["Par catégorie", "Par note des users"], index=None)
if model == "Par note des users":
    def search(searchterm: str) -> list[tuple[str, any]]:
        liste = []
        for i in range(len(game_data[game_data["Game"].str.contains(searchterm, case=False)].values)):
            liste.append(str(game_data[game_data["Game"].str.contains(searchterm, case=False)].values[i])[2:-2])
        return liste

    def render_image(url):
        return f'<img src="{url}" width="150">'

    resultat = st_searchbox(search)
    if st.button("Exécuter le modèle"):
        # Appel à l'API FastAPI avec le prompt saisi par l'utilisateur
        response = requests.post(API_URL, json={"prompt": resultat})

        if response.status_code == 200:
            result = response.json()["result"]
            st.header(f"Si vous avez aimé ce jeu vous allez aimer :sunglasses: :")

            # A list of image urls, sa description et son genre
            url_dict = {
                "Image":[], "Genre":[], "Description":[],"Jeu":[]
            }

            for image in result["Image"]:
                url_dict["Image"].append(result["Image"][image])
                url_dict["Description"].append(result["Description"][image])
                url_dict["Genre"].append(result["Genres"][image])
                url_dict["Jeu"].append(result["Jeux"][image])

            # Create a container for the content that triggers the tooltip on mouseover
            for i, url in enumerate(url_dict["Image"]):
                genre = url_dict["Genre"][i]
                description = url_dict["Description"][i]
                jeu = url_dict["Jeu"][i]
                display_image_on_hover(i, genre, url, description, jeu)

elif model == "Par catégorie":
    st.header("", divider="rainbow")
    response2 = requests.post(API_URL2)
    resultat = response2.json()["result_categorie"]
    rad = st.radio("Choisissez la catégorie:", resultat, index=None)

    if rad != None:
        response45 = requests.post(API_URL3, json={"genre": rad})
        print(response45)
        resultat3 = response45.json()["catego"]
        print(resultat3)
        #print(resultat3)
            #print("CACAAAAAAAAAAAAAAAAAAA")
            #resultat2 = response.json()["df_categorie"]
            #print(resultat2)
            #st.write(resultat2)
