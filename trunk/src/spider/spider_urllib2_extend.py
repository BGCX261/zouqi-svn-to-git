#coding=utf-8

# 对请求的头部进行增加Header,增加需要中文，压缩等需求，
# 对应答，根据返回信息看是否需要进行解压

import urllib2
import zlib
from gzip import GzipFile
from StringIO import StringIO


    
    

class Spider_Extend_Handler(urllib2.BaseHandler):
    """A handler to add gzip capabilities to urllib2 requests """
    # add headers to requests
    def http_request(self, req):
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:16.0) Gecko/20100101 Firefox/16.0")
        req.add_header("Accept-Encoding", "gzip, deflate")
        req.add_header("Accept", "gzip, deflate")
        req.add_header("Accept-Language", "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3")
        req.add_header("Connection", "keep-alive")
        return req
 
    # decode
    def http_response(self, req, resp):
        old_resp = resp
        
        # gzip
        if resp.headers.get("content-encoding") == "gzip":
            gz = GzipFile(
                    fileobj=StringIO(resp.read()),
                    mode="r"
                  )
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg
            
        # deflate
        if resp.headers.get("content-encoding") == "deflate":
            gz = StringIO(resp_deflate(resp.read()))
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)  # 'class to add info() and
            resp.msg = old_resp.msg
        return resp
 
    # deflate support
    def resp_deflate(data):
        # zlib only provides the zlib compress format, not the deflate format;
        # so on top of all there's this workaround:   
        try:               
            return zlib.decompress(data, -zlib.MAX_WBITS)
        except zlib.error:
            return zlib.decompress(data)
        
        
class Spider_Openner_Builder:
    """ """
    
    instance_ = None
    
    def __init__(self):
        self.proxy_conf_ =  None
        pass
    
    #配置Builder的数据，目前只有代理服务器信息
    def config_builder(self,proxy_conf=None):
        self.proxy_conf_ = proxy_conf
    
    #生成openner
    def build_opener(self):
        ''' '''
        extend_support = Spider_Extend_Handler()
        proxy_support = urllib2.ProxyHandler(self.proxy_conf_)
        opener = urllib2.build_opener( extend_support,proxy_support,urllib2.HTTPHandler)
        return opener

    #-------------------------------------------------------------------------------------------
    @staticmethod
    def instance():
        ''' '''
        if (Spider_Openner_Builder.instance_ == None):
            Spider_Openner_Builder.instance_ = Spider_Openner_Builder()
        return Spider_Openner_Builder.instance_    
    
    
    
