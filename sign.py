import argparse
from extract import get_text_coordinates, modified_extraction_with_proximity_check,refined_multi_page_get_text_coordinates , adjust_signature_coordinates
from add_sig import  modified_add_signature_with_offset
import os
import shutil
from PyPDF2 import PdfReader
from utils import filter_by_proximity


def sign_pdf(input_pdf_path, temp_pdf_path, output_pdf_path, signatures, identifiers, offset_increment=40):
    # Copy the original PDF to a temporary PDF
    shutil.copy(input_pdf_path, temp_pdf_path)
    # Determine the number of pages in the PDF
    with open(input_pdf_path, "rb") as pdf_file:
        pdf = PdfReader(pdf_file)
        num_pages = len(pdf.pages)

    if num_pages > 2:
        print('Multiple Pages PDF for Signing')
        proximity = False
        with_white_space = False
        if proximity:
            coordinates_dict = modified_extraction_with_proximity_check(temp_pdf_path, identifiers)  
        if not proximity and not with_white_space:
            coordinates_dict = refined_multi_page_get_text_coordinates(temp_pdf_path, identifiers)
            coordinates_dict = adjust_signature_coordinates(coordinates_dict, 400, 200)
            
    else:
        # Using the modified get_text_coordinates function
        coordinates_dict = get_text_coordinates(temp_pdf_path, identifiers)

    print('Coordinates found for,', coordinates_dict)


    for index, (signature_path, identifier_text) in enumerate(zip(signatures, identifiers)):
        if identifier_text in coordinates_dict:
            for coordinates in coordinates_dict[identifier_text]:
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
    parser = argparse.ArgumentParser(description="Automatically sign PDF files.")
    parser.add_argument("input_pdf", type=str, help="Path to the input PDF file.")
    parser.add_argument("output_pdf", type=str, help="Path to the output signed PDF file.")
    parser.add_argument("--signatures", type=str, nargs='+', required=True, help="Path(s) to the signature image file(s).")
    parser.add_argument("--identifiers", type=str, nargs='+', required=True, help="Identifier text(s) where the signature needs to be placed.")
    
    args = parser.parse_args()

    if len(args.signatures) != len(args.identifiers):
        print("Error: You must provide an equal number of signature images and identifiers.")
        return
    
    temp_pdf = "temp_output.pdf"
    sign_pdf(args.input_pdf, temp_pdf,  args.output_pdf, args.signatures, args.identifiers)

if __name__ == "__main__":
    main()
