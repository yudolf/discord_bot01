import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import io

load_dotenv('.env.obsidian')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 設定
ALLOWED_GUILD_ID = 1397720381149806723
OBSIDIAN_CHANNEL_ID = 1398238810730664056

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))

# メモリ上でメッセージを管理
daily_messages = {}  # {date_str: [messages...]}
sent_files = set()  # 送信済みファイルの日付を記録

def add_message_to_memory(message):
    """メッセージをメモリに追加"""
    # 日本時間での日付を取得
    jst_date = message.created_at.astimezone(JST)
    date_str = jst_date.strftime("%Y-%m-%d")
    
    # 日付ごとにメッセージをグループ化
    if date_str not in daily_messages:
        daily_messages[date_str] = []
    
    # メッセージ情報を保存
    message_data = {
        'timestamp': message.created_at.astimezone(JST),
        'author': message.author.display_name,
        'content': message.content,
        'message_id': message.id
    }
    
    daily_messages[date_str].append(message_data)
    print(f"📝 メッセージをメモリに追加: {date_str} - {message.author.display_name}")

def get_available_dates():
    """利用可能な日付の一覧を取得"""
    return sorted(daily_messages.keys(), reverse=True)

async def auto_generate_and_send(channel, date_str):
    """指定日のマークダウンファイルを自動生成して送信（重複防止）"""
    try:
        if date_str not in daily_messages or not daily_messages[date_str]:
            return
        
        # 重複チェック: この日付のファイルを既に送信済みかどうか
        if date_str in sent_files:
            print(f"⏭️ {date_str} のファイルは送信済みのためスキップ")
            return
        
        # マークダウンコンテンツを生成
        content = generate_markdown_content(date_str)
        
        # バイトストリームとして準備
        content_bytes = content.encode('utf-8')
        file_data = io.BytesIO(content_bytes)
        file_data.seek(0)
        
        # Discordファイルオブジェクトを作成
        discord_file = discord.File(file_data, filename=f"{date_str}.md")
        
        # 簡潔なメッセージで送信
        message_count = len(daily_messages[date_str])
        await channel.send(f"📄 **{date_str}** のマークダウンファイルを生成しました ({message_count}件のメッセージ)", file=discord_file)
        
        # 送信済みとして記録
        sent_files.add(date_str)
        print(f"🤖 自動生成完了: {date_str}.md ({message_count}件)")
        
    except Exception as e:
        print(f"❌ 自動生成エラー: {e}")
        await channel.send(f"❌ マークダウンファイルの生成に失敗しました: {str(e)}")

def generate_markdown_content(date_str):
    """指定日のメッセージからマークダウンコンテンツを生成"""
    if date_str not in daily_messages or not daily_messages[date_str]:
        return f"# {date_str}\n\nこの日のメッセージはありません。"
    
    messages = daily_messages[date_str]
    
    # マークダウンコンテンツを生成
    content = f"# {date_str}\n\n"
    content += f"## 📋 Discord Messages ({len(messages)} 件)\n\n"
    
    for msg in messages:
        timestamp = msg['timestamp'].strftime("%H:%M")
        author = sanitize_content(msg['author'][:50])
        message_content = sanitize_content(msg['content'])
        
        content += f"**{timestamp}** *{author}*: {message_content}\n\n"
    
    return content

def sanitize_content(content):
    """コンテンツをサニタイズ"""
    # セキュリティ: 長さ制限
    MAX_CONTENT_LENGTH = 2000
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "...(省略)"
    
    # セキュリティ: 危険な文字をエスケープ
    content = content.replace('`', '\\`')  # コードブロック防止
    content = content.replace('[', '\\[')  # リンク防止
    content = content.replace(']', '\\]')
    
    return content



@bot.event
async def on_ready():
    print(f'{bot.user}としてログインしました！(ObsidianBot)')
    print(f'監視チャンネルID: {OBSIDIAN_CHANNEL_ID}')
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)}個のスラッシュコマンドを同期しました')
    except Exception as e:
        print(f'スラッシュコマンドの同期に失敗しました: {e}')
    
    print('📝 Discordメッセージ収集機能を開始しました')

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
    
    # 指定されたチャンネルの投稿をメモリに保存
    if message.channel.id == OBSIDIAN_CHANNEL_ID:
        print(f"✅ 対象チャンネル一致！メモリに保存...")
        try:
            # メッセージをメモリに保存
            add_message_to_memory(message)
            print(f"✅ メモリ保存完了")
            
            # 自動でマークダウンファイルを生成して送信
            jst_date = message.created_at.astimezone(JST)
            date_str = jst_date.strftime("%Y-%m-%d")
            await auto_generate_and_send(message.channel, date_str)
            
        except Exception as e:
            print(f"❌ メモリ保存・自動生成エラー: {e}")
    else:
        print(f"チャンネルID不一致 - 受信: {message.channel.id}, 期待: {OBSIDIAN_CHANNEL_ID}")
    
    await bot.process_commands(message)

