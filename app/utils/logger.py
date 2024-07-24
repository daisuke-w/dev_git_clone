import logging

def setup_logger(name):
    """
    ロガーの設定を行う関数
    :param name: ロガーの名前
    :return: 設定されたロガーオブジェクト
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger