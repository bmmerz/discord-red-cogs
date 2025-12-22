from .stonk import Stonk

async def setup(bot):
    await bot.add_cog(Stonk(bot))