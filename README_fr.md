# Bot Telegram Pronote

*Ce fichier README est également disponible en [anglais](README.md).*

Un bot Telegram basé sur Python qui interagit avec Pronote pour fournir aux étudiants et aux parents un accès facile aux informations scolaires telles que les notes, les devoirs et les emplois du temps.

**Ce bot est actuellement en développement et peut contenir des bugs.**

## Fonctionnalités

- **Voir les notes :** Consultez vos dernières notes directement sur Telegram.
- **Consulter les devoirs :** Recevez une liste des devoirs à venir.
- **Voir l'emploi du temps :** Accédez à l'emploi du temps du lendemain.
- **Assistance IA :** posez des questions à l'IA et obtenez de l'aide pour vos devoirs ou ayez une conversation amicale.
- **Notifications :** Notifications automatiques pour les nouvelles notes, les devoirs à venir et d'autres mises à jour importantes.
- **Support multilingue :** Anglais, Français, et plus.

### Fonctionnalités à venir

- **Extension des fonctionnalités :** Ajout d'autres fonctionnalités de Pronote.

## Prérequis

- Python 3.8 ou supérieur
- Un compte Telegram
- Un compte Pronote

## Installation

1. **Cloner le dépôt :**

   ```bash
   git clone https://github.com/SleepInfinity/pronote-telegram-bot.git
   cd pronote-telegram-bot
   ```

2. **Installer les dépendances :**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer les variables d'environnement :**

   Créez un fichier `.env` dans le répertoire racine du projet avec les variables suivantes :

   ```env
   TELEGRAM_TOKEN=votre_token_telegram
   ADMIN_ID=your_telegram_account_id #facultatif
   TIMEZONE=votre_timezone
   POLLING_INTERVAL=300  # valeur par défaut de 5 minutes (300 secondes)
   GOOGLE_API_KEY=your_google_gemini_key
   ```

   - Remplacez `votre_token_telegram` par votre véritable token de bot Telegram.
     Si vous ne savez pas comment obtenir le token de bot, vous pouvez consulter [obtenir votre token de bot](https://core.telegram.org/bots/tutorial#obtain-your-bot-token).

   - Remplacez éventuellement `your_telegram_account_id` par votre identifiant de compte Telegram actuel si vous souhaitez activer la fonctionnalité de diffusion.
     Pour trouver l'identifiant de votre compte Telegram, vous pouvez utiliser ce [Bot](https://t.me/WhatChatIDBot).

   - Remplacez `votre_timezone` par votre fuseau horaire réel, par défaut `UTC`. Pour la France, utilisez `Europe/Paris`.
     Vous pouvez trouver une liste des fuseaux horaires pris en charge [ici](https://gist.githubusercontent.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568/raw/daacf0e4496ccc60a36e493f0252b7988bceb143/pytz-time-zones.py).

   - La variable `POLLING_INTERVAL` définit l'intervalle de temps en secondes pour interroger l'API Pronote pour les nouvelles notifications, avec une valeur par défaut de 300 secondes (5 minutes).

   - Remplacez `your_google_gemini_key` par votre clé API Google Gemini si vous souhaitez utiliser la fonctionnalité d'IA. Pour trouver la clé API, consultez [Obtenir une clé API Gemini](https://ai.google.dev/gemini-api/docs/api-key)

4. **Utilisateurs Windows :**

   Si vous rencontrez une erreur d'importation en exécutant le bot sous Windows, il se peut que vous ayez besoin d'installer le package Visual C++ Redistributable pour Visual Studio 2013. Téléchargez et installez la version appropriée :

   - [vcredist_x64.exe](https://www.microsoft.com/en-us/download/details.aspx?id=40784) si vous utilisez Python 64 bits.
   - [vcredist_x86.exe](https://www.microsoft.com/en-us/download/details.aspx?id=40784) si vous utilisez Python 32 bits.

   Si vous n'utilisez pas Windows, vous pouvez ignorer cette étape.

5. **Exécuter le bot :**

   ```bash
   python main.py
   ```

## Utilisation

Vous pouvez héberger le bot vous-même ou utiliser la version pré-hébergée disponible sur [t.me/pronote_bot](https://t.me/pronote_bot).

## Commandes

Une fois le bot en fonctionnement, vous pouvez interagir avec lui via Telegram en utilisant les commandes suivantes :

- `/login` - Se connecter à votre compte Pronote.
- `/grades` - Voir vos dernières notes (après connexion).
- `/homework` - Consulter vos devoirs à venir (après connexion).
- `/timetable` - Voir l'emploi du temps du lendemain (après connexion).
- `/ai <question>` - Posez n'importe quelle question à l'IA, qu'il s'agisse de vos devoirs ou simplement de discuter.
- `/clear` - Effacez la conversation actuelle de l'IA et démarrez-en une nouvelle.
- `/enable_notifications` - Activer les notifications, le bot interrogera Pronote toutes les 5 minutes (configurable via la variable d'environnement `POLLING_INTERVAL`) pour les mises à jour des nouvelles notes ou devoirs.
- `/disable_notifications` - Désactiver les notifications pour les nouvelles notes et devoirs.
- `/settings` - Paramètres du bot.
- `/broadcast` - Diffuser un message à tous les utilisateurs du bot (pour l'administrateur uniquement).
- `/logout` - Se déconnecter de votre compte Pronote.

## Liste des tâches

Le bot est en cours de développement actif et nous avons une liste de tâches et d'améliorations à venir. Vous pouvez consulter la liste complète des tâches à effectuer dans [TODO.md](TODO.md).

## Contribuer

Si vous souhaitez contribuer à ce projet, n'hésitez pas à forker le dépôt et à créer une pull request avec vos modifications. Vous pouvez également ouvrir une issue pour discuter des améliorations potentielles ou signaler des bugs.

## Remerciements

- [PronotePy](https://github.com/bain3/pronotepy) - Wrapper Python pour Pronote.
- [TGram](https://github.com/z44d/tgram) - Un wrapper Python pour l'API Telegram Bot.
- [Kvsqlite](https://github.com/AYMENJD/Kvsqlite) - Un stockage de valeurs-clés simple et rapide basé sur SQLite.
