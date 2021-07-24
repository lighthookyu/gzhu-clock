import requests
import re
import execjs

def js_from_file(file_name):
    """
    读取js文件
    :return:
    """
    with open(file_name, 'r', encoding='UTF-8') as file:
        result = file.read()
    return result


def get_rsa(un, psd, lt):
    """
    :param un:
    :param psd:
    :param lt:
    :return:
    """
    context = execjs.compile(js_from_file('./des.js'))
    result = context.call("strEnc", un+psd+lt, '1', '2', '3')
    return result


class GZHU(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = requests.session()

    def login(self):
        new_cas_url = 'https://newcas.gzhu.edu.cn/cas/login'

        res = self.client.get(new_cas_url)
        lt = re.findall(r'name="lt" value="(.*)"', res.text)

        login_form = {
            'rsa': get_rsa(self.username, self.password, lt[0]),
            'ul': len(self.username),
            'pl': len(self.password),
            'lt': lt[0],
            'execution': 'e1s1',
            '_eventId': 'submit',
        }

        resp = self.client.post(new_cas_url, data=login_form)
        print(resp)


sp = GZHU('', '')
sp.login()
