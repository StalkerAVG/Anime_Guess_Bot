# Anime_Guess_Bot
Anime_Guess_Bot is a fun Discord bot that lets you play an anime guessing game! It fetches random anime from MyAnimeList (MAL) and matches them with images from Sakugabooru. Compete with your friends and see who’s the true weeb! 🌸

## Features 🚀
- 🎮 **Anime Guessing Game:** Get a random anime image and choose from 4 possible titles.
- 🌐 **MyAnimeList Integration:** Fetches anime info directly from MAL.
- 🖼️ **Sakugabooru Images:** Matches anime with high-quality images.
- 🗂️ **Genre Filtering:** Choose specific genres like action, romance, horror, and more.
- 🕒 **Year Range:** Limit anime suggestions by release year.

## Setup 🛠️

### Prerequisites
- Python 3.8+
- Discord.py
- requests
- aiohttp

### Installation
```bash
# Clone the repository
git clone https://github.com/StalkerAVG/Anime_Guess_Bot
cd Anime_Guess_Bot

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Create a Discord bot and get its token from the [Discord Developer Portal](https://discord.com/developers/applications).
2. Get your MyAnimeList Client ID.
3. Replace placeholders in `disanimebot.py`:
```python
MAL_CLIENT_ID = "your_mal_client_id"
bot.run("your_discord_bot_token")
```

## Usage 🎉
Run the bot:
```bash
python disanimebot.py
```

In Discord, type the following command:
```
/guess_anime [year_from] [year_to] [genre]
```
For example:
```
/guess_anime 2010 2020 action
```
Or just:
```
/guess_anime
```

The bot will post an image and four anime title options — pick the right one before time runs out! 🕒

## Supported Genres 🎭
- action
- adventure
- comedy
- drama
- fantasy
- horror
- mystery
- romance
- sci-fi
- sports
- isekai
- mecha

## Contributing 🤝
Pull requests are welcome! Feel free to submit issues or feature requests.

## License 📝
This project is licensed under the MIT License.

## Acknowledgments 🌸
- [MyAnimeList API](https://myanimelist.net/apiconfig)
- [Sakugabooru](https://www.sakugabooru.com)

Happy guessing! 🎉

