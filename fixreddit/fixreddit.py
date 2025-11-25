import re
import discord
from discord import app_commands
from redbot.core import commands

REDDIT_REGEX = re.compile(r"(https?://)(www\.|old\.)?reddit\.com(/[^\s]*)?", re.IGNORECASE)
MESSAGE_LINK_REGEX = re.compile(r"https://discord.com/channels/\d+/(\d+)/(\d+)")

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
        # Defer because we might fetch a message
        await interaction.response.defer()

        # Case 1: message link
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

            # Extract first reddit link
            extracted = None
            for word in message.content.split():
                if REDDIT_REGEX.search(word):
                    extracted = word
                    break
            if not extracted:
                await interaction.followup.send("❌ No reddit link found in message.")
                return

            url = extracted

        # Case 2: direct URL
        if not url:
            await interaction.followup.send("❌ You must provide a URL or message link.")
            return

        match = REDDIT_REGEX.search(url)
        if not match:
            await interaction.followup.send("❌ That is not a valid reddit URL.")
            return

        protocol = match.group(1)
        subdomain = match.group(2) or ""
        rest = match.group(3) or ""

        if subdomain.lower() == "old.":
            new_url = f"{protocol}reddit.com{rest}"
        else:
            new_url = f"{protocol}old.reddit.com{rest}"

        await interaction.followup.send(f"🔗 **Converted:**\n{new_url}")
