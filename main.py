import discord
from discord import app_commands
import modules.emojis as emojis
import random
from typing import Optional, Union, Any
import modules.haj_data as haj_data
import os
import modules.errors as errors
from datetime import timedelta, datetime


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

        
    responses = {
        "🦈" : f"rawwwww {emojis.blahajar['blahaj_boo']}",
        "boop" : emojis.blahajar['blahaj_boop'],
        "blahaj" : random.choice(list(emojis.blahajar.values())),
        "blahajar" : "".join(random.choices(list(emojis.blahajar.values()), k=3)),
        "lithuania" : ":flag_lt:"
    }

    if message.content.lower() in responses:
        await message.reply(responses[message.content.lower()])
    elif 'boop' in message.content.lower() and message.content.startswith('<:') and message.content.endswith('>'):
        await message.reply(emojis.blahajar['blahaj_boop'])
    

    user_data = client.haj_data.get_data(message.author)

    if user_data is None:
        return

    if random.randint(1, 10) == 1:
        await message.add_reaction("🐟")
            
        user_data['fish'] = user_data.get('fish', 0) + 1
        client.haj_data.sync_changes(message.author, user_data)

    if random.randint(1, 50) == 1:
        await message.add_reaction("🍫")
        
        user_data['chocolate'] = user_data.get('chocolate', 0) + 1
        client.haj_data.sync_changes(message.author, user_data)


@client.tree.error
async def on_error(interaction: discord.Interaction, 
                   error: app_commands.AppCommandError):
    embed = discord.Embed(
        color=discord.Color.red(),
        title="Error"
    )

    if isinstance(error, errors.InvalidFood):
        embed.description = "Invalid food."
    elif isinstance(error, errors.TooLittleOfFood):
        embed.description = "You don't have enough of that food."
    elif isinstance(error, errors.TooLittleBait):
        embed.description = "You don't have enough bait."
    elif isinstance(error, errors.InvalidAmount):
        embed.description = "Invalid amount."
    elif isinstance(error, errors.NoBlahaj):
        embed.description = "You don't have a blahaj!"
    elif isinstance(error, errors.NoBlahajOthers):
        embed.description = "That user has no blahaj."
    elif isinstance(error, errors.NameTooLong):
        embed.description = "Name too long (32 characters or less required)."
    elif isinstance(error, errors.AlreadyHaveBlahaj):
        embed.description = "You already have a blahaj!"
    elif isinstance(error, errors.BaitCooldown):
        embed.description = "You already got bait today! Try again tommorow."
    else:   
        print(error)

    await interaction.response.send_message(embed=embed, ephemeral=True)

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
    
    size = user_data.get('size', 0)
    blahaj_sizes = {
        80 : "babyhaj",
        160 : "tinyhaj",
        550 : "smallhaj",
        1000 : "normal haj",
        1500 : "megahaj",
        3000 : "colossalhaj"
    }

    blahaj_size = [key for key in blahaj_sizes if key <= (size+80)].pop()
    blahaj_size = blahaj_sizes[blahaj_size]
    
    embed.add_field(name="Name", 
                    value=f"{user_data.get('haj_profile')} {user_data.get('name')}", 
                    inline=False)
    embed.add_field(name="Stats",
                    value=f"Love ❤️ {user_data.get('love', 0)} \
                        \nSize ⬆️ {(size/10)+8}cm ({blahaj_size})",
                    inline=False)
    embed.add_field(name="Food" , 
                    value=f"🐟 {user_data.get('fish', 0)} \
                        \n🍫 {user_data.get('chocolate', 0)} \
                        \n{emojis.blahajar['transphobe >:(']} {user_data.get('transphobes', 0)}", 
                    inline=False)
    embed.add_field(name="Items" , 
                    value=f"🪱 {user_data.get('bait', 0)}", 
                    inline=False)
    
    await interaction.response.send_message(embed=embed)


@client.tree.command(description="Adopt a blahaj!")
async def adopt(interaction: discord.Interaction,
            name : str):
    
    if len(name) > 32:
        raise errors.NameTooLong()
    elif client.haj_data.get_data(interaction.user) is not None:
        raise errors.AlreadyHaveBlahaj()
    
    embed = discord.Embed(
            color=discord.Color.purple(),
            title=f"You adopted a blahaj!",
            description=f"{emojis.blahajar['blahaj']} {name}"
    )
    
    client.haj_data.sync_changes(interaction.user, haj_data.user_data(name=name))
    
    
    await interaction.response.send_message(embed=embed)


