import json
import time
import os
from zipfile import ZipFile

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.params import ArgStr
from nonebot.typing import T_State
from nonebot.log import logger

import git

from .utils import async_download, zipfile_gbk

submit_branch = on_command("ocgit 提交", aliases={"ocgit submit"})


async def get_download_url(bot: Bot, event: Event, file_id):
    submit_folder = await get_submit_folder(bot, event)
    for file in submit_folder["files"]:
        if file["file_id"] == file_id:
            return await bot.call_api("get_group_file_url", group_id=event.group_id, file_id=file_id, busid=0)


async def get_sub_file_list(bot, event, arrowed_time):
    """
    寻找指定的提交文件
    :param bot: 机器人对象
    :param event: 时间对象
    :param arrowed_time: 允许的超时时间(秒)（从获取开始允许有arrowed_time的误差），比如先后300秒的文件

    :return:list, dirt 包含所有符合条件的 file_id， 以及提交文件夹目录字典
    """
    files = []
    now = time.time()
    submit_folder = await get_submit_folder(bot, event)
    for file in submit_folder["files"]:
        if file["uploader"] == event.user_id and file["upload_time"] > now - arrowed_time and file["busid"] == 0:
            files.append(file["file_id"])
    return files, submit_folder["files"]


async def get_submit_folder(bot: Bot, event: Event):
    """获取提交文件夹底下的所有文件"""
    all_folder = await bot.call_api("get_group_root_files", group_id=event.group_id)
    for folder in all_folder["folders"]:
        if folder["folder_name"] == "提交文件夹":
            sub_folder_id = folder['folder_id']
            submit_folder = await bot.call_api("get_group_files_by_folder", group_id=event.group_id,
                                               folder_id=sub_folder_id)
            # await submit_branch.send(json.dumps(submit_folder, indent=4))
            return submit_folder


@submit_branch.handle()
async def get_submit_file(bot: Bot, event: Event, state: T_State):
    await submit_branch.send("OCGIT提交向导....")
    await submit_branch.send('正在检测"提交文件夹"有无您在20分钟内提交的压缩包....')
    (files, submit_folder) = await get_sub_file_list(bot, event, 1200)
    state["files"] = files
    if not files:
        await submit_branch.finish("没有符合要求的文件！请先提交压缩包到”提交文件夹“再使用此命令！")
    confirm_msg = "----检查到的符合要求的文件----\n"
    count = 1
    for file in submit_folder:
        if file["file_id"] in files:
            confirm_msg = confirm_msg + f"{count}. {file['file_name']}\n"
            count += 1
    confirm_msg += "------------------------"
    await submit_branch.send(confirm_msg)


@submit_branch.got("chosen_file", prompt="请回复要提交的文件的编号")
async def submit(bot: Bot, event: Event, state: T_State, chosen_file=ArgStr()):
    # 读取插件配置文件 查询是哪个企划的pr 得到project_name
    with open(os.path.join(".", "data", "ocgit", "config.json"), "r", encoding="utf8") as f:
        data = json.load(f)
        project_name = data["group_and_project_list"][str(event.group_id)]
    # 获取文件下载url
    file_id = state["files"][int(chosen_file) - 1]
    url = await get_download_url(bot, event, file_id)
    url = url["url"]
    # 下载
    start_t = time.time()  # 计时器
    await submit_branch.send("正在处理（下载文件耗时过大，可能得等待好久）")
    download_file_name = f"download_{file_id.replace('/', '')}_{time.time()}.zip"
    await async_download(os.path.join(".", "data", "ocgit", project_name, "cache", download_file_name), url)
    # 切换分支
    project_git = git.Repo(os.path.join(".", "data", "ocgit", project_name))
    try:
        project_git.git.checkout(event.user_id)
    except git.exc.GitCommandError:
        await submit_branch.send("没有你的分支，正在新建")
        project_git.git.branch(event.user_id)
        project_git.git.checkout(event.user_id)
        # await submit_branch.finish("切换到分支成功")
    # 解压提交文件
    with zipfile_gbk(ZipFile(os.path.join(".", "data", "ocgit", project_name, "cache", download_file_name))) as zipfile:
        zipfile.extractall(os.path.join(".", "data", "ocgit", project_name, "project"))
    # 进行add
    for root, dirs, files in os.walk(os.path.join(".", "data", "ocgit", project_name, "project")):
        for file in files:
             project_git.index.add(os.path.join("project", file))
    project_git.index.commit(f"来自{event.user_id}在{time.strftime('%Y-%m-%d', time.localtime())}的提交")
    logger.info(f"[ocgit]{event.user_id}在{time.strftime('%Y-%m-%d', time.localtime())}向{project_name}完成一次提交")
    os.remove(os.path.join(".", "data", "ocgit", project_name, "cache", download_file_name))
    await submit_branch.finish(f"你已完成提交！耗时{time.time()-start_t} sec")

