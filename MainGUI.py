import tkinter as tk
from tkinter import *
from tkinter.filedialog import askdirectory
import os
from PIL import Image, ImageTk

class MainGUI:
	def __init__(self, master):
		self.pointer = 0
		self.img_dir = None
	
		frame = Frame(master)
		root.state('zoomed')
		frame.pack()
		
		self.next_button = Button(root, text='Next image', command=self.next_img)
		self.next_button.pack(side=RIGHT)
		
		self.previous_button = Button(root, text='Previous image', command=self.previous_img)
		self.previous_button.pack(side=LEFT)
	
	def set_img_dir(self):
		img_dir = askdirectory(parent=root, initialdir="D:/Temp/", title='Choose folder')
		os.chdir(img_dir)
		img_dir=(os.listdir(img_dir))
		self.img_dir = sorted(img_dir, key=str)
		return
	
	def display_image(self):
		print("in display_image", type(self.img_dir))
		photo = ImageTk.PhotoImage(Image.open(self.img_dir[self.pointer]))
		panel = tk.Label(root, image=photo)
		panel.image = photo # keep a reference!
		panel.pack()
		return
		
	def next_img(self):
		# increment pointer, remove previous image, 
		# display next image in the image directory
		self.pointer += 1
		self.display_image()
		return
	
	def previous_img():
		# drecrement pointer, remove previouos image,
		# display previous image in the image directory
		pass 

if __name__ == '__main__':
	root = tk.Tk()
	m=MainGUI(root)
	m.set_img_dir()
	m.display_image()
	root.mainloop()
	

