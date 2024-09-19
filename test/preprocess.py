import pandas as pd
import re

# Charger le dataset
df = pd.read_csv('gamesIGDB.csv')  # Remplacez par le nom de votre fichier

def nettoyer_texte(texte):
    if pd.isna(texte):
        return ''
    # Supprimer les caractères spéciaux et les chiffres
    texte = re.sub(r'[^a-zA-Z\s]', '', str(texte))
    
    # Convertir en minuscules
    texte = texte.lower()
    
    # Supprimer les espaces multiples
    texte = re.sub(r'\s+', ' ', texte).strip()
    
    return texte

# Afficher le nombre de lignes avant le nettoyage
print(f"Nombre de lignes avant le nettoyage : {len(df)}")

# Appliquer la fonction de nettoyage à la colonne 'summary'
df['summary_clean'] = df['summary'].apply(nettoyer_texte)

# Supprimer les lignes où 'summary_clean' est vide
df = df[df['summary_clean'] != '']

# Réinitialiser l'index
df = df.reset_index(drop=True)

# Remplacer la colonne 'summary' par 'summary_clean'
df['summary'] = df['summary_clean']
df = df.drop('summary_clean', axis=1)

# Afficher le nombre de lignes après le nettoyage
print(f"Nombre de lignes après le nettoyage : {len(df)}")

# Afficher quelques exemples pour vérification
print(df['summary'].head())

# Sauvegarder le dataset nettoyé
df.to_csv('cleangames.csv', index=False)