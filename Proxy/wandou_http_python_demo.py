#encoding=UTF-8
import http.client
import base64

# 请求头认证方式暂时不支持https协议
# 请通过添加ip白名单方式添加全局支持
# 添加白名单接口: https://h.wandouip.com/get/add-white-list?iplist=你的公网ip (登录状态下调用，公网ip请通过网络查询)

def base_code(username, password):
    str = '%s:%s' % (username, password)
    encodestr = base64.b64encode(str.encode('utf-8'))
    return '%s' % encodestr.decode()


if __name__ == '__main__':
    username = "xxxxxxxx"  # 您的用户名
    password = "xxxxx"  # 您的密码
    proxy_ip = "xx.xx.xx.xx"  # 代理ip，通过http://h.wandouip.com/get获得
    proxy_port = "xxx"  # 代理端口号
    headers = {
        'Proxy-Authorization': 'Basic %s' % (base_code(username, password))
    }
    url = 'https://myip.ipip.net'
    try :
        con = http.client.HTTPConnection(proxy_ip, port=proxy_port, timeout=10)
        con.request("GET", url, headers=headers)
        resu = con.getresponse()
        text = resu.read().decode("utf-8", errors="ignore")
        print(text)
    except Exception as e:
        print(e)