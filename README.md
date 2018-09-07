# moguding-spider

#### 项目介绍
蘑菇丁爬虫

#### 软件架构
软件架构说明
spider_org1.py : 地方登记数据爬取（约80w条）
spider_org2.py : 明政局登记数据爬取（约2000条）
update.py:          更新数据库（地方登记）

#### 安装教程

需要使用的python库：
pymysql，re，selenium，lxml，json
及其他python自带库


#### 使用说明

点击运行
使用selenium库启动浏览器，获取网页JS渲染后的html代码，提取所需要的字段数据并存入mysql数据库中。
第一次启动会生成爬取页面进度记录文件，支持断点续爬，续爬需要将生成记录文件函数注释掉。
