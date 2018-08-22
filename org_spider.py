import pymysql
import re
from selenium import webdriver
from lxml import etree
import time

'''打开组织信息界面'''
def org_page_open(browser, orgnum):
    org_page = browser.find_element_by_xpath('//table/tbody/tr['+str(orgnum)+']/td/a')
    org_page.click()
    browser.switch_to.window(browser.window_handles[1])
    browser.implicitly_wait(30)
    time.sleep(1)#休息一下
    text = browser.page_source
    html = etree.HTML(text)
    print(html)
    for item in org_item(html):
        print(item)
        write_sql(item)#数据库写入
    time.sleep(1)
    browser.close()
    browser.switch_to.window(browser.window_handles[0])

def org_item(html):
    ''''''
    '''企业名称+信用代码'''
    name_code = html.xpath('//div/h3/text()')
    name = re.findall('(.*?)\xa0\xa0', ''.join(name_code))
    code = re.findall('\d.*', ''.join(name_code))
    '''组织类型'''
    type = html.xpath('//table/tbody/tr[5]/td[4]/text()')
    type = ''.join(type).split()
    print(type)
    '''企业地址'''
    address = html.xpath('//table/tbody/tr[6]/td[2]/text()')
    a = []
    for add in address:
        if (add.split() != []):
            a.append(''.join(add.split()))
    address = [''.join(a)]
    '''法人'''
    representative = html.xpath('//table/tbody/tr[2]/td[2]/text()')
    representative = representative[0].split()
    '''电话'''
    tel = html.xpath('//table/tbody/tr[4]/td[4]/text()')
    tel = tel[0].split()
    '''企业登记时间'''
    ini_time = html.xpath('//table/tbody/tr[2]/td[4]/text()')
    ini_time = ini_time[0].split()
    '''写入时间'''
    info_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    yield{
        'name':''.join(name),
        'code':''.join(code),
        'type':''.join(type),
        'address':''.join(address),
        'representative':''.join(representative),
        'tel':''.join(tel),
        'ini_date':''.join(ini_time),
        'info_write_time':info_time
    }
'''写入数据库'''
def write_sql(data):
    '''登录MYSQL,连接至social_organization数据库'''
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='social_organization')
    cursor = db.cursor()
    table = 'org'
    keys = ','.join(data.keys())
    values = ','.join(['%s'] * len(data))
    sql = 'INSERT INTO {table}({keys}) VALUE ({values})'.format(table=table, keys=keys, values=values)
    try:
        if cursor.execute(sql, tuple(data.values())):
            print("successful")
            db.commit()
    except:
        print('Failed')
        db.rollback()
    db.close()
def main():
    browser = webdriver.Chrome()
    browser.get('http://www.chinanpo.gov.cn/search/orgindex.html')
    browser.implicitly_wait(30)  # 隐式时间等待
    '''下一页
    for page in range(114):
        time.sleep(5)  # 休息一下
        button = browser.find_element_by_css_selector("a[onclick=\"f_goto_page(searchOrgFormM, 'next');\"]")#获取下一页按钮
        button.click()#点击下一页
        browser.implicitly_wait(10)  # 隐式时间等待
    '''

    for page in range(116-114):
        time.sleep(1)#休息一下
        '''对当前页面下20个组织进行：打开页面抓取数据后关闭'''
        for org_pageNo in range(1, 21):
            time.sleep(1)
            org_page_open(browser, org_pageNo)
            print('第',page+1+114,'页',org_pageNo)

        time.sleep(1)  # 休息一下
        button = browser.find_element_by_css_selector("a[onclick=\"f_goto_page(searchOrgFormM, 'next');\"]")#获取下一页按钮
        button.click()#点击下一页
        browser.implicitly_wait(10)  # 隐式时间等待
main()

