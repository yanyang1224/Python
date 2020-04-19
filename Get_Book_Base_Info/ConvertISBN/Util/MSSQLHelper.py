import pymssql

class MSSQLHelper:
    def __init__(self, server, user, password, database, charset='UTF-8', port=1433, as_dict=True):
        '''
         实例化
         server: 服务器IP
         user：用户名
         password：密码
         database：数据库名
         charset：链接编码格式，默认"UTF-8"
         port： 数据库链接端口，默认1433
         as_dict：数据返回是否为字典，默认True
         '''
        self.__conn_path = {
            'server' : server,
            'user' : user,
            'password' : password,
            'database' : database,
            'charset' : charset,
            'port' : port,
            'as_dict' : as_dict
        }

    def __GetConnect(self):
        """类方法
        连接数据库
        """
        self.conn = pymssql.connect(**self.__conn_path)
        cur = self.conn.cursor(as_dict=True)
        if not cur:
            raise NameError("链接数据库失败")
        else:
            return cur

    def ExecQuery(self, sql, arge=tuple()):
        """
        类方法
            sql:字符串sql查询语句
            return：数据list列表,无数据返回空列表
            arge:元组参数
            error:None
        """
        try:
            if not isinstance(arge,tuple):
                print("参数：",arge)
                raise Exception("type类型错误")
            cur = self.__GetConnect()
            cur.execute(sql,arge)
            result = cur.fetchall()
            self.conn.close()
            return result
        except Exception as ex:
            print("------------>操作error：",ex)
            return None

    def ExecNonQuery(self, sql, arge=''):
        """类方法
            sql:字符串sql单条更新语句
            return：插入影响行数
            arge:多数据，list()----->[(1, 'John Smith', 'John Doe')]
                 单条数据，元组
            error:-1
            eg：
            单数据：
                sql="INSERT INTO persons VALUES(1, 'John Smith', 'John Doe')"
            多数据：
                sql="INSERT INTO persons VALUES (%d, %s, %s)",
                arge=[(1, 'John Smith', 'John Doe'),
                 (2, 'Jane Doe', 'Joe Dog'),
                 (3, 'Mike T.', 'Sarah H.')]
        """
        try:
            cur = self.__GetConnect()
            if isinstance(arge,list):
                cur.executemany(sql,arge)
            else:
                cur.execute(sql,arge)
            effectRow = cur.rowcount
            self.conn.commit()
            self.conn.close()
            return effectRow
        except Exception as ex:
            print("------------>操作error：",ex)
            return -1

    class SqlClass(object):
        """复杂sql数据存储类"""
        def __init__(self, sql, arge):
            '''sql:sql
               arge:所需参数
                        插入为列表list[]
                        其他为元组()
            '''
            self.sql = sql
            self.arge = arge
    
    def transaction_sql(self, sql):
        '''
        数据库复杂sql操作，提供事务
        sql:sql操作语句类(SqlClass)列表
        return:影响行数
        error：-1
        使用方式
            sqlhelp=SQLHelp("localhost","sa","123",'GuiYang_UniversityTown_New')
            lists = list()
            lists.append(sqlhelps.SqlClass('delete from T_Model where code=%s','5201612032090000000165'))
            n = sqlhelps.transaction_sql(lists)
        '''
        try:
            if not isinstance(sql,list):
                raise Exception("参数type类型错误,异常")
            else:
                n = 0#默认0，失败
            cur = self.__GetConnect()
            for x in sql:
                if isinstance(x.arge,list):
                    cur.executemany(x.sql,x.arge)
                else:
                    cur.execute(x.sql,x.arge)
                n += cur.rowcount
                if n:
                    self.conn.commit()
            return n
        except Exception as ex:
            print("------------>操作error:",ex)
            return -1

