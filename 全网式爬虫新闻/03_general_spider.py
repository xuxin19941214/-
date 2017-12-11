# coding=utf-8
import json
import re
from lxml import etree
import time
import Configs
# 协程并发
import gevent
from gevent import monkey
# 将一些常见的阻塞，如socket、select等会阻塞的地方实现协程跳转，而不是在那里一直等待，导致整个协程组无法工作。
monkey.patch_all()


class GeneralSpider(object):

    # url替换':'字符串为'@@'
    def convert_url2key(self, url):
        # 替换字符串
        res = url.replace(':', '@@')
        return res

    def __init__(self, base_url):
        # 配置数据库信息
        # 查询字段，并赋值到本地变量。
        mongo_rules = Configs.MongoConfigs.col_site_rule.find_one({'base_url': base_url})
        self.source_spider = mongo_rules['source_spider']
        self.base_url = base_url
        rule_site = mongo_rules['site_pattern']
        self.pattern_site = self.re_compiler_list(json.loads(rule_site))
        rule_article = json.loads(mongo_rules['detail_url_pattern'])
        self.pattern_article = self.re_compiler_list(rule_article)
        rule_exit = json.loads(mongo_rules['forbidden_site_pattern'])
        self.pattern_exit = self.re_compiler_list(rule_exit)
        self.xpath_list_article = json.loads(mongo_rules.get('xpath_list_article', '[]'))

        self.end = False
        #
        # self.xpath_createtime = mongo_rules['xpath_createtime']
        # self.xpath_title = mongo_rules['xpath_title']
        # self.xpath_list_article = mongo_rules['xpath_list_article']
        """
        self.xpath_createtime = mongo_rules['xpath_createtime']
        self.xpath_title = mongo_rules['xpath_title']
        self.xpath_list_article = mongo_rules['xpath_list_article']
        """

    # 开始运行起始url，如果end不为False,就一直循环下一个url
    def start(self):
        self.run(self.base_url)
        while not self.end:
            try:
                self.next_url()
            except Exception as e:
                print(e)

    # 遍历键值，加入列表里
    def re_compiler_dict(self, dic):
        res = dict()
        for k in dic.keys():
            res[k] = self.re_compiler_list(dic[k])
        return res

    # 在列表里增加
    def re_compiler_list(self, list_row):
        result = []
        for s in list_row:
            result.append(re.compile(s))
        return result

    def append_href(self, front_href, h):
        exit_set = ('#', '', '/')
        if h.startswith('java') or (h in exit_set):
            return front_href
        if ''.find(' ') > 0:
            return front_href
        # startswith用于检查字符串是否以指定字符串开头
        if not h.startswith('http'):
            return front_href + h
        else:
            return h

    def push_href(self, url, html):
        print(url)
        try:
            xhtml = etree.HTML(html)
            hrefs = xhtml.xpath('//a/@href')
        except:
            return
        try:
            end = url.index('/', 7)
            front_href = url[:end]
        except:
            front_href = url
        after_hrefs = [self.append_href(front_href, h) for h in hrefs]
        for after_href in after_hrefs:
            # 查重
            Configs.ToolsObjManager.spider_tool.sadd_value(self.convert_url2key(self.base_url), after_href)
        # return after_hrefs

    def next_url(self):
        url = Configs.ToolsObjManager.spider_tool.spop_value(self.convert_url2key(self.base_url))
        if url:
            self.run(url)
        else:
            self.end = True

    def save_url(self, url):
        '''
        查重， 抽取数据，存储到mongodb库  加入重复
        :param url:
        :return:html
        '''
        print('ready save %s' % url)
        harvest = Configs.ToolsObjManager.extract_tool.extract(url)
        if not harvest['article']:
            print('未抽取到正文。')
            return ''
            # raise Exception('未取到正文')
        # self.tool.print_log('准备存入数据')
        Configs.MongoConfigs.db_web.web_data.insert_one(
            {
                'by_xpath': 2,
                'url': url,
                'title': harvest['title'],
                'crawling_time': int(time.time()),
                'create_time': harvest['create_time'],
                'article': harvest['article'],
                'source_spider': self.source_spider
            }
        )
        Configs.MongoConfigs.db_web.web_data_snapshoot.insert_one({
            'url': url,
            'snap_shot': harvest['html']
        })
        Configs.ToolsObjManager.general_tool.print_log('成功存入数据')
        return harvest['html']

    def run(self, url):
        # isinstance内建函数，判断对象是否为可迭代对象
        if isinstance(url, bytes):
            url = url.decode()


        # 判断是否退出。
        for exit_pattern in self.pattern_exit:
            if exit_pattern.search(url):
                return

        # 是否是详情页面， 是--》抽取正文，存储，去重加入
        for detail_pattern in self.pattern_article:
            if detail_pattern.search(url):
                # 去重
                # repeat = requests.post('http://127.0.0.1:8883/url_sismember', data={'url': url}).text
                repeat = Configs.ToolsObjManager.spider_tool.\
                    sismember_value(Configs.Configs.redis_key_general_spider, url)
                if not repeat:
                    html = self.save_url(url)
                    if not html:
                        return
                    self.push_href(url, html)
                    # requests.post('http://127.0.0.1:8883/url_add', data={'url': url}).text
                    Configs.ToolsObjManager.spider_tool.sadd_value(Configs.Configs.redis_key_general_spider, url)

                return

        # 是导航页面：抽取href，
        for nav_pattern in self.pattern_site:
            if nav_pattern.search(url):
                html = Configs.ToolsObjManager.extract_tool.extract_html(url)[0]
                self.push_href(url, html)
                return
        # 加入重复
        # requests.post('http://127.0.0.1:8883/url_add', data={'url': url}).text
        Configs.ToolsObjManager.spider_tool.sadd_value(Configs.Configs.redis_key_general_spider, url)

if __name__ == "__main__":
    # 0为什么要加双引号
    print("0")
    res = Configs.MongoConfigs.col_site_rule.find()
    print(1)
    spawn_list = []
    for i in res:
        g = GeneralSpider(i["base_url"])
        spawn_list.append(gevent.spawn(g.start))
    gevent.joinall(spawn_list)
