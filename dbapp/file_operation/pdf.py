import io
import re
from datetime import datetime

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTChar, LTTextBoxHorizontal, LTTextLineHorizontal
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser

def PDF_extractor(file_obj):
    try:
        result = None
        data = io.BytesIO(file_obj.read())
        parser = PDFParser(data)
        document = PDFDocument(parser)
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        texts = ['']
        font_sizes = []
        text_fontsize = []
        before_font_size = 0
        for page in PDFPage.get_pages(data):
            interpreter.process_page(page)
            layout = device.get_result()

            for element in layout:
                if isinstance(element, LTTextBoxHorizontal):
                    for text_line in element:
                        if isinstance(text_line, LTTextLineHorizontal):
                            line_text = text_line.get_text().strip()
                            font_size = 0
                            for char in text_line:
                                if isinstance(char, LTChar):
                                    font_size = max(font_size, abs(char.matrix[0]))

                            if font_size == before_font_size or texts[-1] == '':
                                texts[-1] += line_text
                            else:
                                text_fontsize.append((before_font_size, texts[-1]))
                                font_sizes.append(before_font_size)
                                texts.append(line_text)

                            before_font_size = font_size

        match = re.search(r'\d{14}', str(document.info[0]['CreationDate'].decode()))
        pubyear = datetime.strptime(match.group(), "%Y%m%d%H%M%S")

        if pubyear.month < 4:
            pubyear_jp = int(f"{pubyear.year - 1}")
        else:
            pubyear_jp = int(f"{pubyear.year}")

        content = "\n".join(texts)

        result = {"content": content, "pubyear": pubyear_jp}

    except Exception as e:
        print(e)

    finally:
        data.close()
        parser.close()
        device.close()

    return result

if __name__ == "__main__":
    from argparse import ArgumentParser

    arg = ArgumentParser()
    
    arg.add_argument('-f', '--file', type=str, default=None)
    arg.add_argument('-t', '--type', type=str, default="all")

    args = arg.parse_args()
    with open(args.file, 'rb') as data:
        pdf = PDF_extractor(data)
    
    if args.type == "all":
        print(pdf)