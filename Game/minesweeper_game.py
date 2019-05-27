import pygame
from random import randrange

class Tile:
	UNCLICKED, FLAGGED, CLICKED = range(3) # basically an enum

	def __init__(self, x, y, num=0, state=UNCLICKED):
		self.x = x
		self.y = y
		self.num = num
		self.state = state

	def __str__(self):
		return "({}, {}): {} ".format(self.x, self.y, self.num)

	def str_pad(self):
		s = str(self.num)
		return " "*max((2-len(s)), 0) + s

def get_neighbor_coords(x, y):
	ret = []
	for i in range(-1, 2):
		for j in range(-1, 2):
			nx = x+i
			ny = y+j
			if not (i == 0 and j == 0) and nx<num_width and ny<num_height and nx>=0 and ny>=0: # this tile isn't at (x,y) and isn't outside of the grid
				ret.append([nx,ny])
	return ret

def reveal_neighbors(x, y):
	global numasdf
	print("starting reveal_neighbors, ", numasdf)
	numasdf += 1
	if grid[y][x].num != 0 or grid[y][x].state == Tile.UNCLICKED:
		return
	for neighbor_coords in get_neighbor_coords(x, y):
		neighbor = grid[neighbor_coords[1]][neighbor_coords[0]]
		if neighbor.state == Tile.UNCLICKED and neighbor.num == 0:
			neighbor.state = Tile.CLICKED
			reveal_neighbors(neighbor.x, neighbor.y)
		elif neighbor.state == Tile.UNCLICKED and neighbor.num != -1:
			neighbor.state = Tile.CLICKED


def update(event):
	click_x = int(event.pos[0]/screen_width*num_width)
	click_y = int(event.pos[1]/screen_height*num_height)
	tile = grid[click_y][click_x]
	#print("clicking at ({}, {})".format(click_x, click_y))

	if event.button == 3: # right click
		if tile.state == Tile.UNCLICKED:
			tile.state = Tile.FLAGGED
		elif tile.state == Tile.FLAGGED:
			tile.state = Tile.UNCLICKED

	elif event.button == 1: # left click
		if tile.state == Tile.FLAGGED or tile.state == Tile.CLICKED:
			return
		#tile.state = Tile.CLICKED
		if tile.num > 0:
			#print("revealing a number tile")
			tile.state = Tile.CLICKED
		elif tile.num == -1: # you clicked on a bomb!
			print("you clicked on a bomb!")
		else:
			tile.state = Tile.CLICKED
			reveal_neighbors(click_x, click_y)


def draw(disp):
	disp.fill((255, 0, 255))

	for j in range(num_height):
		for i in range(num_width):

			img = ""
			# if grid[j][i].num == -1: # FOR TESTING ONLY
			# 	img = tile_pics[-2]

			if grid[j][i].state == Tile.UNCLICKED:
				img = tile_pics[0]
			elif grid[j][i].state == Tile.FLAGGED:
				img = tile_pics[-1]
			elif grid[j][i].num == -1: # bomb
				img = tile_pics[-2]
			else:
				img = tile_pics[ grid[j][i].num+1 ]

			disp.blit(img, (i*tile_size, j*tile_size))

numasdf = 0

num_width = 30 # 30
num_height = 16 # 16
num_bombs = 50 # 99
grid = []

#board_buffer = 10
tile_size = 24
screen_width = num_width*tile_size
screen_height = num_height*tile_size

tile_filenames = ["empty"] + ["t" + str(i) for i in range(0,6)] + ["bomb", "flag"]
tile_pics = [ pygame.image.load("Tiles/{}.png".format(n)) for n in tile_filenames ]
#print("loading files ", tile_filenames)

#print("neighbors", get_neighbor_coords(0,0))
#print("\nneighbors", get_neighbor_coords(1,1))

pygame.init()
display = pygame.display.set_mode((screen_width, screen_height))

# initialize bomb locations
bomb_spots = []
while len(bomb_spots) < num_bombs:
	rx = randrange(num_width)
	ry = randrange(num_height)

	if [rx, ry] not in bomb_spots:
		bomb_spots.append([rx, ry]) 

# initialize grid numbers
for j in range(num_height):
	row = []
	for i in range(num_width):

		neighbors = get_neighbor_coords(i, j) # TODO can this be optimized? currently has 48000 iterations
		bombs_adjacent = 0
		for b in bomb_spots:
			if b == [i, j]: # this tile is a bomb spot
				bombs_adjacent = -1
				break
			elif b in neighbors:
				bombs_adjacent += 1
		#print("adding bomb with number", bombs_adjacent)
		row.append( Tile(i, j, bombs_adjacent, Tile.UNCLICKED) )
	grid.append(row)


draw(display)
pygame.display.update()

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			break
			#pygame.display.update()			

		if event.type == pygame.MOUSEBUTTONDOWN:
			update(event)
			draw(display)
			pygame.display.update()


pygame.quit()