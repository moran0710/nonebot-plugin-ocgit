import json
import os

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment
from nonebot.params import CommandArg, ArgStr
from nonebot.permission import SUPERUSER

import shutil

"""
对仓库进行管理的模块
1.删除仓库
2.查看所有仓库
3.查看仓库信息
"""

delete = on_command("ocgit 删除", permission=SUPERUSER, aliases={"ocgit 删除仓库", "ocgit 删除企划", "ocgit delete"})
info = on_command("ocgit info", permission=SUPERUSER, aliases={"ocgit 统计信息", "ocgit 企划列表", "ocgit 状态"})


@info.handle()
async def info_func(bot: Bot, event: Event, args: Message = CommandArg()):
    # 指定企划名参数
    if proj_name := args.extract_plain_text():
        try:
            with open(os.path.join(".", "data", "ocgit", proj_name, "config.json"), "r", encoding="utf-8") as f:
                proj_config = json.load(f)
        except FileNotFoundError:
            info.finish("[ERROR] 不存在这个企划")
        # 获取企划信息
        msg = get_project_msg(proj_config)
        await info.finish(msg)

    else:
        # 如果不指定参数全部信息 合并转发
        project_list = []
        # 读取所有企划信息
        for dirs in os.listdir(os.path.join(".", "data", "ocgit")):
            if dirs == "config.json":
                continue
            with open(os.path.join(".", "data", "ocgit", dirs, "config.json"), "r", encoding="utf-8") as f:
                proj_config = json.load(f)
                msg = get_project_msg(proj_config)
                project_list.append(msg)
        # 构造转发消息体
        msg = []
        for project in project_list:
            node = {
                "type": "node",
                "data": {"name": "OCGIT",
                         "uin": str(event.user_id),
                         "content": [MessageSegment.text(project)]},
            }
            msg.append(node)
        # 进行合并转发
        res_id = await bot.call_api("send_forward_msg", messages=msg)
        await bot.send_group_msg(group_id=event.group_id, message=MessageSegment.forward(res_id))


def get_project_msg(proj_config):
    return (f"------企划 {proj_config['project_name']} 信息------\n"
            f"创建时间：{proj_config['create_time']}\n"
            f"绑定群聊：{proj_config['project_qgroup_id']}\n"
            f"管理员列表：{proj_config['project_admin']}\n"
            f"------------------------------")


@delete.handle()
async def delete_():
    await delete.send("删除企划向导")


@delete.got("project_name", prompt="[?]请输入你要删除的企划名字")
@delete.got("confirm", prompt="你真的要删除这个企划吗？\n这个企划将永久消失（真的很久！！！！）\n并且无法恢复！！！！\n"
                              "如果确认，请输入”我确定要删除这个企划“，或者输入任意内容退出删除向导")
async def delete_project(event: Event, project_name: str = ArgStr(), confirm: str = ArgStr()):
    if confirm == "我确定要删除这个企划":
        with open(os.path.join(".", "data", "ocgit", "config.json"), "r", encoding="utf8") as f:
            global_config = json.load(f)
        del global_config["group_and_project_list"][str(event.group_id)]
        try:
            shutil.rmtree(os.path.join(".", "data", "ocgit", project_name))
        except FileNotFoundError:
            await delete.finish("[ERROR] 不存在当前企划")
        logger.info(f"[OCGIT] 用户{event.user_id}删除了企划{project_name}")
        with open(os.path.join(".", "data", "ocgit", "config.json"), "w", encoding="utf8") as f:
            json.dump(global_config, f, indent=4)
        await delete.finish(f"企划 {project_name} 已经完成删除")
    else:
        await delete.finish(f"已经取消删除企划 {project_name}")
