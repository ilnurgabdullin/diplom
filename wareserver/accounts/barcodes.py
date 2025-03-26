from reportlab.lib.pagesizes import mm, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO
import base64
import os
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph


from fpdf import FPDF

def generate_pdf(data, shipment_id):
    # Создаем объект PDF
    pdf = FPDF()
    pdf.add_page()

    # Добавляем шрифт DejaVuSans (поддерживает кириллицу)
    pdf.add_font('DejaVuSans', '', os.path.join('DejaVuSans.ttf'), uni=True)
    pdf.set_font('DejaVuSans', '', 8)

    # Добавляем заголовок
    pdf.cell(0, 10, f"ID поставки: {shipment_id}", ln=True, align='C')

    # Создаем таблицу
    col_widths = [20, 30, 40, 40, 30, 30]  # Ширина столбцов
    headers = ["ID заказа", "Ячейка", "Название", "Баркод", "Артикул", "Номер стикера"]

    # Заголовок таблицы
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1)
    pdf.ln()

    # Данные таблицы
    for order in data['orders']:
        pdf.cell(col_widths[0], 10, str(order['id']), border=1)
        pdf.cell(col_widths[1], 10, "null", border=1)
        pdf.cell(col_widths[2], 10, "Название из БД", border=1)
        pdf.cell(col_widths[3], 10, "Баркод", border=1)
        pdf.cell(col_widths[4], 10, order['article'], border=1)
        pdf.cell(col_widths[5], 10, "Номер стикера", border=1)
        pdf.ln()

    # Сохраняем PDF в файл
    pdf.output(os.path.join('pdfs','supplies', f'{shipment_id}.pdf'))








def create(base64_list, output_pdf="output.pdf", pst_stiker=None, insert_pdf_list=None):
    page_width = 58 * mm
    page_height = 40 * mm
    
    # Создаем временный PDF со стикерами
    temp_pdf = BytesIO()
    c = canvas.Canvas(temp_pdf, pagesize=(page_width, page_height))
    
    # Добавляем pst_stiker, если он передан
    if pst_stiker is not None:
        try:
            # Декодируем Base64 в PNG
            image_data = base64.b64decode(pst_stiker)
            image = ImageReader(BytesIO(image_data))
            
            # Рисуем PNG на странице
            c.drawImage(image, 0, 0, width=page_width, height=page_height)
        except Exception as e:
            print(f"Ошибка при обработке pst_stiker: {e}")
        c.showPage()
    
    # Добавляем стикеры из base64_list
    for base64_data in base64_list:
        try:
            # Декодируем Base64 в PNG
            image_data = base64.b64decode(base64_data)
            image = ImageReader(BytesIO(image_data))
            
            # Рисуем PNG на странице
            c.drawImage(image, 0, 0, width=page_width, height=page_height)
        except Exception as e:
            print(f"Ошибка при обработке base64_data: {e}")
        c.showPage()
    
    c.save()
    
    # Объединяем с insert_pdf_list
    writer = PdfWriter()
    temp_pdf.seek(0)
    input_pdf = PdfReader(temp_pdf)
    
    # Если insert_pdf_list не передан, используем пустой список
    if insert_pdf_list is None:
        insert_pdf_list = [None] * len(base64_list)
    elif len(insert_pdf_list) != len(base64_list):
        raise ValueError("Длина insert_pdf_list должна совпадать с base64_list")
    
    # Функция для создания страницы с ошибкой
    def create_error_page(message):
        packet = BytesIO()
        c_error = canvas.Canvas(packet, pagesize=(page_width, page_height))
        c_error.setFont("Helvetica", 8)  # Убедитесь, что шрифт поддерживается
        lines = message.split('\n')
        y = page_height - 10
        for line in lines:
            c_error.drawString(10, y, line)
            y -= 12
            if y < 10:
                break
        c_error.showPage()
        c_error.save()
        packet.seek(0)
        return PdfReader(packet).pages[0]
    
    # Добавляем страницы стикеров и вставок
    for i, page in enumerate(input_pdf.pages):
        writer.add_page(page)
        if i < len(insert_pdf_list):  # Проверка на выход за пределы списка
            insert_file = insert_pdf_list[i]
            
            if insert_file is not None:
                pdf_path = os.path.join("wb_gi", insert_file)
                if os.path.exists(pdf_path):
                    try:
                        insert_reader = PdfReader(pdf_path)
                        if len(insert_reader.pages) == 0:
                            raise ValueError("PDF пуст")
                        writer.add_page(insert_reader.pages[0])
                    except Exception as e:
                        error_page = create_error_page(f"Ошибка: {insert_file} ({str(e)})")
                        writer.add_page(error_page)
                else:
                    error_page = create_error_page(f"Файл {insert_file} не найден")
                    writer.add_page(error_page)
    
    # Сохраняем итоговый PDF
    with open(output_pdf, "wb") as out_file:
        writer.write(out_file)
    
    print(f"PDF создан: {output_pdf}")


# import PyPDF2
import re

def split_pdf_by_barcode(input_pdf_path):
    # Открываем исходный PDF-файл
    with open(input_pdf_path, 'rb') as file:
        reader = PdfReader(file)
        names = []
        # Обрабатываем каждую страницу
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            
            # Извлекаем текст из страницы
            text = page.extract_text()
            if not text:
                print(f"Страница {page_num + 1}: текст не найден. Пропуск.")
                continue
            
            # Ищем штрих-код (первая строка, содержащая только цифры)
            lines = text.split('\n')
            barcode = None
            for line in lines:
                line = line.strip()
                if re.match(r'^\d+$', line):  # Проверяем, что строка состоит только из цифр
                    barcode = line
                    break
            
            if not barcode:
                print(f"Страница {page_num + 1}: штрих-код не найден. Пропуск.")
                continue
            
            # Создаем новый PDF-файл для страницы
            writer = PdfWriter()
            writer.add_page(page)
            
            # Сохраняем файл
            output_filename = pdf_path = os.path.join("pdfs", f"{barcode}.pdf")
            with open(output_filename, 'wb') as output_file:
                writer.write(output_file)
            names.append(f"Страница {page_num + 1} сохранена как {output_filename}")
        
    return names

# Пример использования
# split_pdf_by_barcode("леопард.pdf")