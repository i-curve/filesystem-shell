#!/usr/bin/python3

import argparse
import os.path
import configparser
import sys

import requests

version = "0.1.0"


class Shell:
    current_bucket = ""
    current_key = ""

    def run(self):
        print(f" 进入 {Config.host} filesystem 系统")
        while True:
            msg = input(f"filesystem [f{Config.username}]#:")
            array_msg = msg.split()
            if msg == "exit":  # 退出
                sys.exit(0)
            elif msg == "help":  # 展示帮助信息
                self.help()
            elif msg == "write":  # 写入配置文件
                self.write_config()
            elif msg == "pwd":  # 展示本地路径
                os.system("pwd")
            elif msg == "rpwd":  # 展示server路径
                print(Config.remote_dir)
            elif msg == "ls":  # 展示本地文件
                os.system("ls")
            elif msg == "rls":  # 展示远程文件
                self.list_dir()
            elif len(array_msg) > 1 and array_msg[0] == "cd":  # 切换本地目录
                os.chdir(array_msg[1])
            elif len(array_msg) > 1 and array_msg[0] == "rcd":  # 切换远程目录
                self.change_dir(array_msg[1])
            elif len(array_msg) > 1 and array_msg[0] == "cat":
                os.system(msg)
            elif len(array_msg) > 1 and array_msg[0] == "rcat":
                self.show_file(array_msg[1])
            elif len(array_msg) > 1 and array_msg[0] == "get":  # 下载文件到本地
                self.download_file(array_msg[1])
            elif len(array_msg) > 1 and array_msg[0] == "put":  # 从本地上传文件
                self.upload_file(array_msg[1])
            elif msg != "":
                print(f"{msg} 命令未找到")

    def help(self):
        print(""" help manu:
    - exit: 退出
    - help: 打印帮助信息
    - pwd: 展示本地路径
    - rpwd: 展示远程路径
    - ls: 展示本地文件
    - rls: 展示远程文件
    - cd: 切换本地路径
    - rcd: 切换远程路径
    - get: 下载文件
    - put: 上传文件""")

    @staticmethod
    def write_config():
        """ 写入配置到文件中"""
        Config.write_config(Config.default_config_path)

    @staticmethod
    def list_dir():
        """ 展示 filesystem 目录下文件"""
        if Config.remote_dir == "/":
            res = requests.get(f"{Config.host}/bucket", headers=Config.headers)
            if res.status_code != 200:
                print(f"request error({res.status_code}): {res.reason}")
            for item in res.json():
                print("{}(d)".format(item["name"]), end=" ")
            print()
        else:
            res = requests.get(f"{Config.host}/file/catalog?path={Config.remote_dir}",
                               headers=Config.headers)
            if res.status_code != 200:
                print(f"request error({res.status_code}): {res.reason}")
            if res.json() is None:
                print("(empty dir)")
                return
            for item in res.json():
                print("{}{}".format(item["filename"], "(d)" if item["is_dir"] else ""), end=" ")
            print()

    def change_dir(self, into_dir):
        """ 切换远程目录路径"""
        new_path = os.path.join(Config.remote_dir, into_dir)
        res = requests.get(f"{Config.host}/file/catalog?path={new_path}",
                           headers=Config.headers)
        if res.status_code != 200:
            print(f"切换路径失败: {res.text if res.text else res.reason}")
            return
        Config.remote_dir = new_path

    def parse_remote_dir(self, filename):
        paths = Config.remote_dir.split("/")
        if paths[1] == "":
            print("the current dir is not right")
            sys.exit(0)

        self.current_bucket = paths[1]
        if len(paths) > 2:
            self.current_key = '/'.join(paths[2:]) + "/" + filename
        else:
            self.current_key = filename

    def download_file(self, key):
        """ 下载文件"""
        if key.count("/") > 0:
            print("error: filename can not contain /")
            return
        self.parse_remote_dir(key)
        res = requests.get(f"{Config.host}/file/download?bucket={self.current_bucket}&key={self.current_key}",
                           headers=Config.headers)
        if res.status_code != 200:
            print(f"文件下载失败: {res.text}")
            return
        with open(key, "wb") as file:
            file.write(res.content)
        print(f"{key} 文件已经下载")

    def show_file(self, key):
        """ 查看文件"""
        if key.count("/") > 0:
            print("error: filename can not contain /")
            return
        self.parse_remote_dir(key)
        res = requests.get(f"{Config.host}/file/download?bucket={self.current_bucket}&key={self.current_key}",
                           headers=Config.headers)
        if res.status_code != 200:
            print(f"文件下载失败: {res.text}")
            return
        print(res.text)

    def upload_file(self, key):
        """ 文件上传"""
        filename = key
        self.parse_remote_dir(key)
        print(self.current_bucket, self.current_key)
        res = requests.post(f"{Config.host}/file/upload",
                            files={"file": open(filename, "rb")},
                            data={"bucket": self.current_bucket, "key": self.current_key},
                            headers=Config.headers)
        if res.status_code != 201:
            print(f"文件上传失败: {res.text}")
            return
        print("文件上传成功.")


