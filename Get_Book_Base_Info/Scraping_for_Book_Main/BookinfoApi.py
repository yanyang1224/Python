from flask import Flask,request
import pymssql
import json

app = Flask(__name__)

# 连接数据库
conn = pymssql.connect(server='127.0.0.1',user='sa',password='123456',database='ResourcesDB')
# cur = conn.cursor()
cur = conn.cursor(as_dict=True) # 除了在建立连接时指定，还可以在这里指定as_dict=True
if not cur:
    raise NameError("数据库连接失败")

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/api/getbookinfo")
def getBookInfo():
    isbn = request.values.get('isbn')
    print(isbn)
    sql = "select top 1 isbn,title,author,publisher,publishdate as pubdate,imgurl as image from resbookinfo where isbn like '%" + isbn + "%'"
    cur.execute(sql)
    data = cur.fetchone()
    jsonData = json.dumps(data,ensure_ascii=False)
    print(json.dumps(data,ensure_ascii=False))
    print(data)
    return str(jsonData)


app.run(host='0.0.0.0',port=777,debug=True)