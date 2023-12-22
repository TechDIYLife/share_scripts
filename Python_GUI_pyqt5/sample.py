from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import time

app = QtWidgets.QApplication([])
ui_path = "."
dlg1 = uic.loadUi(f"{ui_path}/MyUI.ui")
dlg2 = uic.loadUi(f"{ui_path}/MyUI2.ui")


##### 按钮与消息窗口 #####
def showMsg1():
    dlg = QMessageBox()
    dlg.setWindowTitle("I have a question!")
    dlg.setText("This is a question dialog")
    dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    dlg.setIcon(QMessageBox.Question)
    button = dlg.exec()

    if button == QMessageBox.Yes:
        print("Yes!")
    else:
        print("No!")

dlg1.pushButton_msg.clicked.connect(showMsg1)

##### 下拉列表 QComboBox #####
dlg1.comboBox.addItems(["文本1","文本2"])
dlg1.comboBox.addItem("文本3")
dlg1.comboBox.setCurrentIndex(1)

def showMsg2():
    print("comboBox已选择：", dlg1.listWidget.currentRow())

dlg1.comboBox.currentIndexChanged.connect(showMsg2)

##### 列表 QListWidget #####
dlg1.listWidget.addItems(["文本1","文本2"])
dlg1.listWidget.addItem("文本3")
#dlg1.listWidget.setCurrentIndex(1)
dlg1.listWidget.setCurrentRow(1)

def listWidgetChange(index):
    print("listWidget已选择：", dlg1.listWidget.currentRow())
    print("listWidget已选择：", index)
dlg1.listWidget.currentRowChanged.connect(listWidgetChange)


##### 对话窗口 #####
def changeDlg():
    dlg1.hide()
    dlg2.show()

dlg1.pushButton_changeDlg.clicked.connect(changeDlg)

##### CheckBox ######
dlg1.checkBox.setChecked(True)

def showMsg3():
    if dlg1.checkBox.isChecked():
        print("Checked True")
    else:
        print("Checked False")
dlg1.checkBox.stateChanged.connect(showMsg3)

##### 图像显示QLabel #####
img = QtGui.QImage("1.png")
dlg1.label.setFixedWidth(200)
dlg1.label.setFixedHeight(200)
img_scaled = img.scaled(dlg1.label.width(), dlg1.label.height())
dlg1.label.setPixmap(QtGui.QPixmap.fromImage(img_scaled))


##### 图像列表显示 #####
# 设置为IconMode
dlg1.listWidget_imagelist.setViewMode(QListView.IconMode)
# 调整Icon Size
dlg1.listWidget_imagelist.setIconSize(QtCore.QSize(200,200))
# 设置QListWidget的网格大小，以适应你的图标大小
dlg1.listWidget_imagelist.setGridSize(QtCore.QSize(200, 220))

for i in range(1,8):
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(str(i)+".png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    item = QtWidgets.QListWidgetItem()
    item.setIcon(icon)
    dlg1.listWidget_imagelist.addItem(item)


##### 多线程， 切换图片 #####
i = 1
scene = QGraphicsScene()
#view = QGraphicsView()
view = dlg1.graphicsView
view.setScene(scene)

def rotateImage():
    global i
    img = QtGui.QImage(str(i)+".png")
    # QImage -> QPixmap
    pixmap = QtGui.QPixmap.fromImage(img)

    # pixmapをsceneに追加
    pixmap.width = view.width()
    pixmap.height = view.height()
    scene.addPixmap(pixmap)
    view.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio) #调整图像大小
    view.show()
    i +=1
    if i>7: i=1

timer = QtCore.QTimer()
timer.timeout.connect(rotateImage) # 指定要运行的函数
timer.start(1000) # 时间间隔为1s

# 另一种写法
#class WorkThread(QThread):
#     timer = pyqtSignal() #自定义信号，进行通讯
#     def run(self):
#          while True:
#               self.sleep(2)
#               self.timer.emit() # 发送通讯
#     
#worker = WorkThread()
#worker.timer.connect(rotateImage) # 绑定执行函数
#worker.start()


##### 视频播放(播放速度没有调整好) #####
# 视频下载自： https://samplelib.com/sample-mp4.html
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2
from PyQt5 import QtGui

class WorkThreadVideo(QThread):
    change_pixmap_signal = pyqtSignal(QImage)  # Signal to indicate a frame is ready to display
    def __init__(self, video_source="sample-10s.mp4"):
        super().__init__()
        self.video_source = video_source

    def init_video(self):
        # Open the video source
        self.vid = cv2.VideoCapture(self.video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)  # Get the frames per second of the video
        self.delay = int(1000/self.fps)  # Calculate the delay between frames in milliseconds

        self.elapsed_time = 0  # 播放时长计数器

    def run(self):
        play_time_start = time.time()
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while self.vid.isOpened():
            loop_start_time = time.time()  # 记录循环开始的时间
            
            ret, frame = self.vid.read()
            if ret:
                # Convert the frame to QT format
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                #p = convert_to_Qt_format.scaled(360, 280, aspectRatioMode=QtCore.Qt.KeepAspectRatio) # 图像分辨率差
                p = convert_to_Qt_format.scaled(360, 280, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.change_pixmap_signal.emit(p)  # Emit the ready frame
            else:
                self.vid.release()
                return
            
            #cv2.imshow("win",frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
            
            # 计算处理帧所需的时间
            #processing_time = (time.time() - loop_start_time) * 1000  # 转换为毫秒
            # 计算实际的等待时间
            #actual_delay = max(1, int(self.delay - processing_time))
            #self.elapsed_time += processing_time
            #print(self.elapsed_time/1000, processing_time/1000, self.delay/1000, self.fps, time.time()-play_time_start)            
            #self.msleep(actual_delay)

        # Release the video source when the loop is finished
        self.vid.release()
        return

def displayVideo(img):
    dlg1.label_Video.setPixmap(QtGui.QPixmap.fromImage(img))
# Assuming dlg1 is a valid dialog with label_Video
dlg1.label_Video.setFixedWidth(360)
dlg1.label_Video.setFixedHeight(280)

workerVideo = WorkThreadVideo()
workerVideo.change_pixmap_signal.connect(displayVideo)  # Connect signal to display video
def videoPlay():
    workerVideo.init_video()
    workerVideo.start()

dlg1.pushButtonReply.clicked.connect(videoPlay)


if __name__ == "__main__":
    dlg1.show()  # 对话框显示
    app.exec()   # 执行
