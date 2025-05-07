"""
Common UI Components
Shared UI elements used across the application
"""
import tkinter as tk
from tkinter import ttk
import webbrowser

class StatsBar:
    """Stats bar showing counts of entities"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        # Create labels for each stat
        self.sectors_var = tk.StringVar(value="Sectors: 0")
        self.subsectors_var = tk.StringVar(value="Subsectors: 0")
        self.systems_var = tk.StringVar(value="Systems: 0")
        self.planets_var = tk.StringVar(value="Planets: 0")
        
        # Layout in a grid
        self.sectors_label = ttk.Label(parent, textvariable=self.sectors_var, font=("Arial", 8))
        self.sectors_label.grid(row=0, column=0, padx=5, sticky="w")
        
        self.subsectors_label = ttk.Label(parent, textvariable=self.subsectors_var, font=("Arial", 8))
        self.subsectors_label.grid(row=0, column=1, padx=5, sticky="w")
        
        self.systems_label = ttk.Label(parent, textvariable=self.systems_var, font=("Arial", 8))
        self.systems_label.grid(row=1, column=0, padx=5, sticky="w")
        
        self.planets_label = ttk.Label(parent, textvariable=self.planets_var, font=("Arial", 8))
        self.planets_label.grid(row=1, column=1, padx=5, sticky="w")
    
    def update(self):
        """Update the stats display"""
        # Get stats from data loader
        stats = self.app.data_loader.get_stats()
        
        # Update display
        self.sectors_var.set(f"Sectors: {stats['sectors']}")
        self.subsectors_var.set(f"Subsectors: {stats['subsectors']}")
        self.systems_var.set(f"Systems: {stats['systems']}")
        self.planets_var.set(f"Planets: {stats['planets']}")


class HelpDialog:
    """Help dialog with application documentation"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        # Create the dialog window (hidden initially)
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Takamo Galaxy Explorer Help")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Apply same styling as main window
        self.dialog.configure(background="#1e1e2e")
        
        # Content frame with scrollbar
        self.content_frame = ttk.Frame(self.dialog)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.scrollbar = ttk.Scrollbar(self.content_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(self.content_frame, bg="#1e1e2e", highlightthickness=0)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add help content
        self.create_help_content()
        
        # Close button at bottom
        self.close_btn = ttk.Button(self.dialog, text="Close", command=self.hide)
        self.close_btn.pack(pady=10)
        
        # Hide initially
        self.hide()
    
    def create_help_content(self):
        """Create the help dialog content"""
        # Title
        title = ttk.Label(self.scrollable_frame, text="Takamo Galaxy Explorer", font=("Arial", 16, "bold"))
        title.pack(fill=tk.X, pady=10)
        
        # About section
        self.add_section("About", [
            "This tool allows you to explore and visualize your Takamo game data.",
            "It provides both a 3D galaxy map view and list views of sectors, subsectors, systems, and planets."
        ])
        
        # Views section
        self.add_section("Views", [
            "3D View - Shows a 2D projection of the 3D galaxy map with explored sectors.",
            "List View - Shows detailed lists of explored entities that you can filter and explore."
        ])
        
        # Navigation section
        self.add_section("Navigation", [
            "Click on any sector, subsector, system, or planet to view its details.",
            "Use the view mode buttons to switch between different entity types in the list view.",
            "Use the tabs to switch between the 3D view and list view."
        ])
        
        # Coordinate System section
        self.add_section("Coordinate System", [
            "The Takamo galaxy uses a 3D coordinate system with X, Y, and Z axes.",
            "Sectors are identified by three letters (like 'MMM'), with each letter representing a position along one axis (A-Z).",
            "Subsectors are identified by three additional digits (like 'MMM222'), representing position within the sector.",
            "Systems are identified by an additional digit (like 'MMM2221'), representing position within the subsector.",
            "Planets are identified by an additional digit (like 'MMM22214'), representing their orbit within the system."
        ])
        
        # Copyright
        copyright_label = ttk.Label(
            self.scrollable_frame, 
            text="Based on Takamo game data. This visualization tool is for personal use only.",
            font=("Arial", 8)
        )
        copyright_label.pack(fill=tk.X, pady=20)
    
    def add_section(self, title, paragraphs):
        """Add a section to the help content"""
        # Section title
        section_title = ttk.Label(self.scrollable_frame, text=title, font=("Arial", 12, "bold"))
        section_title.pack(fill=tk.X, pady=(10, 5), padx=5, anchor="w")
        
        # Section content
        for paragraph in paragraphs:
            para_label = ttk.Label(
                self.scrollable_frame, 
                text=paragraph, 
                wraplength=550, 
                justify="left"
            )
            para_label.pack(fill=tk.X, pady=2, padx=10, anchor="w")
    
    def show(self):
        """Show the help dialog"""
        self.dialog.deiconify()
        self.dialog.lift()
    
    def hide(self):
        """Hide the help dialog"""
        self.dialog.withdraw()
