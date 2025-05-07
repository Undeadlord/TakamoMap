"""
Slice-based Map View Component
Provides a 2D slice view of the 3D galaxy map with Y-axis navigation
"""
import tkinter as tk
from tkinter import ttk
import math
from utils.coordinates import get_coordinates_from_sector

class SliceMapView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ttk.Frame(parent)
        
        # Y-axis level (A-Z)
        self.current_y_level = 'M'  # Default to M level
        
        # Define colors for different sector types
        self.color_standard = "#2196f3"  # Blue for standard sectors
        self.color_selected = "#ff9800"  # Orange for selected sector
        self.color_wyvern = "#4caf50"    # Green for Wyvern Supremacy sectors
        
        # Text colors with better contrast
        self.text_color_standard = "#ffffff"  # White text on blue
        self.text_color_selected = "#000000"  # Black text on orange
        self.text_color_wyvern = "#ffffff"    # White text on green
        
        # Configuration for the map
        self.grid_size = 1500  # Increased from 1200 to accommodate larger cells
        self.cell_size = 38  # Increased by 25% from 30
        self.margin = 50    # Increased from 40 for better spacing
        self.max_x = 26  # Show all possible X coordinates (A-Z)
        self.max_z = 26  # Show all possible Z coordinates (A-Z)
        
        # Create layout
        self.create_layout()
        
        # Configure the canvas scrolling region
        self.canvas.configure(scrollregion=(0, 0, self.grid_size, self.grid_size))
        
        # Hide initially
        self.hide()
    
    def create_layout(self):
        """Create the map view layout with Y-axis navigation"""
        # Top controls for Y-axis navigation
        self.controls_frame = ttk.Frame(self.frame)
        self.controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Y level navigation
        self.y_nav_frame = ttk.Frame(self.controls_frame)
        self.y_nav_frame.pack(side=tk.LEFT, padx=10)
        
        # Level label
        self.level_label = ttk.Label(self.y_nav_frame, text="Y Level:", font=("Arial", 10, "bold"))
        self.level_label.pack(side=tk.LEFT, padx=5)
        
        # Current level display
        self.level_var = tk.StringVar(value=f"{self.current_y_level}")
        self.level_display = ttk.Label(self.y_nav_frame, textvariable=self.level_var, 
                                      font=("Arial", 12, "bold"), width=2,
                                      background="#313244", foreground="white")
        self.level_display.pack(side=tk.LEFT, padx=5)
        
        # Up/Down buttons
        self.up_btn = ttk.Button(self.y_nav_frame, text="▲", width=3, 
                               command=self.move_level_up)
        self.up_btn.pack(side=tk.LEFT, padx=2)
        
        self.down_btn = ttk.Button(self.y_nav_frame, text="▼", width=3, 
                                 command=self.move_level_down)
        self.down_btn.pack(side=tk.LEFT, padx=2)
        
        # Quick navigation dropdown for Y levels
        self.quick_nav_frame = ttk.Frame(self.controls_frame)
        self.quick_nav_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(self.quick_nav_frame, text="Jump to:").pack(side=tk.LEFT, padx=5)
        
        # Create a list of all possible Y levels (A-Z)
        y_levels = [chr(65 + i) for i in range(26)]  # A-Z
        
        self.jump_var = tk.StringVar(value=self.current_y_level)
        self.jump_combo = ttk.Combobox(self.quick_nav_frame, textvariable=self.jump_var,
                                      values=y_levels, width=5, state="readonly")
        self.jump_combo.pack(side=tk.LEFT, padx=5)
        self.jump_combo.bind("<<ComboboxSelected>>", self.on_jump_selected)
        
        # Information about current view
        self.info_frame = ttk.Frame(self.controls_frame)
        self.info_frame.pack(side=tk.RIGHT, padx=10)
        
        info_text = "Showing sectors with middle coordinate: "
        self.info_label = ttk.Label(self.info_frame, text=info_text)
        self.info_label.pack(side=tk.LEFT)
        
        self.info_value = ttk.Label(self.info_frame, text=self.current_y_level, 
                                   font=("Arial", 10, "bold"))
        self.info_value.pack(side=tk.LEFT)
        
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
        self.legend_frame = ttk.Frame(self.frame)
        self.legend_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        # Add legend items with updated colors
        self.create_legend_item(self.legend_frame, self.color_standard, "Standard Sector")
        self.create_legend_item(self.legend_frame, self.color_selected, "Selected Sector")
        self.create_legend_item(self.legend_frame, self.color_wyvern, "Wyvern Supremacy")
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Bind mouse wheel events for scrolling
        # For Windows/Linux
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        # For Linux (X11)
        self.canvas.bind("<Button-4>", self.on_mousewheel_linux_up)
        self.canvas.bind("<Button-5>", self.on_mousewheel_linux_down)
        
        # Add key bindings for scrolling with arrow keys
        self.canvas.bind("<Up>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Down>", lambda e: self.canvas.yview_scroll(1, "units"))
        self.canvas.bind("<Left>", lambda e: self.canvas.xview_scroll(-1, "units"))
        self.canvas.bind("<Right>", lambda e: self.canvas.xview_scroll(1, "units"))
        
        # Make canvas focusable to receive key events
        self.canvas.config(takefocus=1)
        self.canvas.focus_set()
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling for Windows/MacOS"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_mousewheel_linux_up(self, event):
        """Handle mouse wheel up for Linux"""
        self.canvas.yview_scroll(-1, "units")
    
    def on_mousewheel_linux_down(self, event):
        """Handle mouse wheel down for Linux"""
        self.canvas.yview_scroll(1, "units")
    
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
    
    def move_level_up(self):
        """Move one level up in the Y axis (e.g., N -> M)"""
        # Convert to ASCII code, decrement (move up in the alphabet)
        current_code = ord(self.current_y_level)
        if current_code > ord('A'):
            new_code = current_code - 1
            self.set_y_level(chr(new_code))
    
    def move_level_down(self):
        """Move one level down in the Y axis (e.g., N -> O)"""
        # Convert to ASCII code, increment (move down in the alphabet)
        current_code = ord(self.current_y_level)
        if current_code < ord('Z'):
            new_code = current_code + 1
            self.set_y_level(chr(new_code))
    
    def on_jump_selected(self, event):
        """Handle selection from the jump to combobox"""
        selected_level = self.jump_var.get()
        self.set_y_level(selected_level)
    
    def set_y_level(self, level):
        """Set the current Y level and update the view"""
        if level >= 'A' and level <= 'Z':
            self.current_y_level = level
            self.level_var.set(level)
            self.info_value.config(text=level)
            self.update()  # Redraw the map
    
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
        
        # Draw sectors at current Y level
        self.draw_sectors()
    
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
        
        # Draw coordinate labels (A-Z) for X axis
        for i in range(self.max_x):
            x = self.margin + (i + 0.5) * self.cell_size
            label = chr(65 + i)  # A-Z
            self.canvas.create_text(
                x, self.margin - 15,
                text=label, fill="#cccccc", font=("Arial", 10)
            )
        
        # Draw coordinate labels (A-Z) for Z axis
        for i in range(self.max_z):
            z = self.margin + (i + 0.5) * self.cell_size
            label = chr(65 + i)  # A-Z
            self.canvas.create_text(
                self.margin - 15, z,
                text=label, fill="#cccccc", font=("Arial", 10)
            )
        
        # Draw axis labels
        self.canvas.create_text(
            self.margin + self.grid_size/4, self.margin - 30,
            text="X Axis", fill="#999999", anchor=tk.CENTER,
            font=("Arial", 12)
        )
        self.canvas.create_text(
            self.margin - 30, self.margin + self.grid_size/4,
            text="Z Axis", fill="#999999", angle=90, anchor=tk.CENTER,
            font=("Arial", 12)
        )
    
    def has_wyvern_planet(self, sector_id):
        """Check if a sector contains any Wyvern Supremacy planets"""
        try:
            # Get all subsectors in this sector
            subsectors = self.app.data_loader.get_subsectors_for_sector(sector_id)
            
            for subsector in subsectors:
                if not subsector:
                    continue
                    
                # Get all systems in this subsector
                systems = self.app.data_loader.get_systems_for_subsector(subsector.get('id'))
                
                for system in systems:
                    if not system:
                        continue
                        
                    # Get all planets in this system
                    planets = self.app.data_loader.get_planets_for_system(system.get('id'))
                    
                    # Check if any planet belongs to Wyvern Supremacy
                    for planet in planets:
                        if not planet:
                            continue
                            
                        if planet.get('owner') and "WYVERN SUPREMACY" in planet.get('owner', '').upper():
                            print(f"Found Wyvern planet in sector {sector_id}: {planet.get('location', 'Unknown')} - {planet.get('owner', 'Unknown')}")
                            return True
        except Exception as e:
            print(f"Error checking for Wyvern planets in sector {sector_id}: {e}")
        
        return False
    
    def draw_sectors(self):
        """Draw sectors at the current Y level"""
        # Dictionary to store canvas items by sector code for easier click handling
        self.sector_items = {}
        
        # Count for statistics
        visible_sectors = 0
        wyvern_sectors = 0
        
        # Process each sector
        for sector in self.app.data_loader.sectors:
            if not sector:
                continue
                
            # Get location safely with default
            location = sector.get('location', '')
            
            # Check if sector is at current Y level
            if len(location) == 3 and location[1] == self.current_y_level:
                try:
                    coords = get_coordinates_from_sector(location)
                    
                    # Calculate position (X and Z coordinates)
                    x = self.margin + coords['x'] * self.cell_size + self.cell_size/2
                    z = self.margin + coords['z'] * self.cell_size + self.cell_size/2
                    
                    # Determine if selected
                    is_selected = sector.get('id') == self.app.selected_sector
                    
                    # Check if sector has any Wyvern Supremacy planets (either directly or through cache)
                    has_wyvern = False
                    if hasattr(self.app, 'is_wyvern_location'):
                        has_wyvern = self.app.is_wyvern_location(location)
                        if has_wyvern:
                            print(f"Drawing Wyvern sector: {location}")
                            wyvern_sectors += 1
                    
                    if not has_wyvern:
                        has_wyvern = self.has_wyvern_planet(sector.get('id'))
                        if has_wyvern:
                            print(f"Drawing Wyvern sector (via has_wyvern_planet): {location}")
                            wyvern_sectors += 1
                    
                    # Determine color based on selection and ownership
                    if is_selected:
                        fill_color = self.color_selected  # Orange for selected
                        text_color = self.text_color_selected  # Black text on orange
                    elif has_wyvern:
                        fill_color = self.color_wyvern    # Green for Wyvern
                        text_color = self.text_color_wyvern  # White text on green
                    else:
                        fill_color = self.color_standard  # Blue for standard
                        text_color = self.text_color_standard  # White text on blue
                    
                    # Draw sector marker (circle for better visibility in grid)
                    # Increased size to 85% of cell size (from 80%)
                    rect_size = self.cell_size * 0.85
                    rect_id = self.canvas.create_oval(
                        x - rect_size/2, z - rect_size/2,
                        x + rect_size/2, z + rect_size/2,
                        fill=fill_color,
                        outline="white", width=2,  # Increased outline width for better visibility
                        tags=(f"sector_{sector.get('id')}", f"code_{location}")
                    )
                    
                    # Draw sector code with appropriate text color and larger font
                    text_id = self.canvas.create_text(
                        x, z, text=location,
                        fill=text_color, font=("Arial", 10, "bold"),  # Increased font size from 8 to 10
                        tags=(f"sector_text_{sector.get('id')}", f"code_text_{location}")
                    )
                    
                    # Store canvas items by sector code
                    self.sector_items[location] = {
                        'rect': rect_id,
                        'text': text_id,
                        'id': sector.get('id')
                    }
                    
                    visible_sectors += 1
                except Exception as e:
                    print(f"Error drawing sector {location}: {e}")
        
        print(f"Drew {visible_sectors} sectors at Y level {self.current_y_level}, including {wyvern_sectors} Wyvern sectors")
        
        # If no sectors at this level, show a message
        if visible_sectors == 0:
            x = self.grid_size / 2
            y = self.grid_size / 2
            self.canvas.create_text(
                x, y,
                text=f"No explored sectors at Y level {self.current_y_level}",
                fill="#cccccc", font=("Arial", 14),
                anchor=tk.CENTER
            )
    
    def on_canvas_click(self, event):
        """Handle click on the canvas"""
        # Convert to canvas coordinates if scrolled
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Find which sector was clicked, if any
        items = self.canvas.find_overlapping(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5)
        
        for item in items:
            tags = self.canvas.gettags(item)
            
            # Look for code tags
            for tag in tags:
                if tag.startswith("code_") and not tag.startswith("code_text_"):
                    sector_code = tag[5:]  # Extract sector code (e.g., "ANM")
                    print(f"Clicked on sector with code: {sector_code}")
                    
                    # Find sector with this code and select it
                    for sector in self.app.data_loader.sectors:
                        if sector and sector.get('location') == sector_code:
                            self.app.select_sector(sector.get('id'))
                            return
                    
                    # If sector code clicked but not found in data (edge case)
                    print(f"Warning: Clicked sector {sector_code} not found in data")
        
        # If we reached here, no valid sector was clicked
        print("Click detected, but no valid sector was found at this position")