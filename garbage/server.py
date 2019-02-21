import time
import asyncio
import io
from datetime import datetime
from typing import List

from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from PIL import Image, ImageDraw, ImageFont
import uvicorn

from garbage.calendar import Pickup, get_next_pickup
from garbage.config import FONT_FILE, SHOW_TIMESTAMP


app = Starlette()


MAIN_FONT = ImageFont.truetype(FONT_FILE, 20)
SMALL_FONT = ImageFont.truetype(FONT_FILE, 14)


def get_garbage_image_path(garbage_types: List[str]) -> str:
    if garbage_types == ["Restafval"]:
        return 'garbage/data/trash-w.png'
    return 'garbage/data/recycle-w.png'


def generate_image(pickup: Pickup) -> Image:
    image = Image.new(mode='L', size=(200, 200), color=255)
    trash_image = Image.open(get_garbage_image_path(pickup.garbage_types))
    image.paste(trash_image, (50, 24))
    draw = ImageDraw.Draw(image)
    draw.fontmode = "0"
    garbage_text = ', '.join(pickup.garbage_types)
    human_date = pickup.date.humanize(locale='nl')
    if SHOW_TIMESTAMP:
        locale_time = datetime.isoformat(datetime.now()).split('.')[0]
        w, h = draw.textsize(locale_time, font=SMALL_FONT)
        draw.text((100 - w / 2,10), locale_time, fill=0, font=SMALL_FONT)
    w, h = draw.textsize(garbage_text, font=MAIN_FONT)
    draw.text((100 - w / 2, 130), garbage_text, fill=0, font=MAIN_FONT)
    w, h = draw.textsize(human_date, font=SMALL_FONT)
    draw.text((100 - w / 2, 160), human_date, fill=0, font=SMALL_FONT)
    return image


@app.route('/')
async def homepage(request):
    return JSONResponse({'hello': 'world'})


@app.route('/200x200.{ext}')
async def image(request) -> Response:
    ext = request.path_params['ext']
    loop = asyncio.get_running_loop()
    pickup = await get_next_pickup()
    image = await loop.run_in_executor(None, generate_image, pickup)
    fp = io.BytesIO()
    format = Image.registered_extensions()[f'.{ext}']
    image.save(fp, format)
    return Response(fp.getvalue(), media_type='image/bmp')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
