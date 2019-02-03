#!/bin/env python2
# coding=utf-8

import commands
import json
import logging
import sys
import re
import datetime
import argparse
import xlwt
reload(sys)
sys.setdefaultencoding("utf-8")


command_line = "curl --tlsv1.1 --user-agent  \
               \"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.1650.63 Safari/537.36\" \
               -v --connect-timeout 3 -s -I "


__all__ = [ "get_curl_result", "time_format", "day2today", "get_ssl_time" ]
__version__ = "0.0.1"

def get_cmd_args():
    """
    获取命令行输入参数
    :return: 返回对象
    """
    parser = argparse.ArgumentParser(description='get env from comandline.')
    parser.add_argument('-d',dest='domain_name',metavar='domain name',help='domain name', required=True)
    return parser.parse_args()

def format_domain_name(domain_name):
    """

    :param domain_name:
    :return:
    """
    format_domain_name = domain_name.split(",")
    return format_domain_name



def get_curl_result(url):
    """
    根据传入的url，通过curl命令获取返回内容
    :param url: url地址
    :return: list
    """
    _comm = command_line + url
    _ex_comm = commands.getstatusoutput(_comm)
    curl_result = _ex_comm[1].split("\r\n")
    curl_result_list = [ result.split("\n") for result in curl_result ]
    return curl_result_list

def time_format(t):
    """
    对于年月日进行排序输出，传入参数必须为str类型
    :param t:
    :return:
    """
    if isinstance(t, str):
        time_format_part = t.split()
        time_format = time_format_part[-2] + "年 " + time_format_part[0] + " " + time_format_part[1] + "日 " + time_format_part[2]
        return time_format
    else:
        logging.error("传入参数非字符串类型，传入参数为{0}，类型为{1}".format(t, type(t)))

def day2today(date):
    """
    获取证书到期时间距今的天数
    :param date:
    :return: day from today
    :type: str
    """
    if isinstance(date, str):
        time_format_part = date.split()
        t1 = datetime.datetime.now()#获取当前时间
        y = re.findall(r"\d+", time_format_part[0])
        m = re.findall(r"\d+", time_format_part[1])
        d = re.findall(r"\d+", time_format_part[2])

        t2 = datetime.datetime(int(''.join(y)), int(''.join(m)), int(''.join(d)))#获取指定时间
        t3 = t2 - t1
        return t3.days
    else:
        logging.error("传入参数非字符串类型，传入参数为{0}，类型为{1}".format(date, type(date)))
        return None

def get_ssl_time(curl_result, url):
    """
    获取证书的生效时间、过期时间
    :param curl_result:
    :param url:
    :return:
    """
    ssl_time = {}
    try:
        if isinstance(curl_result, list):
             for part_list in curl_result:
                 for part in part_list:
                     ssl_time["url"] = url
                     if "start date" in part:
                         start_time = part.replace('* \tstart date:', "")
                         ssl_time["start_time"] = time_format(start_time)
                     elif "expire date" in part:
                         expire_date = part.replace('* \texpire date:', "")
                         ssl_time["expire_date"] = time_format(expire_date)
                     #elif "common name" in part:
                     #    ssl_time["common_name"] = part.replace('* \tcommon name:', "")
            # ssl_time = [ ssl_time.append(part) for part_list in curl_result for part in part_list if "start date" or "expire date" in part ]
        else:
            raise ImportError
    except ImportError as e:
        logging.error("{0}".format(e))
    return ssl_time

def write2file(ssl_dict):
    wbk = xlwt.Workbook(encoding='utf-8')
    sheet = wbk.add_sheet('sheet1', cell_overwrite_ok=True)
    title = [ "序号", "域名", "证书状态", "生效时间", "过期时间","距离过期时间/天" ]
    for nu, t in enumerate(title):
        sheet.write(0, nu, t)  # 第0行第一列写入内容
    index = 1
    index_rox = 1
    try:
        if len(ssl_dict) >= 1:
            for part in ssl_dict:
                sheet.write(index, 0, index)
                for k, v in part.items():
                    if k == 'url':
                        sheet.write(index, index_rox, v)
                    elif k == 'status':
                        sheet.write(index, index_rox + 1, v)
                    elif k == 'start_time':
                        sheet.write(index, index_rox + 2, v)
                    elif k == 'expire_date':
                        sheet.write(index, index_rox + 3, v)
                    elif k == 'day_from_today':
                        sheet.write(index, index_rox + 4, v)
                index += 1
    except IOError as e:
        logging.error(e)

            #sheet.write(1,0,"test")
    # if isinstance(ssl_dict, dict):
    #     mumber = len(ssl_dict.keys())
    #     for nu in range(mumber):
    #         sheet.write(nu+1, nu+1, nu)
    #         sheet.write()

    wbk.save('/tmp/test.xls')

if __name__ == "__main__":
    args = get_cmd_args()
    domain_name = args.domain_name
    format_domain = format_domain_name(domain_name)

    all_ssl_part = []
    for u in format_domain:
        curl_result = get_curl_result(u)
        ssl_time_part = get_ssl_time(curl_result, u)
        if not ssl_time_part.has_key("start_time"):
            ssl_time_part["status"] = False
            ssl_time_part["day_from_today"] = None
            ssl_time_part["expire_date"] = None
            ssl_time_part["start_time"] = None
        else:
            ssl_time_part["status"] = True
            day = day2today(ssl_time_part["expire_date"])
            ssl_time_part["day_from_today"] = day
        all_ssl_part.append(ssl_time_part)
    ssl_time = json.dumps(all_ssl_part, sort_keys=True, indent=4,
                          separators=(',', ': '), encoding='utf8', ensure_ascii=False)
    write2file(all_ssl_part)
    print ssl_time
