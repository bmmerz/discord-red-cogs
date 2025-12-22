from redbot.core import errors
import importlib
import sys

try:
    import yfinance
except ModuleNotFoundError:
    raise errors.CogLoadError(
        "yfinance could not be imported"
    )
try:
    importlib.import_module("yfinance")
except ModuleNotFoundError:
    pass

from .stonk import Stonk

async def setup(bot):
    await bot.add_cog(Stonk(bot))