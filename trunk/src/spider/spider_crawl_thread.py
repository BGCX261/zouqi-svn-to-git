#coding=utf-8

import threading
import Queue
import logging
import time

from spider_mysqldb import Spider_MySQL_DBProcess
from spider_website_base import Spider_Website_Base
from spider_data_base import ZQ_Website_Desc
from spider_data_base import ZQ_Website_Country_Url
from spider_data_base import ZQ_Website_City_Url
from spider_data_base import ZQ_Website_Hotel_Url

class Crawl_Website_Thread(threading.Thread):
    '''
         爬行用的线程，用于高效的爬行
    '''
    
    #
    CRAWL_SIGN_RUN        = 10001
    CRAWL_SIGN_DONE_EXIT  = 10002 
    CRAWL_SIGN_FORCE_EXIT = 10003
     
    def __init__(self,crawl_website,crawl_queue,saveto_db):
        threading.Thread.__init__(self)
        self._crawl_website = crawl_website
        self._crawl_queue = crawl_queue
        self._run_sign = Crawl_Website_Thread.CRAWL_SIGN_RUN
        self._saveto_db = saveto_db 
        
        self._logger = logging.getLogger()
 
    def run(self):
        
        while((self._run_sign == Crawl_Website_Thread.CRAWL_SIGN_RUN) or \
        (self._run_sign == Crawl_Website_Thread.CRAWL_SIGN_DONE_EXIT and  self._crawl_queue.qsize() > 0)):
            
            try:
                crawl_object = self._crawl_queue.get(timeout=1)
            except Queue.Empty:
                continue
                
            if (isinstance(crawl_object,ZQ_Website_Desc)):
                self._crawl_website.crawlweb_countryurl(crawl_object,self._saveto_db)
            elif (isinstance(crawl_object,ZQ_Website_Country_Url)):
                self._crawl_website.crawlweb_cityurl(crawl_object,self._saveto_db)
            elif (isinstance(crawl_object,ZQ_Website_City_Url)):
                self._crawl_website.crawlweb_hotelurl(crawl_object,self._saveto_db)
            elif (isinstance(crawl_object,ZQ_Website_Hotel_Url)):
                self._crawl_website.crawlweb_hoteldesc(crawl_object,self._saveto_db)
            time.sleep(1)

            
    def set_run_sign(self,run_sign):
        self._run_sign = run_sign
            
            