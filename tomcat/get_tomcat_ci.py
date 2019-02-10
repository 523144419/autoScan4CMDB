#!/bin/env python
# -*-  coding:utf8 -*-
from infodate.softinfo import *

reload(sys)
sys.setdefaultencoding("utf-8")
import xml.etree.ElementTree as ET

"""
Title: get_tomcat_ci.py
Dependent on: softinfo module
Time: 2018/1/29
function: Get tomcat infomation,and return the value into CMDB
e.g.

:return :
[
    {
        "AppName": "tomcat",
        "InstallDir": "/u01/app/tomcat",
        "JdkVersion": "1.8.0_171",
        "jdbc": "jdbc:mysql://localhost:3306/mysql?autoReconnect=true",
        "jmx": false,
        "jvm_MaxMetaspace": null,
        "jvm_MaxPerm": null,
        "jvm_Metaspace": null,
        "jvm_Perm": null,
        "jvm_Xms": null,
        "jvm_Xmx": null,
        "maxThreads": null,
        "minThreads": null,
        "mode": "BIO",
        "port": "8081",
        "startup_location": "/u01/app/tomcat/bin/startup.sh",
        "user": "cachecloud",
        "version": "Apache Tomcat/8.5.33",
        "webapps_files": "jenkins.war"
    }
]

:type:
AppName : str
InstallDir : str
JdkVersion : str
dbInfo : str
jmx : bool
jvm_MaxMetaspace : str or null
jvm_Metaspace : str or null
jvm_MaxPerm : str or null
jvm_Perm : str or null
jvm_Xms : str or null
jvm_Xmx : str or null
maxThreads : str or null
minThreads : str or null
mode : str
port : str or null
startup_location : str or null
version : str or null
webapps_files : str or null
"""

LogFormat = '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=LogFormat)


