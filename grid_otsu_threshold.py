import argparse
import cv2
import numpy as np
import math

def cal_thresholds(img, thresholds_record, i, j, w, h, side_length):
	thresholds_record_x = i//side_length
	thresholds_record_y = j//side_length

	threshold = 0
	var_max = 0
	sum_num = 0
	sumB = 0
	q1 = 0
	q2 = 0
	mu1 = 0
	mu2 = 0

	histogram = [0] * 256
	total_pixels = w * h

	for x in range(i, i+w):
		for y in range(j, j+h):
			histogram[img[x][y]] += 1

	# determine if it is bimodal distribution
	max1 = 0
	max2 = 0
	for x in histogram:
		if x == 0:
			continue
		if x > max1:
			max2 = max1
			max1 = x
		if x > max2:
			max2 = x

	if not(max1 > side_length/2 and max2 > side_length/3) and (thresholds_record_x - 1 > 0 or thresholds_record_y - 1 > 0):
		mean_threshold = 0
		if thresholds_record_x - 1 > 0 and thresholds_record_y -1 > 0:
			total_neighbor_threshold = thresholds_record[thresholds_record_x-1][thresholds_record_y-1]
			total_neighbor_threshold += thresholds_record[thresholds_record_x][thresholds_record_y-1]
			total_neighbor_threshold += thresholds_record[thresholds_record_x-1][thresholds_record_y]
			mean_threshold = total_neighbor_threshold / 3
		elif thresholds_record_x - 1 > 0:
			mean_threshold = thresholds_record[thresholds_record_x-1][thresholds_record_y]
		else:
			mean_threshold = thresholds_record[thresholds_record_x][thresholds_record_y-1]
		thresholds_record[thresholds_record_x][thresholds_record_y] = mean_threshold
		return

	# calculate threshold otherwise
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

	thresholds_record[i//side_length][j//side_length] = threshold


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--input')
	parser.add_argument("grid_size")
	parser.add_argument('--output')
	args = parser.parse_args()

	input_img = cv2.imread(args.input, 0)
	width, height = input_img.shape
	side_length = int(math.sqrt(float(args.grid_size)))
	output_img = [[0 for x in range(0,height)] for x in range(0,width)]

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
			cal_thresholds(input_img, thresholds, i, j, w, h, side_length)
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

	# img_output = cv2.imread(args.output, 0)
	# cv2.imshow('output', img_output)
	# cv2.waitKey()

	# # validation
	# ret = cv2.adaptiveThreshold(input_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
	#    cv2.THRESH_BINARY, 11, 2);
	# cv2.imshow('q2_example', ret)
	# cv2.waitKey()







