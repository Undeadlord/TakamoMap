"""
Enhanced Sector Detail Component
Displays detailed information about selected sectors with improved context
"""
import tkinter as tk
from tkinter import ttk
from components.details.base_detail import BaseDetailPanel

class EnhancedSectorDetail(BaseDetailPanel):
    """Detail panel for sectors with enhanced context and explanations"""
    
    def load_entity(self, sector_id):
        """Load and display sector data with enhanced context"""
        sector_details = self.app.data_loader.get_sector_details(sector_id)
        if not sector_details:
            self.title_var.set("Sector Not Found")
            return
        
        # Set title and date
        sector_code = sector_details.get('location', 'Unknown Sector')
        self.title_var.set(f"Sector {sector_code}")
        self.date_var.set(f"Last updated: {self.format_date(sector_details.get('date', 'Unknown'))}")
        
        # Initialize subsectors early to avoid scope issues
        subsectors = sector_details.get('subsectors', [])
        print(f"Loading sector detail: {sector_code} (ID: {sector_id})")
        print(f"Initial subsectors count: {len(subsectors)}")
        
        # Create a summary section at the top
        self.add_section_header("Sector Overview")
        
        # Basic sector information
        info_frame = ttk.Frame(self.scrollable_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sector code and coordinates
        code = sector_details.get('location', 'Unknown')
        
        # Parse sector code to get X,Y,Z coordinates (if three letters are present)
        x_coord, y_coord, z_coord = None, None, None
        if code and len(code) == 3:
            x_coord = ord(code[0]) - ord('A') + 1
            y_coord = ord(code[1]) - ord('A') + 1
            z_coord = ord(code[2]) - ord('A') + 1
        
        coord_text = code
        if x_coord and y_coord and z_coord:
            coord_text = f"{code} (X:{x_coord}, Y:{y_coord}, Z:{z_coord})"
        
        code_tooltip = "A sector's three-letter code defines its position in the galaxy. Each letter represents a coordinate along the X, Y, and Z axes."
        code_label = self.create_info_item(info_frame, 0, 0, "Sector Code:", coord_text, tooltip=code_tooltip, span=2)
        
        # Calculate distance from galactic center (MMM)
        center_distance = None
        if x_coord and y_coord and z_coord:
            center_coord = 13  # 'M' is the 13th letter, representing the center
            dx = x_coord - center_coord
            dy = y_coord - center_coord
            dz = z_coord - center_coord
            center_distance = round((dx**2 + dy**2 + dz**2)**0.5, 2)
            
            distance_tooltip = "The distance from the galactic center (sector MMM) in sector units."
            distance_label = self.create_info_item(info_frame, 1, 0, "Distance from Center:", 
                                                  f"{center_distance} sectors", 
                                                  tooltip=distance_tooltip, span=2)
        
        # Add information about sector size
        size_info = "Each sector is a cube 600 parsecs wide and contains 27 subsectors arranged in a 3×3×3 grid."
        size_label = self.create_info_item(info_frame, 2, 0, "Sector Size:", "600 parsecs", tooltip=size_info, span=2)
        
        # Navigation info
        move_tooltip = "Traveling a full sector costs 1 movement point. Your safe movement range depends on your empire's Tech Level."
        move_label = self.create_info_item(info_frame, 3, 0, "Movement Cost:", "1 sector movement point", 
                                           tooltip=move_tooltip, span=2)
        
        # Add separator
        self.add_separator()
        
        # Subsector grid visualization
        self.add_section_header("Subsector Grid")
        
        # Debug output
        print(f"Sector: {sector_code}, Subsectors found: {len(subsectors)}")
        for sub in subsectors:
            print(f"Subsector data: {sub}")
        
        # Create a simple grid with one clickable cell for each actual subsector
        grid_frame = ttk.Frame(self.scrollable_frame)
        grid_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # If there are subsectors, create buttons for them
        if subsectors:
            for subsector in subsectors:
                subsector_loc = subsector.get('location', '')
                subsector_id = subsector.get('id')
                
                # Create a button that represents this subsector
                button_text = f"Subsector {subsector_loc}"
                is_wyvern = self.app.is_wyvern_location(subsector_loc) if hasattr(self.app, 'is_wyvern_location') else False
                
                subsector_button = ttk.Button(
                    grid_frame,
                    text=button_text,
                    style="Wyvern.TButton" if is_wyvern else "TButton",
                    command=lambda sid=subsector_id: self.app.select_subsector(sid)
                )
                subsector_button.pack(padx=10, pady=5, fill=tk.X)
                print(f"Created button for subsector: {subsector_loc} (ID: {subsector_id})")
        else:
            # If no subsectors found in sector_details, try direct query
            print("No subsectors found in sector_details, trying direct query")
            try:
                # Get the sector code
                if sector_code:
                    print(f"Looking for subsectors with location starting with {sector_code}")
                    # Look for any subsectors that have a location starting with the sector code
                    direct_subsectors = [s for s in self.app.data_loader.subsectors 
                                     if s.get('location', '').startswith(sector_code)]
                    print(f"Found {len(direct_subsectors)} subsectors by location code")
                    
                    # If found, create buttons for them
                    if direct_subsectors:
                        for subsector in direct_subsectors:
                            subsector_loc = subsector.get('location', '')
                            subsector_id = subsector.get('id')
                            
                            button_text = f"Subsector {subsector_loc}"
                            is_wyvern = self.app.is_wyvern_location(subsector_loc) if hasattr(self.app, 'is_wyvern_location') else False
                            
                            subsector_button = ttk.Button(
                                grid_frame,
                                text=button_text,
                                style="Wyvern.TButton" if is_wyvern else "TButton",
                                command=lambda sid=subsector_id: self.app.select_subsector(sid)
                            )
                            subsector_button.pack(padx=10, pady=5, fill=tk.X)
                            print(f"Created button for subsector: {subsector_loc} (ID: {subsector_id})")
                    else:
                        # No subsectors found
                        no_subsectors = ttk.Label(grid_frame, text="No subsectors found for this sector.", foreground="#aaaaaa")
                        no_subsectors.pack(padx=10, pady=10)
            except Exception as e:
                print(f"Error finding subsectors: {e}")
                # No subsectors found
                no_subsectors = ttk.Label(grid_frame, text="No subsectors found for this sector.", foreground="#aaaaaa")
                no_subsectors.pack(padx=10, pady=10)
        
        # Add an explanation
        grid_info = ttk.Label(grid_frame, text="Click on a subsector to view its details.", 
                            wraplength=550, justify="left")
        grid_info.pack(fill=tk.X, padx=5, pady=5)
        
        # Add separator
        self.add_separator()
        
        # Subsector listing
        self.add_section_header("Explored Subsectors")
        
        # We've already handled finding subsectors above, so now we just need to display them
        if subsectors:
            print(f"Rendering {len(subsectors)} subsectors in listing")
            subsector_list_frame = ttk.Frame(self.scrollable_frame)
            subsector_list_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Create a scrollable list of subsectors
            for i, subsector in enumerate(subsectors):
                try:
                    subsector_item = ttk.Frame(subsector_list_frame)
                    subsector_item.pack(fill=tk.X, padx=5, pady=2)
                    
                    subsector_loc = subsector.get('location', '')
                    subsector_id = subsector.get('id')
                    
                    # If subsector has stars property, get the count, otherwise just show 0
                    star_count = len(subsector.get('stars', []))
                    
                    # Parse the subsector coordinates (if 3 digits are present after the sector code)
                    if subsector_loc and len(subsector_loc) >= 6:
                        sector_code = subsector_loc[:3]
                        subsector_coords = subsector_loc[3:6]
                        
                        # Try to parse coordinates
                        try:
                            x = int(subsector_coords[0])
                            y = int(subsector_coords[1])
                            z = int(subsector_coords[2])
                            coord_text = f"{subsector_loc} (X:{x}, Y:{y}, Z:{z})"
                        except:
                            coord_text = subsector_loc
                    else:
                        coord_text = subsector_loc
                    
                    # Create a button that navigates to the subsector when clicked
                    print(f"Creating button for subsector: {subsector_loc} (ID: {subsector_id})")
                    nav_button = ttk.Button(
                        subsector_item, 
                        text=f"{coord_text} - {star_count} star{'s' if star_count != 1 else ''}",
                        command=lambda s=subsector_id: self.app.select_subsector(s)
                    )
                    nav_button.pack(fill=tk.X, padx=5, pady=2)
                except Exception as e:
                    print(f"Error creating subsector item {i}: {e}")
        else:
            # No subsector data found for this sector
            no_data = ttk.Label(self.scrollable_frame, text="No subsector data available for this sector.")
            no_data.pack(fill=tk.X, padx=10, pady=10)