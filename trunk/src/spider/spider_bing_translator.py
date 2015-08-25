# coding=utf-8
'''    
Bing translator API V2
包括功能，
翻译，
得到多种翻译结果
得到字符串编码
增加翻译条目（可以影响翻译结果）
得到语音

网上有些兄弟写过，但是大部分是是对于V1的版本的，V2版本改了验证方式
现在微软已经使用了新的验证方式，使用APPID的方法已经玩不转了。必须用一个access token的东东
使用需要一个客户端ID和一个客户端密码，需要在MS的网上申请，我下面的连接里面都有

清参考
http://api.microsofttranslator.com
http://blogs.msdn.com/b/translation/p/gettingstarted1.aspx


杂记
Goolge translate API已经收费，我们的好日子没有了，
有两个选择，
1是直接用这些翻译功能的页面，然后将结果提取出来。
2.用bing的翻译API，微软这次终于上流了，可以每月用翻译200万的数据（其实就2M，还不知道他的浏览怎么算，），呵呵。

某种程度上，我最近玩的东西好像用bing翻译更上流一点，我先玩玩他，算是对我自己多年学习python的总结，
最早看python应该是8年前了，但直到最近2个月才使用，计算机是实践科学，看了不用，等于浪费，没有任何效果

'''

import urllib
import urllib2
import json
import time
import unittest
import xml.etree.ElementTree



class Get_Translate_Data(object):
    '''
    Get Translate 操作取回的数据的，解析后的得到的数据字段，
    '''
    def __init__(self):
        # #翻译结果匹配程度
        self._match_degree = 0
        # #翻译结果被用户选择的次数
        self._selected_count = 0
        # #翻译结果可以认可的比率，MS自己有一套规则，自己上参考网址看
        self._rating = 0
        # #返回的结果
        self._translated_text = ""
        
    def __str__(self):
        return ("match_degree:%s selected_count:%s rating:%s translated_text:%s")\
            % (self._match_degree, self._selected_count, self._rating, self._translated_text)


