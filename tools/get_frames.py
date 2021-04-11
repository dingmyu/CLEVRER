# Author: Mingyu Ding
# Time: 14/1/2021 9:50 PM
# Copyright 2019. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import glob
import os
import random

data_root = '/mnt/lustre/dingmingyu/2021/data/clerver/train/'
video_list = glob.glob(data_root + '*/*.mp4')

for index, item in enumerate(video_list):
    video_index = int(item.split('/')[-1].split('.')[0].split('_')[-1])
    os.makedirs(f'/mnt/lustrenew/dingmingyu/data_t1/CLERVRER/video_frames/sim_{video_index:05d}', exist_ok=True)
    os.system(f'ffmpeg -i {item} -vf fps=25 /mnt/lustrenew/dingmingyu/data_t1/CLERVRER/video_frames/sim_{video_index:05d}/frame_%05d.png')
    print(index, video_index)

