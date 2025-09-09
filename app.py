# app.py - POC Compagnon Vocal Simple
import gradio as gr
import json
import os
from datetime import datetime

class SimpleVoiceCompanion:
    def __init__(self):
        # Mémoire utilisateur simple (fichier JSON local)
        self.memory_file = "user_memory.json"
        self.load_memory()
    
    def load_memory(self):
        """Charge la mémoire depuis fichier JSON"""
        try:
            with open(self.memory_file, 'r') as f:
                self.user_memories = json.load(f)
        except FileNotFoundError:
            self.user_memories = {}
    
    def save_memory(self):
        """Sauvegarde la mémoire dans fichier JSON"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.user_memories, f, indent=2)
    
    def get_user_memory(self, user_id):
        """Récupère mémoire utilisateur"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = {
                "intimacy_level": 1.0,
                "interaction_count": 0,
                "personal_info": {},
                "conversation_history": [],
                "emotional_state": "neutral"
            }
        return self.user_memories[user_id]
    
    def extract_personal_markers(self, text):
        """Extraction simple d'éléments personnels"""
        markers = {
            "nom": ["je m'appelle", "je suis", "mon nom"],
            "humeur": ["je me sens", "je suis triste", "je suis heureux", "je suis content"],
            "activité": ["je travaille", "je fais", "j'étudie"],
            "lieu": ["je vis à", "j'habite", "je suis de"],
            "famille": ["ma famille", "mes parents", "mon mari", "ma femme"],
            "loisirs": ["j'aime", "je pratique", "mon hobby"]
        }
        
        found_info = {}
        text_lower = text.lower()
        
        for category, expressions in markers.items():
            for expr in expressions:
                if expr in text_lower:
                    # Extraire contexte autour de l'expression
                    start = text_lower.find(expr)
                    context = text[start:start+80].strip()
                    found_info[category] = context
                    break
        
        return found_info
    
    def calculate_intimacy_boost(self, text):
        """Calcule augmentation intimité selon contenu"""
        intimacy_triggers = {
            "confidence": ["je te fais confiance", "tu peux m'aider", "j'ai besoin de toi"],
            "personal": ["c'est personnel", "entre nous", "en confidence"],
            "emotional": ["je me sens", "j'ai peur", "je suis inquiet", "ça me rend"],
            "gratitude": ["merci", "tu m'aides", "grâce à toi"],
            "problems": ["j'ai un problème", "je ne sais pas quoi faire", "aide-moi"]
        }
        
        boost = 0.0
        text_lower = text.lower()
        
        for category, triggers in intimacy_triggers.items():
            for trigger in triggers:
                if trigger in text_lower:
                    if category == "confidence":
                        boost += 0.3
                    elif category == "personal":
                        boost += 0.2
                    elif category == "emotional":
                        boost += 0.15
                    elif category == "gratitude":
                        boost += 0.1
                    elif category == "problems":
                        boost += 0.25
                    break
        
        return min(boost, 0.5)  # Max 0.5 points par interaction
    
    def adapt_response_style(self, base_response, intimacy_level, personal_info):
        """Adapte style selon niveau intimité"""
        if intimacy_level <= 1.5:
            # Formel et poli
            response = f"Bonjour ! {base_response}"
            response = response.replace(" tu ", " vous ")
            response = response.replace("Tu ", "Vous ")
        
        elif intimacy_level <= 2.5:
            # Amical mais respectueux
            response = base_response
            if not any(greeting in base_response.lower() for greeting in ["salut", "bonjour", "hello"]):
                response = f"Salut ! {response}"
        
        elif intimacy_level <= 3.5:
            # Familier et chaleureux
            response = base_response
            # Ajouter prénom si connu
            if "nom" in personal_info:
                name = personal_info["nom"].split()[-1]  # Prendre dernier mot comme prénom
                response = f"Salut {name} ! {response}"
            response += " 😊"
        
        elif intimacy_level <= 4.5:
            # Proche et empathique
            empathetic_prefixes = [
                "Je comprends ce que tu ressens... ",
                "Ça me touche que tu me dises ça... ",
                "Je sens que c'est important pour toi... "
            ]
            
            if any(word in base_response.lower() for word in ["triste", "difficile", "problème", "peur"]):
                response = empathetic_prefixes[0] + base_response
            else:
                response = base_response
            
            response += " ❤️"
        
        else:
            # Très intime et complice
            response = base_response
            response += " 💙 Tu sais que tu peux toujours compter sur moi."
        
        return response
    
    def generate_response(self, user_input, user_id):
        """Génère réponse adaptée"""
        memory = self.get_user_memory(user_id)
        
        # Mise à jour compteur interactions
        memory["interaction_count"] += 1
        
        # Extraction infos personnelles
        personal_info = self.extract_personal_markers(user_input)
        memory["personal_info"].update(personal_info)
        
        # Calcul boost intimité
        intimacy_boost = self.calculate_intimacy_boost(user_input)
        memory["intimacy_level"] = min(5.0, memory["intimacy_level"] + intimacy_boost)
        
        # Progression naturelle avec interactions
        if memory["interaction_count"] % 5 == 0:
            memory["intimacy_level"] = min(5.0, memory["intimacy_level"] + 0.1)
        
        # Génération réponse de base (simulation simple)
        base_response = self.generate_base_response(user_input, memory)
        
        # Adaptation style
        final_response = self.adapt_response_style(
            base_response, 
            memory["intimacy_level"], 
            memory["personal_info"]
        )
        
        # Sauvegarde conversation
        memory["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": final_response,
            "intimacy_level": memory["intimacy_level"]
        })
        
        # Garder seulement les 10 dernières conversations
        if len(memory["conversation_history"]) > 10:
            memory["conversation_history"] = memory["conversation_history"][-10:]
        
        self.save_memory()
        
        return final_response, memory["intimacy_level"]
    
    def generate_base_response(self, user_input, memory):
        """Génération réponse de base (simulation - à remplacer par vraie IA)"""
        # Réponses selon niveau intimité et contenu
        intimacy = memory["intimacy_level"]
        
        # Détection intention basique
        input_lower = user_input.lower()
        
        if any(greeting in input_lower for greeting in ["bonjour", "salut", "hello", "coucou"]):
            if intimacy <= 1.5:
                return "Comment puis-je vous aider aujourd'hui ?"
            elif intimacy <= 3:
                return "Comment ça va ? Quoi de neuf ?"
            else:
                return "Hey ! Content de te revoir ! Comment tu te sens aujourd'hui ?"
        
        elif any(word in input_lower for word in ["triste", "déprimé", "mal", "difficile"]):
            if intimacy <= 2:
                return "Je suis désolé d'apprendre que vous traversez une période difficile."
            elif intimacy <= 3.5:
                return "Oh non, ça me fait de la peine de savoir que tu ne vas pas bien. Tu veux en parler ?"
            else:
                return "Mon cœur se serre de te voir comme ça... Je suis là pour toi. Dis-moi tout."
        
        elif any(word in input_lower for word in ["heureux", "content", "joie", "super", "génial"]):
            if intimacy <= 2:
                return "C'est merveilleux d'entendre que tout va bien pour vous !"
            elif intimacy <= 3.5:
                return "Ça me fait plaisir de te voir si heureux ! Raconte-moi !"
            else:
                return "Ton bonheur fait chaud au cœur ! J'adore te voir rayonner comme ça !"
        
        elif any(word in input_lower for word in ["merci", "remercie"]):
            if intimacy <= 2:
                return "Je vous en prie, c'est avec plaisir que je vous aide."
            elif intimacy <= 3.5:
                return "De rien ! C'est normal, on est là pour s'entraider !"
            else:
                return "Ça me touche que tu me remercies... Notre amitié compte tellement pour moi !"
        
        else:
            # Réponse générique adaptée
            if intimacy <= 1.5:
                return "C'est intéressant ce que vous me dites. Pouvez-vous m'en dire davantage ?"
            elif intimacy <= 3:
                return "Ah je vois ! Dis-moi en plus, ça m'intéresse."
            else:
                return "J'écoute avec attention... Continue, tu sais que je suis toujours là pour toi."

