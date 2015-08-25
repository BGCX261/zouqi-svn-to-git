#coding=utf-8

# http://www.booking.com/ 处理booking网站数据


import urllib2
import re
import md5
from bs4 import BeautifulSoup

from spider_mysqldb import Spider_MySQL_DBProcess
from spider_data_base import *
from spider_website_base import Spider_Website_Base



class Spider_Website_Booking(Spider_Website_Base):
    ''' 用于爬Booking网站的数据的东东  ''' 
    
    def __init__(self,mysql_process,filesave_dir):
        Spider_Website_Base.__init__(self,80001,"http://www.booking.com",mysql_process,filesave_dir)
        
        
    def crawlweb_countryurl(self,website_desc,saveto_db=False):
        
        ret = 0
        # 读取国家信息到数据库
        #'http://www.booking.com/destination.zh-cn.html'
        rsp_content = self.openner_crawlweb(website_desc._country_url)
        if (rsp_content == None):
            return -1
        
        self.save_to_file(save_data=saversp_content,
                          country_id=0,\
                          city_id=0,\
                          hotel_id=0,\
                          page_id=0)
        
        # 对于HTML文件进行翻译
        soup = BeautifulSoup(rsp_content)
        # 这个段落没有用class进行区分，
        raw_country_list = soup.find_all(name="div", class_="flatList")
        # 再分析一次，去掉div等信息，吼吼
        soup = BeautifulSoup(str(raw_country_list))
        country_list = soup.find_all(name="a")
        for country_item in country_list :
            country_def = ZQ_Country_Define()
            country_url = ZQ_Website_Country_Url()
            # print country_item
            tag = BeautifulSoup(str(country_item))
            # 这个判定有点太简单了。
            country_def._country_cn_name = tag.string.strip()
            country_url._website_id = self._website_id
            #内部链接要家域名
            country_url._country_city_url = self._website_domain + tag.a['href']
            
            ret,data_count = self._mysql_process.get_country_define(country_def)
            if (ret != 0):
                return ret 
            
            #谁说Python的缩进好看，我和他急
            if (data_count == 0) :
                if (saveto_db == True):
                    ret = self._mysql_process.set_country_define(country_def)
                    if (ret != 0):
                        self._logger.info("Save this country define %s to database fail." % country_def._country_cn_name)
                        return ret    
                else :
                    self._logger.info("No found this country %s in define table. continue process next" % country_def._country_cn_name)
                    continue
            #得到配置的国际ID,然后保存抓取的数据
            country_url._country_id = country_def._country_id
            ret = self._mysql_process.set_website_country_url(country_url)
            if (ret != 0 ):
                self._logger.info("Save this country [%d|%s] to database fail." \
                % (country_def._country_id,country_def._country_cn_name))
                return ret
            else :
                self._logger.info("Save this country desc [%d|%s] to database success." \
                % (country_def._country_id,country_def._country_cn_name))
               
        return 0
    

    
    def crawlweb_cityurl(self, country_url,saveto_db=False):
        ''' '''
        # 读取国家信息到数据库
        rsp_content = self.openner_crawlweb(country_url._country_city_url)
        if (rsp_content == None):
            return -1
        
        self.save_to_file(save_data=rsp_content,
                          country_id=country_url._country_id,\
                          city_id=0,\
                          hotel_id=0,\
                          page_id=0)
        
        # 对于HTML文件进行分析处理，
        soup = BeautifulSoup(rsp_content)
        raw_web_data = soup.find_all(name="div", class_="description deslast")
        
        soup = BeautifulSoup(str(raw_web_data))
        raw_web_data = soup.find_all(name="table", class_="general")
        
        soup = BeautifulSoup(str(raw_web_data))
        city_list = soup.find_all(name="a")
        for city_item in city_list :
            city_def = ZQ_City_Define()
            city_url = ZQ_Website_City_Url()
            # print country_item
            tag = BeautifulSoup(str(city_item))
            # 这个判定有点太简单了。
            city_def.city_cn_name_ = tag.string.strip()
            city_def._country_id = country_url._country_id
            city_url._website_id = self._website_id
            city_url._country_id = country_url._country_id
            #内部链接要家域名
            city_url._city_info_url = self._website_domain + tag.a['href']
            
            ret,data_count = self._mysql_process.get_city_define(city_def)
            if (ret != 0):
                return ret 
            
            #谁说Python的缩进好看，我和他急
            if (data_count == 0) :
                if (saveto_db == True):
                    ret = self._mysql_process.set_city_define(city_def)
                    if (ret != 0):
                        self._logger.info("Save this city define [%s] to database fail." % city_def.city_cn_name_)
                        return ret    
                else :
                    self._logger.info("No found this city define [%s] in define table. continue process next" % city_def.city_cn_name_)
                    continue
            
            #根据city_info的地方得到HOTEL的URL，BOOKING网站比较变态，要跳转2次
            #第一次跳转
            rsp_content = self.openner_crawlweb(city_url._city_info_url)
            if (rsp_content == None):
                self._logger.error("Get city [%s] info url [%s] fail.",city_def.city_cn_name_,city_url._city_info_url)
                continue
            
            soup = BeautifulSoup(rsp_content)
            raw_web_data = soup.find_all(name="p", class_="firstpar")
            
            soup = BeautifulSoup(str(raw_web_data))
            raw_web_data = soup.find_all(name="a")
            tag = BeautifulSoup(str(raw_web_data))
            
            city_url.city_hotel_url_ = self._website_domain + tag.a['href']
            
            #第二次跳转，得到真正所有的的CITY酒店连接
            rsp_content = self.openner_crawlweb(city_url.city_hotel_url_)
            if (rsp_content == None):
                self._logger.error("Get city [%s] hotel url [%s] fail.",city_def.city_cn_name_,city_url._city_info_url)
                continue
            
            soup = BeautifulSoup(rsp_content)
            raw_web_data = soup.find_all(name="p", class_="allhotelsin")
            soup = BeautifulSoup(str(raw_web_data))
            raw_web_data = soup.find_all(name="a" , class_="all_hotels_in_dest")
            tag = BeautifulSoup(str(raw_web_data))
            
            if (tag.a != None) :
                city_url.all_hotel_url_ = self._website_domain + tag.a['href']
                city_url._spider_priority = 100
            
            #得到配置的国际ID,然后保存抓取的数据
            city_url._city_id = city_def._city_id
            ret = self._mysql_process.set_website_city_url(city_url)
            if (ret != 0 ):
                self._logger.info("Save this city desc [%s] to database fail." % city_def.city_cn_name_)
                return ret
            else :
                self._logger.info("Save this city desc [%s] to database success." % city_def.city_cn_name_)
        return 0 
    

    
    def __save_hotel_url(self,city_url,hotel_item,saveto_db=False):
        ''' ''' 
        hotel_def = ZQ_Hotel_Define()
        hotel_url = ZQ_Website_Hotel_Url()
        tag = BeautifulSoup(str(hotel_item))
        
        hotel_name = tag.string.strip()
        hotel_def._hotel_en_name = hotel_name
        
        #如果里面有中文字符串，提取出来 ，示例CHINA(中国)
        bracket_start = hotel_name.find("(")
        if bracket_start != -1 and bracket_start > 0:
            bracket_end = hotel_name.find(")")
            if (bracket_end - bracket_start) > 1:
                hotel_def._hotel_en_name = (hotel_name[0:bracket_start]).strip()
                hotel_def._hotel_cn_name = (hotel_name[bracket_start+1:bracket_end]).strip()
            
        #print "[%s|%s]"%(hotel_def._hotel_en_name,hotel_def._hotel_cn_name)
        hotel_def._website_id = self._website_id
        hotel_def._country_id = city_url._country_id
        hotel_def._city_id = city_url._city_id

        #内部链接要家域名
        hotel_url._website_id = self._website_id
        hotel_url._country_id = city_url._country_id
        hotel_url._city_id = city_url._city_id
        hotel_url._hotel_desc_url = self._website_domain + tag.a['href']
        ret,data_count = self._mysql_process.get_hotel_define(hotel_def)
        if (ret != 0):
            return ret 
    
        #谁说Python的缩进好看，我和他急
        if (data_count == 0) :
            if (saveto_db == True):
                ret = self._mysql_process.set_hotel_define(hotel_def)
                if (ret != 0):
                    self._logger.info("Save this hotel define [%s] to database fail." % hotel_def._hotel_en_name)
                    return ret    
            else :
                self._logger.info("No found this hotel [%s] in define table. continue process next" % hotel_def._hotel_en_name)
                return 0
        #得到配置的ID,然后保存抓取的数据
        hotel_url._hotel_id = hotel_def._hotel_id
        ret = self._mysql_process.set_website_hotel_url(hotel_url)
        if (ret != 0 ):
            self._logger.info("Save this hotel url[%s] to database fail." % hotel_def._hotel_en_name)
            return ret
        else :
            self._logger.info("Save this hotel url [%s] to database success." % hotel_def._hotel_en_name)
        
        return 0 
        
    def crawlweb_hotelurl(self,city_url,saveto_db=False):
        ''' 爬取酒店的URL， '''
        ret = 0
        city_hotel_count = 0
        #对于有多个Hotel的页面进行爬取
        if (city_url.all_hotel_url_ != ""):
            
            #有NEXT页面，所以一次抓取一张
            crawlweb = city_url.all_hotel_url_
            page_count = 0
            while (True):
                
                rsp_content = self.openner_crawlweb(crawlweb)
                if (rsp_content == None):
                    return -1
                
                self.save_to_file(save_data=rsp_content,
                          country_id=city_url._country_id,\
                          city_id=city_url._city_id,\
                          hotel_id=0,\
                          page_id=page_count)
                
                soup = BeautifulSoup(rsp_content)
                
                hotel_list = soup.find_all(name="a",class_="hotel_name_link url ")
                next_web_data = soup.find_all(name="td",class_="next")
                
                for hotel_item in hotel_list :
                    city_hotel_count += 1
                    ret = self.__save_hotel_url(city_url,hotel_item,saveto_db)
                #如果没有下一页，跳出循环，如果有下一页，重新进行爬取得        
                soup = BeautifulSoup(str(next_web_data))
                next_web_data = soup.find_all(name="a")
                
                tag = BeautifulSoup(str(next_web_data))
                if (tag.a == None) :
                    break
                crawlweb = self._website_domain + tag.a['href']
                page_count += 1
        #对于只有少量Hotel信息的页面进行抓取
        elif (city_url.city_hotel_url_ != "") :
            rsp_content = self.openner_crawlweb(city_url.city_hotel_url_)
            if (rsp_content == None):
                return -1
            
            self.save_to_file(save_data=rsp_content,
                          country_id=city_url._country_id,\
                          city_id=city_url._city_id,\
                          hotel_id=0,\
                          page_id=0)
            
            soup = BeautifulSoup(rsp_content)
            table_list = soup.find_all(name="table",class_="promos")
            city_hotel_data = table_list[0]
            soup = BeautifulSoup(str(city_hotel_data))
            hotel_list = soup.find_all(name="a",class_="hotelname")
            for hotel_item in hotel_list :
                city_hotel_count += 1
                ret = self.__save_hotel_url(city_url,hotel_item,saveto_db)
                
        else :
            self._logger.error("This city [%d|%d] has no url ." % (city_url._country_id,city_url._city_id))
            
        self._logger.info("This city [%d|%d] has [%d] url ." % (city_url._country_id,city_url._city_id,city_hotel_count))
        return 0
        
    #---------------------------------------------------------------------------------------------

    

    
    def crawlweb_hoteldesc(self,hotel_url,saveto_db=False):
        '''取得酒店的各种信息，描述，图片，房间等 '''
        
        #TNNNNNND的万里长征终于搞完了第一步 《大龄文艺女青年》     你看 你看 你看她只会做西红柿炒鸡蛋　　你看 你看 还要就着方便面
        
        self._logger.info("This hotel [%d] url [%s]." %\
        (hotel_url._hotel_id,hotel_url._hotel_desc_url))
         
         
        rsp_content = self.openner_crawlweb(hotel_url._hotel_desc_url)
        if (rsp_content == None):
            return -1
        
        self.save_to_file(save_data=rsp_content,
                          country_id=hotel_url._country_id,\
                          city_id=hotel_url._city_id,\
                          hotel_id=hotel_url._hotel_id,\
                          page_id=0)
        soup = BeautifulSoup(rsp_content)
        
        hotel_desc = ZQ_Website_Hotel_Desc()
        hotel_desc._website_id = hotel_url._website_id
        hotel_desc._hotel_id = hotel_url._hotel_id
        hotel_desc.desc_lanuage_ = 1
        
        #find_all(limit=1) 和find功能一致
        item_average = soup.find(name="span",attrs={"class":"average"})
        item_star =  soup.find(name="span",attrs={"class":re.compile("use_sprites")})
        item_desc =  soup.find(name="div",id="summary")
        item_number =  soup.find(name="p",attrs={"class":re.compile("summary")})
        item_facility = soup.find_all(name="p",class_="firstpar")
        item_net = soup.find(name="div",attrs={"id":"internet_policy"})
        item_park = soup.find(name="div",attrs={"id":"parking_policy"})
        item_policies = soup.find(name="div", attrs={"id":"hotelPoliciesInc","class":"descriptionsContainer"})
        item_potho = soup.find(name="div",attrs={"class":"photo_collage base_collage"})
        
        
        #取得得分,#这儿会取得好几个分数，因为页面下面还有其他推荐，我值取第一个，目前看是就是这个酒店。
        if (item_average != None):
            tag = BeautifulSoup(str(item_average))
            hotel_desc.average_ = tag.string.strip()
        else:
            self._logger.error("This hotel page  [%d|%d] don't get average ." % \
                (hotel_url._website_id,hotel_url._hotel_id))
        
        #取得星级,这儿会取得好几个分数，因为页面下面还有其他推荐，我值取第一个，目前看是就是这个酒店。
        if (item_star != None):
            tag = BeautifulSoup(str(item_star))
            hotel_desc.hotel_star_ = tag.span['title']
        else:
            self._logger.error("This hotel page  [%d|%d] don't get star ." % \
                (hotel_url._website_id,hotel_url._hotel_id))    
        
        #读的描述
        if (item_desc != None):
            soup = BeautifulSoup(str(item_desc))
            desc_list = soup.find_all(name="p")
            for desc_item in desc_list :
                tag = BeautifulSoup(str(desc_item))
                if (tag.string != None) :
                    hotel_desc.hotel_desc_ += tag.string.strip()
                    hotel_desc.hotel_desc_ += "\n"
        else:
            self._logger.error("This hotel page  [%d|%d] don't get desc ." % \
                (hotel_url._website_id,hotel_url._hotel_id))
            
        #读的房间数量    
        if (item_number != None):
            soup = BeautifulSoup(str(item_number))
            hotel_desc.room_number_ = soup.text
        else:
            self._logger.error("This hotel page  [%d|%d] don't get room number ." % \
                (hotel_url._website_id,hotel_url._hotel_id))
        #对设施字段进行处理
        if (item_facility != []):
            len_facility = len(item_facility)
            
            if (len_facility >= 2):
                tag = BeautifulSoup(str(item_facility[0]))
                hotel_desc.room_services_ = tag.string
                tag = BeautifulSoup(str(item_facility[1]))
                hotel_desc.hotel_services_ = tag.string
            if (len_facility >= 3):
                tag = BeautifulSoup(str(item_facility[0]))
                hotel_desc.room_services_ = tag.string
                tag = BeautifulSoup(str(item_facility[1]))
                hotel_desc.entertainment_ = tag.string
                tag = BeautifulSoup(str(item_facility[2]))
                hotel_desc.hotel_services_ = tag.string
        else:
            self._logger.error("This hotel page  [%d|%d] don't get facility ." % \
                (hotel_url._website_id,hotel_url._hotel_id))
                #对设施字段进行处理

        #处理网络信息   
        if (item_net != None):
            soup = BeautifulSoup(str(item_net))
            item_net = soup.find(name="p")
            soup = BeautifulSoup(str(item_net))
            hotel_desc.net_facility_ = soup.p.get_text().strip().replace("\n","") 
        else:
            self._logger.error("This hotel page  [%d|%d] don't get internet ." % \
                (hotel_url._website_id,hotel_url._hotel_id))
        
        #处理停车位的信息    
        if (item_park != None):
            
            soup = BeautifulSoup(str(item_park))
            item_net = soup.find(name="p")
            soup = BeautifulSoup(str(item_park))
            hotel_desc.hotel_park_ = soup.p.get_text().strip().replace("\n","") 
        else:
            self._logger.error("This hotel page  [%d|%d] don't get park ." % \
                (hotel_url._website_id,hotel_url._hotel_id))
            
        #爬取酒店政策字段
        if (item_policies != None):
            
            #去掉注释
            soup = BeautifulSoup(re.sub("<!--.+?-->","",str(item_policies)))
            item_list = soup.find_all(name="div",attrs={"class":"description"})
            policies_count = 0
            for item in item_list :
                policies_count += 1
                soup = BeautifulSoup(str(item))
                key_string = soup.find(name="span")
                value_string =   soup.find(name="p")
                if (key_string == None or value_string == None):
                    break
                if (policies_count < 6):
                    hotel_desc.hotel_policy_ += key_string.get_text() + ":"
                    hotel_desc.hotel_policy_ += value_string.get_text().strip().replace("\n","") 
                    hotel_desc.hotel_policy_ += "\n"
                else:
                    hotel_desc.credit_card_  = key_string.get_text() + ":" + value_string.get_text().strip().replace("\n","") 
                
        else:
            self._logger.error("This hotel page  [%d|%d] don't get internet ." % \
                (hotel_url._website_id,hotel_url._hotel_id))
            
        ret = self._mysql_process.set_website_hotel_desc(hotel_desc)
        if (ret != 0 ):
            self._logger.error("Save this hotel desc [%d|%d] to database fail." % \
                              (hotel_url._website_id,hotel_url._hotel_id))
            return ret
        else :
            self._logger.info("Save this hotel desc [%d|%d] to database Success." % \
                              (hotel_url._website_id,hotel_url._hotel_id))
            
        #处理图片信息
        pic_list = []
        if (item_potho != None):
            soup = BeautifulSoup(str(item_potho))
            pic_script = soup.find(name="script")
            
            line_list = str(pic_script).splitlines()
            
            for str_line in line_list :
                pic_url_group = re.search(r"http://.*?\.jpg",str_line)
                if pic_url_group != None:
                    pic_list.append(pic_url_group.group())
                    
        else:
            self._logger.error("This hotel page  [%d|%d] don't get photo  link ." % \
                (hotel_url._website_id,hotel_url._hotel_id))
        
        #将所有的图片信息存放到DB中，以备以后抓取
        md5_fun = md5.new()
        for pic_url in pic_list :
            zq_photo_url = ZQ_Website_Hotel_Picture()
            zq_photo_url._website_id = hotel_url._website_id
            zq_photo_url._hotel_id = hotel_url._hotel_id
            zq_photo_url._picture_url = pic_url
             
            md5_fun.update(pic_url)
            zq_photo_url._picture_url_md5 = md5_fun.hexdigest() 
            ret = self._mysql_process.set_website_hotel_picture(zq_photo_url)
            if ( ret != 0 ):
                self._logger.error("This hotel page  [%d|%d] picture url[%s] save fail ." % \
                                   (hotel_url._website_id,hotel_url._hotel_id,zq_photo_url._picture_url))
        self._logger.info("This hotel page [%d|%d] has number [%d] picture."%\
                          (hotel_url._website_id,hotel_url._hotel_id,len(pic_list)))  
        return 0    

if __name__ == "__main__":
    # print (content)
    test_spider = Spider_Website_Booking()
    test_spider.crawlweb_countryurl()





