"""
List View Component
Provides list views of different entities with Wyvern Supremacy highlighting
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class ListView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ttk.Frame(parent)
        
        # Create a frame for the list header
        self.header_frame = ttk.Frame(self.frame)
        self.header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.title_var = tk.StringVar(value="Explored Sectors (0)")
        self.title_label = ttk.Label(self.header_frame, textvariable=self.title_var, font=("Arial", 12, "bold"))
        self.title_label.pack(side=tk.LEFT)
        
        # Create the list display with scrollbar
        self.list_frame = ttk.Frame(self.frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # List box (custom styling)
        self.listbox_frame = ttk.Frame(self.list_frame)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        # Hide initially
        self.hide()
        
        # Current mode
        self.current_mode = "sectors"
    
    def show(self):
        """Show the list view"""
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hide the list view"""
        self.frame.pack_forget()
    
    def update(self):
        """Update list view with current data"""
        self.update_mode(self.current_mode)
    
    def update_mode(self, mode):
        """Update list view for the specified mode"""
        self.current_mode = mode
        
        # Clear existing items
        for widget in self.listbox_frame.winfo_children():
            widget.destroy()
        
        if mode == "sectors":
            self.show_sectors()
        elif mode == "subsectors":
            self.show_subsectors()
        elif mode == "systems":
            self.show_systems()
        elif mode == "planets":
            self.show_planets()
    
    def show_sectors(self):
        """Display the sectors list"""
        sectors = self.app.data_loader.sectors
        self.title_var.set(f"Explored Sectors ({len(sectors)})")
        
        # Create a canvas with scrollbar for the list items
        canvas = tk.Canvas(self.listbox_frame, bg="#1e1e2e", highlightthickness=0)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=canvas.yview)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add mouse wheel scrolling to the canvas
        # For Windows/MacOS
        canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        # For Linux (X11)
        canvas.bind("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
        
        # Add key bindings for scrolling with arrow keys
        canvas.bind("<Up>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Down>", lambda e: canvas.yview_scroll(1, "units"))
        
        # Make canvas focusable to receive key events
        canvas.config(takefocus=1)
        
        # Add items
        for i, sector in enumerate(sectors):
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill=tk.X, padx=2, pady=2)
            
            # Create a styled button for each item
            is_selected = sector.get('id') == self.app.selected_sector
            is_wyvern = self.app.is_wyvern_location(sector.get('location', ''))
            
            # Choose button style based on selection and Wyvern status
            if is_selected:
                style = "Selected.TButton"  # Orange with black text
            elif is_wyvern:
                style = "Wyvern.TButton"    # Green with white text
            else:
                style = "TButton"           # Default blue with white text
            
            btn = ttk.Button(
                item_frame, 
                style=style,
                text=f"{sector.get('location', 'Unknown')} - {sector.get('nav', 'Unknown')}\n"
                    f"Updated: {self.format_date(sector.get('date', 'Unknown'))}",
                command=lambda s=sector.get('id'): self.app.select_sector(s)
            )
            btn.pack(fill=tk.X, padx=0, pady=0)
        
        # Store the canvas reference so we can access it later
        self.active_canvas = canvas
    
    def show_subsectors(self):
        """Display the subsectors list"""
        subsectors = self.app.data_loader.subsectors
        self.title_var.set(f"Explored Subsectors ({len(subsectors)})")
        
        # Create a canvas with scrollbar for the list items
        canvas = tk.Canvas(self.listbox_frame, bg="#1e1e2e", highlightthickness=0)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=canvas.yview)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add items
        for i, subsector in enumerate(subsectors):
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill=tk.X, padx=2, pady=2)
            
            # Create a styled button for each item
            is_selected = subsector.get('id') == self.app.selected_subsector
            is_wyvern = self.app.is_wyvern_location(subsector.get('location', ''))
            
            # Choose button style based on selection and Wyvern status
            if is_selected:
                style = "Selected.TButton"
            elif is_wyvern:
                style = "Wyvern.TButton"
            else:
                style = "TButton"
            
            note_text = f"\n{subsector.get('note', '')}" if subsector.get('note') else ""
            
            btn = ttk.Button(
                item_frame, 
                style=style,
                text=f"{subsector.get('location', 'Unknown')} - {subsector.get('nav', 'Unknown')}"
                     f"{note_text}\n"
                     f"Updated: {self.format_date(subsector.get('date', 'Unknown'))}",
                command=lambda s=subsector.get('id'): self.app.select_subsector(s)
            )
            btn.pack(fill=tk.X, padx=0, pady=0)
    
    def show_systems(self):
        """Display the systems list"""
        systems = self.app.data_loader.systems
        self.title_var.set(f"Explored Systems ({len(systems)})")
        
        # Create a canvas with scrollbar for the list items
        canvas = tk.Canvas(self.listbox_frame, bg="#1e1e2e", highlightthickness=0)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=canvas.yview)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add items
        for i, system in enumerate(systems):
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill=tk.X, padx=2, pady=2)
            
            # Create a styled button for each item
            is_selected = system.get('id') == self.app.selected_system
            is_wyvern = self.app.is_wyvern_location(system.get('location', ''))
            
            # Choose button style based on selection and Wyvern status
            if is_selected:
                style = "Selected.TButton"
            elif is_wyvern:
                style = "Wyvern.TButton"
            else:
                style = "TButton"
            
            planets_text = f" - {system.get('planets', 0)} planets" if system.get('planets') is not None else ""
            nav_text = f"\n{system.get('nav', '')}" if system.get('nav') else ""
            
            btn = ttk.Button(
                item_frame, 
                style=style,
                text=f"{system.get('location', 'Unknown')}{planets_text}"
                     f"{nav_text}\n"
                     f"Updated: {self.format_date(system.get('date', 'Unknown'))}",
                command=lambda s=system.get('id'): self.app.select_system(s)
            )
            btn.pack(fill=tk.X, padx=0, pady=0)
    
    def show_planets(self):
        """Display the planets list"""
        planets = self.app.data_loader.planets
        self.title_var.set(f"Explored Planets ({len(planets)})")
        
        # Create a canvas with scrollbar for the list items
        canvas = tk.Canvas(self.listbox_frame, bg="#1e1e2e", highlightthickness=0)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=canvas.yview)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add items
        for i, planet in enumerate(planets):
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill=tk.X, padx=2, pady=2)
            
            # Determine if this is a Wyvern-owned planet directly
            is_wyvern_owned = planet.get('owner') and "Wyvern Supremacy" in planet.get('owner', '')
            
            # Create a styled button for each item
            is_selected = planet.get('id') == self.app.selected_planet
            
            # Choose button style based on selection and Wyvern status
            if is_selected:
                style = "Selected.TButton"
            elif is_wyvern_owned or self.app.is_wyvern_location(planet.get('location', '')):
                style = "Wyvern.TButton"
            else:
                style = "TButton"
            
            status_text = f" - {planet.get('status', 'Unknown')}"
            size_text = f" (Size: {planet.get('size', 'Unknown')})" if planet.get('size') else ""
            owner_text = f" • Owner: {planet.get('owner', '').strip()}" if planet.get('owner') else ""
            
            btn = ttk.Button(
                item_frame, 
                style=style,
                text=f"{planet.get('location', 'Unknown')}{status_text}\n"
                     f"{size_text}{owner_text}\n"
                     f"Updated: {self.format_date(planet.get('date', 'Unknown'))}",
                command=lambda p=planet.get('id'): self.app.select_planet(p)
            )
            btn.pack(fill=tk.X, padx=0, pady=0)
    
    def format_date(self, date_str):
        """Format a date string"""
        if not date_str or date_str == 'Unknown':
            return 'Unknown'
            
        try:
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            return date.strftime("%Y-%m-%d")
        except:
            try:
                # Try alternate format
                date = datetime.strptime(date_str, "%Y-%m-%d")
                return date.strftime("%Y-%m-%d")
            except:
                return date_str