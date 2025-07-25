import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv
from datetime import time, datetime, timezone, timedelta
import aiohttp
import xml.etree.ElementTree as ET

load_dotenv('.env.news')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 設定
ALLOWED_GUILD_ID = 1397720381149806723
GREETING_CHANNEL_ID = 1398171685613469746
ECHO_CHANNEL_ID = 1397720382236135446  # エコー機能を使用するチャンネル

# RSS URL
NHK_RSS_URL = 'https://www.nhk.or.jp/rss/news/cat0.xml'
YAHOO_RSS_URL = 'https://news.yahoo.co.jp/rss/topics/top-picks.xml'
GOOGLE_NEWS_URL = 'https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja'

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))

# 最新のニュース配信内容を保存
latest_news = {
    'morning': None,
    'lunch': None, 
    'evening': None
}

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
                        # OGPプレビューを無効化しつつタイトルにリンクを埋め込み
                        news_items.append(f'・[{title}](<{link}>)')
                    
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
                        # OGPプレビューを無効化しつつタイトルにリンクを埋め込み
                        news_items.append(f'・[{title}](<{link}>)')
                    
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
                        # OGPプレビューを無効化しつつタイトルにリンクを埋め込み
                        news_items.append(f'・[{title}](<{link}>)')
                    
                    return news_items
    except Exception as e:
        print(f'Google News取得エラー: {e}')
        return ['Google Newsの取得に失敗しました']

@tasks.loop(time=time(hour=6, minute=0, tzinfo=JST))
async def morning_news_task():
    channel = bot.get_channel(GREETING_CHANNEL_ID)
    if channel:
        news_items = await fetch_nhk_news()
        message = '🌅 おはようございます！今日の主要ニュースをお届けします\n\n' + '\n\n'.join(news_items)
        await channel.send(message)
        # 最新配信内容を保存
        latest_news['morning'] = message

@tasks.loop(time=time(hour=12, minute=0, tzinfo=JST))
async def lunch_news_task():
    channel = bot.get_channel(GREETING_CHANNEL_ID)
    if channel:
        news_items = await fetch_yahoo_news()
        message = '🍽️ お昼のニュースをお届けします\n\n' + '\n\n'.join(news_items)
        await channel.send(message)
        # 最新配信内容を保存
        latest_news['lunch'] = message

@tasks.loop(time=time(hour=18, minute=0, tzinfo=JST))
async def evening_news_task():
    channel = bot.get_channel(GREETING_CHANNEL_ID)
    if channel:
        news_items = await fetch_google_news()
        message = '🌇 夕方のニュースをお届けします\n\n' + '\n\n'.join(news_items)
        await channel.send(message)
        # 最新配信内容を保存
        latest_news['evening'] = message

async def send_latest_news(channel):
    """直近の自動配信ニュースを再送信"""
    try:
        now = datetime.now(JST)
        current_hour = now.hour
        
        # 時間帯に応じて最適なニュースを選択
        if 6 <= current_hour < 12:
            # 朝の時間帯 - 朝のニュースを優先
            if latest_news['morning']:
                await channel.send("📰 **最新の朝ニュース**\n" + latest_news['morning'])
            elif latest_news['evening']:
                await channel.send("📰 **昨夜のニュース**\n" + latest_news['evening'])
            elif latest_news['lunch']:
                await channel.send("📰 **昨日のお昼ニュース**\n" + latest_news['lunch'])
            else:
                await channel.send("📰 まだニュースが配信されていません。しばらくお待ちください。")
                
        elif 12 <= current_hour < 18:
            # 昼の時間帯 - 昼のニュースを優先
            if latest_news['lunch']:
                await channel.send("📰 **最新のお昼ニュース**\n" + latest_news['lunch'])
            elif latest_news['morning']:
                await channel.send("📰 **今朝のニュース**\n" + latest_news['morning'])
            elif latest_news['evening']:
                await channel.send("📰 **昨夜のニュース**\n" + latest_news['evening'])
            else:
                await channel.send("📰 まだニュースが配信されていません。しばらくお待ちください。")
                
        else:
            # 夜の時間帯 - 夜のニュースを優先
            if latest_news['evening']:
                await channel.send("📰 **最新の夕方ニュース**\n" + latest_news['evening'])
            elif latest_news['lunch']:
                await channel.send("📰 **今日のお昼ニュース**\n" + latest_news['lunch'])
            elif latest_news['morning']:
                await channel.send("📰 **今朝のニュース**\n" + latest_news['morning'])
            else:
                await channel.send("📰 まだニュースが配信されていません。しばらくお待ちください。")
                
    except Exception as e:
        print(f"❌ ニュース再送信エラー: {e}")
        await channel.send("❌ ニュースの取得に失敗しました。")

