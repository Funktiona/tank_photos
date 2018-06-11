import socket
import time
import urllib
import cv2
import numpy as np
from collections import Counter

s = socket.socket()
#hosta = '192.168.0.121'
hosta = '192.168.1.137'
host = '192.168.0.121'
#host = '0.0.0.0'
# host = '192.168.0.123' #ip of raspberry pi Erik
port = 10000
s.bind((hosta, port))
# hello
c = []
addr = []
c_1 = None
c_2 = None
addr_1 = None
addr_2 = None


image_nr = 0

def save_photo():
	global image_nr
	image_nr += 1

	urllib.urlretrieve("http://192.168.1.236:8080/stream/snapshot.jpeg?delay_s=0", 'photos/tank_' + str(image_nr) + ".jpg")

# Puts tower to maximum left posision
def reset_tower():
	for tower_pos in range(0,40):
		time.sleep(0.05)
		c_1.send('tower_left')

def contrast_img(img=None):

	global image_nr
	Z = img.reshape((-1,3))

	

	# convert to np.float32
	Z = np.float32(Z)
	#Z = np.float32(img)

	# define criteria, number of clusters(K) and apply kmeans()
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
	K = 3
	ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

	# Now convert back into uint8, and make original image
	center = np.uint8(center)
	res = center[label.flatten()]
	res2 = res.reshape((img.shape))

	cv2.imwrite('contrast/tank_' + str(image_nr) + '.png', res2)
	
	find_tank(img=res2)

def crop_img():

	global image_nr
	
	img = cv2.imread("photos/tank_" + str(image_nr) + ".jpg")
	img_crop = img[100:-165, 125:-160]
	cv2.imwrite('cropped/tank_' + str(image_nr) + '.jpg',img_crop)
	contrast_img(img=img_crop)
	
	

def convert(size, box):
	dw = 1./size[0]
	dh = 1./size[1]
	x = (box[0] + box[1])/2.0
	y = (box[2] + box[3])/2.0
	w = box[1] - box[0]
	h = box[3] - box[2]
	x = x*dw
	w = w*dw
	y = y*dh
	h = h*dh
	return (x,y,w,h)

def find_tank(img=None):
	
	global image_nr
	print('in find tank')

	image_height =  215
	image_width = 355

	# Image to find tank in
	image = img

	#Store all hexa colors
	colors = []

	# Get all hex colors in image
	for x in range(0,image_width):
		for y in range(0,image_height):
			color = image[y,x]
			hexa = "#{:02x}{:02x}{:02x}".format(color[0],color[1],color[2])
			colors.append(hexa)


	# Remove?
	words_to_count = (word for word in colors )
	c = Counter(words_to_count)
	print 'most common'
	print c.most_common(5)
	orange = c.most_common(3)[2][0]

	# Tank pos in image
	min_x = None
	min_y = None
	max_x = None
	max_y = None

	for x in range(0,image_width):
		for y in range(0,image_height):
			color = image[y,x]
			hexa = "#{:02x}{:02x}{:02x}".format(color[0],color[1],color[2])
			if hexa == orange:
				min_x = x
				break
		else:
			continue  # only executed if the inner loop did NOT break
	    	break  # only executed if the inner loop DID break


	for y in range(0,image_height):
		for x in range(0,image_width):
			color = image[y,x]
			hexa = "#{:02x}{:02x}{:02x}".format(color[0],color[1],color[2])
			if hexa == orange:
				min_y = y
				break
		else:
			continue  # only executed if the inner loop did NOT break
	    	break  # only executed if the inner loop DID break

	for x in range(image_width-1,0,-1):
		for y in range(image_height-1,0,-1):
			color = image[y,x]
			hexa = "#{:02x}{:02x}{:02x}".format(color[0],color[1],color[2])
			if hexa == orange:
				max_x = x
				break
		else:
			continue  # only executed if the inner loop did NOT break
	    	break  # only executed if the inner loop DID break


	for y in range(image_height-1,0,-1):
		for x in range(image_width-1,0,-1):
			color = image[y,x]
			hexa = "#{:02x}{:02x}{:02x}".format(color[0],color[1],color[2])
			
			if hexa == orange:
				max_y = y
				break
		else:
			continue  # only executed if the inner loop did NOT break
	    	break  # only executed if the inner loop DID break



	#print min_x, min_y, max_x, max_y

	cv2.rectangle(image, (min_x, min_y), (max_x, max_y), (255,0,0), 2)
	cv2.imwrite('box/tank_' + str(image_nr) + '.jpg', image)
	#dire = "labels/tank_" + str(nr) + ".txt"
	#print dire
	text_file = open("labels/tank_" + str(image_nr) + ".txt", "w")
	#text_file.write("1\n")


	#min_x += 180
	#max_x += 180
	#min_y += 200
	#max_y += 200

	width_x = max_x - min_x
	width_y = max_y - min_y
	
	image_height =  215
	image_width = 355

	#image_h = 480
	#image_w = 640

	b = (float(min_x), float(max_x), float(min_y), float(max_y))
	bb = convert((image_width,image_height), b)
	print 'now'
	print bb
	print bb[0]

	#text_file.write("%s %s %s %s", min_x, min_y, max_x, max_y)
	text_file.write('0 ' + str(bb[0]) + ' '+ str(bb[1]) + ' ' + str(bb[2]) + ' '+ str(bb[3]))
	text_file.close()
	
def all_pos():

	reset_tower()
	tower_left = True


	for tank_pos in range(0,100):
		c_1.send('left')
		time.sleep(1)
		save_photo()
		time.sleep(0.01)

		
		if tower_left :
			print(tower_left)

			for tower_pos in range(0,40):
				
				c_1.send('tower_right')
				time.sleep(0.5)

				save_photo()
				time.sleep(0.01)

			tower_left = False
		else:
			print(tower_left)
			for tower_pos in range(0,40):

				c_1.send('tower_left')
				time.sleep(0.5)
				
				save_photo()
				time.sleep(0.01)
			tower_left = True

s.listen(5)
while 1:
    temp_c, temp_addr = s.accept()
    data=temp_c.recv(1000)
    data = data.decode()
    print(data)
    c_1 = temp_c
    addr_1 = temp_addr

    #if data == '1':
	#print('tank 1 connected')
	#c_1 = temp_c
	#addr_1 = temp_addr

    #if data == '2':
	#print('tank 2 connected')
	#c_2 = temp_c
	#addr_2 = temp_addr
    
    temp_c.send('test')
    if(c_1):
	break

#up, down, left right
#tower_right

    #c.send(data)
print('after')

#for tank_pos in range(0,200):
	#c_1.send('up')
	#time.sleep(0.1)




print('done')
time.sleep(10)
all_pos()



