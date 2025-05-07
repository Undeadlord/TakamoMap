"""
Data Loader Module
Handles loading and parsing the Takamo database directly
"""
import sqlite3
import os
import datetime

class DataLoader:
    def __init__(self, db_path):
        self.db_path = db_path
        self.sectors = []
        self.subsectors = []
        self.systems = []
        self.planets = []
        self.conn = None
        self.sector_codes = set()  # To track which sector codes we have
        
        # Add mapping dictionaries for code -> id lookups
        self.sector_by_code = {}
        self.subsector_by_code = {}
        self.system_by_code = {}
    
    def load(self):
        """Load data directly from the database file"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            
            # Check if tables exist before loading
            cursor = self.conn.cursor()
            tables = self._get_table_list()
            
            # Load data from tables that exist
            if 'sectors' in tables:
                self._load_sectors()
            else:
                print("Warning: 'sectors' table not found in database")
                
            if 'subsectors' in tables:
                self._load_subsectors()
            else:
                print("Warning: 'subsectors' table not found in database")
                
            if 'systems' in tables:
                self._load_systems()
            else:
                print("Warning: 'systems' table not found in database")
                
            if 'planets' in tables:
                self._load_planets()
            else:
                print("Warning: 'planets' table not found in database")
                
            # Create stub sectors for any missing sectors referenced in our data
            self._create_stub_sectors()
            
            # Debug output
            print(f"Total sectors after stubs: {len(self.sectors)}")
            
            # Specifically check for ANM
            anm_exists = any(sector.get('location') == 'ANM' for sector in self.sectors)
            print(f"ANM sector exists: {anm_exists}")
            
            if not anm_exists:
                # Force create ANM sector for testing
                print("Force creating ANM sector")
                self._create_specific_sector('ANM')
                
        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
            # Initialize with empty data
            self.sectors = []
            self.subsectors = []
            self.systems = []
            self.planets = []
    
    def _get_table_list(self):
        """Get list of tables in the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting table list: {e}")
            return []
    
    def _load_sectors(self):
        """Load sectors from the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM sectors")
            self.sectors = [dict(row) for row in cursor.fetchall()]
            
            # Track all sector codes we have
            self.sector_codes = {sector.get('location', '') for sector in self.sectors if sector.get('location')}
            
            # Build the sector_by_code mapping
            self.sector_by_code = {
                sector.get('location'): sector.get('id') 
                for sector in self.sectors 
                if sector.get('location')
            }
        except Exception as e:
            print(f"Error loading sectors: {e}")
            self.sectors = []
    
    def _load_subsectors(self):
        """Load subsectors from the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM subsectors")
            self.subsectors = [dict(row) for row in cursor.fetchall()]
            
            # Build the subsector_by_code mapping
            self.subsector_by_code = {
                subsector.get('location'): subsector.get('id') 
                for subsector in self.subsectors 
                if subsector.get('location')
            }
        except Exception as e:
            print(f"Error loading subsectors: {e}")
            self.subsectors = []
    
    def _load_systems(self):
        """Load systems from the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM systems")
            self.systems = [dict(row) for row in cursor.fetchall()]
            
            # Build the system_by_code mapping
            self.system_by_code = {
                system.get('location'): system.get('id') 
                for system in self.systems 
                if system.get('location')
            }
        except Exception as e:
            print(f"Error loading systems: {e}")
            self.systems = []
    
    def _load_planets(self):
        """Load planets from the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM planets")
            self.planets = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error loading planets: {e}")
            self.planets = []
    
    def _create_specific_sector(self, sector_code):
        """Create a specific sector by code"""
        if sector_code in self.sector_codes:
            print(f"Sector {sector_code} already exists")
            return
        
        try:    
            next_id = max([sector.get('id', 0) for sector in self.sectors], default=0) + 1
            current_date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            stub_sector = {
                'id': next_id,
                'location': sector_code,
                'nav': 'Unexplored Sector',
                'note': 'Manually created stub sector',
                'date': current_date
            }
            self.sectors.append(stub_sector)
            self.sector_codes.add(sector_code)
            self.sector_by_code[sector_code] = next_id
            
            print(f"Created specific sector {sector_code} with ID {next_id}")
        except Exception as e:
            print(f"Error creating specific sector {sector_code}: {e}")
    
    def _create_stub_sectors(self):
        """Create stub sectors for any sectors referenced in subsectors, systems, or planets but not in the sectors table"""
        try:
            missing_sectors = set()
            
            # First, check planet locations for missing sectors
            for planet in self.planets:
                location = planet.get('location', '')
                if location and len(location) >= 3:
                    try:
                        # Parse location format - could be MMM1234 or MMM/123/4
                        if '/' in location:
                            parts = location.split('/')
                            sector_code = parts[0]
                        else:
                            sector_code = location[:3]
                        
                        if sector_code and sector_code not in self.sector_codes:
                            missing_sectors.add(sector_code)
                            print(f"Found missing sector {sector_code} from planet {location}")
                    except Exception as e:
                        print(f"Error parsing planet location {location}: {e}")
            
            # Check systems for missing sectors
            for system in self.systems:
                location = system.get('location', '')
                if location and len(location) >= 3:
                    try:
                        sector_code = location[:3]
                        if sector_code and sector_code not in self.sector_codes:
                            missing_sectors.add(sector_code)
                            print(f"Found missing sector {sector_code} from system {location}")
                    except Exception as e:
                        print(f"Error parsing system location {location}: {e}")
            
            # Check subsectors for missing sectors
            for subsector in self.subsectors:
                location = subsector.get('location', '')
                if location and len(location) >= 3:
                    try:
                        sector_code = location[:3]
                        if sector_code and sector_code not in self.sector_codes:
                            missing_sectors.add(sector_code)
                            print(f"Found missing sector {sector_code} from subsector {location}")
                    except Exception as e:
                        print(f"Error parsing subsector location {location}: {e}")
            
            # Create stub sectors for missing sectors
            print(f"Creating {len(missing_sectors)} stub sectors: {', '.join(missing_sectors)}")
            next_id = max([sector.get('id', 0) for sector in self.sectors], default=0) + 1
            current_date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            for sector_code in missing_sectors:
                stub_sector = {
                    'id': next_id,
                    'location': sector_code,
                    'nav': 'Unexplored Sector',
                    'note': 'Automatically generated stub sector',
                    'date': current_date
                }
                self.sectors.append(stub_sector)
                self.sector_codes.add(sector_code)
                self.sector_by_code[sector_code] = next_id
                print(f"Created stub sector for {sector_code} with ID {next_id}")
                next_id += 1
        except Exception as e:
            print(f"Error creating stub sectors: {e}")
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn = None
    
    def get_sector_id_by_code(self, code):
        """Get sector ID by location code"""
        if code is None:
            return None
        # First try the dictionary
        if code in self.sector_by_code:
            return self.sector_by_code.get(code)
        # If not found, search manually
        for sector in self.sectors:
            if sector.get('location') == code:
                return sector.get('id')
        return None
    
    def get_sector_by_code(self, sector_code):
        """Get a sector by its location code"""
        if not sector_code:
            return None
            
        for sector in self.sectors:
            if sector.get('location') == sector_code:
                return sector
        return None
    
    def get_subsector_id_by_code(self, code):
        """Get subsector ID by location code"""
        if code is None:
            return None
        # First try the dictionary
        if code in self.subsector_by_code:
            return self.subsector_by_code.get(code)
        # If not found, search manually
        for subsector in self.subsectors:
            if subsector.get('location') == code:
                return subsector.get('id')
        return None
    
    def get_system_id_by_code(self, code):
        """Get system ID by location code"""
        if code is None:
            return None
        # First try the dictionary
        if code in self.system_by_code:
            return self.system_by_code.get(code)
        # If not found, search manually
        for system in self.systems:
            if system.get('location') == code:
                return system.get('id')
        return None
    
    def get_stats(self):
        """Get stats about loaded data"""
        return {
            'sectors': len(self.sectors),
            'subsectors': len(self.subsectors),
            'systems': len(self.systems),
            'planets': len(self.planets)
        }
    
    def get_schema(self):
        """Get database schema information"""
        schema = {}
        try:
            cursor = self.conn.cursor()
            
            # Get list of tables
            tables = self._get_table_list()
            
            for table in tables:
                # Get column info for each table
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [{'name': row[1], 'type': row[2]} for row in cursor.fetchall()]
                schema[table] = columns
            
            return schema
        except Exception as e:
            print(f"Error getting schema: {e}")
            return {}
    
    def execute_query(self, query, params=None):
        """Execute a custom SQL query"""
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Return results for SELECT queries
            if query.strip().upper().startswith("SELECT"):
                return [dict(row) for row in cursor.fetchall()]
            
            # Return affected row count for other queries
            return cursor.rowcount
        except Exception as e:
            print(f"Error executing query: {e}")
            return [] if query.strip().upper().startswith("SELECT") else 0
    
    # Entity lookup methods
    def get_sector(self, sector_id):
        """Get a sector by ID"""
        if sector_id is None:
            return None
            
        for sector in self.sectors:
            if sector.get('id') == sector_id:
                return sector
        return None
    
    def get_subsector(self, subsector_id):
        """Get a subsector by ID"""
        if subsector_id is None:
            return None
            
        for subsector in self.subsectors:
            if subsector.get('id') == subsector_id:
                return subsector
        return None
    
    def get_system(self, system_id):
        """Get a system by ID"""
        if system_id is None:
            return None
            
        for system in self.systems:
            if system.get('id') == system_id:
                return system
        return None
    
    def get_planet(self, planet_id):
        """Get a planet by ID"""
        if planet_id is None:
            return None
            
        for planet in self.planets:
            if planet.get('id') == planet_id:
                return planet
        return None
    
    # Relational query methods
    def get_subsectors_for_sector(self, sector_id):
        """Get all subsectors for a sector"""
        if sector_id is None:
            return []
            
        sector = self.get_sector(sector_id)
        if not sector or not sector.get('location'):
            return []
            
        sector_code = sector.get('location')
        return [s for s in self.subsectors if s.get('location') and s.get('location').startswith(sector_code)]
    
    def get_systems_for_subsector(self, subsector_id):
        """Get all systems for a subsector"""
        if subsector_id is None:
            return []
            
        subsector = self.get_subsector(subsector_id)
        if not subsector or not subsector.get('location'):
            return []
            
        subsector_code = subsector.get('location')
        return [s for s in self.systems if s.get('location') and s.get('location').startswith(subsector_code)]
    
    def get_planets_for_system(self, system_id):
        """Get all planets for a system"""
        if system_id is None:
            return []
            
        system = self.get_system(system_id)
        if not system or not system.get('location'):
            return []
            
        system_code = system.get('location')
        return [p for p in self.planets if p.get('location') and p.get('location').startswith(system_code)]
    
    # Detail query methods
    def get_sector_details(self, sector_id):
        """Get sector details with related subsectors"""
        sector = self.get_sector(sector_id)
        if not sector:
            return None
        
        sector_data = dict(sector)
        sector_data['subsectors'] = self.get_subsectors_for_sector(sector_id)
        return sector_data
    
    def get_subsector_details(self, subsector_id):
        """Get subsector details with related systems and parent sector"""
        subsector = self.get_subsector(subsector_id)
        if not subsector:
            return None
        
        subsector_data = dict(subsector)
        subsector_data['systems'] = self.get_systems_for_subsector(subsector_id)
        
        # Find parent sector by code instead of ID
        location = subsector.get('location', '')
        if location and len(location) >= 3:
            sector_code = location[:3]
            parent_sector = self.get_sector_by_code(sector_code)
            if parent_sector:
                subsector_data['sector'] = parent_sector
                subsector_data['sector_id'] = parent_sector.get('id')
        
        return subsector_data
    
    def get_system_details(self, system_id):
        """Get system details with related planets and parent subsector"""
        system = self.get_system(system_id)
        if not system:
            return None
        
        system_data = dict(system)
        system_data['planets'] = self.get_planets_for_system(system_id)
        
        # Find parent subsector by code instead of ID
        location = system.get('location', '')
        if location and len(location) >= 6:
            subsector_code = location[:6]
            for subsector in self.subsectors:
                if subsector.get('location') == subsector_code:
                    system_data['subsector'] = subsector
                    system_data['subsector_id'] = subsector.get('id')
                    break
        
        return system_data
    
    def get_planet_details(self, planet_id):
        """Get planet details with parent system"""
        planet = self.get_planet(planet_id)
        if not planet:
            return None
        
        planet_data = dict(planet)
        
        # Find parent system by code instead of ID
        location = planet.get('location', '')
        if location and len(location) >= 7:
            system_code = location[:7]
            for system in self.systems:
                if system.get('location') == system_code:
                    planet_data['system'] = system
                    planet_data['system_id'] = system.get('id')
                    break
        
        return planet_data
        
    def debug_sector_status(self, sector_code):
        """Debug utility to print status of a specific sector"""
        print(f"\n--- DEBUG FOR SECTOR {sector_code} ---")
        
        # Check if sector exists
        sector = self.get_sector_by_code(sector_code)
        if sector:
            print(f"Sector exists with ID {sector.get('id')}")
        else:
            print(f"Sector NOT found")
        
        # Check for data in this sector
        subsectors = [s for s in self.subsectors if s.get('location') and s.get('location').startswith(sector_code)]
        systems = [s for s in self.systems if s.get('location') and s.get('location').startswith(sector_code)]
        planets = [p for p in self.planets if p.get('location') and p.get('location').startswith(sector_code)]
        
        print(f"Found {len(subsectors)} subsectors, {len(systems)} systems, {len(planets)} planets")
        
        # Print details of each planet
        for planet in planets:
            print(f"Planet: {planet.get('location', 'Unknown')} | Owner: {planet.get('owner', 'Unknown')}")
        
        print("--- END DEBUG ---\n")