from .fixreddit import FixReddit

async def setup(bot):
    await bot.add_cog(FixReddit(bot))