import json
import os
import time

import git

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.params import ArgStr
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

from .utils import get_admin_list

new_project = on_command("新建企划", rule=to_me(), aliases={"new_planing", "init"}, permission=SUPERUSER)


@new_project.handle()
async def init_func():
    await new_project.send("欢迎使用nb-ocgit插件\n现在进入新建企划向导：")


@new_project.got("project_name", prompt="[?]请输入企划名字，这将用于标识企划")
@new_project.got("project_qgroup_id", prompt="[?]此企划绑定到哪个qq群?\n如果就绑定到当前群，请回复0")
async def np(bot: Bot, event: Event,
             project_name=ArgStr(),
             project_qgroup_id=ArgStr(),
             ):
    project_name = project_name.replace("\n", "")
    await new_project.send(f"正在在bot目录/data/ocgit/{project_name} 目录下新建企划{project_name}....")
    # q群重写（当前群）
    if project_qgroup_id == "0":
        project_qgroup_id = str(event.group_id)
    logger.info(project_qgroup_id)

    # 防呆接口1 防止不存在这个群
    group_list = await bot.get_group_list()
    for group in group_list:
        if str(group["group_id"]) == project_qgroup_id:
            break
    else:
        await new_project.finish("[ERROR] 出现错误！机器人不在你绑定的qq群内，无法绑定！")

    # 防呆接口2 一个群只能绑定一个企划
    with open(os.path.join(".", "data", "ocgit", "config.json"), "r", encoding="utf8") as f:
        global_config = json.load(f)
    if project_qgroup_id in global_config["group_and_project_list"]:
        await new_project.finish(
            f"[ERROR] 出现错误！这个q群已经绑定了一个企划 {global_config['group_and_project_list'][project_qgroup_id]}！")

    # 创建git仓库
    try:
        # 新建目录
        os.mkdir(os.path.join("data", "ocgit", project_name))
        os.mkdir(os.path.join("data", "ocgit", project_name, "cache"))
        os.mkdir(os.path.join("data", "ocgit", project_name, "project"))
    except FileExistsError:
        await new_project.finish(f"[ERROR] 出现错误！企划 {project_name} 已经存在！")
    # 新建git仓库
    git.Repo.init(path=os.path.join("data", "ocgit", project_name))
    new_git_project = git.Repo(os.path.join(".", "data", "ocgit", project_name))
    new_git_project.index.add(["project", "cache"])
    new_git_project.index.commit("[初始化] 完成仓库创建,ocgit is ready to go!!!")
    # await new_project.send("[info]git仓库创建完成！")

    # 创建config.json
    with open(os.path.join("data", "ocgit", project_name, "config.json"), "w", encoding="utf8") as f:
        admin_list = await get_admin_list(bot, project_qgroup_id)
        config = {
            "project_name": project_name,
            "project_qgroup_id": project_qgroup_id,
            "project_admin": [event.user_id] + admin_list,
            "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        json.dump(config, f, indent=4)
        # await new_project.send("[info] 配置写入成功")

    # 提交模板及日志和保存总config.json
    # await new_project.send(str(new_git_project.git.branch()))
    logger.info("[OCGIT] 用户{uid}新建了一个仓库，企划名为{name}".format(uid=event.user_id, name=project_name))
    global_config["group_and_project_list"][project_qgroup_id] = project_name
    with open(os.path.join(".", "data", "ocgit", "config.json"), "w", encoding="utf8") as f:
        json.dump(global_config, f, indent=4)
    # finish
    await new_project.finish("已经完成企划仓库创建！OCGIT is ready to go!!!\n"
                             "为了正常使用，请在群文件新建名为“提交文件夹”的群文件夹\n"
                             "后续使用 请发送/ocgit")
