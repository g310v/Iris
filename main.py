import turtle
import random
import time

# global constants
YOUR_ID = '124XXXXXX' 
COLORS = ('green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'brown')
SHAPE_FILE = 'shapes.txt'
SCREEN_DIM_X = 0.7  # screen width factor
SCREEN_DIM_Y = 0.7  # screen height factor
XY_SPAN = 0.8       # canvas factor 
XY_STEP = 10        # step size of x,y coordinates
MIN_DURATION = 5    
MAX_DURATION = 30
MIN_STRETCH = 1
MAX_STRETCH = 10
MIN_SEED = 1
MAX_SEED = 99

# global variables
g_shapes = []       # list of polygons displayed on canvas
g_screen = None
g_range_x = None
g_range_y = None

def get_coordinates(shape:turtle.Turtle) -> list[tuple[int,int]]:
	'''
	Get the coordinates of the vertices of a turtle shape.
	
	Args:
		shape (turtle.Turtle): The turtle shape to get coordinates from.
	
	Returns:
		list[tuple[int,int]]: A list of tuples representing the coordinates of the vertices.
	'''
	curr_pos = shape.pos()
	vertex_coordinates = shape.get_shapepoly()

	# The coordinates are relative to the turtle's current position
	final_coordinates = [(x + curr_pos[0], y + curr_pos[1]) for x, y in vertex_coordinates]

	return final_coordinates

def get_boundaries(shape_coords: list) -> tuple[int,int,int,int]:
	'''
	Get the bounding box of a turtle shape.

	Args:
		shape_coords (list): The coordinates of the vertices of the shape.
	
	Returns:
		tuple[int,int,int,int]: A tuple representing the bounding box (x_min, y_min, x_max, y_max).
	'''
	# Calculate the minimum and maximum x and y coordinates
	x_min = min([x for x, y in shape_coords])
	y_min = min([y for x, y in shape_coords])
	x_max = max([x for x, y in shape_coords])
	y_max = max([y for x, y in shape_coords])

	return x_min, y_min, x_max, y_max

def cross_prod(o: tuple[int, int], a: tuple[int, int], b: tuple[int, int]) -> int:
	'''
	Calculate the cross product of vectors OA and OB.

	Args:
		o (tuple[int, int]): The origin point O.
		a (tuple[int, int]): The point A.
		b (tuple[int, int]): The point B.

	Returns:
		int: The cross product of vectors OA and OB.	
	'''
	return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
	
def cross_prod_sign(x: int) -> int:
	'''
	Determine the sign of the cross product.

	Args:
		x (int): The cross product value.
	
	Returns:
		int: 1 if x > 0, -1 if x < 0, 0 otherwise.
	'''
	return 1 if x > 0 else -1 if x < 0 else 0

def intervals_overlap(a: int, b: int, c: int, d: int) -> bool:
	'''
	Check if two intervals [a, b] and [c, d] overlap.

	Args:
		a (int): Start of the first interval.
		b (int): End of the first interval.
		c (int): Start of the second interval.
		d (int): End of the second interval.

	Returns:
		bool: True if the intervals overlap, False otherwise.
	'''

	if a > b: a, b = b, a
	if c > d: c, d = d, c
	return max(a, c) <= min(b, d)

def line_segments_intersect(line1: tuple[tuple[int, int], tuple[int, int]], 
                            line2: tuple[tuple[int, int], tuple[int, int]]) -> bool:
    '''
    Check if two line segments intersect by using the cross product method.
	This method checks the orientation of the points and determines if the line segments intersect.

    Args:
        line1 (tuple[tuple[int, int], tuple[int, int]]): The first line segment defined by two points.
        line2 (tuple[tuple[int, int], tuple[int, int]]): The second line segment defined by two points.

    Returns:
        bool: True if the line segments intersect, False otherwise.
    '''
    a, b = line1
    c, d = line2

	# Check if the segments are collinear and overlap
    if cross_prod(c, a, d) == 0 and cross_prod(c, b, d) == 0:
        return intervals_overlap(a[0], b[0], c[0], d[0]) and intervals_overlap(a[1], b[1], c[1], d[1])
	
	# Check for intersection using cross product signs
    return cross_prod_sign(cross_prod(a, b, c)) != cross_prod_sign(cross_prod(a, b, d)) and \
		cross_prod_sign(cross_prod(c, d, a)) != cross_prod_sign(cross_prod(c, d, b))


def edge_overlapping(shape1_coords:list[tuple[int, int]], shape2_coords:list[tuple[int, int]]) -> bool:
	'''
	Check if two shapes are touching at their edges.

	For every vertex pair in shape1 (which creates a line segment):
		For every vertex pair in shape2 (which creates a line segment):
			- Check if the two line segments intersect.
			- If they do, return True.
	Otherwise, return False.

	Args:
		shape1_coords (list[tuple[int, int]]): The coordinates of the first shape.
		shape2_coords (list[tuple[int, int]]): The coordinates of the second shape.
	
	Returns:
		bool: True if the shapes are touching at their edges, False otherwise.
	'''
	# Iterate through each edge of shape1
	for i in range(len(shape1_coords)):
		shape1_v1 = shape1_coords[i]
		shape1_v2 = shape1_coords[(i + 1) % len(shape1_coords)]
		# Iterate through each edge of shape2
		for j in range(len(shape2_coords)):
			shape2_v1 = shape2_coords[j]
			shape2_v2 = shape2_coords[(j + 1) % len(shape2_coords)]
			# Check if the two line segments intersect
			if line_segments_intersect((shape1_v1, shape1_v2), (shape2_v1, shape2_v2)):
				return True

	return False

def rectangularly_overlapping(shape1_coords:list[tuple[int, int]], shape2_coords:list[tuple[int, int]]) -> bool:
	'''
	Check if two shapes are overlapping based on their bounding boxes.

	Args: 
		shape1_coords (list[tuple[int, int]]): The coordinates of the first shape.
		shape2_coords (list[tuple[int, int]]): The coordinates of the second shape.
	
	Returns:
		bool: True if the shapes are overlapping, False otherwise.
	'''
	# Get the bounding boxes of both shapes
	shape1_x_min, shape1_y_min, shape1_x_max, shape1_y_max = get_boundaries(shape1_coords)
	shape2_x_min, shape2_y_min, shape2_x_max, shape2_y_max = get_boundaries(shape2_coords)

	# Check if the bounding boxes overlap
	return intervals_overlap(shape1_x_min, shape1_x_max, shape2_x_min, shape2_x_max) and \
		intervals_overlap(shape1_y_min, shape1_y_max, shape2_y_min, shape2_y_max)

def area_of_rectangle(shape_x_min:int, shape_y_min:int, shape_x_max:int, shape_y_max:int) -> int:
	'''
	Calculate the area of a rectangle defined by its bounding box.

	Args:
		shape_x_min (int): Minimum x-coordinate.
		shape_y_min (int): Minimum y-coordinate.
		shape_x_max (int): Maximum x-coordinate.
		shape_y_max (int): Maximum y-coordinate.
	
	Returns:
		int: The area of the rectangle.
	'''
	return (shape_x_max - shape_x_min) * (shape_y_max - shape_y_min)

def is_contained(shape1_coords:list[tuple[int, int]], shape2_coords:list[tuple[int, int]]) -> bool:
	'''
	Check if one shape is contained within another shape.

	Args:
		shape1_coords (list[tuple[int, int]]): The coordinates of the first shape.
		shape2_coords (list[tuple[int, int]]): The coordinates of the second shape.
	
	Returns:
		bool: True if shape1 is contained within shape2, False otherwise.
	'''
	# Get the bounding boxes of both shapes
	shape1_x_min, shape1_y_min, shape1_x_max, shape1_y_max = get_boundaries(shape1_coords)
	shape2_x_min, shape2_y_min, shape2_x_max, shape2_y_max = get_boundaries(shape2_coords)

	# Calculate the area of overlap
	x_overlap = min(shape1_x_max, shape2_x_max) - max(shape1_x_min, shape2_x_min)
	y_overlap = min(shape1_y_max, shape2_y_max) - max(shape1_y_min, shape2_y_min)
	area_of_overlap = x_overlap * y_overlap

	# Calculate the area of both shapes
	area_of_shape1 = area_of_rectangle(shape1_x_min, shape1_y_min, shape1_x_max, shape1_y_max)
	area_of_shape2 = area_of_rectangle(shape2_x_min, shape2_y_min, shape2_x_max, shape2_y_max) 

	# Check if the area of overlap is equal to the area of either shape
	return area_of_overlap == area_of_shape1 or area_of_overlap == area_of_shape2


def is_shape_overlapped_any(shape:turtle.Turtle, shapes:list[turtle.Turtle]) -> bool:
	'''
	Check if shape is overlapped with any of the shapes.
	By checking for rectangular overlap first, 
	then checking for edge overlap or containment.
	- If the bounding boxes of the two shapes overlap, 
		then check for edge overlap or containment.

	Args:
		shape (turtle.Turtle): The shape to check for overlap.
		shapes (list[turtle.Turtle]): List of shapes to check overlap with.
	
	Returns:
		bool: True if the shape
	'''
	for s in shapes:
		shape_coords, s_coords = get_coordinates(shape), get_coordinates(s)
		if rectangularly_overlapping(shape_coords, s_coords):
			if edge_overlapping(shape_coords, s_coords) or is_contained(shape_coords, s_coords):
				return True

	return False

############################################
################## template ################
############################################

def create_shape(shape:turtle.Turtle, color:str, sz_x:int = 1, sz_y:int = 1) -> turtle.Turtle:
	'''
	Create a turtle shape with specified parameters.
	
	Args:
		shape (turtle.Turtle): The base shape for the turtle.
		color (str): The color to set for the turtle.
		sz_x (int, optional): Horizontal stretch factor for the shape. Defaults to 1.
		sz_y (int, optional): Vertical stretch factor for the shape. Defaults to 1.
	
	Returns:
		turtle.Turtle: A configured turtle object with specified shape, color, and size.
	'''
	t = turtle.Turtle(shape)
	t.up()
	t.color(color)
	t.shapesize(sz_y, sz_x)
	return t

def get_random_home_position(range_x:list[int], range_y:list[int]) -> tuple[int,int]:
	'''
	Generates a random (x, y) coordinate tuple by sampling from 
	the provided x and y coordinate ranges.
	
	Args:
		range_x (list[int]): A list of possible x-coordinate values to sample from.
		range_y (list[int]): A list of possible y-coordinate values to sample from.
	
	Returns:
		tuple[int, int]: A randomly selected (x, y) coordinate pair.
	'''
	x = random.sample(range_x, 1)[0]
	y = random.sample(range_y, 1)[0]   
	return (x,y)

def place_a_random_shape(shape:turtle.Turtle, started:float, duration:int) -> None:
	'''
	Repeatedly tries to place the given shape at random coordinates 
	within the predefined canvas range.
	If the shape does not overlap with existing shapes, 
	it is added to the global shapes list and the screen is updated.
	
	Args:
		shape (turtle.Turtle): The turtle shape to be placed on the canvas.
		started (float): The timestamp when the placement process began.
		duration (int): The maximum time allowed for attempting to place the shape.
	'''
	while time.time() - started <= duration:
		x, y = get_random_home_position(g_range_x, g_range_y)
		shape.goto(x, y)
		if is_shape_overlapped_any(shape, g_shapes) is False:
			g_shapes.append(shape)
			g_screen.title(f'{YOUR_ID} - {len(g_shapes)}')
			g_screen.update()
			break

def fill_canvas_with_random_shapes(shapes:list[turtle.Turtle], colors:list[str], 
						 stretch_factor:int, duration:int) -> float:
	'''
	Fills the canvas with randomly positioned and colored shapes 
	within a specified time duration.
	
	Args:
		shapes (list[turtle.Turtle]): A list of available polygon shapes to choose from.
		colors (list[str]): A list of available colors to apply to the shapes.
		stretch_factor (int): The factor by which to stretch the shapes.
		duration (int): The maximum time allowed for placing shapes.
	
	Returns:
		float: The timestamp when the shape placement process started.
	'''
	started = time.time()
	while time.time() - started <= duration:
		shape = random.sample(shapes,1)[0]
		color = random.sample(colors,1)[0]
		turtle_obj = create_shape(shape, color, stretch_factor, stretch_factor)
		place_a_random_shape(turtle_obj, started, duration)

	return started


def import_custom_shapes(file_name:str) -> list[str]:
	'''
	Import custom turtle shapes from a file with predefined shape names and coordinates,
	where each line contains a shape name and its coordinates separated by a colon.
	
	Add each shape to the turtle screen and returns a list of imported shape names.

	Args:
		file_name (str): Path to the file containing custom shape definitions.

	Returns:
		list[str]: A list of names of the imported custom shapes.
	'''
	shapes = []
	with open(file_name, 'r') as f:
		for line in f.readlines():
			if line.find(':') == -1:
				continue
			name, coordinates = line.split(':')
			coordinates = eval(coordinates) # ok for internal use
			g_screen.addshape(name, coordinates)
			shapes.append(name)

	return shapes
	

def setup_canvas_ranges(w:int, h:int, span:float=0.8, step:int=10) -> tuple[list[int], list[int]]:
	'''
	Calculate valid coordinate ranges for canvas placement.
	
	Args:
		w (int): Canvas width.
		h (int): Canvas height.
		span (float, optional): Proportion of canvas to use. Defaults to 0.8.
		step (int, optional): Increment between coordinate values. Defaults to 10.
	
	Returns:
		tuple[list[int], list[int]]: A tuple containing x and y coordinate ranges, 
		centered at (0,0) within the specified canvas span.
	'''
	sz_w, sz_h = int(w/2*span), int(h/2*span)
	return range(-sz_w, sz_w, step), range(-sz_h, sz_h, step)

def setup_screen() -> turtle.Screen:
	'''
	Initialize and configure a turtle graphics screen with specific settings.

	Sets up a screen with auto-refresh disabled, predefined dimensions, 
	and logo mode orientation to prevent custom shape rotation.

	Returns:
		turtle.Screen: A configured turtle graphics screen ready for drawing.
	'''
	scrn = turtle.Screen()
	scrn.tracer(0)  # disable auto refresh
	scrn.setup(SCREEN_DIM_X, SCREEN_DIM_Y, starty=10)
	scrn.mode("logo") # heading up north to avoid rotation of custom shapes

	return scrn

def get_time_str(time_sec) -> str:
	'''
	Convert a timestamp in seconds to a formatted time string.

	Args:
		time_sec (float): The timestamp in seconds since the epoch.

	Returns:
		str: A formatted time string in "HH:MM:SS" format.
	'''
	struct_time = time.localtime(time_sec)
	return time.strftime("%H:%M:%S", struct_time)

def show_result(started:float, count:int) -> None:
	'''
	Display the final results of the drawing process, 
	including student ID, start and end times, duration, and shape count.
	
	Args:
		started (float): The timestamp when the drawing process began.
		count (int): The total number of shapes drawn during the process.
	
	Side effects:
		- Updates the screen title with ID, timing and count information
		- Changes screen background color to black
		- Prints student ID and shape count to console
	'''
	ended = time.time()	# end time 
	start_time = get_time_str(started)
	end_time = get_time_str(ended)
	diff = round(ended-started,2)

	g_screen.title(f'{YOUR_ID} {start_time} - {end_time} - {diff} - {count}')
	g_screen.bgcolor('black')
	print(f'{YOUR_ID},{count}')	# output your student id and shape count

def prompt(prompt:str, default:any) -> str:
	'''
	Prompts the user for input with a default value.
	
	Args:
		prompt (str): The input prompt message to display.
		default (any): The default value to return if no input is provided.
	
	Returns:
		str: The user's input, or the default value if no input is given.
	'''
	ret = input(f'{prompt} (default is {default}) >')
	return default if ret == "" else ret

def prompt_input() -> tuple[int,int,int,str]:
	'''
	Interactively prompt the user for drawing configuration parameters.
	
	Prompts for and validates user inputs for:
	- Minimum shape stretch value
	- Random seed for reproducibility
	- Drawing duration
	- Termination preference
	
	Returns:
		tuple[int,int,int,str]: A tuple containing (min_stretch, seed, duration, termination)
		with each value validated against predefined constraints.
	
	Raises:
		AssertionError: If any input value is outside its allowed range.
	'''
	min_stretch = int(prompt("Stretch Value", 1))
	assert MIN_STRETCH <= min_stretch <= MAX_STRETCH, \
		f"Stretch Value out of range {MIN_STRETCH} - {MAX_STRETCH}"
	
	seed = int(prompt("Random Seed", 1))
	assert MIN_SEED <= seed <= MAX_SEED, \
		f"Invalid Random Seed out of range {MIN_SEED} - {MAX_SEED}"
	
	duration = int(prompt("Duration (s)", 5))
	assert MIN_DURATION <= duration <= MAX_DURATION, \
		f"Invalid Duration out of range {MIN_DURATION} - {MAX_DURATION}"
	
	termination = prompt("Terminate", 'n')
	assert termination in ('y', 'n'), "Invalid Termination, must be y or n"

	return min_stretch, seed, duration, termination

def main() -> None:
	'''
	Main function to orchestrate the polygon drawing process.
	
	Configures the screen and canvas, imports custom shapes, prompts user for drawing parameters,
	initializes random seed, fills canvas with random shapes, and handles optional termination.
	
	Global variables are used to manage screen and drawing range state.
	
	Args:
		None
	
	Returns:
		None
	'''
	global g_screen, g_range_x, g_range_y
   
	g_screen = setup_screen()

	g_range_x, g_range_y = setup_canvas_ranges(g_screen.window_width(), 
											   g_screen.window_height(),
											   XY_SPAN, XY_STEP)
	
	shapes = import_custom_shapes(SHAPE_FILE)

	min_stretch, seed, duration, termination = prompt_input()

	random.seed(seed)

	started = fill_canvas_with_random_shapes(shapes, COLORS, min_stretch, duration)
	
	show_result(started, len(g_shapes))
	
	if termination == 'y':
		turtle.bye()

if __name__ == '__main__':
	main()
	g_screen.mainloop()
