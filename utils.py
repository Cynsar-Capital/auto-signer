from math import sqrt

def distance(point1, point2):
    """
    Calculate the Euclidean distance between two points.
    """
    x1, y1, _ = point1
    x2, y2, _ = point2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def distance_x_y(x,y):
    # Calculate distance based on x and y coordinates only
    return sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)
    

def filter_by_proximity(coordinates_list, threshold=50):
    """
    Filter coordinates based on proximity. If two points are too close, remove one of them.
    """
    filtered_coordinates = []
    for i, coord1 in enumerate(coordinates_list):
        too_close = False
        for j, coord2 in enumerate(coordinates_list):
            if i != j and distance(coord1, coord2) < threshold:
                too_close = True
                break
        if not too_close:
            filtered_coordinates.append(coord1)
    return filtered_coordinates


def filter_by_proximity_across_identifiers(coordinates_dict, threshold=50):
    """
    Filter coordinates based on proximity across different identifiers. 
    If coordinates of one identifier are too close to coordinates of another identifier on the same page, remove one of them.
    """
    # Flatten the coordinates and store them with their associated identifier
    all_coordinates = [(identifier, coord) for identifier, coords in coordinates_dict.items() for coord in coords]
    
    to_remove = set()  # Set to keep track of coordinates to remove
    
    for i, (id1, coord1) in enumerate(all_coordinates):
        for j, (id2, coord2) in enumerate(all_coordinates):
            if i != j and id1 != id2 and coord1[2] == coord2[2] and distance_x_y(coord1, coord2) < threshold:
                to_remove.add(coord1)
                to_remove.add(coord2)
    
    for identifier in coordinates_dict:
        coordinates_dict[identifier] = [coord for coord in coordinates_dict[identifier] if coord not in to_remove]
    return coordinates_dict