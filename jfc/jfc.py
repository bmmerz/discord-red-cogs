import discord
import re
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote
from redbot.core import commands, app_commands


class JFC(commands.Cog):
    """Fetch Bible passages via BibleGateway with version support."""

    def __init__(self, bot):
        self.bot = bot
        # Regex: Optional number, Book Name (supports multi-word), Chapter:Verse(s)
        # Matches: "John 3:16", "1 John 1:9", "Song of Solomon 2:1"
        self.bible_regex = re.compile(r"^([1-3]\s)?[a-zA-Z\s]+\s\d+:\d+(-\d+)?$")

    @app_commands.command(name="jfc", description="Fetch a Bible passage")
    @app_commands.describe(
        passage="e.g., Matt 7:21-23 or John 3:16",
        version="Bible version (e.g., NIV, KJV, ESV, NASB). Defaults to NIV."
    )
    async def jfc_slash(
            self,
            interaction: discord.Interaction,
            passage: str,
            version: str = "NIV"
    ):
        # 1. Sanity Check
        clean_passage = passage.strip()
        if not self.bible_regex.match(clean_passage):
            await interaction.response.send_message(
                "❌ **Invalid Format.** Use `Book Chapter:Verse` (e.g., `Matt 7:21-23`).",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        # 2. Encode URL
        encoded_passage = quote(clean_passage)
        encoded_version = quote(version.upper())
        url = f"https://www.biblegateway.com/passage/?search={encoded_passage}&version={encoded_version}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
                    if resp.status != 200:
                        await interaction.followup.send("Error: BibleGateway is not responding.")
                        return

                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

            # 3. Scrape the passage text
            # BibleGateway uses different classes, but .text-html is the most reliable wrapper
            text_elements = soup.select(".text-html p")

            if not text_elements:
                await interaction.followup.send(
                    f"Could not find **{clean_passage}** in version **{version.upper()}**. "
                    "Check the reference or version code."
                )
                return

            # Clean the text
            full_text = ""
            for p in text_elements:
                # Remove verse numbers, footnotes, and cross-reference markers
                for unwanted in p.find_all(["sup", "footer", "span", "header"]):
                    # Don't decompose specific formatting if you want to keep it,
                    # but 'sup' usually handles the noisy bits.
                    unwanted.decompose()

                para_text = p.get_text(separator=" ").strip()
                if para_text:
                    full_text += para_text + "\n\n"

            # 4. Construct the Response
            embed = discord.Embed(
                title=f"📖 {clean_passage} ({version.upper()})",
                url=url,
                description=full_text[:3800] + ("..." if len(full_text) > 3800 else ""),
                color=0x7289da  # Blurple
            )
            embed.set_footer(text="Source: BibleGateway.com")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")