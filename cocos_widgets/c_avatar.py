import asyncio
import os
import sys

import aiohttp

from PySide6.QtCore import QRectF, Qt, QSize, QTimer, QPropertyAnimation, \
    QPointF, Property, QBuffer, QMimeData
from PySide6.QtGui import QPixmap, QColor, QPainter, QPainterPath, QMovie, QClipboard
from PySide6.QtWidgets import QWidget, QApplication, QHBoxLayout, QMenu, QFileDialog
from PySide6 import QtAsyncio

from db.mysql.async_utils import is_in_async_context


class CAvatar(QWidget):
    Circle = 0  # 圆形
    Rectangle = 1  # 圆角矩形
    SizeLarge = QSize(128, 128)
    SizeMedium = QSize(64, 64)
    SizeSmall = QSize(32, 32)
    StartAngle = 0  # 起始旋转角度
    EndAngle = 360  # 结束旋转角度

    def __init__(self, *args, shape=0, url='', cacheDir='', size=QSize(64, 64), is_OD=False, animation=False,
                 parent=None, **kwargs):
        super(CAvatar, self).__init__(*args, **kwargs)
        self.is_OD = is_OD
        self.parent = parent
        self.url = url
        self.cacheDir = cacheDir
        self._angle = 0  # 旋转角度
        self.pradius = 0  # 加载进度条半径
        self.animation = animation
        self._movie = None  # 动态图对象
        self._pixmap = QPixmap()  # 原始图片
        self.pixmap = QPixmap()  # 绘制的图片对象
        self.isGif = url.endswith('.gif')
        self.scale_factor = 1.0  # 缩放比例

        # 进度动画定时器
        self.loadingTimer = QTimer(self, timeout=self.onLoading)

        # 旋转动画
        self.rotateAnimation = QPropertyAnimation(self, b'angle', self, loopCount=1)

        # 设置参数
        self.setShape(shape)
        self.setCacheDir(cacheDir)
        self.setSize(size)
        if is_in_async_context():
            task = asyncio.create_task(self.setUrl(url))
            asyncio.gather(task)
        else:
            asyncio.run(self.setUrl(url))

    def paintEvent(self, event):
        super(CAvatar, self).paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        path = QPainterPath()
        diameter = min(self.width(), self.height())
        if not self.is_OD:
            radius = int(diameter / 2) if self.shape == self.Circle else 4
            halfW, halfH = self.width() / 2, self.height() / 2
            painter.translate(halfW, halfH)
            path.addRoundedRect(QRectF(-halfW, -halfH, diameter, diameter), radius, radius)
            painter.setClipPath(path)
        else:
            painter.translate(self.width() / 2, self.height() / 2)

        scaled_pixmap = self.pixmap.scaled(self.pixmap.size() * self.scale_factor, Qt.KeepAspectRatio,
                                           Qt.SmoothTransformation)
        if self.rotateAnimation.state() == QPropertyAnimation.Running:
            painter.rotate(self._angle)
            painter.drawPixmap(QPointF(-scaled_pixmap.width() / 2, -scaled_pixmap.height() / 2), scaled_pixmap)
        else:
            painter.drawPixmap(-scaled_pixmap.width() // 2, -scaled_pixmap.height() // 2, scaled_pixmap)

        if self.loadingTimer.isActive():
            diameter = 2 * self.pradius
            painter.setBrush(QColor(45, 140, 240, int((1 - self.pradius / 10) * 255)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(-self.pradius, -self.pradius, diameter, diameter), self.pradius,
                                    self.pradius)

    def enterEvent(self, event):
        """鼠标进入动画"""
        if self.animation:
            self._startRotation(self.StartAngle, self.EndAngle)

    def leaveEvent(self, event):
        """鼠标离开动画"""
        if self.animation:
            self._startRotation(self.EndAngle, self.StartAngle)

    def onLoading(self):
        """更新进度动画"""
        if self.loadingTimer.isActive():
            self.pradius = (self.pradius + 1) % 10
        self.update()

    def onFinished(self, data):
        """图片下载完成"""
        self.loadingTimer.stop()
        if self.isGif:
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            buffer.write(data)
            buffer.seek(0)
            self._movie = QMovie(self)
            self._movie.setDevice(buffer)
            if self._movie.isValid():
                self._movie.frameChanged.connect(self._resizeGifPixmap)
                self._movie.start()
        else:
            self._pixmap.loadFromData(data)
            self._resizePixmap()

    def onError(self, code):
        """下载出错"""
        self._pixmap = QPixmap(self.size())
        self._pixmap.fill(QColor(204, 204, 204))  # 灰色背景提示
        self._resizePixmap()

    async def refresh(self):
        """强制刷新"""
        await self._get(self.url)

    def setShape(self, shape):
        """设置形状"""
        self.shape = shape

    async def setUrl(self, url):
        """设置URL"""
        self.url = url
        await self._get(url)

    def setCacheDir(self, cacheDir=''):
        """设置本地缓存路径"""
        self.cacheDir = cacheDir
        if cacheDir and not os.path.exists(cacheDir):
            os.makedirs(cacheDir)

    def setSize(self, size):
        """设置固定尺寸"""
        if not isinstance(size, QSize):
            size = self.SizeMedium
        self.setMinimumSize(size)
        self.setMaximumSize(size)
        self._resizePixmap()

    @Property(int)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self.update()

    def _resizePixmap(self):
        """缩放图片"""
        if not self._pixmap.isNull():
            self.pixmap = self._pixmap.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio,
                                              Qt.SmoothTransformation)
        self.update()

    def _resizeGifPixmap(self, _):
        """缩放GIF图片"""
        if self._movie:
            self.pixmap = self._movie.currentPixmap().scaled(self.width(), self.height(), Qt.IgnoreAspectRatio,
                                                             Qt.SmoothTransformation)
        self.update()

    def _startRotation(self, start, end):
        """启动旋转动画"""
        self.rotateAnimation.stop()
        self.rotateAnimation.setStartValue(start)
        self.rotateAnimation.setEndValue(end)
        self.rotateAnimation.setDuration(540)
        self.rotateAnimation.start()

    async def _get(self, url):
        """加载图片"""
        if not url:
            self.onError('Empty URL')
            return

        # 本地缓存路径
        cachePath = os.path.join(self.cacheDir, os.path.basename(url)) if self.cacheDir else None

        # 检查缓存
        if cachePath and os.path.exists(cachePath):
            self._pixmap.load(cachePath)
            self._resizePixmap()
            return

        if url.startswith('http'):
            self.loadingTimer.start(50)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=60) as response:
                        if response.status == 200:
                            data = await response.read()
                            if cachePath:
                                with open(cachePath, 'wb') as f:
                                    f.write(data)
                            self.onFinished(data)
                        else:
                            self.onError(response.status)
            except Exception as e:
                self.onError(str(e))
            finally:
                self.loadingTimer.stop()
        elif os.path.exists(url):
            self._pixmap.load(url)
            self._resizePixmap()
        else:
            self.onError('Invalid Path')

    def wheelEvent(self, event):
        """鼠标滚轮缩放图片"""
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor = min(3.0, self.scale_factor + 0.1)
        else:
            self.scale_factor = max(0.5, self.scale_factor - 0.1)
        self.update()

    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)
        copy_url_action = menu.addAction("复制图片URL")
        save_image_action = menu.addAction("保存图片到本地")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copy_url_action:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.url)
        elif action == save_image_action:
            self._saveImageToLocal()

    def _saveImageToLocal(self):
        """保存图片到本地"""
        if not self._pixmap.isNull():
            file_path, _ = QFileDialog.getSaveFileName(self, "保存图片", os.path.basename(self.url),
                                                       "图片文件 (*.png *.jpg *.bmp)")
            if file_path:
                self._pixmap.save(file_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = QWidget()
    layout = QHBoxLayout(widget)

    avatar = CAvatar(shape=CAvatar.Circle, url='https://sfile.chatglm.cn/testpath/gen-1733562562484428664_0.png')
    layout.addWidget(avatar)

    widget.show()
    # 显示窗口
    QtAsyncio.run(handle_sigint=True)
