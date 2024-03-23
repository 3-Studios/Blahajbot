import discord
from discord import app_commands
import modules.emojis as emojis
import random
from typing import Optional
import modules.haj_data as haj_data
import os

if os.getenv('TEST_GUILD'):
    TEST_GUILD = discord.Object(os.environ['TEST_GUILD'])
else:
    TEST_GUILD = None

class blajbot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.haj_data = haj_data.blahaj_data('data/blahajar.json')

    async def setup_hook(self):
                # Copies over to testing server
               self.tree.copy_global_to(guild=TEST_GUILD)
               
               # Syncs all commands
               await self.tree.sync(guild=None)    # Global commands take a while to register with discord.
               await self.tree.sync(guild=TEST_GUILD)
               print("synced commands")


intents = discord.Intents.default()
intents.message_content = True
client = blajbot(intents=intents)

@client.event
async def on_ready():
    print(f'logged in as {client.user} (ID: {client.user.id})')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="with blahajar :3"))

@client.event
async def on_message(message : discord.Message):
    if message.author == client.user or message.author.bot:
        return
    
    if random.randint(1, 10) == 1:
        await message.add_reaction("🐟")
        user_data = client.haj_data.get_data(message.author)

        if user_data is not None:
            user_data['fish'] = user_data.get('fish', 0) + 1
            client.haj_data.sync_changes(message.author, user_data)

    if random.randint(1, 50) == 1:
        await message.add_reaction("🍫")
        user_data = client.haj_data.get_data(message.author)

        if user_data is not None:
            user_data['chocolate_bars'] = user_data.get('chocolate_bars', 0) + 1
            client.haj_data.sync_changes(message.author, user_data)

        
    responses = {
        "🦈" : f"rawwwww {emojis.blahajar['blahaj_boo']}",
        "boop" : emojis.blahajar['blahaj_boop'],
        "blahaj" : random.choice(list(emojis.blahajar.values())),
        "blahajar" : "".join(random.choices(list(emojis.blahajar.values()), k=3)),
        "lithuania" : ":flag_lt:"
    }

    if message.content.lower() in responses.keys():
        await message.reply(responses[message.content.lower()])
    elif 'boop' in message.content.lower() and message.content.startswith('<:') and message.content.endswith('>'):
        await message.reply(emojis.blahajar['blahaj_boop'])

#
# COMMANDS
#
    
@client.tree.command(description="Shows the stats of a member (or yourself by default).")
@app_commands.describe(member="The member to show stats for.")
async def stats(interaction: discord.Interaction,  
               member: Optional[discord.Member]):
        
        if member is None:
            member = interaction.user

        user_data = client.haj_data.get_data(member)

        embed = discord.Embed(
                color=discord.Color.purple(),
                title=f"Stats for {str(member)}'s blahaj"
        )

        if user_data is None:
            embed.color = discord.Color.red()
            embed.title = "Error"
            embed.description = "User has no blahaj."
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed.add_field(name="Name", 
                        value=f"{user_data.get('haj_profile')} {user_data.get('name')}", 
                        inline=False)
        embed.add_field(name="Items", 
                        value=f"🐟 {user_data.get('fish', 0)} \
                        \n🍫 {user_data.get('chocolate_bars', 0)} \
                        \n{emojis.blahajar['transphobe >:(']} {user_data.get('transphobes', 0)}", 
                        inline=False)
        
        await interaction.response.send_message(embed=embed)

@client.tree.command(description="Adopt a blahaj!")
async def adopt(interaction: discord.Interaction,
                name : str):
        
        embed = discord.Embed(
                color=discord.Color.purple(),
                title=f"You adopted a blahaj!",
                description=f"{emojis.blahajar['blahaj']} {name}"
        )
        
        if len(name) > 32:
            embed.color = discord.Color.red()
            embed.title = "Error"
            embed.description = "Name too long."
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        elif client.haj_data.get_data(interaction.user) is not None:
            embed.color = discord.Color.red()
            embed.title = "Error"
            embed.description = "You already have a blahaj!"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        client.haj_data.sync_changes(interaction.user, haj_data.user_data(name=name))
        
        
        await interaction.response.send_message(embed=embed)


@client.tree.command(description="Eat some food.")
async def eat(interaction: discord.Interaction,
                food : str,
                amount : int = 1):
        
        foods = {
            'fish' : 'fish',
            'chocolate' : 'chocolate_bars',
            'transphobes' : 'transphobes'
        }
        
        embed = discord.Embed(
                color=discord.Color.purple(),
                title=f"Ate {amount} {food}.",
                description="yums"
        )

        user_data = client.haj_data.get_data(interaction.user)

        if user_data is None:
            embed.color = discord.Color.red()
            embed.title = "Error"
            embed.description = "You don't have a blahaj!"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        elif food not in foods:
            embed.color = discord.Color.red()
            embed.title = "Error"
            embed.description = "Invalid food!"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user_data.get(foods[food], 0) < amount:
            embed.color = discord.Color.red()
            embed.title = "Error"
            embed.description = "You don't have enough of the specified food!"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_data[foods[food]] = user_data.get(foods[food], 0) - amount
        client.haj_data.sync_changes(interaction.user, user_data)

        await interaction.response.send_message(embed=embed)


TOKEN = os.environ['BOT_TOKEN']
client.run(TOKEN)
