import pygame
from random import randrange
#from functools import lru_cache
# TODO implement chording
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

def reveal_neighbors_recursive(x, y):
	# global numasdf
	# print("starting reveal_neighbors, ", numasdf)
	# numasdf += 1

	if grid[y][x].num != 0 or grid[y][x].state == Tile.UNCLICKED:
		return

	for neighbor_coords in get_neighbor_coords(x, y):
		neighbor = grid[neighbor_coords[1]][neighbor_coords[0]]

		# if neighbor in checked_tiles:
		# 	print("skipping a neighbor")
		# 	continue

		if neighbor.state == Tile.UNCLICKED and neighbor.num == 0:
			neighbor.state = Tile.CLICKED
			reveal_neighbors_recursive(neighbor.x, neighbor.y)
			#checked_tiles.append(neighbor)
		elif neighbor.state == Tile.UNCLICKED and neighbor.num != -1:
			neighbor.state = Tile.CLICKED
			#checked_tiles.append(neighbor)

def reveal_neighbors(x, y):
	# global numasdf

	considered = []
	to_consider = get_neighbor_coords(x, y)
	while len(to_consider) > 0:

		tile_coords = to_consider.pop()
		tile = grid[tile_coords[1]][tile_coords[0]]
		if tile in considered:
			#print("skipping a tile")
			continue

		# print("looping in reveal_neighbors, ", numasdf)
		# numasdf += 1

		considered.append(tile)
		if tile.state == Tile.UNCLICKED:
			if tile.num == 0: # only consider neighbors of an empty tile
				tile.state = Tile.CLICKED
				to_consider.extend(get_neighbor_coords(tile.x, tile.y))
			elif tile.num > 0: # this is a number tile so don't consider its neighbors
				tile.state = Tile.CLICKED


def get_bomb_spots(bad_spots):
	spots = []
	# bomb_spots = [[2, 2], [10,10], [11,11], [13, 13]]
	#bomb_spots = []
	#bad_bomb_spots = []
	while len(spots) < num_bombs:
		rx = randrange(num_width)
		ry = randrange(num_height)

		if [rx, ry] not in spots and [rx, ry] not in bad_spots:
			spots.append([rx, ry])
	return spots

def place_numbers(bomb_spots):
	global grid
	#global bomb_spots
	grid = []
	# print("starting p_n with grid len", len(grid))
	# print("sub", len(grid[0]))
	#global bomb_spots
	#print("place numbers, these are bombs:", bomb_spots)
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
					#print("found adjacent bomb")
			#print("adding bomb with number", bombs_adjacent)
			#print("adding new tile at ({}, {}) with num {}".format(i, j, bombs_adjacent))
			row.append( Tile(i, j, bombs_adjacent, Tile.UNCLICKED) )
		grid.append(row)

def update(event): # handle mouse clicks and update grid accordingly
	global bomb_spots
	global show_bombs
	click_x = int(event.pos[0]/screen_width*num_width)
	click_y = int(event.pos[1]/screen_height*num_height)

	if len(bomb_spots) == 0:  # this is the first left click, so bombs need to be placed now
		if event.button == 1:
			print("initializing bombs and grid")

			bomb_spots = get_bomb_spots( get_neighbor_coords(click_x, click_y) + [[click_x, click_y]] )
			place_numbers(bomb_spots)
			#print("b_s", bomb_spots)
		else:
			return

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
			show_bombs = True
		else:
			tile.state = Tile.CLICKED
			reveal_neighbors(click_x, click_y)
			#reveal_neighbors_recursive(click_x, click_y)


def draw(disp):
	# global show_bombs
	# print("drawing, sb=", show_bombs)

	#disp.fill((192, 192, 192))
	disp.fill((0, 0, 0))

	for j in range(num_height):
		for i in range(num_width):

			tile = grid[j][i]
			img = ""
			# if grid[j][i].num == -1: # FOR TESTING ONLY
			# 	img = tile_pics[-2]
			# if tile.num == 1:
			# 	continue

			if tile.state == Tile.UNCLICKED:
				img = tile_pics[0]
			elif tile.state == Tile.FLAGGED:
				img = tile_pics[-1]
			elif tile.num == -1: # bomb
				img = tile_pics[-2]
			else:
				img = tile_pics[ tile.num+1 ]

			# for show_bombs:
			if show_bombs and tile.num == -1:
				if tile.state == Tile.FLAGGED:
					img = tile_pics[-1] # TODO make this a unique/recognizable bomb picture
				elif tile.state == Tile.UNCLICKED:
					img = tile_pics[-2] # TODO make incorrectly flagged bombs look different

			disp.blit(img, (i*tile_size+screen_buffer, j*tile_size+screen_buffer))
	pygame.display.update()

#numasdf = 0

num_width = 30 # 30
num_height = 16 # 16
num_bombs = 99 # 99

tile_size = 24
screen_buffer = 10
screen_width = num_width*tile_size+screen_buffer*2
screen_height = num_height*tile_size+screen_buffer*2

tile_filenames = ["empty"] + ["t" + str(i) for i in range(0,6)] + ["bomb", "flag"]
tile_pics = [ pygame.image.load("Tiles/{}.png".format(n)) for n in tile_filenames ]
#print("loading files ", tile_filenames)

bomb_spots = []
#bomb_spots = [ [1,0],[4,4],[5,5],[10,12] ]
show_bombs = False
grid = []
place_numbers([])

pygame.init()
pygame.mixer.quit()
display = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("minesweeper clone")

draw(display)

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			break
			#pygame.display.update()			

		elif event.type == pygame.MOUSEBUTTONDOWN:
			update(event)
			draw(display)

	pygame.time.wait(0)

pygame.quit()