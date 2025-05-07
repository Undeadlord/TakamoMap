"""
Map View Component
Provides a 2D projection of the 3D galaxy map with fixed click handling
"""
import tkinter as tk
from tkinter import ttk
import math
from utils.coordinates import get_coordinates_from_sector

class MapView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ttk.Frame(parent)
        
        # Canvas for drawing the map
        self.canvas_frame = ttk.Frame(self.frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='#1a1a2e', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        self.hscrollbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.vscrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.hscrollbar.set, yscrollcommand=self.vscrollbar.set)
        
        self.hscrollbar.pack(fill=tk.X, side=tk.BOTTOM)
        self.vscrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        # Legend/Info at bottom
        self.info_frame = ttk.Frame(self.frame)
        self.info_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        self.legend_frame = ttk.Frame(self.info_frame)
        self.legend_frame.pack(side=tk.LEFT, padx=5)
        
        # Add legend items
        self.create_legend_item(self.legend_frame, "#2196f3", "Standard Sector")
        self.create_legend_item(self.legend_frame, "#4caf50", "Selected Sector")
        self.create_legend_item(self.legend_frame, "#00ff00", "Wyvern Supremacy")
        
        # Add status label for debugging
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(self.info_frame, textvariable=self.status_var, font=("Arial", 8))
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        self.info_label = ttk.Label(self.info_frame, 
                                   text="Note: This is a 2D projection of the galaxy map. The Y axis (top-bottom) is not shown.")
        self.info_label.pack(side=tk.RIGHT)
        
        # Configuration for the map
        self.grid_size = 1200
        self.cell_size = 28
        self.margin = 40
        self.max_x = 26  # Increased from 20 to accommodate more sectors
        self.max_z = 26  # Increased from 20 to accommodate more sectors
        
        # Configure the canvas scrolling region
        self.canvas.configure(scrollregion=(0, 0, self.grid_size, self.grid_size))
        
        # Bind click event
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Hide initially
        self.hide()
    
    def create_legend_item(self, parent, color, text):
        """Create a legend item with color box and text"""
        frame = ttk.Frame(parent)
        frame.pack(side=tk.LEFT, padx=5)
        
        # Create color square (using canvas)
        canvas = tk.Canvas(frame, width=12, height=12, bg=color, highlightthickness=0)
        canvas.pack(side=tk.LEFT, padx=2)
        
        # Create label
        label = ttk.Label(frame, text=text, font=("Arial", 8))
        label.pack(side=tk.LEFT)
    
    def show(self):
        """Show the map view"""
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hide the map view"""
        self.frame.pack_forget()
    
    def update(self):
        """Update the map with current data"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw grid
        self.draw_grid()
        
        # Draw sectors
        self.draw_sectors()
        
        # Debug output
        self.print_sector_debug()
    
    def print_sector_debug(self):
        """Print debug information about sectors"""
        # Check if ANM exists
        anm_exists = False
        anm_coords = None
        
        for sector in self.app.data_loader.sectors:
            if sector['location'] == 'ANM':
                anm_exists = True
                anm_coords = get_coordinates_from_sector('ANM')
                break
        
        if anm_exists:
            status = f"ANM exists in data! Coords: X={anm_coords['x']}, Z={anm_coords['z']}"
            
            # Check if it's within bounds
            if anm_coords['x'] > self.max_x or anm_coords['z'] > self.max_z:
                status += f" - OUT OF BOUNDS (max X={self.max_x}, max Z={self.max_z})"
        else:
            status = "ANM sector NOT found in data"
            
        # Count total sectors
        status += f" | Total sectors: {len(self.app.data_loader.sectors)}"
        
        # Check planets in ANM
        anm_planets = [p for p in self.app.data_loader.planets if p['location'] and p['location'].startswith('ANM')]
        if anm_planets:
            status += f" | ANM planets: {len(anm_planets)}"
        
        self.status_var.set(status)
    
    def update_selection(self):
        """Update the visual selection state"""
        # Redraw to reflect the current selection
        self.update()
    
    def draw_grid(self):
        """Draw the grid lines"""
        # Draw horizontal grid lines
        for i in range(self.max_z + 1):
            y = self.margin + i * self.cell_size
            self.canvas.create_line(
                self.margin, y, 
                self.margin + self.max_x * self.cell_size, y,
                fill="#333333", width=1
            )
        
        # Draw vertical grid lines
        for i in range(self.max_x + 1):
            x = self.margin + i * self.cell_size
            self.canvas.create_line(
                x, self.margin,
                x, self.margin + self.max_z * self.cell_size,
                fill="#333333", width=1
            )
        
        # Draw axis labels
        self.canvas.create_text(
            self.margin + self.grid_size/4, self.margin - 20,
            text="X Axis", fill="#999999", anchor=tk.CENTER
        )
        self.canvas.create_text(
            self.margin - 20, self.margin + self.grid_size/4,
            text="Z Axis", fill="#999999", angle=90, anchor=tk.CENTER
        )
        
        # Draw coordinate numbers
        for i in range(self.max_x + 1):
            if i % 5 == 0:  # Only show every 5th coordinate
                x = self.margin + i * self.cell_size
                self.canvas.create_text(
                    x, self.margin - 5,
                    text=str(i), fill="#999999", anchor=tk.CENTER, font=("Arial", 7)
                )
        
        for i in range(self.max_z + 1):
            if i % 5 == 0:  # Only show every 5th coordinate
                z = self.margin + i * self.cell_size
                self.canvas.create_text(
                    self.margin - 5, z,
                    text=str(i), fill="#999999", anchor=tk.CENTER, font=("Arial", 7)
                )
    
    def has_wyvern_planet(self, sector_id):
        """Check if a sector contains any Wyvern Supremacy planets"""
        # Get all subsectors in this sector
        subsectors = self.app.data_loader.get_subsectors_for_sector(sector_id)
        
        for subsector in subsectors:
            # Get all systems in this subsector
            systems = self.app.data_loader.get_systems_for_subsector(subsector['id'])
            
            for system in systems:
                # Get all planets in this system
                planets = self.app.data_loader.get_planets_for_system(system['id'])
                
                # Check if any planet belongs to Wyvern Supremacy
                for planet in planets:
                    if planet['owner'] and "Wyvern Supremacy" in planet['owner']:
                        return True
        
        return False
    
    def draw_sectors(self):
        """Draw all sectors on the map"""
        drawn_count = 0
        out_of_bounds = 0
        
        # Dictionary to store canvas items by sector code for easier click handling
        self.sector_items = {}
        
        # Draw each sector
        for sector in self.app.data_loader.sectors:
            coords = get_coordinates_from_sector(sector['location'])
            
            # Skip if out of our display bounds
            if coords['x'] > self.max_x or coords['z'] > self.max_z:
                out_of_bounds += 1
                continue
            
            drawn_count += 1
            
            # Calculate position
            x = self.margin + coords['x'] * self.cell_size
            z = self.margin + coords['z'] * self.cell_size
            
            # Determine if selected
            is_selected = sector['id'] == self.app.selected_sector
            
            # Check if sector has any Wyvern Supremacy planets
            has_wyvern = self.has_wyvern_planet(sector['id'])
            
            # Determine color based on selection and ownership
            if is_selected:
                fill_color = "#4caf50"  # Selected sectors are always green
            elif has_wyvern:
                fill_color = "#00ff00"  # Wyvern sectors are bright green
            else:
                fill_color = "#2196f3"  # Default blue
            
            # Draw sector marker (rectangle)
            rect_size = self.cell_size * 2/3
            rect_id = self.canvas.create_rectangle(
                x - rect_size/2, z - rect_size/2,
                x + rect_size/2, z + rect_size/2,
                fill=fill_color,
                outline="white", width=1, 
                tags=(f"sector_{sector['id']}", f"code_{sector['location']}")
            )
            
            # Draw sector code
            text_id = self.canvas.create_text(
                x, z, text=sector['location'],
                fill="white", font=("Arial", 8), 
                tags=(f"sector_text_{sector['id']}", f"code_text_{sector['location']}")
            )
            
            # Store canvas items by sector code
            self.sector_items[sector['location']] = {
                'rect': rect_id,
                'text': text_id,
                'id': sector['id']
            }
        
        # Update debug status
        current_status = self.status_var.get()
        self.status_var.set(f"{current_status} | Drawn: {drawn_count} | Out of bounds: {out_of_bounds}")
    
    def on_canvas_click(self, event):
        """Handle click on the canvas"""
        # Convert to canvas coordinates if scrolled
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Find which sector was clicked, if any
        items = self.canvas.find_overlapping(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5)
        
        for item in items:
            tags = self.canvas.gettags(item)
            
            # First look for code tags (more reliable)
            for tag in tags:
                if tag.startswith("code_") and not tag.startswith("code_text_"):
                    sector_code = tag[5:]  # Extract sector code (e.g., "ANM")
                    print(f"Clicked on sector with code: {sector_code}")
                    
                    # Find sector with this code and select it
                    for sector in self.app.data_loader.sectors:
                        if sector['location'] == sector_code:
                            self.app.select_sector(sector['id'])
                            return
            
            # Fall back to ID-based tags if code tags not found
            for tag in tags:
                if tag.startswith("sector_") and not tag.startswith("sector_text_"):
                    try:
                        sector_id = int(tag.split("_")[1])
                        print(f"Clicked on sector with ID: {sector_id}")
                        self.app.select_sector(sector_id)
                        return
                    except (IndexError, ValueError):
                        pass