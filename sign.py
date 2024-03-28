import argparse

from numpy import False_
from extract import get_text_coordinates, modified_extraction_with_proximity_check,refined_multi_page_get_text_coordinates , adjust_signature_coordinates
from add_sig import  modified_add_signature_with_offset
import os
import shutil
from PyPDF2 import PdfReader
from utils import filter_by_proximity


def sign_pdf(input_pdf_path, temp_pdf_path, output_pdf_path, signatures, identifiers=None, check_proximity=False, adjust_coords=False, reference_text_distance=30, spacing=5, force_refined=False, offset_increment=0, scale_factor=0, footer_padding=20):
    shutil.copy(input_pdf_path, temp_pdf_path)

    if identifiers is None or len(identifiers) == 0:
            # Handle the general case without identifiers
            with open(input_pdf_path, "rb") as pdf_file:
                        pdf = PdfReader(pdf_file)
                        num_pages = len(pdf.pages)
                        page_width = float(pdf.pages[0].mediabox.width)
                        page_height = float(pdf.pages[0].mediabox.height) # Extract width and height from the first page

            signature_width = 100 * scale_factor
            total_signature_width = len(signatures) * signature_width + (len(signatures) - 1) * spacing

            start_x = (page_width - total_signature_width) / 2  # Center the signatures horizontally

            for page_num in range(num_pages):
                        for index, signature_path in enumerate(signatures):
                            x = start_x + index * (signature_width + spacing)
                            y = footer_padding  # Place signatures in the footer area with padding

                            coordinates = (x, y, page_num)  # Place on the current page

                            x_offset = offset_increment
                            y_offset = index * offset_increment
                            modified_add_signature_with_offset(temp_pdf_path, output_pdf_path, signature_path, coordinates, x_offset, y_offset, scale_factor)

                            # After adding the signature, copy the output to temp for the next iteration
                            shutil.copy(output_pdf_path, temp_pdf_path)
                            print(f"Signature placement process finished without error")

    else:
        # Determine the number of pages in the PDF
        with open(input_pdf_path, "rb") as pdf_file:
            pdf = PdfReader(pdf_file)
            num_pages = len(pdf.pages)

        coordinates_dict = {}

        if num_pages > 2:
            print("The pdf has", num_pages, "pages")
            coordinates_dict = modified_extraction_with_proximity_check(temp_pdf_path, identifiers)
            is_empty = all(len(coords) == 0 for coords in coordinates_dict.values())

        if force_refined and is_empty:
            print("The above did not work and now falling back to refined_multi_page_get_text_coordinates()")
            coordinates_dict = refined_multi_page_get_text_coordinates(temp_pdf_path, identifiers)

        if adjust_coords and check_proximity:
            print("Since the adjust Coords is passed on", adjust_coords, check_proximity)
            coordinates_dict = adjust_signature_coordinates(coordinates_dict, reference_text_distance, spacing)

        elif num_pages < 2 and not adjust_coords and not check_proximity:
            print("Checking on", num_pages)
            coordinates_dict = get_text_coordinates(temp_pdf_path, identifiers)

        elif not any(coordinates_dict.values()):
            print("Else falling back on", num_pages, "get_text_coordinates")
            coordinates_dict = get_text_coordinates(temp_pdf_path, identifiers)


        print('Coordinates found for,', coordinates_dict)


        for index, (signature_path, identifier_text) in enumerate(zip(signatures, identifiers)):
            if identifier_text in coordinates_dict:
                coords_list = coordinates_dict[identifier_text]
                # Check if coords_list is an iterable with at least one set of coordinates
                if not isinstance(coords_list, (list, tuple)) or not coords_list:
                    print(f"Unexpected coordinates format for identifier '{identifier_text}': {coords_list}")
                    continue
                if len(coords_list) == 3:
                    print("Single Coordinate Found")
                    coordinates = coordinates_dict[identifier_text]
                    x_offset = offset_increment
                    y_offset = index * offset_increment
                    modified_add_signature_with_offset(temp_pdf_path, output_pdf_path, signature_path, coordinates, x_offset, y_offset)
                    # After adding the signature, copy the output to temp for the next iteration
                    shutil.copy(output_pdf_path, temp_pdf_path)
                    print(f"Signature placement process finished without error")
                else:
                    print("Multiple Coordinate Found")
                    for coordinates in coords_list:
                        x_offset = index * offset_increment
                        y_offset = index * offset_increment
                        modified_add_signature_with_offset(temp_pdf_path, output_pdf_path, signature_path, coordinates, x_offset, y_offset,scale_factor)
                        # After adding the signature, copy the output to temp for the next iteration
                        shutil.copy(output_pdf_path, temp_pdf_path)
                        print(f"Signature placement process finished without error")
            else:
                print(f"Identifier '{identifier_text}' not found in {temp_pdf_path}.")

    # Once all signatures are added, you can remove the temp file
    os.remove(temp_pdf_path)

def main():
    parser = argparse.ArgumentParser(description="Automatically sign PDFs at specified identifiers' locations.")
    parser.add_argument("--force_refined", action="store_true", help="Force using refined multi-page text coordinate extraction.")
    parser.add_argument("--input_pdf", required=True, help="Path to the input PDF.")
    parser.add_argument("--output_pdf", required=True, help="Path to the output signed PDF.")
    parser.add_argument("--signatures", required=True, nargs='+', help="List of paths to signature images.")
    parser.add_argument("--identifiers", required=False, nargs='+', help="List of identifier texts in the PDF where signatures should be placed.")
    parser.add_argument("--check_proximity", action="store_true", help="Enable proximity check to refine signature placement.")
    parser.add_argument("--adjust_coords", action="store_true", help="Adjust signature coordinates if they are too close.")
    parser.add_argument("--reference_text_distance", type=int, default=30, help="Reference distance to check proximity of text blocks (default: 30).")
    parser.add_argument("--spacing", type=int, default=5, help="Spacing to be used between signatures if they are too close (default: 5).")
    parser.add_argument("--offset", type=int, default=0, help="Offset to be used between signatures for creating space (default: 0).")
    parser.add_argument("--scale_factor", type=float, default=0.8, help="Scale Factor for scaling the signatures  (default: 0.8).")
    parser.add_argument("--add_text", help="Add text to the existing PDF.")




    args = parser.parse_args()

    if args.identifiers is None or len(args.identifiers) == 0:
        temp_pdf = "temp_output.pdf"
        sign_pdf(args.input_pdf, temp_pdf, args.output_pdf, args.signatures, check_proximity=args.check_proximity, adjust_coords=args.adjust_coords, reference_text_distance=args.reference_text_distance, spacing=args.spacing, force_refined=args.force_refined, offset_increment=args.offset, scale_factor=args.scale_factor)
    else:
        if len(args.signatures) != len(args.identifiers):
            print("Error: You must provide an equal number of signature images and identifiers.")
            return

        temp_pdf = "temp_output.pdf"
        sign_pdf(args.input_pdf, temp_pdf,  args.output_pdf, args.signatures, args.identifiers, args.check_proximity, args.adjust_coords, args.reference_text_distance, args.spacing, args.force_refined, args.offset, args.scale_factor)

if __name__ == "__main__":
    main()
