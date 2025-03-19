class AppInfo:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        
    def __eq__(self, other):
        if not isinstance(other, AppInfo):
            return False
        return self.name == other.name and self.version == other.version
    
    def __str__(self):
        return f"{self.name} {self.version}"


import json
import os
import logging

class AppModel:
    def __init__(self):
        self.logger = logging.getLogger('app_model')
        self.youtube_revanced = AppInfo("YouTube ReVanced", "")
        self.microg = AppInfo("MicroG", "")
        self.state_file = "app_state.json"
        self.load_state()
    
    def load_state(self):
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.youtube_revanced.version = data.get("youtube_revanced", "")
                    self.microg.version = data.get("microg", "")
                    self.logger.info(f"状態を読み込みました: YT={self.youtube_revanced.version}, MicroG={self.microg.version}")
        except Exception as e:
            self.logger.error(f"状態の読み込み中にエラーが発生しました: {e}")
    
    def save_state(self):
        try:
            data = {
                "youtube_revanced": self.youtube_revanced.version,
                "microg": self.microg.version
            }
            with open(self.state_file, 'w') as f:
                json.dump(data, f)
            self.logger.info(f"状態を保存しました: YT={self.youtube_revanced.version}, MicroG={self.microg.version}")
        except Exception as e:
            self.logger.error(f"状態の保存中にエラーが発生しました: {e}")
    
    def update_app_info(self, app_name, new_version):
        needs_save = False
        old_app = None
        new_app = None
        update_needed = False
        
        if app_name == "YouTube ReVanced":
            old_version = self.youtube_revanced.version
            update_needed = old_version != "" and old_version != new_version
            self.youtube_revanced.version = new_version
            old_app = AppInfo(app_name, old_version)
            new_app = AppInfo(app_name, new_version)
            needs_save = True
        
        elif app_name == "MicroG":
            old_version = self.microg.version
            update_needed = old_version != "" and old_version != new_version
            self.microg.version = new_version
            old_app = AppInfo(app_name, old_version)
            new_app = AppInfo(app_name, new_version)
            needs_save = True
        
        if needs_save:
            self.save_state()
            
        return old_app, new_app, update_needed