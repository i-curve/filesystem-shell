# filesystem-shell

[![GitHub Release](https://img.shields.io/github/v/release/i-curve/filesystem-shell)](https://github.com/i-curve/filesystem-shell/releases)
[![GitHub Tag](https://img.shields.io/github/v/tag/i-curve/filesystem?label=filesystem)](https://github.com/i-curve/filesystem)
[![GitHub Tag](https://img.shields.io/github/v/tag/i-curve/filesystem-gosdk?label=filesystem-gosdk)](https://github.com/i-curve/filesystem-gosdk)
[![GitHub Tag](https://img.shields.io/github/v/tag/i-curve/filesystem-pysdk?label=filesystem-pysdk)](https://github.com/i-curve/filesystem-pysdk)

<!-- TOC -->

* [filesystem-shell](#filesystem-shell)
    * [I. 下载](#i-下载)
    * [II. 进行配置](#ii-进行配置)
    * [III. shell内操作](#iii-shell内操作)

<!-- TOC -->

[filesystem](https://github.com/i-curve/filesystem) 的 shell 客户端, 使你像操纵命令行一样使用 filesystem

## I. 下载

- 下载

直接在release中下载最新版本即可或者直接使用本项目中的filesystem.py文件

- 查看版本信息

```shell
python filesystem version
```

- 查看参数信息

```shell
python filesystem -h
```

- 快速执行

```shell
# 
# 去掉文件后缀名
mv filesystem.py filesystem

#
# 添加文件可执行权限
chmod u+x filesystem

# 
# 修改解释器路径 (如果用的python路径不在 /usr/bin/python3)
# 安装python相应依赖
pip install requests

# 
# 把文件移动到 /usr/local/bin 目录下
mv filesystem /usr/local/bin
```

快速执行:

```shell
# 输出 version 信息
filesystem version
```

## II. 进行配置

- 使用默认配置文件路径

直接执行 ```python filesystem```, 第一次登录需要填充登录信息

- 读取配置文件

```shell
python load [配置配置文件路径]
```

例如: 默认情况下filesystem-shell会读取 ~/.filesystem 文件作为配置文件

```shell
python load ~ /.filesystem
```

- 命令行参数读取

```shell
python connect -u [username] -p [password] --host [filesystem server url]
```

需要 用户名, auth 认证信息, host 主机信息

## III. shell内操作

相关服务器操作命令都会加上 r 前缀

- exit: 退出
- help: 打印帮助信息
- pwd: 展示本地路径
- rpwd: 展示远程路径
- ls: 展示本地文件
- rls: 展示远程文件
- cd: 切换本地路径
- rcd: 切换远程路径
- get: 下载文件
- put: 上传文件

