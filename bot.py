import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv
from datetime import time
import aiohttp
import xml.etree.ElementTree as ET

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_GUILD_ID = 1397720381149806723
GREETING_CHANNEL_ID = 1398171685613469746
NHK_RSS_URL = 'https://www.nhk.or.jp/rss/news/cat0.xml'
YAHOO_RSS_URL = 'https://news.yahoo.co.jp/rss/topics/top-picks.xml'
GOOGLE_NEWS_URL = 'https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja'

async def fetch_nhk_news():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(NHK_RSS_URL) as response:
                if response.status == 200:
                    content = await response.text()
                    root = ET.fromstring(content)
                    
                    news_items = []
                    for item in root.findall('.//item')[:3]:
                        title = item.find('title').text if item.find('title') is not None else 'タイトル不明'
                        link = item.find('link').text if item.find('link') is not None else ''
                        news_items.append(f'・{title}\n{link}')
                    
                    return news_items
    except Exception as e:
        print(f'ニュース取得エラー: {e}')
        return ['ニュースの取得に失敗しました']

async def fetch_yahoo_news():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(YAHOO_RSS_URL) as response:
                if response.status == 200:
                    content = await response.text()
                    root = ET.fromstring(content)
                    
                    news_items = []
                    for item in root.findall('.//item')[:3]:
                        title = item.find('title').text if item.find('title') is not None else 'タイトル不明'
                        link = item.find('link').text if item.find('link') is not None else ''
                        news_items.append(f'・{title}\n{link}')
                    
                    return news_items
    except Exception as e:
        print(f'Yahoo!ニュース取得エラー: {e}')
        return ['Yahoo!ニュースの取得に失敗しました']

async def fetch_google_news():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GOOGLE_NEWS_URL) as response:
                if response.status == 200:
                    content = await response.text()
                    root = ET.fromstring(content)
                    
                    news_items = []
                    for item in root.findall('.//item')[:3]:
                        title = item.find('title').text if item.find('title') is not None else 'タイトル不明'
                        link = item.find('link').text if item.find('link') is not None else ''
                        news_items.append(f'・{title}\n{link}')
                    
                    return news_items
    except Exception as e:
        print(f'Google News取得エラー: {e}')
        return ['Google Newsの取得に失敗しました']

@tasks.loop(time=time(hour=6, minute=0))
async def greeting_task():
    channel = bot.get_channel(GREETING_CHANNEL_ID)
    if channel:
        news_items = await fetch_nhk_news()
        message = '🌅 おはようございます！今日の主要ニュースをお届けします\n\n' + '\n\n'.join(news_items)
        await channel.send(message)

@tasks.loop(time=time(hour=12, minute=0))
async def lunch_news_task():
    channel = bot.get_channel(GREETING_CHANNEL_ID)
    if channel:
        news_items = await fetch_yahoo_news()
        message = '🍽️ お昼のニュースをお届けします\n\n' + '\n\n'.join(news_items)
        await channel.send(message)

@tasks.loop(time=time(hour=18, minute=0))
async def evening_news_task():
    channel = bot.get_channel(GREETING_CHANNEL_ID)
    if channel:
        news_items = await fetch_google_news()
        message = '🌇 夕方のニュースをお届けします\n\n' + '\n\n'.join(news_items)
        await channel.send(message)

@bot.event
async def on_ready():
    print(f'{bot.user}としてログインしました！')
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)}個のスラッシュコマンドを同期しました')
    except Exception as e:
        print(f'スラッシュコマンドの同期に失敗しました: {e}')
    
    greeting_task.start()
    lunch_news_task.start()
    evening_news_task.start()
    print('定期投稿タスクを開始しました')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.guild.id != ALLOWED_GUILD_ID:
        return
    
    await message.channel.send(message.content)
    
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    
    if payload.guild_id != ALLOWED_GUILD_ID:
        return
    
    if str(payload.emoji) == '👍':
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        message_content = message.content[:50] + ('...' if len(message.content) > 50 else '')
        await channel.send(f'「{message_content}」のメッセージにグッドマークが押されたよ！')

@bot.tree.command(name='help', description='このbotの使い方を表示します')
async def help_command(interaction: discord.Interaction):
    if interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("このコマンドは指定されたサーバーでのみ使用できます。", ephemeral=True)
        return
    embed = discord.Embed(
        title="🤖 Bot使い方ガイド",
        description="このbotの機能と使い方を説明します",
        color=0x00ff00
    )
    
    embed.add_field(
        name="📝 基本機能",
        value="・メッセージを送信すると「こんにちは！ハロー！」と返事します\n・スラッシュコマンドに対応しています",
        inline=False
    )
    
    embed.add_field(
        name="⚡ スラッシュコマンド",
        value="`/help` - このヘルプメッセージを表示",
        inline=False
    )
    
    embed.add_field(
        name="💡 使い方",
        value="1. チャンネルでメッセージを送信してみてください\n2. `/help`でいつでもこのガイドを表示できます",
        inline=False
    )
    
    embed.set_footer(text="何かご質問があればお気軽にどうぞ！")
    
    await interaction.response.send_message(embed=embed)

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print('DISCORD_TOKENが設定されていません。.envファイルを確認してください。')