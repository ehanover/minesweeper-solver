import pyautogui
import time
import webbrowser
import numpy as np
from PIL import Image

# -2:flag -1:unclicked 0:noNum 1:one 2:two ... 99:bomb
#dict_sum_all = {"294252":-2, "331407":-1, "322752":0, "291936":1, "260480":2, "279096":3, "262272":4, "251520":5, "271552":6, "234597":99} # -2=flag, -1=unclicked, 0=clickedEmpty
#dict_sum_all_reduced = {"294252":-2, "331407":-1, "322752":0, "291936":1, "260480":2, "279096":3, "262272":4, "251520":5, "271552":6, "234597":99} # -2=flag, -1=unclicked, 0=clickedEmpty
#dict_sum_2 = {"29425":-2, "33140":-1, "32275":0, "29193":1, "26048":2, "27909":3, "26227":4, "25152":5, "23459":99}
#dict_sum_3 = {"294":-2, "331": -1, "322":0, "291":1, "260":2, "279":3, "262":4, "251":5} # for /1000
dict_4 = {"2758":-2, "2583":-1, "282":0, "762":1, "560":2, "962":3, "552":4, "600":5, "417":99}

class Tile:
	def __init__(self, x, y, num=-1):
		self.x = x
		self.y = y
		self.num = num

	def __str__(self):
		return "({}, {}): {} ".format(self.x, self.y, self.num)

	def str_pad(self):
		s = str(self.num)
		return " "*max((2-len(s)), 0) + s # TODO optimize


def mouse(x, y, dur=0, click=False, button="left"):
	pyautogui.moveTo(x, y, duration=dur)
	if click:
		pyautogui.click(button=button)

def open_webpage(url="http://minesweeperonline.com/#150", sleep=2.7):
	webbrowser.open(url, autoraise=True)
	time.sleep(sleep)

def uid_from_img(img):
	img_array = np.array(img)
	#print("r1i", img_array[1])
	img_array = np.where(img_array==np.array([192,192,192]), np.array([0,0,0]), (img_array/50).astype(int))
	#print("r1f", img_array[1])
	return np.sum(img_array)
	#return int(np.sum(img)/1000)

	# b = np.where(img==[192,192,192], [0,0,0], img) # replaces gray color with 0s
	# print("b:", b)
	# return np.sum(b)

	#sub_img_small = np.array(sub_img.resize((1,1), Image.ANTIALIAS))[0][0] # this can't differentiate between 3 and 4?
	#return np.sum(sub_img_small)

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
			nx = x+i
			ny = y+j
			if not (i == 0 and j == 0) and nx<num_width and ny<num_height and nx>=0 and ny>=0: # this tile isn't at (x,y) and isn't outside of the grid
				tiles.append(grid[ny][nx])
	return tiles


mouse_start = pyautogui.position()
#open_webpage()
mouse(1,1)

num_width = 30 # 30
num_height = 16 # 16

topleft = pyautogui.locateOnScreen('tile.png', confidence=0.9)

tile_size = topleft[2] # assumes tile width and height are the same
roi = [ topleft[0], topleft[1], topleft[2]*num_width, topleft[3]*num_height ] # xywh
click_offset = tile_size/2
#print(roi)
# outline roi
#mouse(roi[0], roi[1], 0.1)
#mouse(roi[0]+roi[2], roi[1]+roi[3], 0.1)
#time.sleep(0.1)

# activates first squares
mouse(roi[0]+roi[2]/2, roi[1]+roi[3]/2, click=True) # click the middle tile
#mouse(roi[0]+click_offset, roi[1]+click_offset, click=True) # click the top left tile
#mouse(roi[0]+click_offset+24*6, roi[1]+click_offset, click=True, button="right")
mouse(1,1)


def get_grid_locate():
	grid = []

	#for y in range(start[1], start[1]+(bx*ts), ts):
	for tile_y in range(0, num_height):
		row = []
		#for x in range(start[0], start[0]+(by*ts), ts):
		for tile_x in range(0, num_width):
			screen_x = roi[0] + tile_x*tile_size # screen pixel coordinates
			screen_y = roi[1] + tile_y*tile_size
			#print("x,y: {},{}  sx: {} sy: {}  ss: {}".format(x, y, sx, sy, ss))

			region_buffer = 2 
			region = (screen_x-region_buffer, screen_y-region_buffer, tile_size+region_buffer*2, tile_size+region_buffer*2)

			num = -1 # error tile
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

			row.append(num)
		grid.append(row)

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
			#break
			if(str(uid) in dict_4.keys()): # this number is in the dict already
				row.append( Tile(tile_x, tile_y, dict_4[str(uid)]) )
			else:
				row.append( Tile(tile_x, tile_y, uid*-1) ) # TODO does this help to prevent random clicks in random places?

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
						#print("adding lct", t)
						left_click_tiles.append(t)

	for right_click_tile in right_click_tiles:
		mouse(click_offset+roi[0]+right_click_tile.x*tile_size, click_offset+roi[1]+right_click_tile.y*tile_size, dur=0, click=True, button="right")

	#print("len lc: " + str(len(left_click_tiles)))
	for left_click_tile in left_click_tiles:
		mouse(click_offset+roi[0]+left_click_tile.x*tile_size, click_offset+roi[1]+left_click_tile.y*tile_size, dur=0, click=True, button="left")
		#print("lc: {}".format(left_click_tile))

	if len(left_click_tiles) == 0: # there are no easy clicks, so the grid needs to be rescanned
		return False

	return True


# count = 0
running = True
while running:
	# print("looping {}...".format(count))
	# c += 1

	grid = get_grid_color()

	#print("===")
	for row in grid: # prints unknown tile nums
		#row_text = ""
		for t in row:
			#row_text += t.str_pad() + " "
			if abs(t.num) > 100: # there's an unknown number
				print("unknown: " + str(t))
			if t.num == 99: # there's a bomb on the screen!
				print("bomb detected!")
				running = False
				break
		#print(row_text)

	# print("\nns: ")
	# ns = neighbors(14, 8, grid)
	# for t in ns:
	# 	print(t)
	
	did_click = do_clicks(grid)

	if did_click == False:
		if do_clicks(grid) == False: # check twice to ensure there are no missed just-updated tiles
			running = False
			break

print("done. ")
mouse(mouse_start[0], mouse_start[1]) # put mouse back in original position