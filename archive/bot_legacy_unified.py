import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv
from datetime import time, datetime, timezone, timedelta
import aiohttp
import xml.etree.ElementTree as ET
import io

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_GUILD_ID = 1397720381149806723
GREETING_CHANNEL_ID = 1398171685613469746
OBSIDIAN_CHANNEL_ID = 1398238810730664056
ECHO_CHANNEL_ID = 1397720382236135446  # エコー機能を使用するチャンネル
FILE_DOWNLOAD_CHANNEL_ID = 1398171685613469746  # ファイルダウンロード用チャンネル
NHK_RSS_URL = 'https://www.nhk.or.jp/rss/news/cat0.xml'
YAHOO_RSS_URL = 'https://news.yahoo.co.jp/rss/topics/top-picks.xml'
GOOGLE_NEWS_URL = 'https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja'
OBSIDIAN_VAULT_PATH = os.getenv('OBSIDIAN_VAULT_PATH', "/tmp/daily_notes/")

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))

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

def ensure_obsidian_directory():
    """Obsidianディレクトリが存在することを確認し、なければ作成"""
    try:
        os.makedirs(OBSIDIAN_VAULT_PATH, exist_ok=True)
        print(f"✅ ベースディレクトリ確認完了: {OBSIDIAN_VAULT_PATH}")
    except Exception as e:
        print(f"❌ ベースディレクトリ作成エラー: {e}")
        print(f"Railwayではローカルファイルシステムの制限があります")

def get_daily_note_path(date_str):
    """指定した日付のデイリーノートファイルパスを取得"""
    # 日付をスラッシュ形式に変換 (2025-07-25 -> 2025/07/25)
    date_parts = date_str.split('-')
    date_dir = '/'.join(date_parts)  # 2025/07/25
    
    # 日付別ディレクトリのパスを作成
    date_directory = os.path.join(OBSIDIAN_VAULT_PATH, date_dir)
    
    print(f"🗂️ ディレクトリ作成試行: {date_directory}")
    
    try:
        # ディレクトリが存在しない場合は作成
        os.makedirs(date_directory, exist_ok=True)
        print(f"✅ ディレクトリ作成成功: {date_directory}")
        
        # ディレクトリが実際に存在するか確認
        if os.path.exists(date_directory):
            print(f"✅ ディレクトリ存在確認: OK")
        else:
            print(f"❌ ディレクトリ存在確認: NG")
            
    except Exception as e:
        print(f"❌ ディレクトリ作成エラー: {e}")
        # エラーの場合は元のパスに戻す
        return os.path.join(OBSIDIAN_VAULT_PATH, f"{date_str}.md")
    
    # ファイルパスを返す
    file_path = os.path.join(date_directory, f"{date_str}.md")
    print(f"📄 最終ファイルパス: {file_path}")
    return file_path

