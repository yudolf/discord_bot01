import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_CHANNEL_ID = 1398171685613469746

@bot.event
async def on_ready():
    print(f'{bot.user}としてログインしました！')
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)}個のスラッシュコマンドを同期しました')
    except Exception as e:
        print(f'スラッシュコマンドの同期に失敗しました: {e}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return
    
    await message.channel.send('こんにちは！ハロー！')
    
    await bot.process_commands(message)

@bot.tree.command(name='help', description='このbotの使い方を表示します')
async def help_command(interaction: discord.Interaction):
    if interaction.channel.id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message("このコマンドは指定されたチャンネルでのみ使用できます。", ephemeral=True)
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