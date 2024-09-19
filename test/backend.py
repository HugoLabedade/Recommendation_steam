from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util
import torch
import jwt
import pandas as pd

app = FastAPI()

# Configuration de l'authentification
SECRET_KEY = "votre_clé_secrète_ici"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Structure de données en mémoire pour stocker les utilisateurs, les amitiés et les favoris
users: Dict[str, Dict] = {}
friendships: Dict[str, List[str]] = {}
favorites: Dict[str, List[Dict]] = {}

# Modèles de données
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class RecommendRequest(BaseModel):
    query: str

class Game(BaseModel):
    title: str
    description: str

# Configuration de la sécurité
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fonctions utilitaires
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    return users.get(username)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user['hashed_password']):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/register", response_model=UserOut)
def register(user: UserCreate):
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    users[user.username] = {"username": user.username, "hashed_password": hashed_password}
    friendships[user.username] = []
    favorites[user.username] = []
    return UserOut(username=user.username)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/add_friend/{friend_username}")
async def add_friend(friend_username: str, current_user: dict = Depends(get_current_user)):
    if friend_username not in users:
        raise HTTPException(status_code=404, detail="User not found")
    if friend_username in friendships[current_user['username']]:
        raise HTTPException(status_code=400, detail="Already friends")
    friendships[current_user['username']].append(friend_username)
    return {"message": f"Friend {friend_username} added successfully"}

@app.get("/friends", response_model=List[UserOut])
async def get_friends(current_user: dict = Depends(get_current_user)):
    return [UserOut(username=friend) for friend in friendships[current_user['username']]]

@app.post("/add_favorite")
async def add_favorite(game: Game, current_user: dict = Depends(get_current_user)):
    favorites[current_user['username']].append(game.dict())
    return {"message": f"Le jeu {game.title} a été ajouté à vos favoris"}

@app.get("/favorites", response_model=List[Game])
async def get_favorites(current_user: dict = Depends(get_current_user)):
    return favorites[current_user['username']]

# # Chargement du modèle Sentence Transformer
# model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# # Charger et préparer les données (à remplacer par votre propre base de données de jeux)
# games_df = pd.DataFrame({
#     'title': ['The Witcher 3', 'Minecraft', 'FIFA 22', 'Doom Eternal', 'Stardew Valley', 'Zelda: Breath of the Wild'],
#     'description': [
#         'Action RPG médiéval fantastique avec un monde ouvert',
#         'Jeu de survie et de construction en monde ouvert',
#         'Simulation de football réaliste',
#         'FPS rapide et brutal dans un univers futuriste',
#         'Jeu de simulation de ferme et de vie rurale',
#         'Jeu d\'aventure en monde ouvert avec des énigmes et de l\'exploration'
#     ]
# })

# # Encoder les descriptions de jeux
# games_embeddings = model.encode(games_df['description'].tolist(), convert_to_tensor=True)

# class Query(BaseModel):
#     query: str

# @app.post("/recommend")
# async def recommend_games(query: Query):
#     # Encoder la requête de l'utilisateur
#     query_embedding = model.encode(query.query, convert_to_tensor=True)
    
#     # Calculer la similarité cosinus
#     cos_scores = util.cos_sim(query_embedding, games_embeddings)[0]
    
#     # Trier les jeux par similarité
#     top_results = torch.topk(cos_scores, k=len(games_df))
    
#     recommended_games = [
#         {
#             'title': games_df.iloc[idx.item()]['title'],
#             'description': games_df.iloc[idx.item()]['description'],
#             'score': score.item()
#         }
#         for score, idx in zip(top_results.values, top_results.indices)
#     ]
    
#     return {"recommended_games": recommended_games}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# Chargement du modèle Sentence Transformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Chargement des données de jeux depuis cleangames.csv
df = pd.read_csv('cleangames.csv')
games = df[['name', 'summary']].to_dict('records')

# Encodage des descriptions de jeux
games_embeddings = model.encode([game['summary'] for game in games], convert_to_tensor=True)

@app.post("/recommend")
async def recommend_games(request: RecommendRequest, current_user: dict = Depends(get_current_user)):
    query_embedding = model.encode(request.query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, games_embeddings)[0]
    top_results = torch.topk(cos_scores, k=min(10, len(games)))  # Limite à 10 recommandations maximum
    
    recommended_games = [
        {
            "title": games[idx]['name'],
            "description": games[idx]['summary'],
            "score": score.item()
        }
        for score, idx in zip(top_results.values, top_results.indices)
    ]
    
    return {"recommended_games": recommended_games}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)