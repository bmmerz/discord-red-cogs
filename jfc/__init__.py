from .jfc import JFC

async def setup(bot):
    await bot.add_cog(JFC(bot))