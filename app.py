import json
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import os
import requests

villes_maroc = [
    "Casablanca", "Rabat", "Fès", "Marrakech", "Tanger", "Agadir",
    "Meknès", "Oujda", "Kenitra", "Tétouan", "Safi", "El Jadida",
    "Beni Mellal", "Nador", "Taza", "Khouribga", "Ksar El Kebir"
    # Ajoutez plus de villes si nécessaire
]

# Configuration de la page
st.set_page_config(
    page_title="Mon Application",  # Titre de la page
    page_icon=":rocket:",  # Icône dans l'onglet du navigateur
    layout="wide",  # Disposition large
    initial_sidebar_state="expanded",  # Sidebar ouverte par défaut
)

# Charger les données des fichiers JSON
with open("questions.json", "r") as f:
    questions = json.load(f)

with open("riasec.json", "r") as f:
    riasec_mapping = json.load(f)

with open("riasec_descriptions.json", "r") as f:
    riasec_descriptions = json.load(f)

responses = {}
riasec_scores = {
    "Réaliste": 0,
    "Investigateur": 0,
    "Artiste": 0,
    "Social": 0,
    "Entreprenant": 0,
    "Conventionnel": 0,
}

whatsapp_number = "+212660241204"
whatsapp_message = "Bonjour, j'aimerais en savoir plus!"
whatsapp_link = f"https://wa.me/{whatsapp_number}?text={whatsapp_message}"



