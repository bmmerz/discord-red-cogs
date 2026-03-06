import asyncio
import functools
import datetime
import yfinance
import discord
from redbot.core import commands, app_commands


class Stonk(commands.Cog):
    """Fetches the current value of a stock with market status and error handling."""

    def __init__(self, bot):
        self.bot = bot

    async def fetch_full_data(self, symbol: str):
        """Fetches both history and ticker info in a non-blocking thread."""

        def get_data():
            ticker = yfinance.Ticker(symbol)
            # Fetching 1d history and general info
            history = ticker.history(period="1d", interval="1m")
            info = ticker.info
            return ticker, history, info

        task = functools.partial(get_data)
        return await self.bot.loop.run_in_executor(None, task)

    @app_commands.command(name="quote", description="Get a detailed stock quote with market status.")
    async def quote(self, interaction: discord.Interaction, symbol: str):
        await interaction.response.defer()

        symbol = symbol.upper()

        try:
            ticker, data, info = await self.fetch_full_data(symbol)

            # Check if history is empty (often happens with invalid tickers)
            if data.empty:
                return await interaction.followup.send(
                    f"⚠️ **{symbol}** returned no data. It may be delisted or the ticker is incorrect."
                )

            # Extract Market Status from info
            # Possible states: 'PRE', 'REGULAR', 'POST', 'CLOSED'
            market_state = info.get("marketState", "UNKNOWN").replace("_", " ")
            currency = info.get("currency", "USD")

            # Price Data
            open_price = data['Open'].iloc[0]
            latest_price = data['Close'].iloc[-1]
            change = latest_price - open_price
            percent_change = (change / open_price) * 100

            # Formatting
            color = 0x2ecc71 if change >= 0 else 0xe74c3c
            trend = "▲" if change >= 0 else "▼"

            embed = discord.Embed(
                title=f"{symbol} - {info.get('longName', 'Stock Quote')}",
                color=color,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )

            embed.add_field(name="Market Open", value=f"{open_price:,.2f} {currency}", inline=False)
            embed.add_field(name="Current Price", value=f"**{latest_price:,.2f} {currency}**", inline=True)
            embed.add_field(name="Day Change", value=f"**{trend} {percent_change:+.2f}%**\n({change:+.2f})",
                            inline=True)

            # Footer displays the Market Status
            footer_text = f"Status: {market_state.title()} | Data: Yahoo Finance"
            embed.set_footer(text=footer_text)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            # Handle Specific Error Cases
            err_msg = str(e).lower()
            if "429" in err_msg:
                msg = "🛑 Rate limited! Yahoo Finance is blocking requests. Please try again in a few minutes."
            elif "not found" in err_msg or "none" in err_msg:
                msg = f"❌ Ticker **{symbol}** could not be found."
            else:
                msg = f"⚙️ An unexpected error occurred: `{str(e)}`"

            await interaction.followup.send(msg)
