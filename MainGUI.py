import tkinter as tk
from tkinter import *
from tkinter.filedialog import askdirectory
import os
from PIL import Image, ImageTk

class MainGUI:
	def __init__(self, master):
		frame = Frame(master)
		root.state('zoomed')
		frame.pack()
		
		self.next_button = Button(root, text='Next image', command=MainGUI.next_img)
		self.next_button.pack(side=RIGHT)
		
		self.previous_button = Button(root, text='Previous image', command=MainGUI.previous_img)
		self.previous_button.pack(side=LEFT)

	def change_dir():
		img_dir = askdirectory(parent=root, initialdir="D:/Temp/", title='Choose folder')
		os.chdir(img_dir)
		imgs = iter(os.listdir(img_dir))
	def next_img():
		img_label.img = tk.PhotoImage(file=next(imgs))
		img_label.config(image=img_label.img)
	def previous_img():
		pass 

if __name__ == '__main__':
	root = tk.Tk()
	w = MainGUI(root)
	root.mainloop()