class get_tomcat_info(fifter):
    """
    _init = fifter(self.cmd) 获取运行时Tomcat进程的基础数据
    """

    def get_user(self, pid):
        """get pid of the startup tomcat"""
        user = _init.username(pid)
        return user

    def app_name(self, name):
        """set appname"""
        self.name = name
        return name

    def get_jdk_version(self, pid):
        """get userd java version"""
        jdk_version = _init.jdkVersion(pid)
        return jdk_version

    def get_tomcat_port(self, tomcatBaseHome):
        """
        解析server.xml文件获取Tomcat监听的端口号,判断配在文件中第一个itertag.tag=’Connector‘
        :param tomcatBaseHome:
        :return:
        """
        server_xml_location = tomcatBaseHome + "/conf/server.xml"
        if not os.path.exists(server_xml_location):
            logging.error("{0}文件不存在,请检查,脚本已退出".format(server_xml_location))
            return None
        else:
            serverXml_tree = ET.parse(server_xml_location)
            serverXml_root = serverXml_tree.getroot()
            for child in serverXml_root:
                for itertag in child:
                    if itertag.tag == 'Connector' and itertag.attrib['protocol'] != 'AJP/1.3':
                        tomcat_http_port = itertag.attrib['port']
                        return tomcat_http_port

    def get_tomcat_mode(self, tomcatBaseHome):
        """
        解析server.xml文件获取Tomcat运行的模式，最大、最小线程数
        :param tomcatBaseHome:
        :return:
        """
        tomcat_running_mode = ''
        tomcat_http_MaxThreads = ''
        tomcat_http_MinThreads = ''
        server_xml_location = tomcatBaseHome + "/conf/server.xml"
        if not os.path.exists(server_xml_location):
            logging.error("{0}文件不存在,请检查,脚本已退出".format(server_xml_location))
            return None
        else:
            serverXml_tree = ET.parse(server_xml_location)
            serverXml_root = serverXml_tree.getroot()
            for child in serverXml_root:
                for itertag in child:
                    if itertag.tag == 'Connector':
                        tomcat_http_mode = itertag.attrib['protocol']
                        if tomcat_http_mode == 'HTTP/1.1':
                            tomcat_running_mode = 'BIO'
                        elif tomcat_http_mode == 'org.apache.coyote.http11.Http11NioProtocol':
                            tomcat_running_mode = 'NIO'
                        elif tomcat_http_mode == 'org.apache.coyote.http11.Http11AprProtocol':
                            tomcat_running_mode = 'ARP'
                        else:
                            tomcat_running_mode = None

                        attrib_dict = itertag.attrib
                        if 'maxThreads' in attrib_dict.keys():
                            tomcat_http_MaxThreads = attrib_dict['maxThreads']
                        else:
                            tomcat_http_MaxThreads = None

                        if 'minSpareThreads' in attrib_dict.keys():
                            tomcat_http_MinThreads = attrib_dict['minSpareThreads']
                        else:
                            tomcat_http_MinThreads = None

                        return tomcat_running_mode, tomcat_http_MaxThreads, tomcat_http_MinThreads

    def get_tomcat_webapps(self, tomcatBaseHome):
        """
        根据tomcat basehome拼接出webapps的绝对路径，获取webapps下的工程名称，会区分全量包和增量包的名称。
        :param tomcatBaseHome:
        :return: 全量包和增量包的名称
        :type: str
        """
        tomcat_webapps_location = tomcatBaseHome + "/webapps"
        isdir = []
        isfile = []
        webapps_file = []
        if not os.path.exists(tomcat_webapps_location):
            logging.error("{0}文件不存在,请检查".format(tomcat_webapps_location))
            return None
        else:
            ls_webapps = os.listdir(tomcat_webapps_location)
            prohibit_file = ['manager', 'host-manager', 'examples', 'docs', 'ROOT']
            for prohibitFile in prohibit_file:
                if prohibitFile in ls_webapps:
                    ls_webapps.remove(prohibitFile)
            for file_name in ls_webapps:
                if os.path.isdir(os.path.join(tomcat_webapps_location, file_name)):
                    isdir.append(file_name)
                elif os.path.isfile(os.path.join(tomcat_webapps_location, file_name)):
                    isfile.append(file_name)
                else:
                    logging.error("无法判断 {0} 是文件或者文件夹，请确认".format(file_name))
            for file in isfile:
                file_split = file.split(".war")[0]
                for dict_name in isdir:
                    if file_split == dict_name:
                        webapps_file.append(file)
                        isdir.remove(dict_name)
            webapps_file.extend(isdir)
            return ','.join(webapps_file)

    def get_tomcat_version(self, tomcatBaseHome, username):
        """
        通过执行tomcat自带的version.sh脚本获取当前tomcat的版本信息，使用sudo到进程启动用户执行version.sh，确保环境环境变量一致
        :param tomcatBaseHome: tomcat安装目录
        :param username: 当前进程启动用户
        :return: tomcat版本信息 or None
        """
        tomcat_version_sh = tomcatBaseHome + "/bin/version.sh"
        tomcat_version_cmd = "su - " + username + " -c " + "\"" + tomcat_version_sh + "\""
        tomat_version_dict = {}
        if not os.path.exists(tomcat_version_sh):
            logging.error("{0} 文件不存在".format(tomcat_version_sh))
            return None
        else:
            ex_tomcat_version_cmd = commands.getstatusoutput(tomcat_version_cmd)
            checkCode(ex_tomcat_version_cmd[0], tomcat_version_cmd, ex_tomcat_version_cmd[1])
            tomcat_version_result = ex_tomcat_version_cmd[1].split("\n")
            for result_part in tomcat_version_result:
                tomcat_version = result_part.split(":")
                tomat_version_dict[tomcat_version[0]] = tomcat_version[1]

        if 'Server version' in tomat_version_dict.keys():
            return tomat_version_dict['Server version'].lstrip()
        else:
            return None

    def get_tomcat_jndi(self, tomcatBaseHome):
        """
        通过ET模块解析context.com中的jndi配置，截取url连接串
        :param tomcatBaseHome: tomcat安装目录
        :return:
        """
        if tomcatBaseHome is not None:
            context_xml = tomcatBaseHome + "/conf/context.xml"
            if not os.path.exists(context_xml):
                logging.error("{0} 文件不存在".format(context_xml))
                return None
            else:
                context_tree = ET.parse(context_xml)
                context_root = context_tree.getroot()
                for child_of_context_root in context_root:
                    for jndi_url in child_of_context_root.attrib:
                        if jndi_url == 'url':
                            # addr = child_of_context_root.attrib['url'].split("/")
                            addr = child_of_context_root.attrib['url']
                            return addr
        return None

