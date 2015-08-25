#coding=utf-8
'''描述各种结构，一看就是一个C/C++的土鳖掉到了Python的池子里面'''

#-------------------------------------------------------------------------------
# Website
#-------------------------------------------------------------------------------
class ZQ_Website_Desc:
    """ 
    """ 
    def __init__(self):
        self._website_id = 0
        self._website_name = ""
        self._web_domain = ""
        self._country_url = ""

#-------------------------------------------------------------------------------
# Country
#-------------------------------------------------------------------------------
class ZQ_Country_Define:
    """ 
    """ 
    def __init__(self):
        self._country_id = 0
        self._country_cn_name = ""
        self._country_en_name = ""

class ZQ_Website_Country_Url:
    """ """ 
    def __init__(self):
        self._website_id = 0
        self._country_id = 0
        self._country_city_url = ""
        self._spider_priority = 0

#-------------------------------------------------------------------------------
# City
#-------------------------------------------------------------------------------
class ZQ_City_Define:
    """ """ 
    def __init__(self):
        self._city_id = 0
        self._country_id = 0
        self.city_cn_name_ = ""
        self.city_en_name_ = ""
        
class ZQ_Website_City_Url:
    """ """ 
    def __init__(self):
        self._website_id = 0
        self._city_id = 0
        self._country_id = 0
        self._city_info_url = ""
        self.city_hotel_url_ = ""
        self.all_hotel_url_ = ""
        self._spider_priority = 0        
        
#-------------------------------------------------------------------------------
# Hotel
#-------------------------------------------------------------------------------
class ZQ_Hotel_Define:
    """ """ 
    def __init__(self):
        self._hotel_id = 0
        self._country_id = 0
        self._city_id = 0
        self._hotel_cn_name = ""
        self._hotel_en_name = ""
        
class ZQ_Website_Hotel_Url:
    """ """ 
    def __init__(self):
        self._website_id = 0
        self._hotel_id = 0
        self._country_id = 0
        self._city_id = 0
        self._hotel_desc_url = ""
        self._spider_priority = 0

                                          
class ZQ_Website_Hotel_Desc:
    """ ZQ_Website_Hotel_Desc： 酒店的描述信息，字段含义参考见 website_hotel_desc 表 """ 
    def __init__(self):
        self._website_id = 0
        self._hotel_id = 0
        self.data_md5_ = ""
        self.desc_language_ = 1
        self.average_ = ""
        self.hotel_star_ = ""
        self.hotel_desc_ = ""
        self.room_number_ = ""
        self.room_services_ = ""
        self.hotel_services_ = ""
        self.entertainment_ = ""
        self.net_facility_ = ""
        self.hotel_park_ = ""
        self.credit_card_ = ""
        self.hotel_policy_ = ""

class ZQ_Website_Hotel_Picture:
    """ """ 
    def __init__(self):
        self._website_id = 0
        self._hotel_id = 0
        self._picture_url_md5 = ""
        self._picture_url = ""        
        
class ZQ_Website_Room_Info:
    """ """ 
    def __init__(self):
        self.room_id_ = 0
        self._website_id = 0
        self._hotel_id = 0
        self._hotel_id = 0
        self.room_name_ = ""
        self.room_desc_ = ""

class ZQ_Website_Room_Price:
    """ """ 
    def __init__(self):
        self.room_id_ = 0
        self.provision_ = ""
        self._hotel_id = 0
        self.currency_ = ""
        self.room_price = ""


        
#-------------------------------------------------------------------------------
# Review
#-------------------------------------------------------------------------------

