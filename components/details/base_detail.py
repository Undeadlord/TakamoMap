# components/details/base_detail.py
"""
Base Detail Panel
Base class for all detail panels with common functionality
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class BaseDetailPanel:
    """Base class for detail panels with common functionality"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ttk.Frame(parent)
        
        # Header section
        self.header = ttk.Frame(self.frame)
        self.header.pack(fill=tk.X, padx=10, pady=5)
        
        self.title_var = tk.StringVar()
        self.title_label = ttk.Label(self.header, textvariable=self.title_var, font=("Arial", 14, "bold"))
        self.title_label.pack(side=tk.LEFT)
        
        self.close_btn = ttk.Button(self.header, text="×", width=3, command=self.on_close)
        self.close_btn.pack(side=tk.RIGHT)
        
        # Create a canvas with scrollbar for the detail content
        self.content_frame = ttk.Frame(self.frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
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
        
        # Add mouse wheel scrolling to the canvas
        # For Windows/MacOS
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        # For Linux (X11)
        self.canvas.bind("<Button-4>", self.on_mousewheel_linux_up)
        self.canvas.bind("<Button-5>", self.on_mousewheel_linux_down)
        
        # Add key bindings for scrolling with arrow keys
        self.canvas.bind("<Up>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Down>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        # Make canvas focusable to receive key events
        self.canvas.config(takefocus=1)
        
        # Footer section
        self.footer = ttk.Frame(self.frame)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        self.date_var = tk.StringVar()
        self.date_label = ttk.Label(self.footer, textvariable=self.date_var, font=("Arial", 8))
        self.date_label.pack(side=tk.LEFT)
    
    def on_mousewheel(self, event):
        """Handle mouse wheel for Windows/MacOS"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_mousewheel_linux_up(self, event):
        """Handle mouse wheel up for Linux"""
        self.canvas.yview_scroll(-1, "units")
    
    def on_mousewheel_linux_down(self, event):
        """Handle mouse wheel down for Linux"""
        self.canvas.yview_scroll(1, "units")
    
    def show(self, entity_id):
        """Show the detail panel for the specified entity"""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Hide any other detail panels
        self.hide_all_panels()
        
        # Load and display entity data
        self.load_entity(entity_id)
        
        # Show this panel
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hide this detail panel"""
        self.frame.pack_forget()
    
    def hide_all_panels(self):
        """Hide all detail panels"""
        for widget in self.parent.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.pack_forget()
    
    def on_close(self):
        """Handle close button click"""
        self.hide()
        self.app.clear_selection()
    
    def load_entity(self, entity_id):
        """Load and display entity data - to be implemented by subclasses"""
        pass
    
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
    
    def add_field(self, label, value, is_header=False):
        """Add a labeled field to the detail panel"""
        if not value:
            return  # Skip empty values
        
        field_frame = ttk.Frame(self.scrollable_frame)
        field_frame.pack(fill=tk.X, padx=5, pady=2)
        
        label_widget = ttk.Label(field_frame, text=f"{label}:", font=("Arial", 10, "bold" if is_header else "normal"))
        label_widget.pack(side=tk.LEFT, padx=5)
        
        value_widget = ttk.Label(field_frame, text=str(value))
        value_widget.pack(side=tk.LEFT, padx=5)
    
    def add_separator(self):
        """Add a separator line"""
        separator = ttk.Separator(self.scrollable_frame, orient="horizontal")
        separator.pack(fill=tk.X, padx=5, pady=10)
    
    def add_section_header(self, text):
        """Add a section header to the panel"""
        header = ttk.Label(self.scrollable_frame, text=text, font=("Arial", 12, "bold"))
        header.pack(fill=tk.X, padx=5, pady=5)
    
    def create_info_item(self, parent, row, col, label_text, value_text, tooltip="", span=1, is_highlight=False):
        """Create a labeled field with tooltip in a grid layout"""
        # Create a frame for the field
        field_frame = ttk.Frame(parent)
        field_frame.grid(row=row, column=col, padx=5, pady=2, sticky="w", columnspan=span)
        
        # Create the label
        label_widget = ttk.Label(field_frame, text=f"{label_text}", font=("Arial", 10, "bold"))
        label_widget.pack(side=tk.LEFT, padx=2)
        
        # Create the value
        style = "Bold.TLabel" if is_highlight else "TLabel"
        value_widget = ttk.Label(field_frame, text=str(value_text), style=style)
        value_widget.pack(side=tk.LEFT, padx=2)
        
        # Add tooltip if provided
        if tooltip:
            self.add_tooltip(field_frame, tooltip)
        
        return field_frame
    
    def add_tooltip(self, widget, text):
        """Add a tooltip to a widget (shows on hover)"""
        # This is a simplified tooltip implementation
        # For a production app, you might want a more sophisticated tooltip
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Create a toplevel window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(self.tooltip, text=text, justify='left',
                            background="#2a2a3a", foreground="white", 
                            relief='solid', borderwidth=1,
                            wraplength=300)
            label.pack(ipadx=2, ipady=2)
            
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def add_button(self, text, command, location_code=None):
        """Add a button with optional Wyvern styling for location_code"""
        # Determine style based on location_code
        style = "TButton"
        if location_code and hasattr(self.app, 'is_wyvern_location') and self.app.is_wyvern_location(location_code):
            style = "Wyvern.TButton"
            
        button = ttk.Button(self.scrollable_frame, text=text, command=command, style=style)
        button.pack(fill=tk.X, padx=5, pady=2)