def get_next_message_number(daily_note_path):
    """デイリーノート内の次のメッセージ番号を取得"""
    if not os.path.exists(daily_note_path):
        return 1
    
    try:
        with open(daily_note_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        max_number = 0
        for line in lines:
            # "- **時刻** 作者: 内容" の形式を探す
            if line.strip().startswith('- **') and '**' in line:
                max_number += 1
        
        return max_number + 1
    except Exception:
        return 1

def create_daily_note_template(date_str):
    """一般的なデイリーノートテンプレートを作成"""
    template = f"""# {date_str}

## 📝 Daily Summary
<!-- 今日の振り返りや重要な出来事をここに記録 -->

## 🎯 Today's Goals
<!-- 今日の目標・タスク -->
- [ ] 

## 📈 Progress & Achievements
<!-- 今日の進捗・達成したこと -->

## 💭 Thoughts & Reflections
<!-- 今日の気づき・学び・感想 -->

## 📋 Discord Messages
<!-- Discord からの記録 -->

"""
    return template

def format_discord_message(message, message_number):
    """DiscordメッセージをMarkdown形式に変換"""
    timestamp = message.created_at.astimezone(JST).strftime("%H:%M")
    author = message.author.display_name
    content = message.content
    
    # メンションを適切にフォーマット
    if message.mentions:
        for mention in message.mentions:
            content = content.replace(f'<@{mention.id}>', f'@{mention.display_name}')
    
    # チャンネルメンションを適切にフォーマット
    if message.channel_mentions:
        for channel in message.channel_mentions:
            content = content.replace(f'<#{channel.id}>', f'#{channel.name}')
    
    # マークダウン形式でフォーマット
    return f"**{timestamp}** *{author}*: {content}"

async def append_to_daily_note(message):
    """メッセージをデイリーノートに追加"""
    try:
        ensure_obsidian_directory()
        
        # 日本時間での日付を取得
        jst_date = message.created_at.astimezone(JST)
        date_str = jst_date.strftime("%Y-%m-%d")
        daily_note_path = get_daily_note_path(date_str)
        
        # フォーマットされたメッセージ
        message_number = get_next_message_number(daily_note_path)
        formatted_message = format_discord_message(message, message_number)
        
        # ファイルが存在しない場合、テンプレートを作成
        if not os.path.exists(daily_note_path):
            template = create_daily_note_template(date_str)
            with open(daily_note_path, 'w', encoding='utf-8') as file:
                file.write(template)
            print(f"📝 新しいデイリーノートを作成: {date_str}.md")
        
        # Discord Messagesセクションにメッセージを追加
        with open(daily_note_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Discord Messagesセクションの後に追加
        discord_section = "## 📋 Discord Messages\n<!-- Discord からの記録 -->\n\n"
        if discord_section in content:
            content = content.replace(
                discord_section,
                f"{discord_section}{formatted_message}\n"
            )
        else:
            # セクションが見つからない場合は末尾に追加
            content += f"\n{formatted_message}\n"
        
        # ファイルに書き戻し
        with open(daily_note_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"📄 メッセージを {date_str}.md に保存しました")
        
    except Exception as e:
        print(f"❌ デイリーノート保存エラー: {e}")

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
    print(f'Obsidianデイリーノート保存先: {OBSIDIAN_VAULT_PATH}')
    print(f'監視チャンネルID: {OBSIDIAN_CHANNEL_ID}')
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
    print(f"🔥 on_message呼び出し - 作者: {message.author}")
    
    if message.author == bot.user:
        print(f"🤖 bot自身のメッセージなのでスキップ")
        return
    
    print(f"📋 ギルドID確認 - 受信: {message.guild.id if message.guild else 'なし'}, 期待: {ALLOWED_GUILD_ID}")
    if message.guild.id != ALLOWED_GUILD_ID:
        print(f"❌ ギルドID不一致のためスキップ")
        return
    
    # デバッグ用：すべてのメッセージの詳細を出力
    print(f"✅ メッセージ受信 - チャンネルID: {message.channel.id}, 作者: {message.author.display_name}, 内容: {message.content}")
    
    # 指定されたチャンネルの投稿をObsidianに保存
    if message.channel.id == OBSIDIAN_CHANNEL_ID:
        print(f"✅ Obsidianチャンネル一致！保存処理開始...")
        try:
            await append_to_daily_note(message)
            print(f"✅ Obsidian保存完了")
        except Exception as e:
            print(f"❌ Obsidian保存エラー: {e}")
    else:
        print(f"チャンネルID不一致 - 受信: {message.channel.id}, 期待: {OBSIDIAN_CHANNEL_ID}")
    
    # エコー機能は特定チャンネルでのみ動作
    if message.channel.id == ECHO_CHANNEL_ID:
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

@bot.tree.command(name='obsidian_status', description='Obsidianデイリーノートの状態を確認します')
async def obsidian_status(interaction: discord.Interaction):
    """デイリーノートの現在の状態を表示"""
    if interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("このコマンドは指定されたサーバーでのみ使用できます。", ephemeral=True)
        return
    
    today = datetime.now(JST).strftime("%Y-%m-%d")
    today_note_path = get_daily_note_path(today)
    
    # 日付ディレクトリのパス
    date_parts = today.split('-')
    date_dir = '/'.join(date_parts)
    date_directory = os.path.join(OBSIDIAN_VAULT_PATH, date_dir)
    
    embed = discord.Embed(
        title="📝 Obsidianデイリーノート状態",
        color=0x9f7aea
    )
    
    embed.add_field(
        name="ベースパス",
        value=f"`{OBSIDIAN_VAULT_PATH}`",
        inline=False
    )
    
    embed.add_field(
        name="今日のディレクトリ",
        value=f"`{date_dir}/`",
        inline=False
    )
    
    embed.add_field(
        name="監視チャンネル",
        value=f"<#{OBSIDIAN_CHANNEL_ID}>",
        inline=False
    )
    
    embed.add_field(
        name="今日のノート",
        value=f"`{today}.md`",
        inline=False
    )
    
    embed.add_field(
        name="ファイル存在",
        value="✅ 存在" if os.path.exists(today_note_path) else "❌ 未作成",
        inline=False
    )
    
    embed.add_field(
        name="フルパス",
        value=f"`{today_note_path}`",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='download_note', description='指定した日付のデイリーノートをダウンロード')
async def download_note(interaction: discord.Interaction, date: str = None):
    """デイリーノートを添付ファイルとして送信"""
    if interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("このコマンドは指定されたサーバーでのみ使用できます。", ephemeral=True)
        return
    
    # 日付が指定されていない場合は今日の日付を使用
    if date is None:
        target_date = datetime.now(JST).strftime("%Y-%m-%d")
    else:
        try:
            # 日付形式の検証
            datetime.strptime(date, "%Y-%m-%d")
            target_date = date
        except ValueError:
            await interaction.response.send_message("❌ 日付形式が正しくありません。YYYY-MM-DD形式で入力してください。", ephemeral=True)
            return
    
    try:
        # ファイルパスを取得
        daily_note_path = get_daily_note_path(target_date)
        
        if not os.path.exists(daily_note_path):
            await interaction.response.send_message(f"❌ {target_date} のデイリーノートが見つかりません。", ephemeral=True)
            return
        
        # ファイル内容を読み取り
        with open(daily_note_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # バイトストリームとして準備
        file_data = io.BytesIO(content.encode('utf-8'))
        file_data.seek(0)
        
        # Discordファイルオブジェクトを作成
        discord_file = discord.File(file_data, filename=f"{target_date}.md")
        
        # 埋め込みメッセージを作成
        embed = discord.Embed(
            title="📄 デイリーノートダウンロード",
            description=f"**{target_date}** のデイリーノートです",
            color=0x00ff88
        )
        
        embed.add_field(
            name="📊 統計",
            value=f"文字数: {len(content)} 文字\n行数: {len(content.splitlines())} 行",
            inline=False
        )
        
        embed.add_field(
            name="💾 使用方法",
            value="添付ファイルをダウンロードしてObsidianにインポートしてください",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, file=discord_file)
        print(f"📤 {target_date}.md をDiscordに送信しました")
        
    except Exception as e:
        await interaction.response.send_message(f"❌ ファイル送信エラー: {str(e)}", ephemeral=True)
        print(f"❌ ファイル送信エラー: {e}")

@bot.tree.command(name='list_notes', description='利用可能なデイリーノートの一覧を表示')
async def list_notes(interaction: discord.Interaction):
    """保存されているデイリーノートの一覧を表示"""
    if interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("このコマンドは指定されたサーバーでのみ使用できます。", ephemeral=True)
        return
    
    try:
        ensure_obsidian_directory()
        
        # ノートファイルを検索
        note_files = []
        for root, dirs, files in os.walk(OBSIDIAN_VAULT_PATH):
            for file in files:
                if file.endswith('.md') and file != 'README.md':
                    file_path = os.path.join(root, file)
                    # ファイルサイズを取得
                    file_size = os.path.getsize(file_path)
                    # 作成日時を取得
                    created_time = datetime.fromtimestamp(os.path.getctime(file_path), JST)
                    note_files.append({
                        'name': file,
                        'size': file_size,
                        'created': created_time,
                        'date': file.replace('.md', '') if file.replace('.md', '').count('-') == 2 else 'unknown'
                    })
        
        if not note_files:
            await interaction.response.send_message("📝 まだデイリーノートが作成されていません。", ephemeral=True)
            return
        
        # 日付順でソート
        note_files.sort(key=lambda x: x['date'], reverse=True)
        
        # 埋め込みメッセージを作成
        embed = discord.Embed(
            title="📋 デイリーノート一覧",
            description=f"保存されているデイリーノート: {len(note_files)} 件",
            color=0x9f7aea
        )
        
        # 最新の5件を表示
        recent_notes = note_files[:5]
        note_list = []
        for note in recent_notes:
            size_kb = note['size'] / 1024
            note_list.append(f"📄 `{note['date']}` ({size_kb:.1f}KB)")
        
        embed.add_field(
            name="🕒 最新のノート",
            value="\n".join(note_list) if note_list else "なし",
            inline=False
        )
        
        embed.add_field(
            name="💡 使用方法",
            value="`/download_note YYYY-MM-DD` でファイルをダウンロード\n`/download_note` で今日のノートをダウンロード",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ ノート一覧取得エラー: {str(e)}", ephemeral=True)
        print(f"❌ ノート一覧取得エラー: {e}")

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print('DISCORD_TOKENが設定されていません。.envファイルを確認してください。')