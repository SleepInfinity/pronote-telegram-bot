# Pronote Telegram Bot

*This README is also available in [French](README_fr.md).*

A Python-based Telegram bot that interacts with Pronote to provide students and parents with easy access to school information such as grades, homework, and timetables.

**This bot is currently under development and may contain bugs.**

## Features

- **View Grades:** Get your latest grades directly in Telegram.
- **Check Homework:** Receive a list of upcoming homework assignments.
- **View Timetable:** Access your next day's schedule.
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
   TIMEZONE=your_timezone
   POLLING_INTERVAL=300  # default to 5 minutes (300 seconds)
   ```

   - Replace `your_telegram_bot_token` with your actual Telegram bot token.
   If you don't know how to get the bot token you can take a look at [obtain-your-bot-token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)

   - Replace `your_timezone` with your actual location's timezone, default to `UTC`, for france use `Europe/Paris`.
   [Here](https://gist.githubusercontent.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568/raw/daacf0e4496ccc60a36e493f0252b7988bceb143/pytz-time-zones.py) is a list of all supported timezones.

   - The `POLLING_INTERVAL` defines the time interval in seconds for polling the Pronote API for new notifications, with a default value of 300 seconds (5 minutes).

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
- `/enable_notifications` - Enable notifications, which will poll Pronote every 5 minutes (configurable via the `POLLING_INTERVAL` environment variable) for updates on new grades or homework.
- `/disable_notifications` - Disable notifications for new grades and homework.
- `/settings` - Bot's Settings.
- `/logout` - Log out from your Pronote account.

## To-Do List

- [x] Add notifications for grades, homework, and schedules.
- [x] Implement multi-language support (English, French, and more).
- [ ] Extend features to include additional Pronote functionalities.
- [ ] Clean up the code and spread it into multiple files for more readability and scalability.

## Contributing

If you'd like to contribute to this project, feel free to fork the repository and create a pull request with your changes. You can also open an issue to discuss potential improvements or report bugs.

## Acknowledgments

- [PronotePy](https://github.com/bain3/pronotepy) - Python wrapper for Pronote.
- [TGram](https://github.com/z44d/tgram) - A Python wrapper for the Telegram Bot API.
- [Kvsqlite](https://github.com/AYMENJD/Kvsqlite) - A simple, fast key-value store built on top of SQLite.