def mail_cap(prenom, nom, email, age, ville):
    try:
        sender_email = st.secrets["mail"]["sender_email"]
        sender_password = st.secrets["mail"]["sender_password"]

        receiver_email = sender_email
        subject = "Nouveau contact test Riasec"

        # Construire le corps de l'email en HTML
        body_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                h2 {{
                    color: #2E86C1;
                }}
                ul {{
                    list-style-type: none; /* Supprime les puces */
                    padding: 0;
                }}
                ul li {{
                    margin-bottom: 10px; /* Ajoute un espacement */
                }}
                .info {{
                    margin-top: 20px;
                    padding: 10px;
                    border: 1px solid #ddd;
                    background-color: #f9f9f9;
                }}
            </style>
        </head>
        <body>
            <img src="cid:logo_capstudies" alt="CAPSTUDIES Logo" style="width:200px;height:auto;"/>
            <h2>Bonjour,</h2>
            <p>Voici les informations que vous avez fournies :</p>
            <div class="info">
                <ul>
                    <li><b>Nom :</b> {nom}</li>
                    <li><b>Prénom :</b> {prenom}</li>
                    <li><b>Ville :</b> {ville}</li>
                    <li><b>Email :</b> {mail}</li>
                    <li><b>Âge :</b> {age}</li>
                </ul>
            </div>
            <p>Nous vous remercions pour votre participation.</p>
        </body>
        </html>
        """

        msg = MIMEMultipart(
            "alternative"
        )  # Permet d'inclure à la fois texte brut et HTML
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        # Attacher le contenu HTML
        msg.attach(MIMEText(body_html, "html"))


        # Envoi de l'email via SMTP
        smtp_server = "mail.capstudies.com"
        smtp_port = 587

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(
                sender_email,
                sender_password,
            )
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("E-mail CAP envoyé avec succès.")


    except smtplib.SMTPException as e:
        st.error(f"Erreur SMTP : {e}")
    except KeyError as ke:
        st.error(f"Erreur dans les données d'entrée : {ke}")
    except Exception as e:
        st.error(f"Erreur inattendue : {e}")




def envoi_resultats(prenom, mail, riasec_scores, riasec_descriptions, graph_fig):
    try:
        sender_email = st.secrets["mail"]["sender_email"]
        sender_password = st.secrets["mail"]["sender_password"]

        receiver_email = mail
        subject = "Résultats de votre test RIASEC avec CAPSTUDIES"

        logo_url = (
            "https://www.capstudies.com/wp-content/uploads/2020/10/logo-site-web-1.png"
        )
        logo_path = "capstudies_logo.png"
        with open(logo_path, "wb") as f:
            f.write(requests.get(logo_url).content)

        # Construire le corps de l'email en HTML
        body_html = f"""
                <html>
                <head>
                    <style>
                ul {{
                    list-style-type: none; /* Supprime les puces */
                    padding: 0;
                }}
                li {{
                    margin-bottom: 10px; /* Ajoute un espacement */
                }}
                    b {{
                    font-size: 18px; /* Change la taille de la police */
                    font-weight: bold; /* Assure que le texte est en gras */
                }}
                    i {{
                    font-size: 12px; /* Change la taille de la police */
                    font-weight: bold; /* Assure que le texte est en gras */
                }}
                    </style>
                </head>
                <body>
                    <img src="cid:logo_capstudies" alt="CAPSTUDIES Logo" style="width:200px;height:auto;"/>
                    <h2>Bonjour {prenom},</h2>
                    <h2>Voici les résultats de votre test RIASEC :</h2>
                    <ul>
                """
        for riasec_type, percentage in riasec_scores:
            prc_reponses = f"{int(percentage)}%"
            description = riasec_descriptions[riasec_type]["description"].format(
                prc_reponses=prc_reponses
            )
            body_html += f"""
                    <li>
                        <br><br>
                        <b>{riasec_type}</b> : {prc_reponses}<br>
                        {description}<br>
                        <br>
                        <i>Métiers correspondants :</i>
                        <br>
                        <ul>
                """
            for metier in riasec_descriptions[riasec_type]["metiers"]:
                body_html += f"<li>{metier}</li>"
            body_html += "</ul></li>"

        body_html += """    
                 </ul>
                 <p>Vous trouverez ci-joint un graphique récapitulatif de vos résultats.</p>
                 <p>Cordialement,<br>L'équipe CAPSTUDIES</p>
             </body>
             </html>
             """

        body_html = body_html.replace(".", "·")

        # Sauvegarde du graphique avec couleurs
        graph_image_path = "riasec_graph.png"
        pio.write_image(fig, "riasec_graph.png", format="png", width=800, height=600)

        # Préparation du message email
        msg = MIMEMultipart(
            "alternative"
        )  # Permet d'inclure à la fois texte brut et HTML
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        # Attacher le contenu HTML
        msg.attach(MIMEText(body_html, "html"))

        with open(logo_path, "rb") as logo:
            logo_part = MIMEBase("image", "png")
            logo_part.set_payload(logo.read())
            encoders.encode_base64(logo_part)
            logo_part.add_header(
                "Content-Disposition", "inline", filename="capstudies_logo.png"
            )
            logo_part.add_header("Content-ID", "<logo_capstudies>")
            msg.attach(logo_part)

        # Ajouter le graphique en pièce jointe
        with open(graph_image_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(graph_image_path)}",
            )
            msg.attach(part)

        # Envoi de l'email via SMTP
        smtp_server = "mail.capstudies.com"
        smtp_port = 587

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(
                    sender_email,
                    sender_password,
                )
                server.sendmail(sender_email, receiver_email, msg.as_string())
            st.success("E-mail envoyé avec succès.")
        except:
            pass

    except smtplib.SMTPException as e:
        st.error(f"Erreur SMTP : {e}")
    except KeyError as ke:
        st.error(f"Erreur dans les données d'entrée : {ke}")
    except Exception as e:
        st.error(f"Erreur inattendue : {e}")
    finally:
        for file_path in [logo_path, graph_image_path]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as cleanup_error:
                print(
                    f"Erreur lors de la suppression du fichier {file_path} : {cleanup_error}"
                )


# Titre principal avec l'image à gauche
st.markdown(
    """
    <style>
        /* Bandeau fixe en bas */
        .whatsapp-btn-container {
            display: flex;              /* Disposition horizontale des éléments */
            align-items: center;        /* Alignement vertical centré */
            padding: 20px;              /* Espacement interne */
            background-color: #ffffff;  /* Fond blanc */
            box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);  /* Ombre légère */
            z-index: 100;
            position: fixed;
            bottom: 0;
            left: 0;                    /* Le bandeau reste collé au bord gauche */
            width: 100%;                /* Bandeau pleine largeur */
            height: 80px;               /* Hauteur ajustée */
        }

        /* Conteneur du contenu pour décaler logo et texte */
        .whatsapp-content {
            display: flex;              /* Disposition horizontale des éléments */
            align-items: center;        /* Centrer verticalement les éléments */
            margin-left: 660px;         /* Décalage pour éviter la sidebar */
        }

         /* Modifier le fond de la page entière */
        .main {
            background-color: #f2f2f2; /* Fond gris clair */
            padding: 20px; /* Ajout d'un espace autour du contenu principal */
            border-radius: 8px; /* Optionnel : coins arrondis */
        }

        /* Modifier la largeur de la sidebar */
        section[data-testid="stSidebar"] {
            min-width: 250px; /* Largeur minimale sur mobile */
            max-width: 450px; /* Largeur maximale sur desktop */
            display: block;  /* S'assurer qu'elle est affichée correctement */
        }

        .whatsapp-content img {
            width: 50px;                /* Taille du logo */
            height: 50px;
            margin-right: 15px;         /* Espacement entre le logo et le texte */
        }

        .whatsapp-content .whatsapp-text {
            font-size: 16px;            /* Taille du texte */
            color: #25D366;             /* Couleur verte de WhatsApp */
            text-align: left;           /* Alignement du texte à gauche */
        }

        /* Ajustement pour petits écrans */
        @media only screen and (max-width: 600px) {
            .whatsapp-content {
                margin-left: 0;         /* Pas de décalage si la sidebar est masquée */
            }

            .whatsapp-content img {
                width: 40px;            /* Réduction de la taille du logo */
                height: 40px;
            }

            .whatsapp-content .whatsapp-text {
                font-size: 14px;        /* Réduction de la taille du texte */
            }

            /* Réduction de la sidebar à 250px pour mobile */
            section[data-testid="stSidebar"] {
                width: 250px;  /* Réduit la largeur de la sidebar sur mobile */
                display: none; /* Masquer la sidebar sur mobile par défaut */
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Image dans la sidebar
st.sidebar.image(
    "https://www.capstudies.com/wp-content/uploads/2020/10/logo-site-web-1.png",
    width=200,
)

# Description dans la sidebar
st.sidebar.markdown(
    """
    ## Qu'est-ce que le modèle RIASEC ?

    Le modèle RIASEC (ou Hexaco) est un outil d'orientation professionnelle qui classifie les individus selon six grands types de personnalités. Chaque type est associé à un ensemble d'intérêts professionnels et de comportements typiques :

    - **Réaliste** : Préfère les tâches pratiques et concrètes, souvent liées à des activités techniques ou manuelles.
    - **Investigateur** : Aime résoudre des problèmes et analyser des informations, souvent dans des environnements académiques ou scientifiques.
    - **Artiste** : Recherche des opportunités créatives, souvent dans des domaines comme l'art, la musique ou l'écriture.
    - **Social** : Préfère aider et interagir avec les autres, souvent dans des rôles éducatifs, sociaux ou de conseil.
    - **Entreprenant** : Aime influencer et diriger les autres, souvent dans des environnements de vente ou de gestion.
    - **Conventionnel** : Aussi appelé "Conventionnel", préfère des tâches organisées et structurées, souvent liées à la gestion, l'administration ou l'informatique.

    Ce test vous aidera à découvrir quel profil RIASEC correspond le mieux à vos intérêts et à vos compétences professionnelles.
    """,
    unsafe_allow_html=True,
)

# Titre principal
st.title("Test d'Orientation")

# Code pour gérer les questions et afficher les résultats
st.markdown("<br><br>", unsafe_allow_html=True)


def fig_draw():
    labels = [riasec_type for riasec_type, _ in st.session_state["riasec_scores"]]
    values = [percentage for _, percentage in st.session_state["riasec_scores"]]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.3,
                textinfo="label+percent",
                hoverinfo="label+percent",
                marker=dict(
                    colors=[
                        "#636EFA",
                        "#EF553B",
                        "#00CC96",
                        "#AB63FA",
                        "#FFA15A",
                        "#19D3F3",
                    ]
                ),
            )
        ]
    )

    fig.update_layout(
        title="Répartition des types RIASEC",
        annotations=[dict(text="RIASEC", x=0.5, y=0.5, font_size=20, showarrow=False)],
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    return fig


if "user_info" not in st.session_state:
    for question, answers in questions.items():
        st.markdown(
            f"<div style='font-size: 2rem; font-weight: bold; margin-bottom: 5px;'>{question}</div>",
            unsafe_allow_html=True,
        )
        options = [
            answers["reponse 1"],
            answers["reponse 2"],
        ]  # Liste des réponses textuelles
        response = st.radio(
            "label",
            options=options,
            key=question,
            format_func=lambda x: x if x else "Sélectionnez une réponse",
            label_visibility="hidden",
        )
        responses[question] = response
        st.markdown("<br><br>", unsafe_allow_html=True)

    # Bouton de soumission
    if st.button("Soumettre", key="soumettre1"):
        if None in responses.values():
            st.warning("Veuillez répondre à toutes les questions avant de soumettre.")
        else:
            # Réinitialiser les scores RIASEC
            riasec_scores = {key: 0 for key in riasec_scores}

            for question, response in responses.items():
                # Trouver la clé ("reponse 1" ou "reponse 2") associée à la réponse textuelle
                response_key = next(
                    (
                        key
                        for key, value in questions[question].items()
                        if value == response
                    ),
                    None,
                )

                # Récupérer le type RIASEC associé à cette réponse
                if response_key:
                    riasec_type = riasec_mapping[question].get(response_key)
                    if riasec_type:
                        riasec_scores[riasec_type] += 1

            # Calcul des pourcentages RIASEC
            total_responses = sum(riasec_scores.values())
            if total_responses > 0:
                riasec_percentages = {
                    key: (value / total_responses) * 100
                    for key, value in riasec_scores.items()
                }
            else:
                riasec_percentages = {key: 0 for key in riasec_scores}

            # Tri des types RIASEC par pourcentage décroissant
            sorted_riasec = sorted(
                riasec_percentages.items(), key=lambda x: x[1], reverse=True
            )

            # Affichage des résultats
            st.session_state["riasec_scores"] = sorted_riasec
            st.session_state["form_ready"] = True

    # Formulaire de collecte d'informations
    if "form_ready" in st.session_state and st.session_state["form_ready"]:
        st.subheader("Veuillez entrer vos informations personnelles")
        with st.form(key="input_form"):
            nom = st.text_input("Votre nom :")
            prenom = st.text_input("Votre prénom :")
            age = st.text_input("Votre âge :")
            mail = st.text_input("Votre email :")
            ville = st.selectbox("Votre ville :", villes_maroc)
            recevoir_mail = st.radio(
                "recevoir les résultats par email", options=["oui", "non"]
            )
            submit_button = st.form_submit_button("Valider")

            fig = fig_draw()

            if submit_button:
                errors = False

                # Validation de l'âge
                if not age.isdigit() or not (10 <= int(age) <= 99):
                    st.error("Veuillez entrer un âge valide (entre 10 et 99 ans).")
                    errors = True

                # Validation de l'e-mail
                if "@" not in mail or "." not in mail:
                    st.error("Veuillez entrer une adresse e-mail valide.")
                    errors = True

                # Vérification que tous les champs sont remplis
                if not (nom and prenom and age and mail and ville):
                    st.error("Veuillez remplir tous les champs avant de valider.")
                    errors = True

                # Si aucune erreur, poursuivre le traitement
                if not errors:
                    st.session_state["user_info"] = {
                        "nom": nom,
                        "prenom": prenom,
                        "age": age,
                        "mail": mail,
                        "ville": ville,
                    }
                    st.session_state["form_ready"] = False
                    mail_cap(prenom, nom, mail, age, ville)

                    if recevoir_mail == "oui":
                        envoi_resultats(
                            prenom,
                            mail,
                            st.session_state["riasec_scores"],
                            riasec_descriptions,
                            fig,
                        )

    # Afficher les résultats si toutes les étapes sont complétées
if "riasec_scores" in st.session_state and "user_info" in st.session_state:

    st.plotly_chart(fig_draw())

    st.markdown("<br>", unsafe_allow_html=True)
    for riasec_type, percentage in st.session_state["riasec_scores"]:
        prc_reponses = f"{int(percentage):}%"
        description = riasec_descriptions[riasec_type]["description"].format(
            prc_reponses=prc_reponses
        )
        st.markdown(f"### {riasec_type} : {prc_reponses}")
        st.write(description, unsafe_allow_html=True)

        st.markdown(f"#### Métiers correspondants au profil {riasec_type}:")
        for metier in riasec_descriptions[riasec_type]["metiers"]:
            st.markdown(f"- {metier}")

        st.markdown("<br><br>", unsafe_allow_html=True)

        # Bouton "Relancer le test" avec clé unique
    if st.button("Relancer le test", key="button_restart"):
        st.session_state.clear()
        st.rerun()


st.markdown(
    f"""
                            <div class="whatsapp-btn-container">
                                <div class="whatsapp-content">
                                    <a href="{whatsapp_link}" target="_blank">
                                        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp Logo">
                                        <span class="whatsapp-text">Contactez-nous sur WhatsApp</span>
                                    </a>
                                </div>
                            </div>
                            """,
    unsafe_allow_html=True,
)