# Instance globale
companion = SimpleVoiceCompanion()

def process_conversation(message, chat_history, user_id):
    """Traite la conversation"""
    if not message.strip():
        return chat_history, "Veuillez entrer un message", ""
    
    # Génération réponse
    response, intimacy_level = companion.generate_response(message, user_id)
    
    # Mise à jour historique
    chat_history.append([message, response])
    
    # Info intimité
    intimacy_info = f"Niveau intimité: {intimacy_level:.1f}/5.0"
    if intimacy_level <= 1.5:
        intimacy_info += " (Formel)"
    elif intimacy_level <= 2.5:
        intimacy_info += " (Amical)"
    elif intimacy_level <= 3.5:
        intimacy_info += " (Familier)"
    elif intimacy_level <= 4.5:
        intimacy_info += " (Proche)"
    else:
        intimacy_info += " (Très intime)"
    
    return chat_history, intimacy_info, ""

def reset_conversation(user_id):
    """Reset conversation pour un utilisateur"""
    if user_id in companion.user_memories:
        del companion.user_memories[user_id]
        companion.save_memory()
    return [], "Niveau intimité: 1.0/5.0 (Formel)"

# Interface Gradio
with gr.Blocks(
    title="Compagnon Vocal Intime - POC", 
    theme=gr.themes.Soft()
) as demo:
    
    gr.Markdown("""
    # 🤖💙 Compagnon Vocal Intime - POC
    
    **Démonstration d'un assistant qui développe une relation personnelle**
    
    ✨ **Testez l'évolution de l'intimité :**
    - Commencez par un simple "Bonjour"
    - Partagez des informations personnelles
    - Exprimez des émotions
    - Observez comment le ton s'adapte !
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            # Zone de chat principale
            chatbot = gr.Chatbot(
                label="💬 Conversation",
                height=500,
                show_label=True,
                placeholder="La conversation apparaîtra ici...",
                type="messages"
            )
            
            # Indicateur niveau intimité
            intimacy_display = gr.Textbox(
                label="📊 Niveau de relation",
                value="Niveau intimité: 1.0/5.0 (Formel)",
                interactive=False,
                max_lines=1
            )
        
        with gr.Column(scale=1):
            # Contrôles utilisateur
            gr.Markdown("### 👤 Paramètres")
            
            user_id = gr.Textbox(
                label="ID Utilisateur",
                value="demo_user",
                placeholder="votre_nom",
                info="Pour tester plusieurs profils"
            )
            
            gr.Markdown("### 💭 Suggestions de test")
            gr.Markdown("""
            **Progression naturelle :**
            1. "Bonjour !"
            2. "Je m'appelle Marie"
            3. "Je me sens un peu triste aujourd'hui"
            4. "Merci de m'écouter"
            5. "Je te fais confiance"
            
            **Observez l'évolution du ton !**
            """)
    
    # Zone de saisie
    with gr.Row():
        with gr.Column(scale=4):
            message_input = gr.Textbox(
                label="✍️ Votre message",
                placeholder="Tapez votre message ici...",
                lines=2
            )
        
        with gr.Column(scale=1):
            send_btn = gr.Button("📤 Envoyer", variant="primary", size="lg")
            clear_btn = gr.Button("🗑️ Reset", variant="secondary")
    
    # Événements
    send_btn.click(
        fn=process_conversation,
        inputs=[message_input, chatbot, user_id],
        outputs=[chatbot, intimacy_display, message_input]
    )
    
    message_input.submit(
        fn=process_conversation,
        inputs=[message_input, chatbot, user_id],
        outputs=[chatbot, intimacy_display, message_input]
    )
    
    clear_btn.click(
        fn=lambda uid: reset_conversation(uid),
        inputs=[user_id],
        outputs=[chatbot, intimacy_display]
    )

# Lancement application
if __name__ == "__main__":
    demo.launch(
        debug=True,
        share=False  # True pour URL publique temporaire
    )