# coding=utf-8
# 运行mongod实例创建一个MongoClient
from pymongo import MongoClient
from Extract_Tools import ExtractTools
from GeneralTools import GeneralTools
from SearchSpiderTools import SearchSpiderTools
from redis import StrictRedis
from SpiderTools import SpiderTool
import pymysql


class Configs(object):
    host = '127.0.0.1'
    interface_host = 'http://%s' % host
    redis_key_general_spider = 'general_climbed_url'


class RedisConfigs(object):
    sr = StrictRedis()
    # r = redis.StrictRedis(host='localhost', port=6379, db=0)


# mongo数据库的配置
class MongoConfigs(object):
    # mongo数据库的ip
    host = Configs.host
    # mongo数据库的端口号
    port = 27017
    # mongo数据库使用者的名字
    username = ''
    # mongo数据库的密码
    password = ''
    conn = MongoClient(host='122.115.46.176', port=port, username=username,
                       password=password)
    db_web = conn.portal
    col_data = db_web.web_data
    col_snapshoot = db_web.web_data_snapshoot

    db_config = conn.website_config
    col_baidu_forbid_pattern = db_config.baidu_forbid_pattern
    col_site_rule = db_config.site_rule

# class MysqlConfigs(object):
#     host = Configs.host
#     port = 3306
#     username = "root"
#     password = "mysql"
#     conn = pymysql.connect(host=host, user=username, passwd=password, db=db, charset=c, port=port)
#     cue = conn.cursor()
#     conn.rollback()
#     conn.commit()
#     conn.close()


class ToolsObjManager(object):
    extract_tool = ExtractTools()
    general_tool = GeneralTools()
    searchspider_tools = SearchSpiderTools()
    spider_tool = SpiderTool()

