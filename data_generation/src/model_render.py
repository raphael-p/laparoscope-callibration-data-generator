from vtk.util import colors
import numpy as np
import vtk
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow
from PySide2.QtWidgets import QApplication
from vtk.util.numpy_support import vtk_to_numpy
from cv2 import flip, imwrite, cvtColor, COLOR_RGB2BGR

from os import walk


def move_model(target):
    """
    updates rotation matrix to perform random, normally distributed, small angle rotation in 3D
    :param target: rotation matrix to be updated
    :return: rotational part of extrinsic matrix of model (calibration board)
    """
    # random rotation angles
    rot_dev = np.pi/20
    theta = np.random.normal(0, rot_dev)
    phi = np.random.normal(0, rot_dev)
    psi = np.random.normal(0, rot_dev)

    # random translation distances
    x_dev = 20
    y_dev = 11.2
    z_dev = 10
    x_shift = np.random.normal(0, x_dev)
    y_shift = np.random.normal(0, y_dev)
    z_shift = np.random.normal(0, z_dev)

    # rotate
    target.SetElement(0, 0, np.cos(psi) * np.cos(theta))
    target.SetElement(0, 1, np.sin(psi) * np.cos(theta))
    target.SetElement(0, 2, -np.sin(theta))
    target.SetElement(1, 0, -np.sin(psi) * np.cos(phi) + np.cos(psi) * np.sin(theta) * np.cos(phi))
    target.SetElement(1, 1, np.cos(psi) * np.cos(phi) + np.sin(psi) * np.sin(theta) * np.sin(phi))
    target.SetElement(1, 2, np.cos(theta) * np.sin(phi))
    target.SetElement(2, 0, np.sin(psi) * np.sin(phi) + np.cos(psi) * np.sin(theta) * np.cos(phi))
    target.SetElement(2, 1, -np.cos(psi) * np.sin(phi) + np.sin(psi) * np.sin(theta) * np.cos(phi))
    target.SetElement(2, 2, np.cos(theta) * np.cos(phi))

    # translate
    x_pos = target.GetElement(0, 3) + x_shift
    y_pos = target.GetElement(1, 3) + y_shift
    z_pos = target.GetElement(2, 3) + z_shift
    target.SetElement(0, 3, x_pos)
    target.SetElement(1, 3, y_pos)
    target.SetElement(2, 3, z_pos)
    return [x_shift, y_shift, z_shift]


