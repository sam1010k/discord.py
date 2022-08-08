import discord
from discord import app_commands
from discord.ext import commands
import random
import re
import os
import pandas as pd
from pathlib import Path
from datetime import date
import dotenv 
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
today = date.today()

class aclient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix = "", intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f'We have logged in as {self.user}')

client = aclient()
tree = app_commands.CommandTree(client)

def process_figure_post(line_split):
        figure_game_url = line_split[0]
        figure_num = line_split[1]
        figure_trys = line_split[2]
        figure_time = line_split[3]

        figure_num_pattern = "Figure #(.*)"
        mo = re.search(figure_num_pattern,figure_num)
        figure_number = mo.group(1)

        for s in figure_trys.split():
            if s.isdigit():
                number_of_tries = s

        figure_times = [int(s) for s in figure_time.split() if s.isdigit()]
        figure_minutes = figure_times[0]
        figure_seconds = figure_times[1]
        return figure_number, number_of_tries, figure_minutes, figure_seconds

def record_data(username, figure_number, number_of_tries, figure_minutes, figure_seconds):
    date = today.strftime("%m/%d/%y")
    new_row_dict = {'Username': [username],'Figure Number': [figure_number],'Number of Tries': [number_of_tries],
    'Minutes': [figure_minutes],'Seconds': [figure_seconds],'Date': [date]}
    new_row_df = pd.DataFrame(new_row_dict)
    figure_data_df = pd.read_csv('figure_data.csv')
    figure_data_df = figure_data_df.append(new_row_df, ignore_index=True)
    figure_data_df.drop(columns=['Unnamed: 0'], inplace=True)
    figure_data_df = figure_data_df.drop_duplicates(subset=['Username', 'Figure Number'], keep='last').reset_index(drop = True)
    print(figure_data_df)
    filepath = Path('figure_data.csv')  
    filepath.parent.mkdir(parents=True, exist_ok=True)  
    figure_data_df.to_csv(filepath)
    return figure_data_df

def figure_say_good_job(username, figure_number, number_of_tries, figure_minutes, figure_seconds):
    response = (f'Great Job {username}!\n'
    f'You did the {figure_number}th figure in {number_of_tries} trys.\n'
    f'It only took you {figure_minutes} minutes and {figure_seconds} seconds!!!\n'
    f'Super proud of you bud.')
    return response

def get_random_string(csv):
    df = pd.read_csv(csv)
    print(len(df.index))
    rand_string = str(df.iat[random.randrange(len(df.index)),0]).strip()
    return rand_string     

@tree.command(name='fb', description = 'prompt')
async def self(interaction:discord.Interaction, prompt:str):
    username = str(interaction.user).split('#')[0]

    if interaction.user == client.user:
        print(f'client user')
        return

    if prompt.lower() == 'hello' or prompt.lower() == 'hi':
        greetings_phrase = get_random_string('greeting.csv')
        await interaction.response.send_message(f'{greetings_phrase} {username}!')
        return
    elif prompt.lower() == 'bye':
        goodbye_phrase = get_random_string('goodbyes.csv')
        await interaction.response.send_message(f'{goodbye_phrase} {username}!')
        return
    elif prompt.lower() == '!random':
        response = f'This is your random number {random.randrange(420000)}'
        await interaction.response.send_message(response)
        return
    elif prompt == '<:fullsalute:1005165220215398520>':
        salute_phrase = get_random_string('salute.csv')
        response = f'{salute_phrase} {username} <:fullsalute:1005165220215398520>'
        await interaction.response.send_message(response)
        return
    elif prompt == '<:fullsalute:1005149563809710241>':
        salute_phrase = get_random_string('salute.csv')
        response = f'{salute_phrase} {username} <:fullsalute:1005149563809710241>'
        await interaction.response.send_message(response)
        return
    elif prompt =='scoreboard':
        df = pd.read_csv('figure_data.csv')
        df.drop(columns=['Unnamed: 0'], inplace=True)
        response = f'Scoreboard \n\n {df.to_markdown()}'
        await interaction.response.send_message(response)
        return
    else:
        return

@client.event
async def on_message(message):

    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel_name = str(message.channel.name)
    line_split = user_message.split("\n")
    print(f'{username}: {user_message} {channel_name}')

    # Handle when a user submits their figure scores
    if 'https://figure.game' in line_split[0]:
        figure_number, number_of_tries, figure_minutes, figure_seconds = process_figure_post(line_split)
        figure_data_df = record_data(username, figure_number, number_of_tries, figure_minutes, figure_seconds)
        response = figure_say_good_job(username, figure_number, number_of_tries, figure_minutes, figure_seconds)
        await message.channel.send(response)
        return

client.run(TOKEN)