

# AutoSigner


AutoSigner is a Python-based utility designed to automate the process of placing signatures on PDFs at specified identifiers' locations. The tool scans the PDF for given identifiers and then overlays the provided signatures at the corresponding positions.

## Features
- **Signature Placement**: Automatically places signatures at specified identifiers in a PDF.
- **Multiple Signatures**: Supports multiple signature placements in a single PDF.
- **Intelligent Detection**: If multiple signature identifiers are too close, the tool can adjust the placement to prevent overlapping.

## Prerequisites
- Python 3.x
- Dependencies from `requirements.txt`

## Setup
1. Clone the repository.
```
git clone https://github.com/Cynsar-Capital/auto-signer.git
```
2. Navigate to the project directory.
```
cd autosigner
```
3. Install the required packages.
```
pip install -r requirements.txt
```

## Usage
```
python sign.py --input_pdf [INPUT_PDF_PATH] --output_pdf [OUTPUT_PDF_PATH] --signatures [SIGNATURE_PATH_1, SIGNATURE_PATH_2,...] --identifiers [IDENTIFIER_1, IDENTIFIER_2,...]
```

## TODO
1. **Fix Spacing Issues**: Enhance the code to handle close Signature Identifiers better and prevent appending signatures too close or on top of each other.
2. **Signature Spacing**: If two signatures are provided, ensure that they have a predefined spacing between them for clearer visualization.
3. **Web-based Interface**: Implement a user-friendly web interface, allowing users to easily run the utility by providing signatures, coordinates, or identifier values.

## Ideas for Improvement
1. **Signature Resizing**: Implement a feature to resize the signature image based on the available space in the PDF.
2. **OCR Integration**: Use OCR to detect signature blocks in PDFs that are scanned images.
3. **Batch Processing**: Allow the tool to process multiple PDFs in a batch, especially useful for bulk signing tasks.
4. **Customizable Layouts**: Allow users to choose from a set of layouts for placing multiple signatures.
5. **Integration with Cloud Storage**: Integrate with cloud storage solutions like Google Drive or Dropbox for easier access and processing of PDFs and signatures.
6. **Interactive UI**: Create an interactive UI where users can visually select where they want signatures placed on the PDF.
7. **Single Identifiers**: If the page has the identifiers listed somewhere as paragraph need more rules to avoid that.