def render(background_image_location='../data/operating_theatre/1.or-efficiency-orepp-partnership-program.jpg',
           save_file='../data/generated_images/gen_img_test.png',
           width=1920, height=1080, fx=1740.660258, fy=1744.276691, cx=913.206542, cy=449.961440,
           os='mac', show_widget=True, compress=False):
    """
    uses vtk to render and save an image of a calibration board on a background in a random pose and position
    :param background_image_location: STR relative address of folder where background images are stored
    :param save_file: STR name and location of savefil
    :param width: INT width of image
    :param height: INT height of image
    :param fx: FLOAT focal length along x, in pixels
    :param fy: FLOAT focal length along y, in pixels
    :param cx: FLOAT x-coordinate of optical center or principal point, in pixels
    :param cy: FLOAT y-coordinate of optical center or principal point, in pixels
    :param os: STR operating system of machine, 'mac' or 'linux'
    :param show_widget: BOOL shows generated image
    :param compress: BOOl compresses save file
    :return: numpy array, extrinsic matrix of the calibration object
    """
    try:
        app = QApplication([])
    except RuntimeError:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

    # create foreground image (checkerboard)
    input_file = '../data/grid_board.ply'
    model = VTKSurfaceModel(input_file, colors.white)
    model.set_texture('../data/checkerboard-3mm.png')

    # create background image (OR)
    try:
        input_file = '../data/grid_background.ply'
        model_bckg = VTKSurfaceModel(input_file, colors.white)
        model_bckg.set_texture(background_image_location)
    except ValueError:
        return

    # generate widget and disable interactor
    widget = VTKOverlayWindow(offscreen=False)
    widget.interactor = None
    widget.SetInteractorStyle(widget.interactor)
    widget.add_vtk_actor(model_bckg.actor, layer=1)
    widget.add_vtk_actor(model.actor, layer=1)
    background_image = np.zeros((1080, 1920, 3))

    # generate and set intrinsic matrix
    intrinsic = np.array([[fx, 0, cx],
                          [0, fy, cy],
                          [0, 0, 1]])
    widget.set_camera_matrix(intrinsic)

    # scale
    cam = widget.get_foreground_camera()
    transform = vtk.vtkTransform()
    transform.Scale(4, 4, 1)
    cam.SetModelTransformMatrix(transform.GetMatrix())

    # center background
    extrinsic_bckg = model_bckg.get_model_transform()
    extrinsic_bckg.SetElement(0, 3, -105)
    extrinsic_bckg.SetElement(1, 3, -69)
    extrinsic_bckg.SetElement(2, 3, -30)

    # center board
    extrinsic_board = model.get_model_transform()
    extrinsic_board.SetElement(0, 3, 19)
    extrinsic_board.SetElement(1, 3, -4.3)

    # rotate and translate
    extrinsic = model.get_model_transform()
    print(type(extrinsic))
    translation = move_model(extrinsic)

    widget.set_video_image(background_image)
    widget.show()

    # resize widget
    if os == 'linux':
        widget.resize(width, height)
    elif os == 'mac':
        widget.resize(width//2, height//2)
    else:
        raise ValueError("'"+str(os)+"' is an invalid OS, choose either 'mac' or 'linux'")

    # test: check widget size
    render_window = widget.GetRenderWindow()
    dimensions = render_window.GetSize()
    window_width = dimensions[0]
    window_height = dimensions[1]
    if width != window_width or height != window_height:
        raise AssertionError("Incorrect window dimensions: try changing os argument")

    # save image: retrieve and convert to numpy array
    widget.vtk_win_to_img_filter = vtk.vtkWindowToImageFilter()
    widget.vtk_win_to_img_filter.SetInput(widget.GetRenderWindow())
    widget.vtk_win_to_img_filter.SetInputBufferTypeToRGB()
    widget.vtk_win_to_img_filter.Update()
    widget.vtk_image = widget.vtk_win_to_img_filter.GetOutput()
    width, height, _ = widget.vtk_image.GetDimensions()
    widget.vtk_array = widget.vtk_image.GetPointData().GetScalars()
    number_of_components = widget.vtk_array.GetNumberOfComponents()
    np_array = vtk_to_numpy(widget.vtk_array).reshape(height,
                                                      width,
                                                      number_of_components)
    widget.output = flip(np_array, flipCode=0)
    widget.convert_scene_to_numpy_array()
    widget.output = cvtColor(widget.output, COLOR_RGB2BGR)
    imwrite(save_file, widget.output)

    # assemble the calibration object's extrinsic matrix
    mod_ext = model.get_model_transform()
    model_extrinsic = [mod_ext.GetElement(0, 0), mod_ext.GetElement(0, 1), mod_ext.GetElement(0, 2),
                       mod_ext.GetElement(1, 0), mod_ext.GetElement(1, 1), mod_ext.GetElement(1, 2),
                       mod_ext.GetElement(2, 0), mod_ext.GetElement(2, 1), mod_ext.GetElement(2, 2),
                       translation[0], translation[1], translation[2]]
    if compress:
        import os
        os.system('./pngquant --ext .png -f --quality=70 --speed 11 -- '+str(save_file))

    if show_widget:
        app.exec_()
    else:
        widget.close()
    return model_extrinsic


if __name__ == "__main__":
    # retrieve background files
    background_folder = '../data/operating_theatre/'
    (_, _, backgrounds) = next(walk(background_folder))
    for idx in range(len(backgrounds)):
        render(compress=True, background_image_location=background_folder+backgrounds[idx])
