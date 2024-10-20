# Pronote Telegram Bot

*This README is also available in [French](README_fr.md).*

A Python-based Telegram bot that interacts with Pronote to provide students and parents with easy access to school information such as grades, homework, and timetables.

**This bot is currently under development and may contain bugs.**

## Features

- **View Grades:** Get your latest grades directly in Telegram.
- **Check Homework:** Receive a list of upcoming homework assignments.
- **View Timetable:** Access your next day's schedule.
- **AI Assistance:** Ask questions to the AI and get help with your homework or have a friendly conversation.
- **Notifications:** Automatic notifications for new grades, upcoming homework, and other important updates.
- **Multi-language Support:** English, French and more.

### Upcoming Features

- **Extend features:** to include additional Pronote functionalities.

## Requirements

- Python 3.8 or higher
- A Telegram account
- A Pronote account

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/SleepInfinity/pronote-telegram-bot.git
   cd pronote-telegram-bot
   ```

2. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables:**

   Create a `.env` file in the root directory of the project with the following variable:

   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   ADMIN_ID=your_telegram_account_id #optional
   TIMEZONE=your_timezone
   POLLING_INTERVAL=300  # default to 5 minutes (300 seconds)
   GOOGLE_API_KEY=your_google_gemini_key
   ```

   - Replace `your_telegram_bot_token` with your actual Telegram bot token.
   If you don't know how to get the bot token you can take a look at [obtain-your-bot-token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)

   - Optionally replace `your_telegram_account_id` with your actual Telegram account ID if you want to enable the broadcast feature.
   To find your telegram account ID you can use this [Bot](https://t.me/WhatChatIDBot).

   - Replace `your_timezone` with your actual location's timezone, default to `UTC`, for france use `Europe/Paris`.
   [Here](https://gist.githubusercontent.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568/raw/daacf0e4496ccc60a36e493f0252b7988bceb143/pytz-time-zones.py) is a list of all supported timezones.

   - The `POLLING_INTERVAL` defines the time interval in seconds for polling the Pronote API for new notifications, with a default value of 300 seconds (5 minutes).

   - Replace `your_google_gemini_key` with your Google Gemini api key if you want to use the AI functionallity. To find the api key take a look at [Get a Gemini API key](https://ai.google.dev/gemini-api/docs/api-key)

4. **Windows Users:**

   If you encounter an ImportError when running the bot on Windows, you may need to install the Visual C++ Redistributable Packages for Visual Studio 2013. Download and install the appropriate version:

   - [vcredist_x64.exe](https://www.microsoft.com/en-us/download/details.aspx?id=40784) if using 64-bit Python.
   - [vcredist_x86.exe](https://www.microsoft.com/en-us/download/details.aspx?id=40784) if using 32-bit Python.
  
   If you are not running the bot on Windows just skip this step.

5. **Run the bot:**

   ```bash
   python main.py
   ```

## Usage

You can either host the bot yourself or use the pre-hosted version available at [t.me/pronote_bot](https://t.me/pronote_bot).

## Commands

Once the bot is running, you can interact with it through Telegram. Use the following commands:

- `/login` - Log in to your Pronote account.
- `/grades` - View your latest grades (after logging in).
- `/homework` - Check your upcoming homework assignments (after logging in).
- `/timetable` - View your next day's timetable (after logging in).
- `/ai <question>` - Ask the AI any question, whether it's about your homework or just to chat.
- `/clear` - Clear the current AI conversation and start a new one.
- `/enable_notifications` - Enable notifications, which will poll Pronote every 5 minutes (configurable via the `POLLING_INTERVAL` environment variable) for updates on new grades or homework.
- `/disable_notifications` - Disable notifications for new grades and homework.
- `/settings` - Bot's Settings.
- `/broadcast` - Broadcast a message to all the bot's users (For admin only).
- `/logout` - Log out from your Pronote account.

## To-Do List

The bot is under active development, and we have a list of upcoming tasks and improvements. You can check the full to-do list in [TODO.md](TODO.md).

## Contributing

If you'd like to contribute to this project, feel free to fork the repository and create a pull request with your changes. You can also open an issue to discuss potential improvements or report bugs.

## Acknowledgments

- [PronotePy](https://github.com/bain3/pronotepy) - Python wrapper for Pronote.
- [TGram](https://github.com/z44d/tgram) - A Python wrapper for the Telegram Bot API.
- [Kvsqlite](https://github.com/AYMENJD/Kvsqlite) - A simple, fast key-value store built on top of SQLite.
