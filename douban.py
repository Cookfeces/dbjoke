#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-4-2 17:11:42
# @Author  : Quxm (bron7691@qq.com)

import re,urllib,urllib2,cookielib
import time
import os

email = '' #这里填入豆瓣帐号
password = '' ＃这里填入密码
cookies_file = 'Cookies_saved.txt'
#这是生成文件的文件名，是dbjoke+时期.html
filename = "dbjoke"+time.strftime('%Y-%m-%d',time.localtime(time.time()))+".html"

def check_file():
    if os.path.exists(filename):
        return True
    else:
        return False

class douban_robot:

    def __init__(self):
        self.file_name = filename
        self.email = email
        self.password = password
        self.data = {
                "form_email": email,
                "form_password": password,
                "source": "index_nav",
                "remember": "on"
        }

        self.login_url = 'https://www.douban.com/accounts/login'
        #查找并载入cookies文件
        self.load_cookies()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.opener.addheaders = [("User-agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/\
                                            537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36")]
        self.get_ck()

    def load_cookies(self):
        try:
            self.cookie = cookielib.MozillaCookieJar()
            self.cookie.load(cookies_file)
            print "loading cookies for file..."
        except Exception, e:
                print "The cookies file is not exist."
                #如果不存在cookies文件,尝试登录并生存新的cookies
                self.login_douban()
                #reload the cookies.
                self.load_cookies()

    def get_ck(self):
        #open a url to get the value of ck.
        self.opener.open('https://www.douban.com')
        #read ck from cookies.
        for c in list(self.cookie):

            if c.name == 'ck':
                self.ck = c.value.strip('"')
                print "ck:%s" %self.ck
                break
        else:
            print 'ck is end of date.'
            self.login_douban()
            # #reload the cookies.
            self.cookie.revert(cookies_file)
            self.get_ck()



    def login_douban(self):
        '''
        login douban and save the cookies into file.

        '''
        cookieJar = cookielib.MozillaCookieJar(cookies_file)
        #will create (and save to) new cookie file

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
        opener.addheaders = [("User-agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/\
                                            537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36")]
        #!!! following urllib2 will auto handle cookies
        response = opener.open(self.login_url, urllib.urlencode(self.data))
        html = response.read()
        #print (html)
        #检查是否需要输入验证码,如果需要则根据给出的网站上的验证码手动输入
        regex = r'<img id="captcha_image" src="(.+?)" alt="captcha"'
        imgurl = re.compile(regex).findall(html)
        if imgurl:
            # urllib.urlretrieve(imgurl[0], 'captcha.jpg')
            print "The captcha_image url address is %s" %imgurl[0]

            #download the captcha_image file.
            # data = opener.open(imgurl[0]).read()
            # f = file("captcha.jpg","wb")
            # f.write(data)
            # f.close()

            captcha = re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>', html)
            if captcha:
                vcode=raw_input('图片上的验证码是：')
                self.data["captcha-solution"] = vcode
                self.data["captcha-id"] = captcha.group(1)
                self.data["user_login"] = "登录"
                #验证码验证
                response = opener.open(self.login_url, urllib.urlencode(self.data))
        #登录成功
        cookieJar.save()
        if response.geturl() == "http://www.douban.com/":
            print 'login success !'
            #update cookies, save cookies into file
            # cookieJar.save();
        else:
            return False
        return True

    #获取所关注的人的昨天发表的说说
    def get_talk(self):
        talks = [];
        #在1-15页的范围内查找
        for page in range(1, 15):
            url = "https://www.douban.com/?p="+str(page)
            html = self.opener.open(url).read()
            body = re.search('<div id="content">(.*)<div id="footer">',html,re.S).group(1)
            # print (body)
            talks_page = re.findall('<div class="status-item"[ \t\n\x0B\f\r]+'
                               'data-sid=".*?"[ \t\n\x0B\f\r]+'
                               'data-action=".*?"[ \t\n\x0B\f\r]+'
                               'data-target-type="sns"[ \t\n\x0B\f\r]+'
                               'data-object-kind="1018"[ \t\n\x0B\f\r]+'
                               'data-object-id.*?>.*?'
                               '<div class="usr-pic">[ \t\n\x0B\f\r]+'
                               '<a href="(.*?)".*?'
                               '<img src="https://img[0-9]+.doubanio.com/icon/.*?"[ \t\n\x0B\f\r]+'
                               'alt="(.*?)"/>.*?'
                               '<div class="status-saying">'
                               '(.*?)'
                               '</div>[ \t\n\x0B\f\r]+'
                               '<div class="actions">.*?'
                               '<span class="created_at"[ \t\n\x0B\f\r]+'
                               'title=.*?>[ \t\n\x0B\f\r]*'
                               '<a href=".*?">(.*?)</a></span>[ \t\n\x0B\f\r]+'
                               '<a href="(.*?)"[ \t\n\x0B\f\r]+'
                               'class=".*?"[ \t\n\x0B\f\r]+'
                               '.*?'
                               '&nbsp;&nbsp;(.*?)&nbsp;&nbsp;', body, re.S)
            for item in talks_page:
                #print (item[0]+item[1]+item[2]+"  "+str(page))
                if item[3] == "昨天":
                    seq = ('id', 'content','page_addr','like_count')
                    talk_item = dict.fromkeys(seq)
                    talk_item["id"] = item[1]
                    talk_item["id_addr"] = item[0]
                    talk_content = re.search('<blockquote>.*?<p>(.*?)</p>.*?</blockquote>',
                                             item[2],re.S)
                    if talk_content:
                        talk_item["content"] = talk_content.group(1)
                    else:
                        talk_item["content"] = ""
                    talk_item["page_addr"] = item[4]
                    talk_item["like_count"] = item[5]
                    talks.append(talk_item)
        for item in talks:
            #print item["id"]+"  :  "+item["content"]
            #print item["page_addr"]
            #print item["like_count"]
        return talks

    #筛选说说中段子或者获赞数大于50的说说
    def get_jokes(self):
        talks_yesterday = self.get_talk();
        for item in talks_yesterday:
            like_count = re.search('<span class="count like-count" data-count="(.*?)">',
                                    item["like_count"], re.S)
            if like_count and int(like_count.group(1)) > 50:
                print (item["page_addr"])
                print (like_count.group(1))
            else:
                url = item["page_addr"]
                html = self.opener.open(url).read()
                comment_item = re.search('<div class="comment-item".*?'
                                         '<p class="text">(.*?)</p>',
                                         html,re.S)
                if comment_item:
                    #筛选的标准是恢复中含有如下内容
                    is_joke = re.search('哈|hh|ha|233',
                                        comment_item.group(1),
                                        re.S)
                    if is_joke:
                        print (item["page_addr"])
                        print (like_count.group(1))

    #获取你所关注的人的说说中的段子,并生成html文件
    def get_jokes_only(self):
        #生成html头
        self.put_html_head()
        talks_yesterday = self.get_talk()
        for item in talks_yesterday:
            like_count = re.search('<span class="count like-count" data-count="(.*?)">',
                                    item["like_count"], re.S)
            url = item["page_addr"]
            #print (url)
            html = self.opener.open(url).read()
            comment_item = re.findall('<div class="comment-item".*?'
                                     '<p class="text">(.*?)</p>',
                                     html,re.S)
            if comment_item:
                for i in range(1, len(comment_item)):
                    is_joke = re.search('哈|hh|ha|233',
                                        comment_item[i],
                                        re.S)
                    if is_joke:
                        #如果是段子,则在html中添加一项
                        # print (item["page_addr"])
                        # print (like_count.group(1))
                        self.fp.write('<div class="status-item">\n')
                        self.fp.write('<div class="author">\n'
                                      '<a href="'+item["id_addr"]+'" >'
                                      +item["id"]+
                                      '</a> 说:'
                                      '</div>\n')
                        self.fp.write('<div class="content">\n'
                                      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                                      +item["content"]+'\n'
                                      '#<a href="'+item["page_addr"]+'">链接</a>#'
                                      '</div>\n')
                        group_pic = re.findall('<div class="group-pic">[ \t\n\x0B\f\r]+'
                                               '<img src="(.*?)" class="upload-pic" />',
                                               html,re.S)
                        for pic in group_pic:
                            self.fp.write('<div class="group_pic" align="middle">\n'
                                          '<img src="'+pic+'" class="upload-pic" />\n'
                                          '</div>\n')
                        self.fp.write('</div>\n')
                        self.fp.write('<HR style="FILTER: alpha(opacity=100,finishopacity=0,style=1)" '
                                      'width="100%" '
                                      'color=#987cb9 SIZE=3>')
                        break
        #生成html尾
        self.put_html_tail()

    def put_html_head(self):
        self.fp = open(self.file_name,'w')
        self.fp.write('<!DOCTYPE HTML>\n'
                 '<html>\n'
                 '<head>\n'
                 '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n'
                 '<title>豆瓣精选瞎鸡巴扯说说</title>\n'
                 '</head>\n'
                 '<body>\n')

    def put_html_tail(self):
        self.fp.write('</body>\n'
                      '</html>\n')
        self.fp.close()


if __name__ == '__main__':
    app = douban_robot()
    app.get_jokes_only()
