# autoScan4CMDB
CMDB中各类中间件的CI扫描

## 脚本名称：ssl_verification_check.py

### -- 功能：
  #### 1、对于https证书获取证书有效期
  #### 2、生成表格记录跟踪状态
### -- 依赖：
  ### pip install softinfo==0.2
  ### pip install argparse
  ### pip install xlwt
### -- Usages:
  python ssl_verification_check.py -d “https://www.baidu.com,https://126.com”
### -- 脚本执行结果
![image](https://raw.githubusercontent.com/523144419/autoScan4CMDB/master/images/image_ssl_verification_check.png)
### -- exexl结果文件内容
![image](https://raw.githubusercontent.com/523144419/autoScan4CMDB/master/images/image_ssl_verification_check_execl.png)
  
## 脚本名称：get_jar_info.py

### -- 功能：
  #### 1、获取系统运行中的jar包或者war包的jvm属性、jmx信息以及进程信息
  #### 2、已json格式输出
  #### 3、如没有运行中的进程则默认输出用已标识
### -- 依赖：
  ### pip install softinfo==0.2
### -- Usages:
  python get_jar_info.py
### -- 脚本执行结果
  #### -- 有运行中jar、war包进程输出结果如下
  [
    {
        "AppName": "JAR",
        "JdkVersion": "1.8.0_171",
        "jarLocal": "/opt/jardemo/",
        "jmx": true,
        "jvm_MaxMetaspaceSize": "null",
        "jvm_MaxPermSize": "144m",
        "jvm_MetaspaceSize": "null",
        "jvm_PermSize": "144m",
        "jvm_Xms": "64m",
        "jvm_Xmx": "64m",
        "port": "11111",
        "user": "root",
        "webapps_files": "demo-0.0.1.jar"
    }
]
  #### -- 无运行中jar、war包进程输出结果如下
  [{'AppName': 'JAR'}]
  
## 脚本名称：get_tomcat_ci.py

### -- 功能：
  #### 1、获取系统运行中的tomcat中间件的jvm属性、jmx信息以及进程信息
  #### 2、已json格式输出
  #### 3、如没有运行中的进程则默认输出用已标识
### -- 依赖：
  ### pip install softinfo==0.2
### -- Usages:
  python get_tomcat_ci.py
  
