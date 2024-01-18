from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modèle factice pour la démonstration
# Ici, vous utiliseriez votre propre modèle de machine learning
def run_machine_learning_model(prompt):
    # Placeholder - Exécutez votre modèle sur le prompt
    result = f"Le modèle a reçu le prompt : '{prompt}' et a retourné un résultat."
    return result

class PromptRequest(BaseModel):
    prompt: str

@app.post("/run_model/")
async def run_model(prompt_request: PromptRequest):
    result = run_machine_learning_model(prompt_request.prompt)
    return {"result": result}
