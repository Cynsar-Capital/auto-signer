import argparse
from extract import get_text_coordinates, modified_extraction_with_proximity_check,refined_multi_page_get_text_coordinates , adjust_signature_coordinates
from add_sig import  modified_add_signature_with_offset
import os
import shutil
from PyPDF2 import PdfReader
from utils import filter_by_proximity


def sign_pdf(input_pdf_path, temp_pdf_path, output_pdf_path, signatures, identifiers, offset_increment=40, check_proximity=False, adjust_coords=False, reference_text_distance=30, spacing=5):
    # Copy the original PDF to a temporary PDF
    shutil.copy(input_pdf_path, temp_pdf_path)
    # Determine the number of pages in the PDF
    with open(input_pdf_path, "rb") as pdf_file:
        pdf = PdfReader(pdf_file)
        num_pages = len(pdf.pages)

    coordinates_dict = {}
    
    if num_pages > 2:
        coordinates_dict = modified_extraction_with_proximity_check(temp_pdf_path, identifiers)
    if not any(coordinates_dict.values()):
        coordinates_dict = refined_multi_page_get_text_coordinates(temp_pdf_path, identifiers)

    if adjust_coords and check_proximity:
        coordinates_dict = adjust_signature_coordinates(coordinates_dict, reference_text_distance, spacing)
    
    elif num_pages < 2 and not adjust_coords and not check_proximity:
        coordinates_dict = get_text_coordinates(temp_pdf_path, identifiers)

    else:
    # You can add any other conditions or fallback logic here if needed
        coordinates_dict = get_text_coordinates(temp_pdf_path, identifiers)


    print('Coordinates found for,', coordinates_dict)


    for index, (signature_path, identifier_text) in enumerate(zip(signatures, identifiers)):
        if identifier_text in coordinates_dict:
            coordinates = coordinates_dict[identifier_text]
            # Check if coordinates is an iterable with at least three values
            if not isinstance(coordinates, (list, tuple)) or len(coordinates) < 3:
                print(f"Unexpected coordinates format for identifier '{identifier_text}': {coordinates}")
                continue

            x_offset = offset_increment
            y_offset = index * offset_increment
            modified_add_signature_with_offset(temp_pdf_path, output_pdf_path, signature_path, coordinates, x_offset, y_offset)
            # After adding the signature, copy the output to temp for the next iteration
            shutil.copy(output_pdf_path, temp_pdf_path)
        else:
            print(f"Identifier '{identifier_text}' not found in {temp_pdf_path}.")


    # Once all signatures are added, you can remove the temp file
    os.remove(temp_pdf_path)

def main():
    parser = argparse.ArgumentParser(description="Automatically sign PDFs at specified identifiers' locations.")
    parser.add_argument("--input_pdf", required=True, help="Path to the input PDF.")
    parser.add_argument("--output_pdf", required=True, help="Path to the output signed PDF.")
    parser.add_argument("--signatures", required=True, nargs='+', help="List of paths to signature images.")
    parser.add_argument("--identifiers", required=True, nargs='+', help="List of identifier texts in the PDF where signatures should be placed.")
    parser.add_argument("--check_proximity", action="store_true", help="Enable proximity check to refine signature placement.")
    parser.add_argument("--adjust_coords", action="store_true", help="Adjust signature coordinates if they are too close.")
    parser.add_argument("--reference_text_distance", type=int, default=30, help="Reference distance to check proximity of text blocks (default: 30).")
    parser.add_argument("--spacing", type=int, default=5, help="Spacing to be used between signatures if they are too close (default: 5).")

    
    args = parser.parse_args()

    if len(args.signatures) != len(args.identifiers):
        print("Error: You must provide an equal number of signature images and identifiers.")
        return
    
    temp_pdf = "temp_output.pdf"
    sign_pdf(args.input_pdf, temp_pdf,  args.output_pdf, args.signatures, args.identifiers, args.check_proximity, args.adjust_coords, args.reference_text_distance, args.spacing)

if __name__ == "__main__":
    main()
