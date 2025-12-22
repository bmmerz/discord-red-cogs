#from redbot.core import errors
#import importlib
#import sys

#try:
#    import yfinance
#except ModuleNotFoundError:
#    raise errors.CogLoadError(
#        "yfinance could not be imported"
#    )
#try:
#    importlib.import_module("yfinance")
#except ModuleNotFoundError:
#    pass

import subprocess
import sys

def install_requirements():
    try:
        subprocess.call('pip install -r requirements.txt', shell=True)
    except subprocess.CalledProcessError:
        print("error installing requirements")

install_requirements()

from .stonk import Stonk

async def setup(bot):
    await bot.add_cog(Stonk(bot))