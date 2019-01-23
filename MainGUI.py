import tkinter
from tkinter import *
from matplotlib import cm
from PIL import Image, ImageTk
from numpy import linspace, empty
from os import chdir, listdir, path
from matplotlib import pyplot as plt
from cv2 import imread, IMREAD_GRAYSCALE
#for saving figure w/o extra whitespace
from matplotlib.pyplot import gca
import matplotlib.ticker as tick
import filter_expression

# this script holds the GUI, it also contains:
# - function for overlaying the template image with the expression image/images
# - the function that superimposes all the currenly selected expression maps (compare_maps())

class MainGUI:
	def __init__(self, master):
		filter_expression.main()
		self.master=master
		frame = Frame(self.master)
		
		self.pointer = 0 # to track image number
		self.origin_dir = path.dirname(path.realpath(__file__))
		self.template_dir = self.origin_dir + "\\template images"
		self.maps_dir = self.origin_dir + "\expression maps"
		self.current_selection = [] # for genes
		
		self.template_filenames = self.get_filenames(self.template_dir)
		self.gene_names = self.get_filenames(self.maps_dir)
		
		self.previous_button = Button(root, bg="#42f4ce", text="Previous\nImage", font=('Helvetica', '12','bold'), height=28, width=8, command=self.previous_img)
		self.previous_button.grid(row=0, column=0, sticky=W)
		
		self.next_button = Button(root, bg="#42f4ce", font=('Helvetica', '12','bold'), height=28, width=8, text="Next\nImage", command=self.next_img)
		self.next_button.grid(row=0, column=2, sticky=E)
	
		self.img_view= tkinter.Label(root, image = None )
		self.img_view.grid(row=0, column=1, sticky=N)
		
		# for selecting genes to visualize
		self.okay_button = Button(root, bg="green", font=('Helvetica', '12','bold'), height=3, width=5, text="Go", command=self.set_current_selection)
		self.okay_button.grid(row=2, column=1, sticky=SE)
		
		# for selecting genes to visualize
		self.list_box = Listbox(self.master, selectmode='multiple', height = 4, width = 81)
		for gene_name in self.gene_names:
			self.list_box.insert(END, gene_name)
		self.list_box.grid(row=2,column =1,sticky=SW)
		
		self.img_tracker = Text(self.master, bg="white", font=('Helvetica', '12','bold'), height=2, width=15)
		self.img_tracker.insert(INSERT, "Image "+ str(self.pointer)+" of " + str(len(self.template_dir)))
		self.img_tracker.tag_configure("center", justify='center')
		self.img_tracker.tag_add("center", "1.0", "end")
		self.img_tracker.grid(row=1, column =1, sticky=S)
		
		self.display_image()
		
	def get_filenames(self,dir):
		chdir(dir)
		return listdir(dir)
		
	def display_image(self): #takes RGBA PIL.Image
		# if the user has no genes selected, display the template
		# otherwise, overlay the expression map with the template
		if len(self.current_selection) == 0:
			img = self.get_template_img()
		else:
			img = self.overlay_expression()
		img=img.resize((550,550), Image.ANTIALIAS)
		
		# remove previous image, put in new one, keeping a refrence
		self.img_view.config(image="")
		img = ImageTk.PhotoImage(img)
		self.img_view.config(image=img)
		self.img_view.image = img #keep a refrence!
		self.img_view.grid(row=0, column=1)
		# update pointer count on display
		self.set_img_tracker()
		return
		
	def get_template_img(self):
		chdir(self.template_dir)
		img=Image.open(self.template_filenames[self.pointer])
		return img
		
	def overlay_expression(self):
		# get a list of the currrent gene maps selected
		current_maps = self.get_current_maps()
		# if there is one gene map selcted, make that the expression_img
		if len(current_maps) == 1:
			expression_img = current_maps[0]
			expression_img = Image.fromarray(expression_img)
		else:
			# otherwise superimpose all the maps
			expression_img = self.compare_maps(current_maps)
		
		# turn white pixels into clear using alpha channel
		expression_img = expression_img.convert("RGBA")
		expression_img= self.white_to_alpha(expression_img)
		
		# get template image and convert to match mode of expression image
		template_img = self.get_template_img()
		template_img = template_img.convert("RGBA")
		# paste images together
		img = Image.alpha_composite(template_img, expression_img)
		return img
		
	def get_current_maps(self): 
		# makes a list of ndarrays for all genes selected at the current pointer
		current_maps = []
		for gene in self.current_selection:
			gene_dir = self.maps_dir + "\~" + gene
			gene_dir = gene_dir.replace("~", "")
			filenames = self.get_filenames(gene_dir)
			img = imread(filenames[self.pointer], IMREAD_GRAYSCALE)
			current_maps.append(img)
		return current_maps
		
	def compare_maps(self, current_maps):
		summation_expression_map = empty(([current_maps[0].shape[0], current_maps[0].shape[1]]))
		N=(2**(len(current_maps)))
		
		# loop through all the pixels in new image
		for y in range(summation_expression_map.shape[0]):
			for x in range (summation_expression_map.shape[1]):
				values = []
				pixel_summation = 0
				# store the current pixel's value for each map being displayed
				for img in current_maps:
					values.append(img[y][x])
				# get a pixel summation number based on the combination of pixel values in the list
				for k in range(0,(len(current_maps))):
					pixel_summation += ((N-k) * (values[k]/255))
				summation_expression_map[y][x] = pixel_summation
		
		# add color map to summation_expression_map, each unique pixel value gets a different color
		plt.imshow(summation_expression_map, cmap = self.discrete_cmap(N,"nipy_spectral"))
		
		# temporarily save matplotlib img (FIX THIS LATER) 
		gca().set_axis_off()
		gca().xaxis.set_major_locator(tick.NullLocator())
		gca().yaxis.set_major_locator(tick.NullLocator())
		chdir(self.origin_dir + "\\temp")
		plt.savefig("temp.png", bbox_inches='tight', pad_inches=0) 
		# open same image as PIL.Image
		img = Image.open("temp.png")
		return img
		
	def discrete_cmap(self, N, base_cmap=None):
		# make a new colormap based on N, the number of possible combinations of expression
		base = plt.cm.get_cmap(base_cmap)
		# evely spaced apart
		color_list = base(linspace(0, 1, N))
		# force no expression to be white
		color_list[N-1] = (1,1,1,1)
		cmap_name = base.name + str(N)	
		return base.from_list(cmap_name, color_list, N)
		
	def white_to_alpha(self,img):
		# set all white pixels to be clear
		pixel_data = img.getdata()
		new_data = []
		for item in pixel_data:
			if item[0] == 255 and item[1] == 255 and item[2] == 255:
				new_data.append((255, 255, 255, 0))
			else:
				new_data.append(item)

		img.putdata(new_data)
		return img
		
	def next_img(self):
		self.pointer += 1
		if self.pointer > len(self.template_filenames)-1:
			self.pointer = 0
		self.display_image()
		return
	
	def previous_img(self):
		self.pointer -= 1
		if self.pointer < 0:
			self.pointer = len(self.template_filenames)-1
		self.display_image()
		return

	def set_img_tracker(self):
		self.img_tracker.delete('1.0', END)
		self.img_tracker.insert(INSERT, "Image "+ str(self.pointer+1)+" of " + str(len(self.template_filenames)))
		self.img_tracker.tag_add("center", "1.0", "end")
		self.img_tracker.grid(row=1, column =1, sticky=S)
		return
		
	def set_current_selection(self): # current selection of genes
		self.current_selection = [self.list_box.get(idx) for idx in self.list_box.curselection()]
		self.display_image()
		return
	
if __name__ == '__main__':
	root = tkinter.Tk()
	m=MainGUI(root)
	root.mainloop()
	

