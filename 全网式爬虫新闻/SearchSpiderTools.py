from pymysql import connect


class SearchSpiderTools(object):
    def get_key_word(self):
        conn = connect(host='122.115.46.176', port=3306, user='root', password='Duba0406.', database='zkdp',
                       charset='utf8')
        sql = 'select * from keyword'
        # 操作游标
        cur = conn.cursor()
        # 执行sql语句
        cur.execute(sql)
        # 接受全部返回结果
        return cur.fetchall()




