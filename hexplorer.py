#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
PyQt File Explorer for Text and Binary Files
Dependencies: PyQt5
Author: ferbcn

TODO: editing binary files in hexadecimal mode
"""

import sys
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QMainWindow, QPushButton, QApplication,
                             QFileDialog, QTextEdit, QLineEdit, QPlainTextEdit, QToolBar, QAction, QCheckBox, QMessageBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

import os
import time

class Editor(QWidget):
    def __init__(self, parent, path, x_pos, y_pos):
        super().__init__()
        #QMainWindow.__init__ (self, None)
        self.parent = parent

        self.path = path
        self.title = 'Editor'
        self.left = x_pos
        self.top = y_pos
        self.width = 640
        self.height = 480
        self.initUI()
        self.open_file(self.path)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.textbox = QTextEdit(self)
        self.textbox.resize(self.width, self.height)

        saveButton = QPushButton("Save")
        saveButton.setMinimumHeight(20)
        saveButton.setMaximumWidth(90)
        clrButton = QPushButton("Clear")
        clrButton.setMinimumHeight(20)
        clrButton.setMaximumWidth(90)
        resetButton = QPushButton("Reset")
        resetButton.setMinimumHeight(20)
        resetButton.setMaximumWidth(90)

        saveButton.clicked.connect(self.save_item)
        clrButton.clicked.connect(self.clear_text)
        resetButton.clicked.connect(self.reset_item)

        hbox = QHBoxLayout()
        hbox.addWidget(saveButton)
        hbox.addWidget(clrButton)
        hbox.addWidget(resetButton)
        hbox.setContentsMargins(0, 0, 0, 0)

        vbox = QVBoxLayout()
        vbox.addWidget(self.textbox)
        vbox.addLayout(hbox)
        vbox.setContentsMargins(5, 5, 5, 5)

        self.setLayout(vbox)

        self.show()

    def save_item(self):
        content = self.textbox.toPlainText()
        dir_path = os.path.dirname(self.path)
        new_path, _ = QFileDialog.getSaveFileName(self, "Save file as ", dir_path,
                                                  "All Files (*);;Text Files (*.txt)")
        if new_path:
            print("saving: ", new_path)
            with open(new_path, "w") as output:
                output.writelines(content)
            self.parent.open_url()

    def clear_text(self):
        self.textbox.clear()

    def reset_item(self):
        self.open_file(self.path)

    def open_file(self, path):
        print("opening: ", path)
        try:
            with open(path, "r") as f:
                try:
                    content = f.readlines()
                except UnicodeDecodeError:
                    print(f'reading binary-encoded file: {path}')
                    # print(e, " (not a ascii-encoded unicode string)")
                    self.open_hex_file(path)
                else:
                    print(f'reading ascii-encoded unicode text file: {path}')
                    self.open_text_file(path, content)
            f.close()
        except PermissionError:
            print("Permission error")

    def open_text_file(self, path, lines):
        print("opening text file: ", path)
        for line in lines:
            self.textbox.insertPlainText(line)

    def open_hex_file(self, path):
        print("opening binary file: ", path)
        os.system("open "+path)

    def closeEvent(self, event):
        print("closing editor")
        self.parent.open_url()


class App(QMainWindow):

    def __init__(self, *args, **kwargs):
        super (App, self).__init__ (*args, **kwargs)

        #cwd = os.getcwd()
        home_dir = os.path.expanduser("~")
        self.last_file = None
        self.home_dir = home_dir
        self.current_dir = home_dir

        self.show_hidden_files = False
        self.show_preview = False
        self.sort_invert = False

        self.nav_history = []
        self.nav_history_index = -1

        # get screen size and set app size
        screen_resolution = app.desktop().screenGeometry()
        self.screenW, self.screenH = screen_resolution.width(), screen_resolution.height()
        self.window_width = int(self.screenW/2)
        self.window_height = int(self.screenH * 0.5)

        self.initUI()

    def initUI(self):
        #QMainWindow.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        # set position
        self.setGeometry(100, 100, self.window_width, self.window_height)
        self.setWindowTitle('HeXplorer')

        # File Menu
        # MENUBAR
        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(True)
        #self.menubar.setStyleSheet("QMenuBar{color: lightgrey}")
        viewMenu = self.menubar.addMenu('&View')

        # Navigation Toolbar
        navtb = QToolBar ("Navigation")
        navtb.setIconSize (QSize (16,16))

        back_btn = QAction (QIcon (os.path.join ('images', 'arrow-180.png')), "Back", self)
        back_btn.setStatusTip ("Back page")
        back_btn.triggered.connect (self.go_back)
        navtb.addAction (back_btn)

        fwd_btn = QAction(QIcon(os.path.join('images', 'arrow-000.png')), "Forward", self)
        fwd_btn.setStatusTip("Forward page")
        fwd_btn.triggered.connect(self.go_forward)
        navtb.addAction(fwd_btn)

        home_btn = QAction (QIcon (os.path.join ('images', 'home.png')), "Home", self)
        home_btn.setStatusTip ("Go home")
        home_btn.triggered.connect (self.go_home)
        navtb.addAction (home_btn)
        navtb.addSeparator ()

        sort_btn = QAction(QIcon(os.path.join('images', 'sort.png')), "Sort", self)
        sort_btn.setStatusTip("Inverse file sorting")
        sort_btn.triggered.connect(self.invert_list_sorting)
        navtb.addAction(sort_btn)
        navtb.addSeparator()

        self.hidden_check = QCheckBox("Show Hidden")
        self.hidden_check.setChecked(self.show_hidden_files)
        self.hidden_check.stateChanged.connect(lambda: self.show_hidden_state(self.hidden_check))
        navtb.addWidget(self.hidden_check)

        self.preview_check = QCheckBox("Preview Large")
        self.preview_check.setChecked(self.show_preview)
        self.preview_check.stateChanged.connect(lambda: self.show_preview_state(self.preview_check))
        navtb.addWidget(self.preview_check)

        self.urlbar = QLineEdit ()
        self.urlbar.returnPressed.connect (self.open_url)
        navtb.addWidget (self.urlbar)

        del_btn = QAction(QIcon(os.path.join('images', 'cross.png')), "Delete File", self)
        del_btn.setStatusTip("Delete file")
        del_btn.triggered.connect(self.delete_file)
        navtb.addAction(del_btn)

        self.dir_listbox = QListWidget()
#       self.dir_listbox.setMinimumHeightint(int(self.screenH * 0.05))
        self.dir_listbox.setMinimumWidth(int(self.screenW * 0.1))
        self.dir_listbox.setMaximumWidth(int(self.screenW * 0.1))
        self.dir_listbox.setAlternatingRowColors(True)
        self.dir_listbox.setFocusPolicy(1) #remove blue frame when window is selected yeaaaah!

        self.files_listbox = QListWidget ()
        self.files_listbox.setMinimumHeight (int(self.screenH * 0.05))
        self.files_listbox.setMinimumWidth (int(self.screenW * 0.1))
        self.files_listbox.setMaximumWidth (int(self.screenW * 0.1))
        self.files_listbox.setAlternatingRowColors (True)
        self.files_listbox.setFocusPolicy (1)  # remove blue frame when window is selected yeaaaah!

        """
        self.files_info_listbox = QListWidget()
        self.files_info_listbox.setMinimumHeight(int(self.screenH * 0.05))
        self.files_info_listbox.setMinimumWidth(int(self.screenW * 0.03))
        self.files_info_listbox.setMaximumWidth(int(self.screenW * 0.05))
        self.files_info_listbox.setAlternatingRowColors(True)
        self.files_info_listbox.setFocusPolicy(1)  # remove blue fram
        """

        self.files_attributes_listbox = QListWidget ()
        self.files_attributes_listbox.setFixedHeight(int(self.screenH * 0.07))
        self.files_attributes_listbox.setMinimumWidth (int(self.screenW * 0.15))
        self.files_attributes_listbox.setFocusPolicy (1)  # remove blue frame when window is selected yeaaaah!

        self.preview_textbox = QPlainTextEdit (self)
        self.preview_textbox.setReadOnly(True)
        #self.preview_textbox.setDisabled(True)

        viewbox = QVBoxLayout ()
        viewbox.addWidget (self.files_attributes_listbox)
        viewbox.addWidget (self.preview_textbox)

        navbox = QHBoxLayout ()
        navbox.addWidget(self.dir_listbox)
        navbox.addWidget (self.files_listbox)
        #navbox.addWidget(self.files_info_listbox)
        navbox.addLayout(viewbox)
        navbox.setContentsMargins(0, 0, 0, 0)

        # main layout: a vertical box with the clipboard and the horizontal box in it
        vbox = QVBoxLayout()
        vbox.addWidget(navtb)
        #vbox.addWidget (splitter)
        vbox.addLayout(navbox)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        container = QWidget ()
        container.setLayout (vbox)
        self.setCentralWidget (container)

        # connect button to methods on_click
        self.dir_listbox.clicked.connect(self.dir_onselect)
        self.files_listbox.clicked.connect (self.file_onselect)
        self.files_listbox.doubleClicked.connect (self.file_run)
        self.urlbar.returnPressed.connect (self.open_url)

        self.open_dir (self.home_dir)
        self.update_path (self.home_dir)
        self.open_url()

        self.show()


    def invert_list_sorting(self):
        self.sort_invert = not self.sort_invert
        self.open_dir(self.current_dir)


    def get_file_path_from_list(self):
        try:
            items = self.files_listbox.selectedItems()
            file = items[0].text()
            path = "/".join(self.urlbar.text().split("/") + [file])
        except IndexError:
            return None
        return path


    def show_preview_state(self, b):
        if b.isChecked() == True:
            print("Large file " + b.text() + " activated")
            self.show_preview = True
            path = self.get_file_path_from_list()
            if path:
                self.preview_file(path)
        else:
            print("Large file " + b.text() + " deactivated")
            self.show_preview = False


    def show_hidden_state(self, b):
        #if b.text() == "Hidden":
        if b.isChecked() == True:
            print("Showing " + b.text() + " files")
            self.show_hidden_files = True
        else:
            print("Not showing " + b.text() + " files")
            self.show_hidden_files = False
        self.open_dir(self.current_dir)


    def go_back(self):
        print("Back History!")
        if len(self.nav_history) > self.nav_history_index * -1:
            self.nav_history_index -= 1
        path = self.nav_history[self.nav_history_index]
        self.open_dir(path)
        self.update_path(path)

    def go_forward(self):
        print("Forward History!")
        if self.nav_history_index < -1:
            self.nav_history_index += 1
        path = self.nav_history[self.nav_history_index]
        self.open_dir(path)
        self.update_path(path)

    def go_home(self):
        print("Go Home!")
        self.open_dir (self.home_dir)
        self.update_path (self.home_dir)
        self.add_path_to_history(self.home_dir)

    def delete_file(self):
        path = self.get_file_path_from_list()
        if path:
            reply = QMessageBox.question(self, 'Delete File',
                                         "Are you sure you want to delete this file? \n\n "+ path, QMessageBox.No |
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                print("File DELETED!")
                os.remove(path)
                self.open_url()
            else:
                print("File NOT deleted!")
        else:
            print("No file selected!")

    # open a directory from url path
    def open_url(self):
        path = self.urlbar.text ()
        self.open_dir (path)
        self.add_path_to_history(path)

    # updates url bar
    def update_path (self, path):
        self.urlbar.clear()
        self.urlbar.setText (path)

    def add_path_to_history(self, path):
        self.nav_history.append(path)
        self.nav_history_index = -1
        # limit history to 100 items
        if len(self.nav_history) > 100:
            self.nav_history = self.nav_history[1:]
        #print(self.nav_history)

    def open_dir (self, path):
        self.clear_all ()
        self.current_dir = "/".join (path.split ("/"))  # save the last path
        # insert the back option ('..') in the directory listbox
        self.dir_listbox.insertItem (0, '..')
        l_dirs = self.dir_listbox.count()
        l_files = self.files_listbox.count ()
        #l_files = self.files_listbox.rowCount()
        for root, dirs, files in os.walk (path):
            # update directories
            dirs.sort(key=str.casefold) #ignore lower upper case ordering
            if not self.sort_invert:
                dirs = reversed(dirs)
            for dir in dirs:
                if dir[0] == "." and not self.show_hidden_files:
                    pass
                else:
                    self.dir_listbox.insertItem (l_dirs, dir)
            # update files
            files.sort(key=str.casefold)
            if not self.sort_invert:
                files = reversed(files)
            file_count = 0
            for file in files:
                """
                try:
                    file_obj = os.stat(os.path.join(path, file))
                    file_size = file_obj.st_size
                    file_size_info = str(file_size) + " bytes"
                except FileNotFoundError:
                    file_size = 0
                except PermissionError:
                    print("Permission Error")
                    file_size = 0
                """
                if file[0] == "." and not self.show_hidden_files:
                    pass
                else:
                    self.files_listbox.insertItem(l_files, file)
                    #self.files_info_listbox.insertItem(l_files, file_size_info)
            break

    def dir_onselect (self):
        self.last_file = None
        items = self.dir_listbox.selectedItems()
        dir = items[0].text()
        path = self.urlbar.text()
        print(f'opening directory: {path}')
        if dir == '..':
            if len (path) == 0:
                path = "/"
            else:
                path = "/".join (path.split ("/")[0:-1])
        else:
            if len (path) == 1:
                path = self.urlbar.text() + dir
            else:
                path = self.urlbar.text () + "/" + dir

        self.update_path (path)
        self.open_dir (path)
        self.add_path_to_history(path)

    def file_onselect (self, event):
        path = self.get_file_path_from_list()
        self.update_path (os.path.split (path)[0])
        file_size = self.show_file_attributes(path)
        if file_size < 5120 or self.show_preview:
            self.preview_file(path)

    def show_file_attributes(self, path_to_file):
        file_obj = os.stat (path_to_file)
        file_size = file_obj.st_size
        file_size_kb = file_size / 1024
        self.files_attributes_listbox.clear()  # make sure the listbox is cleared
        self.files_attributes_listbox.insertItem (0, "File Size: " + str (file_size) + " bytes (" + str ("{0:.3f}".format(file_size_kb))+" Kbytes)")
        self.files_attributes_listbox.insertItem (1, "Last Accessed: %s" % time.ctime (file_obj.st_atime))
        self.files_attributes_listbox.insertItem (2, "Last Modified: %s" % time.ctime (file_obj.st_mtime))
        self.preview_textbox.clear()
        return file_size

    def preview_file(self, path):
        self.preview_textbox.clear()
        try:
            with open (path, "r") as f:
                try:
                    content = f.readlines ()
                except UnicodeDecodeError:
                    print(f'reading binary-encoded file: {path}')
                    #print(e, " (not a ascii-encoded unicode string)")
                    self.show_hex_preview(path)
                else:
                    print (f'reading ascii-encoded unicode text file: {path}')
                    self.show_text_preview (content)
            f.close ()
        except PermissionError:
            print ("Permission error")


    def show_text_preview(self, lines):
        num_of_chars = 0
        for line in lines:
            self.preview_textbox.insertPlainText (line)
            num_of_chars += len(line)
        self.files_attributes_listbox.insertItem (3, "Lines: " + str(len(lines)))
        self.files_attributes_listbox.insertItem (4, "Characters: " + str (num_of_chars))

    def show_hex_preview(self, filename):
        address_line = 0
        with open(filename, "rb") as input_file:

            # define address padding length
            filesize_bytes = os.path.getsize(filename)
            if filesize_bytes > 16 ** 6:
                padding = 10
            elif filesize_bytes > 16 ** 4:
                padding = 8
            elif filesize_bytes > 16 ** 2:
                padding = 6
            else:
                padding = 4

            # loop through file in chunks of 16 bytes
            while True:
                hexdata = input_file.read(16).hex()  # reading 16 bytes in a row
                if len(hexdata) == 0:  # breaks loop once no more binary data is read
                    break

                # format address string
                address_str = "{0:#0{1}x}".format(address_line, padding) + ": "

                # format Hex data string
                data_str = ""
                for i in range(0, 32, 2):
                    data_str += (hexdata[i:i + 2]).upper() + " "
                    if i == 14:
                        data_str += " "

                # convert hex data to ASCII
                ascii_str = ''.join(chr(int(hexdata[i:i + 2], 16)) for i in range(0, len(hexdata), 2))
                ascii_str = ''.join([i if ord(i) < 127 else '.' for i in ascii_str])
                ascii_str = (''.join(ascii_str.splitlines())) #remove linebreaks

                #print(address_str, data_str, ascii_str)
                hex_line = '{0:10} {1:55} {2}'.format(address_str, data_str, ascii_str) + '\n'
                self.preview_textbox.insertPlainText(hex_line)
                address_line += 16

            #print(f"filesize: {filesize_bytes} bytes")

    def file_run(self):
        items = self.files_listbox.selectedItems ()
        if not len(items) == 0:
            file = items[0].text ()
            path = self.urlbar.text ()
            file_path = os.path.join(path, file)
            widget = self.geometry()
            x_pos = self.window_width - widget.width()
            y_pos = self.window_height - widget.height()
            self.editor = Editor(self, file_path, x_pos+self.window_width, y_pos)

    def clear_all (self):
        self.dir_listbox.clear ()
        self.files_listbox.clear ()
        #self.files_info_listbox.clear()
        self.files_attributes_listbox.clear ()
        self.preview_textbox.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = App()
    sys.exit(app.exec_())
