from PyPDF2 import PdfReader, PdfWriter, PageObject, Transformation
from PIL import Image
from extract import verify_content_at_coordinates
from io import BytesIO
from reportlab.pdfgen import canvas




def add_signature_to_pdf(input_pdf_path, output_pdf_path, signature_path, coordinates, scale_factor):

    print("Adding Signature to the,",input_pdf_path, signature_path)
    
    img = Image.open(signature_path)
    pdf_bytes = BytesIO()
    img.save(pdf_bytes, "PDF")
    pdf_bytes.seek(0)  # Reset the position to the beginning of the BytesIO stream

    with open(input_pdf_path, "rb") as pdf_file:
        pdf = PdfReader(pdf_file)
        signature_pdf = PdfReader(pdf_bytes)
        pdf_writer = PdfWriter()

        # Extracting x, y coordinates and page number
        x, y, target_page_num = coordinates
        
        # Iterate through the pages and add the signature only to the target page
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            
            # Check if current page is the target page
            if page_num == target_page_num:
                # Create a blank page with the same size as the original page
                signature_page = PageObject.create_blank_page(width=page.mediabox.width, 
                                                            height=page.mediabox.height)
                
                # Apply the scaling and translation transformation to the signature's PDF page
                signature_pdf.pages[0].add_transformation(Transformation().scale(scale_factor).translate(x, y))
                
                # Merge the signature page with the blank page
                signature_page.merge_page(signature_pdf.pages[0])
                
                # Merge the signature page with the original page
                page.merge_page(signature_page)
                
            pdf_writer.add_page(page)
        
        # Write the output
        with open(output_pdf_path, "wb") as output_file:
            pdf_writer.write(output_file)
            



def modified_add_signature_with_offset(input_pdf_path, output_pdf_path, signature_path, coordinates, x_offset,  y_offset, scale_factor):
    """
    Add signature to PDF with a y-offset and verify its addition based on content at expected coordinates.
    """
    if x_offset and y_offset: 
         # Apply the y-offset if the signed output is not desired
        x, y, target_page_num = coordinates
        x -= x_offset
        y -= y_offset 
    else: 
        x, y, target_page_num = coordinates
    
    overlay_signature_on_pdf(input_pdf_path, output_pdf_path, signature_path, (x, y, target_page_num), scale_factor)
    
    # Verify if there's content at the expected signature coordinates
    if not verify_content_at_coordinates(output_pdf_path, (x, y, target_page_num)):
        print(f"Error: Content not detected at expected coordinates for signature '{signature_path}' in {output_pdf_path}.")






def create_signature_pdf(signature_path, coordinates, page_size, scale_factor=0):
    """
    Create a PDF with the signature image at the specified coordinates.
    """
    print('Creating signature PDF', signature_path, page_size)
    # Create a new PDF in memory
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=page_size)

    c.setStrokeColor((0, 0, 0, 0)) 

    #img = ImageReader(signature_path)
    
    # Place the signature image on the PDF at the specified coordinates
    x, y, _ = coordinates
    c.drawImage(signature_path, x, y, width=100*scale_factor, height=50*scale_factor, mask='auto')  # Adjust width and height as needed
    
    # Save the PDF to the BytesIO stream
    c.save()
    
    # Reset the stream position
    output.seek(0)
    return output


def overlay_signature_on_pdf(input_pdf_path, output_pdf_path, signature_path, coordinates, scale_factor):
    """
    Overlay the signature image directly onto the PDF at the specified coordinates.
    """
    # Create a signature PDF with the image at the desired coordinates
    with open(input_pdf_path, "rb") as pdf_file:
        pdf = PdfReader(pdf_file)
        page_size = pdf.pages[0].mediabox[2], pdf.pages[0].mediabox[3]  # Extract width and height from the first page
        signature_pdf_stream = create_signature_pdf(signature_path, coordinates, page_size, scale_factor)
        signature_pdf = PdfReader(signature_pdf_stream)
        
        # Merge the signature PDF with the original PDF
        pdf_writer = PdfWriter()
        for page_num, page in enumerate(pdf.pages):
            if page_num == coordinates[2]:  # Check if it's the target page
                page.merge_page(signature_pdf.pages[0])
            pdf_writer.add_page(page)
        
        # Write the merged PDF to the output file
        with open(output_pdf_path, "wb") as output_file:
            pdf_writer.write(output_file)
