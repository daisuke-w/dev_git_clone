import os
import re
from utils.logger import setup_logger

class LocalRepo:
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
    
    def get_repo_list(self):
        """
        tmp_clone配下のリポジトリ名を取得する関数
        :return: リポジトリ名のリスト
        """
        repos_path = os.path.join('..', 'tmp_clone')
        if os.path.exists(repos_path):
            return [d for d in os.listdir(repos_path) if os.path.isdir(os.path.join(repos_path, d))]
        return []
    
    def has_non_comment_lines(self, file_path):
        """
        ファイルがコメント以外の行を含んでいるかどうかを確認する関数
        :param file_path: チェックするファイルのパス
        :return: コメント以外の行が存在する場合は True、それ以外は False
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    # コメント行でない場合
                    if line.strip() and not line.strip().startswith('#'):
                        return True
        except Exception:
            self.logger.exception(f"Error reading file {file_path}")
        return False
    
    def extract_path_from_routes(self, routes_file_path):
        """
        `routes.rb` ファイルからルートパスを抽出する関数
        :param routes_file_path: `routes.rb` ファイルのパス
        :return: ルートパスの文字列。見つからない場合は None
        """
        try:
            with open(routes_file_path, 'r') as file:
                content = file.read()
                
                # root の設定を探す
                root_pattern = r"root"
                root_match = re.search(root_pattern, content)
                self.logger.info(f"Root match: {root_match}")
                if root_match:
                    return '/'  # root はトップレベルパスなので / を返す
                
                # `get 'path', to: 'controller#index'` の形式を探す
                path_pattern = rf"get\s+'([^']+)',\s+to:\s+'([^']+#index)'"
                path_match = re.search(path_pattern, content)
                self.logger.info(f"Path match: {path_match}")
                if path_match:
                    return f'/{path_match.group(1)}'
                
                # どちらも見つからない場合は None
                return None
        
        except Exception as e:
            self.logger.exception(f"Error reading file {routes_file_path}: {e}")
            return None
