from . import (new_project,
               git_manager,
               upload_file,
               upload_file,
               pull_request,
               merge)
from .start import start

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="ocgit",
    description="使用git和qq群文件管理你的oc企划！",
    usage="暂时不写",
    type="application",
    homepage="{项目主页}",
    supported_adapters={"~onebot.v11"},
)

start()
