#coding=utf-8

import MySQLdb
import logging
from spider_data_base import *


class Spider_MySQL_DBProcess:
    '''各种数据  MySQL 入库处理的代码 '''
    
    instance_  = None
    
    #错误信息
    SUCCESS               = 0
    INVALID_ARGUMENT      = -1
    CONNECT_MYSQL_FAIL    = -2
    SQL_EXECUTE_FAIL      = -3
    SELECT_NOT_GET_DATA   = -4
    REPLACE_NOT_SET_DATA  = -5
    UPDATE_NOT_SET_DATA   = -6
    
    #-------------------------------------------------------------------------------------------
    def __init__(self):
        self.db_ipaddress_ = "127.0.0.1"
        self._db_user = "root"
        self._db_password = ""
        self._db_port = 3306
        self._if_connect_db = False
        self._db_handle = None
        self._db_cursor = None
        self._logger = logging.getLogger()
        
    def __del__(self):
        ''' '''
        self.disconnect()
    
    #-------------------------------------------------------------------------------------------
    def set_db_info(self,db_ipaddress="127.0.0.1", db_usr="root", db_password="", db_port=3306):
        ''' '''
        self.db_ipaddress_ = db_ipaddress
        self._db_user = db_usr
        self._db_password = db_password
        self._db_port = db_port
        return
                
    def connect_to_db(self):
        ''' 连接数据库 '''
        try:
            self._db_handle = MySQLdb.connect(host=self.db_ipaddress_ , 
                                              user=self._db_user, 
                                              passwd=self._db_password ,
                                              port=self._db_port,
                                              charset="utf8")
        except MySQLdb.Error, e:
            self._logger.error("Connect fail.Error %d: %s" % (e.args[0], e.args[1]))
            return -1
        
        self._if_connect_db = True
        self._db_cursor = self._db_handle.cursor()
        self._logger.info("Connect %s |%d mysql server success."%(self.db_ipaddress_,self._db_port))     
        return 0
    
    def disconnect(self):
        ''' 断开连接数据库 '''
        if self._if_connect_db == True :
            self._db_handle.close()
            self._if_connect_db = False 
            self._db_cursor.close()
            
    #-------------------------------------------------------------------------------------------        
    def get_country_define(self, get_data):
        '''取得国家配置信息  
                    返回值的第一个值标识是否成功，==0 执行成功，
                    返回值的第二个值表示执行后取得的数据数量 '''
        
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "" 
        if (get_data._country_id != 0) :
            sql_string = "SELECT country_id,country_cn_name,country_en_name " \
            "FROM web_rawdata.country_define WHERE (country_id=%d)" % get_data._country_id
        elif (cmp(get_data._country_cn_name , "") != 0) :
            sql_string = "SELECT country_id,country_cn_name,country_en_name " \
            "FROM web_rawdata.country_define WHERE "\
            "(UPPER(country_cn_name)=UPPER('%s') OR (UPPER(country_en_name)=UPPER('%s')))" \
            % (self._db_handle.escape_string(get_data._country_cn_name),\
               self._db_handle.escape_string(get_data._country_cn_name))
        else:
            return (-1,0)
        #print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return (-1,0)
        item = self._db_cursor.fetchone()
        
        #执行成功，但没有取得数据
        if (item == None) :
            return (0,0)
        
        #print "Get item %s"%(str(item))
        #你可以认为get_data是一个字典，可以改变
        get_data._country_id =  item[0]
        get_data._country_cn_name  = item[1]
        get_data._country_en_name = item[2] 
        
        return (0,1)
    
    def set_country_define(self, set_data):
        '''设置国家配置信息 
                    返回值的第一个值标识是否成功，==0 执行成功，
                    返回值的第二个值表示执行后修改改变的数据数量 '''
        
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句,使用REPLACE INTO的语句进行处理
        sql_string = "REPLACE INTO web_rawdata.country_define (country_id,country_cn_name,country_en_name) " \
            "VALUES (%d,'%s','%s')" \
            % (set_data._country_id,\
            self._db_handle.escape_string(set_data._country_cn_name),\
            self._db_handle.escape_string(set_data._country_en_name))
        try:
            #print sql_string
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        
        #如果有插入ID，保存下来
        if (self._db_handle.affected_rows() > 0 and set_data._country_id == 0) :
            set_data._country_id = self._db_handle.insert_id()
        
        return 0
    
    #    CREATE TABLE IF NOT EXISTS web_rawdata.website_country_url (
    #    website_id              INT UNSIGNED NOT NULL,   
    #    country_id              INT UNSIGNED NOT NULL,
    #    country_city_url        VARCHAR(1024) NOT NULL,                                            -- 
    #    spider_priority         INT UNSIGNED NOT NULL DEFAULT 0,                                   -- 爬虫的优先级
    #    last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
    #PRIMARY KEY (website_id,country_id)
    #)ENGINE=MyISAM DEFAULT CHARSET=utf8;

    def get_website_country_url(self, get_data):
        '''取得站点对国家信息描述的代码  
                    返回值的第一个值标识是否成功，==0 执行成功，
                    返回值的第二个值表示执行后修改改变的数据数量 '''
                    
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "" 
        if (get_data.website_id != 0 and get_data._country_id != 0) :
            sql_string = "SELECT website_id,country_id,country_city_url,spider_priority " \
            "FROM web_rawdata.website_country_url WHERE ((website_id=%d )AND(country_id=%d))" \
            % (get_data._website_id,get_data._country_id)
        else:
            return (-1,0)
        #print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return (-1,0)
        item = self._db_cursor.fetchone()
        
        if (item == None) :
            return (0,0)
        
        #print "Get item %s"%(str(item)) 
        get_data._website_id =  item[0]
        get_data._country_id  = item[1]
        get_data._country_city_url = item[2]
        get_data._spider_priority =  item[3] 
        return (0,1)
    
    
    def set_website_country_url(self,set_data):
        '''设置国家配置信息 '''
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句,使用REPLACE INTO的语句进行处理
        sql_string = "REPLACE INTO web_rawdata.website_country_url (website_id,country_id,country_city_url,spider_priority) " \
            "VALUES (%d,%d,'%s',%d)" \
            % (set_data._website_id,\
            set_data._country_id,\
            self._db_handle.escape_string(set_data._country_city_url),\
            set_data._spider_priority)
        try:
            #print sql_string
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        
        return 0
    
    
    def list_website_country_url(self,\
                                 get_list,
                                 website_id=0,\
                                 country_id=0,\
                                 spider_priority=0, \
                                 start_no=0, \
                                 num_query=0):
        '''取得站点对国家信息描述的LIST，多条记录  '''

        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "SELECT website_id,country_id,country_city_url,spider_priority " \
            "FROM web_rawdata.website_country_url "
        
        #SQL语句添加WHERE添加    
        where_string = "WHERE "
        if (website_id !=0 ):
            where_string = where_string + "(website_id=%d ) "% website_id
            if (country_id != 0) :
                where_string = where_string + "AND (country_id=%d) "% country_id
            if (spider_priority > 0) :
                where_string = where_string + "AND (spider_priority >=%d) "% spider_priority
        if (where_string != "WHERE "):
            sql_string = sql_string + where_string
        
        #            
        limit_string = "LIMIT %d,%d "%(start_no,num_query)    
        if (num_query > 0):
            sql_string = sql_string + limit_string
        
        #print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
            
        item_list = self._db_cursor.fetchall()
        get_count = len(item_list)
        if (get_count == 0) :
            return 0
        
        for item in item_list :
            get_data = ZQ_Website_City_Url()
            get_data._website_id =  item[0]
            get_data._country_id  = item[1]
            get_data._country_city_url = item[2]
            get_data._spider_priority =  item[3] 
            get_list.append(get_data)
        #print "Get item %s"%(str(item))
         
        return 0
    
    #-------------------------------------------------------------------------------------------
    #CREATE TABLE IF NOT EXISTS web_rawdata.city_define (
    #city_id                 INT UNSIGNED NOT NULL AUTO_INCREMENT,  
    #city_cn_name            VARCHAR(256) NOT NULL,                                             -- 城市的中文名称
    #city_en_name            VARCHAR(256) NOT NULL,                                             -- 城市的英文文名称
    #last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
    #PRIMARY KEY (city_id),
    #UNIQUE INDEX(city_cn_name),
    #INDEX(city_en_name)
    #)ENGINE=MyISAM DEFAULT CHARSET=utf8;
    
    def get_city_define(self,  get_data):
        '''取得城市配置信息  '''
        
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "" 
        if (get_data._country_id != 0) :
            sql_string = "SELECT city_id,country_id,city_cn_name,city_en_name " \
            "FROM web_rawdata.city_define WHERE (city_id=%d)" % get_data._city_id
        elif (cmp(get_data._country_cn_name , "") != 0) :
            sql_string = "SELECT city_id,country_id,city_cn_name,city_en_name " \
            "FROM web_rawdata.city_define "\
            "WHERE ((UPPER(city_cn_name)=UPPER('%s')) (OR UPPER(city_en_name=UPPER(%s)))" \
            % (self._db_handle.escape_string(get_data.city_cn_name_),\
            self._db_handle.escape_string(get_data.city_cn_name_))
            
        else:
            return (-1,0)
        
        #print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return (-1,0)    
        item = self._db_cursor.fetchone()
        
        if (item == None) :
            return (0,0)
        
        #print "Get item %s"%(str(item))
        get_data._city_id =  item[0]
        get_data._country_id = item[1]
        get_data.city_cn_name_ = item[2]
        get_data.city_en_name_ = item[3] 
        
        return (0,1)
    
    def set_city_define(self, set_data):
        '''设置网站获取的城市配置信息 '''
        
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句,使用REPLACE INTO的语句进行处理
        sql_string = "REPLACE INTO web_rawdata.city_define " \
            "(city_id,country_id,city_cn_name,city_en_name) " \
            "VALUES (%d,%d,'%s','%s')" % \
            (set_data._city_id,\
             set_data._country_id,\
             self._db_handle.escape_string(set_data.city_cn_name_),\
             self._db_handle.escape_string(set_data.city_en_name_))
        try:
            #print sql_string
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        
        #如果有插入ID，保存下来
        if (self._db_handle.affected_rows() > 0 and set_data._city_id == 0) :
            set_data._city_id = self._db_handle.insert_id()
            
        return 0
    

    #CREATE TABLE IF NOT EXISTS web_rawdata.website_city_url (
    #    website_id              INT UNSIGNED NOT NULL,   
    #    city_id                 INT UNSIGNED NOT NULL,
    #    country_id              INT UNSIGNED NOT NULL,
    #    city_info_url           VARCHAR(1024) NOT NULL,                                            -- 这个城市信息的表示
    #    city_hotel_url          VARCHAR(1024) NOT NULL,                                            -- 这个城市内部的酒店的URL，
    #    all_hotel_url           VARCHAR(1024) NOT NULL,                                            -- 如果这个城市酒店很多，会有一个ALLURL,
    #    spider_priority         INT UNSIGNED NOT NULL DEFAULT 0,                                   -- 爬虫的优先级
    #    last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
    #PRIMARY KEY (website_id,city_id)
    #)ENGINE=MyISAM DEFAULT CHARSET=utf8;
    def get_website_city_url(self, get_data):
        '''取得城市配置信息  '''

        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "" 
        if ((get_data._website_id != 0) and (get_data._city_id != 0)) :
            sql_string = "SELECT website_id,city_id,country_id,city_info_url,"\
            "city_hotel_url,all_hotel_url,spider_priority " \
            "FROM web_rawdata.website_city_url WHERE ((website_id=%d) AND (city_id=%d))" \
            % (get_data._website_id,get_data._city_id)
        else:
            return (-1,0)
        
        #print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return (-1,0)    
        item = self._db_cursor.fetchone()
        
        if (item == None) :
            return (0,0)
        
        #print "Get item %s"%(str(item))
        get_data._website_id =  item[0]
        get_data._city_id  =  item[1]
        get_data._country_id = item[2]
        get_data._city_info_url = item[3]
        get_data.city_hotel_url_ = item[4]
        get_data.all_hotel_url_ = item[5] 
        get_data._spider_priority = item[6]
        
        return (0,1)
    
    def set_website_city_url(self,  set_data):
        '''设置网站获取的城市配置信息 '''
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句,使用REPLACE INTO的语句进行处理
        sql_string = "REPLACE INTO web_rawdata.website_city_url (website_id,city_id," \
            "country_id,city_info_url,city_hotel_url,all_hotel_url,spider_priority) " \
            "VALUES (%d,%d,%d,'%s','%s','%s',%d)" % \
            (set_data._website_id, \
            set_data._city_id,\
            set_data._country_id,\
            self._db_handle.escape_string(set_data._city_info_url),\
            self._db_handle.escape_string(set_data.city_hotel_url_),\
            self._db_handle.escape_string(set_data.all_hotel_url_),\
            set_data._spider_priority)
        try:
            #print sql_string
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        return 0
    
    def list_website_city_url(self,\
                              get_list,
                              website_id=0,\
                              country_id=0,\
                              city_id=0,\
                              spider_priority=0, \
                              start_no=0, \
                              num_query=0):
        '''取得站点对某(N)个城市信息描述的LIST，多条记录  '''

        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "SELECT website_id,city_id,country_id,city_info_url,"\
            "city_hotel_url,all_hotel_url,spider_priority FROM web_rawdata.website_city_url " 
        
        #SQL语句添加WHERE添加    
        where_string = "WHERE "
        if (website_id !=0 ):
            where_string = where_string + "(website_id=%d) "% website_id
            if (country_id != 0) :
                where_string = where_string + "AND (country_id=%d) "% country_id
            if (city_id != 0) :
                where_string = where_string + "AND (city_id=%d) "% city_id    
            if (spider_priority > 0) :
                where_string = where_string + "AND (spider_priority >=%d) "% spider_priority
        if (where_string != "WHERE "):
            sql_string = sql_string + where_string
        
        #            
        limit_string = "LIMIT %d,%d "%(start_no,num_query)    
        if (num_query > 0):
            sql_string = sql_string + limit_string
        
        #print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
            
        item_list = self._db_cursor.fetchall()
        get_count = len(item_list)
        if (get_count == 0) :
            return 0
        
        for item in item_list :
            get_data = ZQ_Website_City_Url()
            get_data._website_id =  item[0]
            get_data._city_id  =  item[1]
            get_data._country_id = item[2]
            get_data._city_info_url = item[3]
            get_data.city_hotel_url_ = item[4]
            get_data.all_hotel_url_ = item[5] 
            get_data._spider_priority = item[6]
            get_list.append(get_data)
        #print "Get item %s"%(str(get_list))
         
        return 0
    
    #-------------------------------------------------------------------------------------------
    #CREATE TABLE IF NOT EXISTS web_rawdata.hotel_define (
    #hotel_id                INT UNSIGNED NOT NULL AUTO_INCREMENT,                              -- 我们自己对于酒店的定义ID，这儿有一个剔重的问题要解决^|^
    #country_id              INT UNSIGNED NOT NULL,
    #city_id                 INT UNSIGNED NOT NULL,
    #hotel_cn_name           VARCHAR(256) NOT NULL,                                             -- Hotel的中文名称
    #hotel_en_name           VARCHAR(256) NOT NULL,                                             -- Hotel的英文名称
    #last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
    #PRIMARY KEY (hotel_id),
    #UNIQUE INDEX(hotel_cn_name),
    #INDEX(hotel_en_name)
    #)ENGINE=MyISAM DEFAULT CHARSET=utf8;
    
    def get_hotel_define(self,get_data):
        '''取得城市配置信息  '''
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "" 
        if (get_data._hotel_id != 0) :
            sql_string = "SELECT hotel_id,country_id,city_id,hotel_cn_name,hotel_en_name " \
            "FROM web_rawdata.hotel_define WHERE (hotel_id=%d)" % get_data._hotel_id
        elif (cmp(get_data._hotel_en_name , "") != 0) :
            sql_string = "SELECT hotel_id,country_id,city_id,hotel_cn_name,hotel_en_name " \
            "FROM web_rawdata.hotel_define "\
            "WHERE (UPPER(hotel_cn_name)=UPPER('%s') OR UPPER(hotel_en_name)=UPPER('%s'))" \
            % (self._db_handle.escape_string(get_data._hotel_en_name),\
            self._db_handle.escape_string(get_data._hotel_en_name))
        else:
            return (-1,0)
        
        #print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return (-1,0)    
        item = self._db_cursor.fetchone()
        
        if (item == None) :
            return (0,0)
        
        #print "Get item %s"%(str(item))
         
        get_count = 1
        get_data._hotel_id =  item[0]
        get_data._country_id =  item[1]
        get_data._city_id =   item[2]
        get_data._hotel_cn_name = item[3]
        get_data._hotel_en_name = item[4] 
        
        return (0,1)
    
    def set_hotel_define(self, set_data):
        '''设置网站获取的城市配置信息 '''
        #ping 保证数据链接
        self._db_handle.ping()
       
        #根据参数的各种情况得到SQL语句,使用REPLACE INTO的语句进行处理
        sql_string = "REPLACE INTO web_rawdata.hotel_define (hotel_id,country_id,city_id,hotel_cn_name,hotel_en_name) " \
            "VALUES (%d,%d,%d,'%s','%s')" % \
            (set_data._hotel_id,\
             set_data._country_id,\
             set_data._city_id,\
             self._db_handle.escape_string(set_data._hotel_cn_name),\
             self._db_handle.escape_string(set_data._hotel_en_name))
        try:
            #print sql_string
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        #如果有插入ID，保存下来
        if (self._db_handle.affected_rows() > 0 and set_data._hotel_id == 0) :
            set_data._hotel_id = self._db_handle.insert_id()
        return 0
    
    #CREATE TABLE IF NOT EXISTS web_rawdata.website_hotel_url (
    #    website_id              INT UNSIGNED NOT NULL,                                             -- 
    #    hotel_id                INT UNSIGNED NOT NULL,                                             -- 酒店的ID，取之定义表
    #    country_id              INT UNSIGNED NOT NULL,
    #    city_id                 INT UNSIGNED NOT NULL,
    #    hotel_desc_url          VARCHAR(1024) NOT NULL,                                            -- HOTEL抓取的URL
    #    spider_priority         INT UNSIGNED NOT NULL DEFAULT 0,                                   -- 爬虫的优先级
    #PRIMARY KEY (website_id,hotel_id)
    #)ENGINE=MyISAM DEFAULT CHARSET=utf8;
    def get_website_hotel_url(self, get_data):
        '''取得城市配置信息  '''

        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "" 
        if ((get_data._website_id != 0) and (get_data._city_id != 0)) :
            sql_string = "SELECT website_id,hotel_id,country_id,city_id,hotel_desc_url,spider_priority " \
            "FROM web_rawdata.website_hotel_url WHERE ((website_id=%d) AND (hotel_id=%d))" \
            % (get_data._website_id,get_data._hotel_id)
        else:
            return (-1,0)
        
        #print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return (-1,0)    
        item = self._db_cursor.fetchone()
        
        if (item == None) :
            return (0,0)
        
        #print "Get item %s"%(str(item))
        get_count = 1
        get_data._website_id =  item[0]
        get_data._hotel_id  = item[1]
        get_data._country_id  = item[2]
        get_data._city_id  = item[3]
        get_data._hotel_desc_url == item[4]
        get_data._spider_priority = item[5]
        return (0,1)
    
    def set_website_hotel_url(self, set_data):
        '''设置网站获取的城市配置信息 '''
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句,使用REPLACE INTO的语句进行处理
        sql_string = "REPLACE INTO web_rawdata.website_hotel_url ("\
            "website_id,hotel_id,country_id,city_id,hotel_desc_url,spider_priority )" \
            "VALUES (%d,%d,%d,%d,'%s',%d)" % \
            (set_data._website_id, \
            set_data._hotel_id,\
            set_data._country_id,\
            set_data._city_id,\
            self._db_handle.escape_string(set_data._hotel_desc_url), \
            set_data._spider_priority)
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        
        return 0
    
    def list_website_hotel_url(self,\
                               get_list,\
                               website_id,\
                               country_id=0,\
                               city_id=0,\
                               hotel_id=0,\
                               spider_priority=0, \
                               start_no=0, \
                               num_query=0):
        '''取得站点对某(N)个城市信息描述的LIST，多条记录  '''

        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "SELECT website_id,hotel_id,country_id,city_id,hotel_desc_url,spider_priority "\
            "FROM web_rawdata.website_hotel_url " 
        
        #SQL语句添加WHERE添加    
        where_string = "WHERE "
        if (website_id !=0 ):
            if (hotel_id != 0):
                where_string = where_string + "(hotel_id=%d) "% hotel_id
            else:
                if (country_id != 0) :
                    where_string = where_string + "AND (country_id=%d) "% country_id
                if (city_id != 0) :
                    where_string = where_string + "AND (city_id=%d ) "% city_id
                if (spider_priority > 0) :
                    where_string = where_string + "AND (spider_priority >=%d ) "% spider_priority
        if (where_string != "WHERE "):
            sql_string = sql_string + where_string
        
        #            
        limit_string = "LIMIT %d,%d "%(start_no,num_query)    
        if (num_query > 0):
            sql_string = sql_string + limit_string
        
        #print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
            
        item_list = self._db_cursor.fetchall()
        get_count = len(item_list)
        if (get_count == 0) :
            return 0
        
        for item in item_list :
            get_data = ZQ_Website_Hotel_Url()
            get_data._website_id =  item[0]
            get_data._hotel_id  = item[1]
            get_data._country_id  = item[2]
            get_data._city_id  = item[3]
            get_data._hotel_desc_url = item[4]
            get_data._spider_priority = item[5]
            get_list.append(get_data)
        #print "Get item %s"%(str(get_list))
         
        return 0
    
    
    #CREATE TABLE IF NOT EXISTS web_rawdata.website_hotel_desc (
    #website_id              INT UNSIGNED NOT NULL,                                             -- 
    #hotel_id                INT UNSIGNED NOT NULL,                                             -- 酒店的ID，取之定义表
    #data_md5                VARCHAR(64) NOT NULL,                                              -- 抓取数据的MD5，用于避免重复抓取
    #desc_language           INT UNSIGNED NOT NULL,                                             -- 描述的语言，1中文，2英文，如果是E文还要翻译，
    #hotel_star              VARCHAR(16) NOT NULL,                                              -- 酒店星级
    #average                 VARCHAR(16) NOT NULL,                                              -- 总分
    #hotel_desc              BLOB(20480) NOT NULL,                                              -- 酒店描述信息，字段不全面，后面补充
    #room_services           VARCHAR(1024) NOT NULL,                                            -- 房间服务信息
    #hotel_services          VARCHAR(1024) NOT NULL,                                            -- 酒店服务信息
    #entertainment           VARCHAR(1024) NOT NULL,                                            -- 娱乐设施
    #net_facility            VARCHAR(1024) NOT NULL,                                            -- 网络设施
    #hotel_park              VARCHAR(1024) NOT NULL,                                            -- 停车场
    #credit_card             VARCHAR(1024) NOT NULL,                                            -- 行用卡 
    #hotel_policy            VARCHAR(5120) NOT NULL,                                            -- 酒店政策
    #last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,                          --  
    #PRIMARY KEY (website_id,hotel_id)
    #)ENGINE=MyISAM DEFAULT CHARSET=utf8;
    def get_website_hotel_desc(self, get_data):
        '''取得城市配置信息  '''
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "" 
        if ((get_data._website_id != 0) and (get_data._city_id != 0)) :
            sql_string = "SELECT website_id,hotel_id,data_md5,desc_language,hotel_star,"
            "average,hotel_desc,room_services,room_number,hotel_services,entertainment,"\
            "net_facility,hotel_park,credit_card,hotel_policy "\
            "FROM web_rawdata.website_hotel_desc WHERE ((website_id=%d) AND (hotel_id=%d))" \
            % (get_data._website_id,get_data._hotel_id)
            
            
        else:
            return (-1,0)
        
        #print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return (-1,0)    
        item = self._db_cursor.fetchone()
        
        if (item == None) :
            return (0,0)
        
        #print "Get item %s"%(str(item))
        get_count = 1
        get_data._website_id =  item[0]
        get_data._hotel_id  = item[1]
        get_data.data_md5 = item[2]
        get_data.desc_language_ = item[3]
        get_data.average_ = item[4]
        get_data.hotel_star_  = item[5]
        get_data.hotel_desc_ = item[6]
        get_data.room_number_ = item[7]
        get_data.room_services_ = item[7]
        get_data.hotel_services_ = item[8]
        get_data.entertainment_ = item[9]
        get_data.net_facility_ = item[10]
        get_data.hotel_park_ = item[11]
        get_data.credit_card_ = item[12]
        get_data.hotel_policy_ = item[13]
        
        return (0,1)
    
    def set_website_hotel_desc(self, set_data):
        '''设置网站获取的城市配置信息 '''
        
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句,使用REPLACE INTO的语句进行处理
        sql_string = "REPLACE INTO web_rawdata.website_hotel_desc ("\
            "website_id,hotel_id,data_md5,desc_language,hotel_star,"\
            "average,hotel_desc,room_number,room_services,hotel_services,entertainment,net_facility,"\
            "hotel_park,credit_card,hotel_policy )"\
            "VALUES (%d,%d,'%s',%d,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s' )" % \
            (\
            set_data._website_id, \
            set_data._hotel_id,\
            set_data.data_md5_, \
            set_data.desc_language_,\
            self._db_handle.escape_string(set_data.hotel_star_),\
            self._db_handle.escape_string(set_data.average_),\
            self._db_handle.escape_string(set_data.hotel_desc_),\
            self._db_handle.escape_string(set_data.room_number_),
            self._db_handle.escape_string(set_data.room_services_),\
            self._db_handle.escape_string(set_data.hotel_services_),\
            self._db_handle.escape_string(set_data.entertainment_),\
            self._db_handle.escape_string(set_data.net_facility_),\
            self._db_handle.escape_string(set_data.hotel_park_),\
            self._db_handle.escape_string(set_data.credit_card_),\
            self._db_handle.escape_string(set_data.hotel_policy_) )
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        
        return 0
    

    
    #CREATE TABLE IF NOT EXISTS web_rawdata.website_hotel_picture (
    #picture_id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    #website_id              INT UNSIGNED NOT NULL,
    #hotel_id                INT UNSIGNED NOT NULL,                                             -- 酒店的ID，取之定义表
    #_picture_url_md5         VARCHAR(32) NOT NULL,                                              -- 为了避免重复，而且索引不可能太长，用URL MD5作为KEY
    #picture_url             VARCHAR(1024) NOT NULL,                                            -- 图片URL
    #last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
    #PRIMARY KEY (picture_id),
    #UNIQUE INDEX(website_id,hotel_id,_picture_url_md5)
    #)ENGINE=MyISAM DEFAULT CHARSET=utf8;
    def get_website_hotel_picture(self, get_data):
        '''
                    取得HOTEL图片信息  
        '''
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "" 
        if (get_data._website_id != 0 and get_data._hotel_id != 0 and get_data._picture_url_md5_ !="")  :
            sql_string = "SELECT website_id,hotel_id,_picture_url_md5,picture_url " \
            "FROM web_rawdata.website_hotel_picture WHERE " \
            " ((website_id=%d) AND (hotel_id='%d') AND (_picture_url_md5='%s') )" \
            % (get_data._website_id,get_data._hotel_id,get_data._picture_url_md5_)
        else:
            return (-1,0)
        
        print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        item = self._db_cursor.fetchone()
        
        if (item == None) :
            return (0,0)
        
        #print "Get item %s"%(str(item))
        get_data._website_id = item[1]
        get_data._hotel_id = item[2] 
        get_data._picture_url_md5 = item[3]
        get_data._picture_url  = item[4]
        get_data.bigpic_url_  = item[5]
        return (0,0)
    
    def set_website_hotel_picture(self, set_data):
        '''设置网站获取的城市配置信息 '''
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句,使用REPLACE INTO的语句进行处理
        sql_string = "REPLACE INTO web_rawdata.website_hotel_picture " \
            " (website_id,hotel_id,picture_url_md5,picture_url) " \
            "VALUES (%d,%d,'%s','%s')" % \
            (set_data._website_id,\
            set_data._hotel_id,\
            set_data._picture_url_md5, \
            set_data._picture_url )
        try:
            
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        
        return 0
    
    #CREATE TABLE IF NOT EXISTS web_rawdata.website_hotel_room (
    #room_id                 INT UNSIGNED NOT NULL AUTO_INCREMENT,                              -- 房间的ID
    #website_id              INT UNSIGNED NOT NULL,
    #hotel_id                INT UNSIGNED NOT NULL,
    #room_name               VARCHAR(256) NOT NULL, 
    #room_desc               BLOB(10240) NOT NULL,
    #last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,                          --  
    #PRIMARY KEY (room_id),
    #UNIQUE INDEX(website_id,hotel_id,room_name)
    #)ENGINE=MyISAM DEFAULT CHARSET=utf8;
    
    def get_website_hotel_room(self, get_count, get_data):
        '''取得酒店的房间  '''
        get_count = 0
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "" 
        if (get_data.room_id_ != 0)  :
            sql_string = "SELECT room_id,website_id,hotel_id,room_name,room_desc " \
            "FROM web_rawdata.website_hotel_room WHERE (room_id=%d) " \
            % (get_data.room_id_ )
        elif ((get_data._website_id != 0) and (get_data._hotel_id != 0) and (get_data.room_name_ != "" ) ):
            sql_string = "SELECT room_id,website_id,hotel_id,room_name,room_desc " \
            "FROM web_rawdata.website_hotel_room WHERE ((website_id=%d) AND (hotel_id=%d) AND (room_name='%s') )" \
            % (get_data._website_id,get_data._hotel_id,get_data.room_name_)
        else:
            return -1
        
        print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        item = self._db_cursor.fetchone()
        
        if (item == None) :
            return 0
        
        #print "Get item %s"%(str(item))
        get_count = 1
        get_data.room_id_ =  item[0]
        get_data._website_id  = item[1]
        get_data._hotel_id  = item[2] 
        get_data.room_name_ = item[3]
        get_data.room_desc_ = item[4]
        
        return 0
    
    def set_website_hotel_room(self, set_count, set_data):
        '''设置网站获取的城市配置信息 '''
        set_count = 0
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句,使用REPLACE INTO的语句进行处理
        sql_string = "REPLACE INTO web_rawdata.website_hotel_room (room_id,website_id,hotel_id,room_name,room_desc) " \
            "VALUES (%d,%d,%d,'%s','%s')" % \
            (set_data.room_id_, \
            set_data._website_id,\
            set_data._hotel_id,\
            set_data.room_name_, \
            set_data.room_desc_
            )
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        
        set_count = self._db_handle.affected_rows()
        return 0
    
    #CREATE TABLE IF NOT EXISTS web_rawdata.website_room_price (
    #room_id                 INT UNSIGNED NOT NULL,
    #provision               VARCHAR(128) NOT NULL,                                             -- 政策
    #hotel_id                INT UNSIGNED NOT NULL,
    #currency                VARCHAR(32) NOT NULL,                                              -- 币种(这个有点难办)    
    #room_price              VARCHAR(32) NOT NULL,                                              -- 房间价格
    #last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
    #PRIMARY KEY (room_id,provision)
    #)ENGINE=MyISAM DEFAULT CHARSET=utf8;
    def get_website_hotel_price(self, get_count, get_data):
        '''取得城市配置信息  '''
        get_count = 0
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句
        sql_string = "" 
        if (get_data.room_id_ != 0 and get_data.provision_ !="")  :
            sql_string = "SELECT room_id,provision,hotel_id,currency,room_price " \
            "FROM web_rawdata.website_room_price WHERE ((room_id=%d) AND (provision='%s'))" \
            % (get_data.room_id_,get_data.provision_)
        else:
            return -1
        
        print sql_string
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        item = self._db_cursor.fetchone()
        
        if (item == None) :
            return 0
        
        #print "Get item %s"%(str(item))
        get_count = 1
        get_data.room_id_ =  item[0]
        get_data.provision_  = item[1]
        get_data._hotel_id  = item[2] 
        get_data.currency_ = item[3]
        get_data.room_price_ = item[4]
        
        return 0
    
    def set_website_hotel_price(self, set_count, set_data):
        '''设置网站获取的城市配置信息 '''
        set_count = 0
        #ping 保证数据链接
        self._db_handle.ping()
        
        #根据参数的各种情况得到SQL语句,使用REPLACE INTO的语句进行处理
        sql_string = "REPLACE INTO web_rawdata.website_room_price " \
            " (room_id,provision,hotel_id,currency,room_price) " \
            "VALUES (%d,'%s',%d,'%s','%s')" % \
            (set_data.room_id_, \
            set_data.provision_,\
            set_data._hotel_id,\
            set_data.currency_, \
            set_data.room_price_
            )
        try:
            self._db_cursor.execute(sql_string)
        except MySQLdb.Error, e:
            self._logger.error("Execute sql fail.error %d: %s execute sql[%s]" % (e.args[0], e.args[1] ,sql_string ))
            return -1
        
        set_count = self._db_handle.affected_rows()
        return 0
    
        
    #-------------------------------------------------------------------------------------------
    @staticmethod
    def instance():
        ''' 返回单子实例 '''
        if (Spider_MySQL_DBProcess.instance_  == None ):
            Spider_MySQL_DBProcess.instance_ = Spider_MySQL_DBProcess()
        return Spider_MySQL_DBProcess.instance_
    
        
    #-------------------------------------------------------------------------------------------
    @staticmethod
    def test_fun():
        db_process = Spider_MySQL_DBProcess()
        ret = db_process.connect_to_db()
        if ret != 0 :
            return
        set_country_def = ZQ_Country_Define()
        set_country_def._country_id = 1
        set_country_def._country_cn_name = u"中国"
        set_country_def._country_en_name = u"China"
        
        
        db_process.set_country_define(set_country_def)
        
        get_country_def = ZQ_Country_Define()
        get_country_def._country_id = 1
                
        ret = db_process.get_country_define(get_country_def)
    
            
        
        
if __name__ == "__main__":
    Spider_MySQL_DBProcess.test_fun()
	
	
	
	
		 