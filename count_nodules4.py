import argparse
import cv2
import numpy as np
import random
import grid_otsu_threshold
import math

def find_parent(parent, i):
	temp = i
	while parent[temp] != -1:
		temp = parent[temp]
	return temp
 
def union(parent,x,y):
	if x == y:
		return
	x_set = find_parent(parent, x)
	y_set = find_parent(parent, y)

	if x_set < y_set:
		parent[x_set] = y_set
	elif y_set > x_set:
		parent[y_set] = x_set
	# if x_set == y_set means they are in the same subset


parser = argparse.ArgumentParser()
parser.add_argument('--input')
parser.add_argument('--size')
parser.add_argument("--optional_output", action="store")
args = parser.parse_args()

input_img = cv2.imread(args.input, 0)
width, height = input_img.shape
area = int(args.size)
BACKGROUND = 255
side_length = 10

######################################### threshold the image
####### filter, preprocess
input_img = cv2.GaussianBlur(input_img,(5,5),0) 
# kernel = np.ones((5,5),np.uint8)
# input_img = cv2.erode(input_img, kernel, iterations = 1)
# input_img = cv2.dilate(input_img,kernel,iterations = 1)
# input_img = cv2.morphologyEx(input_img, cv2.MORPH_OPEN, kernel)
# input_img = cv2.morphologyEx(input_img, cv2.MORPH_CLOSE, kernel)
# input_img = cv2.morphologyEx(input_img, cv2.MORPH_TOPHAT, kernel)

####### thresholding
height_ceil = int(math.ceil(float(height)/float(side_length)))
width_ceil = int(math.ceil(float(width)/float(side_length)))
thresholds = [[0 for x in range(0, height_ceil)] for x in range(0, width_ceil)]

i = 0
j = 0
w = side_length
h = side_length
while i < width:
	j = 0
	h = side_length
	if i + side_length > width:
		w = width - i
	while j < height:
		if j + side_length > height:
			h = height - j
		grid_otsu_threshold.cal_thresholds(input_img, thresholds, i, j, w, h, side_length)
		j += side_length
	i += side_length

# generate output image
for i in range(0, width):
	for j in range(0, height):
		if input_img[i][j] > thresholds[i//side_length][j//side_length]:
			input_img[i][j] = 255
		else:
			input_img[i][j] = 0

################## calculate connected components
parent = [-1] # it is used to record label, label is corresponding to the key of parent list
next_label = 1
labels = [[0 for x in range(0, height)] for x in range(0, width)]
for x in range(0, width):
	for y in range(0, height):
		if input_img[x][y] == BACKGROUND:
			pass
		
		if y > 0 and input_img[x][y] == input_img[x][y-1] and x > 0 and input_img[x][y] == input_img[x-1][y]:
			if labels[x][y-1] != labels[x-1][y]:
				labels[x][y] = min(labels[x][y-1], labels[x-1][y])
				union(parent, labels[x][y-1], labels[x-1][y])
			else:
				labels[x][y] = labels[x][y-1]
		elif y > 0 and input_img[x][y] == input_img[x][y-1]:
			labels[x][y] = labels[x][y-1]
		elif x > 0 and input_img[x][y] == input_img[x-1][y]:
			labels[x][y] = labels[x-1][y]
		else:
			labels[x][y] = next_label
			parent.append(-1)
			next_label += 1
			assert(len(parent) == next_label)

for x in range(0, width):
	for y in range(0, height):
		if input_img[x][y] != BACKGROUND:
			labels[x][y] = find_parent(parent, labels[x][y])

area_label_counter = {}
for x in range(0, width):
	for y in range(0, height):
		if labels[x][y] in area_label_counter:
			area_label_counter[labels[x][y]] += 1
		else:
			area_label_counter[labels[x][y]] = 1

area_counter = 0
for key in area_label_counter:
	if area_label_counter[key] > area:
		area_counter += 1
print(area_counter)

if args.optional_output: 
	output_image = [[0 for x in range(0,height)] for x in range(0,width)]
	label_colors = {}
	used_color = []
	for x in range(0, width):
		for y in range(0, height):
			if input_img[x][y] != BACKGROUND:
				if labels[x][y] not in label_colors:
					color_temp = random.randint(0,BACKGROUND)
					while color_temp in used_color:
						color_temp = random.randint(0,BACKGROUND)
					label_colors[labels[x][y]] = color_temp
				output_image[x][y] = label_colors[labels[x][y]]
			else:
				output_image[x][y] = BACKGROUND

	output_image = np.array(output_image)
	cv2.imwrite(args.optional_output, output_image)

	# img_output = cv2.imread(args.optional_output, 0)
	# cv2.imshow('output', img_output)
	# cv2.waitKey()