class Bing_Translator_API(object):
    '''
          此工具用于使用bing的翻译API，让你快速的得到翻译的结果
          我是按照2012年12月22日看到的API V2的要求实现的，
    Bing 翻译V2的接口包括，翻译，得到翻译候选列表，（一次翻译多个语句）设置翻译内容，得到语音，
    '''
    # 最大请求的字符长度，微软的要求
    REQ_STR_MAX_LEN = 10000
    # add trascation 增加翻译的原文最大长度
    ADD_ORIGINALTEXT_LEN = 1000
    # add trascation 增加翻译的翻译文字长度
    ADD_TRANSLATEDTEXT_LEN = 2000
    # SPEEK string的最大值
    SPEAK_STRING_LEN = 2000
    
    # 最大返回的结果个数
    RSP_RESULT_MAX_NUMBER = 10
    
    # 取得acess token的两个参数，常量
    ACCESS_TOKEN_REQ_SCOPE = "http://api.microsofttranslator.com"
    ACCESS_TOKEN_REQ_GRANT_TYPE = "client_credentials"
    
    # POST取得ACESS TOKEN的URL
    ACCESS_TOKEN_REQ_URL = "https://datamarket.accesscontrol.windows.net/v2/OAuth2-13"
    # GET方法得到翻译的结果，只得到一个结果，估计这个最常用
    TRANSLATE_REQ_URL = "http://api.microsofttranslator.com/V2/Http.svc/Translate"
    # POST取得翻译结果的结果的URL,这个是一次可以取回多个翻译结果
    GET_TRANSLATE_REQ_URL = "http://api.microsofttranslator.com/V2/Http.svc/GetTranslations"
    # 检测语句的语言
    DETECT_REQ_URL = "http://api.microsofttranslator.com/V2/Http.svc/Detect"
    # 增加翻译的URL
    ADD_TRANSLATION_URL = "http://api.microsofttranslator.com/V2/Http.svc/AddTranslation"
    # 发音的请求
    SPEAK_REQ_URL = "http://api.microsofttranslator.com/V2/Http.svc/Speak"  
    
    # LC=language code,常用的几个都写在这儿，免得你还要查询
    LC_CHINESE_SIMPLIFIED = "zh-CHS"
    LC_CHINESE_TRADITIONAL = "zh-CHT"
    LC_ENGLISH = "en"
    LC_JAPANESE = "ja"
    LC_KOREAN = "ko"
    LC_FRENCH = "fr"
    LC_GERMAN = "de"
    
    def __init__ (self, client_id, client_secret, proxy_conf=None):
        '''
        @param client_id 客户端ID，你在MS网址注册得到的ID
        @param client_secret 客户端密钥
        @param proxy_conf 代理配置,默认None，不配置,如果配置http，https都要写，
                    比如{'http': 'http://proxy.a.com:8080/','https': 'http://proxy.a.com:8080/'},折腾了我一个下午
        '''
                
        # 你请求获得acess token的两个参数，客户端ID，和一个验证密码
        self._client_id = client_id
        self._client_secret = client_secret
        
        self._token_opener = None
        self._api_opener = None
        
        # 如果有代理，配置代理
        if proxy_conf == None :
            self._token_opener = urllib2.build_opener() 
            self._api_opener = urllib2.build_opener()
        else:
            self._token_opener = urllib2.build_opener(urllib2.ProxyHandler(proxy_conf), urllib2.HTTPSHandler())
            self._api_opener = urllib2.build_opener(urllib2.ProxyHandler(proxy_conf), urllib2.HTTPHandler())
      
        self._access_token = ""         
        self._expires_time = 0
      
    

    
    def __get_acess_token(self, retry_num=3):
        '''
        @brief 得到访问的access token，如果已经有了token，而且没有超时，就不继续使用原有的token
        @retry_num 重试的次数
        '''
        # 检查超时与否，如果没有超时，什么都不做
        if (time.time() - 10 < self._expires_time):
            return 0
            
        post_data = urllib.urlencode({'client_id':self._client_id, \
                                      'client_secret':self._client_secret, \
                                      'scope':Bing_Translator_API.ACCESS_TOKEN_REQ_SCOPE,
                                      'grant_type':Bing_Translator_API.ACCESS_TOKEN_REQ_GRANT_TYPE })

        retry_count = 0 
        resp_data = None
        
        # 进行N词重试
        while (retry_count < retry_num) :
            try :        
                resp_data = self._token_opener.open(fullurl=Bing_Translator_API.ACCESS_TOKEN_REQ_URL, \
                                                    data=post_data, \
                                                    timeout=10)
            except Exception, e:
                retry_count += 1
                self._token_opener.close()
                print str(e), Bing_Translator_API.ACCESS_TOKEN_REQ_URL, retry_count
                continue
            break
        
        self._token_opener.close()
        if (retry_count == retry_num):
            return -1
        
        str_data = unicode(resp_data.read())
        
        # 分析json得到数据和超时时间，        
        token_data = json.loads(str_data)
        # 注意，不要解码，我画蛇添足的搞了1个小时才发现这个错误
        self._access_token = token_data["access_token"]
        self._expires_time = time.time() + int(token_data["expires_in"])
                    
        return 0
    
    def translate(self, from_language, to_language , want_translate, content_type="text/plain", category="general", retry_num=3):
        '''
        @brief 得到翻译,只有一个翻译结果，作为返回值返回,
        @notice 这个方法使用的是GET 请求
        @param from_language 翻译的语言，参考前面的LC_XXX定义
        @param to_language
        @param want_translate 要翻译的的文本信息，必须用UTF8的编码，
        @param content_type "text/plain" 或者"text/html"
        @param category 分类，估计可以提高翻译的准确度，但MS也没有告知我们可以填写啥，默认"general"
        @return 一个元组，第一个数值是int,==0表示成功，第二个是成功后翻译的语句，
        '''
        ret_text = ""

        if (len(want_translate) > Bing_Translator_API.REQ_STR_MAX_LEN):
            return (-1, ret_text)
        # 检查token还是否有效，以及是否需要重新获取
        ret = self.__get_acess_token(retry_num)
        if (ret != 0):
            return (ret, ret_text)
                
        # print self._api_opener.addheaders
        # 得到请求的URL
        url_all = Bing_Translator_API.TRANSLATE_REQ_URL + "?" + urllib.urlencode({'text':want_translate, \
                                   'from':from_language, \
                                   'to':to_language, \
                                   'contentType':content_type, \
                                   'category':category })
        url_req = urllib2.Request(url=url_all)
        url_req.add_header('Authorization', 'bearer ' + self._access_token)
        
        retry_count = 0 
        resp_data = None
        # 进行N次重试
        while (retry_count < retry_num) :
            try :        
                resp_data = self._token_opener.open(url_req, timeout=10)
            except Exception, e:
                retry_count += 1
                print str(e), url_req, retry_count
                continue
            else:
                break
            finally:
                self._token_opener.close()
                    
        if (retry_count == retry_num):
            return (-1, ret_text)
        
        # 解析XML结果得到数据
        xml_str = resp_data.read()
        tag = xml.etree.ElementTree.fromstring(xml_str)
        ret_text = tag.text
        
        return (0, ret_text)
     
    def get_translate(self, from_language, to_language , want_translate, result_list, \
                      content_type="text/plain", category="general", user="", uri="", retry_num=3):
        '''
        @brief 得到翻译,可能有多个翻译的结果返回，返回的是一个列表，
        @notice 这个方法使用的是GET 请求
        @param  result_list 返回参数，返回的翻译list的Get_Translator_Data
        @param  user 用户名称，默认为"",如果对翻译效果不满意，可以改为all
        @param  uri  URI
        @param 其他参数同translate函数,不多解释
        @return 返回0表示成功，其他表示失败
        '''
        
        if (len(want_translate) > Bing_Translator_API.REQ_STR_MAX_LEN):
            return -1
        # 检查token还是否有效，以及是否需要重新获取
        ret = self.__get_acess_token(retry_num)
        if (ret != 0):
            return ret
        
        
        # 得到请求的URL
        url_all = Bing_Translator_API.GET_TRANSLATE_REQ_URL + "?" + urllib.urlencode({'text':want_translate, \
                                   'from':from_language, \
                                   'to':to_language, \
                                   'maxTranslations':Bing_Translator_API.RSP_RESULT_MAX_NUMBER })
        
        # 其实不发送下面Post数据也可以发送请求(发送参数="",不能不写，否则是GET请求)，也可以得到结果，我测试过。增加下面这段反而又让我调试了半天
        # Post 请求的参数，里面的State是一个事务ID，请求带过去，返回的结果，MS给你带回来，你要希望使用，自己改造
        # 这样的到的翻译很多，但效果感觉比较糟糕，估计有些是用户添加的，如果你不喜欢，可以在User的值改为all
        post_data = "<TranslateOptions xmlns=\"http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2\">"\
                  "<Category>%s</Category>"\
                  "<ContentType>%s</ContentType>"\
                  "<ReservedFlags></ReservedFlags>"\
                  "<State>20121221</State>"\
                  "<Uri>%s</Uri>"\
                  "<User>%s</User>"\
                  "</TranslateOptions>" % (category, content_type, uri, user)
        
        
        url_req = urllib2.Request(url=url_all, data=post_data)
        url_req.add_header('Authorization', 'bearer ' + self._access_token)
        # 如果要加post数据，这行必须加，否返回500的错误，看了半天C#的例子
        url_req.add_header('Content-Type', 'text/xml')
        retry_count = 0 
        resp_data = None
        # 进行N次重试
        while (retry_count < retry_num) :
            try :        
                resp_data = self._token_opener.open(url_req, timeout=10)
            except Exception, e:
                retry_count += 1
                print str(e), url_req, retry_count
                continue
            else:
                break
            finally:
                self._token_opener.close()
        
        if (retry_count == retry_num):
            return -1
        
        # 倒霉的XML namespace，麻烦死了
        MS_GETTRNS_NAMESPACES = "http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2"
        
        xml_str = resp_data.read()
        tag = xml.etree.ElementTree.fromstring(xml_str)
        # 前面非要家那个.//，而且还必须有那个XML的名字空间{http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2}
        tans_list = tag.findall(".//{%s}TranslationMatch" % MS_GETTRNS_NAMESPACES)
        for tag_item in tans_list:
            trans_data = Get_Translate_Data()
            for iter_item in tag_item.iter():
                if iter_item.tag == "{%s}Count" % MS_GETTRNS_NAMESPACES:
                    trans_data._selected_count = int(iter_item.text)
                if iter_item.tag == "{%s}MatchDegree" % MS_GETTRNS_NAMESPACES:
                    trans_data._match_degree = int(iter_item.text)
                if iter_item.tag == "{%s}Rating" % MS_GETTRNS_NAMESPACES:
                    trans_data._rating = int(iter_item.text)
                if iter_item.tag == "{%s}TranslatedText" % MS_GETTRNS_NAMESPACES:
                    trans_data._translated_text = iter_item.text
            # print trans_data
            result_list.append(trans_data)
        return 0
            
    def detect(self, detect_text, retry_num=3):
        '''
        @brief 检查语句的语言
        @notice 这个方法使用的是GET 请求
        @param detect_text 检测的语句，必须用UTF8的编码，
        @return 一个元组，第一个数值是int,==0表示成功，否则表示失败，第二个是成功后返回语言的标识，如果失败，返回''
        '''
        ret_text = ""

        if (len(detect_text) > Bing_Translator_API.REQ_STR_MAX_LEN):
            return (-1, ret_text)
        # 检查token还是否有效，以及是否需要重新获取
        ret = self.__get_acess_token(retry_num)
        if (ret != 0):
            return (ret, ret_text)
                
        # print self._api_opener.addheaders
        # 得到请求的URL
        url_all = Bing_Translator_API.DETECT_REQ_URL + "?" + urllib.urlencode({'text':detect_text})
        url_req = urllib2.Request(url=url_all)
        url_req.add_header('Authorization', 'bearer ' + self._access_token)
        
        retry_count = 0 
        resp_data = None
        # 进行N次重试
        while (retry_count < retry_num) :
            try :        
                resp_data = self._token_opener.open(url_req, timeout=10)
            except Exception, e:
                retry_count += 1
                print str(e), url_req, retry_count
                continue
            else:
                break
            finally:
                self._token_opener.close()
                    
        if (retry_count == retry_num):
            return (-1, ret_text)
        
        # 解析XML结果得到数据
        xml_str = resp_data.read()
        tag = xml.etree.ElementTree.fromstring(xml_str)
        ret_text = tag.text
        
        return (0, ret_text)
    
    def add_translation(self, original_text, translated_text, from_language, to_language, user, \
                        rating=1, content_type="text/plain", category="general", uri="", retry_num=3):
        '''
        @brief 增加翻译内容，用于改善后面的翻译
        @notice 这个方法使用的是GET 请求
        @param original_text 原文
        @param translated_text 已经翻译的原文
        @param from_language 
        @param to_language
        @param usr 用户名称,估计在get的时候会有一些作用   
        @param rating -10~10
        @param content_type "text/plain" 或者"text/html"
        @param category 分类，估计可以提高翻译的准确度，但MS也没有告知我们可以填写啥，默认"general"
        @param uri 
        @param retry_num 重试次数
        @return 返回0表示成功，其他表示失败
        '''
        
        if (len(original_text) > Bing_Translator_API.ADD_ORIGINALTEXT_LEN):
            return -1
        if (len(translated_text) > Bing_Translator_API.ADD_TRANSLATEDTEXT_LEN):
            return -1
        # 检查token还是否有效，以及是否需要重新获取
        ret = self.__get_acess_token(retry_num)
        if (ret != 0):
            return (ret, ret_text)
                
        # print self._api_opener.addheaders
        # 得到请求的URL
        url_all = Bing_Translator_API.ADD_TRANSLATION_URL + "?" + urllib.urlencode({'originalText':original_text, \
                                   'translatedText':translated_text, \
                                   'from':from_language, \
                                   'to':to_language, \
                                   'rating':rating, \
                                   'contentType':content_type, \
                                   'category':category, \
                                   'user':user,
                                   'uri':uri })
        url_req = urllib2.Request(url=url_all)
        url_req.add_header('Authorization', 'bearer ' + self._access_token)
        
        retry_count = 0 
        resp_data = None
        # 进行N次重试
        while (retry_count < retry_num) :
            try :        
                resp_data = self._token_opener.open(url_req, timeout=10)
            except Exception, e:
                retry_count += 1
                print str(e), url_req, retry_count
                continue
            else:
                break
            finally:
                self._token_opener.close()
                    
        if (retry_count == retry_num):
            return -1
        
        return 0
    
    
    def speak(self, speak_text, language, format="audio/wav", options="MinSize", retry_num=3):
        '''
        @brief 得到翻译,可能有多个翻译的结果返回，返回的是一个列表，
        @notice 这个方法使用的是GET 请求
        @param  speak_text 
        @param  language 语言
        @param  format 为 audio/wav 或者  audio/mp3
        @param  options 为“MaxQuality” 或者 "MinSize"
        @return 返回0表示成功，其他表示失败
        '''
        
        if (len(speak_text) > Bing_Translator_API.SPEAK_STRING_LEN):
            return -1
        # 检查token还是否有效，以及是否需要重新获取
        ret = self.__get_acess_token(retry_num)
        if (ret != 0):
            return ret
        
        ret_speak = ""
        # 得到请求的URL
        url_all = Bing_Translator_API.SPEAK_REQ_URL + "?" + urllib.urlencode({'text':speak_text, \
                                   'language':language, \
                                   'format':format, \
                                   'options':options })
        url_req = urllib2.Request(url=url_all)
        url_req.add_header('Authorization', 'bearer ' + self._access_token)
        
        retry_count = 0 
        resp_data = None
        # 进行N次重试
        while (retry_count < retry_num) :
            try :        
                resp_data = self._token_opener.open(url_req, timeout=10)
            except Exception, e:
                retry_count += 1
                print str(e), url_req, retry_count
                continue
            else:
                break
            finally:
                self._token_opener.close()
                    
        if (retry_count == retry_num):
            return (-1, ret_speak)
        
        # 解析XML结果得到数据
        ret_speak = resp_data.read()
                
        return (0, ret_speak)


