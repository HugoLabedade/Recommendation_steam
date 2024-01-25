import pandas as pd
import numpy as np


df = pd.read_csv("./csv_clean.csv")
df = df.drop('Unnamed: 0', axis=1)

#le playtime de minutes en heures
def min_heure(nom_dataset, colonne):
    nom_dataset[colonne] = nom_dataset[colonne] / 60
min_heure(df, "Average playtime forever")
min_heure(df, "Average playtime two weeks")
min_heure(df, "Median playtime forever")
min_heure(df, "Median playtime two weeks")


#On charge le df des users
df2 = pd.read_csv("./steam-200k.csv", names=["UserID", "Game", "purchase/play", "Heure_jouee", "0"])

def supprimer_colonne(nom_dataset, colonne):
    nom_dataset = nom_dataset.drop(columns=colonne,inplace = True)

#On garde que les lignes "play" car purchase sert a rien
# df2 = df2.drop(df2[df2["purchase/play"] == "purchase"].index)
supprimer_colonne(df2,'0')

#On enlève des caractères spéciaux pour préparer le merge sur le nom des jeux
def remplacement(nom_dataset, colonne, element):
    nom_dataset[colonne] = nom_dataset[colonne].str.replace(element,'')
remplacement(df, 'Name', ':')
remplacement(df, 'Name', '®')
remplacement(df, 'Name', '™')
#En particulier pour Resident Evil (~150 lignes en +)
remplacement(df2, 'Game', ' / Biohazard 6')
remplacement(df2, 'Game', ' / biohazard HD REMASTER')
remplacement(df2, 'Game', ' / Biohazard 5')
remplacement(df2, 'Game', ' / biohazard 4')
remplacement(df2, 'Game', ' / Biohazard 6')
remplacement(df2, 'Game', ' / Biohazard Revelations 2')
remplacement(df2, 'Game', ' / Biohazard Revelations')

#On merge les deux datasets par rapport au nom du jeu
df_clean = df2.merge(df, right_on="Name", left_on="Game")
supprimer_colonne(df_clean, "Name")
#56789 lignes en commun



#On calcule un score de user en fonction de son temps de jeu par rapport au temps de jeu moyen de tous les users
heure = "Heure_jouee"
temps = "Average playtime forever"
condition = [
    df_clean[heure]>= (df_clean[temps]),
   (df_clean[heure]>=0.9*df_clean[temps])&(df_clean[heure]<0.9*df_clean[temps]),
   (df_clean[heure]>=0.8*df_clean[temps])&(df_clean[heure]<0.8*df_clean[temps]),
   (df_clean[heure]>=0.7*df_clean[temps])&(df_clean[heure]<0.7*df_clean[temps]),
   (df_clean[heure]>=0.6*df_clean[temps])&(df_clean[heure]<0.6*df_clean[temps]),
   (df_clean[heure]>=0.5*df_clean[temps])&(df_clean[heure]<0.5*df_clean[temps]),
   (df_clean[heure]>=0.4*df_clean[temps])&(df_clean[heure]<0.4*df_clean[temps]),
   (df_clean[heure]>=0.3*df_clean[temps])&(df_clean[heure]<0.3*df_clean[temps]),
   (df_clean[heure]>=0.2*df_clean[temps])&(df_clean[heure]<0.2*df_clean[temps]),
   (df_clean[heure]>=0.1*df_clean[temps])&(df_clean[heure]<0.1*df_clean[temps]),
    df_clean[heure]>=0
    
]
values = [5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1, 0.5, 0]
df_clean['Score'] = np.select(condition,values)

df_clean.to_csv("Dataset.csv")
