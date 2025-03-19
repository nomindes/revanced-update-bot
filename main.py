import os
import sys
import logging
import argparse
from dotenv import load_dotenv

from model.app_model import AppModel
from viewmodel.update_checker import UpdateChecker
from view.discord_view import DiscordView
from debug.simulator import run_simulator

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log', encoding='utf-8')
        ]
    )

def main():
    load_dotenv()
    
    setup_logging()
    logger = logging.getLogger('main')
    
    parser = argparse.ArgumentParser(description='YouTube ReVanced & MicroG アップデート通知Bot')
    parser.add_argument('--debug', action='store_true', help='デバッグモードで実行')
    parser.add_argument('--check-only', action='store_true', help='アップデートをチェックして終了')
    parser.add_argument('--yt-version', type=str, help='YouTube ReVancedの新しいバージョン（デバッグモード用）')
    parser.add_argument('--microg-version', type=str, help='MicroGの新しいバージョン（デバッグモード用）')
    args = parser.parse_args()
    
    app_model = AppModel()
    update_checker = UpdateChecker(app_model)
    
    if args.debug:
        logger.info("デバッグモードで起動")
        import asyncio
        from aiohttp import ClientSession
        
        original_fetch = update_checker._fetch_website
        
        async def mock_fetch_website():
            try:
                async with ClientSession() as session:
                    async with session.get('http://localhost:8080/') as response:
                        if response.status == 200:
                            return await response.text()
                        else:
                            logger.error(f"モックサーバーからのレスポンスエラー: {response.status}")
                            return None
            except Exception as e:
                logger.error(f"モックサーバー接続エラー: {e}")
                return None
        
        update_checker._fetch_website = mock_fetch_website
        
        run_simulator(app_model, update_checker, args.yt_version, args.microg_version)
        
        update_checker._fetch_website = original_fetch
        
        return
    
    if args.check_only:
        logger.info("アップデートチェックのみモードで実行")
        import asyncio
        
        async def check_once():
            logger.info(f"現在のバージョン: YouTube ReVanced={app_model.youtube_revanced.version}, MicroG={app_model.microg.version}")
            
            updates = await update_checker.check_updates()
            if updates:
                for old_app, new_app in updates:
                    logger.info(f"更新が見つかりました: {old_app.name} {old_app.version} -> {new_app.version}")
            else:
                logger.info("更新は見つかりませんでした")
                
            logger.info(f"更新後のバージョン: YouTube ReVanced={app_model.youtube_revanced.version}, MicroG={app_model.microg.version}")
        
        asyncio.run(check_once())
        return
    
    logger.info("Discord Botを起動します")
    
    if not os.getenv('DISCORD_TOKEN'):
        logger.error("DISCORD_TOKENが設定されていません。.envファイルを確認してください。")
        sys.exit(1)
    
    discord_view = DiscordView(update_checker)
    try:
        discord_view.start()
    except KeyboardInterrupt:
        logger.info("Botを終了します")
        discord_view.stop()
    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {e}")
        discord_view.stop()

if __name__ == "__main__":
    main()