@client.tree.command(description="Eat some food.")
async def eat(interaction: discord.Interaction,
            food : str,
            amount : str = "1"):
    
    try:
        amount = int(amount)
    except ValueError:
        amount = amount
    
    food_effects = {
        'fish' : (1, 1),            # First element is change in size
        'chocolate' : (0, 3),       # Second is change in love
        'transphobes' : (25, 0)
    }

    food_effect = food_effects.get(food, None)

    user_data = client.haj_data.get_data(interaction.user)

    if user_data is None:
        raise errors.NoBlahaj()
    elif food_effect is None:
        raise errors.InvalidFood()
    
    try:
        amount = int(amount)
    except ValueError:
        amount = user_data.get(food, 0)
    
    if amount < 1:
        raise errors.InvalidAmount()
    elif user_data.get(food, 0) < amount:
        raise errors.TooLittleOfFood()
    
    if amount == "all":
        amount = user_data.get(food, 0)

    embed = discord.Embed(
            color=discord.Color.purple(),
            title=f"Ate {amount} {food}.",
            description="yums"
    )
    
    user_data[food] = user_data.get(food, 0) - amount
    if food_effect[0]:
        user_data['size'] = user_data.get('size', 0) + food_effect[0]*amount
        embed.description += f"\nSize ⬆️ increased by {(food_effect[0]*amount)/10}cm."
    if food_effect[1]:
        user_data['love'] = user_data.get('love', 0) + food_effect[1]*amount
        embed.description += f"\nLove ❤️ increased by {food_effect[1]*amount}."
    client.haj_data.sync_changes(interaction.user, user_data)

    await interaction.response.send_message(embed=embed)


@client.tree.command(description="Fish some food.")
async def fish(interaction: discord.Interaction):
    user_data = client.haj_data.get_data(interaction.user)

    if user_data is None:
        raise errors.NoBlahaj()
    elif user_data.get('bait', 0) < 1:
        raise errors.TooLittleBait()
    
    fish_gained = random.choices(range(6), [0.1, 0.65, 0.1, 0.075, 0.05, 0.025])[0]
    chocolate_gained = random.choices(range(4), [0.8, 0.1, 0.07, 0.03])[0]
    transphobes_gained = random.choices(range(3), [0.95, 0.045, 0.005])[0]
    total_gained = fish_gained+chocolate_gained+transphobes_gained

    embed = discord.Embed(
        color=discord.Color.purple(),
        title="Fishing result",
        description="You got:\n"
    )

    if total_gained == 0:
        embed.description += "Nothing this time :("
        await interaction.response.send_message(embed=embed)
        return

    if fish_gained:
        user_data['fish'] = user_data.get('fish', 0) + fish_gained
        embed.description += f"🐟 {fish_gained} \n"
    if chocolate_gained:
        user_data['chocolate'] = user_data.get('chocolate', 0) + chocolate_gained
        embed.description += f"🍫 {chocolate_gained} \n"
    if transphobes_gained:
        user_data['transphobes'] = user_data.get('transphobes', 0) + transphobes_gained
        embed.description += f"{emojis.blahajar['transphobe >:(']} {transphobes_gained} \n"
    
    user_data['bait'] = user_data.get('bait', 0) - 1
    client.haj_data.sync_changes(interaction.user, user_data)

    await interaction.response.send_message(embed=embed)


@client.tree.command(description="Get some of your daily bait.")
async def bait(interaction: discord.Interaction):

    user_data = client.haj_data.get_data(interaction.user)

    if user_data is None:
        raise errors.NoBlahaj()

    last_bait = user_data.get('last_bait', None)
    now = datetime.now()

    if last_bait is None:
        last_bait = now - timedelta(days=1)
    else:
        last_bait = datetime.strptime(last_bait, "%Y-%m-%d")

    if last_bait.date() >= now.date():
        raise errors.BaitCooldown()

    user_data['last_bait'] = now.strftime("%Y-%m-%d")

    daily_bait = user_data.get('daily_bait', 10)
    
    embed = discord.Embed(
        color=discord.Color.purple(),
        title="Daily bait",
        description=f"You got {daily_bait} bait! 🪱"
    )
    
    user_data['bait'] = user_data.get('bait', 0) + daily_bait
    client.haj_data.sync_changes(interaction.user, user_data)

    await interaction.response.send_message(embed=embed)

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    print("No 'BOT_TOKEN' environment variable found.")
else:
    client.run(TOKEN)
