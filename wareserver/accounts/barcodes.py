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

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fpdf import FPDF

def generate_pdf(data, shipment_id : str):
    # Создаем объект PDF
    pdf = FPDF()
    pdf.add_page()

    # Добавляем шрифт DejaVuSans (поддерживает кириллицу)
    pdf.add_font('DejaVuSans', '', os.path.join('DejaVuSans.ttf'), uni=True)
    pdf.add_font('DejaVuSans', 'B', os.path.join('DejaVuSans-Bold.ttf'), uni=True)  # Добавляем жирный шрифт
    pdf.set_font('DejaVuSans', '', 8)

    # Добавляем заголовок
    sh_id, nam = shipment_id.split('#')
    pdf.cell(0, 10, f"ID поставки: {sh_id+' '+nam}", ln=True, align='C')

    # Создаем таблицу
    col_widths = [20, 40, 45, 50, 40]  # Ширина столбцов
    headers = ["ID заказа", "Ячейка", "Название", "Баркод", "Номер стикера"]
    row_height = 10  # Высота строки (меньше стандартной 10)

    # Заголовок таблицы
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1)
    pdf.ln()

    # Функция для разбиения текста на строки
    def split_text(text, max_width):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if pdf.get_string_width(test_line) < max_width - 2:  # -2 для небольшого запаса
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines or ['']

    # Данные таблицы
    for order in data:
        # Получаем все строки для каждой колонки
        id_lines = split_text(str(order.get('id', '')), col_widths[0])
        cell_lines = split_text(str(order.get('cell', '')), col_widths[1])
        name_lines = split_text(str(order.get('name', '')), col_widths[2])
        barc_lines = split_text(str(order.get('barc', '')), col_widths[3])
        stik_lines = split_text(str(order.get('stik', '')), col_widths[4])
        
        # Определяем максимальное количество строк для этого ряда
        max_lines = max(len(id_lines), len(cell_lines), len(name_lines), 
                        len(barc_lines), len(stik_lines))
        
        # Печатаем каждую строку ряда
        for i in range(max_lines):
            # ID заказа
            pdf.cell(col_widths[0], row_height, 
                     id_lines[i] if i < len(id_lines) else '', border=1)
            # Ячейка
            pdf.cell(col_widths[1], row_height, 
                     cell_lines[i] if i < len(cell_lines) else '', border=1)
            # Название
            pdf.cell(col_widths[2], row_height, 
                     name_lines[i] if i < len(name_lines) else '', border=1)
            # Баркод
            pdf.cell(col_widths[3], row_height, 
                     barc_lines[i] if i < len(barc_lines) else '', border=1)
            
            # Номер стикера с особым форматированием последних 4 символов
            stik_text = stik_lines[i] if i < len(stik_lines) else ''
            if len(stik_text) >= 4:
                # Первая часть текста (все кроме последних 4 символов)
                normal_part = stik_text[:-4]
                # Последние 4 символа
                bold_part = stik_text[-4:]
                
                # Печатаем нормальную часть
                pdf.cell(col_widths[4], row_height, normal_part, border=1)
                # Сохраняем текущую позицию X
                x = pdf.get_x()
                y = pdf.get_y()
                
                # Печатаем жирную часть с увеличенным шрифтом
                pdf.set_font('DejaVuSans', 'B', 12)  # Жирный и больше размер
                pdf.text(x*0.875, y + row_height/1.6, bold_part)  # Подбираем позиционирование
                
                # Возвращаем обычный шрифт
                pdf.set_font('DejaVuSans', '', 8)
            else:
                pdf.cell(col_widths[4], row_height, stik_text, border=1)
            
            pdf.ln()

    # Сохраняем PDF в файл
    pdf.output(os.path.join('pdfs','supplies', f'{sh_id}.pdf'))
    return sh_id


def create(base64_list, output_pdf="output.pdf", pst_stiker=None, insert_pdf_list=None):
    writer = PdfWriter()
    def create_error_page(message):
        packet = BytesIO()
        c_error = canvas.Canvas(packet, pagesize=(page_width, page_height))
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    
    # Устанавливаем зарегистрированный шрифт
        c_error.setFont("DejaVuSans", 8)
        # c_error.setFont("DejaVuSans", os.path.join('DejaVuSans.ttf') , 8)  # Убедитесь, что шрифт поддерживается
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
    
    if len(base64_list) == 0:
        
        writer.add_page(create_error_page('Не удалось получить стикеры'))
        with open(output_pdf, "wb") as out_file:
            writer.write(out_file)
        return 1
        
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
    
    temp_pdf.seek(0)
    input_pdf = PdfReader(temp_pdf)
    
    # Если insert_pdf_list не передан, используем пустой список
    if insert_pdf_list is None:
        insert_pdf_list = [None] * len(base64_list)
    elif len(insert_pdf_list) != len(base64_list):
        raise ValueError("Длина insert_pdf_list должна совпадать с base64_list")

    # Добавляем страницы стикеров и вставок
    for i, page in enumerate(input_pdf.pages):
        writer.add_page(page)
        if i < len(insert_pdf_list):  # Проверка на выход за пределы списка
            insert_file = insert_pdf_list[i] + '.pdf'
            
            if insert_file is not None:
                pdf_path = os.path.join('pdfs',insert_file)
                print('ищу pdf:',pdf_path)
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
            output_filename  = os.path.join("pdfs", f"{barcode}.pdf")
            with open(output_filename, 'wb') as output_file:
                writer.write(output_file)
            names.append(f"Страница {page_num + 1} сохранена как {output_filename}")
        
    return names

# Пример использования
# split_pdf_by_barcode("леопард.pdf")