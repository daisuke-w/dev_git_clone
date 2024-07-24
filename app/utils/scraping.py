import os
import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth

from utils.logger import setup_logger

class Scraping:
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)

    def scrape_html_css(self, app_url, is_basic_auth):
        """
        アクセス先のページをスクレイピングする関数
        :param app_url: アクセス先のURL
        :param is_basic_auth: アクセス先がBasic認証を設定しているか
        :return: html, cssの内容
        """
        try:
            self.logger.info(f"Scraping HTML and CSS from: {app_url}")
            if is_basic_auth:
                username = os.environ.get('BASIC_AUTH_USER')
                password = os.environ.get('BASIC_AUTH_PASSWORD')
                response = requests.get(app_url, auth=HTTPBasicAuth(username, password))
            else:
                response = requests.get(app_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                html = soup.prettify()
                css = ""
                for link in soup.find_all('link', rel='stylesheet'):
                    css_url = link.get('href')
                    if css_url:
                        css_url = urljoin(app_url, css_url)
                        css_response = requests.get(css_url)
                        if css_response.status_code == 200:
                            css += css_response.text
                return html, css
            else:
                self.logger.error(f"Failed to scrape HTML and CSS: {response.status_code}")
                return "", ""
        except Exception as e:
            self.logger.exception("Error during scraping HTML and CSS.")
            return "", "", str(e)

    def extract_body_content(self, html_content):
        """
        スクレイピングした結果からbodyの内容を抽出する関数
        :param html_content: htmlの内容
        :return: bodyの中身
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        # コメント文の除去
        for comment in soup(text=lambda x: isinstance(x, Comment)):
            comment.extract()

        body = soup.find('body')
        if body:
            # <body> タグ内のコンテンツを取り出し、<body> タグを取り除く
            body_content = ''.join(str(child) for child in body.contents)
            return body_content
        return html_content
