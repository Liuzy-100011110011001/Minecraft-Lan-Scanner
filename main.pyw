import tkinter as tk
from tkinter import ttk,messagebox
import threading
import socket
import struct
import time
import re
from mcstatus import JavaServer
from PIL import ImageTk
import lansearch
import fakeplayer
WIDTH=800
HEIGHT=600
ICON_PATH='./resource/icon.ico'
class Main:
    def __init__(self):
        self.root=tk.Tk()
        self.root.title("Minecraft局域网扫描")
        self.root.iconphoto(True,ImageTk.PhotoImage(file=ICON_PATH))
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{int((self.root.winfo_screenwidth()-WIDTH)/2)}+{int((self.root.winfo_screenheight()-HEIGHT)/2)}")
        self.scanning=False

        self.menu=tk.Menu(self.root)
        option_menu=tk.Menu(self.menu,tearoff=0)
        self.menu.add_cascade(label="操作", menu=option_menu)
        option_menu.add_command(label="查看服务器详细信息",command=self.show_detailInfo)
        self.menu.add_command(label="帮助",command=self.show_helpInfo)
        self.menu.add_command(label="关于",command=self.show_aboutInfo)
        
        top=ttk.Frame(self.root)
        top.pack(fill='x',padx=5,pady=5)
        
        self.btn=ttk.Button(top,text="开始扫描",command=self.start_scan)
        self.btn.pack(side='left',padx=5)
        
        self.status=tk.Label(top,text="就绪")
        self.status.pack(side='left',padx=10)
        
        cols=('ip','port','motd')
        self.tree=ttk.Treeview(self.root,columns=cols,show='headings')
        self.tree.heading('ip',text='IP')
        self.tree.heading('port',text='端口')
        self.tree.heading('motd',text='MOTD')
        self.tree.column('ip',width=150)
        self.tree.column('port',width=80)
        self.tree.column('motd',width=300)
        self.tree.pack(fill='both',expand=True,padx=5,pady=5)
        self.tree.bind('<Double-1>',self.show_detail)

        self.root.config(menu=self.menu)
        self.root.mainloop()
    def show_helpInfo(self):
        messagebox.showinfo("帮助","懒得写，自己琢磨去吧。")
    def show_aboutInfo(self):
        messagebox.showinfo("关于","当前应用程序版本，V1.0。\n开发者：n_lzy（Mc游戏ID，正版）")
    def show_detailInfo(self):
        selected_items=self.tree.selection()
        if len(selected_items)==0:
            messagebox.showerror("错误","你必须选中一个栏目，当前未选中。")
            return
        if len(selected_items)>1:
            messagebox.showerror("错误",f"你只能选中一个栏目，当前选中{len(selected_items)}个。")
            return
        values=self.tree.item(selected_items[0],'values')
        self.show_detail(values)
    def start_scan(self):
        if self.scanning:
            return
        self.scanning=True
        self.btn.config(state='disabled',text='扫描中...')
        self.status.config(text='正在扫描局域网...')
        for i in self.tree.get_children():
            self.tree.delete(i)
        t=threading.Thread(target=self.scan_thread)
        t.start()
    def scan_thread(self):
        servers=lansearch.scan_lan()
        self.root.after(0,self.scan_done,servers)
    def scan_done(self,servers):
        self.scanning=False
        self.btn.config(state='normal',text='开始扫描')
        if servers:
            self.status.config(text='发现 %d 个服务器' % len(servers))
            for s in servers:
                self.tree.insert('','end',values=(s['ip'],s['port'],s['motd']))
        else:
            self.status.config(text='未找到服务器')
            messagebox.showinfo('完成','局域网内没有发现 Minecraft 服务器。')
    def show_detail(self,event):
        sel=self.tree.selection()
        if not sel:
            return
        item=sel[0]
        values=self.tree.item(item,'values')
        ip=values[0]
        port=int(values[1])
        motd=values[2]
        win=tk.Toplevel(self.root)
        win.title(ip + ':' + str(port))
        win.geometry('400x400')
        tk.Label(win,text='IP: ' + ip).pack(anchor='w',padx=10,pady=2)
        tk.Label(win,text='端口: ' + str(port)).pack(anchor='w',padx=10,pady=2)
        tk.Label(win,text='MOTD: ' + motd,wraplength=350).pack(anchor='w',padx=10,pady=2)
        tk.Label(win,text='玩家列表:').pack(anchor='w',padx=10,pady=5)
        self.player_text=tk.Text(win,height=8)
        self.player_text.pack(fill='both',expand=True,padx=10,pady=5)
        self.player_status=tk.Label(win,text='查询中...')
        self.player_status.pack()
        t=threading.Thread(target=self.query_server,args=(win,ip,port))
        t.start()
    def query_server(self,win,ip,port):
        try:
            info=lansearch.server_info(ip,port,timeout=10)
            self.root.after(0,self.update_detail,info['online'],info['max'],info['latency'],info['players'])
        except Exception as e:
            te=e
            self.root.after(0,lambda :self.player_status.config(text=f'查询失败: {te}'))
    def update_detail(self,online,maxp,latency,players):
        self.player_status.config(text=f'在线: {online}/{maxp}  延迟: {latency}ms')
        self.player_text.delete(1.0,'end')
        if players:
            self.player_text.insert('end','\n'.join(players))
        else:
            self.player_text.insert('end','无在线玩家或服务器玩家名称保护')
if __name__ == '__main__':
    try:
        Main()
    except Exception as e:
        print('程序错误：'+str(e))
