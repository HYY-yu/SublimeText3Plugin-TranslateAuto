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
        # 总翻译字符串
        query_str = str()
        # 遍历选择的每一行
        for s in self.view.sel():
            # 此处检测代码不改变
            if s.empty() or s.size() <= 1:
                break
            # 我与原作者的不同点，将每一行拼接为一个字符串
            one_line_str = self.view.substr(s)
            # print(str_)
            query_str += one_line_str
            
        # 替换换行符为空格，使其可以翻译多行（否则还是只有一行）
        query_str = query_str.replace("\n", " ")
        # 查询单词
        t = NewThread(
            getTranslationFromBaidu, (query_str,))
        t.start()
        t.join()
        # 得到翻译结果
        resultString = t.getResult()
        # 此处我将其改成原英文与中文同时显示的形式
        # v v v v v v v v v v v v v v v v v v v v
        All_Str = query_str + " | " + resultString
        # 你不喜欢的话可以将其改成
        # All_str = resultString
        # 就只会显示英文了
        # 弹窗显示
        self.view.show_popup(
            All_Str, sublime.HIDE_ON_MOUSE_MOVE_AWAY, -1, 1000, 1000)
        # 最后两个数字是弹窗大小，可以根据自己的需要更改


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
