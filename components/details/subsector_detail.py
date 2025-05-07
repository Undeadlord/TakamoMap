"""
Enhanced Subsector Detail Component
Displays detailed information about selected subsectors
"""
import tkinter as tk
from tkinter import ttk
from .base_detail import BaseDetailPanel

class EnhancedSubsectorDetail(BaseDetailPanel):
    """Detail panel for subsectors with enhanced context and explanations"""
    
    def load_entity(self, subsector_id):
        """Load and display subsector data with enhanced context"""
        subsector_details = self.app.data_loader.get_subsector_details(subsector_id)
        if not subsector_details:
            self.title_var.set("Subsector Not Found")
            return
        
        # Set title and date
        subsector_code = subsector_details.get('location', 'Unknown Subsector')
        self.title_var.set(f"Subsector {subsector_code}")
        self.date_var.set(f"Last updated: {self.format_date(subsector_details.get('date', 'Unknown'))}")
        
        # Add debug output
        print(f"Loading subsector detail: {subsector_code} (ID: {subsector_id})")
        print(f"Subsector systems count: {len(subsector_details.get('systems', []))}")
        
        # Create a summary section at the top
        self.add_section_header("Subsector Overview")
        
        # Basic subsector information
        info_frame = ttk.Frame(self.scrollable_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Subsector code and coordinates
        code = subsector_details.get('location', 'Unknown')
        
        # Parse subsector code 
        # Format should be AAA111 - where AAA is sector code and 111 is subsector code
        sector_code = ""
        x_coord, y_coord, z_coord = None, None, None
        
        if code and len(code) >= 6:
            sector_code = code[:3]
            subsector_coords = code[3:6]
            
            if len(subsector_coords) == 3 and subsector_coords.isdigit():
                x_coord = int(subsector_coords[0])
                y_coord = int(subsector_coords[1])
                z_coord = int(subsector_coords[2])
        
        coord_text = code
        if x_coord and y_coord and z_coord:
            coord_text = f"{code} (X:{x_coord}, Y:{y_coord}, Z:{z_coord})"
        
        code_tooltip = "A subsector's code consists of the three-letter sector code followed by three numbers representing the X, Y, Z coordinates within the sector (each from 1-3)."
        code_label = self.create_info_item(info_frame, 0, 0, "Subsector Code:", coord_text, tooltip=code_tooltip, span=2)
        
        # Add information about parent sector
        parent_sector = f"{sector_code}" if sector_code else "Unknown"
        sector_link = ttk.Button(
            info_frame, 
            text=f"Parent Sector: {parent_sector}",
            command=lambda: self.app.select_entity('sector', self.app.data_loader.get_sector_id_by_code(sector_code))
        )
        sector_link.grid(row=1, column=0, padx=5, pady=2, sticky="w", columnspan=2)
        
        # Add separator
        self.add_separator()
        
        # If systems are missing, try to find them directly
        systems = subsector_details.get('systems', [])
        if not systems or len(systems) == 0:
            print("No systems found in subsector_details, trying direct query")
            subsector_loc = subsector_details.get('location', '')
            if subsector_loc:
                # Look for systems that have a location starting with the subsector code
                direct_systems = [s for s in self.app.data_loader.systems 
                              if s.get('location', '').startswith(subsector_loc)]
                print(f"Found {len(direct_systems)} systems by location code")
                
                # Add the systems to the subsector details
                if direct_systems:
                    subsector_details['systems'] = direct_systems
                    systems = direct_systems
        
            # Also try getting systems by subsector_id
            if not systems or len(systems) == 0:
                direct_systems = self.app.data_loader.get_systems_for_subsector(subsector_id)
                print(f"Found {len(direct_systems)} systems using get_systems_for_subsector")
                if direct_systems:
                    subsector_details['systems'] = direct_systems
                    systems = direct_systems
        
        # Star systems section
        self.add_section_header("Star Systems")
        
        # Star system explanation
        sys_info = ttk.Label(self.scrollable_frame, 
                            text="A subsector can contain up to 5 star systems. Each star system is numbered from 1 to 5, and may contain up to 9 planets.",
                            wraplength=550, justify="left")
        sys_info.pack(fill=tk.X, padx=10, pady=5)
        
        # Systems list
        systems_frame = ttk.Frame(self.scrollable_frame)
        systems_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if systems:
            # Set up a consistent table layout
            # First create headers
            headers_frame = ttk.Frame(systems_frame)
            headers_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Headers with specific widths and positions
            headers = [
                {"text": "System", "width": 120},
                {"text": "Star Type", "width": 320}, 
                {"text": "Planets", "width": 80},
                {"text": "Details", "width": 180}
            ]
            
            # Create the header labels
            for i, header in enumerate(headers):
                label = ttk.Label(headers_frame, text=header["text"], font=("Arial", 10, "bold"))
                label.grid(row=0, column=i, padx=5, sticky=tk.W)
            
            # Add a separator
            ttk.Separator(systems_frame, orient="horizontal").pack(fill=tk.X, padx=5, pady=5)
            
            # Create rows for each system
            for i, system in enumerate(systems):
                try:
                    row_frame = ttk.Frame(systems_frame)
                    row_frame.pack(fill=tk.X, padx=5, pady=2)
                    
                    # System button
                    system_loc = system.get('location', 'Unknown')
                    system_id = system.get('id', 'Unknown')
                    
                    system_button = ttk.Button(
                        row_frame, 
                        text=system_loc,
                        style="Wyvern.TButton" if hasattr(self.app, 'is_wyvern_location') and self.app.is_wyvern_location(system_loc) else "TButton",
                        width=12,
                        command=lambda s=system_id: self.app.select_system(s)
                    )
                    system_button.grid(row=0, column=0, padx=5, sticky=tk.W)
                    
                    # Star Type
                    system_type = system.get('type', 'Unknown')
                    type_label = ttk.Label(row_frame, text=system_type)
                    type_label.grid(row=0, column=1, padx=5, sticky=tk.W)
                    
                    # Planet Count
                    planet_count = len(system.get('planets', [])) if isinstance(system.get('planets', []), list) else system.get('planets', 0)
                    planet_label = ttk.Label(row_frame, text=str(planet_count))
                    planet_label.grid(row=0, column=2, padx=5, sticky=tk.W)
                    
                    # Details
                    details = system.get('extras', '')
                    details_label = ttk.Label(row_frame, text=details)
                    details_label.grid(row=0, column=3, padx=5, sticky=tk.W)
                    
                    print(f"Added system row: {system_loc} (ID: {system_id}) with {planet_count} planets")
                except Exception as e:
                    print(f"Error creating system row {i}: {e}")
        else:
            # No systems found message
            no_systems = ttk.Label(systems_frame, text="No star systems found in this subsector.") 
            no_systems.pack(fill=tk.X, padx=10, pady=10)
            
            # Create test button to navigate to a system if we know one should exist
            try:
                subsector_loc = subsector_details.get('location', '')
                if subsector_loc:
                    # Try to construct a likely system code
                    test_system_loc = f"{subsector_loc}1"  # First system in subsector
                    test_button = ttk.Button(
                        systems_frame,
                        text=f"Try navigate to system {test_system_loc}",
                        command=lambda: self.app.select_entity('system', 
                                                             self.app.data_loader.get_system_id_by_code(test_system_loc))
                    )
                    test_button.pack(fill=tk.X, padx=5, pady=2)
                    print(f"Created test button for possible system {test_system_loc}")
            except Exception as e:
                print(f"Error creating test button: {e}")