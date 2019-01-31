import time
import asyncio
import io
from datetime import datetime

from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from PIL import Image, ImageDraw
import uvicorn

from garbage.calendar import Pickup, get_next_pickup

app = Starlette()


def generate_image(pickup: Pickup) -> Image:
    image = Image.new(mode='L', size=(200, 200), color=255)
    trash_image = Image.open('garbage/data/trash-w.png')
    image.paste(trash_image, (50, 30))
    draw = ImageDraw.Draw(image)
    locale_time = datetime.isoformat(datetime.now()).split('.')[0]
    draw.text((10,10), locale_time, fill=0)
    draw.text((10, 160), ', '.join(pickup.garbage_types), fill=0)
    draw.text((10, 170), pickup.date.humanize(locale='nl'), fill=0)
    return image


@app.route('/')
async def homepage(request):
    return JSONResponse({'hello': 'world'})


@app.route('/200x200.{ext}')
async def image(request) -> Response:
    ext = request.path_params['ext']
    loop = asyncio.get_running_loop()
    pickup = await get_next_pickup()
    print(pickup)
    image = await loop.run_in_executor(None, generate_image, pickup)
    fp = io.BytesIO()
    format = Image.registered_extensions()[f'.{ext}']
    image.save(fp, format)
    return Response(fp.getvalue(), media_type='image/bmp')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
