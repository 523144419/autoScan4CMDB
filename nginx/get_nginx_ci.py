#!/bin/env python
# -*-  coding:utf8 -*-
import json
import sys
import commands
import nginx
import re
import copy
import logging
import nginx
from softinfo import *
reload(sys)
sys.setdefaultencoding("utf-8")

"""
:return:
[
    {
        "AppName": "nginx",
        "InstallDir": "/opt/nginx_echo/",
        "NginxConf": "/opt/nginx_echo/conf/nginx.conf",
        "binFile": "/opt/nginx_echo/sbin/nginx",
        "keepalive_timeout": "65",
        "port": "10002",
        "server_tokens": "off",
        "user": "root",
        "version": "nginx/1.10.3"
    }
]
"""

__all__ = ['analyze_nginx_conf']
__version__ = "0.0.1"

LogFormat='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO,format=LogFormat)

def is_running_ng():
    """实例化fifter,cmd命令执行失败返回'cmd命令没有执行成功，请确认输入'"""
    cmdline = fifter("ps axu|grep nginx|grep master|grep -v grep", appType='NGINX')
    return cmdline

def get_runing_pid():
    """当服务器上有多个节点，将多个pid放入pidList列表中"""
    pidList = []
    cmdline = is_running_ng()
    result = cmdline.lookfor
    for i in result:
        pidList.append(i[1])
    return pidList

def get_fifter_object():
    """
    初始化softinfo 包中的fifter类
    :return:
    """
    ps = fifter("ps axu|grep nginx|grep master|grep -v grep", appType='NGINX')
    return ps

def get_bin_file(pid):
    """
    获取运行中nginx的sbin可执行文件的绝对路径
    :param pid:
    :return:
    """
    bin_file = get_fifter_object().exe(pid)
    return bin_file

def get_nginx_conf(pid):
    """
    根据pid获取运行中的nginx的配置文件nginx.conf的绝对路径
    :param pid: 运行中的pid
    :return: nginx.conf的绝对路径
    """
    try:
        nginx_sbin = get_bin_file(pid)
        nginx_conf = nginx_sbin.replace(nginx_sbin[-10:],"conf/nginx.conf")
        if not os.path.exists(nginx_conf):
            ps_aux_line = is_running_ng().command_list
            for k in ps_aux_line:
                if k == '-c':
                    k_index = ps_aux_line.index(k)
                    return ps_aux_line[k_index + 1]
        else:
            return nginx_conf
    except IOError as e:
        logging.error("PID={0}的nginx进程配置文件获取失败，错误日志为{1}".format(pid, e))
        exit(-1)

def get_nginx_user(pid):
    """
    根据pid获取运行中的nginx的启动用户
    :param pid:
    :return:
    """
    nginx_user = get_fifter_object().username(pid)
    return nginx_user

def get_nginx_location(pid):
    """
    nginx的安装路径
    :param pid:
    :return:
    """
    nginx_location = get_nginx_conf(pid)
    if nginx_location:
        return nginx_location[0:-15]

def get_nginx_version(pid):
    """
    获取nginx的版本号
    :param pid:
    :return:
    """
    nginx_sbin = get_bin_file(pid)
    cmd_nginx_sbin = nginx_sbin + " -v 2>&1" + "|grep 'nginx version'"
    ex_nginx_sbin = commands.getstatusoutput(cmd_nginx_sbin)
    checkCode(ex_nginx_sbin[0], cmd_nginx_sbin, ex_nginx_sbin[1])
    return ex_nginx_sbin[1][15:]

def remove_irr_file(conf):
    """
    通过commands模块对于nginx的配置文件进行去除空行和注释内容，生产临时文件存放在/tmp目录下
    :param conf: 输入通过get_nginx_conf()函数获取到的nginx配置文件路径
    :return: 临时文件的据对路径
    """
    cmdline = "grep -v \# " + conf + "|sed /^$/d"
    _ex_cmdline = commands.getstatusoutput(cmdline)
    checkCode(_ex_cmdline[0], cmdline, _ex_cmdline[1])
    return _ex_cmdline[1]

class analyze_nginx_conf():

    def __init__(self, ngxin_conf):
        """
        ngxin_conf，配置文件绝对路径
        :param ngxin_conf:
        """
        self.ngxin_conf = ngxin_conf

    @property
    def init_analyze_conf(self):
        """
        初始化nginx.conf配置文件，格式化文件内容返回
        :return:
        """
        init_analyze = nginx.loadf(self.ngxin_conf)
        return init_analyze

    def analyze_http(self, iniAnalyze):
        """
        获取nginx配置文件中http语句块中的所有内容
        :param iniAnalyze:
        :return:
        """
        iniAna_dict = iniAnalyze.as_dict
        for http in iniAna_dict['conf']:
            for key, value in http.items():
                if key == 'http ':
                    return http[key]

    def analyze_server(self, http):
        """
        从配置文件中获取
        :param http:
        :return:
        """
        return [v for part in http for k, v in part.items() if k == "server"]

    def get_part_all(self, server):
        """
        从配置文件中获取所有nginx的监听端口
        :return: list
        """
        return [v.split()[0] for part in server for server_part in part for k, v in server_part.items() if k == "listen"]

    def get_conf_part(self, http, part):
        """
        从http context中获取part配置项，例如从http中获取server_tokens和keepalive_timeout的值
        :param http:
        :param part:
        :return:
        """
        return ''.join([v for p in http for k, v in p.items() if k == part])


# 主程序入口
if __name__ == "__main__":
    # 获取运行时的nginx的pid
    pid = get_runing_pid()
    NginxInfo = []
    PartInfo = {}
    for pidnu in pid:
        PartInfo = copy.deepcopy(PartInfo)
        user = get_nginx_user(pidnu)
        BinFile = get_bin_file(pidnu)
        AppName = "nginx"
        InstallDir = get_nginx_location(pidnu)
        ng_version = get_nginx_version(pidnu)
        ng_conf = get_nginx_conf(pidnu)
        # 通过command模块去除nginx.conf文件中的空行和注释内容
        nginx_conf_irr = remove_irr_file(ng_conf)
        init_nginx_conf = analyze_nginx_conf(ng_conf)
        analyze_conf = init_nginx_conf.init_analyze_conf

        http = init_nginx_conf.analyze_http(analyze_conf)
        server_list = init_nginx_conf.analyze_server(http)
        port_list = init_nginx_conf.get_part_all(server_list)
        server_tokens = init_nginx_conf.get_conf_part(http, 'server_tokens')
        keepalive_timeout = init_nginx_conf.get_conf_part(http, 'keepalive_timeout')

        for port in port_list:
            PartInfo = {
                "user": user,
                "binFile": BinFile,
                "AppName": AppName,
                "port": port,
                "InstallDir": InstallDir,
                "version": ng_version,
                "NginxConf": ng_conf,
                "server_tokens": server_tokens,
                "keepalive_timeout": keepalive_timeout,
            }
            NginxInfo.append(PartInfo)
    sys.stdout.write(json.dumps(NginxInfo, sort_keys=True, indent=4, separators=(',', ': '), encoding='utf8',
                       ensure_ascii=True))

