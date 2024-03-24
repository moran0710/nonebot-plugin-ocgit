import os
import json

from nonebot import logger
import nonebot

def start():
    """
    初始化本模块
    :return: None
    """
    config = nonebot.get_driver().config
    logger.info("[OCGIT] 检查运行环境中....")
    if not os.path.exists('data'):
        logger.warning("[OCGIT] 不存在插件data目录！正在新建在 项目根目录 下")
        os.mkdir('data')
    if not os.path.exists(os.path.join(".", "data", 'ocgit')):
        logger.warning("[OCGIT] 不存在ocgit存储目录！ 正在新建在 项目根目录/ocgit 下")
        os.mkdir(os.path.join(".", "data", "ocgit"))
    if not os.path.exists(os.path.join(".", "data", 'ocgit', "config.json")):
        logger.warning("[OCGIT] 不存在根config.json存储目录！ 正在新建在 项目根目录/ocgit 下")
        with open(os.path.join(".", "data", "ocgit", "config.json"), "w", encoding="utf8") as f:
            json.dump({"group_and_project_list": {}}, f, indent=4)

    count = os.listdir(os.path.join(".", "data", "ocgit"))
    logger.info("[OCGIT] 目录检查完毕，本bot管理的企划数量： {0}  ".format(len(count)))
    logger.info("[OCGIT] 使用qq客户端：{}  ".format(config.qq_platform))
    logger.info("[OCGIT] OCGIT插件正确启动！")
