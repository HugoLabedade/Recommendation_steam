import streamlit as st
import requests

API_URL = "http://localhost:8000"

def register(username, password):
    response = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
    return response.json() if response.status_code == 200 else None

def login(username, password):
    response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
    return response.json() if response.status_code == 200 else None

def add_friend(friend_username, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/add_friend/{friend_username}", headers=headers)
    return response.json() if response.status_code == 200 else None

def get_friends(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/friends", headers=headers)
    return response.json() if response.status_code == 200 else None

def recommend_games(query, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/recommend", json={"query": query}, headers=headers)
    return response.json() if response.status_code == 200 else None

def add_favorite(game, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/add_favorite", json=game, headers=headers)
    return response.json() if response.status_code == 200 else None

def get_favorites(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/favorites", headers=headers)
    return response.json() if response.status_code == 200 else None

st.set_page_config(page_title="Recommandation de Jeux IA", page_icon="🎮", layout="wide")

st.title("Trouvez votre prochain jeu préféré avec l'IA 🎮")

# Gestion de l'état de l'utilisateur
if 'token' not in st.session_state:
    st.session_state.token = None

# Interface de connexion/inscription
if not st.session_state.token:
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    
    with tab1:
        st.header("Connexion")
        username = st.text_input("Nom d'utilisateur", key="login_username")
        password = st.text_input("Mot de passe", type="password", key="login_password")
        if st.button("Se connecter"):
            result = login(username, password)
            if result:
                st.session_state.token = result['access_token']
                st.success("Connexion réussie!")
                st.rerun()
            else:
                st.error("Échec de la connexion. Veuillez vérifier vos identifiants.")

    with tab2:
        st.header("Inscription")
        new_username = st.text_input("Nom d'utilisateur", key="register_username")
        new_password = st.text_input("Mot de passe", type="password", key="register_password")
        if st.button("S'inscrire"):
            result = register(new_username, new_password)
            if result:
                st.success("Inscription réussie!")
                # Connexion automatique après inscription
                login_result = login(new_username, new_password)
                if login_result:
                    st.session_state.token = login_result['access_token']
                    st.success("Vous êtes maintenant connecté!")
                    st.rerun()
                else:
                    st.error("Inscription réussie, mais erreur lors de la connexion automatique. Veuillez vous connecter manuellement.")
            else:
                st.error("Échec de l'inscription. Ce nom d'utilisateur est peut-être déjà pris.")

else:
    # Interface principale après connexion
    st.sidebar.success("Connecté avec succès!")
    if st.sidebar.button("Se déconnecter"):
        st.session_state.token = None
        st.rerun()

    # Onglets principaux
    tab1, tab2, tab3 = st.tabs(["Recommandations", "Profil", "Amis"])

    with tab1:
        # Recommandation de jeux
        query = st.text_input("Décrivez le jeu que vous recherchez")

        if st.button("Rechercher"):
            if query:
                recommended_games = recommend_games(query, st.session_state.token)
                if recommended_games:
                    st.subheader("Jeux recommandés:")
                    for i, game in enumerate(recommended_games['recommended_games'], 1):
                        similarity_score = game['score'] * 100  # Convert to percentage
                        with st.expander(f"{i}. {game['title']} (Similarité: {similarity_score:.2f}%)"):
                            st.write(game['description'])
                            st.progress(game['score'])
                            if st.button(f"Ajouter aux favoris", key=f"fav_{i}"):
                                result = add_favorite({"title": game['title'], "description": game['description']}, st.session_state.token)
                                if result:
                                    st.success("Jeu ajouté aux favoris!")
                                else:
                                    st.error("Erreur lors de l'ajout aux favoris.")
                else:
                    st.error("Une erreur s'est produite lors de la récupération des recommandations.")
            else:
                st.warning("Veuillez entrer une description pour obtenir des recommandations.")

    with tab2:
        # Profil utilisateur
        st.header("Votre profil")
        favorites = get_favorites(st.session_state.token)
        if favorites:
            st.subheader("Vos jeux favoris:")
            for i, game in enumerate(favorites, 1):
                st.write(f"{i}. {game['title']}")
                st.write(f"   Description: {game['description']}")
                st.write("---")
        else:
            st.info("Vous n'avez pas encore de jeux favoris.")

    with tab3:
        # Système d'amis
        st.header("Amis")
        new_friend = st.text_input("Ajouter un ami")
        if st.button("Ajouter"):
            result = add_friend(new_friend, st.session_state.token)
            if result:
                st.success("Ami ajouté avec succès!")
            else:
                st.error("Impossible d'ajouter cet ami.")

        friends = get_friends(st.session_state.token)
        if friends:
            st.subheader("Liste d'amis:")
            for friend in friends:
                st.write(f"- {friend['username']}")
        else:
            st.info("Vous n'avez pas encore d'amis.")

st.sidebar.header("À propos")
st.sidebar.info(
    "Cette application utilise un modèle d'intelligence artificielle avancé (Sentence Transformers) "
    "pour recommander des jeux en fonction de votre description. Le modèle comprend le contexte "
    "et la sémantique de votre requête pour fournir des recommandations plus précises."
)