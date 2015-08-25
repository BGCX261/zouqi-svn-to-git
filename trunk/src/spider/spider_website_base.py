#coding=utf-8

import os
import logging
import urllib2
from spider_urllib2_extend import Spider_Extend_Handler
from spider_urllib2_extend import Spider_Openner_Builder

class Spider_Website_Base:
    '''    
    '''
    
    WEBSITE_ID_INVALID = 80000
    WEBSITE_ID_BOOKING = 80001
    
    
    def __init__ (self,website_id,website_domain,mysql_process,filesave_dir):
        ''' '''
        #处理的网页站点的ID和域名
        self._website_id = website_id
        self._website_domain = website_domain
        
        #日志模块，免得每个人都去折腾了        
        self._logger = logging.getLogger()
        
        #得到openner
        self._opener = Spider_Openner_Builder.instance().build_opener()
        
        #为了多线程考虑，用累成员对象
        self._mysql_process = mysql_process
        
        #文件保存的的目录
        self._filesave_dir = filesave_dir
    
    def openner_crawlweb(self,open_url,retry_num =3):
        ''' 对一个网页进行爬去，如果不能进行爬取，重试N次 '''
        retry_count = 0 
        resp_data = None
        while (retry_count < retry_num) :
            try :
                resp_data = self._opener.open(fullurl=open_url)
            except Exception,e:
                retry_count += 1
                self._opener.close() 
                self._logger.error("catch one exception[%s],crawl page [%s] fail.fail number %d.",str(e),open_url,retry_count)
                continue
            break
            
        if (resp_data == None):
            return None    
        rsp_content = resp_data.read()
        self._opener.close()
        return rsp_content
        
        
    def save_to_file(self,\
                     save_data,\
                     country_id=0,\
                     city_id=0,\
                     hotel_id=0,\
                     page_id=0):
        '''
                    将数据保存在某个目录中保存，目录按照网站，国家，城市，酒店的目录结构保存
        '''
        dir_name = ""
        file_name=""
        if (country_id == 0 ):
            dir_name = os.path.join(self._filesave_dir,\
                                   "%08d"%self._website_id)
            file_name = "ALL_COUNTRY_URL_%08d.html"%(page_id)
        elif (country_id != 0 and city_id ==0):
            dir_name = os.path.join(self._filesave_dir,\
                                   "%08d"%self._website_id,\
                                   "%08d"%country_id)
            file_name = "CITY_URL_%08d.html"%(page_id)
        elif (city_id != 0 and hotel_id ==0):
            dir_name = os.path.join(self._filesave_dir,\
                                   "%08d"%self._website_id,\
                                   "%08d"%country_id,
                                   "%08d"%city_id)
            file_name = "HOTEL_URL_%08d.html"%(page_id)
        elif (city_id != 0 and hotel_id !=0):
            dir_name = os.path.join(self._filesave_dir,\
                                   "%08d"%self._website_id,\
                                   "%08d"%country_id,
                                   "%08d"%city_id)
            file_name = "HOTEL_%08d_DESC_%08d.html"%(hotel_id,page_id)
        
        if (not os.path.exists(dir_name)):
            os.makedirs(dir_name)
        file_name = os.path.join(dir_name,file_name)
        try:    
            file_object = open(file_name,mode="wb")
            file_object.write(save_data)    
            file_object.close()
        except IOError,e: 
            self._logger.error("Save file [%s]fail,exception[%s].",file_name,str(e)) 
        return 0    
        
