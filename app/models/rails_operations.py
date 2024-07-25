import os
import re
import subprocess
import requests
import time

from utils.scraping import Scraping
from utils.local_repo import LocalRepo
from utils.logger import setup_logger

class RailsOperations:
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        self.scraping = Scraping()
        self.local_repo = LocalRepo()

    def start_server(self, repo_name):
        """
        Railsサーバーを起動する関数
        :param repo_name: サーバーを起動するリポジトリ名
        """
        try:
            repo_path = os.path.join('..', 'tmp_clone', repo_name)
            if not os.path.exists(repo_path):
                return {"message": "指定されたリポジトリが存在しません。", "error": "Repo not found"}

            # 環境のセットアップ
            self.setup_environment(repo_path)

            self.logger.info(f"Rails server起動: {repo_path}")
            subprocess.Popen(['rails', 's', '-d', '-p', '4000'], cwd=repo_path)
            
            # サーバー起動まで待機
            is_basic_auth = self.wait_for_server("http://localhost:4000")

            # `routes.rb` からルートパスを取得
            routes_file_path = os.path.join(repo_path, 'config', 'routes.rb')
            self.logger.info(f"routes.rbからルートパス探索: {routes_file_path}")
            app_path = self.local_repo.extract_path_from_routes(routes_file_path)
            if not app_path:
                return {"message": "ルートパスの取得に失敗しました。", "error": "Failed to get route path"}

            app_url = f"http://localhost:4000{app_path}"
            self.logger.info(f"Final URL: {app_url}")
            html_content, css_content = self.scraping.scrape_html_css(app_url, is_basic_auth)
            return {"message": "サーバーが起動しました。", "html": html_content, "css": css_content, "url": app_url}
        except Exception as e:
            self.logger.exception("Error during start_server")
            return {"message": "内部サーバーエラーが発生しました。", "error": str(e)}

    def stop_server(self):
        """
        Railsサーバーを停止する関数
        """
        try:
            self.logger.info("Stopping Rails server")
            # lsof -i:4000 コマンドを実行してプロセスIDを取得
            result = subprocess.run(['lsof', '-i:4000'], stdout=subprocess.PIPE, text=True)
            lines = result.stdout.strip().split('\n')
            
            if len(lines) <= 1:
                self.logger.warning("Rails server process not found.")
                return {"message": "Railsサーバーのプロセスが見つかりませんでした。"}
            
            # 各行からPIDを取得してkillコマンドを実行
            for line in lines[1:]:
                pid = line.split()[1]
                subprocess.run(['kill', '-9', pid])
                self.logger.info(f"Process {pid} killed.")
            
            return {"message": "サーバー停止処理を実行しました。"}

        except Exception as e:
            self.logger.exception("Error stopping Rails server")
            return {"message": "内部サーバーエラーが発生しました。", "error": str(e)}

    def wait_for_server(self, app_url):
        """
        Railsサーバーが起動するまで待機する関数
        :param app_url: 起動先のURL
        """
        self.logger.info(f"Waiting for server to start at: {app_url}")
        while True:
            self.logger.info("wait 5 seconds...")
            time.sleep(5)

            try:
                response = requests.get(app_url)
                if response.status_code == 200:
                    self.logger.info("Server is up and running.")
                    return False
                elif response.status_code == 401:
                    self.logger.info("Server is up and running. Basic authentication is set")
                    return True
            except requests.ConnectionError:
                self.logger.info("Server not reachable yet.")
            except requests.RequestException as e:
                self.logger.error(f"Request error: {e}")

    def setup_environment(self, repo_path):
        """
        Rails環境をセットアップする関数
        :param repo_path: リポジトリのパス
        """
        # 必要なgemがインストールされているか確認し、インストールされていない場合はインストール
        self.install_missing_gems(repo_path)
        
        # bundle install
        self.run_command(['bundle', 'install'], cwd=repo_path)

        # rails db:create
        result = self.run_command(['rails', 'db:create'], cwd=repo_path)
        if "already exists" in result.stderr:
            self.logger.info("Database already exists.")

        # rails db:migrate
        self.run_command(['rails', 'db:migrate'], cwd=repo_path)

        # rails db:seed (ファイルが存在し、コメント以外の内容がある場合)
        seed_file_path = os.path.join(repo_path, 'db', 'seeds.rb')
        if os.path.exists(seed_file_path) and self.local_repo.has_non_comment_lines(seed_file_path):
            self.run_command(['rails', 'db:seed'], cwd=repo_path)
        else:
            self.logger.info("No seed file or file contains only comments.")

    def install_missing_gems(self, repo_path):
        """
        Gemfileに記載されたすべてのgemがインストールされているか確認し、
        インストールされていない場合はインストールする
        :param repo_path: リポジトリのパス
        """
        gemfile_path = os.path.join(repo_path, 'Gemfile')
        gem_pattern = re.compile(r'^(?!\s*#)\s*gem\s+["\']([^"\']+)["\']')

        with open(gemfile_path, 'r') as gemfile:
            for line in gemfile:
                match = gem_pattern.search(line)
                if match:
                    gem_name = match.group(1)
                    result = subprocess.run(['gem', 'list', '-i', gem_name], text=True, capture_output=True)
                    if 'false' in result.stdout:
                        self.logger.info(f"Installing missing gem: {gem_name}")
                        subprocess.run(['gem', 'install', gem_name], text=True)

    def run_command(self, command, cwd=None):
        """
        コマンドを実行して結果をログに記録する関数
        :param command: 実行するコマンド
        :param cwd: コマンドを実行する作業ディレクトリ
        :return: コマンドの標準出力と標準エラー
        """
        self.logger.info(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
        self.logger.info(f"Output: {result.stdout}")
        if result.stderr:
            self.logger.error(f"Error: {result.stderr}")
        return result
