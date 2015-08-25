#coding=utf-8

import os
import signal
import Queue
import logging

from spider_website_base import Spider_Website_Base
from spider_mysqldb import Spider_MySQL_DBProcess
from spider_crawl_thread import Crawl_Website_Thread
from spider_website_booking import Spider_Website_Booking

class Spider_Schedule_Manager:
    '''
           爬虫的调度管理器 
    '''
    instance_ = None
    
    #队列最大长度
    CRAWL_QUEUE_SIZE      = 512
    #一次取得MYSQL队列数据
    ONCE_QUERY_ARRAY_SIZE = 256
    
    def __init__(self):
        self._db_ipaddress = ""
        self._db_user = ""
        self._db_password = ""
        self._db_port = 3306
        self._mysql_process = None
        
        
        self._crawl_website_id = Spider_Website_Base.WEBSITE_ID_BOOKING
        
        self._crawl_queue = None
        
        self._crawl_task_num = 0
        self._crawl_task_list = []
        
        self._filesave_dir = ""
        
        #日志模块，免得每个人都去折腾了        
        self._logger = logging.getLogger()
        

        
    def init(self,\
             crawl_website_id,\
             crawl_task_num,\
             saveto_db,\
             filesave_dir,\
             db_ipaddress,\
             db_usr,\
             db_password,\
             db_port=3306):
        '''
                    初始化，确定调度器如何工作
        '''
        ret = 0
        self._db_ipaddress = db_ipaddress
        self._db_user = db_usr
        self._db_password = db_password
        self._db_port = db_port
        
        self._crawl_website_id = crawl_website_id
        
        if (not os.path.exists("./%s/"%self._crawl_website_id)):
            os.mkdir("./%s/"%self._crawl_website_id)
        
        self._saveto_db = saveto_db
        self._filesave_dir = filesave_dir
        
        #为了多线程考虑，用累成员对象
        self._mysql_process = Spider_MySQL_DBProcess()
        self._mysql_process.set_db_info(db_ipaddress=self._db_ipaddress,\
                                        db_usr=self._db_user,\
                                        db_password=self._db_password,
                                        db_port=self._db_port)
        
        ret = self._mysql_process.connect_to_db()
        if (ret != 0):
            return ret
        
        self._crawl_queue = Queue.Queue(Spider_Schedule_Manager.CRAWL_QUEUE_SIZE)
        
        #Windows下的Ctrl+C 的处理
        signal.signal(signal.SIGINT, Spider_Schedule_Manager.exit_handler)
        
        self._crawl_task_num = crawl_task_num
        
        task_count = 0
        while task_count < self._crawl_task_num :
            
            crawl_task = Crawl_Website_Thread(self.create_crawl_website(),\
                                              self._crawl_queue,\
                                              self._saveto_db)
            crawl_task.start()
            self._crawl_task_list.append(crawl_task)
            task_count+=1
        return 0
        
        
    def create_crawl_website(self):
        '''
        
        '''
        mysql_hdl = Spider_MySQL_DBProcess()
        mysql_hdl.set_db_info(db_ipaddress=self._db_ipaddress,\
                              db_usr=self._db_user,\
                              db_password=self._db_password,
                              db_port=self._db_port)
        ret = mysql_hdl.connect_to_db()
        if (ret != 0):
            return None
        crawl_base = None
        if (self._crawl_website_id == Spider_Website_Base.WEBSITE_ID_BOOKING):
            crawl_base = Spider_Website_Booking(mysql_hdl,self._filesave_dir)
        else :
            assert(False)
        return crawl_base
        
    
    def readdb_countrylist_tocrawl(self,country_id = 0):
        '''
                    从DB读取国际的信息（列表），同时对他们进行爬取  
        '''
        start = 0
        while (True):
            ret = 0
            get_list = []
            ret = self._mysql_process.list_website_country_url(get_list, \
                                                               self._crawl_website_id,\
                                                               country_id,
                                                               0,
                                                               0,
                                                               start,
                                                               Spider_Schedule_Manager.ONCE_QUERY_ARRAY_SIZE)
            
            
            if (ret != 0):
                return ret
            
            len_ary = len(get_list)
            start += len_ary
            self._logger.info("Country data get all[%d] this time [%d] array to process."%(start,len_ary))
            if ( len_ary == 0):
                self._logger.info("Country data array process done.!")
                break
            for item in get_list :
                #努力讲数据放到消息队列
                while (True):
                    try:
                        self._crawl_queue.pub(item,timeout=1)
                    except Queue.Full:
                        self._logger.info("Queue is full.wait 1 second don't put into.qsize:[%d]."%self._crawl_queue.qsize())
                        continue
                    else:
                        break
        return 0
    
    def readdb_citylist_tocrawl(self,country_id=0,city_id=0,saveto_db=False):
        ''' 
                    读取城市的列表进行爬行处理 
        '''
        start = 0
        while (True):
            ret = 0
            get_list = []
            ret = self._mysql_process.list_website_city_url(get_list, \
                                                            self._crawl_website_id, \
                                                            country_id,\
                                                            city_id,\
                                                            0,\
                                                            start,\
                                                            Spider_Schedule_Manager.ONCE_QUERY_ARRAY_SIZE)
            if (ret != 0):
                return ret
        
            len_ary = len(get_list)
            start += len_ary
            self._logger.info("City data get all[%d] this time [%d] array to process."%(start,len_ary))
            if ( len_ary == 0):
                self._logger.info("City data array process done.!")
                break
            for item in get_list :
                #努力讲数据放到消息队列
                while (True):
                    try:
                        self._crawl_queue.put(item,timeout=1)
                    except Queue.Full:
                        self._logger.info("Queue is full.wait 1 second don't put into.qsize:[%d]."%self._crawl_queue.qsize())
                        continue
                    else:
                        break
        return 0            
    
    def readdb_hotellist_tocrawl(self,country_id=0,city_id = 0,hotel_id=0):
        '''
                     读取酒店的列表进行爬行处理 
        '''
        start = 0
        while (True):
            ret = 0
            get_list = []
            ret = self._mysql_process.list_website_hotel_url(get_list, \
                                                             self._crawl_website_id, \
                                                             country_id,\
                                                             city_id,
                                                             hotel_id,\
                                                             0,\
                                                             start,\
                                                             Spider_Schedule_Manager.ONCE_QUERY_ARRAY_SIZE)
        
            len_ary = len(get_list)
            start += len_ary
            self._logger.info("Hotel data get all[%d] this time [%d] array to process."%(start,len_ary))
            if ( len_ary == 0):
                self._logger.info("Hotel data array process done.!")
                break
            for item in get_list :
                #努力讲数据放到消息队列
                while (True):
                    try:
                        self._crawl_queue.put(item,timeout=1)
                    except Queue.Full:
                        self._logger.info("Queue is full.wait 1 second don't put into.qsize:[%d]."%self._crawl_queue.qsize())
                        continue
                    else:
                        break
        
        
        return 0
    
    def exit_crawl_thread(self,run_sign):
        '''
                    退出爬取的线程
        '''
        assert(run_sign == Crawl_Website_Thread.CRAWL_SIGN_DONE_EXIT or \
               run_sign == Crawl_Website_Thread.CRAWL_SIGN_FORCE_EXIT )
        
        for crawl_thread in self._crawl_task_list :
            crawl_thread.set_run_sign(run_sign)
        
        # 等待所有的线程退出
        for crawl_thread in self._crawl_task_list :
            crawl_thread.join()
        return 0    
    
    def wait_thread_exit(self):
        # 通知并且等待所有线程处理完成后退出 
        self.exit_crawl_thread(Crawl_Website_Thread.CRAWL_SIGN_DONE_EXIT)
        return 0
         
    @staticmethod
    def exit_handler(signum, frame):
        '''
                    信号退出的处理方法，Wiondows下就是Ctrl +C 
        '''
        instance().exit_crawl_thread(Crawl_Website_Thread.CRAWL_SIGN_FORCE_EXIT)
    
    @staticmethod
    def instance():
        '''
                    单子实例函数
        '''
        if (Spider_Schedule_Manager.instance_  == None ):
            Spider_Schedule_Manager.instance_ = Spider_Schedule_Manager()
        return Spider_Schedule_Manager.instance_
    
    