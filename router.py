#encoding=utf8

import sys
from urllib.parse import urlparse
import json
import platform
import atexit
import os
import base64
import socket
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
if platform.system().lower() == 'windows':
    import wmi

class TrayIcon(QSystemTrayIcon):
    def __init__(self, app, icon, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.app = app
        self.setIcon(icon)
        self.showMenu()
        self.show()

    def showMenu(self):
        self.menu = QMenu()
        self.quitAction = QAction('Quit', self, triggered=self.quitWin)
        self.menu.addAction(self.quitAction)
        self.activated.connect(self.activatedHandler)

    def quitWin(self):
        cleanDNS()
        qApp.quit()
        sys.exit(0)

    def showMessage(self, title, content):
        super(TrayIcon, self).showMessage(title, content, self.MessageIcon())

    def activatedHandler(self, reason):
        try:
            self.setContextMenu(self.menu)
        except:
            self.quitWin()

class MainWindow(QMainWindow):
    def __init__(self, icon=None, parent=None):
        super(MainWindow, self).__init__(parent)
        self.icon = icon
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.trayIcon = TrayIcon(self, self.icon)
        self.changeDNS()
        self.trayIcon.showMessage('Notice', 'VORG DNS Router is running') 

    def closeEvent(self, event):
        try:
            self.hide()
            event.ignore()
        except:
            pass

    def changeDNS(self):
        try:
            ip = socket.gethostbyname('dns.vorg.io')
        except:
            self.trayIcon.showMessage('Warning', 'Cannot get DNS IP')
            sys.exit()
        osName = platform.system().lower()
        if osName == 'darwin':
            os.popen('networksetup -setdnsservers Wi-Fi {}'.format(ip)).close()
        elif osName == 'windows':
            if not DNSUpdate(ip):
                self.trayIcon.showMessage('Warning', 'Set DNS Route Failed')
                sys.exit()
        elif osName == 'linux':
            with open('/etc/resolv.conf', 'r+') as f:
                content = f.read().split("\n")
                row = content[0].split(' ')
                if len(row) <= 1 or row[0] != 'nameserver' or row[1] != ip:
                    content = 'nameserver {}\n{}'.format(ip, "\n".join(content))
                    f.seek(0)
                    f.write(content)
        else:
            self.trayIcon.showMessage('Warning', 'Operating System Not Supported')

def cleanDNS():
    osName = platform.system().lower()
    if osName == 'darwin':
        os.popen('networksetup -setdnsservers Wi-Fi Empty').close()
    elif osName == 'windows':
        DNSUpdate()
    elif osName == 'linux':
        with open('/etc/resolv.conf', 'r+') as f:
            content = f.read().split("\n")
            row = content[0].split(' ')
            if len(row) > 1 and row[0] == 'nameserver' and row[1] == ip:
                content = "\n".join(content[1:])
                f.seek(0)
                f.write(content)
    else:
        print("Operating System Not Supported")

def DNSUpdate(ip=None):
    wmiService = wmi.WMI()
    colNicConfigs = wmiService.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    if len(colNicConfigs) < 1:
        return False
    objNicConfig = colNicConfigs[0]
    if ip is None:
        returnValue = objNicConfig.SetDNSServerSearchOrder()
    else:
        arrDNSServers = [ip]
        returnValue = objNicConfig.SetDNSServerSearchOrder(DNSServerSearchOrder=arrDNSServers)
    if returnValue[0] == 0:
        return True
    return False

img = "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"

if __name__ == "__main__":
    atexit.register(cleanDNS)
    if platform.system().lower() == 'windows':
        tmpFile = '.icon.png'
    else:
        tmpFile = '/tmp/.icon.png'
    with open(tmpFile, 'wb') as f:
        f.write(base64.b64decode(img))
    app = QApplication(sys.argv)
    icon = QIcon('{}'.format(tmpFile))
    app.setWindowIcon(icon)
    form = MainWindow(icon)
    os.remove(tmpFile)
    app.exec_()
