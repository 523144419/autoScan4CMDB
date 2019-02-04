#!/bin/env python
# -*- coding:utf8 -*-
import json
import sys
import commands
import logging
from softinfo import *
import copy

jvm_parm = {
    "-Xms": "jvm_Xms",
    "-Xmx": "jvm_Xmx",
    "-XX:MetaspaceSize=": "jvm_MetaspaceSize",
    "-XX:MaxMetaspaceSize=": "jvm_MaxMetaspaceSize",
    "-XX:PermSize=": "jvm_PermSize",
    "-XX:MaxPermSize=": "jvm_MaxPermSize"
}

__all__ = ['get_proc_info', 'get_jar_info']

class get_jar_info(fifter):
    """
    获取指定进程pid的启动用户
    设置捕获的进程类型
    获取进程的jdk版本
    """
# _init = fifter(self.cmd)

    def get_user(self, pid):
        """get pid of the startup JAVA"""
        user = _init.username(pid)
        return user

    def app_name(self, name):
        """set appname"""
        self.name = name
        return name

    def get_jdk_version(self, pid):
        """get used java version"""
        jdk_version = _init.jdkVersion(pid)
        return jdk_version

class get_proc_info(object):
    """
    通过命行行的和PROC进程目录下的数据获取JVM、JMX以及工程包的信息
    """

    def __init__(self, pid):
        self.pid = pid

    @property
    def get_jvm_info(self):
        """
        根据当前进程的pid，获取strings /proc/PID/cmdline命令的所有返回
        :return: strings /proc/PID/cmdline命令的所有返回
        :type: str
        """
        _cmd_line = "strings /proc/{0}/cmdline".format(self.pid)
        _ex_cmd_line = commands.getstatusoutput(_cmd_line)
        checkCode(_ex_cmd_line[0], _cmd_line, _ex_cmd_line[1])
        proc_jvm = _ex_cmd_line[1]
        return proc_jvm

    def get_jvm_info2list(self, jvm_info):
        """
        根据strings命令的返回内容，将其拼接为list
        :param jvm_info: strings /proc/PID/cmdline命令的所有返回，type为str
        :return: strings /proc/PID/cmdline命令的所有返回，type为list
        :type: list
        """
        linelist = jvm_info.split("\n")
        return linelist

    def get_jvm_list(self, infolist):
        """
        获取命令行中所有以—X开头的jvm参数，并返回一个list
        :param infolist:
        :return:
        """
        _jvm = []
        _par = []
        for part in infolist:
            jstart_part = re.compile(r"-X(.*)")
            find_jstart = jstart_part.match(part)
            if find_jstart is not None:
                jvm_Xm = find_jstart.group()
                _jvm.append(jvm_Xm)
        for part1 in _jvm:
            parm = filter(lambda x: x not in '0123456789', part1)
            parm_1 = parm[0:-1]
            if parm_1 in jvm_parm.keys():
                _par.append(part1)
        return _par

    def get_jvm(self, jvmlist):
        """
        根据jvm_parm拼接返回的JSON中的kv对
        :param jvmlist:
        :return: jvm_dict
        :type: dict
        """
        if not isinstance(jvmlist,list):
            return None
        jvm_dict = {}
        for jvm in jvmlist:
            jvm_str = filter(lambda x: x not in '0123456789', jvm)
            jvm_dict[jvm_str[0:-1]] = jvm.replace(jvm_str[0:-1], '')
        for i in jvm_parm.keys():
            if i in jvm_dict.keys():
                jvm_value = jvm_dict[i]
                jvm_dict.pop(i)
                jvm_dict[jvm_parm[i]] = jvm_value
            else:
                jvm_dict[jvm_parm[i]] = 'null'
        return jvm_dict

    def get_jmx(self, infolist):
        """
        从get_jvm_info2list函数返回的list内容中，匹配-D开头的jvm参数,匹配-Dcom.sun.management.jmxremote.port参数判断该节点是否配在了jmx监控
        :param infolist:
        :return: True or None
        """
        jmx_set = False
        for part in infolist:
            dstart_part = re.compile(r"-Dcom.sun.management.jmxremote.port=(.\S*)", re.S).search(part)
            if dstart_part:
                jmx_set = True
                jmx_port = dstart_part.group(1)
                return jmx_set, jmx_port
        if not jmx_set:
            return False, None

    def get_jar_port(self, pid, jmxport):
        """
        通过netstat -tunlp命令获取指定pid的监听端口
        :param pid:
        :param limitNum:
        :param jmxPort:
        :return:
        """
        net_info = _init.netInfo(pid, jmxport=jmxport)
        port = _init.get_pid_port(net_info, num=30000)
        return port

    def get_jar_name(self, infolist):
        """
        按照命行的输出查找带有jar和war的工程名称和安装目录
        :param infolist:
        :return:
        """
        for part in infolist:
            _cmd_line_grep = 'echo ' + "\"" + part + "\"" + " |grep -e " + "\"" + "\.jar" + "\"" + " -e " + "\"" + "\.war" + "\""
            _ex_cmd_line_grep = commands.getstatusoutput(_cmd_line_grep)
            if _ex_cmd_line_grep[0] == 0:
                jar_name_part = _ex_cmd_line_grep[1].split("/")
                jar_name = jar_name_part[-1]
                jar_local = _ex_cmd_line_grep[1].replace(jar_name, "")
                if len(jar_local) == 0:
                    jar_local = _init.cwd(self.pid)
                return jar_name, jar_local

if __name__ == '__main__':
    _init = get_jar_info("ps axu|grep java |grep -v grep |grep -v 'cmdline-jmxclient-0.10.3.jar'|grep 'java'|grep '\-jar'", appType='JAR')
    jar_list = []
    pid_list = _init.pidList

    for pid in pid_list:
        jar_dict = {}
        appname = _init.app_name("JAR")
        user = _init.get_user(pid)
        JkdVersion = _init.get_jdk_version(pid)

        proc_info = get_proc_info(pid)
        jvm_info = proc_info.get_jvm_info
        jvm_info2list = proc_info.get_jvm_info2list(jvm_info)

        jvm_list = proc_info.get_jvm_list(jvm_info2list)

        jvm_dict = proc_info.get_jvm(jvm_list)
        jar_dict.update(jvm_dict)
        jmx = proc_info.get_jmx(jvm_info2list)[0]
        if jmx:
            jmxport = proc_info.get_jmx(jvm_info2list)[1]
        else:
            jmxport = None
        jarName, jarLocal = proc_info.get_jar_name(jvm_info2list)
        port_2_list = proc_info.get_jar_port(pid, jmxport=jmxport)

        if len(port_2_list) == 0:
            defult_dict = {}
            defult_list = []
            defult_dict["AppName"] = appname
            defult_list.append(defult_dict)
            print defult_list
            exit(0)
        for port in port_2_list:
            jar_dict = copy.deepcopy(jar_dict)
            jar_dict["port"] = port
            jar_dict["AppName"] = appname
            jar_dict["JdkVersion"] = JkdVersion
            jar_dict["jarLocal"] = jarLocal
            jar_dict["jmx"] = jmx
            jar_dict["user"] = user
            jar_dict["webapps_files"] = jarName
            jar_list.append(jar_dict)
    node_dict = json.dumps(jar_list, sort_keys=True, indent=4,
                           separators=(',', ': '), encoding='utf8',
                           ensure_ascii=True)
    print node_dict
