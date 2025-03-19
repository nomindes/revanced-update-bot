import asyncio
import logging
import argparse
import os
from aiohttp import web
from model.app_model import AppInfo

class UpdateSimulator:
    def __init__(self, app_model, update_checker):
        self.app_model = app_model
        self.update_checker = update_checker
        self.logger = logging.getLogger('update_simulator')
        
        self.app = web.Application()
        self.app.router.add_get('/', self.handle_root)
        
        self.parser = argparse.ArgumentParser(description='アップデートシミュレーター')
        self.parser.add_argument('--yt-version', type=str, help='YouTube ReVancedの新しいバージョン')
        self.parser.add_argument('--microg-version', type=str, help='MicroGの新しいバージョン')
        
    async def handle_root(self, request):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vanced.to - Mock</title>
        </head>
        <body>
            <div>
                <a href="/youtube-revanced" class="block bg-red-600 text-white text-center py-3 px-6 rounded-lg hover:bg-red-700 transition duration-300">
                    YouTube ReVanced {self.youtube_revanced_version}
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 ml-2 inline-block">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" x2="12" y1="15" y2="3"></line>
                    </svg>
                </a>
            </div>
            <div>
                <a href="/gmscore-microg" class="block bg-green-600 text-white text-center py-3 px-6 rounded-lg hover:bg-green-700 transition duration-300">
                    MicroG {self.microg_version}
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 ml-2 inline-block">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" x2="12" y1="15" y2="3"></line>
                    </svg>
                </a>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html_content, content_type='text/html')
    
    async def simulate_update(self, app_name=None, new_version=None):
        if app_name == "YouTube ReVanced" and new_version:
            self.youtube_revanced_version = new_version
            self.logger.info(f"YouTube ReVancedのバージョンを {new_version} に更新")
            
        elif app_name == "MicroG" and new_version:
            self.microg_version = new_version
            self.logger.info(f"MicroGのバージョンを {new_version} に更新")
        
        updates = await self.update_checker.check_updates()
        return updates
    
    async def start_server(self, host='localhost', port=8080):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        self.logger.info(f"モックサーバーが http://{host}:{port}/ で起動しました")
        return runner
    
    async def interactive_cli(self):
        print("\n===== アップデートシミュレーター =====")
        print("1. YouTube ReVancedのバージョンを変更")
        print("2. MicroGのバージョンを変更")
        print("3. 現在のバージョンを表示")
        print("4. 状態ファイルをリセット")
        print("5. 終了")
        
        while True:
            try:
                choice = input("\n選択してください (1-5): ")
                
                if choice == '1':
                    new_version = input("YouTube ReVancedの新しいバージョンを入力してください: ")
                    updates = await self.simulate_update("YouTube ReVanced", new_version)
                    if updates:
                        print("更新が検出されました:", updates)
                    else:
                        print("更新は検出されませんでした")
                
                elif choice == '2':
                    new_version = input("MicroGの新しいバージョンを入力してください: ")
                    updates = await self.simulate_update("MicroG", new_version)
                    if updates:
                        print("更新が検出されました:", updates)
                    else:
                        print("更新は検出されませんでした")
                
                elif choice == '3':
                    print(f"現在のバージョン:")
                    print(f"YouTube ReVanced: {self.youtube_revanced_version}")
                    print(f"MicroG: {self.microg_version}")
                
                elif choice == '4':
                    if os.path.exists(self.app_model.state_file):
                        os.remove(self.app_model.state_file)
                        print(f"状態ファイル {self.app_model.state_file} を削除しました")
                    self.app_model.youtube_revanced.version = ""
                    self.app_model.microg.version = ""
                    print("アプリの状態をリセットしました")
                
                elif choice == '5':
                    print("シミュレーターを終了します。")
                    break
                
                else:
                    print("無効な選択です。1から5までの数字を入力してください。")
            
            except KeyboardInterrupt:
                print("\nシミュレーターを終了します。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
    
    async def run(self, yt_version=None, microg_version=None):
        runner = await self.start_server()
        
        try:
            if yt_version or microg_version:
                if yt_version:
                    await self.simulate_update("YouTube ReVanced", yt_version)
                if microg_version:
                    await self.simulate_update("MicroG", microg_version)
                
                updates = await self.update_checker.check_updates()
                if updates:
                    print("更新が検出されました:", updates)
                else:
                    print("更新は検出されませんでした")
            
            await self.interactive_cli()
        
        finally:
            await runner.cleanup()

def run_simulator(app_model, update_checker, yt_version=None, microg_version=None):
    simulator = UpdateSimulator(app_model, update_checker)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(simulator.run(yt_version, microg_version))
    except KeyboardInterrupt:
        pass