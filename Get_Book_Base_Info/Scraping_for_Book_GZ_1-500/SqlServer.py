import pymssql

class SQLServer:
    def __init__(self,server,user,password,database):
        self.server = server
        self.user = user
        self.password = password
        self.database = database

    def __GetConnect(self):
        if not self.database:
            # raise(NameError,"没有设置数据库信息")
            raise NameError("没有设置数据库信息")
        self.conn = pymssql.connect(server=self.server,user=self.user,password=self.password,database=self.database)
        cur = self.conn.cursor()
        if not cur:
            # raise(NameError,"连接数据库失败")
            raise NameError("链接数据库失败")
        else:
            return cur

    def ExecQuery(self,sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        result = cur.fetchall()
        self.conn.close()
        return result