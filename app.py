import os
import tempfile
import shutil
import random
import string
from PyPDF2 import PdfReader, PdfWriter
from flask import Flask, request, render_template, send_from_directory

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route('/download/<filename>')
def download(filename):
    directory = os.path.join(app.root_path, 'static', 'separated_files')
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def convert_pdf():
    if request.method == 'POST':
        if 'pdfFile' in request.files:
            pdf_file = request.files['pdfFile']
            pdf_filename = pdf_file.filename

            temp_dir = os.path.join(app.root_path, 'temp')  # Use a specific folder for temporary files
            os.makedirs(temp_dir, exist_ok=True)  # Create the temp folder if it doesn't exist

            pdf_path = os.path.join(temp_dir, pdf_filename)
            pdf_file.save(pdf_path)

            input_pdf = PdfReader(open(pdf_path, 'rb'))

            separated_files = []
            for page_number, page in enumerate(input_pdf.pages, start=1):
                output_pdf = PdfWriter()
                output_pdf.add_page(page)

                output_filename = f'page_{page_number}_{generate_random_string()}.pdf'
                output_path = os.path.join(temp_dir, output_filename)
                with open(output_path, 'wb') as output_file:
                    output_pdf.write(output_file)

                separated_files.append(output_path)

            target_dir = os.path.join(app.root_path, 'static', 'separated_files')
            # Eliminar archivos anteriores en la carpeta static/separated_files
            shutil.rmtree(target_dir)
            os.makedirs(target_dir, exist_ok=True)

            moved_files = []
            for file_path in separated_files:
                new_file_path = os.path.join(target_dir, os.path.basename(file_path))
                # Cerrar el archivo PDF antes de moverlo
                output_pdf.close()
                shutil.move(file_path, new_file_path)  # Use shutil.move instead of os.rename
                moved_files.append(new_file_path)

            # Cerrar el archivo PDF de entrada
            input_pdf.stream.close()

            # Eliminar la carpeta temporal de la conversión actual
            shutil.rmtree(temp_dir)

            return render_template('result.html', pdf_path=pdf_path, pdf_filename=pdf_filename,
                       separated_files=moved_files, os=os)

    return render_template('index.html')


def generate_random_string(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
