from vtk.util import colors
import numpy as np
import vtk
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow
from PySide2.QtWidgets import QApplication
from vtk.util.numpy_support import vtk_to_numpy
from cv2 import imread, flip, imwrite, cvtColor, COLOR_RGB2BGR, IMWRITE_PNG_COMPRESSION


def rotate_model(target):
    """
    void function, updates rotation matrix to perform random, normally distributed, small angle rotation in 3D
    :param target: rotation matrix to be updated
    :return: rotational part of extrinsic matrix of model (calibration board)
    """
    rot_dev = np.pi/7
    x_rot = np.random.normal(0, rot_dev)
    y_rot = np.random.normal(0, rot_dev)
    z_rot = np.random.normal(0, rot_dev)

    Z = vtk.vtkMatrix4x4()
    Z.DeepCopy(target)
    Z.SetElement(0, 0, np.cos(z_rot))
    Z.SetElement(0, 1, -np.sin(z_rot))
    Z.SetElement(1, 0, np.sin(z_rot))
    Z.SetElement(1, 1, np.cos(z_rot))

    Y = vtk.vtkMatrix4x4()
    Y.DeepCopy(target)
    Y.SetElement(0, 0, np.cos(y_rot))
    Y.SetElement(0, 2, np.sin(y_rot))
    Y.SetElement(2, 0, -np.sin(y_rot))
    Y.SetElement(2, 2, np.cos(y_rot))

    X = vtk.vtkMatrix4x4()
    X.DeepCopy(target)
    X.SetElement(2, 2, np.cos(x_rot))
    X.SetElement(1, 2, -np.sin(x_rot))
    X.SetElement(2, 1, np.sin(x_rot))
    X.SetElement(1, 1, np.cos(x_rot))

    YZ = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Multiply4x4(Y, Z, YZ)
    vtk.vtkMatrix4x4.Multiply4x4(X, YZ, target)
    return


def shift_camera(centre):
    """
    translates camera in 3D
    :param centre: numpy array containing 3D coordinates of camera position when image is centred
    :return: translated extrinsic matrix of camera
    """
    xtrans_std_dev = 15
    ytrans_std_dev = 5
    ztrans_std_dev = 20

    x_shift = np.random.normal(0, xtrans_std_dev)
    y_shift = np.random.normal(0, ytrans_std_dev)
    z_shift = np.random.normal(0, ztrans_std_dev)

    x_pos, y_pos, z_pos = centre
    extrinsic = np.array([[1, 0, 0, x_pos + x_shift],
                          [0, 1, 0, y_pos + y_shift],
                          [0, 0, 1, z_pos + z_shift],
                          [0, 0, 0, 1]])
    return extrinsic


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
    :return: void
    """
    try:
        app = QApplication([])
    except RuntimeError:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

    # create foreground image (checkerboard)
    input_file = '../data/grid_manual.ply'
    model = VTKSurfaceModel(input_file, colors.white)
    model.set_texture('../data/checkerboard-3mm.png')

    # rotate model
    extrinsic = model.get_model_transform()
    rotate_model(extrinsic)
    model.set_model_transform(extrinsic)

    # load background image
    background_image = imread(background_image_location)

    # generate widget and disable interactor
    widget = VTKOverlayWindow(offscreen=False)
    widget.interactor = None
    widget.SetInteractorStyle(widget.interactor)
    widget.add_vtk_actor(model.actor)
    try:
        widget.set_video_image(background_image)
    except TypeError:
        return
    widget.show()

    # resize widget
    if os == 'linux':
        widget.resize(width, height)
    elif os == 'mac':
        widget.resize(width//2, height//2)
    else:
        raise ValueError("'"+str(os)+"' is an invalid OS, choose either 'mac' or 'linux'")

    # generate and set intrinsic matrix
    intrinsic = np.array([[fx, 0, cx],
                          [0, fy, cy],
                          [0, 0, 1]])
    widget.set_camera_matrix(intrinsic)

    # translate camera position
    camera = widget.get_foreground_camera()
    cam_matrix = camera.GetModelViewTransformMatrix()
    cam_centre = np.array([-cam_matrix.GetElement(0, 3),
                           -cam_matrix.GetElement(1, 3),
                           cam_matrix.GetElement(2, 3)])
    cam_extrinsic = shift_camera(cam_centre)
    widget.set_camera_pose(cam_extrinsic)

    # test: check widget size
    render_window = widget.GetRenderWindow()
    dimensions = render_window.GetSize()
    window_width = dimensions[0]
    window_height = dimensions[1]
    if width != window_width or height != window_height:
        raise AssertionError("Incorrect window dimensions: try changing os argument")

    # save image
    # widget.save_scene_to_file(save_file)
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

    mod_ext = model.get_model_transform()
    model_extrinsic = [mod_ext.GetElement(0,0), mod_ext.GetElement(0,1), mod_ext.GetElement(0,2),
                       mod_ext.GetElement(1,0), mod_ext.GetElement(1,1), mod_ext.GetElement(1,2),
                       mod_ext.GetElement(2,0), mod_ext.GetElement(2,1), mod_ext.GetElement(2,2)]

    if compress:
        import os
        os.system('./pngquant --ext .png -f --quality=70 --speed 11 -- '+str(save_file))

    if show_widget:
        app.exec_()
    else:
        widget.close()
    return model_extrinsic


if __name__ == "__main__":
    render(compress=True)




