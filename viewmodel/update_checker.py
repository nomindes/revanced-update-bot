import aiohttp
import asyncio
import re
import logging
from bs4 import BeautifulSoup

from model.app_model import AppInfo

class UpdateChecker:
    def __init__(self, app_model):
        self.app_model = app_model
        self.logger = logging.getLogger('update_checker')
        
    async def check_updates(self):
        try:
            html_content = await self._fetch_website()
            if not html_content:
                return []
                
            updates = []
            
            yt_version = self._extract_youtube_revanced_version(html_content)
            if yt_version:
                old_app, new_app, needs_update = self.app_model.update_app_info("YouTube ReVanced", yt_version)
                if needs_update:
                    updates.append((old_app, new_app))
            
            microg_version = self._extract_microg_version(html_content)
            if microg_version:
                old_app, new_app, needs_update = self.app_model.update_app_info("MicroG", microg_version)
                if needs_update:
                    updates.append((old_app, new_app))
            
            return updates
            
        except Exception as e:
            self.logger.error(f"アップデートチェック中にエラーが発生しました: {e}")
            return []
    
    async def _fetch_website(self):
        url = "https://vanced.to/"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        self.logger.error(f"ウェブサイトの取得に失敗しました。ステータスコード: {response.status}")
                        return None
        except aiohttp.ClientError as e:
            self.logger.error(f"ウェブサイトへの接続中にエラーが発生しました: {e}")
            return None
    
    def _extract_youtube_revanced_version(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        youtube_link = soup.find('a', href='/youtube-revanced')
        if youtube_link:
            text = youtube_link.get_text(strip=True)
            match = re.search(r'YouTube ReVanced (\d+\.\d+\.\d+)', text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_microg_version(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        microg_link = soup.find('a', href='/gmscore-microg')
        if microg_link:
            text = microg_link.get_text(strip=True)
            match = re.search(r'MicroG ([\d\.]+)', text)
            if match:
                return match.group(1)
        
        return None