class Test_Bing_Translator_API(unittest.TestCase):
    '''
          单元测试，把几个代码都测试了一下。
    '''
    def setUp(self):
        # self._test_api = Bing_Translator_API(client_id="fullsail_translate",\
        #                                    client_secret="HnayjERCQyLsa7/ojUMhGTCaUJfmxLraH88r9B9J+W4=")
        self._test_api = Bing_Translator_API(client_id="fullsail_translate", \
                                            client_secret="HnayjERCQyLsa7/ojUMhGTCaUJfmxLraH88r9B9J+W4=", \
                                            proxy_conf={'http': 'http://proxy.tencent.com:8080/', 'https': 'http://proxy.tencent.com:8080/'})
        
        
    def test_translate(self): 
        ret, trans_str = self._test_api.translate(Bing_Translator_API.LC_CHINESE_SIMPLIFIED, \
                                            Bing_Translator_API.LC_ENGLISH, \
                                            "中华人民共和国");
        print ret , trans_str
    
        test_string = "中华人民共和国"
        test_gb2312 = test_string.encode('gb2312')
        # 这个地方翻译会错误，所以编码不能用GB2312这类编码
        ret, trans_str = self._test_api.translate(Bing_Translator_API.LC_CHINESE_SIMPLIFIED, \
                                            Bing_Translator_API.LC_ENGLISH, \
                                            test_gb2312);
        print ret , trans_str
    
    def test_get_translate(self):
        result_list = []
        ret = self._test_api.get_translate(Bing_Translator_API.LC_CHINESE_SIMPLIFIED, \
                        Bing_Translator_API.LC_ENGLISH, \
                        "中华人民共和国",
                        result_list);
        for trans_data in result_list :
            print trans_data
        result_list = []
        ret = self._test_api.get_translate(Bing_Translator_API.LC_ENGLISH, \
                        Bing_Translator_API.LC_CHINESE_SIMPLIFIED, \
                        "to",
                        result_list);
        for trans_data in result_list :
            print trans_data
    
    def test_detect(self):
        ret, detect_lan = self._test_api.detect("中华人民共和国")
        print ret, detect_lan
        ret, detect_lan = self._test_api.detect("made in china")
        print ret, detect_lan 
    
    def test_add_translation(self):
        ret = self._test_api.add_translation(original_text="china", \
                                    translated_text="瓷器", \
                                    from_language=Bing_Translator_API.LC_ENGLISH, \
                                    to_language=Bing_Translator_API.LC_CHINESE_SIMPLIFIED, \
                                    user="fullsail")
        print ret
        result_list = []
        ret = self._test_api.get_translate(Bing_Translator_API.LC_ENGLISH, \
                        Bing_Translator_API.LC_CHINESE_SIMPLIFIED, \
                        "china",
                        result_list,
                        user="fullsail");
        for trans_data in result_list :
            print trans_data
        
        
    def test_speek(self):
        ret, ret_speak = self._test_api.speak(speak_text="人一走，茶就凉，是自然规律；人没走，茶就凉，是世态炎凉。一杯茶，佛门看到的是禅，道家看到的是气，儒家看到的是礼，商家看到的是利。茶说：我就是一杯水，给你的只是你的想像，你想什么，什么就是你。心即茶，茶即心。", \
                        language=Bing_Translator_API.LC_CHINESE_SIMPLIFIED);
    
                        
        file_hdl = open("D:\\123.wav", "wb+")
        file_hdl.write(ret_speak)
        file_hdl.close()   


if __name__ == '__main__':
    unittest.main()    
        

    


    
    
