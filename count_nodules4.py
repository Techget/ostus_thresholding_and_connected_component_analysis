import argparse
import cv2
import numpy as np
import random
import grid_otsu_threshold
import math
from pprint import pprint

def find_parent(parent,i):
    if parent[i] == -1:
        return i
    if parent[i]!= -1:
         return find_parent(parent,parent[i])
 
def union(parent,x,y):
	if x == y:
		return
	x_set = find_parent(parent, x)
	y_set = find_parent(parent, y)

	if x_set > y_set:
		parent[x_set] = y_set
	elif x_set < y_set:
		parent[y_set] = x_set
	# if x_set == y_set means they are in the same subset

if __name__ == "__main__":
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
	threshold = 0
	var_max = 0
	sum_num = 0
	sumB = 0
	q1 = 0
	q2 = 0
	mu1 = 0
	mu2 = 0
	histogram = [0] * 256
	total_pixels = input_img.size
	for il in input_img:
		for j in il:
			histogram[j] += 1

	sum_num = 0
	for t in range(0, 256):
		sum_num += t * histogram[t]

	for t in range(0, 256):
		q1 += histogram[t]
		if q1 == 0:
			continue
		q2 = total_pixels - q1
		if q2 == 0:
			break

		sumB += t * histogram[t]
		mu1 = float(sumB / float(q1))
		mu2 = float((sum_num - sumB) / float(q2))
		sigma = float(q1*q2*(float(mu1 - mu2)**2))

		if sigma > var_max:
			threshold = t
			var_max = sigma

	for i in range(0, width):
		for j in range(0, height):
			if input_img[i][j] > threshold:
				input_img[i][j] = 255
			else:
				input_img[i][j] = 0

	##################################### calculate connected components
	parent = [-1] # it is used to record label, label is corresponding to the key of parent list
	next_label = 0
	labels = [[0 for x in range(0, height)] for x in range(0, width)]
	for x in range(0, width):
		for y in range(0, height):
			if input_img[x][y] == BACKGROUND:
				continue

			if (y > 0 and input_img[x][y] == input_img[x][y-1]) and (x > 0 and input_img[x][y] == input_img[x-1][y]):
				if labels[x][y-1] != labels[x-1][y]:
					union(parent, labels[x][y-1], labels[x-1][y])
					labels[x][y] = min(labels[x][y-1], labels[x-1][y])
				else:
					labels[x][y] = labels[x][y-1]
			elif y > 0 and input_img[x][y] == input_img[x][y-1]:
				labels[x][y] = labels[x][y-1]
			elif x > 0 and input_img[x][y] == input_img[x-1][y]:
				labels[x][y] = labels[x-1][y]
			else:
				next_label += 1
				labels[x][y] = next_label
				parent.append(-1)
				
	# relabel, replace label value with its parent's label value
	for x in range(0, width):
		for y in range(0, height):
			if input_img[x][y] != BACKGROUND:
				labels[x][y] = find_parent(parent, labels[x][y])

	area_label_counter = {}
	for x in range(0, width):
		for y in range(0, height):
			if labels[x][y] == 0:
				continue
			if labels[x][y] in area_label_counter:
				area_label_counter[labels[x][y]] += 1
			else:
				area_label_counter[labels[x][y]] = 1

	area_counter = 0
	for key in area_label_counter:
		if area_label_counter[key] > area:
			area_counter += 1
	print(area_counter)
	# pprint(labels)
	# print(parent)

	if args.optional_output: 
		# output_image = [[0 for x in range(0,height)] for x in range(0,width)]
		# output_image = cv2.copy(input_img)
		output_image = np.zeros((width, height,3))
		label_colors = {}
		used_color = []
		for x in range(0, width):
			for y in range(0, height):
				if labels[x][y] != 0:
					if labels[x][y] not in label_colors:
						label_colors[labels[x][y]] = [random.randint(0,BACKGROUND), random.randint(0,BACKGROUND), random.randint(0,BACKGROUND)]
					output_image[x][y] = label_colors[labels[x][y]]
				else:
					output_image[x][y] = [BACKGROUND, BACKGROUND, BACKGROUND]
		cv2.imwrite(args.optional_output, output_image)




### debug input
# input_img = np.array([[255, 255, 255, 0, 0, 0, 255, 255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                      [255, 255, 255, 0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0, 255, 255, 0, 0, 0],
#                     [255, 255, 255, 0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 255, 255, 0, 0, 0],
#                     [255, 255, 255, 0, 0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 255, 255, 0, 0, 0],
#                     [255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 0, 0, 0],
#                     [255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 0, 0, 0],
#                     [255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 0, 0, 0, 0],
#                     [255, 255, 255, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 0, 0, 0, 0],
#                     ])


