from fastapi import FastAPI
from pydantic import BaseModel
#from main_svd import print_similar_games
import numpy as np
import pandas as pd
np.seterr(divide='ignore', invalid='ignore')
app = FastAPI()

# Ouverture des csv
df = pd.read_csv("data/Dataset.csv", usecols=["UserID", "Game", "Score", "GameID"])
game_data = pd.read_csv("data/Dataset.csv", usecols=["GameID", "Game", "Categories", "About the game", "Genres", "Header image"])
game_data = game_data.rename(columns={"About the game": "About_the_game", "Header image": "Header_image"})
game_data = game_data.drop_duplicates()
game_data = game_data.reset_index(drop=True)

ratings_mat = np.ndarray(shape=(np.max(df.GameID.values), np.max(df.UserID.values)))
ratings_mat[df.GameID.values-1, df.UserID.values-1] = df.Score.values

# normalisation de la matrice : on soustrait la moyenne
normalised_mat = ratings_mat - np.asarray([(np.mean(ratings_mat, 1))]).T
# ultérieure normalisation et transposition pour passer à la matrice A "classique"
A = normalised_mat.T / np.sqrt(ratings_mat.shape[0] - 1)
U, S, Vh = np.linalg.svd(A, full_matrices=True)

def top_cosine_similarity(data, game, top_n=5):
    index = game_data[game_data.Game == game].GameID.values[0] # game id starts from 1 in the dataset
    game_row = data[index, :]
    magnitude = np.sqrt(np.einsum('ij, ij -> i', data, data))
    similarity = np.dot(game_row, data.T) / (magnitude[index] * magnitude)
    sort_indexes = np.argsort(-similarity)
    return sort_indexes[1:top_n+1]

# fonction pour imprimer les titres des top 10 games les plus similaires à un jeu donné

def print_similar_games(game_data, game, V):
    
    sliced = V.T[:, :25] # utilisation seulement des K features latentes les plus importantes
    top_indexes = top_cosine_similarity(sliced, game, 5)
    jeu_reco = {"Jeux": [], "Description": [], "Genre": [], "Image": []}
    for id in top_indexes + 1:
        jeu_reco["Jeux"].append(game_data[game_data.GameID == id].Game.values[0])
        jeu_reco["Description"].append(game_data[game_data.GameID == id].About_the_game.values[0])
        jeu_reco["Genre"].append(game_data[game_data.GameID == id].Genres.values[0])
        jeu_reco["Image"].append(game_data[game_data.GameID == id].Header_image.values[0])
    return jeu_reco

# Modèle factice pour la démonstration
# Ici, vous utiliseriez votre propre modèle de machine learning
def run_machine_learning_model(prompt):
    global Vh
    # Placeholder - Exécutez votre modèle sur le prompt
    liste_jeux = print_similar_games(game_data, prompt, Vh)
    result = pd.DataFrame({"Jeux": liste_jeux["Jeux"], "Description": liste_jeux["Description"], "Genres": liste_jeux["Genre"], "Image": liste_jeux["Image"]})
    return result

class PromptRequest(BaseModel):
    prompt: str

@app.post("/run_model/")
async def run_model(prompt_request: PromptRequest):
        result = run_machine_learning_model(prompt_request.prompt)
        return {"result": result}
