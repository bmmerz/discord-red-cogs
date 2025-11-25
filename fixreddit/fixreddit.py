import re
import discord
from discord import app_commands
from redbot.core import commands

# Robust Reddit URL regex
REDDIT_REGEX = re.compile(
    r"https?://(?:www\.|old\.)?reddit\.com/[^\s<>]+",
    re.IGNORECASE
)

MESSAGE_LINK_REGEX = re.compile(
    r"https://discord.com/channels/\d+/(\d+)/(\d+)"
)

class FixReddit(commands.Cog):
    """Flips reddit.com <-> old.reddit.com URLs."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="fixreddit",
        description="Convert reddit.com <-> old.reddit.com. Accepts direct URL or message link."
    )
    @app_commands.describe(
        url="A reddit.com URL to convert",
        message_link="A Discord message link containing a reddit URL"
    )
    async def fixreddit(self, interaction: discord.Interaction, url: str = None, message_link: str = None):
        await interaction.response.defer()

        # CASE 1: Message link
        if message_link:
            match = MESSAGE_LINK_REGEX.match(message_link)
            if not match:
                await interaction.followup.send("❌ Invalid message link.")
                return

            channel_id, message_id = match.groups()
            if int(channel_id) != interaction.channel.id:
                await interaction.followup.send("❌ Message link must be from this channel.")
                return

            try:
                message = await interaction.channel.fetch_message(int(message_id))
            except discord.NotFound:
                await interaction.followup.send("❌ Message not found.")
                return

            url_match = REDDIT_REGEX.search(message.content)
            if not url_match:
                await interaction.followup.send("❌ No reddit URL found in the message.")
                return

            url = url_match.group(0)

        # CASE 2: Direct URL
        if not url:
            await interaction.followup.send("❌ You must provide a URL or message link.")
            return

        url_match = REDDIT_REGEX.search(url)
        if not url_match:
            await interaction.followup.send("❌ That does not look like a valid reddit URL.")
            return

        url = url_match.group(0)

        # Flip old <-> normal
        if "old.reddit.com" in url.lower():
            new_url = url.lower().replace("old.reddit.com", "reddit.com")
        else:
            new_url = url.lower().replace("www.reddit.com", "old.reddit.com").replace("reddit.com", "old.reddit.com")

        await interaction.followup.send(f"🔗 **Converted:**\n{new_url}")
