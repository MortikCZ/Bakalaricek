import discord
from discord.ext import commands, tasks
import json
import extractor as bk
import os
import logging
import aiofiles

logging.basicConfig(level=logging.INFO)

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        with open(self.config_file) as file:
            self.data = json.load(file)

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.data, file, indent=4)

    def get(self, key, default=None):
        return self.data.get(key, default)

config = Config('config.json')

TOKEN = config.get('token')
TIMETABLE_URL = config.get('timetable_url')
NOTIFICATION_CHANNEL_ID = config.get('notification_channel_id')
NEXT_WEEK_TIMETABLE_URL = config.get('next_week_timetable_url')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

PREVIOUS_SUBSTITUTIONS_FILE = 'previous_substitutions.json'
SUBSTITUTIONS_FILE = 'substitutions.json'
NEXT_WEEK_SUBSTITUTIONS_FILE = 'next_week_substitutions.json'

async def load_previous_substitutions():
    if os.path.exists(PREVIOUS_SUBSTITUTIONS_FILE):
        async with aiofiles.open(PREVIOUS_SUBSTITUTIONS_FILE, 'r') as file:
            return json.loads(await file.read())
    return None

async def save_previous_substitutions(substitutions):
    async with aiofiles.open(PREVIOUS_SUBSTITUTIONS_FILE, 'w') as file:
        await file.write(json.dumps(substitutions, indent=4))

previous_substitutions = None

async def initialize_previous_substitutions():
    global previous_substitutions
    previous_substitutions = await load_previous_substitutions()

async def send_notifications(channel, new_data):
    if channel is None:
        logging.warning("Notification channel not found.")
        return
    role_id = config.get('role_id')
    role_mention = f"<@&{role_id}>" if role_id else ""
    for date, changes in new_data.items():
        for change in changes:
            message = (
                f"{role_mention}\n"
                f"# Nová změna v rozvrhu!\n"
                f"**Datum:** {date}\n"
                f"**Číslo hodiny:** {change['hour']}\n"
                f"**Popis:** {change['changeinfo'] or change['removedinfo'] or change['absentinfo']}"
            )
            await channel.send(message)

@tasks.loop(minutes=30)
async def handle_week_transition():
    global previous_substitutions
    if previous_substitutions:
        async with aiofiles.open(NEXT_WEEK_SUBSTITUTIONS_FILE, 'r', encoding='utf-8') as file:
            next_week_data = json.loads(await file.read())
        current_week_dates = set(previous_substitutions.keys())
        next_week_dates = set(next_week_data.keys())
        
        if not current_week_dates.isdisjoint(next_week_dates):
            previous_substitutions = await load_previous_substitutions()
            await save_previous_substitutions(previous_substitutions)

@tasks.loop(minutes=30)
async def fetch_timetable_changes():
    await handle_week_transition()
    bk.get_substitutions(TIMETABLE_URL, SUBSTITUTIONS_FILE)
    bk.get_substitutions(NEXT_WEEK_TIMETABLE_URL, NEXT_WEEK_SUBSTITUTIONS_FILE)
    
    async with aiofiles.open(SUBSTITUTIONS_FILE, 'r', encoding='utf-8') as file:
        new_data = json.loads(await file.read())
    
    async with aiofiles.open(NEXT_WEEK_SUBSTITUTIONS_FILE, 'r', encoding='utf-8') as file:
        next_week_data = json.loads(await file.read())
    
    global previous_substitutions
    channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
    
    if previous_substitutions is None:
        previous_substitutions = new_data
        await save_previous_substitutions(new_data)
        await send_notifications(channel, new_data)
        await send_notifications(channel, next_week_data)
        return
    
    if new_data != previous_substitutions:
        await save_previous_substitutions(new_data)
        previous_substitutions = new_data
        await send_notifications(channel, new_data)
        await send_notifications(channel, next_week_data)

async def set_bot_status():
    status = config.get('status')
    if status:
        await bot.change_presence(activity=discord.Game(name=status))

@bot.command()
@commands.has_permissions(administrator=True)
async def setstatus(ctx, *, new_status: str):
    config.data['status'] = new_status
    config.save_config()
    await bot.change_presence(activity=discord.Game(name=new_status))
    await ctx.send(f"Status updated to: {new_status}")

@setstatus.error
async def setstatus_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to change the status.")

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')
    await set_bot_status()
    await initialize_previous_substitutions()
    fetch_timetable_changes.start()
    handle_week_transition.start()

bot.run(TOKEN)