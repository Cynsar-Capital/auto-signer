import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO



def add_text_to_pdf(input_pdf_path, output_pdf_path, text, x, y):
    # Create a PDF in-memory
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    # Set the location of the new text
    can.drawString(x, y, text)
    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PyPDF2.PdfReader(packet)

    # Read the existing PDF
    existing_pdf = PyPDF2.PdfReader(open(input_pdf_path, "rb"))
    output = PyPDF2.PdfWriter()

    # Add the "watermark" (which is the new text) on the existing page
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # Write the modified content to an output file
    with open(output_pdf_path, "wb") as output_stream:
        output.write(output_stream)