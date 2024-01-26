import pandas as pd
import numpy as np


df = pd.read_csv("./csv_clean.csv")
df = df.drop('Unnamed: 0', axis=1)

#le playtime de minutes en heures
df["Average playtime forever"] = df["Average playtime forever"] / 60
df["Average playtime two weeks"] = df["Average playtime two weeks"] / 60
df["Median playtime forever"] = df["Median playtime forever"] / 60
df["Median playtime two weeks"] = df["Median playtime two weeks"] / 60

#On charge le df des users
df2 = pd.read_csv("./steam-200k.csv", names=["UserID", "Game", "purchase/play", "Heure_jouee", "0"])

#On garde que les lignes "play" car purchase sert a rien
df2 = df2.drop(df2[df2["purchase/play"] == "purchase"].index)
df2.drop(columns =['0'],inplace =True)

#On enlève des caractères spéciaux pour préparer le merge sur le nom des jeux
df['Name'] = df['Name'].str.replace(':','')
df['Name'] = df['Name'].str.replace('®','')
df['Name'] = df['Name'].str.replace('™','')
#En particulier pour Resident Evil (~150 lignes en +)
df2['Game'] = df2['Game'].str.replace(' / Biohazard 6','')
df2['Game'] = df2['Game'].str.replace(' / biohazard HD REMASTER','')
df2['Game'] = df2['Game'].str.replace(' / Biohazard 5','')
df2['Game'] = df2['Game'].str.replace(' / biohazard 4','')
df2['Game'] = df2['Game'].str.replace(' / Biohazard Revelations 2','')
df2['Game'] = df2['Game'].str.replace(' / Biohazard Revelations','')

#On merge les deux datasets par rapport au nom du jeu
df_clean = df2.merge(df, right_on="Name", left_on="Game")
df_clean.drop(columns="Name", inplace =True)
#56789 lignes en commun

#On calcule un score de user en fonction de son temps de jeu par rapport au temps de jeu moyen de tous les users
condition = [
    df_clean['Heure_jouee'].astype('float')>= (df_clean["Median playtime forever"]),
   (df_clean['Heure_jouee'].astype('float')>=0.9*df_clean["Median playtime forever"])&(df_clean['Heure_jouee'].astype('float')<1*df_clean["Median playtime forever"]),
   (df_clean['Heure_jouee'].astype('float')>=0.8*df_clean["Median playtime forever"])&(df_clean['Heure_jouee'].astype('float')<0.9*df_clean["Median playtime forever"]),
   (df_clean['Heure_jouee'].astype('float')>=0.7*df_clean["Median playtime forever"])&(df_clean['Heure_jouee'].astype('float')<0.8*df_clean["Median playtime forever"]),
   (df_clean['Heure_jouee'].astype('float')>=0.6*df_clean["Median playtime forever"])&(df_clean['Heure_jouee'].astype('float')<0.7*df_clean["Median playtime forever"]),
   (df_clean['Heure_jouee'].astype('float')>=0.5*df_clean["Median playtime forever"])&(df_clean['Heure_jouee'].astype('float')<0.6*df_clean["Median playtime forever"]),
   (df_clean['Heure_jouee'].astype('float')>=0.4*df_clean["Median playtime forever"])&(df_clean['Heure_jouee'].astype('float')<0.5*df_clean["Median playtime forever"]),
   (df_clean['Heure_jouee'].astype('float')>=0.3*df_clean["Median playtime forever"])&(df_clean['Heure_jouee'].astype('float')<0.4*df_clean["Median playtime forever"]),
   (df_clean['Heure_jouee'].astype('float')>=0.2*df_clean["Median playtime forever"])&(df_clean['Heure_jouee'].astype('float')<0.3*df_clean["Median playtime forever"]),
   (df_clean['Heure_jouee'].astype('float')>=0.1*df_clean["Median playtime forever"])&(df_clean['Heure_jouee'].astype('float')<0.2*df_clean["Median playtime forever"]),
    df_clean['Heure_jouee'].astype('float')>=0
]

values = [5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1, 0.5, 0]
df_clean['Score'] = np.select(condition,values)

#On attribue un tag True ou False pour savoir si le jeu est recommandable si le score >= 4
df_clean["Recommandable"] = df_clean['Score'].apply(lambda x: True if x >= 4 else False)

df_clean.to_csv("Dataset.csv")