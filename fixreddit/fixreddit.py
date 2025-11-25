import re
from redbot.core import commands

# Regex for Reddit URLs (all subdomains)
REDDIT_REGEX = re.compile(
    r"https?://(?:www\.|old\.)?reddit\.com/[^\s<>]+",
    re.IGNORECASE
)

# Regex for Discord message links
MESSAGE_LINK_REGEX = re.compile(
    r"https://discord.com/channels/\d+/(\d+)/(\d+)"
)


class FixReddit(commands.Cog):
    """Flips reddit.com <-> old.reddit.com URLs from Discord messages."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fixreddit(self, ctx, *, message_link: str):
        """
        Flip reddit.com ↔ old.reddit.com for all Reddit links in a Discord message.
        Usage:
        [p]fixreddit <Discord message link>
        """
        message_link = message_link.strip()
        match = MESSAGE_LINK_REGEX.match(message_link)
        if not match:
            await ctx.send("❌ Invalid Discord message link.")
            return

        channel_id, message_id = match.groups()
        if int(channel_id) != ctx.channel.id:
            await ctx.send("❌ Message link must be from this channel.")
            return

        try:
            message = await ctx.channel.fetch_message(int(message_id))
        except Exception:
            await ctx.send("❌ Could not fetch the message.")
            return

        # Find all Reddit URLs in the message
        urls = REDDIT_REGEX.findall(message.content)
        if not urls:
            await ctx.send("❌ No Reddit URLs found in that message.")
            return

        # Flip each URL
        converted_urls = []
        for url_tuple in urls:
            url = url_tuple[0] + (url_tuple[1] or '') + (url_tuple[2] or '')
            if "old.reddit.com" in url.lower():
                new_url = url.lower().replace("old.reddit.com", "reddit.com")
            else:
                new_url = url.lower().replace("www.reddit.com", "old.reddit.com").replace("reddit.com", "old.reddit.com")
            converted_urls.append(new_url)

        # Send results
        response = "🔗 **Converted URLs:**\n" + "\n".join(converted_urls)
        await ctx.send(response)
