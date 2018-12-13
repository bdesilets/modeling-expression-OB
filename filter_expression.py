from PIL import Image
from numpy import empty
from itertools import product
from os import chdir, listdir, path, makedirs
from cv2 import imread, cvtColor, IMREAD_COLOR, COLOR_BGR2RGB

# This script detects & filters the gene expression of new RGB 
# ISH image sets added to the ABA image directory

# variables for expression detection
THRESHOLD_R = 180 
THRESHOLD_G = 150
THRESHOLD_B = 255
# variables for filetering expression
N_RADIUS = 4
MIN_EXPRESSION_DENSITY = (((N_RADIUS*2)+1)**2)*.40


def main():
	# store directories of origin, expression maps and the ABA's ISH images
	origin_dir = path.dirname(path.realpath(__file__))
	map_dir = origin_dir + "\expression maps"
	ABA_dir = origin_dir + "\ABA images" 
	
	# check for new gene sets in ABA images
	ABA_gene_set = set(get_filenames(ABA_dir))
	map_gene_set = set(get_filenames(map_dir))
	new_genes = list(ABA_gene_set - map_gene_set)
	
	# if there are new gene sets in the ABA gene folder:
		# detect and filter their expression
	if len(new_genes) != 0:
		for gene in new_genes:
			print("New genes to detect and filter expression: ")
			print (new_genes)
			# store the dir for the new gene
			gene_dir = "\~" + gene
			gene_dir = gene_dir.replace("~", "")
			# in map_dir, create a new folder for the gene
			chdir(map_dir)
			makedirs(map_dir + gene_dir)
			# make a list of image filenames within the gene from ABA images
			img_filenames = get_filenames(ABA_dir + gene_dir)
			for img_file in img_filenames:
				print("file: ",img_file)
				chdir(ABA_dir + gene_dir)
				img = imread(img_file,IMREAD_COLOR)
				cvtColor(img,COLOR_BGR2RGB)
				expression_map = detect_expression(img)
				filtered_expression_map = filter_expression(expression_map)
				# save filtered expression map as an image to new gene folder in map_dir
				chdir(map_dir + gene_dir)
				filtered_expression_img = Image.fromarray(filtered_expression_map)
				filtered_expression_img = filtered_expression_img.convert("L") # convert to greyscale
				save_img(filtered_expression_img, img_file)
	
def get_filenames(dir):
	chdir(dir)
	return listdir(dir)
	
def detect_expression(img):
	# create new binary expression map
	expression_map = empty(([img.shape[0],img.shape[1]]))
	
	# check pixel value against to threshold values, color new map accordingly
	for y in range(img.shape[0]):
		for x in range (img.shape[1]):
			if (img[y, x, 0] <= THRESHOLD_R) and (img[y, x, 1] <= THRESHOLD_G) and (img[y, x, 2] <= THRESHOLD_B):
				expression_map[y,x] = 0
			else:
				expression_map[y,x] = 255
	return expression_map
	
def filter_expression(expression_map):
	last_pixel = None
	window_dict={}
	# create new binary expression map for the filtered expression
	filtered_expression_map = empty(([expression_map.shape[0], expression_map.shape[1]]))
	
	# loop through each pixel in the image
	for y,x in product(range(filtered_expression_map.shape[0]), range(filtered_expression_map.shape[1])):
		# define window min/max values
		xmin_window = x-N_RADIUS
		xmax_window= x+N_RADIUS
		ymin_window = y-N_RADIUS
		ymax_window= y+N_RADIUS
		
		# edge cases for window, no wrap around
		if xmin_window < 0:
			xmin_window = 0
		
		if xmax_window > filtered_expression_map.shape[1]-1:
			xmax_window = filtered_expression_map.shape[1]-1
		
		if ymin_window < 0:
			ymin_window = 0	
		
		if ymax_window > filtered_expression_map.shape[0]-1:
			ymax_window = filtered_expression_map.shape[0]-1
			
		# if starting at the first pixel of the image, or at a new row of pixels,
		# build window_dict	where key=coordinate of the pixel; value=the value of the pixel (0 or 255)
		if last_pixel==None or last_pixel[0] != y: # or start new row
			window_dict.clear()
			window_density_count = 0
			# loop through the pixels in the window, add them to window_dict, increment count if pixel has expression
			for coord in list(product(range(ymin_window,ymax_window+1), range(xmin_window,xmax_window+1))):
				window_dict[coord] = expression_map[coord[0]][coord[1]]
				if window_dict[coord] == 0:
					window_density_count += 1
		# if not at the first pixel or a new row, loop through the coordinates of the window
		else:
			for u in range(ymin_window,ymax_window+1):
				# if the coordinate is inside the bounds of the image and not in the window dict already, add it
				# also increment the expression counter if the added pixel has expression
				if (xmax_window <= filtered_expression_map.shape[1]-1) and ((u,xmax_window) not in window_dict):
					window_dict[(u,xmax_window)]=expression_map[u][xmax_window]
					if window_dict[(u,xmax_window)] == 0:
						window_density_count += 1
				# if the coordinate is out of the range for new window, remove it
				# also decrement the expression counter if the pixel showed expression
				if (u,xmin_window-1) in window_dict:
					if window_dict[(u,xmin_window-1)]==0:
						window_density_count -= 1
					del window_dict[(u,xmin_window-1)]			
					
		# check against min expression density, if count>=min, current pixel has expression, otherwise it does not
		if window_density_count >= MIN_EXPRESSION_DENSITY:
			filtered_expression_map[y][x]=0
		else:
			filtered_expression_map[y][x]=255
		last_pixel = (y,x)
	return filtered_expression_map

def save_img(img,filename):
	# remove .jpg from filename
	filename = filename[:-4] 
	filename += "_expression.png"
	img.save(filename)
	print("saved! ", filename )
	return
	
if __name__== "__main__":
		main()