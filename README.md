# nonebot-plugin-ocgit
基于nonebot2的oc企划管理插件
## 介绍
~~其实我就是封装了一个git到qq插件上（（（~~

利用git的强大功能，更方便的管理oc企划

## 安装
1. 在你的虚拟环境下执行`pip install -r requirement.txt`， 或者手动安装gitpython和aiohttp
2. clone本仓库，或到release下载压缩包
3. 将项目解压到你的插件文件夹下
4. 安装git **注意：如果在windows部署，安装git的时候一定要将git添加到path！！！！**
5. 请使用KonataDev/Lagrange.Core 作为qq协议端，因为用了超级多的文件api，不保证gocq和其他协议能跑

## 使用
`@bot 新建企划`
用于新建一个企划

`/ocgit 删除/删除仓库/删除企划/delete`
用于删除一个企划

`/ocgit info/统计信息/企划列表/状态`
查看已有的企划，如果跟上企划名参数，则只返回这个企划的信息

`/ocgit 合并/merge`
将用户分支和主分支合并

`/ocgit 提交/submit`
上传自己的设定到自己的分支

`/ocgit 更新文件/update/upload/上传`
上传指定分支文件

## 计划
1. 加入更多协议端支持
2. 加入单文件提交
3. （09bot）一键部署包
4. 多群同企划管理

## 公共09bot

你可以来q群798523753联系墨冉获取公共09bot，带ocgit全部功能和一些娱乐功能

## 鸣谢
感谢以下项目对ocgit的支持
1. git/git ~~封装了一个git到qq插件上，感谢老祖宗~~
2. KonataDev/Lagrange.Core 赞美热心外国网友
3. nonebot/nonebot2 真的好用，我爱你

