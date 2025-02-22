import asyncio
import difflib

import discord
from discord.ext import commands
import aiohttp
import random
import string

intents = discord.Intents.default()  # Default intents include basic events
intents.messages = True  # Required for reading messages in text channels
intents.message_content = True  # Required for fetching message content

# Initialize the bot with intents
bot = commands.Bot(command_prefix="/", intents=intents)

# Replace with your MAL client ID
MAL_CLIENT_ID = ""

# Genre Mapping (MAL requires numeric IDs)
GENRE_IDS = {
    "action": 1, "adventure": 2, "comedy": 4, "drama": 8, "fantasy": 10,
    "horror": 14, "mystery": 7, "romance": 22, "sci-fi": 24, "sports": 30, 'hentai': 12,
    "mecha": 18, 'isekai': 62,
}

class GuessAnimeView(discord.ui.View):
    def __init__(self, correct_title, choices):
        super().__init__()
        self.correct_title = correct_title
        self.choices = choices
        self.answered_users = set()  # Track users who already guessed
        self.answered_correctly = False  # Check if someone won
        self.game_message = None

        self.ind = 0
        random.shuffle(self.choices)
        for choice in self.choices:
            self.add_item(GuessButton(choice, choice == correct_title, self, row=self.ind))
            self.ind += 1

        self.restart_button = RestartButton()
        self.restart_button.disabled = True  # Initially disabled
        self.add_item(self.restart_button)

    async def timeout_game(self, ctx):
        await asyncio.sleep(10)  # Wait 20 seconds
        if not self.answered_correctly:  # If no one answered
            for child in self.children:
                if isinstance(child, GuessButton):
                    child.disabled = True
            self.restart_button.disabled = False  # Enable restart button
            if self.game_message:
                await self.game_message.edit(content=f"⏳ **Time is up. Correct was** {self.correct_title}",
                                             view=self)

    async def reveal_answer(self, interaction):
        self.answered_correctly = True
        for child in self.children:
            if isinstance(child, GuessButton):
                child.style = discord.ButtonStyle.green if child.is_correct else discord.ButtonStyle.grey
                child.disabled = True
        self.restart_button.disabled = False  # Enable restart button
        await interaction.message.edit(view=self)

class RestartButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="🔄 again?", style=discord.ButtonStyle.blurple, disabled=True)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔄 again...", ephemeral=False)
        await guess_anime(interaction.message.channel)  # Restart the game

class GuessButton(discord.ui.Button):
    def __init__(self, label, is_correct, parent_view: GuessAnimeView, row):
        super().__init__(label=label, style=discord.ButtonStyle.grey, row=row)  # All buttons start as grey
        self.is_correct = is_correct
        self.parent_view = parent_view  # Store the parent view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.parent_view.answered_users:
            return

        self.parent_view.answered_users.add(interaction.user.id)

        embed = discord.Embed(
            title="🎉 Congrats!",
            description=f"{interaction.user.display_name} guessed right. Right one is **{self.label}**!",
            color=discord.Color.dark_blue()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        if self.is_correct:
            await interaction.response.send_message(embed=embed, ephemeral=False)
            await self.parent_view.reveal_answer(interaction)
        else:
            await interaction.response.send_message("❌ WRONG", ephemeral=True)

async def fetch_anime_from_mal(year_from, year_to, genre=None):
    """
    Fetches a random anime from MyAnimeList API based on ranking.
    """
    url = "https://api.myanimelist.net/v2/anime/ranking"  # Corrected endpoint

    params = {
        "ranking_type": "all",
        "limit": 500,  # Fetch a larger pool to filter from
        "fields": "id,title,main_picture,start_date,genres,popularity"
    }

    # Add genre filter if provided
    if genre:
        genre_id = GENRE_IDS.get(genre.lower())
        if genre_id:
            params["genres"] = genre_id
        else:
            print(f"Invalid genre: {genre}")
            return None

    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {".eyJhdWQiOiI0OTVmMzA5NDA5NmI3YzNjMGY4YjVhMDk0NGIyZGU4YiIsImp0aSI6IjIyNTYwYThmNmNmZjE2NDljOWYwNTIwMDA2MjYxOWRiMjk1OTUxZDRiOTRjY2E0MDc3ZDZkMmNiZjdlZWFmMDE3NjA4MGYyMGMxOTkzODIwIiwiaWF0IjoxNzM4MTc3NTMxLCJuYmYiOjE3MzgxNzc1MzEsImV4cCI6MTc0MDg1NTkzMSwic3ViIjoiMTkzNDg1NDkiLCJzY29wZXMiOltdfQ.mbfrpPlaODjug3TM-7mLuqiYTBBbBZQB7XwZXfFPuQkSJnc5Sr7D3Egd1SEtLFG4QPTP6yeoJsuxRyvV_E_Br4SxYM5ShxMV706F_M_52F_itsdxJisloy4dp7cIHeTJaPBgSH80J8G3AXc6iWmn4hL7m3Nyd9AX3Op5uz7UGnl_Clb3lYnBcgS-aUsJRqe-ncM0SZCw1xm-AgXyMOUrGPKUCUM-227MOA4jD6KK651Iej-TeyrSGHZPC4lSqPEnHxfBaVJIZlfXs8P31b4Sg4MC4zmytqVJJiw-Chnyg2vKt5S1ypaKOg-S1Zop-L7SEFHj_OHJPi-DMninRoTEJA"}"
        }
        async with session.get(url, headers=headers, params=params) as response:
            if response.status != 200:
                print(f"Error {response.status}: {await response.text()}")
                return None

            data = await response.json()
            anime_list = data.get("data", [])

            # Filter results by year range and popularity
            filtered_anime = [
                anime["node"] for anime in anime_list
                if anime["node"].get("start_date") and year_from <= int(anime["node"]["start_date"][:4]) <= year_to
                   and anime["node"].get("popularity") and anime["node"]["popularity"] >= 200
            ]

            # Filter by genre if specified
            if genre:
                genre_id = GENRE_IDS.get(genre.lower())
                if genre_id:
                    filtered_anime = [
                        anime for anime in filtered_anime
                        if any(g["id"] == genre_id for g in anime.get("genres", []))
                    ]
                else:
                    print(f"Invalid genre: {genre}")
                    return None

            return random.choices(filtered_anime, k=4) if filtered_anime else None

