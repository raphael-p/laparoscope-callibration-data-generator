from model_render import render
from os import walk
import numpy as np
from tqdm import tqdm

if __name__ == "__main__":
    # retrieve background files
    background_folder = '../data/operating_theatre/'
    (_, _, backgrounds) = next(walk(background_folder))
    background_file = backgrounds[0]

    # set iteration parameters
    image_count = 10
    change_background_frequency = 2

    # initialise intrinsic parameters
    f_x = 1740.660258
    f_y = 1744.276691
    c_x = 913.206542
    c_y = 449.961440

    for iter_count in tqdm(range(image_count)):
        # select background
        if iter_count % change_background_frequency == 0:
            rand_int = int(np.random.random() * len(backgrounds))
            background_file = background_folder+backgrounds[rand_int]

        # randomise intrinsic parameters
        f_x = np.random.normal(1740.660258, 174)
        f_y = np.random.normal(1744.276691, 174)
        c_x = np.random.normal(913.206542, 91)
        c_y = np.random.normal(449.961440, 45)

        # generate image
        filename = '../data/images/batch_1/gen_img_1_'+str(iter_count)+'.png'
        render(fx=f_x, fy=f_y, cx=c_x, cy=c_y,
               background_image=background_file, screenshot_filename=filename, show_widget=False, os="mac")
