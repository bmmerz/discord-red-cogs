import importlib
import logging

# Set up logging so you can see errors in the bot's console
log = logging.getLogger("red.stonk")

async def setup(bot):
    # Check if yfinance is installed
    try:
        importlib.import_module("yfinance")
    except ImportError:
        log.critical(
            "yfinance is not installed! "
            "Please run 'pip install yfinance' in your bot's environment."
        )
        raise RuntimeError(
            "Missing dependency: yfinance. Install it and reload the cog."
        )

    # If check passes, load the cog
    from .stonk import Stonk
    await bot.add_cog(Stonk(bot))
