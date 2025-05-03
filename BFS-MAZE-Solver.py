import tkinter as tk
import random
import time
from collections import deque

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # 1 represents walls, 0 represents paths
        self.maze = [[1 for _ in range(width)] for _ in range(height)]
        
    def generate_maze(self):
        # Start with all walls
        self.maze = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        # Starting point
        start_x = random.randint(0, (self.width - 3) // 2) * 2 + 1
        start_y = random.randint(0, (self.height - 3) // 2) * 2 + 1
        
        # Set starting point as path
        self.maze[start_y][start_x] = 0
        
        # Stack for backtracking
        stack = [(start_x, start_y)]
        
        # Directions: right, down, left, up
        directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]
        
        while stack:
            current_x, current_y = stack[-1]
            
            # Find unvisited neighbors
            neighbors = []
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                
                if (0 <= nx < self.width and 0 <= ny < self.height and 
                    self.maze[ny][nx] == 1):
                    neighbors.append((nx, ny, dx, dy))
            
            if neighbors:
                # Choose a random unvisited neighbor
                next_x, next_y, dx, dy = random.choice(neighbors)
                
                # Remove the wall between current cell and chosen cell
                self.maze[current_y + dy // 2][current_x + dx // 2] = 0
                
                # Mark the chosen cell as visited
                self.maze[next_y][next_x] = 0
                
                # Push the chosen cell to the stack
                stack.append((next_x, next_y))
            else:
                # Backtrack
                stack.pop()
        
        # Set entrance and exit
        self.maze[1][0] = 0  # Entrance
        self.maze[self.height - 2][self.width - 1] = 0  # Exit
        
        # Set start and end points
        self.start = (0, 1)
        self.end = (self.width - 1, self.height - 2)
        
        return self.maze, self.start, self.end

class MazeSolver:
    def __init__(self, maze, start, end):
        self.maze = maze
        self.height = len(maze)
        self.width = len(maze[0])
        self.start = start
        self.end = end
        
    def solve_bfs(self, callback=None):
        visited = set([self.start])
        queue = deque([(self.start, [self.start])])
        
        while queue:
            (x, y), path = queue.popleft()
            
            if (x, y) == self.end:
                return path
            
            if callback:
                callback(x, y, path)
                time.sleep(0.01)  # Slow down for visualization
            
            # Check all four directions
            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                nx, ny = x + dx, y + dy
                
                if (0 <= nx < self.width and 0 <= ny < self.height and 
                    self.maze[ny][nx] == 0 and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        
        return None  # No path found

class MazeGUI:
    def __init__(self, root, width=31, height=21):
        self.root = root
        self.root.title("BFS Maze Solver")
        
        self.width = width
        self.height = height
        self.cell_size = 20
        
        self.canvas_width = self.width * self.cell_size
        self.canvas_height = self.height * self.cell_size
        
        # Frame for canvas
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Canvas for maze
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            width=self.canvas_width, 
            height=self.canvas_height,
            bg="white"
        )
        self.canvas.pack()
        
        # Frame for controls
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        
        # Algorithm label
        self.algorithm_label = tk.Label(
            self.control_frame, 
            text="Algorithm: Breadth-First Search (BFS)",
            font=("Arial", 10, "bold")
        )
        self.algorithm_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Description
        self.description = tk.Label(
            self.control_frame,
            text="BFS explores all neighbor nodes at the present depth before moving to nodes at the next depth. It guarantees the shortest path in an unweighted graph.",
            wraplength=200,
            justify=tk.LEFT
        )
        self.description.pack(anchor=tk.W, pady=(0, 15))
        
        # Buttons
        self.generate_button = tk.Button(
            self.control_frame, 
            text="Generate New Maze", 
            command=self.generate_maze
        )
        self.generate_button.pack(fill=tk.X, pady=(5, 5))
        
        self.solve_button = tk.Button(
            self.control_frame, 
            text="Solve Maze with BFS", 
            command=self.solve_maze
        )
        self.solve_button.pack(fill=tk.X, pady=5)
        
        self.clear_button = tk.Button(
            self.control_frame, 
            text="Clear Solution", 
            command=self.clear_solution
        )
        self.clear_button.pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            self.control_frame, 
            textvariable=self.status_var,
            wraplength=200
        )
        self.status_label.pack(pady=(20, 0))
        
        # Initialize maze
        self.generator = MazeGenerator(self.width, self.height)
        self.maze = None
        self.start = None
        self.end = None
        self.solver = None
        self.solution = None
        self.visited_cells = set()
        
        # Generate initial maze
        self.generate_maze()
    
    def generate_maze(self):
        self.status_var.set("Generating maze...")
        self.root.update()
        
        self.maze, self.start, self.end = self.generator.generate_maze()
        self.solver = MazeSolver(self.maze, self.start, self.end)
        self.solution = None
        self.visited_cells = set()
        
        self.draw_maze()
        self.status_var.set("Maze generated")
    
    def draw_maze(self):
        self.canvas.delete("all")
        
        for y in range(self.height):
            for x in range(self.width):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if self.maze[y][x] == 1:  # Wall
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="")
                else:  # Path
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="")
        
        # Draw start and end
        start_x, start_y = self.start
        end_x, end_y = self.end
        
        self.canvas.create_rectangle(
            start_x * self.cell_size, 
            start_y * self.cell_size, 
            (start_x + 1) * self.cell_size, 
            (start_y + 1) * self.cell_size, 
            fill="green", 
            outline=""
        )
        
        self.canvas.create_rectangle(
            end_x * self.cell_size, 
            end_y * self.cell_size, 
            (end_x + 1) * self.cell_size, 
            (end_y + 1) * self.cell_size, 
            fill="red", 
            outline=""
        )
    
    def update_cell(self, x, y, path):
        if (x, y) != self.start and (x, y) != self.end:
            self.canvas.create_rectangle(
                x * self.cell_size, 
                y * self.cell_size, 
                (x + 1) * self.cell_size, 
                (y + 1) * self.cell_size, 
                fill="lightblue", 
                outline=""
            )
        
        self.visited_cells.add((x, y))
        self.root.update()
    
    def draw_solution(self, solution):
        if not solution:
            self.status_var.set("No solution found!")
            return
        
        # Draw the solution path
        for x, y in solution:
            if (x, y) != self.start and (x, y) != self.end:
                self.canvas.create_rectangle(
                    x * self.cell_size, 
                    y * self.cell_size, 
                    (x + 1) * self.cell_size, 
                    (y + 1) * self.cell_size, 
                    fill="yellow", 
                    outline=""
                )
        
        # Redraw start and end
        start_x, start_y = self.start
        end_x, end_y = self.end
        
        self.canvas.create_rectangle(
            start_x * self.cell_size, 
            start_y * self.cell_size, 
            (start_x + 1) * self.cell_size, 
            (start_y + 1) * self.cell_size, 
            fill="green", 
            outline=""
        )
        
        self.canvas.create_rectangle(
            end_x * self.cell_size, 
            end_y * self.cell_size, 
            (end_x + 1) * self.cell_size, 
            (end_y + 1) * self.cell_size, 
            fill="red", 
            outline=""
        )
        
        self.solution = solution
        path_length = len(solution) - 1  # Subtract 1 because we count edges, not nodes
        self.status_var.set(f"Solution found! Path length: {path_length}")
    
    def solve_maze(self):
        if not self.maze:
            return
        
        self.clear_solution()
        self.status_var.set("Solving with BFS...")
        self.root.update()
        
        start_time = time.time()
        solution = self.solver.solve_bfs(callback=self.update_cell)
        end_time = time.time()
        
        self.draw_solution(solution)
        
        if solution:
            self.status_var.set(
                f"Solution found in {end_time - start_time:.2f} seconds\n"
                f"Path length: {len(solution) - 1}"
            )
        else:
            self.status_var.set("No solution found!")
    
    def clear_solution(self):
        self.visited_cells = set()
        self.solution = None
        self.draw_maze()
        self.status_var.set("Solution cleared")

def main():
    root = tk.Tk()
    app = MazeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()