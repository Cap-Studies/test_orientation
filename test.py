import json
import streamlit as st

# Charger les questions depuis questions.json
with open("questions.json", "r") as f:
    questions = json.load(f)

# Charger le mapping RIASEC depuis riasec.json
with open("riasec.json", "r") as f:
    riasec_mapping = json.load(f)

# Charger les descriptions RIASEC
with open("riasec_descriptions.json", "r") as f:
    descriptions = json.load(f)

# Variables
responses = {}
riasec_scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}

# Interface utilisateur
st.title("Test d'Orientation RIASEC")

# Collecte des réponses
st.subheader("Répondez aux questions ci-dessous :")
for question, answers in questions.items():
    # Gérer les réponses avec une valeur par défaut vide
    if question not in st.session_state:
        st.session_state[question] = None

    response = st.radio(
        question,
        options=[None] + list(answers.keys()),  # Ajouter une option vide au début
        format_func=lambda x: x if x else "Sélectionnez une réponse",  # Texte pour l'option vide
        key=question,
    )
    responses[question] = response

# Bouton Soumettre
if st.button("Soumettre"):
    # Vérification : Toutes les réponses doivent être cochées
    if None in responses.values():
        st.warning("Veuillez répondre à toutes les questions avant de soumettre.")
    else:
        # Calcul des scores
        for question, response in responses.items():
            riasec_type = riasec_mapping[question][response]
            riasec_scores[riasec_type] += 1

        # Trier les résultats RIASEC
        sorted_riasec = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_riasec = [item[0] for item in sorted_riasec[:4]]  # Prendre les 4 premiers

        # Construire le profil combiné
        profile_combination = "".join(sorted_riasec)

        # Afficher le résultat
        st.subheader("Résultats du test RIASEC")
        if profile_combination in descriptions:
            st.write(descriptions[profile_combination])
        else:
            st.error(f"Aucune description disponible pour le profil : {profile_combination}.")
