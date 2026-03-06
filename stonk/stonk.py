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
        """Fetches 2d history and fast_info in a non-blocking thread."""

        def get_data():
            ticker = yfinance.Ticker(symbol)
            # Fetch 2 days to get 'Previous Close' and today's 'Open'
            history = ticker.history(period="2d", interval="1d")
            fast_info = ticker.fast_info
            # 'info' is used sparingly for the Long Name
            name = ticker.info.get("longName", symbol)
            return name, history, fast_info

        task = functools.partial(get_data)
        return await self.bot.loop.run_in_executor(None, task)

    @app_commands.command(name="quote", description="Get a detailed stock quote with market status.")
    async def quote(self, interaction: discord.Interaction, symbol: str):
        await interaction.response.defer()
        symbol = symbol.upper()

        try:
            name, data, fast_info = await self.fetch_full_data(symbol)

            if data.empty:
                return await interaction.followup.send(
                    f"⚠️ **{symbol}** returned no data. It may be delisted or the ticker is incorrect."
                )

            # Basic Stats
            latest_price = fast_info.last_price
            currency = fast_info.currency
            curr_sym = "$" if currency == "USD" else f"{currency} "

            # Get the actual Open price from today's session
            today_open = data['Open'].iloc[-1]

            # Calculate Daily Change (Today's Price vs Yesterday's Close)
            if len(data) >= 2:
                prev_close = data['Close'].iloc[-2]
                change = latest_price - prev_close
                percent_change = (change / prev_close) * 100
            else:
                # Fallback to Day Open if only 1 day of data is available
                change = latest_price - today_open
                percent_change = (change / today_open) * 100

            # Formatting Visuals
            color = 0x2ecc71 if change >= 0 else 0xe74c3c
            trend = "▲" if change >= 0 else "▼"
            plus = "+" if change >= 0 else ""

            # Formatting the Day Change string
            # Example: ▲ +2.50% (+$5.40)
            change_line = f"**{trend} {percent_change:+.2f}%**\n({plus}{curr_sym}{abs(change):,.2f})"

            embed = discord.Embed(
                title=f"{symbol} - {name}",
                color=color,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )

            # Primary Pricing Info
            embed.add_field(name="Market Open", value=f"{today_open:,.2f} {currency}", inline=True)
            embed.add_field(name="Current Price", value=f"**{latest_price:,.2f} {currency}**", inline=True)

            # Spacer/Break (optional, but keeps columns aligned)
            embed.add_field(name="\u200b", value="\u200b", inline=True)

            # Secondary Market Stats
            embed.add_field(name="Day Change", value=change_line, inline=True)
            embed.add_field(name="Day High/Low", value=f"H: {fast_info.day_high:,.2f}\nL: {fast_info.day_low:,.2f}",
                            inline=True)

            # Market Status Footer
            market_state = getattr(fast_info, "market_state", "UNKNOWN").replace("_", " ")
            embed.set_footer(text=f"Status: {market_state.title()} | Data: Yahoo Finance")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg:
                msg = "🛑 Rate limited! Yahoo Finance is blocking requests."
            elif "not found" in err_msg:
                msg = f"❌ Ticker **{symbol}** could not be found."
            else:
                msg = f"⚙️ An unexpected error occurred: `{str(e)}`"

            await interaction.followup.send(msg)