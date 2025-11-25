import re
import discord
from discord import app_commands
from redbot.core import commands

# Regex to match reddit.com, www.reddit.com, or old.reddit.com
REDDIT_REGEX = re.compile(
    r"(https?://)(www\.|old\.)?reddit\.com([^\s]*)",
    re.IGNORECASE
)

# Regex to match Discord message links
MESSAGE_LINK_REGEX = re.compile(
    r"https://discord.com/channels/\d+/(\d+)/(\d+)"
)


class FixReddit(commands.Cog):
    """Flips reddit.com <-> old.reddit.com URLs."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="fixreddit",
        description="Convert reddit.com → old.reddit.com or old.reddit.com → reddit.com. Accepts direct URL or message link."
    )
    @app_commands.describe(
        url="A reddit.com URL to convert (supports www and old subdomains)",
        message_link="A Discord message link containing a reddit URL"
    )
    async def fixreddit(
        self,
        interaction: discord.Interaction,
        url: str = None,
        message_link: str = None
    ):
        # Defer if fetching messages (might take a moment)
        await interaction.response.defer()

        # -------------------------
        # CASE 1: message link provided
        # -------------------------
        if message_link:
            match = MESSAGE_LINK_REGEX.match(message_link)
            if not match:
                await interaction.followup.send("❌ That is not a valid message link.")
                return

            channel_id, message_id = match.groups()
            if int(channel_id) != interaction.channel.id:
                await interaction.followup.send("❌ The message link must be from this channel.")
                return

            try:
                message = await interaction.channel.fetch_message(int(message_id))
            except discord.NotFound:
                await interaction.followup.send("❌ Message not found.")
                return

            # Extract first reddit link from message
            extracted = None
            for word in message.content.split():
                if REDDIT_REGEX.search(word):
                    extracted = word
                    break

            if not extracted:
                await interaction.followup.send("❌ No reddit link found in that message.")
                return

            url = extracted  # Use extracted reddit URL

        # -------------------------
        # CASE 2: direct URL provided
        # -------------------------
        if not url:
            await interaction.followup.send("❌ You must provide either a reddit URL or a message link.")
            return

        match = REDDIT_REGEX.search(url)
        if not match:
            await interaction.followup.send("❌ That does not look like a reddit.com link.")
            return

        protocol = match.group(1)          # https://
        subdomain = match.group(2) or ""   # www. or old. or None
        rest = match.group(3) or ""        # path after reddit.com

        # Flip old <-> normal
        if subdomain.lower() == "old.":
            new_url = f"{protocol}reddit.com{rest}"
        else:
            new_url = f"{protocol}old.reddit.com{rest}"

        # Send converted URL as followup
        await interaction.followup.send(f"🔗 **Converted:** <{new_url}>")
