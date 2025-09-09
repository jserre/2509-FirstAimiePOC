# 🤖💙 Compagnon Vocal Intime - POC

Un prototype de compagnon conversationnel qui développe progressivement une relation personnelle avec l'utilisateur grâce à un système d'intimité adaptatif.

## ✨ Fonctionnalités

- **Système d'intimité progressif** : Le ton s'adapte selon le niveau de confiance (1.0 à 5.0)
- **Extraction d'informations personnelles** : Détection automatique du nom, humeur, activités, etc.
- **Mémoire persistante** : Sauvegarde des interactions et du profil utilisateur
- **Adaptation du style** : Passage du vouvoiement formel au tutoiement intime
- **Interface Gradio** : Interface web simple et intuitive

## 🎯 Niveaux d'intimité

1. **Formel (1.0-1.5)** : Vouvoiement, politesse distante
2. **Amical (1.5-2.5)** : Tutoiement cordial
3. **Familier (2.5-3.5)** : Utilisation du prénom, emojis
4. **Proche (3.5-4.5)** : Empathie marquée, support émotionnel
5. **Très intime (4.5-5.0)** : Complicité profonde, engagement personnel

## 🚀 Utilisation

```bash
pip install -r requirements.txt
python app.py
```

## 💡 Test suggéré

1. "Bonjour !"
2. "Je m'appelle Marie"
3. "Je me sens un peu triste aujourd'hui"
4. "Merci de m'écouter"
5. "Je te fais confiance"

Observez l'évolution du ton et du niveau d'intimité !

## 🔧 Architecture

- `SimpleVoiceCompanion` : Classe principale gérant l'intimité et la mémoire
- `user_memory.json` : Stockage persistant des profils utilisateurs
- Interface Gradio pour l'interaction web

## 📝 Licence

MIT License
