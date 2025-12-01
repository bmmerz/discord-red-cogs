from .reddit import Reddit

async def setup(bot):
    await bot.add_cog(Reddit(bot))