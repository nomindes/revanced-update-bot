import discord
import os
import logging
from discord.ext import tasks

class DiscordView:
    def __init__(self, update_checker):
        self.update_checker = update_checker
        self.logger = logging.getLogger('discord_view')
        
        self.server_id = 1305598058892890303
        self.channel_id = 1351933957838737408
        
        intents = discord.Intents.default()
        self.client = discord.Client(intents=intents)
        
        self.client.event(self.on_ready)
    
    async def on_ready(self):
        self.logger.info(f'{self.client.user}としてログインしました')
        channel = self.client.get_channel(self.channel_id)
        if not channel:
            self.logger.error(f'チャンネルID {self.channel_id} が見つかりません')
            
        if not self.check_updates_task.is_running():
            self.check_updates_task.start()
    
    @tasks.loop(hours=1)
    async def check_updates_task(self):
        try:
            updates = await self.update_checker.check_updates()
            
            if updates:
                channel = self.client.get_channel(self.channel_id)
                if channel:
                    for old_app, new_app in updates:
                        await self.send_update_notification(channel, old_app, new_app)
                else:
                    self.logger.error(f'チャンネルID {self.channel_id} が見つかりません')
        
        except Exception as e:
            self.logger.error(f'アップデート確認中にエラーが発生しました: {e}')
    
    @check_updates_task.before_loop
    async def before_check_updates(self):
        await self.client.wait_until_ready()
    
    async def send_update_notification(self, channel, old_app, new_app):
        embed = discord.Embed(
            title=f"{new_app.name} アップデート通知",
            description=f"{new_app.name} の新しいバージョンが利用可能です！",
            color=discord.Color.green()
        )
        
        embed.add_field(name="前のバージョン", value=old_app.version or "不明", inline=True)
        embed.add_field(name="新しいバージョン", value=new_app.version, inline=True)
        embed.add_field(name="ダウンロード", value="https://vanced.to/", inline=False)
        
        await channel.send(embed=embed)
    
    def start(self):
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            self.logger.error('DISCORD_TOKENが設定されていません')
            return
            
        self.client.run(token)
    
    def stop(self):
        self.check_updates_task.cancel()
        self.client.close()