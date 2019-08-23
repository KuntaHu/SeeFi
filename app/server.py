import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

export_file_url = 'https://www.googleapis.com/drive/v3/files/1FZPFfL2Xw8rbLuNaC-whS5agGnOF7c0z?alt=media&key=AIzaSyAbegNxXGDquLKG_oVzOs5zTX0JRUmC7Vo'
export_file_name = 'export.pkl'

# classes = ['Burnt', 'unBurnt']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))

#############################

import base64
import matplotlib.pyplot as plt
from io import BytesIO

# import cv2
from PIL import Image
import numpy as np
import os
from numpy import asarray

def aray_to_base64(arr):
    plt.imshow(arr)
    buffer = BytesIO()
    plt.axis('off')
    plt.savefig(buffer, bbox_inches='tight')
    plot_data = buffer.getvalue()
    imb = base64.b64encode(plot_data)
    ims = imb.decode()
    imd = "data:image/png;base64,"+ims
    return imd

def resize_shape(image):
    width, height = image.size
    image.thumbnail((300,300))
    image = asarray(image)
    hg = image.shape[0]
    wd = image.shape[1]
    fixed_array = np.zeros([300,300, 3], dtype=np.uint8)
    fixed_array[0:hg, 0:wd] = image
    fixed_image = Image.fromarray(fixed_array)
    fixed_image.save("temp.png")
    fixed_image = open_image("temp.png") 
    return fixed_image, hg, wd, height, width

def return_ori(image, hg, wd, height, width):
    image_part = image[0:hg, 0:wd]
    
    image_part = Image.fromarray(image_part.astype('uint8'))
    image_part = image_part.resize((width, height))
    image_ori = asarray(image_part, dtype = "int64")
    return image_ori

def acc_fixed(input, targs):
    n = targs.shape[0]
    targs = targs.squeeze(1)
    targs = targs.view(n,-1)
    input = input.argmax(dim=1).view(n,-1)
    return (input==targs).float().mean()

def acc_thresh(input:Tensor, target:Tensor, thresh:float=0.5, sigmoid:bool=True)->Rank0Tensor:
#     "Compute accuracy when `y_pred` and `y_true` are the same size."
    
#     pdb.set_trace()
    if sigmoid: input = input.sigmoid()
    n = input.shape[0]
    input = input.argmax(dim=1).view(n,-1)
    target = target.view(n,-1)
    return ((input>thresh)==target.byte()).float().mean()

def dice(input:Tensor, targs:Tensor, iou:bool=False, eps:float=1e-8)->Rank0Tensor:
#     "Dice coefficient metric for binary target. If iou=True, returns iou metric, classic for segmentation problems."
    n = targs.shape[0]
    input = input.argmax(dim=1).view(n,-1)
    targs = targs.view(n,-1)
    intersect = (input * targs).sum(dim=1).float()
    union = (input+targs).sum(dim=1).float()
    if not iou: l = 2. * intersect / union
    else: l = intersect / (union-intersect+eps)
    l[union == 0.] = 1.
    return l.mean()

import pdb

def dice_loss(input, target):
#     pdb.set_trace()
    smooth = 1.
    input = input[:,1,None].sigmoid()
    iflat = input.contiguous().view(-1).float()
    tflat = target.view(-1).float()
    intersection = (iflat * tflat).sum()
    return (1 - ((2. * intersection + smooth) / ((iflat + tflat).sum() +smooth)))

def combo_loss(pred, targ):
    bce_loss = CrossEntropyFlat(axis=1)
    return bce_loss(pred,targ) + dice_loss(pred,targ)

class SegLabelListCustom(SegmentationLabelList):
    def open(self, fn): return open_mask(fn, div=True)

class SegItemListCustom(SegmentationItemList):
    _label_cls = SegLabelListCustom
    
###############################

async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = await (img_data['file'].read())
#     img = open_image(BytesIO(img_bytes))
    img = Image.open(BytesIO(img_bytes))
#     img = Image.open(img_data)   
    img, hg, wd, height, width = resize_shape(img)
    prediction = learn.predict(img)[1][0].numpy()
    prediction = return_ori(prediction, hg, wd, height, width)
    prediction_str = aray_to_base64(prediction)
    return JSONResponse({'result': prediction_str})
    ##### ======== change the way to show image ========= #######
#     prediction = learn.predict(img)[0] ## ImageSegement
#     fig, ax = plt.subplots(figsize = (10,10))
#     prediction.show(figsize = (10,10), alpha = 0.7, ax = ax)
#     return JSONResponse({'result': prediction)})
   

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
