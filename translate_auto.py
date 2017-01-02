import threading
import random
import hashlib
import json
from urllib import request, parse

import sublime
import sublime_plugin

appid = '20170101000035055'
secretKey = '42I1a2L4KencJQ6vraSD'
targetUrl = 'https://fanyi-api.baidu.com/api/trans/vip/translate'


def getTranslationFromBaidu(src):
    q = src
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    md5Value = hashlib.md5()
    md5Value.update(sign.encode('utf-8'))
    sign = md5Value.hexdigest()

    postData = {
        'appid': appid,
        'q': q,
        'sign': sign,
        'salt': salt,
        'from': 'auto',
        'to': 'zh'
    }

    postDataEncode = parse.urlencode(postData)
    f = request.urlopen(targetUrl, data=postDataEncode.encode())
    data = f.read()
    jsonResultString = data.decode('utf-8')
    jsonResult = json.loads(jsonResultString)

    trans_result = jsonResult['trans_result']
    dst = trans_result[0]['dst']
    return dst


class translateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for s in self.view.sel():
            if s.empty() or s.size() <= 1:
                break
            # 只处理第一个Region，其它忽略
            str = self.view.substr(s)
            print(str)
            # 查询单词
            t = NewThread(
                getTranslationFromBaidu, (str,))
            t.start()
            t.join()

            # 得到翻译结果 弹窗显示
            resultString = t.getResult()
            self.view.show_popup(
                resultString, sublime.HIDE_ON_MOUSE_MOVE_AWAY, -1, 600, 500)
            break


class NewThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def getResult(self):
        return self.res

    def run(self):
        self.res = self.func(*self.args)
