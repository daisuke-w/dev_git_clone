import streamlit as st
import streamlit.components.v1 as components

from models.git_operations import GitOperations
from models.rails_operations import RailsOperations
from utils.local_repo import LocalRepo
from utils.scraping import Scraping
from utils.logger import setup_logger

class AppView:
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        self.git_ope = GitOperations()
        self.rails_ope = RailsOperations()
        self.local_repo = LocalRepo()
        self.scraping = Scraping()

    def display_app(self):
        self._display_header()
        self._display_clone_form()
        self._initialize_repos()
        self._display_repo_selection()
        self._display_buttons()
        self._display_result()

    def _display_header(self):
        expander = st.expander("ツール概要", True, icon="💡")
        expander.markdown('''
            - 本ツールは以下作業を自動化したものです。\n
                - git clone
                - bundle install (足りないGemはinstall)
                - rails db\:create
                - rails db\:migrate
                - rails db\:seed (seedファイルがある場合)
                - rails s
            - 使用するにはローカル環境にPythonをインストールする必要があります。\n
            - クローンするリポジトリは TECH CAMPのカリキュラムに則ったruby on railsで開発されているものを前提としています。\n
            - 使用する際は自己判断でお願いします。
        ''')
        st.title("GitHubリポジトリクローン")

    def _display_clone_form(self):
        with st.form("clone_form"):
            repo_url = st.text_input("GitHubリポジトリのURL", "")
            clone_button = st.form_submit_button("Clone")
            if clone_button:
                st.session_state.clone_button_clicked = True
                st.session_state.repo_url = repo_url
                with st.spinner("クローンを実行中..."):
                    result = self.git_ope.clone_repo(repo_url)
                st.session_state.result = result.get("message", "クローン処理に失敗しました。")
                st.session_state.repos = result.get("repos", [])

    def _initialize_repos(self):
        if "repos" not in st.session_state:
            st.session_state.repos = self.local_repo.get_repo_list()

    def _display_repo_selection(self):
        repos = st.session_state.get("repos", [])
        st.session_state.selected_repo = st.selectbox("リポジトリを選択", ["選択してください"] + repos, key="repo_select")

    def _display_buttons(self):
        start_button = st.button("Start Server", key="start_button")
        stop_button = st.button("Stop Server", key="stop_button")
        if start_button:
            self._handle_start_server()
        if stop_button:
            self._handle_stop_server()

    def _handle_start_server(self):
        selected_repo = st.session_state.selected_repo
        if selected_repo != "選択してください":
            with st.spinner("サーバーを起動中..."):
                result = self.rails_ope.start_server(selected_repo)
            st.session_state.result = result.get("message", "サーバーの起動に失敗しました。")
            if "html" in result and "css" in result:
                html_content = result["html"]
                css_content = result["css"]
                base_url = result["url"]
                body_content = self.scraping.extract_body_content(html_content)
                self._display_preview(body_content, css_content, base_url)
        else:
            st.session_state.result = "リポジトリを選択してください。"

    def _display_preview(self, body_content, css_content, base_url):
        preview_html = f"""
        <html>
          <head>
            <style>{css_content}</style>
          </head>
          <body>
            {body_content}
          </body>
        </html>
        """
        button_html = f"""
        <a href="{base_url}" target="_blank" style="text-decoration: none;">
            <button style="width: 60px; height: 30px; background-color: #0de459; color: white; border: none; box-shadow: 1px 1px 1px 1px gray; align-items: center; justify-content: center; cursor: pointer;">
            Open</button>
        </a>
        """
        st.divider()
        st.header("Railsアプリプレビュー")
        st.write("""
        ・こちらはプレビューです、画像の表示や一部スタイルが崩れている場合があります。\n
        ・プレビュー内のボタン等は操作できません。\n
        ・正式なサイトを閲覧する場合は「Railsアプリを別タブで開く」のボタンを押してください。
        """)
        components.html(preview_html, height=300, scrolling=True)
        st.divider()
        st.header("Railsアプリを別タブで開く")
        components.html(button_html)

    def _handle_stop_server(self):
        with st.spinner("サーバーを停止中..."):
            result = self.rails_ope.stop_server()
        st.session_state.result = result.get("message", "サーバーの停止に失敗しました。")

    def _display_result(self):
        if "result" not in st.session_state:
            st.session_state.result = ""
        st.empty().divider()
        st.empty().write(st.session_state.result)