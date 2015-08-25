#coding=utf-8

import os
import sys
import logging

from spider_log_dayrotating_hdl import DayRotating_FileHandler
from spider_mysqldb import Spider_MySQL_DBProcess
from spider_website_base import Spider_Website_Base
from spider_website_booking import Spider_Website_Booking
from spider_urllib2_extend import Spider_Extend_Handler
from spider_urllib2_extend import Spider_Openner_Builder
from spider_schedule_manager import Spider_Schedule_Manager


class Spider_Application:
    '''爬虫的application '''
    def __init__(self):
        self._logger = None
        return None
    
    def init_log(self,log_level):
        ''' APPlication 日志输出的初始化，搞后台的，就靠日志救命呀'''
        if (not os.path.exists("./log/")):
            os.mkdir("./log/")
            
        logger = logging.getLogger()
        
        formatter = logging.Formatter('%(asctime)s[%(levelname)s]%(message)s')
        
        
        #按天生成日志文件
        filehandler = DayRotating_FileHandler("./log/spider_",10)
        # 设置后缀名称，跟strftime的格式一样
        #filehandler.suffix = r"%Y%m%d.log"
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
        
        logger.setLevel(log_level)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        self._logger =  logger
        return None
    
    def init_app(self): 
        ''' 服务矜持初始化 '''
        ret = 0
        self.init_log(logging.DEBUG)
        self._logger.info("application init start.")
        Spider_MySQL_DBProcess.instance().set_db_info( db_usr="root", db_password="zxzxzx")
        ret = Spider_MySQL_DBProcess.instance().connect_to_db()
        if (ret != 0):
            return ret
        
        Spider_Openner_Builder.instance().config_builder({'http': 'http://proxy.tencent.com:8080/'})
        #Spider_Openner_Builder.instance().config_builder()
        
        Spider_Schedule_Manager.instance()
        Spider_Schedule_Manager.instance().init(80001,\
             10,\
             True,\
             "E:/My.Travel/",
             "127.0.0.1",\
             "root",\
             "zxzxzx")
        
        return 0
        
    def run_app(self):
        # print (content)
        self._logger.info("application run start.")

        
        #Spider_Schedule_Manager.instance().readdb_citylist_tocrawl(country_id=96)
        
        Spider_Schedule_Manager.instance().readdb_hotellist_tocrawl(hotel_id=1000)
             
        Spider_Schedule_Manager.instance().wait_thread_exit()
        return 0
    
    @staticmethod
    def spider_main():
        ''' 全局主函数 '''
        ret = 0
        #Windows的代码不对
        if (sys.getdefaultencoding() != "utf-8"):
            reload(sys)  
            sys.setdefaultencoding('utf-8')
        print "spider application encoding %s."%sys.getdefaultencoding()
        
        spider_app = Spider_Application()
        ret = spider_app.init_app()
        if (ret != 0 ):
            spider_app._logger.error("spider application init fail.")
            return ret
        ret = spider_app.run_app()
        if (ret != 0 ):
            spider_app._logger.error("spider application run fail.")
            return ret
        return 0
    

if __name__ == "__main__":
    Spider_Application.spider_main()

    
    
  