import Tkinter
from gui.tck_main_app import App

if __name__ == "__main__":
    root = Tkinter.Tk()
    root.geometry("900x700")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    app = App(master=root)
    app.mainloop()