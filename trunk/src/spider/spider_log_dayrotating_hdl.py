#coding=utf-8

import re
import time
from logging.handlers import BaseRotatingHandler


class DayRotating_FileHandler(BaseRotatingHandler):
    """
           增加一种按天滚动的日志方式，同时符合我自己的日志风格，这个代码是从TimedRotatingFileHandler改动得到
    TimedRotatingFileHandler 不符合我预期的主要问题在于其当前的文件是只用前缀格式保留，
           这样如果你的代码不是一直在运行，你其实无法理解分清日志的当前时间是什么，不符合我对日志的喜好
    """
    def __init__(self, prefix_name, backup_count=0, encoding=None, delay=False, utc=False):
        self.suffix_name_ = "%Y%m%d.log"
        self.prefix_name_= prefix_name
        self.utc_ = utc
        cur_file_name = self._current_log_filename()
        self.backup_count_ = backup_count
        BaseRotatingHandler.__init__(self, cur_file_name, 'a', encoding, delay)
        
        self.interval_ = 60 * 60 * 24 # one day
        self.ext_match_ = re.compile(r"^\d{4}\d{2}\d{2}$")
        
        self.rollover_at_ = self.compute_rollover()
        
    def _current_log_filename(self):
        
        current_time = int(time.time())
        ''' 得到当前的日志名称 '''
        if self.utc_:
            time_tuple = time.gmtime(current_time)
        else:
            time_tuple = time.localtime(current_time)
        return self.prefix_name_ + "." + time.strftime(self.suffix_name_, time_tuple)

    def compute_rollover(self):
        '''
                    计算滚动的时间点，文件在多长时间后进行滚动，更新到下一个文件上面去
        '''
        current_time = int(time.time())
        # This could be done with less code, but I wanted it to be clear
        if self.utc_:
            t = time.gmtime(current_time)
        else:
            t = time.localtime(current_time)
        current_hour = t[3]
        current_minute = t[4]
        current_second = t[5]
        # r is the number of seconds left between now and midnight
        r = 24 * 60 * 60 - ((current_hour * 60 + current_minute) * 60 +
                current_second)
        result = current_time + r

        return result
    
    def _getfiles_to_delete(self):
        """
                    找到前缀的文件删除掉。
        """
        dir_name, base_name = os.path.split(self.prefix_name_)
        select_files = os.listdir(dir_name)
        result = []
        prefix = base_name + "."
        plen = len(prefix)
        for file_name in select_files:
            if file_name[:plen] == prefix:
                suffix = file_name[plen:]
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dir_name, file_name))
        result.sort()
        
        #如果文件个数已经大于备份
        if len(result) < self.backup_count_:
            result = []
        else:
            result = result[:len(result) - self.backup_count_]
        return result

    def shouldRollover(self, record):
        """
                    判定是否要发生日志滚动，这个应该是重载函数，
        """
        t = int(time.time())
        if t >= self.rollover_at_:
            return 1
        #print "No need to rollover: %d, %d" % (t, self.rollover_at_)
        return 0



    def doRollover(self):
        """
                    执行滚动操作，这个应该是重载函数，
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        
        if self.backup_count_ > 0:
            # 找到老的日志文件进行删除
            for s in self._getfiles_to_delete():
                os.remove(s)
        
        # get the time that this sequence started at and make it a TimeTuple
        self.baseFilename = self._current_log_filename()
        self.mode = 'w'
        self.stream = self._open()
        
        
        current_time = int(time.time())
        new_rollover_at = self.compute_rollover()
        #这个其实是原来代码的思路。
        while new_rollover_at <= current_time:
            new_rollover_at = new_rollover_at + self.interval_
        #If DST changes 如果夏令时发送改变，文件的切换也变化一下 
        #好奇一下，米国的程序员是怎样记录日志的，考虑夏令时的？如果要考虑不是很麻烦吗。。。
        if not self.utc_:
            #如果夏令时不一样
            if time.localtime(current_time)[-1] != time.localtime(new_rollover_at)[-1]:
                # DST kicks in before next rollover, so we need to deduct an hour
                if  time.localtime(current_time)[-1] == 0:  
                    new_rollover_at = new_rollover_at - 3600
                # DST bows out before next rollover, so we need to add an hour
                else:           
                    new_rollover_at = new_rollover_at + 3600
        self.rollover_at_ = new_rollover_at

