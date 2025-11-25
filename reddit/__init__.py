from .fixreddit import FixReddit

async def setup(bot):
    cog = FixReddit(bot)
    await bot.add_cog(cog)
    await bot.tree.sync()
