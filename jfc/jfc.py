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
        self.bible_regex = re.compile(r"^([1-3]\s)?[a-zA-Z\s]+\s\d+:\d+(-\d+)?$")

    @app_commands.command(name="jfc", description="Fetch a Bible passage")
    @app_commands.describe(
        passage="e.g., Matt 7:21-23 or John 3:16",
        version="Bible version (e.g., NIV, KJV, ESV). Defaults to NIV."
    )
    async def jfc_slash(
            self,
            interaction: discord.Interaction,
            passage: str,
            version: str = "NIV"
    ):
        clean_passage = passage.strip()
        if not self.bible_regex.match(clean_passage):
            await interaction.response.send_message(
                "❌ **Invalid Format.** Use `Book Chapter:Verse` (e.g., `John 3:16`).",
                ephemeral=True
            )
            return

        await interaction.response.defer()

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

            # --- Refined Scraping Logic ---
            # Look for the main content area
            content = soup.find("div", class_="passage-content")

            if not content:
                await interaction.followup.send(
                    f"Could not find **{clean_passage}** in version **{version.upper()}**."
                )
                return

            # Remove the "noise" before extracting text
            # .chapternum and .versenum are often kept, but cross-refs and footnotes MUST go
            for unwanted in content.find_all(["sup", "footer", "div", "header"], class_=re.compile(
                    r"crossreference|footnote|results-header|button-container")):
                unwanted.decompose()

            # Find all text-bearing paragraphs or spans
            text_blocks = content.find_all(["p", "span"], class_=re.compile(r"text|line"))

            lines = []
            for block in text_blocks:
                # Clean out any remaining footnote/cross-ref markers inside the block
                for sup in block.find_all("sup"):
                    sup.decompose()

                txt = block.get_text().strip()
                if txt and txt not in lines:  # Simple de-duplication
                    lines.append(txt)

            full_text = " ".join(lines)
            # Clean up double spaces that often occur after stripping elements
            full_text = re.sub(r'\s+', ' ', full_text).strip()

            if not full_text:
                await interaction.followup.send("Found the passage, but couldn't extract the text content.")
                return

            # --- Construct the Response ---
            embed = discord.Embed(
                title=f"📖 {clean_passage} ({version.upper()})",
                url=url,
                description=full_text[:3900] + ("..." if len(full_text) > 3900 else ""),
                color=0x7289da
            )
            embed.set_footer(text="Source: BibleGateway.com")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")