
import pytest
from utils import distance, filter_by_proximity, filter_by_proximity_across_identifiers

# Test cases for distance function
def test_distance():
    test_cases = [
        ((0, 0, 0), (0, 0, 0), 0),     # Same point
        ((0, 0, 0), (3, 4, 0), 5),     # Common case
        ((-1, -1, 0), (1, 1, 0), 2.8284271247461903), # Negative coordinates
    ]
    results = []
    for point1, point2, expected in test_cases:
        results.append((point1, point2, distance(point1, point2), expected))
    assert results

# Test cases for filter_by_proximity function
def test_filter_by_proximity():
    test_cases = [
        ([(0, 0, 0), (3, 4, 0), (0, 1, 0)], 2, [(0, 0, 0), (3, 4, 0)]), # Filter one close point
        ([(0, 0, 0), (3, 4, 0), (5, 8, 0)], 10, [(0, 0, 0)]), # Filter two close points
        ([(0, 0, 0), (3, 4, 0), (5, 8, 0)], 50, [(0, 0, 0), (3, 4, 0), (5, 8, 0)]), # No filtering
    ]
    results = []
    for coords, threshold, expected in test_cases:
        results.append((coords, threshold, filter_by_proximity(coords, threshold), expected))
    assert results

# Test cases for filter_by_proximity_across_identifiers function
def test_filter_by_proximity_across_identifiers():
    test_cases = [
        ({
            "id1": [(0, 0, 0), (3, 4, 0)],
            "id2": [(0, 1, 0), (3, 3.9, 0)]
        }, 2, {
            "id1": [(0, 0, 0), (3, 4, 0)],
            "id2": []
        }), # Filter close points across identifiers
    ]
    results = []
    for coords_dict, threshold, expected in test_cases:
        results.append((coords_dict, threshold, filter_by_proximity_across_identifiers(coords_dict, threshold), expected))
    assert results
