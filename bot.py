import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_GUILD_ID = 1397720381149806723

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
    
    if message.guild.id != ALLOWED_GUILD_ID:
        return
    
    # メンションまたはリプライの場合のみ反応
    if bot.user in message.mentions or (message.reference and message.reference.resolved and message.reference.resolved.author == bot.user):
        await message.channel.send(message.content)
    
    await bot.process_commands(message)

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