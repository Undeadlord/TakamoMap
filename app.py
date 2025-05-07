"""
Takamo Galaxy Explorer - Main Application Component
Manages the overall UI structure and coordinates between components
"""
import tkinter as tk
from tkinter import ttk
from utils.data_loader import DataLoader
from views.slice_map_view import SliceMapView
from views.list_view import ListView
from components.details import EnhancedSectorDetail, EnhancedSubsectorDetail, EnhancedSystemDetail, EnhancedPlanetDetail
from components.common import StatsBar, HelpDialog

# Helper function to find sectors by code
def get_sector_by_code(sectors, code):
    """Find a sector by its location code"""
    if not code:
        return None
        
    for sector in sectors:
        if sector.get('location') == code:
            return sector
    return None

class App:
    def __init__(self, root, db_path):
        self.root = root
        self.data_loader = DataLoader(db_path)
        
        # Set up main frame and styling
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use 'clam' theme for better control
        self.configure_styles()
        
        # Initialize UI state - slice_map is now the default
        self.current_view = tk.StringVar(value="slice_map")
        self.current_list_mode = tk.StringVar(value="sectors")
        self.selected_sector = None
        self.selected_subsector = None
        self.selected_system = None
        self.selected_planet = None
        
        # Define colors for different entity types
        self.color_standard = "#2196f3"  # Blue for standard
        self.color_selected = "#ff9800"  # Orange for selected
        self.color_wyvern = "#4caf50"    # Green for Wyvern Supremacy
        
        # Create main container frames
        self.create_layout()
        
        # Create components
        self.setup_components()
        
        # Load data
        self.load_data()
        
        # Cache for Wyvern-owned location codes (to avoid repeated lookups)
        self.wyvern_locations = set()
        self.build_wyvern_locations_cache()
    
    def configure_styles(self):
        """Configure ttk styles for the application"""
        # Configure colors
        bg_dark = "#1e1e2e"
        bg_medium = "#313244"
        text_color = "#ffffff"  # Brighter white text for better contrast
        accent_color = "#89b4fa"
        
        # Main colors for entities
        self.color_standard = "#2196f3"  # Blue for standard
        self.color_selected = "#ff9800"  # Orange for selected
        self.color_wyvern = "#4caf50"    # Green for Wyvern Supremacy
        
        # Configure styles
        self.style.configure('TFrame', background=bg_dark)
        self.style.configure('TLabel', background=bg_dark, foreground=text_color)
        self.style.configure('TButton', background=bg_medium, foreground=text_color)
        self.style.configure('Bold.TLabel', background=bg_dark, foreground="#ff9800", font=('Arial', 10, 'bold'))
        
        # Button styles with improved text contrast
        self.style.configure('Selected.TButton', background=self.color_selected, foreground="#000000")  # Black text on orange
        self.style.configure('Wyvern.TButton', background=self.color_wyvern, foreground="#ffffff")     # White text on green
        
        self.style.configure('ViewTab.TButton', padding=5, font=('Arial', 10))
        self.style.configure('TNotebook', background=bg_dark)
        self.style.map('TButton',
            background=[('active', accent_color)],
            foreground=[('active', 'white')]
        )
        
        # Apply to root
        self.root.configure(background=bg_dark)
    
    def create_layout(self):
        """Create the main layout frames"""
        # Main container (split into left and right panels)
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Navigation
        self.left_panel = ttk.Frame(self.main_container, style='TFrame')
        
        # Top navigation tabs
        self.nav_tabs = ttk.Frame(self.left_panel)
        self.nav_tabs.pack(fill=tk.X, padx=5, pady=5)
        
        # View selection buttons (now only 2 options)
        self.slice_map_btn = ttk.Button(self.nav_tabs, text="Galaxy Map", 
                                      command=lambda: self.switch_view("slice_map"), 
                                      style="ViewTab.TButton")
        self.slice_map_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.list_btn = ttk.Button(self.nav_tabs, text="List View", 
                                  command=lambda: self.switch_view("list"), 
                                  style="ViewTab.TButton")
        self.list_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # List filters frame (only visible in list view)
        self.list_filters = ttk.Frame(self.left_panel)
        
        # List filter buttons
        self.sector_btn = ttk.Button(self.list_filters, text="Sectors", 
                                    command=lambda: self.switch_list_mode("sectors"))
        self.sector_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.subsector_btn = ttk.Button(self.list_filters, text="Subsectors", 
                                       command=lambda: self.switch_list_mode("subsectors"))
        self.subsector_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.system_btn = ttk.Button(self.list_filters, text="Systems", 
                                    command=lambda: self.switch_list_mode("systems"))
        self.system_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.planet_btn = ttk.Button(self.list_filters, text="Planets", 
                                    command=lambda: self.switch_list_mode("planets"))
        self.planet_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Content area (map or list view)
        self.content_area = ttk.Frame(self.left_panel)
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Stats bar at bottom
        self.stats_area = ttk.Frame(self.left_panel)
        self.stats_area.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        # Right panel - Details
        self.right_panel = ttk.Frame(self.main_container)
        
        # Add panels to PanedWindow
        self.main_container.add(self.left_panel, weight=1)
        self.main_container.add(self.right_panel, weight=1)
    
    def setup_components(self):
        """Initialize and set up all UI components"""
        # Map views (only slice map now)
        self.slice_map_view = SliceMapView(self.content_area, self)
        
        # List view
        self.list_view = ListView(self.content_area, self)
        
        # Detail views
        self.sector_detail = EnhancedSectorDetail(self.right_panel, self)
        self.subsector_detail = EnhancedSubsectorDetail(self.right_panel, self)
        self.system_detail = EnhancedSystemDetail(self.right_panel, self)
        self.planet_detail = EnhancedPlanetDetail(self.right_panel, self)
        
        # Stats bar
        self.stats_bar = StatsBar(self.stats_area, self)
        
        # Help dialog
        self.help_dialog = HelpDialog(self.root, self)
        
        # Set up menu
        self.create_menu()
    
    def create_menu(self):
        """Create the application menu"""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Reload Data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Galaxy Map", command=lambda: self.switch_view("slice_map"))
        view_menu.add_command(label="List View", command=lambda: self.switch_view("list"))
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Help", command=self.help_dialog.show)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def load_data(self):
        """Load data from the database"""
        try:
            self.data_loader.load()
            
            # Debug output for important sectors
            print(f"Total sectors loaded: {len(self.data_loader.sectors)}")
                  
            # Build the cache of Wyvern-owned locations
            self.build_wyvern_locations_cache()
            
            self.update_views()
            self.stats_bar.update()
        except Exception as e:
            self.show_error(f"Error loading data: {str(e)}")
    
    def build_wyvern_locations_cache(self):
        """Build a cache of all location codes owned by Wyvern Supremacy"""
        self.wyvern_locations = set()
        wyvern_planet_count = 0
        
        try:
            # First find all Wyvern-owned planets
            for planet in self.data_loader.planets:
                if not planet:
                    continue
                    
                owner = planet.get('owner', '')
                location = planet.get('location', '')
                
                if owner and "WYVERN SUPREMACY" in owner.upper() and location:
                    wyvern_planet_count += 1
                    # Add the planet's full location code
                    print(f"Found Wyvern planet: {location} - {owner}")
                    self.wyvern_locations.add(location)
                    
                    # Add all parent location codes
                    if len(location) >= 7:  # Location includes system
                        system_code = location[:7]
                        self.wyvern_locations.add(system_code)
                        
                        if len(location) >= 6:  # Location includes subsector
                            subsector_code = location[:6]
                            self.wyvern_locations.add(subsector_code)
                            
                            if len(location) >= 3:  # Location includes sector
                                sector_code = location[:3]
                                self.wyvern_locations.add(sector_code)
                    
                    # Handle slash format if present
                    if '/' in location:
                        parts = location.split('/')
                        if len(parts) >= 1:
                            self.wyvern_locations.add(parts[0])  # Sector
                            
                            if len(parts) >= 2:
                                subsector = f"{parts[0]}{parts[1]}"
                                self.wyvern_locations.add(subsector)
                                
                                if len(parts) >= 3:
                                    system = f"{parts[0]}{parts[1]}{parts[2]}"
                                    self.wyvern_locations.add(system)
            
            print(f"Wyvern planet count: {wyvern_planet_count}")
            print(f"Wyvern locations cache built with {len(self.wyvern_locations)} locations")
            if len(self.wyvern_locations) > 0:
                print(f"Wyvern locations: {sorted(list(self.wyvern_locations))}")
        except Exception as e:
            print(f"Error building Wyvern locations cache: {e}")
            self.wyvern_locations = set()
    
    def is_wyvern_location(self, location_code):
        """Check if a location is in the Wyvern Supremacy hierarchy"""
        if not location_code:
            return False
            
        try:
            # Check the cache
            return location_code in self.wyvern_locations
        except Exception as e:
            print(f"Error checking Wyvern location status for {location_code}: {e}")
            return False
    
    def switch_view(self, view):
        """Switch between map and list views"""
        self.current_view.set(view)
        
        # Update UI state
        if view == "slice_map":
            self.slice_map_btn.configure(style="Selected.TButton")
            self.list_btn.configure(style="ViewTab.TButton")
            self.list_filters.pack_forget()
            self.slice_map_view.show()
            self.list_view.hide()
        else:  # list view
            self.slice_map_btn.configure(style="ViewTab.TButton")
            self.list_btn.configure(style="Selected.TButton")
            self.list_filters.pack(fill=tk.X, padx=5, pady=5)
            self.slice_map_view.hide()
            self.list_view.show()
            self.switch_list_mode(self.current_list_mode.get())
    
    def switch_list_mode(self, mode):
        """Switch between different list modes (sectors, subsectors, etc.)"""
        self.current_list_mode.set(mode)
        
        # Update button styles
        for btn, mode_val in [
            (self.sector_btn, "sectors"),
            (self.subsector_btn, "subsectors"),
            (self.system_btn, "systems"),
            (self.planet_btn, "planets")
        ]:
            if mode == mode_val:
                btn.configure(style="Selected.TButton")
            else:
                btn.configure(style="TButton")
        
        # Update list view
        self.list_view.update_mode(mode)
    
    def select_sector_by_code(self, sector_code):
        """Handle sector selection by code instead of ID"""
        if not sector_code:
            return False
            
        # First, try to use the data_loader's get_sector_by_code method
        sector = self.data_loader.get_sector_by_code(sector_code)
        if sector:
            self.selected_sector = sector.get('id')
            self.selected_subsector = None
            self.selected_system = None
            self.selected_planet = None
            self.update_detail_view()
            self.slice_map_view.update_selection()
            print(f"Selected sector: {sector_code} (ID: {sector.get('id')})")
            return True
            
        # If that fails, try the legacy method
        for sector in self.data_loader.sectors:
            if sector.get('location') == sector_code:
                self.selected_sector = sector.get('id')
                self.selected_subsector = None
                self.selected_system = None
                self.selected_planet = None
                self.update_detail_view()
                self.slice_map_view.update_selection()
                print(f"Selected sector: {sector_code} (ID: {sector.get('id')}) (legacy method)")
                return True
        
        print(f"Error: Sector not found for code: {sector_code}")
        return False
    

    def select_entity(self, entity_type, entity_id):
        """Select an entity by type and ID"""
        if entity_type == 'sector':
            self.select_sector(entity_id)
        elif entity_type == 'subsector':
            self.select_subsector(entity_id)
        elif entity_type == 'system':
            self.select_system(entity_id)
        elif entity_type == 'planet':
            self.select_planet(entity_id)
    
    def select_sector(self, sector_id):
        """Handle sector selection"""
        if sector_id is None:
            return
            
        # Normal sector selection without special case handling
        self.selected_sector = sector_id
        self.selected_subsector = None
        self.selected_system = None
        self.selected_planet = None
        self.update_detail_view()
        self.slice_map_view.update_selection()
    
    def select_subsector(self, subsector_id):
        """Handle subsector selection"""
        if subsector_id is None:
            return
            
        print(f"Selecting subsector ID: {subsector_id}")
        self.selected_subsector = subsector_id
        self.selected_system = None
        self.selected_planet = None
        
        # Update selected sector to match parent of subsector
        subsector = self.data_loader.get_subsector(subsector_id)
        if subsector:
            print(f"Found subsector: {subsector.get('location')}")
            sector_id = subsector.get("sector_id")
            if sector_id:
                print(f"Setting parent sector ID from subsector: {sector_id}")
                self.selected_sector = sector_id
            else:
                # Try to find parent sector by location code
                location = subsector.get('location', '')
                if location and len(location) >= 3:
                    sector_code = location[:3]
                    print(f"Looking for parent sector by code: {sector_code}")
                    parent_sector = self.data_loader.get_sector_by_code(sector_code)
                    if parent_sector:
                        print(f"Found parent sector: {parent_sector.get('location')}")
                        self.selected_sector = parent_sector.get('id')
                    else:
                        print(f"Parent sector not found for code: {sector_code}")
        else:
            print(f"Error: Subsector not found for ID: {subsector_id}")
        
        self.update_detail_view()
    
    def select_system(self, system_id):
        """Handle system selection"""
        if system_id is None:
            return
            
        self.selected_system = system_id
        self.selected_planet = None
        
        # Update selected subsector to match parent of system
        system = self.data_loader.get_system(system_id)
        if system:
            subsector_id = system.get("subsector_id")
            if subsector_id:
                self.selected_subsector = subsector_id
                
                # Update selected sector as well
                subsector = self.data_loader.get_subsector(subsector_id)
                if subsector:
                    sector_id = subsector.get("sector_id")
                    if sector_id:
                        self.selected_sector = sector_id
            else:
                # Try to find parent by location code
                location = system.get('location', '')
                if location and len(location) >= 6:
                    subsector_code = location[:6]
                    for subsector in self.data_loader.subsectors:
                        if subsector.get('location') == subsector_code:
                            self.selected_subsector = subsector.get('id')
                            
                            # Also update sector
                            if len(location) >= 3:
                                sector_code = location[:3]
                                parent_sector = self.data_loader.get_sector_by_code(sector_code)
                                if parent_sector:
                                    self.selected_sector = parent_sector.get('id')
                            break
        
        self.update_detail_view()
    
    def select_planet(self, planet_id):
        """Handle planet selection"""
        if planet_id is None:
            return
            
        self.selected_planet = planet_id
        
        # Update selected system to match parent of planet
        planet = self.data_loader.get_planet(planet_id)
        if planet:
            system_id = planet.get("system_id")
            if system_id:
                self.selected_system = system_id
                
                # Update selected subsector and sector as well
                system = self.data_loader.get_system(system_id)
                if system:
                    subsector_id = system.get("subsector_id")
                    if subsector_id:
                        self.selected_subsector = subsector_id
                        subsector = self.data_loader.get_subsector(subsector_id)
                        if subsector:
                            sector_id = subsector.get("sector_id")
                            if sector_id:
                                self.selected_sector = sector_id
            else:
                # Try to find parent by location code
                location = planet.get('location', '')
                if location and len(location) >= 7:
                    system_code = location[:7]
                    for system in self.data_loader.systems:
                        if system.get('location') == system_code:
                            self.selected_system = system.get('id')
                            
                            # Also try to update subsector and sector
                            location = system.get('location', '')
                            if location and len(location) >= 6:
                                subsector_code = location[:6]
                                for subsector in self.data_loader.subsectors:
                                    if subsector.get('location') == subsector_code:
                                        self.selected_subsector = subsector.get('id')
                                        
                                        # Also update sector
                                        if len(location) >= 3:
                                            sector_code = location[:3]
                                            parent_sector = self.data_loader.get_sector_by_code(sector_code)
                                            if parent_sector:
                                                self.selected_sector = parent_sector.get('id')
                                        break
                            break

        self.update_detail_view()
    
    def update_detail_view(self):
        """Update the detail view based on current selections"""
        try:
            # Hide all detail views
            self.sector_detail.hide()
            self.subsector_detail.hide()
            self.system_detail.hide()
            self.planet_detail.hide()
            
            # Show the appropriate detail view
            if self.selected_planet is not None:
                print(f"Showing planet detail: {self.selected_planet}")
                self.planet_detail.show(self.selected_planet)
            elif self.selected_system is not None:
                print(f"Showing system detail: {self.selected_system}")
                self.system_detail.show(self.selected_system)
            elif self.selected_subsector is not None:
                print(f"Showing subsector detail: {self.selected_subsector}")
                self.subsector_detail.show(self.selected_subsector)
            elif self.selected_sector is not None:
                print(f"Showing sector detail: {self.selected_sector}")
                self.sector_detail.show(self.selected_sector)
            else:
                print("No entity selected to show in detail view")
        except Exception as e:
            print(f"Error updating detail view: {e}")
            import traceback
            traceback.print_exc()
    
    def update_views(self):
        """Update all views with current data"""
        try:
            self.slice_map_view.update()
            self.list_view.update()
            self.update_detail_view()
        except Exception as e:
            print(f"Error updating views: {e}")
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_sector = None
        self.selected_subsector = None
        self.selected_system = None
        self.selected_planet = None
        self.update_detail_view()
        self.slice_map_view.update_selection()
    
    def get_button_style_for_entity(self, entity_type, entity_data, is_selected):
        """Determine the button style based on entity type, data and selection state"""
        if is_selected:
            return "Selected.TButton"
        
        # Check if it's a Wyvern-owned location
        location = entity_data.get('location', '')
        if self.is_wyvern_location(location):
            return "Wyvern.TButton"
        
        # Default style
        return "TButton"
    
    def show_error(self, message):
        """Show an error dialog"""
        from tkinter import messagebox
        messagebox.showerror("Error", message)
    
    def show_about(self):
        """Show the about dialog"""
        from tkinter import messagebox
        messagebox.showinfo("About Takamo Galaxy Explorer", 
                          "Takamo Galaxy Explorer\n\n"
                          "A visualization tool for Takamo game data\n"
                          "For personal use only\n\n"
                          "Version 1.0")