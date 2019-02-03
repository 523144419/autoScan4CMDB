#!/bin/env python
# -*- coding:utf8 -*-
import commands
import json
import logging
import re
import sys
import os
import pwd
import grp
reload(sys)
sys.setdefaultencoding("utf-8")


LogFormat='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO,format=LogFormat)

def checkCode(code, command, result):
    """
    检测commands命令执行的返回值，非0退出脚本，返回执行命令和执行结果
    :param code: commands命令执行的返回码
    :param command: commands执行的命令
    :param result: commands执行命令的结果
    :except exit code为1则为该脚本检测到错误后退出
    :return: Null
    """
    if code != 0:
        logging.error("命令%s执行返回值非0，执行结果为%s已退出脚本" % (command, result))
        exit(code=1)
    else:
        pass

class ps_aux(object):

    def __init__(self, cmd, appType=None):
        """Initialize,cmd 用于 ps axu或是 ps -ef 等筛选语句为str"""
        self.cmd = cmd
        self.appTpye = appType

    def return_cmd(self):
        """
        :return: 执行的命令
        """
        return self.cmd, self.appTpye

    @property
    def execute(self):
        """
        调用commands方法执行命令
        :return: 返回commands命令执行的结果
        :type: str
        """
        command_line = self.cmd
        _ex_command_line = commands.getstatusoutput(command_line)
        # checkCode(_ex_command_line[0], command_line, _ex_command_line[1])
        if not self.appTpye:
            if _ex_command_line[0] == 0:
                return _ex_command_line[1]
            else:
                logging.error("命令%s执行返回值非0，执行结果为%s已退出脚本" % (command_line, _ex_command_line[1]))
                exit(code=0)
        else:
            if _ex_command_line[0] == 0:
                return _ex_command_line[1]
            else:
                print [{"AppName": self.appTpye}]
                exit(code=0)

