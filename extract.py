from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from utils import filter_by_proximity_across_identifiers

from scipy.spatial.distance import euclidean

def get_text_coordinates(pdf_path, search_texts):
    coordinates_dict = {}
    for search_text in search_texts:
        for page_num, page_layout in enumerate(extract_pages(pdf_path)):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        if search_text in text_line.get_text():
                            start = text_line.get_text().find(search_text)
                            end = start + len(search_text)
                            chars = text_line._objs
                            if start < len(chars) and end <= len(chars):
                                # Take the average of the start and end coordinates
                                x0 = (chars[start].x0 + chars[end-1].x0) / 2
                                y0 = (chars[start].y0 + chars[end-1].y0) / 2
                                coordinates_dict[search_text] = (x0, y0, page_num)
    return coordinates_dict



def verify_signature_in_pdf(pdf_path, signature_path):
    """
    Verify if the signature's path is found in the PDF.
    """
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if signature_path in text_line.get_text():
                        return True
    return False


def verify_content_at_coordinates(pdf_path, coordinates):
    """
    Verify if there's any content at the specified coordinates in the PDF.
    """
    x, y, target_page_num = coordinates
    for page_num, page_layout in enumerate(extract_pages(pdf_path)):
        if page_num == target_page_num:
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    # Check if the element's bounding box intersects with the target coordinates
                    if element.x0 <= x <= element.x1 and element.y0 <= y <= element.y1:
                        return True
    return False


def modified_multi_page_get_text_coordinates(pdf_path, identifiers):
    """
    Extract the coordinates of the given identifiers from the PDF.
    Returns a dictionary where each identifier maps to a list of coordinates (x, y, page number).
    """
    coordinates_dict = {identifier: [] for identifier in identifiers}
    
    for page_num, page_layout in enumerate(extract_pages(pdf_path)):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    for identifier in identifiers:
                        if identifier in text_line.get_text():
                            x = (text_line.x0 + text_line.x1) / 2
                            y = (text_line.y0 + text_line.y1) / 2
                            coordinates_dict[identifier].append((x, y, page_num))
    
    # Filter out identifiers without any coordinates
    coordinates_dict = {k: v for k, v in coordinates_dict.items() if v}
    return coordinates_dict


def modified_extraction_with_proximity_check(pdf_path, identifiers):
    """
    Extract the coordinates of the given identifiers from the PDF with a proximity check.
    """
    coordinates_dict = modified_multi_page_get_text_coordinates(pdf_path, identifiers)
    
    return filter_by_proximity_across_identifiers(coordinates_dict)


def refined_multi_page_get_text_coordinates(pdf_path, identifiers):
    """
    Refine the extraction of coordinates to consider individual character bounding boxes.
    """
    coordinates_dict = {identifier: [] for identifier in identifiers}
    
    for page_num, page_layout in enumerate(extract_pages(pdf_path)):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    for identifier in identifiers:
                        if identifier in text_line.get_text():
                            # Extract bounding boxes for each character in the identifier
                            char_bboxes = [char.bbox for char in text_line if char.get_text() in identifier]
                            # Calculate the average center point of the character bounding boxes
                            avg_x = sum([bbox[0] + bbox[2] for bbox in char_bboxes]) / (2 * len(char_bboxes))
                            avg_y = sum([bbox[1] + bbox[3] for bbox in char_bboxes]) / (2 * len(char_bboxes))
                            coordinates_dict[identifier].append((avg_x, avg_y, page_num))
    
    # Filter out identifiers without any coordinates
    coordinates_dict = {k: v for k, v in coordinates_dict.items() if v}
    return coordinates_dict


def adjust_signature_coordinates(coordinates_dict, reference_text_distance=30, spacing=5):
    """
    Adjust coordinates based on proximity and reference text.
    """
    adjusted_coordinates = {}
    

    # A set to keep track of processed coordinates to avoid double adjustments
    processed_coords = set()

    for identifier, coords_list in coordinates_dict.items():
        for coords in coords_list:
            x, y, page_num = coords
            
            # If this coordinate is already processed, skip it
            if coords in processed_coords:
                continue

            # Check if another identifier's coordinates are nearby
            for other_identifier, other_coords_list in coordinates_dict.items():
                if identifier != other_identifier:
                    for other_coords in other_coords_list:
                        other_x, other_y, other_page_num = other_coords
                        
                        # If the other coordinate is already processed, skip it
                        if other_coords in processed_coords:
                            continue
                        
                        if other_page_num == page_num and euclidean((x, y), (other_x, other_y)) < reference_text_distance:
                            # Adjust the x-coordinates of the second signature by adding spacing to the x-coordinate of the first signature
                            adjusted_other_x = x + spacing
                            
                            if identifier not in adjusted_coordinates:
                                adjusted_coordinates[identifier] = []
                            if other_identifier not in adjusted_coordinates:
                                adjusted_coordinates[other_identifier] = []
                                
                            adjusted_coordinates[identifier].append(coords)
                            adjusted_coordinates[other_identifier].append((adjusted_other_x, other_y, other_page_num))
                            
                            # Mark these coordinates as processed
                            processed_coords.add(coords)
                            processed_coords.add(other_coords)
                        else:
                            if identifier not in adjusted_coordinates:
                                adjusted_coordinates[identifier] = []
                            adjusted_coordinates[identifier].append(coords)
                            
    return adjusted_coordinates
