# coding=utf-8
# 导入时间模块
import time
# 导入正则模块
import re
from newspaper import Article
# 导入第三方requests模块
import requests
from lxml import etree


class ExtractTools(object):
    def __init__(self):
        self.pattern_create_tm = re.compile('(\D|^)(20\d{2})\D(\d{1,2})\D(\d{1,2})\D{1,4}(\d{1,2})\D(\d{1,2})($|\D)')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }
        self.url_pattern = "URL='(.*?)'\">"

    # 从html文档中用正则匹配发布时间
    def extract_time_str(self, html, dt):
        try:
            if not int(dt):
                try:
                    tm = self.pattern_create_tm.search(html)
                    dt = "%s-%s-%s %s:%s" % (tm.group(2), tm.group(3), tm.group(4), tm.group(5), tm.group(6))
                except:
                    pass
            time_array = time.strptime(dt, '%Y-%m-%d %H:%M')
            return int(time.mktime(time_array))
        except:
            return 0

    # 提取图片相关信息
    def extract(self, url):
        try:
            html, after_url = self.extract_html(url)
            a = Article(url, language='zh')
            a.download()
            a.parse()
            try:
                row_t = str(a.publish_date)[0:16]
                create_time = self.extract_time_str(html, row_t)
            except:
                create_time = 0
            if not a.title:
                a.title = ''
            # url = self.url_pattern.search(html).group(1)

            # split()使用默认分隔符
            d_r = {
                'title': a.title,
                'article': a.text.split(),
                'html': html,
                'create_time': int(create_time),
                'url': after_url
            }
            return d_r
        except:
            print('抽取错误！！！')
            print(url)

    # 获取页面详情
    def extract_html(self, url):
        '''
        ①解决编码问题， 通过try  exception  获取html源码。
        ②加入Requests Headers
        :param url:
        :return: [html, after_url]
        '''
        ori = requests.get(url, headers=self.headers)
        b_html = ori.content
        after_url = ori.url
        try:
            html = b_html.decode(encoding='utf-8')
        except:
            try:
                html = b_html.decode(encoding='gbk')
            except:
                html = ori.text
        return [html, after_url]
