from model_render import render
from os import walk
import numpy as np
from tqdm import tqdm


def run(n_images=30, system='mac',
        background_folder='../data/operating_theatre/', save_folder='../data/generated_images/batch_0/',
        compression=False, im_width=1920, im_height=1080):
    """
    runs model_render.py multiple times, used to generate a batch of images
    :param n_images: INT number of images to generate
    :param system: STR operating system of machine
    :param background_folder: STR relative address of folder where background images are stored
    :param save_folder: STR relative address of folder to save generated images in
    :param compression: BOOL compresses image using pngquant
    :param im_width: INT width of image
    :param im_height: INT height of image
    :return: void
    """
    # retrieve background files
    (_, _, backgrounds) = next(walk(background_folder))
    background_file = backgrounds[0]

    # set iteration parameters
    change_background_frequency = 1
    change_intrinsic_frequency = 10

    # initialise intrinsic parameters
    f_x = 1740.660258
    f_y = 1744.276691
    c_x = 913.206542
    c_y = 449.961440

    for iter_count in tqdm(range(n_images)):
        # select background
        if iter_count % change_background_frequency == 0:
            rand_int = int(np.random.random() * len(backgrounds))
            background_file = background_folder+backgrounds[rand_int]

        # randomise intrinsic parameters
        if iter_count % change_intrinsic_frequency == 0:
            f_x = np.random.normal(1740.660258, 174)
            f_y = np.random.normal(1744.276691, 174)
            c_x = np.random.normal(913.206542, 91)
            c_y = np.random.normal(449.961440, 45)

        # generate image
        dir_name = list(filter(None, save_folder.split('/')))[-1]
        filename = save_folder+'genim_'+dir_name+'_'+str(iter_count+1)+'.png'
        render(fx=f_x, fy=f_y, cx=c_x, cy=c_y,
               background_image_location=background_file, save_file=filename,
               show_widget=False, os=system, compress=compression,
               width=im_width, height=im_height)


if __name__ == "__main__":
    run()
