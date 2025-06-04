import sys, threading
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QMessageBox, QDesktopWidget,QHBoxLayout, QVBoxLayout,QLabel,QGridLayout,QLineEdit,QScrollArea, QSizePolicy, QCheckBox, QLayout, QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal
from course import Course
from progress_bar import ProgressBar
from config_rw import ConfigReadWriter
from wprinter import *
import traceback
from config_manager import ConfigManager

class MainWindow(QWidget):
    progressChanged = pyqtSignal(int, int, int)
    widgetAdded = pyqtSignal(dict)
    textReceived = pyqtSignal(str)

    def __init__(self):
        self._width = 1600
        self._height = 900
        self._style = '''
            QLabel {
                text-align: left;           /* 左对齐 */
                font-size: 20px;            /* 字体大小 */
                color: black;               /* 文字颜色 */
                background-color: #ffffff;  /* 按钮背景颜色 */
                border: 2px solid #2980b9;  /* 边框样式 */
                border-radius: 10px;        /* 边框圆角 */
                padding: 10px;              /* 内边距 */
            }
        '''
        self.startSearch = None
        super().__init__()
        self.initUI()
        self.cm = ConfigManager()
        self.filterWindow = None
        self.widgetAdded.connect(self.generate_item)
        wp.signal = self.textReceived
        self.textReceived.connect(self.show_info)

        # thread
        self._thread = None
        self.should_restart = False
        self.should_close = False
        self.thread_lock = threading.Lock()

    def initUIHeader(self) -> QLayout:
        header = QHBoxLayout()
        #进度条
        self.progressBar = ProgressBar()
        self.progressBar.progress.setFixedWidth(500)
        self.progressBar.hide()        
        self.progressChanged.connect(self.progressBar.increaseProgressto_n)
        #筛选
        filterButton = QPushButton('筛选', self)
        filterButton.clicked.connect(self.showFilterWindow)
        #开始检索
        startButton = QPushButton('开始检索', self)
        filterButton.resize(filterButton.sizeHint()) 
        startButton.clicked.connect(self.search)
        self.startSearch = startButton

        header.addStretch(1)
        header.addWidget(self.progressBar)
        header.addStretch(1)
        header.addWidget(filterButton)
        header.addWidget(startButton)
        return header

    def initUIBody(self) -> QWidget:
        body = QHBoxLayout()
        widget = QWidget()
        widget2 = QWidget()
        right = QScrollArea()
        right.setFixedHeight(600)
        right.setFixedWidth(300)
        right.setWidgetResizable(True)

        self.container = QVBoxLayout(widget)
        self.container.setAlignment(Qt.AlignHCenter)
        self.container.addStretch(1)
        self.info = QVBoxLayout(widget2)
        self.info.addStretch(1)
        
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)  # 使滚动区域自适应窗口大小
        scroll_area.setWidget(widget)

        body.addWidget(scroll_area)
        body.addWidget(right)
        right.setWidget(widget2)
        return body

    def generate_item(self, info:dict):
        text = f"""<body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 20px;">

    <h1 style="text-align: center; color: #333; font-size: 2.5em; margin-bottom: 20px;">
        {info["name"]}
    </h1>

    <div style="margin-bottom: 40px;">
        <h2 style="font-size: 1.8em; color: #555; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px;">
            课程介绍
        </h2>
        <p style="font-size: 1.2em; margin-bottom: 15px; text-indent: 2em;">
            {info["intro"]}
        </p>
        <ul style="list-style-type: none; padding: 0;">
            <li style="margin-bottom: 10px; padding: 10px; border-radius: 5px;">
                <strong>上课时间:</strong> {info["schedule"]}
            </li>
            <li style="margin-bottom: 10px; padding: 10px; border-radius: 5px;">
                <strong>选课时间:</strong> {info["selection"]}
            </li>
            <li style="margin-bottom: 10px; padding: 10px; border-radius: 5px;">
                <strong>学时说明:</strong> {info["creditExplanation"]}
            </li>
            <li style="margin-bottom: 10px; padding: 10px; border-radius: 5px;">
                <strong>上课地点:</strong> {info["venue"]}
            </li>
            <li style="margin-bottom: 10px; padding: 10px; border-radius: 5px;">
                <strong>报名人数:</strong> <font color="green">{info["enrollment"]} </font>/ {info["maxEnrollment"]}
            </li>
            <li style="margin-bottom: 10px; padding: 10px; border-radius: 5px;">
                <strong>网站:</strong> 
                <a href="{info["url"]}" style="color: #778dad;text-decoration: none;" target="_blank">{info["url"]}</a>
            </li>
        </ul>
    </div>

    <div style="margin-bottom: 40px;">
        <h2 style="font-size: 1.8em; color: #555; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px;">
            活动流程
        </h2>
        <p style="font-size: 1.2em; margin-bottom: 15px; text-indent: 2em;">
            {info["flow"]}
        </p>
    </div>

    <div style="margin-bottom: 40px;">
        <h2 style="font-size: 1.8em; color: #555; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px;">
            课程说明
        </h2>
        <p style="font-size: 1.2em; margin-bottom: 15px;">
            {"无" if len(info["specification"])==0 else info["specification"]}
        </p>
    </div>

    </body>
    """
        
        item = QLabel(text)
        item.setOpenExternalLinks(True)
        item.setWordWrap(True)

        item.setFixedWidth(1000)
        item.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        item.setStyleSheet(self._style)

        self.container.insertWidget(self.container.count() - 1, item)        

    def initUI(self):
        self.resize(self._width, self._height)
        self.center()
        self.setWindowTitle('第二课堂')

        # 布局
        mainPage = QVBoxLayout()
        header = self.initUIHeader()                
        body = self.initUIBody()
        
        mainPage.addLayout(header)
        mainPage.addLayout(body)

        self.setLayout(mainPage)
        self.show()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.should_close = True
            if self.filterWindow is not None:
                self.filterWindow.close()
            event.accept()
        else:
            event.ignore()      
        
    def search(self): 
        # 禁用点击
        self.startSearch.setEnabled(False)
        self.startSearch.setText("重新检索")
        # processBar
        self.progressBar.show()

        # thread
        with self.thread_lock:
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._search_thread, args=(self.exception_callback,))
                self._thread.start()
            else:
                # 存在线程运行
                self.should_restart = True

    def exception_callback(self, exception:Exception):
        exc_type, exc_value, exc_traceback = sys.exc_info()
    
        wp.print("回调函数：子线程异常！")
        wp.print("="*60)
        wp.print(f"异常类型: {exc_type.__name__}")
        wp.print(f"异常消息: {exc_value}")
        
        # 获取最后一个堆栈帧
        frame = exc_traceback.tb_frame
        lineno = exc_traceback.tb_lineno
        filename = frame.f_code.co_filename
        
        wp.print(f"文件位置: {filename} 第 {lineno} 行")
        wp.print("-"*60)
        limit = 6
        wp.print(f"堆栈跟踪{limit}:")
        for i in traceback.format_tb(exc_traceback, limit=limit):
            wp.print(i)
        wp.print("="*60)

    def _search_thread(self, callback:callable):
        try:
            self.search_thread()
            while True:
                        if self.should_restart:
                            self.should_restart = False
                            wp.print("Restarting thread work...")
                            self.search_thread()
                            continue 
                        elif self.should_close:
                            print("结束子线程")
                            break

        except Exception as e:
            callback(e)

    def search_thread(self): 
        if not hasattr(self, "_course"):             
            self._course = Course()
        else: # 多次运行
            self._course = Course(self._course.browser)


        skip_count = 0
        for count in range(1, self.cm.get("search_count") + 1):   
            c = self._course            

            condition_not_met_if_ = False
            if self.cm.get("campus_jiuli"):
                condition_not_met_if_ |= self._course.campus_restriction()
            if self.cm.get("department_jingguan"):
                condition_not_met_if_ |= self._course.department_restriction()
            if self.cm.get("participants_full"):
                condition_not_met_if_ |= self._course.registration_is_full()       
            if self.cm.get("times_up"):
                condition_not_met_if_ |= self._course.selection_has_ended()         
            if self.cm.get("is_early"):
                condition_not_met_if_ |= self._course.selection_not_begun()       
            if self.cm.get("venue") == "jiuli":
                condition_not_met_if_ |= self._course.take_place_in_xipu()
            if self.cm.get("venue") == "xipu":
                condition_not_met_if_ |= not self._course.take_place_in_xipu()

            if condition_not_met_if_:
                skip_count += 1                
            else:               
                course_info = {
                    "name" : c.get_course_name(), 
                    "intro" : c.get_full_introduction(), 
                    "schedule" : c.get_course_time(), 
                    "selection" : c.get_course_selection_time(),
                    "venue" : c.get_course_location(),
                    "enrollment" : c.get_number_of_enrollee(),
                    "maxEnrollment" : c.get_max_number_of_enrollee(), 
                    "url" : c.get_course_url(), 
                    "flow" : c.get_course_process(), 
                    "specification" : c.get_course_description(), 
                    "creditExplanation" : c.get_course_hours_explanation()
                }

                self.widgetAdded.emit(course_info)

            n = int( (count) * 100 / self.cm.get("search_count") )
            self.progressChanged.emit(n, self.cm.get("search_count"), skip_count)   #n , max, skip

            self._course.next()
        # 启用点击
        self.startSearch.setEnabled(True)

    def showFilterWindow(self):
        self.filterWindow = FilterWindow(self, self.cm)
        self.filterWindow.show()   

    def show_info(self, text:str):
        a = QLabel(text)
        a.setAlignment(Qt.AlignTop)
        a.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        a.setWordWrap(True)
        self.info.addWidget(a)

