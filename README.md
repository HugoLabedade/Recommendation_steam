Pour importer Transformers, utiliser la commande suivante ```pip install transformers``` dans votre environnement virtuel.

Installer aussi ```pip install 'transformers[torch]'``` afin de pouvoir faire tourner le modèle en local.

Vérifier que tout est bien installer avec la commande suivante ```python -c "from transformers import pipeline; print(pipeline('sentiment-analysis')('we love you'))"```

La sortie devrait être ```[{'label': 'POSITIVE', 'score': 0.9998704195022583}]```