@bot.tree.command(name='obsidian_status', description='メッセージ収集の状態を確認します')
async def obsidian_status(interaction: discord.Interaction):
    """メッセージ収集の現在の状態を表示"""
    if interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("このコマンドは指定されたサーバーでのみ使用できます。", ephemeral=True)
        return
    
    today = datetime.now(JST).strftime("%Y-%m-%d")
    today_count = len(daily_messages.get(today, []))
    
    embed = discord.Embed(
        title="📝 メッセージ収集状態",
        color=0x9f7aea
    )
    
    embed.add_field(
        name="監視チャンネル",
        value=f"<#{OBSIDIAN_CHANNEL_ID}>",
        inline=False
    )
    
    embed.add_field(
        name="今日の収集メッセージ数",
        value=f"{today_count} 件",
        inline=False
    )
    
    embed.add_field(
        name="総収集日数",
        value=f"{len(daily_messages)} 日",
        inline=False
    )
    
    available_dates = get_available_dates()
    if available_dates:
        recent_dates = available_dates[:5]
        dates_list = []
        for date in recent_dates:
            count = len(daily_messages[date])
            dates_list.append(f"`{date}` ({count}件)")
        
        embed.add_field(
            name="最近の収集日",
            value="\n".join(dates_list),
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='download_note', description='指定した日付のメッセージをマークダウンファイルでダウンロード')
async def download_note(interaction: discord.Interaction, date: str = None):
    """指定日のメッセージをマークダウンファイルとして送信"""
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
        # 指定日のメッセージが存在するかチェック
        if target_date not in daily_messages or not daily_messages[target_date]:
            await interaction.response.send_message(f"❌ {target_date} のメッセージが見つかりません。", ephemeral=True)
            return
        
        # マークダウンコンテンツを生成
        content = generate_markdown_content(target_date)
        
        # セキュリティ: ファイルサイズ制限 (Discordの上限は25MB)
        MAX_FILE_SIZE = 24 * 1024 * 1024  # 24MB
        content_bytes = content.encode('utf-8')
        
        if len(content_bytes) > MAX_FILE_SIZE:
            await interaction.response.send_message(f"❌ ファイルサイズが大きすぎます ({len(content_bytes)/1024/1024:.1f}MB)。25MB以下にしてください。", ephemeral=True)
            return
        
        # バイトストリームとして準備
        file_data = io.BytesIO(content_bytes)
        file_data.seek(0)
        
        # Discordファイルオブジェクトを作成
        discord_file = discord.File(file_data, filename=f"{target_date}.md")
        
        # 埋め込みメッセージを作成
        message_count = len(daily_messages[target_date])
        embed = discord.Embed(
            title="📄 メッセージダウンロード",
            description=f"**{target_date}** のメッセージです",
            color=0x00ff88
        )
        
        embed.add_field(
            name="📊 統計",
            value=f"メッセージ数: {message_count} 件\n文字数: {len(content)} 文字",
            inline=False
        )
        
        embed.add_field(
            name="💾 使用方法",
            value="添付ファイルをダウンロードしてObsidianにインポートしてください",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, file=discord_file)
        
        # 手動送信時は送信済み記録をリセット（再生成を可能にする）
        if target_date in sent_files:
            sent_files.remove(target_date)
        
        print(f"📤 {target_date}.md をDiscordに送信しました ({message_count}件のメッセージ)")
        
    except Exception as e:
        await interaction.response.send_message(f"❌ ファイル送信エラー: {str(e)}", ephemeral=True)
        print(f"❌ ファイル送信エラー: {e}")

@bot.tree.command(name='list_notes', description='収集済みメッセージの一覧を表示')
async def list_notes(interaction: discord.Interaction):
    """収集済みメッセージの一覧を表示"""
    if interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("このコマンドは指定されたサーバーでのみ使用できます。", ephemeral=True)
        return
    
    try:
        if not daily_messages:
            await interaction.response.send_message("📝 まだメッセージが収集されていません。", ephemeral=True)
            return
        
        # 埋め込みメッセージを作成
        embed = discord.Embed(
            title="📋 収集済みメッセージ一覧",
            description=f"収集されているメッセージ: {len(daily_messages)} 日分",
            color=0x9f7aea
        )
        
        # 最新の10件を表示
        available_dates = get_available_dates()
        recent_dates = available_dates[:10]
        note_list = []
        for date in recent_dates:
            count = len(daily_messages[date])
            note_list.append(f"📄 `{date}` ({count}件)")
        
        embed.add_field(
            name="🕒 最新の収集日",
            value="\n".join(note_list) if note_list else "なし",
            inline=False
        )
        
        embed.add_field(
            name="💡 使用方法",
            value="`/download_note YYYY-MM-DD` でマークダウンファイルをダウンロード\n`/download_note` で今日のメッセージをダウンロード",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ 一覧取得エラー: {str(e)}", ephemeral=True)
        print(f"❌ 一覧取得エラー: {e}")

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN_OBSIDIAN')
    if token:
        bot.run(token)
    else:
        print('DISCORD_TOKEN_OBSIDIANが設定されていません。.env.obsidianファイルを確認してください。')