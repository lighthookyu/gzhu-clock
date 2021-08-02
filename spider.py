import requests
import re
import execjs
import json
from datetime import datetime, date
import time
import os


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
    context = execjs.compile(js_from_file(r'.\des.js'))
    result = context.call("strEnc", un+psd+lt, '1', '2', '3')
    return result


class GZHU(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = requests.session()
        self.duplicate_key = date.today().isoformat() + ":" + self.username

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
        '''
        cookies = requests.utils.dict_from_cookiejar(self.client.cookies)
        with open("cook.txt", "w") as fp:
            json.dump(cookies, fp)
        '''
        return True

    def clock_in(self, stu_id, days=None):
        res = self.client.get('http://yqtb.gzhu.edu.cn/infoplus/form/XNYQSB/start')

        # get csrfToken
        csrfToken = re.findall(r'<meta itemscope="csrfToken" content="(?P<token>.*?)">', res.text)

        # before getting the URL with stepId
        form_get_url = {
            'idc': 'XNYQSB',
            'release': '',
            'csrfToken': csrfToken[0],
            'lang': 'zh'
        }
        res_get_url = self.client.post('http://yqtb.gzhu.edu.cn/infoplus/interface/start', data=form_get_url)

        # get URL with stepId from response
        url = json.loads(res_get_url.text)['entities'][0]

        # get json
        stepId = re.findall(r'form/(?P<id>.*?)/render', url)
        form = {
            'stepId': stepId,
            'instanceId': '',
            'admin': 'false',
            'rand': '114.514',
            'width': '1536',
            'lang': 'zh',
            'csrfToken': csrfToken[0]
        }
        self.client.headers.update({'referer': 'http://yqtb.gzhu.edu.cn/infoplus/form/XNYQSB/start'})
        data = self.client.post(url='http://yqtb.gzhu.edu.cn/infoplus/interface/render', data=form)
        data_json = json.loads(data.text)['entities'][0]

        # get boundField (dummy)
        field = ''
        for key in data_json['fields']:
            field += key
            field += ','
        field = field[:-1]

        form_data = data_json['data']

        form_data['_VAR_ENTRY_NAME'] = '学生健康状况申报_'
        form_data['_VAR_ENTRY_TAGS'] = '疫情应用,移动端'
        form_data['_VAR_URL'] = url
        form_data['fieldCNS'] = 'True'  # 打勾
        form_data['fieldJKMsfwlm'] = '1'  # 绿码

        # check in ahead of schedule
        if days:
            form_data['fieldSQSJ'] += (days * 86400)

        # convert timestamp to datetime and it will be displayed later
        timestamp = form_data['fieldSQSJ'] + 8 * 3600
        _datetime = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        form = {
            'actionId': '1',
            'formData': json.dumps(form_data),
            'rand': '114.514191981',
            'remark': '',
            'nextUsers': '{}',
            'stepId': stepId,
            'timestamp': str(int(time.time())),
            'boundFields': field,
            'csrfToken': csrfToken[0],
            'lang': 'zh'
        }

        submit = self.client.post('http://yqtb.gzhu.edu.cn/infoplus/interface/doAction', data=form)

        if '打卡成功' in submit.text:
            print('打卡成功: {} : {}'.format(stu_id, _datetime))
            return '成功'
        else:
            print('打卡失败: {} : {}'.format(stu_id, _datetime))
            return '失败:' + submit.text

