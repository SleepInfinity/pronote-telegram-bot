# Pronote Telegram Bot

A Python-based Telegram bot that interacts with Pronote to provide students and parents with easy access to school information such as grades, homework, and timetables.

**This bot is currently under development and may contain bugs.**

## Features

- **View Grades:** Get your latest grades directly in Telegram.
- **Check Homework:** Receive a list of upcoming homework assignments.
- **View Timetable:** Access your next day's schedule.

### Upcoming Features

- **Notifications:** Automatic notifications for new grades, upcoming deadlines, and other important updates.
- **Multi-language Support:** English and French, with more languages to be added.

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
   ```

   Replace `your_telegram_bot_token` with your actual Telegram bot token.
   If you don't know how to get the bot token you can take a look at [obtain-your-bot-token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)

4. **Windows Users:**

   If you encounter an ImportError when running the bot on Windows, you may need to install the Visual C++ Redistributable Packages for Visual Studio 2013. Download and install the appropriate version:

   - [vcredist_x64.exe](https://www.microsoft.com/en-us/download/details.aspx?id=40784) if using 64-bit Python.
   - [vcredist_x86.exe](https://www.microsoft.com/en-us/download/details.aspx?id=40784) if using 32-bit Python.
  
   If you are not running the bot on Windows just skip this step.

6. **Run the bot:**

   ```bash
   python main.py
   ```

## Usage

Once the bot is running, you can interact with it through Telegram. Use the following commands:

- `/login` - Log in to your Pronote account.
- `/grades` - View your latest grades (after logging in).
- `/homework` - Check your upcoming homework assignments (after logging in).
- `/timetable` - View your next day's timetable (after logging in).
- `/logout` - Log out from your Pronote account.

## To-Do List

- [ ] Add notifications for grades, homework, and schedules.
- [x] Implement multi-language support (English, French, and more).
- [ ] Extend features to include additional Pronote functionalities.
- [ ] Clean up the code and spread it into multiple files for more readability and scalability.

## Contributing

If you'd like to contribute to this project, feel free to fork the repository and create a pull request with your changes. You can also open an issue to discuss potential improvements or report bugs.

## Acknowledgments

- [PronotePy](https://github.com/bain3/pronotepy) - Python wrapper for Pronote.
- [telebot/PyTelegramBotApi](https://github.com/eternnoir/pyTelegramBotAPI) - A Python wrapper for the Telegram Bot API.
- [Kvsqlite](https://github.com/AYMENJD/Kvsqlite) - A simple, fast key-value store built on top of SQLite.
