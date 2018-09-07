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
#### 参与贡献

1. Fork 本项目
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request


#### 码云特技

1. 使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2. 码云官方博客 [blog.gitee.com](https://blog.gitee.com)
3. 你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解码云上的优秀开源项目
4. [GVP](https://gitee.com/gvp) 全称是码云最有价值开源项目，是码云综合评定出的优秀开源项目
5. 码云官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6. 码云封面人物是一档用来展示码云会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)