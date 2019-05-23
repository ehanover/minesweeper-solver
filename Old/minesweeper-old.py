import pyautogui
#import imagehash
import PIL
from PIL import Image
import time
import matplotlib.pyplot as plt

TILE_SIZE = 24
GRID_X = 30
GRID_Y = 16

GRID_SX = GRID_X*TILE_SIZE
GRID_SY = GRID_Y*TILE_SIZE


start = pyautogui.locateOnScreen('grid.png')
sx = start[0]
sy = start[1]
#imagehash.dhash.force_pil()

def get_image_int(img):
	#return img.resize(2, 2, PIL.Image.ANTIALIAS)
	#img.thumbnail((1, 1), PIL.Image.ANTIALIAS)
	r,g,b = img.getpixel((1, 1))
	return r+g+b
	#return img[0,0]
	# imagehash.dhash(img)
	# print(img.getdata())

def click_tile(x, y, i):
	b = "left"
	if i != 0:
		b = "right"
	pyautogui.click(x=(sx+TILE_SIZE*x), y=(sy+TILE_SIZE*y), button=b)

def get_grid():
	grid = []
	screen = pyautogui.screenshot(region=(sx, sy, GRID_SX, GRID_SY))
	screen.show()
	plt.imshow(screen)
	for i in range(sx, sx+GRID_SX, TILE_SIZE):
		row = []
		for j in range(sy, sy+GRID_SY, TILE_SIZE):
			#pyautogui.moveTo(i, j)
			sub = screen.crop((i, j, i+TILE_SIZE, j+TILE_SIZE))
			sub.show()
			#print(sub)
			#print(get_image_int(sub))
			#time.sleep(0.2)
			break	
		break

	return grid


# def do_turn():
# 	grid = get_grid()
# 	print(grid)

#click_tile(29, 15, 0)
#time.sleep(1)
print(get_grid())
