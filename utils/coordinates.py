"""
Coordinates Module
Handles coordinate calculations for the Takamo galaxy
"""
import math

def get_coordinates_from_sector(location):
    """
    Get X, Y, Z coordinates from a sector location string (like "MMM")
    
    Args:
        location (str): The sector location code (3 letters)
        
    Returns:
        dict: Coordinates as {x, y, z}
    """
    if not location or len(location) < 3:
        return {'x': 0, 'y': 0, 'z': 0}
    
    try:
        # A = 0, B = 1, ..., Z = 25
        x = ord(location[0].upper()) - 65
        y = ord(location[1].upper()) - 65
        z = ord(location[2].upper()) - 65
        
        # Ensure values are in range 0-25
        x = max(0, min(25, x))
        y = max(0, min(25, y))
        z = max(0, min(25, z))
        
        return {'x': x, 'y': y, 'z': z}
    except Exception as e:
        print(f"Error parsing sector coordinates from {location}: {e}")
        return {'x': 0, 'y': 0, 'z': 0}

def get_coordinates_from_subsector(location):
    """
    Get X, Y, Z coordinates from a subsector location string (like "MMM222")
    
    Args:
        location (str): The subsector location code (3 letters + 3 digits)
        
    Returns:
        dict: Coordinates as {x, y, z, sx, sy, sz}
    """
    if not location or len(location) < 6:
        return {'x': 0, 'y': 0, 'z': 0, 'sx': 0, 'sy': 0, 'sz': 0}
    
    try:
        sector_part = location[:3]
        subsector_part = location[3:6]
        
        sector_coords = get_coordinates_from_sector(sector_part)
        
        # Default subsector coordinates
        sx, sy, sz = 0, 0, 0
        
        # Subsector coordinates (1-indexed in the data to 0-indexed for calculations)
        try:
            sx = int(subsector_part[0]) - 1
            sy = int(subsector_part[1]) - 1
            sz = int(subsector_part[2]) - 1
            
            # Ensure values are in valid range
            sx = max(0, min(9, sx))
            sy = max(0, min(9, sy))
            sz = max(0, min(9, sz))
        except ValueError:
            # If parsing fails, use default values
            pass
        
        return {
            'x': sector_coords['x'], 
            'y': sector_coords['y'], 
            'z': sector_coords['z'],
            'sx': sx, 
            'sy': sy, 
            'sz': sz
        }
    except Exception as e:
        print(f"Error parsing subsector coordinates from {location}: {e}")
        return {'x': 0, 'y': 0, 'z': 0, 'sx': 0, 'sy': 0, 'sz': 0}

def get_coordinates_from_system(location):
    """
    Get X, Y, Z coordinates from a system location string (like "MMM2221")
    
    Args:
        location (str): The system location code (3 letters + 3 digits + 1 digit)
        
    Returns:
        dict: Coordinates as {x, y, z, sx, sy, sz, system_pos}
    """
    if not location or len(location) < 7:
        return {
            'x': 0, 'y': 0, 'z': 0, 
            'sx': 0, 'sy': 0, 'sz': 0, 
            'system_pos': 0
        }
    
    try:
        subsector_part = location[:6]
        
        # Default system position
        system_pos = 0
        
        # Try to get the last digit as system position
        try:
            system_pos = int(location[6]) - 1  # Convert to 0-indexed
            system_pos = max(0, min(9, system_pos))  # Ensure in valid range
        except ValueError:
            # If parsing fails, use default value
            pass
        
        subsector_coords = get_coordinates_from_subsector(subsector_part)
        subsector_coords['system_pos'] = system_pos
        
        return subsector_coords
    except Exception as e:
        print(f"Error parsing system coordinates from {location}: {e}")
        return {
            'x': 0, 'y': 0, 'z': 0, 
            'sx': 0, 'sy': 0, 'sz': 0, 
            'system_pos': 0
        }

def calculate_sector_distance(sector1, sector2):
    """
    Calculate the distance between two sectors in 3D space
    
    Args:
        sector1 (str): First sector location code
        sector2 (str): Second sector location code
        
    Returns:
        float: Distance in sectors
    """
    if not sector1 or not sector2:
        return 0.0
        
    try:
        coords1 = get_coordinates_from_sector(sector1)
        coords2 = get_coordinates_from_sector(sector2)
        
        # Calculate distance using the 3D distance formula
        dx = coords2['x'] - coords1['x']
        dy = coords2['y'] - coords1['y']
        dz = coords2['z'] - coords1['z']
        
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    except Exception as e:
        print(f"Error calculating sector distance between {sector1} and {sector2}: {e}")
        return 0.0

def format_location(location):
    """
    Format a location code for display
    
    Args:
        location (str): Location code
        
    Returns:
        str: Formatted location display
    """
    if not location:
        return ''
    
    try:
        if len(location) == 3:
            # Sector
            return location
        elif len(location) == 6:
            # Subsector
            return f"{location[:3]}-{location[3:]}"
        elif len(location) == 7:
            # System
            return f"{location[:3]}-{location[3:6]}-{location[6]}"
        elif len(location) == 8:
            # Planet
            return f"{location[:3]}-{location[3:6]}-{location[6]}-{location[7]}"
        
        # Handle slash format if present
        if '/' in location:
            parts = location.split('/')
            if len(parts) == 3:
                return f"{parts[0]}-{parts[1]}-{parts[2]}"
            elif len(parts) == 4:
                return f"{parts[0]}-{parts[1]}-{parts[2]}-{parts[3]}"
        
        return location
    except Exception as e:
        print(f"Error formatting location {location}: {e}")
        return str(location)