# -*- coding: utf-8 -*-
import tkinter
from tkinter import filedialog
from tkinter.ttk import Treeview
from tkinter import *
import tkinter as tk
import os
import pickle
import tkinter.messagebox
from ListView import ListView
from operatemtputty import Operatemtputty
from extractlog import ExtractLog
from generateNetconfTcl import generateNetconfTcl
import time


class Gui_Mirror():
    def __init__(self, init_window_name):
        self.init_window_name = init_window_name
        self.logpath = ''
        self.tclpath = ''
        self.tempconfig = ''
        self.TMdata = []
        self.operatemtputty = Operatemtputty()

    def set_init_window(self):
        self.init_window_name.title("魔镜脚本开发系统")
        # self.init_window_name.state('zoomed') # 打开是不是全屏
        self.init_window_name.geometry('1068x681+260+100')
        self.init_window_name["bg"] = "Beige"
        # self.init_window_name.attributes("-alpha", 0.95)
        # 工具logo
        self.image_file = tk.PhotoImage(file='logo.png')  # 创建图片对象
        self.imgLabel = Label(self.init_window_name, image=self.image_file)  # 把图片整合到标签类中
        self.imgLabel.place(x=50,y=10,anchor='nw',)

        # self.canvas = tk.Canvas(self.init_window_name, width=400, height=135, bg='green')
        # image_file = tk.PhotoImage(file='logo.png')
        # image = self.canvas.create_image(200, 0, anchor='n', image=image_file)
        # self.canvas.pack(side='top')


        # 按钮
        self.button1 = Button(self.init_window_name, text="连接设备", background="lightblue", foreground='black', width=10,command=self.popwind_device).place(x=100,y=100,anchor='nw',)
        self.button2 = Button(self.init_window_name, text='连接测试仪', background="lightblue", foreground='black', width=10,command=self.popwind_Tm).place(x=100, y=180, anchor='nw')
        self.button3 = Button(self.init_window_name, text='HOST连接', background="lightblue", foreground='black', width=10).place(x=100, y=260, anchor='nw')
        self.button4 = Button(self.init_window_name, text=' 开始录制 ', background="lightblue", foreground='black', width=10, command=self.startest).place(x=100, y=340, anchor='nw')
        self.button5 = Button(self.init_window_name, text=' 结束录制 ', background="lightblue", foreground='black', width=10, command=self.endtest).place(x=100, y=420, anchor='nw')
        self.button5 = Button(self.init_window_name, text=' 生成脚本 ', background="lightblue", foreground='black', width=10, command=self.createtcl).place(x=100,
                                                                                                                                                      y=500,
                                                                                                                                                      anchor='nw')
        self.button6 = Button(self.init_window_name, text='log路径设置', background="lightblue", foreground='black', width=10,command=self.creat_log).place(x=350, y=20, anchor='nw')
        self.button7 = Button(self.init_window_name, text='生成路径设置', background="lightblue", foreground='black', width=10,command=self.creat_Tcl).place(x=550, y=20, anchor='nw')
        self.button8 = Button(self.init_window_name, text='保存', background="lightblue", foreground='black', width=5).place(x=700, y=135, anchor='nw')

        # 输出框
        self.logtext = Text(self.init_window_name, height=4, width=70)
        self.logtext.place(x=250, y=75, anchor='nw')
        self.tcltext = Text(self.init_window_name, height=25, width=70)
        self.tcltext.place(x=250, y=180, anchor='nw')
        self.showpath()
        self.writetext()

    def tree_sort_column(self,tree, col, reverse):  # Treeview、列名、排列方式
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        l.sort(reverse=reverse)  # 排序方式
        for index, (val, k) in enumerate(l):  # 根据排序后索引移动
            tree.move(k, '', index)
        tree.heading(col, command=lambda: self.tree_sort_column(tree, col, not reverse))

    def treeviewclick(self,event, tree):
        self.popwind1.clipboard_clear()
        strs = ""
        for item in tree.selection():
            item_text = tree.item(item, "values")
            strs += item_text[0] + "\n"  # 获取本行的第一列的数据
        self.popwind1.clipboard_append(strs)

    def creat_log(self):
        top_log = tkinter.Toplevel()
        top_log.title('路径选择')
        max_w, max_h = top_log.maxsize()
        top_log.geometry(f'600x50+{int((max_w - 600) / 2)}+{int((max_h - 400) / 2)}')  # 居中显示
        top_log["bg"] = "Beige"
        top_log.resizable(width=False, height=False)

        def selectPath():
            path_ = filedialog.askdirectory()  # 使用askdirectory()方法返回文件夹的路径
            if path_ == "":
                path_ = path.get()  # 当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
            else:
                path_ = path_.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
                path.set(path_)
            self.logpath = path_
            top_log.destroy()
            self.writetext()


        # os.chdir('./log')  # 设置默认路径

        def openPath():
            dir = os.path.dirname(path.get() + "\\")
            os.system('start ' + dir)
            top_log.destroy()
            # print(dir)

        path = tkinter.StringVar()
        path.set(self.logpath)

        tkinter.Label(top_log, text="目标路径:").grid(row=0, column=0)
        tkinter.Entry(top_log, textvariable=path, state="readonly").grid(row=0, column=1, ipadx=100)

        # e.insert(0,os.path.abspath("."))
        tkinter.Button(top_log, text="路径选择", background="lightblue", foreground='black', command=selectPath).grid(row=0, column=2)
        tkinter.Button(top_log, text="打开文件位置", background="lightblue", foreground='black', command=openPath).grid(row=0, column=3)
        top_log.mainloop()

    def creat_Tcl(self):
        creat_Tcl = tkinter.Toplevel()
        creat_Tcl.title('路径选择')
        max_w, max_h = creat_Tcl.maxsize()
        creat_Tcl.geometry(f'600x50+{int((max_w - 600) / 2)}+{int((max_h - 400) / 2)}')  # 居中显示
        creat_Tcl["bg"] = "Beige"
        creat_Tcl.resizable(width=False, height=False)

        def selectPath():
            path_ = filedialog.askdirectory()  # 使用askdirectory()方法返回文件夹的路径
            if path_ == "":
                path_ = path.get()  # 当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
            else:
                path_ = path_.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
                path.set(path_)
            self.tclpath = path_
            creat_Tcl.destroy()
            self.writetext()

        def openPath():
            dir = os.path.dirname(path.get() + "\\")
            os.system('start ' + dir)
            creat_Tcl.destroy()
            # print(dir)

        path = tkinter.StringVar()

        path.set(self.tclpath)

        tkinter.Label(creat_Tcl, text="目标路径:").grid(row=0, column=0)
        tkinter.Entry(creat_Tcl, textvariable=path, state="readonly").grid(row=0, column=1, ipadx=100)

        # e.insert(0,os.path.abspath("."))
        tkinter.Button(creat_Tcl, text="路径选择", background="lightblue", foreground='black', command=selectPath).grid(row=0, column=2)
        tkinter.Button(creat_Tcl, text="打开文件位置", background="lightblue", foreground='black', command=openPath).grid(row=0, column=3)
        creat_Tcl.mainloop()

    def comtcl(self):
        self.tempconfig = 1
        self.pop_end_wind.destroy()
        operator = Operatemtputty()
        operator.openmtputty()
        if self.TMdata:
            operator.protestmasterconfig()
        for device in self.selectdata:
            devicename = device[3] + ':' + device[4]
            operator.connetdevice(device)
            operator.extraputtyset(devicename)
            operator.setlogging(self.logpath + '\\' + device[1] + '.log')
            # operator.extraputtyset(devicename)
            # operator.setputtylog()
            # operator.setwindowtitle(devicename)
            operator.startrecording(self.init_window_name,devicename,self.tempconfig)
        tkinter.messagebox.showinfo(title='Hi', message='设置成功，请开始测试！')

    def netconftcl(self):
        self.tempconfig = 2
        self.pop_end_wind.destroy()
        operator = Operatemtputty()
        operator.openmtputty()
        if self.TMdata:
            operator.protestmasterconfig()
        for device in self.selectdata:
            devicename = device[3] + ':' + device[4]
            operator.connetdevice(device)
            operator.extraputtyset(devicename)
            operator.setlogging(self.logpath + '\\' + device[1] + '.log')
            # operator.extraputtyset(devicename)
            # operator.setputtylog()
            # operator.setwindowtitle(devicename)
            operator.startrecording(self.init_window_name,devicename,self.tempconfig)

        tkinter.messagebox.showinfo(title='Hi', message='设置成功，请开始测试！')

    def select_popwind(self):
        self.pop_end_wind = tkinter.Toplevel(self.init_window_name)
        self.pop_end_wind.title("选择脚本类型")
        self.pop_end_wind.geometry('300x200+650+380')
        self.pop_end_wind["bg"] = "Ivory"
        self.pop_end_wind.resizable(False, False)
        funbutton = tk.Button(self.pop_end_wind, text="功能脚本", background="lightblue", foreground='black', width=10,command=self.comtcl)
        funbutton.pack(side=tk.LEFT, expand=1)

        netbutton = tk.Button(self.pop_end_wind, text="netconf脚本", background="lightblue", foreground='black', width=10,command=self.netconftcl)
        netbutton.pack(side=tk.LEFT, expand=1)

    def popwind_device(self):

        def onSumbitClick():
            name = str(nameval.get())
            ip = str(ipval.get())
            port = str(portval.get())
            username = str(usernameval.get())
            passworld = str(passworldval.get())
            type = str(typeeddl.get())
            connetinfo = {
                'name':name,
                'ip': ip,
                'port': port,
                'username': username,
                'passworld': passworld,
                'type': type,
            }
            # print(type)
            with open('usrs_info.pkl', 'rb+') as usr_file:
                with open('usrs_info_bak.pkl', 'wb+') as usr_file_bak:
                    pickle.dump(connetinfo, usr_file_bak)
                    while True:
                        try:
                            usr_info_data = pickle.load(usr_file)
                            # print(usr_info_data)
                            if usr_info_data.get('name') == name:
                                continue
                            else:
                                pickle.dump(usr_info_data, usr_file_bak)
                        except EOFError:
                            break
                usr_file.close()
                usr_file_bak.close()

            with open('usrs_info.pkl', 'wb+') as usr_file:
                with open('usrs_info_bak.pkl', 'rb+') as usr_file_bak:
                    while True:
                        try:
                            usr_info_data_bak = pickle.load(usr_file_bak)
                            pickle.dump(usr_info_data_bak, usr_file)
                        except EOFError:
                            break
                    usr_file.close()
                    usr_file_bak.close()
            tkinter.messagebox.showinfo(title='Hi', message='保存成功！')
            self.popwind1.destroy()
            self.popwind_device()
            # reflshdata()

        def addata():
            with open('usrs_info.pkl', 'rb+') as usr_file:
                userdata = []
                while True:
                    try:
                        usr_info_data = pickle.load(usr_file)
                        userdata.append(usr_info_data)
                    except EOFError:
                        break
            usr_file.close()
            return userdata

        # 添加数据
        def reflshdata():
            userdata = addata()
            if userdata:
                for user in userdata:
                    row = [user.get('name'), user.get('type'), user.get('ip'), user.get('port')]
                    lv.add_row(False, row)

        def connect():
            self.selectdata = lv.get_row_values_by_allselectdata()
            self.popwind1.destroy()
            # print(self.selectdata)

        # 定义弹窗
        self.popwind1 = tkinter.Toplevel(self.init_window_name)
        # self.popwind1 = tk.Tk()
        self.popwind1.title("设备连接信息")
        self.popwind1.geometry('750x600+386+163')
        self.popwind1["bg"] = "Ivory"

        lv = ListView(self.popwind1, x=100, y=25, height=344, width=550)
        # lv = ListView(self.popwind1, x=100, y=50, width=800, height=500)
        lv.add_column('名称', 120)
        lv.add_column('类型', 120)
        lv.add_column('地址', 120)
        lv.add_column('端口', 120)
        lv.set_rows_height_fontsize(30, 10)
        lv.set_head_font('微软雅黑', 10)
        lv.create_listview()

        tkinter.Label(self.popwind1, text='名称:').place(x=50, y=400, anchor='nw')
        tkinter.Label(self.popwind1, text='类型:').place(x=500, y=400, anchor='nw')
        tkinter.Label(self.popwind1, text='地址:').place(x=50, y=450, anchor='nw')
        tkinter.Label(self.popwind1, text='端口:').place(x=500, y=450, anchor='nw')
        tkinter.Label(self.popwind1, text='用户:').place(x=50, y=500, anchor='nw')
        tkinter.Label(self.popwind1, text='密码:').place(x=500, y=500, anchor='nw')

        # 将输入的注册名赋值给变量
        nameval = tkinter.StringVar()
        nameval.set('DUT1')
        ipval = tkinter.StringVar()
        portval = tkinter.StringVar()
        portval.set('23')
        usernameval = tkinter.StringVar()
        passworldval = tkinter.StringVar()

        nameentry = tkinter.Entry(self.popwind1, highlightbackground='white', textvariable=nameval)
        nameentry.place(x=100, y=400)
        ipentry = tkinter.Entry(self.popwind1, highlightbackground='white', textvariable=ipval)
        ipentry.place(x=100, y=450)
        usernameentry = tkinter.Entry(self.popwind1, highlightbackground='white', textvariable=usernameval)
        usernameentry.place(x=100, y=500)
        typeeddl = tkinter.ttk.Combobox(self.popwind1, state='readonly', width=17)
        # typeeddl = tkinter.ttk.Combobox(self.popwind1, textvariable=typeval, state='readonly', width=17)
        typeeddl['value'] = ("telnet", "ssh")
        typeeddl.current(0)
        typeeddl.pack(side=tkinter.RIGHT, padx=1, pady=1)
        typeeddl.place(x=550, y=400)
        # typeentry = tkinter.Entry(self.popwind1, highlightbackground='white', textvariable=typeval)
        # typeentry.place(x=550, y=300)
        portentry = tkinter.Entry(self.popwind1, highlightbackground='white', textvariable=portval)
        portentry.place(x=550, y=450)
        passworldentry = tkinter.Entry(self.popwind1, highlightbackground='white', textvariable=passworldval)
        passworldentry.place(x=550, y=500)
        tkinter.Button(self.popwind1, text='连接', width=10, command=connect).place(x=400, y=550, anchor='nw')
        tkinter.Button(self.popwind1, text='保存', width=10, command=onSumbitClick).place(x=500, y=550, anchor='nw')
        tkinter.Button(self.popwind1, text='取消', width=10, command=self.popwind1.destroy).place(x=600, y=550, anchor='nw')
        reflshdata()

    def popwind_Tm(self):

        def onSumbitClick():
            name = str(nameval.get())
            ip = str(ipval.get())
            port = str(portval.get())
            username = str(usernameval.get())
            passworld = str(passworldval.get())
            type = str(typeeddl.get())
            connetinfo = {
                'name': name,
                'ip': ip,
                'port': port,
                'username': username,
                'passworld': passworld,
                'type': type,
            }
            # print(type)
            with open('TM_info.pkl', 'rb+') as usr_file:
                with open('TM_info_bak.pkl', 'wb+') as usr_file_bak:
                    pickle.dump(connetinfo, usr_file_bak)
                    while True:
                        try:
                            usr_info_data = pickle.load(usr_file)
                            # print(usr_info_data)
                            if usr_info_data.get('name') == name:
                                continue
                            else:
                                pickle.dump(usr_info_data, usr_file_bak)
                        except EOFError:
                            break
                usr_file.close()
                usr_file_bak.close()

            with open('TM_info.pkl', 'wb+') as usr_file:
                with open('TM_info_bak.pkl', 'rb+') as usr_file_bak:
                    while True:
                        try:
                            usr_info_data_bak = pickle.load(usr_file_bak)
                            pickle.dump(usr_info_data_bak, usr_file)
                        except EOFError:
                            break
                    usr_file.close()
                    usr_file_bak.close()
            tkinter.messagebox.showinfo(title='Hi', message='保存成功！')
            self.popwind2.destroy()
            self.popwind_Tm()
            # reflshdata()

        def addata():
            with open('Tm_info.pkl', 'rb+') as usr_file:
                userdata = []
                while True:
                    try:
                        usr_info_data = pickle.load(usr_file)
                        userdata.append(usr_info_data)
                    except EOFError:
                        break
            usr_file.close()
            return userdata

        # 添加数据
        def reflshdata():
            userdata = addata()
            if userdata:
                for user in userdata:
                    row = [user.get('name'), user.get('type'), user.get('ip'), user.get('port')]
                    lv.add_row(False, row)

        def connect():
            self.TMdata = lv.get_row_values_by_allselectdata()
            self.popwind2.destroy()
            # print(self.selectdata)

        # 定义弹窗
        self.popwind2 = tkinter.Toplevel(self.init_window_name)
        # self.popwind2 = tk.Tk()
        self.popwind2.title("设备连接信息")
        self.popwind2.geometry('750x600+386+163')
        self.popwind2["bg"] = "Ivory"

        lv = ListView(self.popwind2, x=100, y=25, height=344, width=550)
        # lv = ListView(self.popwind2, x=100, y=50, width=800, height=500)
        lv.add_column('名称', 120)
        lv.add_column('类型', 120)
        lv.add_column('地址', 120)
        lv.add_column('端口', 120)
        lv.set_rows_height_fontsize(30, 10)
        lv.set_head_font('微软雅黑', 10)
        lv.create_listview()

        tkinter.Label(self.popwind2, text='名称:').place(x=50, y=400, anchor='nw')
        tkinter.Label(self.popwind2, text='类型:').place(x=500, y=400, anchor='nw')
        tkinter.Label(self.popwind2, text='地址:').place(x=50, y=450, anchor='nw')
        tkinter.Label(self.popwind2, text='端口:').place(x=500, y=450, anchor='nw')
        tkinter.Label(self.popwind2, text='用户:').place(x=50, y=500, anchor='nw')
        tkinter.Label(self.popwind2, text='密码:').place(x=500, y=500, anchor='nw')

        # 将输入的注册名赋值给变量
        nameval = tkinter.StringVar()
        nameval.set('TM1')
        ipval = tkinter.StringVar()
        portval = tkinter.StringVar()
        portval.set('22')
        usernameval = tkinter.StringVar()
        passworldval = tkinter.StringVar()

        nameentry = tkinter.Entry(self.popwind2, highlightbackground='white', textvariable=nameval)
        nameentry.place(x=100, y=400)
        ipentry = tkinter.Entry(self.popwind2, highlightbackground='white', textvariable=ipval)
        ipentry.place(x=100, y=450)
        usernameentry = tkinter.Entry(self.popwind2, highlightbackground='white', textvariable=usernameval)
        usernameentry.place(x=100, y=500)
        typeeddl = tkinter.ttk.Combobox(self.popwind2, state='readonly', width=17)
        # typeeddl = tkinter.ttk.Combobox(self.popwind2, textvariable=typeval, state='readonly', width=17)
        typeeddl['value'] = ("telnet", "ssh")
        typeeddl.current(1)
        typeeddl.pack(side=tkinter.RIGHT, padx=1, pady=1)
        typeeddl.place(x=550, y=400)
        # typeentry = tkinter.Entry(self.popwind2, highlightbackground='white', textvariable=typeval)
        # typeentry.place(x=550, y=300)
        portentry = tkinter.Entry(self.popwind2, highlightbackground='white', textvariable=portval)
        portentry.place(x=550, y=450)
        passworldentry = tkinter.Entry(self.popwind2, highlightbackground='white', textvariable=passworldval)
        passworldentry.place(x=550, y=500)
        tkinter.Button(self.popwind2, text='连接', width=10, command=connect).place(x=400, y=550, anchor='nw')
        tkinter.Button(self.popwind2, text='保存', width=10, command=onSumbitClick).place(x=500, y=550, anchor='nw')
        tkinter.Button(self.popwind2, text='取消', width=10, command=self.popwind2.destroy).place(x=600, y=550, anchor='nw')
        reflshdata()

    def showpath(self):
        if not os.path.exists('./log'):
            os.mkdir('./log')
        if not os.path.exists('./result'):
            os.mkdir('./result')
        path = os.path.abspath(".")
        # path.set(os.path.abspath("."))
        # ss = path.get()
        self.logpath = path + '\\devicelog'
        self.tclpath = path + '\\result'

    def writetext(self):
        self.logtext.delete(0.0, END)
        self.logtext.insert(tk.INSERT, 'Log保存路径：' + self.logpath)
        self.logtext.insert(tk.INSERT, '\n')
        self.logtext.insert(tk.INSERT, 'Tcl保存路径：' + self.tclpath)

    def open_file(self, file_path):
        # file_path = filedialog.askopenfilename(title=u'选择⽂件', initialdir=(os.path.expanduser(':C/')))
        # print('打开⽂件：', file_path)
        self.tcltext.delete(0.0, END)
        if file_path is not None:
            with open(file=file_path, mode='r+', encoding='gbk') as file:
                file_text = file.read()
                self.tcltext.insert('insert', file_text)

    def save_file(self, file_path):
        file_path = filedialog.asksaveasfilename(title=u'保存⽂件')
        print('保存⽂件：', file_path)
        file_text = self.tcltext.get('1.0', tk.END)
        if file_path is not None:
            with open(file=file_path, mode='a+', encoding='gbk') as file:
                file.write(file_text)

    def startest(self):
        self.select_popwind()


    def endtest(self):
        filelist = []
        operator = Operatemtputty()
        resultename = './result/' + time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()) + '.tcl'
        for device in self.selectdata:
            filelist.append(device[1] + '.log')
            devicename = device[3] + ':' + device[4]
            operator.stoprecording(self.init_window_name,devicename)
        operator.copyfile(self.logpath, './log', filelist)
        if self.tempconfig == 1:
            extractlog = ExtractLog('./log',resultename)
            extractlog.creattcl()
        elif self.tempconfig == 2:
            generate = generateNetconfTcl('./log',resultename)
            generate.creattcl()

        self.open_file(resultename)
        tkinter.messagebox.showinfo(title='Hi', message='脚本生成成功，请查看！')

    def createtcl(self):
        self.pop_select_wind = tkinter.Toplevel(self.init_window_name)
        self.pop_select_wind.title("选择脚本类型")
        self.pop_select_wind.geometry('300x200+650+380')
        self.pop_select_wind["bg"] = "Ivory"
        self.pop_select_wind.resizable(False, False)
        funbutton = tk.Button(self.pop_select_wind, text="功能脚本", background="lightblue", foreground='black', width=10, command=self.createcomtcl)
        funbutton.pack(side=tk.LEFT, expand=1)

        netbutton = tk.Button(self.pop_select_wind, text="netconf脚本", background="lightblue", foreground='black', width=10, command=self.createnetconftcl)
        netbutton.pack(side=tk.LEFT, expand=1)

    def createcomtcl(self):
        self.pop_select_wind.destroy()
        resultename = './result/' + time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()) + '.tcl'
        create = ExtractLog('./log/',resultename)
        create.creattcl()
        self.open_file(resultename)

    def createnetconftcl(self):
        self.pop_select_wind.destroy()
        resultename = './result/' + time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()) + '.tcl'
        generate = generateNetconfTcl('./log/', resultename)
        generate.creattcl()
        self.open_file(resultename)



if __name__ == '__main__':
    init_window = tk.Tk()  # 实例化出一个父窗口
    mirror_gui = Gui_Mirror(init_window)

    mirror_gui.set_init_window()

    init_window.mainloop()





