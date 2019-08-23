# !usr/bin/env python
# -*- coding:utf-8 -*-
# author: hui
# datetime: 2019-08-19 13:26
# project: fastai-v3-master

import base64
import cv2


def array_to_json(arr):
    retval, buffer = cv2.imencode('.jpeg', arr)
    pic_str = base64.b64encode(buffer)
    pic_str = pic_str.decode()

    return 'data:image/jpeg;base64,' + pic_str


if __name__ == '__main__':
    import numpy as np
    arr = np.array([[[1, 1, 1], [2, 2, 2], [1, 1, 1]]])
    p = array_to_json(arr)