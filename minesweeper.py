import pyautogui
import time
import webbrowser
import numpy as np
import cv2
from PIL import Image


class Tile:
	def __init__(self, x, y, num=-1):
		self.x = x
		self.y = y
		self.num = num

	def __str__(self):
		return "({}, {}) {} ".format(self.x, self.y, self.num)

	def str_pad(self):
		s = str(self.num)
		return " "*max((2-len(s)), 0) + s # TODO optimize

#dict_sum_avg = {"564":33, "576":-1, "497":10, "436":20, "476":30}
dict_sum_all = {"294252":-2, "331407":-1, "322752":0, "291936":1, "260480":2, "279096":3, "262272":4, "251520":5} # -2=flag, -1=unclicked, 0=clickedEmpty

# x, y = pyautogui.locateCenterOnScreen('tile.png')
# pyautogui.click(x, y)

# for pos in pyautogui.locateAllOnScreen('tile.png'):
# 	print(pos)

#time.sleep(2)
mouse_start = pyautogui.position()

def mouse(x, y, dur=0, click=False, button="left"):
	pyautogui.moveTo(x, y, duration=dur)
	if click:
		pyautogui.click(button=button)

def open_webpage(url="http://minesweeperonline.com/#150", sleep=2.7):
	webbrowser.open(url, autoraise=True)
	time.sleep(sleep)

def uid_from_img(img):
	return np.sum(img)
	#return np.sum( np.where(img==[192,192,192], [0,0,0], img) ) # replaces gray color with 0s
	
	#sub_img_small = np.array(sub_img.resize((1,1), Image.ANTIALIAS))[0][0]
	#sub_img_small_avg = np.sum(sub_img_small)

def num_count(tiles, num):
	count = 0
	for t in tiles:
		if t.num == num:
			count += 1
	return count

def neighbors(x, y, grid):
	tiles = []
	for i in range(-1, 2):
		for j in range(-1, 2):
			if not (i == 0 and j == 0) and x+j<num_width and y+i<num_height: # this tile isn't at (x,y)
				tiles.append(grid[y+i][x+j])
	return tiles

open_webpage()
mouse(1,1)

num_width = 30 # 30
num_height = 16 # 16

topleft = pyautogui.locateOnScreen('tilec.png')

#ts = 21#start[2]
#ss = start[2] + 2

tile_size = topleft[2] # assumes width and height are the same

roi = [ topleft[0], topleft[1], topleft[2]*num_width, topleft[3]*num_height ] # xywh

# outline roi
mouse(roi[0], roi[1], 0.1)
mouse(roi[0]+roi[2], roi[1]+roi[3], 0.1)
time.sleep(0.1)

# activates first squares
mouse(roi[0]+roi[2]/2, roi[1]+roi[3]/2, click=True) # middle
#mouse(roi[0]+2, roi[1]+2, click=True) # top left
mouse(1,1)

