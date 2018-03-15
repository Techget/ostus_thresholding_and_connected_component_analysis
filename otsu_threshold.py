import argparse
import cv2
import numpy as np

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--input')
parser.add_argument('--output')
parser.add_argument("--threshold", action="store_true")
args = parser.parse_args()

img = cv2.imread(args.input, 0)
width, height = img.shape
output_image = [[0 for x in range(0,height)] for x in range(0,width)]

# verification
# ret, imgf = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
# print(ret)
# print(imgf)
# cv2.imshow('imgf', imgf)
# cv2.waitKey()

threshold = 0
var_max = 0
sum_num = 0
sumB = 0
q1 = 0
q2 = 0
mu1 = 0
mu2 = 0

histogram = [0] * 256
total_pixels = img.size

for il in img:
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
		if img[i][j] > threshold:
			output_image[i][j] = 255
		else:
			output_image[i][j] = 0

output_image = np.array(output_image)

cv2.imwrite(args.output, output_image)

# img_output = cv2.imread(args.output, 0)
	
# cv2.imshow('output', img_output)
# cv2.waitKey()

# print(np.array_equal(imgf, output_image))

