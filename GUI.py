from threading import Thread
from tkinter import *
from tkinter.ttk import Treeview, Progressbar
import webbrowser
import core


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title('Nexus Forgotten Tracked Mods')
        self.selected_game_val = StringVar()
        self.geometry("640x480")
        self.middle_frame = Frame(self, width= 400, height= 30)
        self.bottom_frame = Frame(self)
        cols = ['mod_id', 'mod_url', 'mod_name']
        self.tv = Treeview(self.bottom_frame, columns=cols, show="headings")
        self.progress_bar = Progressbar(self.middle_frame, orient="horizontal", mode="indeterminate", length=100)
        self.create_widgets()

    def create_widgets(self):
        top_frame = Frame(self)
        top_frame.pack(pady=10)
        self.middle_frame.pack(pady=10)
        self.bottom_frame.pack(fill="both", expand=True)

        selected_game_label = Label(top_frame, text="Selected game:")
        selected_game_label.pack(side="left")
        self.selected_game_val.set(core.get_game_name())
        selected_game_value = Label(top_frame, textvariable=self.selected_game_val, bg="white")
        selected_game_value.pack(side="left", padx=10)
        change_game_btn = Button(top_frame, text="Change game", command=Dialog)
        change_game_btn.pack(padx=20)

        list_mods_btn = Button(self.middle_frame, text="List mods not downloaded yet",
                               command=self.load_nondownloaded_mods)
        #list_mods_btn.pack(side="left", anchor="center", padx=10)
        list_mods_btn.place(relx=.5, rely=.5, anchor='c')

        self.create_treeview()

    def create_treeview(self):
        tv_scrollbar = Scrollbar(self.bottom_frame, orient="vertical")

        self.tv.heading('mod_id', text="ID")
        self.tv.heading('mod_url', text="URL")
        self.tv.heading('mod_name', text="Mod Name")
        self.tv.column('mod_id', width=5)
        self.tv.column('mod_url', width=400)
        self.tv.column('mod_name', width=100)

        self.tv.configure(yscroll=tv_scrollbar.set)
        self.load_nondownloaded_mods()

        self.tv.bind('<<TreeviewSelect>>', self.tv_on_select_item)
        self.tv.pack(side="left", fill="both", expand=True)
        tv_scrollbar.config(command=self.tv.yview)
        tv_scrollbar.pack(side="right", fill="y")

    def tv_on_select_item(self, event):
        item = self.tv.focus()
        url = self.tv.item(item)['values'][1]
        webbrowser.open_new_tab(url)
        self.update_tv_item()

    def update_tv_item(self):
        item = self.tv.focus()
        old_values = self.tv.item(item)['values']
        mod_id = self.tv.item(item)['values'][0]
        data = core.get_mod_data(mod_id)
        try:
            new_values = [old_values[0], old_values[1], data['name']]
        except KeyError:
            new_values = [old_values[0], old_values[1], 'DELETED']
        self.tv.item(item, values=new_values)

    def load_nondownloaded_mods(self):
        #self.progress_bar.pack(side="right", anchor='n',fill='both')
        self.progress_bar.place(relx=1, rely=.5, anchor='e')
        self.progress_bar.start()
        download_thread = AsyncDownload()
        download_thread.start()
        self.monitor(download_thread)

    def monitor(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.monitor(thread))
        else:
            for mod in thread.mod_list:
                self.tv.insert('', END, values=mod)
            self.progress_bar.stop()
            self.progress_bar.place_forget()


class Dialog(Toplevel):

    def __init__(self, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        self.list_frame = Frame(self)
        self.search_frame = Frame(self)
        self.scrollbar = Scrollbar(self.list_frame, orient="vertical")
        self.lb = Listbox(self.list_frame, width=50, height=20, yscrollcommand=self.scrollbar.set)
        self.search_label = Label(self.search_frame, text="Search:")
        self.search_var = StringVar()
        self.search_box = Entry(self.search_frame, textvariable=self.search_var, width=30)
        self.grab_set()
        self.create_widgets()

    def create_widgets(self):
        self.list_frame.pack()
        self.search_frame.pack()
        self.lb.bind('<<ListboxSelect>>', self.change_game)
        self.lb.insert(END, *core.domains_to_names.values())
        self.lb.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.lb.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.search_label.pack(side="left")
        self.search_box.pack(side="left")
        self.search_var.trace("w", self.search)

    def change_game(self, *args):
        if self.lb.size() == 0:
            return
        index = self.lb.curselection()[0]
        item = self.lb.get(index)
        core.change_game_domain(item)
        app.selected_game_val.set(core.get_game_name())
        for item in app.tv.get_children():
            app.tv.delete(item)
        self.destroy()

    def search(self, *args):
        pattern = self.search_var.get().casefold()
        choices = [x for x in core.domains_to_names.values() if pattern in str(x).casefold()]
        self.lb.delete(0, "end")
        self.lb.insert("end", *choices)

    def fill_listbox(self, ld):
        for item in ld:
            self.lb.insert(END, item)


class AsyncDownload(Thread):
    def __init__(self):
        super().__init__()
        self.mod_list = None

    def run(self):
        self.mod_list = core.get_non_downloaded_mods()


app = App()
app.mainloop()