class get_proc_info(object):
    """    通过proc中的信息获取jvm和jmx的相关信息    """

    def __init__(self, pid):
        """
        :param pid: The running TOMCAT`s pid
        """
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

    def get_jvm(self, infolist):
        """
        从get_jvm_info2list函数返回的list内容中，返回jvm参数，区分jdk1.7以下和jdk1.8
        :param infolist:
        :return: jvm
        :type： tuple
        """
        jvm_Xms = None
        jvm_Xmx = None
        jvm_Perm = None
        jvm_MaxPerm = None
        jvm_Metaspace = None
        jvm_MaxMetaspace = None

        for part in infolist:
            jstart_Xm_part = re.compile(r"-Xms(.*)").match(part)
            if jstart_Xm_part is not None:
                jvm_Xms = jstart_Xm_part.group()
                jvm_Xms = jvm_Xms.replace('-Xms', '')

            jstart_Xm_part = re.compile(r"-Xmx(.*)").match(part)
            if jstart_Xm_part is not None:
                jvm_Xmx = jstart_Xm_part.group()
                jvm_Xmx = jvm_Xmx.replace('-Xmx', '')

            Jstart_XXMeta_part = re.compile(r"-XX:MetaspaceSize(.*)").match(part)
            if Jstart_XXMeta_part is not None:
                jvm_Metaspace = Jstart_XXMeta_part.group()
                jvm_Metaspace = jvm_Metaspace.replace('-XX:MetaspaceSize=', '')

            Jstart_XXMaxMeta_part = re.compile(r"-XX:MaxMetaspaceSize(.*)").match(part)
            if Jstart_XXMaxMeta_part is not None:
                jvm_MaxMetaspace = Jstart_XXMaxMeta_part.group()
                jvm_MaxMetaspace = jvm_MaxMetaspace.replace('-XX:MaxMetaspaceSize=', '')

            jstart_XXPer_part = re.compile(r"-XX:PermSize(.*)").match(part)
            if jstart_XXPer_part is not None:
                jvm_Perm = jstart_XXPer_part.group()
                jvm_Perm = jvm_Perm.replace('-XX:PermSize=', '')

            Jstart_XXMaxPer_part = re.compile(r"-XX:MaxPermSize(.*)").match(part)
            if Jstart_XXMaxPer_part is not None:
                jvm_MaxPerm = Jstart_XXMaxPer_part.group()
                jvm_MaxPerm = jvm_MaxPerm.replace('-XX:MaxPermSize=', '')

        return jvm_Xms, jvm_Xmx, jvm_Perm, jvm_MaxPerm, jvm_Metaspace, jvm_MaxMetaspace

    def get_jmx(self, infolist):
        """
        从get_jvm_info2list函数返回的list内容中，匹配-D开头的jvm参数,匹配-Dcom.sun.management.jmxremote.port参数判断该节点是否配在了jmx监控
        :param infolist:
        :return: True or None
        """
        jmx = []
        for part in infolist:
            dstart_part = re.compile(r"-D(.*)")
            find_dstart = dstart_part.match(part)
            if find_dstart is not None:
                jmx_D = find_dstart.group()
                jmx.append(jmx_D)
        for jmx_part in jmx:
            jmx_D_split = jmx_part.split("=")
            if jmx_D_split[0] == '-Dcom.sun.management.jmxremote.port':
                jmx_set = True
                return jmx_set

    def get_tomcat_install(self, jmxinfo):
        """
        查找Dcatalina.home的绝对路径
        :param jmxinfo: jmx and other jvm param
        :return: Dcatalina.home的绝对路径
        :type: str
        """
        for part in jmxinfo:
            re_tomcat_install = re.compile(r"-Dcatalina.home=(.*)")
            tomcat_install = re_tomcat_install.match(part)
            if tomcat_install is not None:
                tomcat_install_local = tomcat_install.groups(1)[0]
                return tomcat_install_local

    def get_startup_location(self, tomcatBaseHome):
        """
        根据-Dcatalina.home，查找tomcat的startup.sh脚本的绝对路径
        :param jmxinfo: -Dcatalina.home的绝对路径
        :return: tomcat的startup.sh脚本的绝对路径
        :type: str or None
        """
        startup_location = tomcatBaseHome + "/bin/startup.sh"
        if not os.path.exists(startup_location):
            logging.error("{0}文件不存在,请检查".format(startup_location))
            return None
        else:
            return startup_location

    def get_netstat_db(self, dbRuslt=True):
        """
        当get_tomcat_jndi函数返回值为None时，执行该函数，通过netstat命令获取和数据库建链情况
        :param dbRuslt: 是否执行该函数，默认为不执行
        :return:
        """
        if not dbRuslt:
            db_port = ["3306", "1521"]
            for port in db_port:
                _comm = "netstat -anp|grep -v grep |grep " + port + "|grep " + self.pid
                _ex_comm = commands.getstatusoutput(_comm)
                if _ex_comm[0] == 0:
                    _net_info = [x.split()[4] for x in _ex_comm[1].split("\n")]
                    _net_db = list(set(_net_info))
                    return _net_db
                else:

                    return None
        else:
            return


