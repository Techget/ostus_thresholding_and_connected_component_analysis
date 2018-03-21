import argparse
import cv2
import numpy as np
import math
import grid_otsu_threshold

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--input')
	parser.add_argument('--output')
	args = parser.parse_args()

	input_img = cv2.imread(args.input, 0)
	width, height = input_img.shape
	side_length = min(width//10, height//10)
	output_img = [[0 for x in range(0,height)] for x in range(0,width)]

	####### filter, preprocess
	input_img = cv2.GaussianBlur(input_img,(5,5),0) 
	kernel = np.ones((5,5),np.uint8)
	# input_img = cv2.erode(input_img, kernel, iterations = 1)
	# input_img = cv2.dilate(input_img,kernel,iterations = 1)
	input_img = cv2.morphologyEx(input_img, cv2.MORPH_OPEN, kernel)
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
				output_img[i][j] = 255
			else:
				output_img[i][j] = 0

	output_img = np.array(output_img)
	cv2.imwrite(args.output, output_img)
