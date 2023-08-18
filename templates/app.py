import os
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from flask import Flask, request, render_template, send_from_directory

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'separated_files'), filename=filename, as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def convert_pdf():
    if request.method == 'POST':
        if 'pdfFile' in request.files:
            pdf_file = request.files['pdfFile']
            pdf_filename = pdf_file.filename

            temp_dir = tempfile.mkdtemp()
            pdf_path = os.path.join(temp_dir, pdf_filename)
            pdf_file.save(pdf_path)

            input_pdf = PdfReader(open(pdf_path, 'rb'))

            separated_files = []
            for page_number, page in enumerate(input_pdf.pages, start=1):
                output_pdf = PdfWriter()
                output_pdf.add_page(page)

                output_path = os.path.join(temp_dir, f'page_{page_number}.pdf')
                with open(output_path, 'wb') as output_file:
                    output_pdf.write(output_file)

                separated_files.append(output_path)

            target_dir = os.path.join(app.root_path, 'static', 'separated_files')
            os.makedirs(target_dir, exist_ok=True)
            moved_files = []
            for file_path in separated_files:
                new_file_path = os.path.join(target_dir, os.path.basename(file_path))
                os.rename(file_path, new_file_path)
                moved_files.append(new_file_path)

            return render_template('result.html', pdf_path=pdf_path, pdf_filename=pdf_filename,
                       separated_files=moved_files, os=os)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
