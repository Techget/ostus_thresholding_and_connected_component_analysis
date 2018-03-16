import argparse
import cv2
import numpy as np

# def find_parent(parent,i):
# 	if parent[i] == -1:
# 		return i
# 	if parent[i]!= -1:
# 		 return find_parent(parent, parent[i])

def find_parent(parent, i):
	temp = i
	print("########", parent)
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
	else:
		parent[y_set] = x_set

parser = argparse.ArgumentParser()
parser.add_argument('--input')
parser.add_argument('--size')
parser.add_argument("--optional_output", action="store")
args = parser.parse_args()

input_img = cv2.imread(args.input, 0)
width, height = input_img.shape
area = int(args.size)
BACKGROUND = 255

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
	cv2.imwrite(args.output, output_image)

	img_output = cv2.imread(args.output, 0)
	cv2.imshow('output', img_output)
	cv2.waitKey()



