# app_with_ai.py - POC Compagnon avec vraie IA
import gradio as gr
import json
import os
from datetime import datetime
import requests
from typing import Optional

class AIVoiceCompanion:
    def __init__(self):
        # Mémoire utilisateur simple (fichier JSON local)
        self.memory_file = "user_memory.json"
        self.load_memory()
        
        # Configuration IA - à modifier selon vos besoins
        self.ai_config = {
            "provider": "huggingface",  # ou "ollama", "openai"
            "model": "microsoft/DialoGPT-medium",
            "api_token": os.getenv("HF_TOKEN"),  # Token Hugging Face
            "base_url": "https://api-inference.huggingface.co/models/"
        }
    
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
        
        return min(boost, 0.5)
    
    def create_context_prompt(self, user_input: str, memory: dict) -> str:
        """Crée le prompt contextuel pour l'IA"""
        intimacy = memory["intimacy_level"]
        personal_info = memory["personal_info"]
        
        # Base du prompt système
        system_prompt = "Tu es un assistant conversationnel empathique et adaptatif. "
        
        # Adaptation selon niveau d'intimité
        if intimacy <= 1.5:
            system_prompt += "Utilise le vouvoiement et reste professionnel mais chaleureux. "
        elif intimacy <= 2.5:
            system_prompt += "Sois amical et utilise le tutoiement avec respect. "
        elif intimacy <= 3.5:
            system_prompt += "Sois familier et chaleureux. "
            if "nom" in personal_info:
                name = personal_info["nom"].split()[-1]
                system_prompt += f"L'utilisateur s'appelle {name}. "
        elif intimacy <= 4.5:
            system_prompt += "Sois proche et empathique. Montre de la compréhension émotionnelle. "
        else:
            system_prompt += "Sois très proche et complice. Cette personne te fait confiance. "
        
        # Ajout contexte personnel
        if personal_info:
            system_prompt += f"Informations personnelles connues: {personal_info}. "
        
        # Historique récent
        if memory["conversation_history"]:
            recent = memory["conversation_history"][-2:]  # 2 derniers échanges
            context = "Contexte récent: "
            for conv in recent:
                context += f"User: {conv['user']} | Assistant: {conv['assistant']} | "
            system_prompt += context
        
        return f"{system_prompt}\n\nRéponds naturellement à: {user_input}"
    
    def query_huggingface_api(self, prompt: str) -> Optional[str]:
        """Interroge l'API Hugging Face"""
        if not self.ai_config["api_token"]:
            return "⚠️ Token Hugging Face manquant. Définir HF_TOKEN dans les variables d'environnement."
        
        headers = {"Authorization": f"Bearer {self.ai_config['api_token']}"}
        
        # Pour DialoGPT et modèles conversationnels
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        try:
            url = f"{self.ai_config['base_url']}{self.ai_config['model']}"
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                else:
                    return str(result)
            else:
                return f"⚠️ Erreur API ({response.status_code}): {response.text}"
        except Exception as e:
            return f"⚠️ Erreur connexion: {str(e)}"
    
    def query_ollama_local(self, prompt: str) -> Optional[str]:
        """Interroge Ollama en local"""
        try:
            payload = {
                "model": "llama2",  # ou autre modèle installé
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate", 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                return f"⚠️ Erreur Ollama: {response.text}"
        except Exception as e:
            return f"⚠️ Ollama non disponible: {str(e)}"
    
    def generate_ai_response(self, prompt: str) -> str:
        """Génère réponse via IA selon configuration"""
        if self.ai_config["provider"] == "huggingface":
            return self.query_huggingface_api(prompt)
        elif self.ai_config["provider"] == "ollama":
            return self.query_ollama_local(prompt)
        else:
            return "⚠️ Fournisseur IA non configuré"
    
    def adapt_response_style(self, ai_response: str, intimacy_level: float, personal_info: dict) -> str:
        """Adapte le style de la réponse IA selon niveau intimité"""
        if not ai_response or ai_response.startswith("⚠️"):
            return ai_response
        
        response = ai_response
        
        if intimacy_level <= 1.5:
            # Assurer vouvoiement si pas présent
            response = response.replace(" tu ", " vous ")
            response = response.replace("Tu ", "Vous ")
        
        elif intimacy_level <= 2.5:
            # Amical mais respectueux - pas de modification nécessaire
            pass
        
        elif intimacy_level <= 3.5:
            # Familier et chaleureux
            if "nom" in personal_info:
                name = personal_info["nom"].split()[-1]
                if name.lower() not in response.lower():
                    response = f"{name}, {response}"
            response += " 😊"
        
        elif intimacy_level <= 4.5:
            # Proche et empathique
            response += " ❤️"
        
        else:
            # Très intime et complice
            response += " 💙"
        
        return response
    
    def generate_response(self, user_input: str, user_id: str):
        """Génère réponse adaptée avec IA"""
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
        
        # Génération prompt contextuel
        context_prompt = self.create_context_prompt(user_input, memory)
        
        # Génération réponse IA
        ai_response = self.generate_ai_response(context_prompt)
        
        # Adaptation style selon intimité
        final_response = self.adapt_response_style(
            ai_response, 
            memory["intimacy_level"], 
            memory["personal_info"]
        )
        
        # Sauvegarde conversation
        memory["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": final_response,
            "intimacy_level": memory["intimacy_level"],
            "ai_raw": ai_response  # Pour debug
        })
        
        # Garder seulement les 10 dernières conversations
        if len(memory["conversation_history"]) > 10:
            memory["conversation_history"] = memory["conversation_history"][-10:]
        
        self.save_memory()
        
        return final_response, memory["intimacy_level"]

