import yfinance
import datetime
from redbot.core import commands, app_commands
import discord

class Stonk(commands.Cog):
    """Fetches the current value of a stock from Yahoo Finance using yfinance."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quote", description="Fetch the current stock price for a given ticker symbol.")
    async def quote(self, interaction: discord.Interaction, symbol: str):
        """
        Fetch the latest stock price for a given symbol, along with time and percent change.
        Usage:
        /quote <symbol>
        Example: /quote AAPL
        """
        try:
            # Fetch the stock data using yfinance
            stock = yfinance.Ticker(symbol)
            # Get the most recent market data (1 minute intervals for the day)
            data = stock.history(period="1d", interval="1m")

            if data.empty:
                await interaction.response.send_message(f"❌ No data available for **{symbol.upper()}**.")
                return

            # Get the latest closing price and timestamp
            latest_price = data['Close'].iloc[-1]
            latest_time = data.index[-1].strftime("%Y-%m-%d %H:%M:%S")  # Convert the timestamp to a readable format

            # Get the previous closing price (the price at the beginning of the day)
            previous_price = data['Close'].iloc[0]

            # Calculate the percent change
            percent_change = ((latest_price - previous_price) / previous_price) * 100

            # Define the color formatting
            if percent_change > 0:
                percent_change_str = f"🟢 **+{percent_change:.2f}%**"  # Green for positive change
            else:
                percent_change_str = f"🔴 **{percent_change:.2f}%**"  # Red for negative change

            # Format the response with time, latest price, and percent change
            response = (f"The latest price for **{symbol.upper()}** is: **${latest_price:.2f}**\n"
                        f"Last updated at: {latest_time}\n"
                        f"Change from opening: {percent_change_str}")

            await interaction.response.send_message(response)

        except Exception as e:
            # In case of any errors, send an error message
            await interaction.response.send_message(f"❌ Error fetching data for symbol **{symbol.upper()}**: {str(e)}")
