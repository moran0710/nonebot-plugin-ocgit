from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.log import logger
import nonebot
from nonebot.params import ArgStr
from nonebot.typing import T_State

from .utils import zip_dir, get_all_branch, get_project_name

import os
import json
import time

import git

config = nonebot.get_driver().config
uploader = on_command("ocgit 更新文件", aliases={"ocgit update", "ocgit upload", "ocgit 上传"})


@uploader.handle()
async def upload_st(bot: Bot, event: Event, state: T_State):
    project_name = await get_project_name(event)
    state["project_name"] = project_name
    # 获取分支
    branches = get_all_branch(project_name)
    msg = "---------已有的用户分支---------\n"
    count = 1
    branch_list = []
    for branch in branches:
        if branch == "master":
            username = "主分支（正式发布版）"
        else:
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=branch)
            username = user_info["nickname"]
        msg += f"{count}. {username}\n"
        branch_list.append(branch)
        count += 1
    state["branch_list"] = branch_list
    await uploader.send(msg + "-------------------------")


@uploader.got("branch", prompt="请选择你想查看的分支")
async def upload(state: T_State, bot: Bot, event: Event, branch=ArgStr()):
    chosen = int(branch)
    project_name = state["project_name"]
    branch_list = state["branch_list"]
    repo = git.Repo(os.path.join(".", "data", "ocgit", project_name))
    repo.git.checkout(branch_list[chosen - 1])
    await uploader.send("正在上传压缩包....\n\n（开发者碎碎念）\n由于lagrange实现问题，"
                        "暂时只能上传当前的企划文件压缩包，所有驱动器都这样实现先orz")
    filename = f"{project_name}_分支{branch_list[chosen - 1]}_更新日期{time.strftime('%Y-%m-%d', time.localtime())}.zip"
    try:
        zip_dir(os.path.join(".", "data", "ocgit", project_name, "project"),
                os.path.join(".", "data", "ocgit", project_name, "cache",
                             filename))
    except PermissionError:
        await uploader.finish("[ERROR] data目录权限不足！你需要关闭项目文件夹的只读模式，或使用chmod")
    try:
        await bot.call_api("upload_group_file", group_id=event.group_id,
                           file=str(os.path.join("..", "bot09", "data", "ocgit", project_name, "cache", filename)),
                           name=filename)
    except nonebot.adapters.onebot.v11.exception.ActionFailed:
        await bot.call_api("upload_group_file", group_id=event.group_id,
                           file=str(os.path.join("data", "ocgit", project_name, "cache", filename)),
                           name=filename)
    except nonebot.adapters.onebot.v11.exception.NetworkError:
        await uploader.send("[ERROR] 上传可能超时，但是由于拉格朗实现特性，也可能成功，如果长时间没成功上传请查看bot日志")
    finally:
        os.remove(os.path.join(".", "data", "ocgit", project_name, "cache", filename))
    logger.info(f"[ocgit] 企划 {project_name} 完成一次压缩包上传")