class Config:
    """filesystem configuration"""
    default_config_path = os.path.join(os.path.expanduser("~"), '.filesystem')
    remote_dir = "/"
    username = ''
    password = ''
    host = ''
    headers = {}

    @classmethod
    def init(cls, args: argparse.Namespace) -> bool:
        if args.command == 'version':
            print(version)
            sys.exit(0)
        elif args.command == 'connect':
            cls.set_data(args.username, args.password, args.host)
        elif args.command == 'load':
            cls.read_config(args.config_path)
        else:
            if not os.path.exists(cls.default_config_path):
                cls.create_config()
            cls.read_config(cls.default_config_path)
        status, _ = cls.check_config()
        return status

    @classmethod
    def check_config(cls) -> (bool, str):
        """check the config"""
        res = requests.get(f'{cls.host}/version')
        if res.status_code != 200:
            print(f'{cls.host} 连接失败')
            return False, f'{cls.host} 连接失败'
        res = requests.get(f'{cls.host}/version', headers={'user': cls.username, 'auth': cls.password})
        if res.status_code != 200:
            print(f'auth 失败: {res.reason}')
            return False, f'auth 失败: {res.reason}'
        cls.headers = {'user': cls.username, 'auth': cls.password}
        return True, ''

    @classmethod
    def set_data(cls, username, password, host):
        """set the config data"""
        cls.username, cls.password, cls.host = username, password, host

    @classmethod
    def read_config(cls, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f'配置文件不存在: {config_path}')
        config = configparser.ConfigParser()
        config.read(config_path)
        cls.username = config.get("system", "username")
        cls.password = config.get("system", "password")
        cls.host = config.get("system", "host")

    @classmethod
    def create_config(cls):
        print('------------ 检测到没有默认配置文件 ------')
        is_create = input('------------ 是否创建配置文件 [Y/n]: ')
        if is_create == 'N' or is_create == 'n':
            sys.exit(0)
        cls.username = input("请输入用户名:")
        cls.password = input("请输入密码:")
        cls.host = input("请输入host:")

    @classmethod
    def write_config(cls, config_path):
        if config_path is None:
            config_path = os.path.join('~', '.filesystem')

        with open(config_path, 'w') as file:
            config = configparser.ConfigParser()
            config.add_section("system")
            config.set("system", "username", cls.username)
            config.set("system", "password", cls.password)
            config.set("system", "host", cls.host)
            config.write(file)
        print(f"配置文件义写入 {config_path}")


class ParseArgs:
    """ parse arguments"""

    @classmethod
    def init(cls) -> argparse.Namespace:
        parser = argparse.ArgumentParser(prog='filesystem',
                                         description='a filesystem client to connect the filesystem system')

        sp = parser.add_subparsers(dest='command')
        sp_version = sp.add_parser('version', help='output the filesystem client version')
        # parse connect args
        sp_connect = sp.add_parser('connect', help='connect the filesystem server')
        cls.parse_connect(sp_connect)

        # parse config file args
        sp_load = sp.add_parser('load', help="load config file path")
        cls.parse_load(sp_load)

        args = parser.parse_args()
        # print(args
        return args

    @classmethod
    def parse_connect(cls, connect: argparse.ArgumentParser) -> None:
        """ connect the server by command line args"""
        connect.add_argument('-u', '--user', type=str, help='username')
        connect.add_argument('-p', '--password', type=str, help='password')
        connect.add_argument('--host', type=str, help="the filesystem server url")

    @classmethod
    def parse_load(cls, load: argparse.ArgumentParser) -> None:
        """ load the config file"""
        load.add_argument('config_path', help="config file path.(ini type)")


if __name__ == "__main__":
    print(f"hello filesystem-shell, version: {version}")
    args = ParseArgs.init()

    if not Config.init(args):
        sys.exit(0)

    # 执行事件循环
    Shell().run()
