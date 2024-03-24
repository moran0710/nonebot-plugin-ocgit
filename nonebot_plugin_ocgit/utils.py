import os
import zipfile
import aiohttp
import git
import json
from zipfile import ZipFile


async def get_admin_list(bot, gid):
    user_list = await bot.call_api("get_group_member_list", group_id=gid)
    admin_list = []
    for user in user_list:
        if user["role"] == "owner" or user["role"] == "admin":
            admin_list.append(user["user_id"])
    return admin_list


def zip_dir(dirpath, out_full_name):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param out_full_name: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zp = zipfile.ZipFile(out_full_name, "w", zipfile.ZIP_DEFLATED)  # outFullName为压缩文件的完整路径
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '')

        for filename in filenames:
            zp.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zp.close()


async def async_download(file_path, url):
    """
    异步下载器
    传入文件路径和url
    :param file_path: 保存文件路径，一定要带后缀！！！
    :param url: 下载路径
    :return: None
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False) as resp:
            content = await resp.content.read()
            with open(file_path, "wb") as f:
                f.write(content)


def get_all_branch(project_name):
    """
    获取指定项目的所有分支
    :param project_name: 项目名称
    :return: list 所有分支名字
    """
    repo = git.Repo(os.path.join(".", "data", "ocgit", project_name))
    branches = repo.git.branch().replace(" ", "").replace("*", "").split("\n")
    return branches

async def get_project_name(event):
    """
    获取当前会话所在群所绑定的企划
    :param event: 事件对象，参见nonebot
    :return: str 企划名字
    """
    try:
        with open(os.path.join(".", "data", "ocgit", "config.json"), "r", encoding="utf8") as f:
            project_name = json.load(f)["group_and_project_list"][str(event.group_id)]
        return project_name
    except Exception:
        return None


def zipfile_gbk(zip_file: ZipFile):
    name_to_info = zip_file.NameToInfo
    # copy map first
    for name, info in name_to_info.copy().items():
        real_name = name.encode('cp437').decode('gbk')
        if real_name != name:
            info.filename = real_name
            del name_to_info[name]
            name_to_info[real_name] = info
    return zip_file
