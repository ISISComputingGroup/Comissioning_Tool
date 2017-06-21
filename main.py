import Tkinter
from gui.tck_main_app import App

if __name__ == "__main__":
    root = Tkinter.Tk()
    root.geometry("1000x800")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.wm_title("Motion Tester")
    root.iconbitmap(default='gear.ico')
    app = App(master=root)
    app.mainloop()