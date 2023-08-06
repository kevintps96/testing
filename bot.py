import testing
import discord
from flask import Flask
import requests
import openai
import os
import aiohttp
import ssl
import certifi
import zipfile

from discord.ext import commands

app = Flask(__name__)

discord_token = 'MTEyOTA4ODgxMTgxMzU4NDkyNg.GtGbeH.OqHQpoxoRxpxA6QbhULQkeY0qJurJ6a0qikpuI'
openai.api_key = 'Vj8b49N6roCxsFQO7Bm0T3BlbkFJqD3OeDEi2lmVosq0PO2S'
surfer_api_key = 'OqTnG18V5zR6eJ7YzbxNFHgat2y8IeaV'
wordpress_username = 'nightowl'
wordpress_password = '33websuppor'
wordpress_site_url = 'https://happysparrow.com.sg'

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

connector = aiohttp.TCPConnector(ssl=ssl_context)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents, connector=connector)

async def send_message(message, content, is_private):
    try:
        await message.author.send(content) if is_private else await message.channel.send(content)
    except Exception as e:
        print(e)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    channel = bot.get_channel(1102863701217923154)
    await channel.send("I'm ready to generate articles!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)  # Process text commands


@bot.command(
    name="generate_articles",
    help="Generate articles about a specific topic"
)
async def generate_articles(ctx: commands.Context, topic: str):
    if len(topic.strip()) > 0:
        await ctx.send(f"Generating articles about {topic}, please wait...")

        articles = generate_articles(topic, 1)
        if articles:
            zip_filepath = generate_zip(articles)
            with open(zip_filepath, 'rb') as file:
                await ctx.send(file=discord.File(file, filename='generated_articles.zip'))
        else:
            await ctx.send("Unable to generate articles. Please try again later.")
    else:
        await ctx.send("Invalid command. Please use the command '/generate_articles 'topic'.")


def generate_articles(topic, num_articles):
    prompt = f'''
    I Want You To Act As A Content Writer Very Proficient SEO Writer Writes Fluently English. First Create Two Tables. First Table Should be the Outline of the Article and the Second Should be the Article. Bold the Heading of the Second Table using Markdown language. Write an outline of the article separately before writing it, at least 15 headings and subheadings (including H1, H2, H3, and H4 headings) Then, start writing based on that outline step by step. Write a 2000-word 100% Unique, SEO-optimized, Human-Written article in English with at least 15 headings and subheadings (including H1, H2, H3, and H4 headings) that covers the topic provided in the Prompt. Write The article In Your Own Words Rather Than Copying And Pasting From Other Sources. Consider perplexity and burstiness when creating content, ensuring high levels of both without losing specificity or context. Use fully detailed paragraphs that engage the reader. Write In A Conversational Style As Written By A Human (Use An Informal Tone, Utilize Personal Pronouns, Keep It Simple, Engage The Reader, Use The Active Voice, Keep It Brief, Use Rhetorical Questions, and Incorporate Analogies And Metaphors).  End with a conclusion paragraph and 5 unique FAQs After The Conclusion. this is important to Bold the Title and all headings of the article, and use appropriate headings for H tags. And  In The Very Bottom of the article Write This Custom Massage "
    Get Access Now: https://bit.ly/J_Umma "
    Now Write An Article On This Topic "{topic}"'
    '''

    generated_articles = []

    for _ in range(num_articles):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=2000,
            temperature=0.7,
            n=1,
            stop=None
        )
        generated_article = response.choices[0].text.strip()
        generated_articles.append(generated_article)

    return generated_articles


def generate_zip(articles):
    directory = 'generated_articles'
    os.makedirs(directory, exist_ok=True)

    for i, article in enumerate(articles):
        filename = f'article_{i+1}.txt'
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(article)

    zip_filename = 'generated_articles.zip'
    zip_filepath = os.path.join(directory, zip_filename)
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for foldername, subfolders, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                zip_file.write(filepath, filename)

    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(foldername, filename)
            os.remove(filepath)
    os.rmdir(directory)

    return zip_filepath


if __name__ == '__main__':
    bot.run('MTEyOTA4ODgxMTgxMzU4NDkyNg.GtGbeH.OqHQpoxoRxpxA6QbhULQkeY0qJurJ6a0qikpuI')
