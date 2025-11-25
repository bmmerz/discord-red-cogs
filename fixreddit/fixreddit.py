import re
import discord
from discord import app_commands
from redbot.core import commands


# Matches reddit.com or old.reddit.com URLs
REDDIT_REGEX = re.compile(
    r"(https?://)(www\.|old\.)?reddit\.com([^\s]*)",
    re.IGNORECASE
)

# Matches Discord message links
MESSAGE_LINK_REGEX = re.compile(
    r"https://discord.com/channels/\d+/(\d+)/(\d+)"
)


class FixReddit(commands.Cog):
    """Flips reddit.com <-> old.reddit.com URLs."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="fixreddit",
        description="Convert reddit.com → old.reddit.com or the reverse. Accepts direct URL or message link."
    )
    @app_commands.describe(
        url="A reddit.com or old.reddit.com URL",
        message_link="A link to a message containing a reddit link"
    )
    async def fixreddit(
        self,
        interaction: discord.Interaction,
        url: str = None,
        message_link: str = None
    ):
        await interaction.response.defer()

        # ---------------------------------------------------
        # CASE 1: A message link is provided
        # ---------------------------------------------------
        if message_link:
            match = MESSAGE_LINK_REGEX.match(message_link)
            if not match:
                await interaction.followup.send("❌ That is not a valid message link.")
                return

            channel_id, message_id = match.groups()

            # Ensure link belongs to current channel
            if int(channel_id) != interaction.channel.id:
                await interaction.followup.send(
                    "❌ The message link must be from **this channel**."
                )
                return

            try:
                message = await interaction.channel.fetch_message(int(message_id))
            except discord.NotFound:
                await interaction.followup.send("❌ Message not found.")
                return

            # Extract first reddit link
            extracted = None
            for word in message.content.split():
                if REDDIT_REGEX.match(word):
                    extracted = word
                    break

            if not extracted:
                await interaction.followup.send("❌ No reddit link found in that message.")
                return

            url = extracted  # Use extracted reddit URL

        # ---------------------------------------------------
        # CASE 2: Direct URL provided
        # ---------------------------------------------------
        if not url:
            await interaction.followup.send(
                "❌ You must provide either a reddit URL or a message link."
            )
            return

        match = REDDIT_REGEX.match(url)
        if not match:
            await interaction.followup.send("❌ That does not look like a reddit.com link.")
            return

        protocol = match.group(1)          # https://
        subdomain = match.group(2) or ""   # www. or old. or None
        rest = match.group(4)              # everything after reddit.com

        # Flip old <-> normal
        if subdomain.lower() == "old.":
            new_url = f"{protocol}www.reddit.com{rest}"
        else:
            new_url = f"{protocol}old.reddit.com{rest}"

        await interaction.followup.send(f"🔗 **Converted:** <{new_url}>")
