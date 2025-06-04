from PyQt5.QtWidgets import QProgressBar, QVBoxLayout, QWidget, QLabel
from wprinter import *

class ProgressBar(QWidget):
    def __init__(self):
        self._show = True
        super().__init__()

        self._initUI()

    def _initUI(self):
        # 创建布局
        self._layout = QVBoxLayout()

        # 创建进度条
        self.progress = QProgressBar(self)
        self._reset_progress()

        # 将进度条和按钮添加到布局
        self._layout.addWidget(self.progress)

        self.setLayout(self._layout)
    
    def _reset_progress(self):
        self.progress.setValue(0)      # 从0开始
        self.progress.setMaximum(100)  # 最大值为100

    def increaseProgressto_n(self, n:int, max:int, skip:int):
        self.progress.setValue(n)
        if n >= 100:
            self.hide()
            wp.print(f"加载完成{max-skip}/{max}课程，因筛选跳过{skip}项")
            # self._layout.addWidget(QLabel(f"加载完成{max-skip}/{max}课程，因筛选跳过{skip}项"))
            self._reset_progress()

    def show(self):
        if self._show is not True:
            self._show = True
            self.progress.show()

    def hide(self):
        if self._show is True:
            self._show = False
            self.progress.hide()