class FilterWindow(QWidget):
    def __init__(self, _parent:MainWindow, cm:ConfigManager):
        self._width = 700
        self._height = 600
        self.closed = False
        self._parent = _parent
        self.cm = cm

        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(self._width, self._height)
        self.center()
        self.setWindowTitle('筛选')

        # 校区限制
        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel("校区限制"),1,0)
        checkBox1 = QCheckBox("九里校区")

        checkBox1.setChecked(self.cm.get("campus_jiuli"))
        checkBox1.stateChanged.connect(lambda: self.cm.set("campus_jiuli", self.cm.get("campus_jiuli") == False, False))
        gridLayout.addWidget(checkBox1,1,1)

        # 专业限制
        gridLayout.addWidget(QLabel("专业限制"),2,0)
        checkBox2 = QCheckBox("经管")
        checkBox2.setChecked(self.cm.get("department_jingguan"))
        checkBox2.stateChanged.connect(lambda: self.cm.set("department_jingguan", self.cm.get("department_jingguan") == False, False))
        gridLayout.addWidget(checkBox2,2,1)

        # 检索次数
        gridLayout.addWidget(QLabel("检索次数(1-30)"),3,0)
        lineBox = QLineEdit()
        lineBox.setText(str(self.cm.get("search_count")))
        lineBox.setFixedWidth(300)
        lineBox.textChanged.connect(self.searchCountChanged)
        gridLayout.addWidget(lineBox,3,1)

        # 报名人数
        gridLayout.addWidget(QLabel("报名人数"),4,0)
        checkBox3 = QCheckBox("跳过报名人数已满")
        checkBox3.setChecked(self.cm.get("participants_full"))
        checkBox3.stateChanged.connect(lambda : self.cm.set("participants_full", self.cm.get("participants_full") == False, False))
        gridLayout.addWidget(checkBox3,4,1)

        # 时间 
        gridLayout.addWidget(QLabel("选课时间"),5,0)
        checkBox4 = QCheckBox("跳过未开始选课")
        checkBox4.setChecked(self.cm.get("is_early"))
        checkBox4.stateChanged.connect(lambda : self.cm.set("is_early", self.cm.get("is_early") == False, False))
        checkBox5 = QCheckBox("跳过已结束选课")
        checkBox5.setChecked(self.cm.get("times_up"))
        checkBox5.stateChanged.connect(lambda : self.cm.set("times_up", self.cm.get("times_up") == False, False))
        gridLayout.addWidget(checkBox4,5,1)
        gridLayout.addWidget(checkBox5,5,2)

        gridLayout.addWidget(QLabel("上课地点"),6,0)
        checkbox6 = QCheckBox("犀浦校区")
        checkbox6.setChecked(self.cm.get("venue") == "xipu")
        checkbox6.stateChanged.connect(lambda : self.cm.set("venue", "any" if self.cm.get("venue") =="xipu" else "xipu", False))
        gridLayout.addWidget(checkbox6,6,1)
        checkbox7 = QCheckBox("九里校区")
        checkbox7.setChecked(self.cm.get("venue") == "jiuli")
        checkbox7.stateChanged.connect(lambda : self.cm.set("venue", "any" if self.cm.get("venue") =="jiuli" else "jiuli", False))
        gridLayout.addWidget(checkbox7,6,2)

        # 确定按钮
        confirmLayout = QHBoxLayout()
        button = QPushButton("确定")
        button.clicked.connect(self.confirm)
        confirmLayout.addStretch(1)
        confirmLayout.addWidget(button)
        confirmLayout.addStretch(1)

        # 添加布局
        vlayout = QVBoxLayout()
        vlayout.addLayout(gridLayout)
        vlayout.addLayout(confirmLayout)

        self.setLayout(vlayout)        

    def confirm(self, event):
        # write config
        self.cm._save()

        # message box
        reply = QMessageBox.question(self, 'Message',"保存成功", QMessageBox.Yes , QMessageBox.Yes)                

        if reply == QMessageBox.Yes:
            self.close()

    def searchCountChanged(self, text:str):
        if text.isdigit():
            self.cm.set("search_count", text, False)
        else:
            if text != "":
                reply = QMessageBox.question(self, 'Message',"检索次数必须为整数", QMessageBox.Yes , QMessageBox.Yes)                

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())    


def excepthook(exc_type, exc_value, exc_tb):
    """全局异常捕获函数"""
    error_info = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Critical Error")
    msg.setText(f"Unhandled Exception: {exc_type.__name__}")
    msg.setInformativeText(str(exc_value))
    msg.setDetailedText(error_info)
    
    # 直接获取详细文本框
    detail_text = msg.findChild(QTextEdit)
    detail_text.setFixedHeight(detail_text.sizeHint().height())  # 最大高度限制    
    detail_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏滚动条

    # 修改3: 调整对话框尺寸
    msg.layout().setSizeConstraint(QLayout.SetFixedSize) 

    copy_btn = msg.addButton("Copy Error and Exit", QMessageBox.ActionRole)
    copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(error_info))

    msg.exec_()
    
    sys.exit(1)  # 强制退出

if __name__ == '__main__':
    # 重写全局异常钩子
    sys.excepthook = excepthook
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())