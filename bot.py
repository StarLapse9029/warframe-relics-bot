import discord
from discord import app_commands
from dotenv import dotenv_values
import ast

# Load token
token = dotenv_values(".env").get("token")

# Load relic data
r = {}
with open("./clean_data.txt", "r", encoding="utf-8") as fd:
    for line in fd:
        if ":" not in line:
            continue
        x, y = line.split(":", 1)
        try:
            r[x.strip()] = ast.literal_eval(y.strip())
        except Exception:
            continue


# Rarity → Emoji mapping
RARITY_EMOJIS = {
    "Common": "🥉",     # Bronze
    "Uncommon": "🥈",   # Silver
    "Rare": "🥇"        # Gold
}


class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")


client = MyClient()


@client.tree.command(name="relic", description="Look up a relic and see its drops")
@app_commands.describe(name="The name of the relic (example: Lith A1)")
async def relic(interaction: discord.Interaction, name: str):
    relic_name = name.strip().title()

    if relic_name in r:
        data = r[relic_name]

        embed = discord.Embed(
            title=f"Relic {relic_name}",
            color=discord.Color.gold()
        )

        drops = data.get("Drops", [])

        formatted_lines = []

        for drop in drops:
            item = drop.get("Item", "Unknown Item")
            part = drop.get("Part", "")
            rarity = drop.get("Rarity", "Common")

            emoji = RARITY_EMOJIS.get(rarity, "")
            line = f"{emoji} **{item}**: {part} — *{rarity}*"
            formatted_lines.append(line)

        embed.add_field(
            name="Drops",
            value="\n".join(formatted_lines) if formatted_lines else "No drop data available.",
            inline=False
        )

        embed.set_footer(text="Warframe Relic Lookup")

        await interaction.response.send_message(embed=embed)

    else:
        preview = ", ".join(list(r.keys())[:10])

        embed = discord.Embed(
            title="Relic Not Found",
            description=f"Relic **{relic_name}** does not exist.",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Available Relics (preview)",
            value=preview + "..." if preview else "No relic data loaded.",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


if token:
    client.run(token)
else:
    print("No token found in .env file.")