def get_grid_locate():
	grid = []
	#blank = list( pyautogui.locateAllOnScreen('tile.png') )

	#for y in range(start[1], start[1]+(bx*ts), ts):
	for tile_y in range(0, num_height):
		row = []
		#for x in range(start[0], start[0]+(by*ts), ts):
		for tile_x in range(0, num_width):

			screen_x = roi[0] + tile_x*tile_size # screen pixel coordinates
			screen_y = roi[1] + tile_y*tile_size


			num = -1 # error tile

			#print("x,y: {},{}  sx: {} sy: {}  ss: {}".format(x, y, sx, sy, ss))

			#print( str(pyautogui.locateOnScreen('tileb.png', region=(sx, sy, ss, ss))), end=", ")
			#print( str(pyautogui.locateOnScreen('1b.png', region=(sx, sy, ss, ss))) )
			region_buffer = 2 
			region = (screen_x-region_buffer, screen_y-region_buffer, tile_size+region_buffer*2, tile_size+region_buffer*2)

			if pyautogui.locateOnScreen('tilec.png', region=region, grayscale=True): # unclicked
				num = 0
			elif pyautogui.locateOnScreen('emptyc.png', region=region, grayscale=True): # empty
				num = 33			
			elif pyautogui.locateOnScreen('flagb.png', region=region, grayscale=True): # bomb
				num = 88
			else: # must be a number square
				pass


			# elif pyautogui.locateOnScreen('1c.png', region=region, grayscale=True):
			# 	num = 1
			# elif pyautogui.locateOnScreen('2b.png', region=region, grayscale=True):
			# 	num = 2
			# elif pyautogui.locateOnScreen('3b.png', region=(x, y, ts, ts)):
			# 	num = 3
			# elif pyautogui.locateOnScreen('4b.png', region=(x, y, ts, ts)):
			# 	num = 4
			# elif pyautogui.locateOnScreen('5b.png', region=(x, y, ts, ts)):
			# 	num = 5

			row.append(num)

		grid.append(row)


	#pyautogui.click(start)
	#print(str(blank[:2]))
	#print(str(start))
	return grid

def get_grid_color():
	grid = []

	img = pyautogui.screenshot(region=tuple(roi))

	for tile_y in range(0, num_height):

		row = []
		for tile_x in range(0, num_width):

			img_x = tile_x*tile_size # image pixel coordinates
			img_y = tile_y*tile_size

			# find the region of img to add the pixel colors
			region_buffer = 0
			region = (img_x-region_buffer, img_y-region_buffer,	img_x+tile_size+region_buffer, img_y+tile_size+region_buffer) # top, left, right, bottom
			#mouse(topleft[0]+region[0], topleft[1]+region[1], dur=0.3)

			sub_img = img.crop(tuple(region))
			uid = uid_from_img(sub_img)

			if(str(uid) in dict_sum_all.keys()): # this number is in the dict already
				row.append( Tile(tile_x, tile_y, dict_sum_all[str(uid)]) )
			else:
				row.append( Tile(tile_x, tile_y, uid) )

			#print("reg: {}   avg rgb: {}   avg sum: {}".format(region, sub_img_small, num))

		grid.append(row)

	return grid

def do_clicks(grid):

	right_click_tiles = []
	left_click_tiles = []

	for y in range(num_height):
		for x in range(num_width):

			tile = grid[y][x]
			tile_neighbors = neighbors(x, y, grid)

			if num_count(tile_neighbors, -1) + num_count(tile_neighbors, -2) == tile.num: # can safely flag all unclicked tiles around this tile
				for t in tile_neighbors:
					if t.num == -1 and t not in right_click_tiles:
						t.num = -2
						right_click_tiles.append(t)

			if tile.num > 0 and num_count(tile_neighbors, -2) == tile.num: # can safely click all tiles around this tile
				for t in tile_neighbors:
					if t.num == -1 and t not in left_click_tiles:
						left_click_tiles.append(t)



	if len(left_click_tiles) == 0: # there are no easy clicks
		return False

	for right_click_tile in right_click_tiles:
		mouse(2+roi[0]+right_click_tile.x*tile_size, 2+roi[1]+right_click_tile.y*tile_size, dur=0.1, click=True, button="right")

	for left_click_tile in left_click_tiles:
		mouse(2+roi[0]+left_click_tile.x*tile_size, 2+roi[1]+left_click_tile.y*tile_size, dur=0.1, click=True, button="left")


	return True





while True:
	grid = get_grid_color()

	for row in grid:
		row_text = ""
		for t in row:
			if t.num > 100:
				print(t)
		# 	row_text += t.str_pad() + " "
		# print(row_text)

	# print("\nns: ")
	# ns = neighbors(14, 8, grid)
	# for t in ns:
	# 	print(t)

	did_click = do_clicks(grid)

	if did_click == False:
		break



print("done. ")
mouse(mouse_start[0], mouse_start[1]) # put mouse back in original position