class fifter(ps_aux):

    @property
    def lookfor(self):
        """
        用于方便选择需要匹配的字段，按照数字排序输出ps命令的全部结果
        :keyword: InList:用于存放ps命令的结果信息保存,数据类型为list
        :keyword: parts：由于ps命令结果中有很多空格，将空格去除后存放在，数据类型为list
        :keyword: resultList
        """
        InList = []
        resultList = []
        init = ps_aux(self.cmd, self.appTpye)
        result = init.execute
        parts = result.split("\n")

        for part in parts:
            part = re.split(" ", part)
            while '' in part:
                part.remove("")
            InList.append(part)

        for list in InList:
            PartNum = len(list)
            numlist = range(PartNum)
            InDict = dict(zip(numlist,list))
            resultList.append(InDict)
        return resultList

    @property
    def command_list(self):
        """
        用于方便选择需要匹配的字段，按照数字排序输出ps命令的全部结果
        :keyword: InList:用于存放ps命令的结果信息保存,数据类型为list
        :keyword: parts：由于ps命令结果中有很多空格，将空格去除后存放在，数据类型为list
        :keyword: resultList
        """
        InList = []
        resultList = []
        init = ps_aux(self.cmd)
        result = init.execute
        parts = result.split("\n")

        for part in parts:
            part = re.split(" ", part)
            while '' in part:
                part.remove("")
            #InList.append(part)
            return  part

    @property
    def takelook(self):
        """对于lookfor方法的输出进行json格式的输出"""
        ini = fifter(self.cmd)
        resultList=ini.lookfor
        node_dict = json.dumps(resultList, sort_keys=True, indent=4, separators=(',', ': '), encoding='utf8',
                               ensure_ascii=True)
        return node_dict

    def Fifer(self,*args):
        """
        匹配ps命令中的某一个字段，由于将ps命令的结果作为了一个list，需要传入索引。
        :param args: list的索引
        :except exit code为2则为该脚本检测到错误后退出
        :return:
        """
        #arg = [lambda nu:nu if type(nu) == int else TypeError("请输入数字") ]
        returnPart = ''
        for nu in args:
            if not isinstance(nu,int):
                raise TypeError("请输入数字")
            elif len(args) > 4:
                raise ImportError("目前只支持索引到3层")
            else:
                pass

        init=fifter(self.cmd)
        result=init.lookfor
        nuResult = len(result)
        nuLen = len(args)
        if nuResult < nuLen:
            raise ImportError("输入匹配层级不匹配！")
        elif nuLen == 1:
            nu = args[0]
            returnPart = result[0][nu]
        elif nuLen == 2:
            nu_in_list1,nu_in_list2= args
            returnPart = result[nu_in_list1][nu_in_list2]
        elif nuLen == 3:
            nu_in_list1, nu_in_list2,nu_in_list3= args
            returnPart = result[nu_in_list1][nu_in_list2][nu_in_list3]
        else:
            logging.error("目前只支持索引到3层")
            sys.exit(2)
        return returnPart


    def username(self,pid):
        """获取进程的用户"""
        if not isinstance(pid,str):
            logging.error("传入的pid不唯一或pid不为str类型，%s 的类型为 %s" %(pid,type(pid)))
        environ_file = "/proc/{0}/environ".format(pid)
        stat_file = os.stat(environ_file)
        file_uid = stat_file.st_uid
        file_owner = pwd.getpwuid(file_uid)[0]
        return file_owner


    def exe(self,pid):
        """获取启动命令"""
        if not isinstance(pid,str):
            logging.error("进程PID获取错误，输入的PID为%s" %pid)
            sys.exit(3)
        localtion = os.path.join("/proc",pid)
        _cd = "ls -trl " + localtion + " |grep exe |awk -F '-> ' '{print $2}'"
        _ex_cd = commands.getstatusoutput(_cd)
        if _ex_cd[0] != 0:
            raise ImportError("%s 命令执行失败"%_cd)
        else:
            re.sub('\s','',_ex_cd[1])
        return _ex_cd[1]

    def cwd(self,pid):
        """
        获取当前进程的工作目录
        :param pid:
        :return:
        """
        if not isinstance(pid,str):
            logging.error("进程PID获取错误，输入的PID为%s" %pid)
            sys.exit(4)
        localtion = os.path.join("/proc",pid)
        _cd = "ls -trl " + localtion + " |grep cwd |awk -F '-> ' '{print $2}'"
        _ex_cd = commands.getstatusoutput(_cd)
        if _ex_cd[0] != 0:
            raise ImportError("%s 命令执行失败"%_cd)
        else:
            re.sub('\s','',_ex_cd[1])
        return _ex_cd[1]

    def cmdline(self,pid):
        """
        获取程序启动时执行的命令
        :param pid:
        :return: 获取结果
        :type: str
        """
        if not isinstance(pid,str):
            logging.error("进程PID获取错误，输入的PID为%s" %pid)
            sys.exit(5)
        localtion = os.path.join("/proc", pid,"cmdline")
        _cmd = "strings " + localtion
        _ex_cmd = commands.getstatusoutput(_cmd)
        checkCode(_ex_cmd[0],_cmd,_ex_cmd[1])
        return _ex_cmd[1]

    @property
    def pidList(self):
        """
        :return:截取ps命令中所有的pid
        :type: list
        """
        pidList = []
        init=fifter(self.cmd, self.appTpye)
        result = init.lookfor
        for i in result:
            pidList.append(i[1])
        return pidList

    def jdkVersion(self,pid):
        """
        如ps命令的进程是java进程，可以获取对于pid进程的java绝对路径并返回jdk的版本
        :return: jdk version
        :type: str
        """
        init = fifter(self.cmd)
        username = init.username(pid)
        for proc_count in init.lookfor:
            if pid == proc_count[1]:
                localjava = proc_count[10]
                if 'java' in localjava:
                    # logging.info("java绝对路径获取成功，路径为%s" % localjava)
                    _command = "su - " + username + " -c " + "\"" + localjava + " -version" + "\""
                    java_version = commands.getstatusoutput(_command)
                    checkCode(java_version[0],_command,java_version[1])
                    jdk_version = java_version[1].split("\n")
                    if 'OpenJDK' in jdk_version[1].split():
                        version = jdk_version[0][14:-1] + "_OpenJDK"
                    else:
                        version = jdk_version[0][14:-1]
                    return version
                else:
                    logging.error("jdk版本获取失败，%s 命令未抓取到java头部信息 %s" %(self.cmd,ImportError))
                    sys.exit(6)

    def netInfo(self,pid, jmxport=None):
        """
        通过netstat 命了获取指定pid的监听端口，并排除大于num的数值和jmxport的端口
        :param pid: 进程的pid
        :param num: 指定排除大于多少的数字
        :param jmxport: jmx的端口
        :return: 进程的端口
        """
        if jmxport is None:
            _cmd_net = "netstat -tnlp|grep " + pid
            _ex_cmd_net = commands.getstatusoutput(_cmd_net)
            checkCode(_ex_cmd_net[0], _cmd_net, _ex_cmd_net[1])
            _net_split = _ex_cmd_net[1].split("\n")
            _net_info = [x.split() for x in _net_split]
            return _net_info
        elif jmxport is not None:
            _cmd_net = "netstat -tnlp|grep " + pid + "|grep -v " + jmxport
            _ex_cmd_net = commands.getstatusoutput(_cmd_net)
            checkCode(_ex_cmd_net[0], _cmd_net, _ex_cmd_net[1])
            _net_split = _ex_cmd_net[1].split("\n")
            _net_info = [x.split() for x in _net_split]
            return _net_info

    def get_pid_port(self, _net_info, num=None):
        """
        通过netInfo 函数返回的netstat -tnlp 返回的列表数据获取当前进程的所有的TCP监听端口，并且排除大于指定端口
        :param _net_info:
        :param num: 小于该端口的信息将被写入port列表
        :return:
        """
        port_of_pid = []
        if isinstance(_net_info, list):
            try:
                port_of_netinfo = [ port_list_part[3].split(":")[-1] for port_list_part in _net_info ]
                if num is not None:
                    for port in port_of_netinfo:
                        if int(port) < int(num):
                            port_of_pid.append(port)
            except ValueError as e:
                logging.error("{0}格式化netstat数据获取监听端口失败".format(e))
        else:
            logging.error("{0} 传入参数非法，必须为netstat格式化数据列表".format(_net_info))
        return port_of_pid
