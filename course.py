import requests
import re
from time import time, strptime, mktime
# from bs4 import Tag
from login_and_get_sc import Browser
from wprinter import *

__HEADER__ = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
__COURSE_URL_PREFIX__ = "https://ocw.swjtu.edu.cn/yethan/YouthIndex?setAction=courseInfo&courseid="

class AllCourses:
    def __init__(self) -> None:
        self._page = 1
        self._courses = None
        self._pattern = re.compile('<p class="list-tit" onclick="getCourseInfo\(\'(?P<courseid>.*?)\'\)">(?P<name>.*?)</p>.*?<span>(?P<gotten_time>.*?)</span>.*?<span>(?P<type>.*?)</span>.*?<p class="list-txt">(?P<introduction>.*?)</p>.*?<span class="times">(?P<time_to_attend>.*?)</span>.*?<span>已报名</span><span>(?P<n_attend>.*?)</span> <span>/(?P<n_maxattend>.*?)</span>.*?<span class="endTime" v="(?P<endtime>.*?)"></span>',re.S)

    def next(self) -> re.Match:
        match = None
        try:
            match = self._courses.__next__()
        except (AttributeError, StopIteration) :
            self._fill_up_courses()
            match = self._courses.__next__()
        return match

    def _next_page(self) -> str:
        url='https://ocw.swjtu.edu.cn/yethan/YouthIndex?'
        params={'setAction':'courseList','jumpPage':self._page,'key5':'all'}
        self._page += 1
        response=requests.get(url=url,headers=__HEADER__,params=params)
        return response.text
    
    def _fill_up_courses(self) -> None:        
        iterator=self._pattern.finditer(self._next_page())
        self._courses = iterator

