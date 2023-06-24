import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
from keep_alive import keep_alive
import os

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)
slash = SlashCommand(bot, sync_commands=True)

watched_users = {}
notification_channel = None

@bot.event
async def on_ready():
    print(f'sprites team presents,{bot.user.name}')
    # Start the keep-alive task
    keep_alive.start()

@tasks.loop(minutes=5)
async def keep_alive():
    # Keep-alive task logic (e.g., make an API request to keep the bot alive)
    print("Bot is still running!")

@slash.slash(
    name="setchannel",
    description="Set the channel to receive GitHub notifications",
)
async def set_channel(ctx: SlashContext):
    global notification_channel
    notification_channel = ctx.channel
    await ctx.send(f"GitHub notifications channel set to {notification_channel.mention}!")

@slash.slash(
    name="adduser",
    description="Add a user to receive GitHub notifications",
)
async def add_user(ctx: SlashContext):
    await ctx.send("Please provide the GitHub username of the user you want to add.")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        message = await bot.wait_for('message', timeout=30.0, check=check)
        username = message.content.strip()

        if username.lower() in watched_users:
            raise ValueError("This user is already being watched.")

        watched_users[username.lower()] = ctx.channel.id
        await ctx.send(f"Added {username} to the GitHub notifications list!")
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Please try again.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the message contains a GitHub notification
    if "github.com" in message.content and notification_channel:
        for username, channel_id in watched_users.items():
            # Check if the GitHub notification is for a watched user
            if username.lower() in message.content.lower():
                # Extract the relevant information from the GitHub notification
                # Replace the following code with your own logic to parse the GitHub notification
                embed = discord.Embed(
                    title="New GitHub Notification",
                    description=message.content,
                    color=discord.Color.blue()
                )
                embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)

                # Send the embed message to the specified notification channel
                channel = bot.get_channel(channel_id)
                await channel.send(embed=embed)

    await bot.process_commands(message)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run(os.getenv("BOT_TOKEN"))

run()
