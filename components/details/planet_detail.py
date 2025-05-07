"""
Enhanced Planet Detail Component
Displays detailed information about selected planets
"""
import tkinter as tk
from tkinter import ttk
from components.details.base_detail import BaseDetailPanel

class EnhancedPlanetDetail(BaseDetailPanel):
    """Detail panel for planets with enhanced context and explanations"""
    
    def load_entity(self, planet_id):
        """Load and display planet data with enhanced context"""
        planet_details = self.app.data_loader.get_planet_details(planet_id)
        if not planet_details:
            self.title_var.set("Planet Not Found")
            return
        
        # Set title and date
        title = planet_details.get('location', 'Unknown Planet')
        if planet_details.get('size'):
            title += f" (Size: {planet_details['size']})"
        self.title_var.set(title)
        self.date_var.set(f"Last updated: {self.format_date(planet_details.get('date', 'Unknown'))}")
        
        # Debug output
        print(f"Loading planet detail: {title} (ID: {planet_id})")
        
        # Create a summary section at the top
        self.add_section_header("Planet Overview")
        
        # Create grid layout for overview section
        overview_frame = ttk.Frame(self.scrollable_frame)
        overview_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Location code
        location = planet_details.get('location', 'Unknown')
        location_label = self.create_info_item(overview_frame, 0, 0, "Location:", location, 
                                              tooltip="Unique coordinates that identify this planet's position in the galaxy")
        
        # Planet status
        status_text = planet_details.get('status', 'Unknown')
        status_info = "A planet's status determines what can be built on it and how it can be used"
        status_label = self.create_info_item(overview_frame, 0, 1, "Status:", status_text, tooltip=status_info)
        
        # Planet size
        size_text = planet_details.get('size', 'Unknown')
        size_info = "Planet size determines maximum population and military capacity (1-9 scale)"
        if size_text:
            try:
                size_val = int(size_text)
                size_text = f"{size_text} (Max Pop: {size_val * 13}, Max Forts: {size_val * 5})"
            except:
                pass
        size_label = self.create_info_item(overview_frame, 1, 0, "Size:", size_text, tooltip=size_info)
        
        # Atmosphere and hydrosphere details - with interpretation
        atmos_val = planet_details.get('atmos')
        atmos_info = "Atmospheric value affects habitat range and population transfers (1-9 scale)"
        atmos_text = f"{atmos_val if atmos_val else 'Unknown'}"
        atmos_label = self.create_info_item(overview_frame, 1, 1, "Atmosphere:", atmos_text, tooltip=atmos_info)
        
        hyp_val = planet_details.get('hyp')
        hyp_info = "Hydrographic value affects habitat range and population transfers (1-9 scale)"
        hyp_text = f"{hyp_val if hyp_val else 'Unknown'}"
        hyp_label = self.create_info_item(overview_frame, 2, 0, "Hydrographics:", hyp_text, tooltip=hyp_info)
        
        # Owner
        is_wyvern = False
        owner_text = planet_details.get('owner', 'Unknown')
        if owner_text and "WYVERN SUPREMACY" in owner_text.upper():
            is_wyvern = True
        owner_label = self.create_info_item(overview_frame, 2, 1, "Owner:", owner_text, 
                                           tooltip="The player who controls this planet", is_highlight=is_wyvern)
        
        # Tech Level
        tec_level = "Unknown"
        if planet_details.get('ptl'):
            tec_level = planet_details['ptl']
        elif planet_details.get('tl'):
            tec_level = planet_details['tl']
        
        tec_info = "Determines the strength of military units and what can be built here"
        tec_label = self.create_info_item(overview_frame, 3, 0, "Tech Level:", tec_level, tooltip=tec_info)
        
        # Mining potential and actual
        mpot = planet_details.get('mpot', 'Unknown')
        mpot_info = "Maximum number of Mining Centers (MCs) that can be built"
        mpot_label = self.create_info_item(overview_frame, 3, 1, "Mining Potential:", mpot, tooltip=mpot_info)
        
        # Add separator
        self.add_separator()
        
        # Economic Information Section
        self.add_section_header("Economy & Infrastructure")
        econ_frame = ttk.Frame(self.scrollable_frame)
        econ_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Mining Centers
        mc_count = planet_details.get('mprod', 0)
        if not mc_count and planet_details.get('mcenter'):
            mc_count = planet_details.get('mcenter', 0)  # Alternative field name
        mc_info = "Each MC provides 20 RUs per turn and allows building 5 PCs"
        mc_label = self.create_info_item(econ_frame, 0, 0, "Mining Centers:", mc_count, tooltip=mc_info)
        
        # Production Centers
        pc_count = planet_details.get('pcenter', 0)
        pc_info = "Each PC provides 20 RUs per turn"
        pc_label = self.create_info_item(econ_frame, 0, 1, "Production Centers:", pc_count, tooltip=pc_info)
        
        # Shipyards
        sy_count = planet_details.get('sy', 0)
        sy_max = ((int(planet_details.get('size', 0)) + 1) // 2) if planet_details.get('size') else "?"
        sy_info = f"Used to build and repair ships (Max: {sy_max})"
        sy_label = self.create_info_item(econ_frame, 1, 0, "Shipyards:", sy_count, tooltip=sy_info)
        
        # Population
        pop_count = planet_details.get('pop', 0)
        pop_max = int(planet_details.get('size', 0)) * 13 if planet_details.get('size') else "?"
        pop_info = f"Used for recruiting MUs and taxation (Max: {pop_max})"
        pop_label = self.create_info_item(econ_frame, 1, 1, "Population:", pop_count, tooltip=pop_info)
        
        # Special Centers
        has_tc = False  # Trade Center
        has_ac = False  # Agricultural Center
        has_sc = False  # Smuggling Center
        
        # Add special centers status (check if this data is available)
        special_centers = []
        if planet_details.get('tc'):
            special_centers.append("Trade Center (TC)")
            has_tc = True
        if planet_details.get('ac'):
            special_centers.append("Agricultural Center (AC)")
            has_ac = True
        if planet_details.get('sc'):
            special_centers.append("Smuggling Center (SC)")
            has_sc = True
        
        special_centers_text = ", ".join(special_centers) if special_centers else "None"
        special_info = "Special centers provide additional benefits based on player type"
        special_label = self.create_info_item(econ_frame, 2, 0, "Special Centers:", special_centers_text, 
                                             tooltip=special_info, span=2)
        
        # Add separator
        self.add_separator()
        
        # Military Information Section
        self.add_section_header("Military Forces & Defenses")
        mil_frame = ttk.Frame(self.scrollable_frame)
        mil_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # MUs
        mu_count = planet_details.get('mu', 0)
        mu_max = int(planet_details.get('size', 0)) * 100 if planet_details.get('size') else "?"
        mu_info = f"Basic ground forces for defense and invasion (Max: {mu_max})"
        mu_label = self.create_info_item(mil_frame, 0, 0, "Marine Units:", mu_count, tooltip=mu_info)
        
        # HMUs
        hmu_count = planet_details.get('hmu', 0)
        hmu_max = int(planet_details.get('size', 0)) * 100 if planet_details.get('size') else "?"
        hmu_info = f"Heavy ground forces with 2x combat power (Max: {hmu_max})"
        hmu_label = self.create_info_item(mil_frame, 0, 1, "Heavy Marines:", hmu_count, tooltip=hmu_info)
        
        # Forts
        fort_count = planet_details.get('fort', 0)
        fort_max = int(planet_details.get('size', 0)) * 5 if planet_details.get('size') else "?"
        fort_info = f"Orbital defense installations (Max: {fort_max})"
        fort_label = self.create_info_item(mil_frame, 1, 0, "Forts:", fort_count, tooltip=fort_info)
        
        # Fighters
        ftr_count = planet_details.get('fighter', 0)
        ftr_max = int(planet_details.get('size', 0)) * 25 if planet_details.get('size') else "?"
        ftr_info = f"Planetary defense fighters (Max: {ftr_max})"
        ftr_label = self.create_info_item(mil_frame, 1, 1, "Fighters:", ftr_count, tooltip=ftr_info)
        
        # Torpedoes
        torp_count = planet_details.get('torp', 0)
        torp_class = planet_details.get('torpclass', 'None')
        torp_max = fort_count * 20 if fort_count else 0
        torp_info = f"Long-range missiles housed in Forts (Max: {torp_max})"
        torp_text = f"{torp_count} (Class {torp_class})" if torp_count else "None"
        torp_label = self.create_info_item(mil_frame, 2, 0, "Torpedoes:", torp_text, tooltip=torp_info)

        # ABMs (Anti-Ballistic Missiles)
        abm_count = planet_details.get('abm', 0)
        abm_max = int(planet_details.get('size', 0)) * 25 if planet_details.get('size') else "?"
        abm_info = f"Defense against enemy missiles (Max: {abm_max})"
        abm_label = self.create_info_item(mil_frame, 2, 1, "ABMs:", abm_count, tooltip=abm_info)
        
        # Guerrillas (if any)
        gu_count = planet_details.get('gu', 0)
        if gu_count:
            gu_info = "Rebel forces that can attack planetary installations"
            gu_label = self.create_info_item(mil_frame, 3, 0, "Guerrillas:", gu_count, tooltip=gu_info, span=2)
        
        # Add aggression level
        agg_level = planet_details.get('agg', 'Unknown')
        agg_info = "Determines how likely the planet is to engage in combat (10-100 scale)"
        agg_label = self.create_info_item(mil_frame, 4, 0, "Aggression Level:", agg_level, tooltip=agg_info, span=2)
        
        # Add Notes Section if present
        if planet_details.get('notes'):
            self.add_separator()
            self.add_section_header("Planet Notes")
            notes_frame = ttk.Frame(self.scrollable_frame)
            notes_frame.pack(fill=tk.X, padx=5, pady=5)
            
            notes_text = planet_details.get('notes', '')
            notes_label = ttk.Label(notes_frame, text=notes_text, wraplength=550, justify="left")
            notes_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Parent system and navigation section
        self.add_separator()
        self.add_section_header("Navigation")
        
        # Parent system
        system = planet_details.get('system')
        if system:
            nav_frame = ttk.Frame(self.scrollable_frame)
            nav_frame.pack(fill=tk.X, padx=5, pady=5)
            
            system_text = f"{system.get('location', 'Unknown')} - {system.get('nav', 'Unknown')}"
            nav_button = ttk.Button(
                nav_frame, 
                text=f"Parent System: {system_text}",
                command=lambda s=system.get('id'): self.app.select_system(s)
            )
            nav_button.pack(fill=tk.X, padx=5, pady=2)
            
            # Extract parent subsector and sector codes
            system_loc = system.get('location', '')
            if system_loc and len(system_loc) >= 6:
                subsector_code = system_loc[:6]
                sector_code = system_loc[:3]
                
                # Add parent subsector button
                subsector_button = ttk.Button(
                    nav_frame,
                    text=f"Parent Subsector: {subsector_code}",
                    command=lambda: self.app.select_entity('subsector', 
                                                         self.app.data_loader.get_subsector_id_by_code(subsector_code))
                )
                subsector_button.pack(fill=tk.X, padx=5, pady=2)
                
                # Add parent sector button
                sector_button = ttk.Button(
                    nav_frame,
                    text=f"Parent Sector: {sector_code}",
                    command=lambda: self.app.select_entity('sector', 
                                                        self.app.data_loader.get_sector_id_by_code(sector_code))
                )
                sector_button.pack(fill=tk.X, padx=5, pady=2)
        else:
            # If no direct system reference, try to infer from location code
            location = planet_details.get('location', '')
            if location and len(location) >= 7:
                system_code = location[:7]
                nav_frame = ttk.Frame(self.scrollable_frame)
                nav_frame.pack(fill=tk.X, padx=5, pady=5)
                
                system_button = ttk.Button(
                    nav_frame,
                    text=f"Parent System: {system_code}",
                    command=lambda: self.app.select_entity('system', 
                                                        self.app.data_loader.get_system_id_by_code(system_code))
                )
                system_button.pack(fill=tk.X, padx=5, pady=2)
                
                # Also add subsector and sector links
                if len(location) >= 6:
                    subsector_code = location[:6]
                    subsector_button = ttk.Button(
                        nav_frame,
                        text=f"Parent Subsector: {subsector_code}",
                        command=lambda: self.app.select_entity('subsector', 
                                                             self.app.data_loader.get_subsector_id_by_code(subsector_code))
                    )
                    subsector_button.pack(fill=tk.X, padx=5, pady=2)
                
                if len(location) >= 3:
                    sector_code = location[:3]
                    sector_button = ttk.Button(
                        nav_frame,
                        text=f"Parent Sector: {sector_code}",
                        command=lambda: self.app.select_entity('sector', 
                                                            self.app.data_loader.get_sector_id_by_code(sector_code))
                    )
                    sector_button.pack(fill=tk.X, padx=5, pady=2)