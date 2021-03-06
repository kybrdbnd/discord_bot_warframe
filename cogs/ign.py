import discord
from datetime import datetime
from discord.ext import commands
from cogs.utils.constants import *


def check_user(ctx):
    return ctx.message.author.id == int(USER_ID)  # only pucci can do it


class IGN(commands.Cog, name='In-Game Name'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(help='IGN Commands')
    async def ign(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid IGN command passed...')

    @ign.command(name='save', help='Saves your IGN', usage='<YOUR_IGN>')
    async def ign_save(self, ctx, ign_name: str):
        collection = db[IGN_COLLECTION_NAME]
        ignJSON = {
            'id': ctx.author.id,
            'ign': ign_name,
            'updatedOn': datetime.now()
        }
        collection.update_one({'id': ctx.author.id},
                              {'$set': ignJSON},
                              upsert=True)

        await ctx.send(f"Hunter your name has been updated to {ign_name}")

    @ign.command(name='search', help='Search for a user IGN', usage='<@user>')
    async def ign_search(self, ctx, members: commands.Greedy[discord.Member], *, search='ign'):
        collection = db[IGN_COLLECTION_NAME]
        message = ''
        if len(members) > 0:
            for member in members:
                query = {
                    'id': member.id
                }
                ignDoc = collection.find_one(query)
                if ignDoc is not None:
                    message += f"Hunter {member.mention} IGN is {ignDoc['ign']} \n"
                else:
                    message += f"Hunter {member.mention} IGN not found \n"
            await ctx.send(message)
        else:
            await ctx.send("Please enter atleast one user")

    @ign.command(name='mine', help='display your IGN')
    async def ign_mine(self, ctx):
        collection = db[IGN_COLLECTION_NAME]
        query = {
            'id': ctx.author.id
        }
        ignDoc = collection.find_one(query)
        if ignDoc is not None:
            await ctx.send(f"Hunter your IGN is {ignDoc['ign']}")
        else:
            await ctx.send(f"IGN not found")

    @ign.command(name='list', help='display members ign')
    async def ign_list(self, ctx):
        collection = db[IGN_COLLECTION_NAME]
        ignDocs = list(collection.find({}))
        message = ''
        if len(ignDocs) > 0:
            for doc in ignDocs:
                member = self.bot.get_user(doc['id'])
                if member is not None:
                    message += f"Hunter {member.mention} IGN is {doc['ign']} \n"
            await ctx.send(message)
        else:
            await ctx.send("No warframe user names found")

    @ign.command(name='save_member', help='save member ign')
    @commands.check(check_user)
    async def save_member(self, ctx, member: discord.Member, ign_name: str):
        collection = db[IGN_COLLECTION_NAME]
        query = {
            'id': member.id
        }
        collection.update_one(query, {'$set': {'ign': ign_name, 'updatedOn': datetime.now()}}, upsert=True)
        await ctx.send(f"Hunter {member.mention} ign saved successfully")

    @ign_save.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Invalid IGN provided')

    @save_member.error
    async def save_member_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide member/ign')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('You are not authorized')


def setup(bot):
    bot.add_cog(IGN(bot))