@bot.event
async def on_ready():
    print(f'{bot.user}としてログインしました！(ニュースBot)')
    print(f'ニュース配信チャンネル: {GREETING_CHANNEL_ID}')
    print(f'エコーチャンネル: {ECHO_CHANNEL_ID}')
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)}個のスラッシュコマンドを同期しました')
    except Exception as e:
        print(f'スラッシュコマンドの同期に失敗しました: {e}')
    
    morning_news_task.start()
    lunch_news_task.start()
    evening_news_task.start()
    print('📰 ニュース配信タスクを開始しました')

@bot.event
async def on_message(message):
    print(f"🔥 on_message呼び出し - 作者: {message.author}")
    
    if message.author == bot.user:
        print(f"🤖 bot自身のメッセージなのでスキップ")
        return
    
    print(f"📋 ギルドID確認 - 受信: {message.guild.id if message.guild else 'なし'}, 期待: {ALLOWED_GUILD_ID}")
    if message.guild.id != ALLOWED_GUILD_ID:
        print(f"❌ ギルドID不一致のためスキップ")
        return
    
    print(f"✅ メッセージ受信 - チャンネルID: {message.channel.id}, 作者: {message.author.display_name}, 内容: {message.content}")
    
    # ニューストリガー機能
    content_lower = message.content.lower()
    if any(keyword in content_lower for keyword in ['ニュース', 'news', '最新', 'ニュース教えて', 'ニュースある？']):
        await send_latest_news(message.channel)
        print(f"📰 ニューストリガー実行完了")
    
    # エコー機能は特定チャンネルでのみ動作
    elif message.channel.id == ECHO_CHANNEL_ID:
        await message.channel.send(message.content)
        print(f"🔄 エコー送信完了")
    
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

@bot.tree.command(name='news_help', description='ニュースBotの機能を表示します')
async def news_help_command(interaction: discord.Interaction):
    if interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("このコマンドは指定されたサーバーでのみ使用できます。", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📰 ニュースBot機能一覧",
        description="このbotのニュース配信機能について説明します",
        color=0x00ff00
    )
    
    embed.add_field(
        name="⏰ 定期ニュース配信",
        value="・**06:00** - NHK主要ニュース 3件\n・**12:00** - Yahoo!ニュース 3件\n・**18:00** - Google News 3件",
        inline=False
    )
    
    embed.add_field(
        name="💬 その他機能",
        value="・エコー機能（特定チャンネル）\n・👍 リアクション応答",
        inline=False
    )
    
    embed.add_field(
        name="📡 配信チャンネル",
        value=f"<#{GREETING_CHANNEL_ID}>",
        inline=False
    )
    
    embed.set_footer(text="24時間自動配信中 📺")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='news_status', description='ニュース配信の状態を確認します')
async def news_status(interaction: discord.Interaction):
    if interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("このコマンドは指定されたサーバーでのみ使用できます。", ephemeral=True)
        return
    
    now = datetime.now(JST)
    
    embed = discord.Embed(
        title="📊 ニュース配信状態",
        color=0x0099ff
    )
    
    embed.add_field(
        name="⏰ 現在時刻",
        value=now.strftime("%Y-%m-%d %H:%M:%S JST"),
        inline=False
    )
    
    embed.add_field(
        name="📰 配信スケジュール",
        value="朝: 06:00 | 昼: 12:00 | 夜: 18:00",
        inline=False
    )
    
    embed.add_field(
        name="📡 配信チャンネル", 
        value=f"<#{GREETING_CHANNEL_ID}>",
        inline=False
    )
    
    # 次回配信時間を計算
    next_times = []
    for hour in [6, 12, 18]:
        next_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if next_time <= now:
            next_time += timedelta(days=1)
        next_times.append(next_time)
    
    next_broadcast = min(next_times)
    time_until = next_broadcast - now
    
    embed.add_field(
        name="⏭️ 次回配信",
        value=f"{next_broadcast.strftime('%H:%M')} (あと{time_until.seconds//3600}時間{(time_until.seconds//60)%60}分)",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN_NEWS')
    if token:
        bot.run(token)
    else:
        print('DISCORD_TOKEN_NEWSが設定されていません。.env.newsファイルを確認してください。')