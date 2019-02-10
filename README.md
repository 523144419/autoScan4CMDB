# autoScan4CMDB
CMDB中各类中间件的CI扫描

## 脚本名称：ssl_verification_check.py

### -- 功能：
  #### 1、对于https证书获取证书有效期
  #### 2、生成表格记录跟踪状态
### -- 依赖：
  ### pip install softinfo==0.2
### -- Usages:
  python ssl_verification_check.py -d “https://www.baidu.com,https://126.com”
  
## 脚本名称：get_jar_info.py

### -- 功能：
  #### 1、获取系统运行中的jar包或者war包的jvm属性、jmx信息以及进程信息
  #### 2、已json格式输出
  #### 3、如没有运行中的进程则默认输出用已标识
### -- 依赖：
  ### pip install softinfo==0.2
### -- Usages:
  python get_jar_info.py
  