# Instance globale
companion = AIVoiceCompanion()

def process_conversation(message, chat_history, user_id, ai_provider):
    """Traite la conversation avec IA"""
    if not message.strip():
        return chat_history, "Veuillez entrer un message", ""
    
    # Mise à jour config IA
    companion.ai_config["provider"] = ai_provider.lower()
    
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
    title="Compagnon IA Intime - POC", 
    theme=gr.themes.Soft()
) as demo:
    
    gr.Markdown("""
    # 🤖💙 Compagnon IA Intime - POC Avancé
    
    **Assistant conversationnel avec vraie IA et adaptation d'intimité**
    
    ✨ **Nouveautés :**
    - Intégration Hugging Face API ou Ollama local
    - Prompts contextuels adaptatifs
    - Système d'intimité conservé
    
    🔧 **Configuration requise :**
    - Pour Hugging Face: définir `HF_TOKEN` en variable d'environnement
    - Pour Ollama: installer et lancer Ollama en local
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            # Zone de chat principale
            chatbot = gr.Chatbot(
                label="💬 Conversation avec IA",
                height=500,
                show_label=True,
                placeholder="La conversation avec IA apparaîtra ici..."
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
            gr.Markdown("### 🤖 Configuration IA")
            
            ai_provider = gr.Dropdown(
                choices=["HuggingFace", "Ollama"],
                value="HuggingFace",
                label="Fournisseur IA",
                info="Choisir le backend IA"
            )
            
            user_id = gr.Textbox(
                label="ID Utilisateur",
                value="demo_user",
                placeholder="votre_nom",
                info="Pour tester plusieurs profils"
            )
            
            gr.Markdown("### 💭 Instructions")
            gr.Markdown("""
            **Pour Hugging Face :**
            1. Créer compte sur hf.co
            2. Générer token d'accès
            3. `export HF_TOKEN=votre_token`
            
            **Pour Ollama :**
            1. Installer Ollama
            2. `ollama pull llama2`
            3. `ollama serve`
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
        inputs=[message_input, chatbot, user_id, ai_provider],
        outputs=[chatbot, intimacy_display, message_input]
    )
    
    message_input.submit(
        fn=process_conversation,
        inputs=[message_input, chatbot, user_id, ai_provider],
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
