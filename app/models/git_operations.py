import os
from utils.logger import setup_logger

class GitOperations:
    def __init__(self):
        # ロガーの設定
        self.logger = setup_logger(self.__class__.__name__)

    def clone_repo(self, repo_url):
        """
        git cloneを実行する関数
        
        :param repo_url: リポジトリのURL
        :return: クローン結果とリポジトリリストを含む辞書
        """
        try:
            # クローン先のディレクトリ設定
            repo_name = os.path.basename(repo_url).replace('.git', '')
            clone_dir = os.path.join('..', 'tmp_clone', repo_name)
            
            # 既存のディレクトリがあれば削除
            if os.path.exists(clone_dir):
                self.logger.info(f"ディレクトリ削除: {clone_dir}")
                os.system(f'rm -rf {clone_dir}')
            
            # リポジトリのクローン作成
            os.makedirs(clone_dir, exist_ok=True)
            self.logger.info(f"クローン作成: {clone_dir}")
            os.system(f'git clone {repo_url} {clone_dir}')

            # クローンしたリポジトリのリスト取得
            repos_path = os.path.join('..', 'tmp_clone')
            repos = [d for d in os.listdir(repos_path) if os.path.isdir(os.path.join(repos_path, d))]
            return {"message": "リポジトリのクローンを完了しました。", "repos": repos}

        except Exception as e:
            self.logger.exception("Error during clone_repo")
            return {"message": "内部サーバーエラーが発生しました。", "error": str(e)}
