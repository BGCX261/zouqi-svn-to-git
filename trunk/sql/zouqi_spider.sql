/******************************************************************************************
zouqi的爬虫数据库，
Author:fullsail
在范式和方便之间求平衡，还是考虑用范式了，否则修改异常比较痛苦
******************************************************************************************/

SET FOREIGN_KEY_CHECKS = 0;
DROP DATABASE IF EXISTS web_rawdata;
SET FOREIGN_KEY_CHECKS = 1;

CREATE DATABASE IF NOT EXISTS web_rawdata;


/******************************************************************************************
webside_desc 表,
******************************************************************************************/
CREATE TABLE IF NOT EXISTS web_rawdata.webside_desc (
    website_id              INT UNSIGNED NOT NULL ,  
    web_name                VARCHAR(256) NOT NULL,                                             -- 网站的名称
    web_domain              VARCHAR(256) NOT NULL,                                             -- 网站的URL
	country_url             VARCHAR(1024) NOT NULL,                                            -- COUNTRY的URL
	review_url              VARCHAR(1024) NOT NULL,                                            -- 评论的的URL
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,这狗日的搞这么长为哪班？
PRIMARY KEY (website_id),
UNIQUE INDEX(web_name)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;


/******************************************************************************************
country_define ,website_country_url 表,
country_define        : 用于描述国家的定义，里面的country_id是我们配置的唯一标识
website_country_url  : 
******************************************************************************************/
CREATE TABLE IF NOT EXISTS web_rawdata.country_define (
    country_id              INT UNSIGNED NOT NULL AUTO_INCREMENT,                              -- 国家的ID  
	country_cn_name         VARCHAR(256) NOT NULL,                                             -- 国家的中文名称,一开始抓取的名称可能有E文的，先全部放入这个地方，后面统一用翻译软件都翻译出来
	country_en_name         VARCHAR(256) NOT NULL,                                             -- 国家的英文名称
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
PRIMARY KEY (country_id),
UNIQUE INDEX(country_cn_name),
INDEX(country_en_name)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS web_rawdata.website_country_url (
	website_id              INT UNSIGNED NOT NULL,   
	country_id              INT UNSIGNED NOT NULL,
	country_city_url        VARCHAR(1024) NOT NULL,                                            -- 
	spider_priority         INT UNSIGNED NOT NULL DEFAULT 0,                                   -- 爬虫的优先级
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
PRIMARY KEY (website_id,country_id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;


/******************************************************************************************
city_url 表,website_city_url 表,
******************************************************************************************/
DROP TABLE IF EXISTS web_rawdata.city_define;
CREATE TABLE IF NOT EXISTS web_rawdata.city_define (
    city_id                 INT UNSIGNED NOT NULL AUTO_INCREMENT,
	country_id              INT UNSIGNED NOT NULL,
    city_cn_name            VARCHAR(256) NOT NULL,                                             -- 城市的中文名称
	city_en_name            VARCHAR(256) NOT NULL,                                             -- 城市的英文文名称
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
PRIMARY KEY (city_id),
UNIQUE INDEX(city_cn_name),
INDEX(city_en_name)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS web_rawdata.website_city_url;
CREATE TABLE IF NOT EXISTS web_rawdata.website_city_url (
	website_id              INT UNSIGNED NOT NULL,   
	city_id                 INT UNSIGNED NOT NULL,
	country_id              INT UNSIGNED NOT NULL,
    city_info_url           VARCHAR(1024) NOT NULL,                                            -- 这个城市信息的表示
	city_hotel_url          VARCHAR(1024) NOT NULL,                                            -- 这个城市内部的酒店的URL，
	all_hotel_url           VARCHAR(1024) NOT NULL,                                            -- 如果这个城市酒店很多，会有一个ALLURL,
	spider_priority         INT UNSIGNED NOT NULL DEFAULT 0,                                   -- 爬虫的优先级
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
PRIMARY KEY (website_id,city_id),
INDEX(website_id,country_id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;



/******************************************************************************************
hotel_define 表,酒店名称表格
website_hotel_url  表,
website_hotel_desc 表,爬取得到的网站的酒店信息，用于得到我们的酒店信息
website_hotel_room 表,爬取得到的网站的酒店的房间信息
website_room_price 表,,爬取得到的网站的酒店的房间的价格信息，因为同一个房间不同的政策价格可能不一样
website_hotel_picture 表,酒店的图片信息
******************************************************************************************/
DROP TABLE IF EXISTS web_rawdata.hotel_define;
CREATE TABLE IF NOT EXISTS web_rawdata.hotel_define (
	hotel_id                INT UNSIGNED NOT NULL AUTO_INCREMENT,                              -- 我们自己对于酒店的定义ID，这儿有一个剔重的问题要解决^|^
	country_id              INT UNSIGNED NOT NULL,                                             -- 国家ID，不符合范式，但方便查询 
	city_id                 INT UNSIGNED NOT NULL,                                             -- 城市ID不符合范式，但方便查询
	hotel_cn_name           VARCHAR(256) NOT NULL,                                             -- Hotel的中文名称
    hotel_en_name           VARCHAR(256) NOT NULL,                                             -- Hotel的英文名称,HOTEL的E文名称更加重要
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
PRIMARY KEY (hotel_id),
UNIQUE INDEX(hotel_en_name),
INDEX(hotel_cn_name)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS web_rawdata.website_hotel_url;
CREATE TABLE IF NOT EXISTS web_rawdata.website_hotel_url (
	website_id              INT UNSIGNED NOT NULL,                                             -- 
	hotel_id                INT UNSIGNED NOT NULL,                                             -- 酒店的ID，取之定义表
	country_id              INT UNSIGNED NOT NULL,
	city_id                 INT UNSIGNED NOT NULL,
	hotel_desc_url          VARCHAR(1024) NOT NULL,                                            -- HOTEL抓取的URL
	spider_priority         INT UNSIGNED NOT NULL DEFAULT 0,                                   -- 爬虫的优先级
PRIMARY KEY (website_id,hotel_id),
INDEX(website_id,country_id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

#酒店的描述信息
DROP TABLE IF EXISTS web_rawdata.website_hotel_desc;
CREATE TABLE IF NOT EXISTS web_rawdata.website_hotel_desc (
	website_id              INT UNSIGNED NOT NULL,                                             -- 
	hotel_id                INT UNSIGNED NOT NULL,                                             -- 酒店的ID，取之定义表
	data_md5                VARCHAR(64) NOT NULL,                                              -- 抓取数据的MD5，用于避免重复抓取
	desc_language           INT UNSIGNED NOT NULL,                                             -- 描述的语言，1中文，2英文，如果是E文还要翻译，
	hotel_star              VARCHAR(16) NOT NULL,                                              -- 酒店星级
	average                 VARCHAR(16) NOT NULL,                                              -- 总分
	hotel_desc              BLOB(20480) NOT NULL,                                              -- 酒店描述信息，字段不全面，后面补充
	room_number             VARCHAR(64) NOT NULL,                                              -- 总分
	room_services           VARCHAR(1024) NOT NULL,                                            -- 房间服务信息
	hotel_services          VARCHAR(1024) NOT NULL,                                            -- 酒店服务信息
	entertainment           VARCHAR(1024) NOT NULL,                                            -- 娱乐设施
	net_facility            VARCHAR(1024) NOT NULL,                                            -- 网络设施
	hotel_park              VARCHAR(1024) NOT NULL,                                            -- 停车场
	credit_card             VARCHAR(1024) NOT NULL,                                            -- 行用卡 
	hotel_policy            VARCHAR(5120) NOT NULL,                                            -- 酒店政策
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,                          --  
PRIMARY KEY (website_id,hotel_id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

#酒店图片信息
DROP TABLE IF EXISTS web_rawdata.website_hotel_picture;
CREATE TABLE IF NOT EXISTS web_rawdata.website_hotel_picture (
    website_id              INT UNSIGNED NOT NULL,
	hotel_id                INT UNSIGNED NOT NULL,                                             -- 酒店的ID，取之定义表
	picture_url_md5         VARCHAR(64) NOT NULL,                                              -- 为了避免重复，而且索引不可能太长，用URL MD5作为KEY
	picture_url             VARCHAR(1024) NOT NULL,                                            -- 图片URL
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
PRIMARY KEY (website_id,hotel_id,picture_url_md5)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

#酒店的房价信息，
DROP TABLE IF EXISTS web_rawdata.website_hotel_room;
CREATE TABLE IF NOT EXISTS web_rawdata.website_hotel_room (
	room_id                 INT UNSIGNED NOT NULL AUTO_INCREMENT,                              -- 房间的ID
    website_id              INT UNSIGNED NOT NULL,
	hotel_id                INT UNSIGNED NOT NULL,
	room_name               VARCHAR(256) NOT NULL, 
	room_url                BLOB(10240) NOT NULL,
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,                          --  
PRIMARY KEY (room_id),
UNIQUE INDEX(website_id,hotel_id,room_name)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

# 房间价格
DROP TABLE IF EXISTS web_rawdata.website_room_price;
CREATE TABLE IF NOT EXISTS web_rawdata.website_room_price (
	room_id                 INT UNSIGNED NOT NULL,
	provision               VARCHAR(128) NOT NULL,                                             -- 政策
	hotel_id                INT UNSIGNED NOT NULL,
	currency                VARCHAR(32) NOT NULL,                                              -- 币种(这个有点难办)    
	room_price              VARCHAR(32) NOT NULL,                                              -- 房间价格
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
PRIMARY KEY (room_id,provision)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;



/******************************************************************************************
hotel_review 表,酒店的总体评信息表，是否和hotel_info合并我在看看，从网页上看booking是分开的。
visitor_review 表,游客对于酒店的评价信息，优点和不足也许应该合并成一个字段
******************************************************************************************/
CREATE TABLE IF NOT EXISTS web_rawdata.hotel_review (
	website_id              INT UNSIGNED NOT NULL,   
	hotel_id                INT UNSIGNED NOT NULL,
	total_score             VARCHAR(32) NOT NULL, 
	item_service_level      VARCHAR(32) NOT NULL,
	item_cost_performance   VARCHAR(32) NOT NULL,
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
PRIMARY KEY (website_id,hotel_id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS web_rawdata.visitor_review (
	website_id              INT UNSIGNED NOT NULL,   
	hotel_id                INT UNSIGNED NOT NULL,
	hotel_name              VARCHAR(256) NOT NULL,                                             -- Hotel的名称，不符合范式，但方便查询
	visitor_name            VARCHAR(32) NOT NULL,
	review_time             VARCHAR(32) NOT NULL,
	visitor_comefrom        VARCHAR(32) NOT NULL,                                              -- 游客来自
	visitor_score           VARCHAR(32) NOT NULL,                                              -- 游客评分
	advantages              BLOB(10240) NOT NULL,                                              -- 游客评价的优点
	disadvantages           BLOB(10240) NOT NULL,                                              -- 游客评价的缺点
	last_modify_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,   -- 最后修改的时间戳，系统自动保存,
PRIMARY KEY (website_id,hotel_id,visitor_name,review_time)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

