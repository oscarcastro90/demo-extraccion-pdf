import logging
from io import BytesIO
from typing import Any

import pdfplumber
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from utils.segpal import build_segpal


#class to filter out /healthz from logging
class EndpointFilter(logging.Filter):
    def __init__(
        self,
        path: str,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._path = path

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self._path) == -1

uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(EndpointFilter(path="/healthz"))

app = FastAPI()


@app.get('/', status_code=200)
async def root():
    return {'api': 'extracción de pdf'}


@app.get('/healthz', status_code=200)
async def healthz():
    """
    check if API is up
    """
    return Response(status_code=200)


@app.get('/api/')
async def root_api():
    return {'api': 'extracción de pdf'}


@app.post('/api/segpal')
def get_segpal(
    pdf: UploadFile = File(
        ..., description='archivo pdf'
        ),
    page: int = Query(
        alias='pag', gt=0, description='número de página a extraer.'
        ),
    pdf_pass: str = Query(
        default="", description='contraseña del pdf.'
        ),
    img_height: int | None = Query(
        default=None, alias='img_alto', gt=0, le=10_000,
        description='alto de la imagen para calcular la coordenadas.'
        ),
    img_width: int | None = Query(
        default=None, alias='img_ancho', gt=0, le=10_000,
        description='ancho de la imagen para calcular la coordenadas.'
        ),
):
    # both, img height and width must be none or integer
    if (img_height is not None and img_width is None) or (img_height is None and img_width is not None):
        raise HTTPException(status_code=422, detail='No se recibió valor de alto ó ancho de imagen.')

    file_content = pdf.file.read()
    pdf_content = pdfplumber.open(BytesIO(file_content), password=pdf_pass)

    if page > len(pdf_content.pages):
        raise HTTPException(status_code=422, detail=f'Página {page} es mayor al total de páginas.')

    pdf_page = pdf_content.pages[page-1]

    # TODO: Check if this validation is still needed
    # if img_height is not None:
    #     page_aspect_ratio = pdf_page.height / pdf_page.width
    #     image_aspect_ratio = img_height / img_width
    #     if abs(image_aspect_ratio - page_aspect_ratio) >= 0.5:
    #         uvicorn_logger.warning('Page and image aspect ratio discrepancy.')
    #         img_height = round(page_aspect_ratio * img_width)

    segpal = build_segpal(
        words=pdf_page.extract_words(x_tolerance=2),
        page_dims=(pdf_page.height, pdf_page.width),
        img_dims=(img_height, img_width)
    )

    pdf_content.close()
    pdf.file.close()

    return segpal


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='localhost', port=8088, log_config='api/logging.conf')
