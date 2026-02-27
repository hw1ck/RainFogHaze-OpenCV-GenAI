import cv2

img = cv2.imread("media/fog1.jpg")
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)

clahe = cv2.createCLAHE(3.0, (8, 8))
final = cv2.cvtColor(cv2.merge((clahe.apply(l), a, b)), cv2.COLOR_LAB2BGR)

cv2.imwrite("output/fog1.jpg", final)
print("Done")