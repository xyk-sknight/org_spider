import pymysql
import re
from selenium import webdriver
from lxml import etree
import time
import json
from selenium.webdriver.chrome.options import Options


def browser_ini():
    chrome_options = Options()
    chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
    chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    browser = webdriver.Chrome(chrome_options=chrome_options)
    return browser


'''打开组织信息界面'''


def org_page_open(browser, orgnum):
    org_page = browser.find_element_by_xpath('//table/tbody/tr['+str(orgnum)+']/td/a')
    org_page.click()
    browser.implicitly_wait(30)
    time.sleep(2)  # 假装看网页
    browser.switch_to.frame(0)
    text= browser.page_source
    html = etree.HTML(text)
    '''分析页面数据'''
    for item in org_item(html):
        write_sql(item)#写入数据库
        write_to_log(item['name']+';'+item['info_write_time'])#写入日志
    browser.switch_to.parent_frame()
    org_page_close = browser.find_element_by_css_selector("a[class=\"layui-layer-ico layui-layer-close layui-layer-close2\"]")
    org_page_close.click()
    time.sleep(1)


def org_item(html):
    ''''''
    '''企业名称+信用代码'''
    name_code = html.xpath('//div/h3/text()')
    name = re.findall('(.*?)\xa0\xa0', ''.join(name_code))
    code = re.findall('\d.*', ''.join(name_code))
    #print(name)
    #print(code)
    '''组织类型'''
    type = html.xpath('//table/tbody/tr[4]/td[2]/text()')
    type = ''.join(type).split()
    #print(type)
    '''企业地址'''
    address = html.xpath('//table/tbody/tr[5]/td[2]/text()')
    a = []
    for add in address:
        if (add.split() != []):
            a.append(''.join(add.split()))
    address = [''.join(a)]
    #print(address)
    '''法人'''
    representative = html.xpath('//table/tbody/tr[2]/td[2]/text()')
    representative = ''.join(representative).split()
    #print(representative)
    '''电话'''
    tel = html.xpath('//table/tbody/tr[6]/td[2]/text()')
    tel = tel[0].split()
    '''企业登记时间'''
    ini_time = html.xpath('//table/tbody/tr[2]/td[4]/text()')
    ini_time = ini_time[0].split()
    #print(ini_time)
    '''写入时间'''
    info_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #print(info_time)
    yield {
        'name': ''.join(name),
        'code': ''.join(code),
        'type': ''.join(type),
        'address': ''.join(address),
        'representative': ''.join(representative),
        'tel': ''.join(tel),
        'ini_date': ''.join(ini_time),
        'info_write_time': info_time
    }


'''写入数据库'''


def write_sql(data):
    '''登录MYSQL,连接至social_organization数据库'''
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='social_organization')
    cursor = db.cursor()
    table = 'org2'
    keys = ','.join(data.keys())
    values = ','.join(['%s'] * len(data))
    sql = 'INSERT INTO {table}({keys}) VALUE ({values})'.format(table=table, keys=keys, values=values)
    try:
        if cursor.execute(sql, tuple(data.values())):
            print("successful")
            db.commit()
    except:
        print(data)
        print('Failed')
        db.rollback()
    db.close()


'''查询初始化'''


def page_start():
    with open('result.txt', 'r')as f:
        text = re.findall('(.*?);', f.read())
    page = int(text[-1])#开始页面
    return  page


'''到达开始查询的页面'''


def go_to_page(browser,page):
    time.sleep(1)
    input_goTopage = browser.find_element_by_css_selector('input[name="to_page"]')
    input_goTopage.send_keys(str(page))
    time.sleep(1)
    button_goTopage = browser.find_element_by_css_selector(
        'a[onclick="f_goto_page(searchOrgFormL, searchOrgFormL.to_page.value);"]')
    button_goTopage.click()


'''用于初始查询页面定位'''


def write_to_file(content):
    with open('page_log.txt', 'a', encoding='utf-8') as f:
        print(type(json.dumps(content)))
        f.write(json.dumps(content, ensure_ascii=False)+';')


'''爬取记录'''


def write_to_log(content):
    with open('data_log.txt', 'a', encoding='utf-8') as f:
        print(type(json.dumps(content)))
        f.write(json.dumps(content, ensure_ascii=False)+'\n')


def main():
    browser = browser_ini()
    '''初始化'''
    browser.get('http://www.chinanpo.gov.cn/search/orgindex.html')  # 打开组织查询主页面
    browser.implicitly_wait(10)  # 隐式时间等待
    '''切换到地方登记页面'''
    button_local = browser.find_element_by_css_selector('a[href="javascript:changeTab(2);"]')
    button_local.click()

    page_s = page_start()  # 获得开始页面
    go_to_page(browser, page_s)  # 前往开始页面

    for page in range(40000-page_s):
        write_to_file(page + page_s)  # 写入当前页数
        time.sleep(1)  # 休息一下
        '''对当前页面下20个组织进行：打开页面抓取数据后关闭'''
        for org_pageNo in range(1, 21):
            time.sleep(1)

            write_to_log('第' + str(page + page_s) + '页' + str(org_pageNo))
            org_page_open(browser, org_pageNo)
            print('第', page+page_s, '页', org_pageNo)

        time.sleep(1)  # 休息一下
        button = browser.find_element_by_css_selector("a[onclick=\"f_goto_page(searchOrgFormL, 'next');\"]")  # 获取下一页按钮
        button.click()  # 点击下一页
        browser.implicitly_wait(10)  # 隐式时间等待
    browser.close()


main()
