import re
import discord
from redbot.core import commands, app_commands

# Regex for Reddit URLs
REDDIT_REGEX = re.compile(
    r"https?://(?:www\.|old\.)?reddit\.com/[^\s<>]+",
    re.IGNORECASE
)

# Discord message link
MESSAGE_LINK_REGEX = re.compile(
    r"https://discord.com/channels/\d+/(\d+)/(\d+)"
)


class FixReddit(commands.Cog):
    """Flips reddit.com ↔ old.reddit.com URLs from Discord messages."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fixreddit", description="Flip reddit.com ↔ old.reddit.com for all Reddit links in a Discord message.")
    async def fixreddit(self, interaction: discord.Interaction, message_link: str):
        """
        Flip reddit.com ↔ old.reddit.com for all Reddit links in a Discord message.
        Usage:
        /fixreddit <Discord message link>
        """
        message_link = message_link.strip()
        match = MESSAGE_LINK_REGEX.match(message_link)
        if not match:
            await interaction.response.send_message("❌ Invalid Discord message link.")
            return

        channel_id, message_id = match.groups()
        if int(channel_id) != interaction.channel.id:
            await interaction.response.send_message("❌ Message link must be from this channel.")
            return

        try:
            message = await interaction.channel.fetch_message(int(message_id))
        except Exception:
            await interaction.response.send_message("❌ Could not fetch the message.")
            return

        # Find all Reddit URLs
        urls = [m.group(0) for m in REDDIT_REGEX.finditer(message.content)]
        if not urls:
            await interaction.response.send_message("❌ No Reddit URLs found in that message.")
            return

        # Flip URLs correctly
        converted_urls = []
        for url in urls:
            url_lower = url.lower()
            if "old.reddit.com" in url_lower:
                new_url = url_lower.replace("old.reddit.com", "www.reddit.com")
            else:
                new_url = re.sub(r"(www\.)?reddit\.com", "old.reddit.com", url_lower)
            converted_urls.append(new_url)

        # Send results
        response = "🔗 **Converted URLs:** " + "\n".join(converted_urls)
        await interaction.response.send_message(response)
