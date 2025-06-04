from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
import ddddocr
from wprinter import *

class Browser:
    max_try = 5
    login_url = "https://ocw.swjtu.edu.cn/yethan/UserAction?setAction=userLogin"
    def __init__(self, mode:str = "") -> None:
        self.ocr = None
        self._count = 0
        self._read_account()
        self._launch_browser(mode)
        self._login()

    def _read_account(self) -> None:
        with open('crawler\\account', 'r') as file:
            self.username = file.readline().strip()
            self.password = file.readline().strip()
    
    def _launch_browser(self, mode:str) -> None:
        options = webdriver.EdgeOptions()
        if mode == "test":
            pass
        else:
            options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
            options.add_argument('--disable-gpu')  # 禁用GPU加速
        options.add_argument('--disable-infobars')
        wp.print("启动自动化edge浏览器...")
        self.driver = webdriver.Edge(options=options)

    def close_browser(self) -> None:
        if hasattr(self, 'driver'):
            self.driver.quit()
        print("关闭自动化浏览器\n")

    def _identify_img(self, img_element:WebElement) -> str:
        img_data = img_element.screenshot_as_png
        if not self.ocr:
            self.ocr = ddddocr.DdddOcr(show_ad=False)
        verification_code = self.ocr.classification(img_data)
        wp.print(f"识别验证码: {verification_code}")
        return verification_code
    
    def _login(self) -> None:
        self.driver.get(self.login_url)

        wait = WebDriverWait(self.driver, 10, 1)
        wp.print("等待登录页面渲染...")
        login_button = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "button")))

        self.driver.find_element(By.ID, "university").click()
        self.driver.find_elements(By.TAG_NAME, "option")[1].click()
        self.driver.find_element(By.ID, "username").send_keys(self.username)
        self.driver.find_element(By.ID, "password").send_keys(self.password)

        img_element = self.driver.find_element(By.ID, 'ranstringImg')    
        verification_code = self._identify_img(img_element)
        self.driver.find_element(By.ID, "ranstring").send_keys(verification_code)

        login_button.click() # login
        wp.print("正在登录...")

        for i in range(0, self.max_try):
            # 检测验证码错误
            try:
                WebDriverWait(self.driver, 2).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert.dismiss()
                wp.print("\n验证码错误")
                wp.print(f"第{i+2}次尝试登录...")
                img_element = self.driver.find_element(By.ID, 'ranstringImg')
                verification_code = self._identify_img(img_element)
                ranstr = self.driver.find_element(By.ID, "ranstring")
                ranstr.clear()
                ranstr.send_keys(verification_code)

                login_button.click() # login
                sleep(2) # wait 2 second for refreshing the image
            except:
                wp.print("登录成功！\n")
                break
            if i >= self.max_try-1:
                raise Exception("登录失败")

    def get_course_info_by(self, course_url:str) -> str:
        self.driver.get(course_url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "limit")))

        self._count += 1
        wp.print(f"第{self._count}个课程爬取成功")
        return self.driver.page_source

    def __del__(self) -> None:
        self.close_browser()



if __name__  == "__main__":
    url1 = "https://ocw.swjtu.edu.cn/yethan/YouthIndex?setAction=courseInfo&courseid=2211AE1814DA3B03"
    url2 = "https://ocw.swjtu.edu.cn/yethan/YouthIndex?setAction=courseInfo&courseid=00BFE48ACA8B52F3"
    b = Browser(mode="test")
    b.get_course_info_by(url1)
    input()
    b.close_browser()