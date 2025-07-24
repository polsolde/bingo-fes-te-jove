
import generate
import cairo
import time

start_time = int(time.time())

# W = (210 / 25.4) * 72
# H = (297 / 25.4) * 72
# surface = cairo.PDFSurface(f"output/cards_{start_time:d}.pdf", W, H)
# cx = cairo.Context(surface)
# pt_mm = 72 / 25.4
# cx.scale(pt_mm, pt_mm)
# cx.set_source_rgba(0.0, 0.0, 0.0, 1.0)
# cx.set_line_width(0.3)
# cx.set_line_cap(cairo.LINE_CAP_ROUND)
# label_face = cairo.ToyFontFace("Fira Mono Medium", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
# the_face = cairo.ToyFontFace("Fira Sans Book", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

# top_margin = 8.0
# left_margin = 3.0
# col_shift = 9.0
# row_shift = 10.0
# card_shift = 31.0
# bank_shift = 82.0

# page_number_x = 98
# page_number_y = 285

# # ought to compute font metrics to do these properly!
# deltax = -1.5
# deltay = -7

# label_sep = 1.0

# for page in range(2):
#     cx.set_font_face(the_face)
#     cx.set_font_size(4)
#     cx.move_to(page_number_x, page_number_y)
#     cx.show_text(f"Page {page+1:d}")
#     for bank in [0,1]:
#         cx.set_font_face(the_face)
#         cx.set_font_size(6)
#         foo = (1000 + (page * 2) + bank)
#         seed = [start_time, foo]
#         cards = generate.generate_cards(seed)
#         print(cards)
#         for card in range(6):
#             for row in range(3):
#                 for col in range(9):
#                     val = cards[card, row, col]
#                     if val > 0:
#                         x = left_margin + (bank * bank_shift) + (col * col_shift)
#                         y = top_margin + (card * card_shift) + (row * row_shift)
#                         cx.move_to(x, y)
#                         cx.show_text(f"{val:2d}")
#             for col in range(10):
#                 x = deltax + left_margin + (bank * bank_shift) + (col * col_shift)
#                 y0 = deltay + top_margin + (card * card_shift)
#                 y1 = y0 + (3 * row_shift)
#                 cx.move_to(x, y0)
#                 cx.line_to(x, y1)
#             for row in range(4):
#                 x0 = deltax + left_margin + (bank * bank_shift)
#                 x1 = x0 + (9 * col_shift)
#                 y = deltay + top_margin + (card * card_shift) + (row * row_shift)
#                 cx.move_to(x0, y)
#                 cx.line_to(x1, y)
#             cx.stroke()
#         # labelling
#         cx.set_font_face(label_face)
#         cx.set_font_size(2.5)
#         for card in range(6):
#             # label = f"{seed[0]:10d} {seed[1]:5d}  {(card+1):1d}"
#             x = deltax + left_margin + (bank * bank_shift)
#             y = deltay + top_margin + (card * card_shift) + (3 * row_shift)
#             cx.save()
#             cx.translate(x, y)
#             cx.rotate(-3.1415926535/2.0)
#             cx.move_to(0,-label_sep)
#             # cx.show_text(label)
#             cx.restore()

#     cx.show_page()


import random
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib import utils
from itertools import islice

def generate_random_table():
    return [[random.randint(1, 99) for _ in range(9)] for _ in range(3)]

def get_image(path, width, height):
    img = utils.ImageReader(path)
    img_width, img_height = img.getSize()
    aspect = img_height / float(img_width)
    return (width, width * aspect)

def draw_table(c, data, x, y, width, height, image_path):
    rows = len(data)
    cols = len(data[0])-2
    cell_width = width / cols
    cell_height = height / rows

    c.setFont("Helvetica-Bold", num_size)
    c.setLineWidth(1.2)  # Thicker lines

    for i, row in enumerate(data):
        for j, cell in enumerate(row):
            if cell != 0:
                text = str(cell)
                text_width = c.stringWidth(text, "Helvetica-Bold", num_size)
                text_x = x + j * cell_width + (cell_width - text_width) / 2
                text_y = y - (i + 1) * cell_height + (cell_height - 12) / 2
                c.drawString(text_x, text_y, text)
            else:
                img_width, img_height = get_image(image_path, cell_width - photo_margin, cell_height - photo_margin)
                c.drawImage(image_path, x + j * cell_width + (cell_width - img_width) / 2, 
                            y - (i + 1) * cell_height + (cell_height - img_height) / 2,
                            img_width, img_height)
            c.rect(x + j * cell_width, y - (i + 1) * cell_height, cell_width, cell_height)

def create_pdf(filename, image_path):
    
    c = canvas.Canvas(filename, pagesize=landscape(letter))
    width, height = landscape(letter)
    margin = 0.2 * cm
    table_width = (width - 35 * margin) / 2
    table_height = (height - 17 * margin) / num_rows
    
    margin_y = 1 * cm
    x_positions = [margin, width / 2 + margin / 2]
    y_positions = [height - margin_y - i * (table_height + margin_y) for i in range(num_rows)]

    for page in range(n_pages):
        # el generate_cards podria anar aqui JAJAJAJAJA (seria mes eficient)
        for i, y in enumerate(y_positions):
            for j, x in enumerate(x_positions):
                start_time = int(time.time()) + random.randint(1,99)
                table_data = generate.generate_cards(start_time)
                # Draw the "BINGO!" text above the table
                c.setFont("Helvetica-Bold", 16)
                text_width = c.stringWidth(text, "Helvetica-Bold", 16)
                c.drawString(x,  y + 5, "RONDA: " + str(ronda))  # Positioning above table
                c.drawString(x + text_width/2, y + 5, text)  # Positioning above table
                draw_table(c, table_data[i+j], x, y, table_width, table_height, image_path)
                
        c.showPage()

    c.save()

ronda = 9
n_rondes = 8
n_pages = 1500
text = "GRAN BINGO DE FES-TE JOVE"
photo_margin = 1
num_rows = 3
num_size = 24
image_path = "Logo_FJ_imatge-invert.jpg"  # Replace with your actual image file nam    
    
create_pdf("T:/bingo4/bingo_cards/final/ronda_"+str(ronda)+".pdf", image_path)
# table_data = generate.generate_cards(start_time)
# y_positions = [height - margin - i * (table_height + margin) for i in range(5)]
# draw_table(c, table_data[i+j], x, y, table_width, table_height)
# T:/bingo3 - copia\bingo_cards\Logo_FJ_imatge.jpg