async def get_correct_sakugabooru_tag(title):
    """
    Uses Sakugabooru's tag completion API to find the best tag match for the given anime title.
    """
    remover = str.maketrans('','',string.punctuation)
    title = title.translate(remover)
    title_ref = title.split(' ')[0].lower()
    url = "https://www.sakugabooru.com/tag.json"
    params = {"name": title_ref}  # Convert spaces to underscores

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                print(f"Error {response.status}: {await response.text()}")
                return None
            data = await response.json()

            if not data:
                return None

            tag_names = [tag["name"] for tag in data]
            # Get the most relevant tag (first in list)
            best_match = difflib.get_close_matches(title.replace(' ','_').lower(), tag_names, n=1)
            return best_match[0] if best_match else None

async def fetch_image_from_sakugabooru(titles):
    """
    Fetches a random image for the given anime title from SakugaBooru using the correct tag.
    """
    correct_tag = await get_correct_sakugabooru_tag(titles)
    if not correct_tag:
        print(f"No tag found for {titles}")
        return None

    url = "https://www.sakugabooru.com/post.json"
    params = {"tags": correct_tag, "limit": 50}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                print(f"Error {response.status}: {await response.text()}")
                return None
            data = await response.json()
            if not data:
                return None
            return random.choice(data)["preview_url"]

@bot.command()
async def guess_anime(ctx, year_from: int = 2000, year_to: int = 2023, genre: str = None):
    """
    Starts an anime guessing game with 4 options.
    """
    await ctx.send("🔍 **Searching for an anime...**")

    # Get 4 random anime titles
    anime_list = await fetch_anime_from_mal(year_from, year_to, genre)
    if not anime_list:
        await ctx.send("❌ No anime found matching your criteria.")
        return

    correct_anime = anime_list[0]
    choices = [anime["title"] for anime in anime_list]

    # Find a valid image
    image_url = await fetch_image_from_sakugabooru(correct_anime["title"])
    if not image_url:
        # If no image is found, try another anime from the choices
        for anime in anime_list[1:]:
            image_url = await fetch_image_from_sakugabooru(anime["title"])
            if image_url:
                correct_anime = anime
                break
        else:
            await ctx.send("❌ Could not find an image for any of the selected anime.")
            return

    embed = discord.Embed(title="🎮 Guess Anime UwU")
    embed.set_image(url=image_url)

    view = GuessAnimeView(correct_anime["title"], choices)
    game_message = await ctx.send(embed=embed, view=view)
    view.game_message = game_message  # Store bot message reference
    await view.timeout_game(ctx)

bot.run("")