class Course:
    def __init__(self, browser = None) -> None:
        self._allCourses = AllCourses()
        if browser:
            self.browser = browser
        else:
            self.browser = Browser()

        self.match = None
        self.info = None
        self._course_detail_cont = None

        self._move_to_next_match()   # move to first course
            
    def _move_to_next_match(self) -> None:
        self.match = self._allCourses.next()

    def _fetch_course_info(self) -> None:
        if not self.info:
            self.info = self.browser.get_course_info_by(self.get_course_url())

    def _fetch_course_detail_cont(self) -> None:
        from bs4 import BeautifulSoup, NavigableString
        html = self.get_course_html()
        soup = BeautifulSoup(html, 'html.parser')

        container = None
        for child in soup.body.find("div", {"class", "max-width"}).contents:
            if child.__class__ is not NavigableString and child["class"][0] == "container":
                container = child
                break
        if not container:
            raise Exception("div.container not exists.")

        details = container.find("div", {"class", "details"}).find("div", {"class", "details-cont"})
        self._course_detail_cont = details

    def get_full_introduction(self) -> str:
        self._fetch_course_detail_cont()
        titles = self._course_detail_cont.select('.details-cont > h2') 
        txts = self._course_detail_cont.find_all("div", {"class", "introduce-txt"})
        for i in range(0, len(titles)):
            if titles[i].string == "课程介绍":
                return txts[i].get_text().strip()
        return "无课程介绍"

    def get_course_process(self) -> str:
        self._fetch_course_detail_cont()
        titles = self._course_detail_cont.select('.details-cont > h2') 
        txts = self._course_detail_cont.find_all("div", {"class", "introduce-txt"})
        for i in range(0, len(titles)):
            if titles[i].string == "活动流程":
                return txts[i].get_text().strip()
        return "无活动流程"
    
    def get_course_description(self) -> str:
        self._fetch_course_detail_cont()
        titles = self._course_detail_cont.select('.details-cont > h2') 
        txts = self._course_detail_cont.find_all("div", {"class", "introduce-txt"})
        for i in range(0, len(titles)):
            if titles[i].string == "课程说明":
                return txts[i].get_text().strip()
        return "无课程说明"
    
    def get_course_html(self) -> str:
        self._fetch_course_info()
        return self.info

    def get_course_url(self) -> str:
        return __COURSE_URL_PREFIX__ + self.get_course_id()

    def get_course_id(self) -> str:
        return self.match.group("courseid")
    
    def get_course_name(self) ->str:
        return self.match.group("name")
    
    def get_course_hour(self) -> str:
        return self.match.group("gotten_time")
    
    def get_course_type(self) -> str:
        return self.match.group("type")
    
    def get_course_brief_intro(self) -> str:
        return self.match.group("introduction")
    
    def get_course_time(self) -> str:
        return self.match.group("time_to_attend")

    def get_number_of_enrollee(self) -> str:
        return self.match.group("n_attend")
    
    def get_max_number_of_enrollee(self) -> str:
        return self.match.group("n_maxattend")

    def get_enrollment_deadline(self) -> str:
        return self.match.group("endtime")    
    
    def get_course_selection_time(self) -> str:
        self._fetch_course_info()
        pattern = re.compile('选课时间：</div>.*?<div class="limit-item" style="flex: none;display: block;border: none;line-height: 38px;">(?P<time_to_choose>.*?)</div>',re.S)
        iterator = pattern.finditer(self.info)
        match = iterator.__next__().group("time_to_choose").strip()
        return match

    def get_course_hours_explanation(self) -> str:
        self._fetch_course_info()
        pattern = re.compile('<h2>学时说明</h2>.*?80px;">(?P<gotten_time_introduction>.*?)</div>',re.S)
        iterator = pattern.finditer(self.info)
        match = iterator.__next__().group("gotten_time_introduction").strip()
        return match
    
    def get_course_location(self) -> str:
        self._fetch_course_info()
        pattern = re.compile('上课地点：</div>.*?line-height: 38px;">(?P<lesson_place>.*?)</div>',re.S)
        iterator = pattern.finditer(self.info)
        match = iterator.__next__().group("lesson_place").strip()
        return match

    def department_restriction(self) -> bool:
        """False:没有限制，都可以报名"""
        self._fetch_course_info()
        pattern = re.compile('<div class="limit-title">学院限制：</div>.*?经管',re.S)
        if pattern.search(self.info):
            return False
        else:
            return True

    def campus_restriction(self) -> bool:
        """return:
        False:没有限制，所有校区都可以报名
        True:有限制，九里校区不能报名"""
        self._fetch_course_info()
        pattern = re.compile('<div class="limit-title">校区限制：</div>.*?九里校区',re.S)
        if pattern.search(self.info):
            return False
        else:
            return True
        
    def registration_is_full(self) -> bool:
        if int(self.get_number_of_enrollee()) >= int(self.get_max_number_of_enrollee()):
            return True
        else:
            return False
        
    def selection_has_ended(self) -> bool:
        selection_time = self.get_course_selection_time()
        lst = selection_time.split(" 至 ")
        begin = strptime(lst[0],'%Y-%m-%d %H:%M')
        end = strptime(lst[1],'%Y-%m-%d %H:%M')
        if( mktime(end)-time()>0 ):
            return False
        else:
            return True
        
    def selection_not_begun(self) -> bool:
        selection_time = self.get_course_selection_time()
        lst = selection_time.split(" 至 ")
        begin = strptime(lst[0],'%Y-%m-%d %H:%M')
        end = strptime(lst[1],'%Y-%m-%d %H:%M')
        if( time() - mktime(begin) ):
            return False
        else:
            return True

    def take_place_in_xipu(self) -> bool:
        location = self.get_course_location()
        if location.startswith("犀浦校区"):
            return True
        else:
            return False
        
    def filter(self) -> bool:
        conditions_not_met = self.campus_restriction() | self.department_restriction() | self.registration_is_full() | self.selection_has_ended()
        return conditions_not_met

    def next(self) -> None:
        self._move_to_next_match()
        self.info = None

    "return number of skipped course."
    def next_with_filter(self) -> int:
        count = 0
        while(True):
            self.next()
            conditions_not_met = self.filter()
            if(conditions_not_met):
                # print("skip:",self.get_course_url())
                count += 1
                if count > 10:
                    raise Exception("can't find one more available course after more than 10 searches")
                continue 
            else:
                break

def main():
    c = Course()
    max = 10
    for i in range(0, max):
        # condition_not_met = c.filter()
        # if condition_not_met:
        #     c.next()
        #     continue
        print(f"{i+1}、", c.get_course_name())
        print('--------------------------------------------------------------课程介绍:')
        print(c.get_full_introduction())
        # print('上课时间:',end="")
        # print(c.get_course_time())
        # print("选课时间：",end="")
        # print(c.get_course_selection_time())
        print("学时说明：",end="")
        print(c.get_course_hours_explanation())
        print("上课地点：",end="")
        print(c.get_course_location())
        # print('报名人数:{0}/{1}'.format(c.get_number_of_enrollee(),c.get_max_number_of_enrollee()))
        # print("Website:", end="")
        # print(c.get_course_url())
        # print("--------------------------------------------------------------活动流程：")
        # print(c.get_course_process())
        # print("--------------------------------------------------------------课程说明：")
        # print(f"++{len(c.get_course_description())}++")
        print()  
        c.next()      

if __name__ == '__main__':
    main()