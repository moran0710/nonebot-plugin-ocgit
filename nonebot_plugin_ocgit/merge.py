import json
import os

import nonebot
from nonebot import on_command
from nonebot.params import T_State, ArgStr
from nonebot.adapters.onebot.v11 import Bot, Event

from .utils import get_all_branch, get_project_name, get_admin_list

import git

merge = on_command("ocgit 合并", aliases={"ocgit merge"})


@merge.handle()
async def merger_1st(event: Event, bot: Bot, state=T_State):
    project_name = await get_project_name(event)
    with open(os.path.join(".", "data", "ocgit", project_name, "config.json"), "r", encoding="utf-8") as f:
        superusers = json.load(f)["project_admin"]
    if event.user_id not in superusers:
        await merge.finish("你没有权限！")
    await merge.send("合并分支向导....")
    branches = get_all_branch(project_name)
    msg = "---------已有的用户分支---------\n"
    count = 1
    branch_list = []
    for branch in branches:
        if branch == "master":
            continue
        else:
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=branch)
            username = user_info["nickname"]
        msg += f"{count}. {username}\n"
        branch_list.append(branch)
        count += 1
    state["branch_list"] = branch_list
    await merge.send(msg + "-------------------------")

@merge.got("chosen", prompt="请输入你想合并到正式版本的用户分支")
async def merge_2nd(event: Event, bot: Bot, state: T_State, chosen=ArgStr()):
    chosen = int(chosen)
    project_name = await get_project_name(event)
    branch = state["branch_list"][chosen-1]
    repo = git.Repo(os.path.join(".", "data", "ocgit", project_name))
    await merge.send("正在处理合并....")
    repo.git.checkout("master")
    repo.git.merge(branch)
    await merge.send("已经完成分支合并！")
