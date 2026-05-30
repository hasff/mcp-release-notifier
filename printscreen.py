import fitz

with fitz.open("assets/part_09/release_444_20260529_173135.pdf") as doc:
    page = doc[0]
    
    zoom = 2.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    pix.save("screenshot_pdf.jpg")