class set_param2json():
    """ 将所需字段封装到一个字典中 """

    def __init__(self, func, tomcat_pid):
        """
        :param func: get_tomcat_info对象
        :param tomcat_pid: 单个tomcat进程的pid
        """
        self.func = func
        self.tomcat_pid = tomcat_pid

    @property
    def param2json(self):
        """
        获取相关信息放入list中
        :return: tomcat、jvm、jmx以及db的相关信息
        :rtype: list
        """

        user = self.func.get_user(self.tomcat_pid)
        appname = self.func.app_name("tomcat")
        jdkversion = self.func.get_jdk_version(self.tomcat_pid)

        json_dick['JdkVersion'] = jdkversion
        json_dick['user'] = user
        json_dick['AppName'] = appname
        proc_info = get_proc_info(pid=self.tomcat_pid)
        proc_jvm = proc_info.get_jvm_info
        proc_jvm_list = proc_info.get_jvm_info2list(proc_jvm)

        if json_dick['JdkVersion'][:3] == '1.8':
            json_dick['jvm_Xms'], json_dick['jvm_Xmx'], json_dick['jvm_Perm'], \
            json_dick['jvm_MaxPerm'], json_dick['jvm_Metaspace'], json_dick['jvm_MaxMetaspace'] = proc_info.get_jvm(proc_jvm_list)
        else:
            json_dick['jvm_Xms'], json_dick['jvm_Xmx'], json_dick['jvm_Perm'], \
            json_dick['jvm_MaxPerm'], json_dick['jvm_Metaspace'], json_dick['jvm_MaxMetaspace'] = proc_info.get_jvm(proc_jvm_list)

        if proc_info.get_jmx(proc_jvm_list) is None:
            json_dick['jmx'] = False
        else:
            json_dick['jmx'] = proc_info.get_jmx(proc_jvm_list)
        json_dick['InstallDir'] = proc_info.get_tomcat_install(proc_jvm_list)
        json_dick['startup_location'] = proc_info.get_startup_location(json_dick['InstallDir'])
        json_dick['port'] = _init.get_tomcat_port(json_dick['InstallDir'])

        db_info = _init.get_tomcat_jndi(json_dick['InstallDir'])
        if db_info:
            json_dick['jdbc'] = _init.get_tomcat_jndi(json_dick['InstallDir'])
        else:
            db_info_list = proc_info.get_netstat_db(dbRuslt=False)
            if db_info_list:
                json_dick['jdbc'] = ','.join(db_info_list)
            else:
                json_dick['jdbc'] = None

        json_dick['mode'], json_dick['maxThreads'], json_dick['minThreads'] = _init.get_tomcat_mode(json_dick['InstallDir'])
        json_dick['webapps_files'] = _init.get_tomcat_webapps(json_dick['InstallDir'])
        json_dick['version'] = _init.get_tomcat_version(tomcatBaseHome=json_dick['InstallDir'],
                                                        username=json_dick['user'])

        return json_dick


if __name__ == "__main__":
    # 初始化对象,根据命令行命令搜索运行中的Tomcat进程
    _init = get_tomcat_info("ps axu|grep java |grep -v grep|grep 'config.file'|grep '\-Dcatalina.home'", appType='Tomcat')
    # 获取运行中进程的pid,组装为list
    pidlist = _init.pidList
    ret_list = []
    # 循环获取当前机器上的tomcat进程的pid
    for idnu in pidlist:
        json_dick = {}
        _init_set_param2json = set_param2json(func=_init, tomcat_pid=idnu)
        tomcat_base_param = _init_set_param2json.param2json
        ret_list.append(tomcat_base_param)
    node_dict = json.dumps(ret_list, sort_keys=True, indent=4, separators=(',', ': '), encoding='utf8',
                           ensure_ascii=True)

    print node_dict
