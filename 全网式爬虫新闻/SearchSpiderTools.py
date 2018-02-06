from pymysql import connect


class SearchSpiderTools(object):
    def get_key_word(self):
        conn = connect(host='', port=, user='', password='', database='',
                       charset='utf8')
        sql = 'select * from keyword'
        # 操作游标
        cur = conn.cursor()
        # 执行sql语句
        cur.execute(sql)
        # 接受全部返回结果
        return cur.fetchall()




