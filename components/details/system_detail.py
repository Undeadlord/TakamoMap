"""
Enhanced System Detail Component
Displays detailed information about selected star systems
"""
import tkinter as tk
from tkinter import ttk
from .base_detail import BaseDetailPanel

class EnhancedSystemDetail(BaseDetailPanel):
    """Detail panel for star systems with enhanced context and explanations"""
    
    def load_entity(self, system_id):
        """Load and display system data with enhanced context"""
        system_details = self.app.data_loader.get_system_details(system_id)
        if not system_details:
            self.title_var.set("System Not Found")
            return
        
        # Set title and date
        system_code = system_details.get('location', 'Unknown System')
        star_type = system_details.get('type', 'Unknown Star Type')
        self.title_var.set(f"System {system_code} - {star_type}")
        self.date_var.set(f"Last updated: {self.format_date(system_details.get('date', 'Unknown'))}")
        
        # Debug output
        print(f"Loading system detail: {system_code} (ID: {system_id})")
        print(f"System planets count: {len(system_details.get('planets', []))}")
        
        # Create a summary section at the top
        self.add_section_header("System Overview")
        
        # Basic system information
        info_frame = ttk.Frame(self.scrollable_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # System code and position information
        code = system_details.get('location', 'Unknown')
        
        # Parse system code 
        # Format should be AAA1111 - where AAA is sector code, 111 is subsector code, and 1 is system number
        sector_code = ""
        subsector_code = ""
        system_num = ""
        
        if code and len(code) >= 7:
            sector_code = code[:3]
            subsector_code = code[3:6]
            system_num = code[6]
            
            subsector_full = sector_code + subsector_code
        
        code_tooltip = "A star system's code consists of the three-letter sector code, followed by three-digit subsector code, followed by system position (1-5)."
        code_label = self.create_info_item(info_frame, 0, 0, "System Code:", code, tooltip=code_tooltip, span=2)
        
        # Star type information
        star_type = system_details.get('type', 'Unknown')
        star_info = self.get_star_info(star_type)
        
        is_hazard = self.is_navigation_hazard(star_type)
        type_tooltip = star_info if star_info else "The classification of the star in this system."
        type_label = self.create_info_item(info_frame, 1, 0, "Star Type:", star_type, 
                                          tooltip=type_tooltip, span=2, is_highlight=is_hazard)
        
        # If it's a navigation hazard, add a warning
        if is_hazard:
            warning_label = ttk.Label(info_frame, text="⚠️ DANGER: This star will destroy any fleet that enters!", 
                                     foreground="red", font=("Arial", 10, "bold"))
            warning_label.grid(row=2, column=0, padx=5, pady=2, sticky="w", columnspan=2)
        
        # Add information about parent subsector
        if subsector_code:
            subsector_btn = ttk.Button(
                info_frame,
                text=f"Parent Subsector: {subsector_full}",
                command=lambda: self.app.select_entity('subsector', 
                                                      self.app.data_loader.get_subsector_id_by_code(subsector_full))
            )
            subsector_btn.grid(row=3, column=0, padx=5, pady=2, sticky="w", columnspan=2)
        
        # Position in subsector
        if system_num:
            position_tooltip = "Star systems in a subsector are numbered 1 through 5, with 1 being the first position."
            position_label = self.create_info_item(info_frame, 4, 0, "Position in Subsector:", 
                                                 f"{system_num} of 5", tooltip=position_tooltip, span=2)
        
        # Planets in system
        planets = system_details.get('planets', [])
        
        # If planets list is empty, try to find planets directly
        if not planets or len(planets) == 0:
            print("No planets found in system_details, trying direct query")
            system_loc = system_details.get('location', '')
            if system_loc:
                # Look for planets that have a location starting with the system code
                direct_planets = [p for p in self.app.data_loader.planets 
                                if p.get('location', '').startswith(system_loc)]
                print(f"Found {len(direct_planets)} planets by location code")
                
                # Add the planets to the system details
                if direct_planets:
                    system_details['planets'] = direct_planets
                    planets = direct_planets
        
            # Also try getting planets by system_id
            if not planets or len(planets) == 0:
                direct_planets = self.app.data_loader.get_planets_for_system(system_id)
                print(f"Found {len(direct_planets)} planets using get_planets_for_system")
                if direct_planets:
                    system_details['planets'] = direct_planets
                    planets = direct_planets
        
        planet_count = len(planets)
        planet_tooltip = "A star system can have up to 9 planets, numbered outward from the star."
        planet_label = self.create_info_item(info_frame, 5, 0, "Planets:", 
                                           f"{planet_count}/9", tooltip=planet_tooltip, span=2)
        
        # Add separator
        self.add_separator()
        
        # Planetary system visualization
        self.add_section_header("Planetary System")
        
        # Planetary system explanation
        planet_info = ttk.Label(self.scrollable_frame, 
                              text="Planets are numbered 1 through 9, from closest to farthest from the star. Each orbit may be empty due to natural absence or Nomad Platform movement.",
                              wraplength=550, justify="left")
        planet_info.pack(fill=tk.X, padx=10, pady=5)
        
        # Create a frame for the planets
        planets_frame = ttk.Frame(self.scrollable_frame)
        planets_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if planets:
            # Set up a consistent table layout
            # First create headers
            headers_frame = ttk.Frame(planets_frame)
            headers_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Headers with specific widths and positions
            headers = [
                {"text": "Orbit", "width": 50},
                {"text": "Type", "width": 180}, 
                {"text": "Size", "width": 50},
                {"text": "Status", "width": 100},
                {"text": "Owner", "width": 250},
                {"text": "Notes", "width": 180}
            ]
            
            # Create the header labels
            for i, header in enumerate(headers):
                label = ttk.Label(headers_frame, text=header["text"], font=("Arial", 10, "bold"))
                label.grid(row=0, column=i, padx=5, sticky=tk.W)
            
            # Add a separator
            ttk.Separator(planets_frame, orient="horizontal").pack(fill=tk.X, padx=5, pady=5)
            
            # Try to sort planets by orbit number
            try:
                sorted_planets = sorted(planets, key=lambda p: int(p.get('location', '0')[-1]) if p.get('location', '0')[-1].isdigit() else 9)
            except Exception as e:
                print(f"Error sorting planets: {e}")
                sorted_planets = planets
            
            # Create rows for each planet
            for i, planet in enumerate(sorted_planets):
                try:
                    row_frame = ttk.Frame(planets_frame)
                    row_frame.pack(fill=tk.X, padx=5, pady=2)
                    
                    # Orbit button
                    planet_code = planet.get('location', '')
                    orbit_num = planet_code[-1] if planet_code and len(planet_code) > 0 else '?'
                    
                    orbit_button = ttk.Button(
                        row_frame, 
                        text=orbit_num,
                        style="Wyvern.TButton" if hasattr(self.app, 'is_wyvern_location') and self.app.is_wyvern_location(planet_code) else "TButton",
                        width=4,
                        command=lambda p=planet.get('id'): self.app.select_planet(p)
                    )
                    orbit_button.grid(row=0, column=0, padx=5, sticky=tk.W)
                    
                    # Planet type
                    planet_type = self.get_planet_type(planet)
                    type_label = ttk.Label(row_frame, text=planet_type if planet_type else "Unknown")
                    type_label.grid(row=0, column=1, padx=5, sticky=tk.W)
                    
                    # Size
                    size = planet.get('size', '?')
                    size_label = ttk.Label(row_frame, text=size)
                    size_label.grid(row=0, column=2, padx=5, sticky=tk.W)
                    
                    # Status
                    status = planet.get('status', 'Unknown')
                    status_label = ttk.Label(row_frame, text=status)
                    status_label.grid(row=0, column=3, padx=5, sticky=tk.W)
                    
                    # Owner
                    owner = planet.get('owner', '')
                    is_wyvern = False
                    if owner and "WYVERN SUPREMACY" in owner.upper():
                        is_wyvern = True
                        owner_display = owner
                    else:
                        owner_display = owner if owner else "Unowned"
                    
                    owner_label = ttk.Label(
                        row_frame, 
                        text=owner_display,
                        foreground="#00ff00" if is_wyvern else "white"
                    )
                    owner_label.grid(row=0, column=4, padx=5, sticky=tk.W)
                    
                    # Notes
                    notes = []
                    if "HOMEWORLD" in status.upper():
                        notes.append("Home World")
                    if planet.get('extras'):
                        notes.append(planet.get('extras'))
                    
                    notes_text = "; ".join(notes) if notes else ""
                    notes_label = ttk.Label(row_frame, text=notes_text)
                    notes_label.grid(row=0, column=5, padx=5, sticky=tk.W)
                    
                    # Add tooltip
                    self.add_planet_tooltip(row_frame, planet)
                    
                    print(f"Added planet: {planet_code} (ID: {planet.get('id')})")
                except Exception as e:
                    print(f"Error creating planet row {i}: {e}")
        else:
            no_planets = ttk.Label(planets_frame, text="No planets found in this star system.")
            no_planets.pack(fill=tk.X, padx=10, pady=10)
            
            # Create test button to a possible planet
            try:
                system_loc = system_details.get('location', '')
                if system_loc:
                    # Try to construct a likely planet code
                    test_planet_loc = f"{system_loc}1"  # First planet in system
                    test_button = ttk.Button(
                        planets_frame,
                        text=f"Try navigate to planet {test_planet_loc}",
                        command=lambda: self.app.select_entity('planet', 
                                                             self.get_planet_id_by_code(test_planet_loc))
                    )
                    test_button.pack(fill=tk.X, padx=5, pady=2)
                    print(f"Created test button for possible planet {test_planet_loc}")
            except Exception as e:
                print(f"Error creating test button: {e}")
        
        # Add separator
        self.add_separator()
        
        # Add orbit information explanation
        self.add_section_header("Orbit Information")
        
        orbit_info_frame = ttk.Frame(self.scrollable_frame)
        orbit_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        orbit_text = (
            "In Takamo, planets are arranged by orbit number (1-9) from closest to farthest from the star. "
            "Some orbits may be empty due to natural formation or Nomad Platform movement.\n\n"
            "Special planet types:\n"
            "• Gas Giants: Typically very large (size 10)\n"
            "• Asteroid Belts: Very small (size 0-1)\n"
            "• Terrestrial Planets: Habitable worlds (sizes 1-9)\n\n"
            "All planets may be colonized and used as military bases, regardless of their type."
        )
        
        orbit_label = ttk.Label(orbit_info_frame, text=orbit_text, wraplength=550, justify="left")
        orbit_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Add separator
        self.add_separator()
        
        # Add navigation section
        self.add_section_header("Navigation")
        
        nav_frame = ttk.Frame(self.scrollable_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add parent subsector button
        if subsector_full:
            subsector_button = ttk.Button(
                nav_frame,
                text=f"Back to Subsector {subsector_full}",
                command=lambda: self.app.select_entity('subsector', 
                                                     self.app.data_loader.get_subsector_id_by_code(subsector_full))
            )
            subsector_button.pack(fill=tk.X, padx=5, pady=2)
        
        # Add parent sector button
        if sector_code:
            sector_button = ttk.Button(
                nav_frame,
                text=f"Back to Sector {sector_code}",
                command=lambda: self.app.select_entity('sector', 
                                                    self.app.data_loader.get_sector_id_by_code(sector_code))
            )
            sector_button.pack(fill=tk.X, padx=5, pady=2)
    
    def get_star_info(self, star_type):
        """Return information about a star type/class"""
        star_info = {
            "Blue - Type W": "One of the hottest and most massive star types.",
            "Blue - Type O": "Very hot, massive, and luminous star.",
            "Blue - Type B": "Hot, blue star, typically found in young clusters.",
            "Blue/White - Type A": "White or blue-white stars.",
            "White - Type F": "White stars slightly hotter than our Sun.",
            "Yellow - Type G": "Yellow stars similar to our Sun.",
            "Orange/Red - Type K": "Orange to red stars, cooler than our Sun.",
            "Red - Type M": "Red dwarf stars, the most common type.",
            "Red - Type C": "Carbon-rich red giant stars.",
            "Red - Type S": "Cool giant stars with unusual spectra.",
            "Bright Supergiant": "Extremely luminous evolved massive star.",
            "Faint Supergiant": "A less luminous supergiant star.",
            "Bright Giant": "Very luminous giant star.",
            "Normal Giant": "Standard giant star, an evolved star with expanded outer layers.",
            "Subgiant": "Star intermediate between a main sequence star and a giant star.",
            "Main Sequence": "A 'normal' star like our Sun, fusing hydrogen in its core.",
            "Subdwarf": "Stars with luminosity 1.5 to 2 magnitudes lower than main sequence stars.",
            "Binary": "A system of two stars orbiting around their common center of mass.",
            "Multiple": "A system of three or more stars orbiting around their common center of mass.",
            "White Dwarf Secondary": "A system containing a white dwarf, the dense remnant of a dead star.",
            "Blackhole Secondary": "A system containing a black hole, extremely hazardous to navigation."
        }
        
        for key, info in star_info.items():
            if key in star_type:
                return info
        
        return None
    
    def is_navigation_hazard(self, star_type):
        """Check if a star type is a navigation hazard"""
        hazardous_types = [
            "Blackhole",
            "Neutron Star",
            "Nova",
            "White Dwarf",
            "Black Dwarf"
        ]
        
        return any(hazard in star_type for hazard in hazardous_types)
    
    def get_planet_type(self, planet):
        """Determine the planet type based on attributes"""
        # First check for specific tags in the extras
        extras = planet.get('extras', '').lower()
        if 'gas giant' in extras:
            return "Gas Giant"
        if 'asteroid' in extras:
            return "Asteroid Belt"
        
        # Check size - gas giants are typically size 10
        size = planet.get('size')
        if size == '10' or size == 10:
            return "Gas Giant" 
        if size == '0' or size == 0:
            return "Asteroid Belt"
        
        # Otherwise it's a terrestrial planet
        return "Terrestrial"
    
    def add_planet_tooltip(self, widget, planet):
        """Add a detailed tooltip for a planet"""
        # Create tooltip content
        tooltip_text = f"Planet: {planet.get('location', 'Unknown')}\n"
        tooltip_text += f"Size: {planet.get('size', '?')}\n"
        tooltip_text += f"Status: {planet.get('status', 'Unknown')}\n"
        
        # Add atmosphere and hydrographics if available
        if planet.get('atmos'):
            tooltip_text += f"Atmosphere: {planet.get('atmos')}\n"
        if planet.get('hyp'):
            tooltip_text += f"Hydrographics: {planet.get('hyp')}\n"
        
        # Add owner if available
        if planet.get('owner'):
            tooltip_text += f"Owner: {planet.get('owner')}\n"
        
        # Add mining potential if available
        if planet.get('mpot'):
            tooltip_text += f"Mining Potential: {planet.get('mpot')}\n"
        
        # Add tech level if available
        if planet.get('tl') or planet.get('ptl'):
            tl = planet.get('tl', planet.get('ptl', '?'))
            tooltip_text += f"Tech Level: {tl}\n"
        
        # Add extra information
        if planet.get('extras'):
            tooltip_text += f"Notes: {planet.get('extras')}"
        
        self.add_tooltip(widget, tooltip_text)
    
    def get_planet_id_by_code(self, planet_code):
        """Get a planet ID by its location code"""
        for planet in self.app.data_loader.planets:
            if planet.get('location') == planet_code:
                return planet.get('id')
        return None