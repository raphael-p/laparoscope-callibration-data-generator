from PIL import Image
from vtk.util import colors
import numpy as np
import vtk
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow
from PySide2.QtWidgets import QApplication


def rotate_model(target):
    """
    void function, updates rotation matrix to perform random, normally distributed, small angle rotation in 3D
    :param target: rotation matrix to be updated
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


def render(background_image='../data/operating_theatre/1.or-efficiency-orepp-partnership-program.jpg',
           screenshot_filename='../data/generated_images/gen_img_test.png',
           width=1920, height=1080, fx=1740.660258, fy=1744.276691, cx=913.206542, cy=449.961440,
           os='mac', show_widget=True):

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
    #jpeg_reader = imread(background_image)
    jpeg_reader = np.asarray(Image.open(background_image))
    channel = np.swapaxes(jpeg_reader, 0, 2)
    bck_img = np.asarray([channel[2], channel[1], channel[0]])
    bck_img = np.swapaxes(bck_img, 0, 2)
    bck_img = np.asarray(bck_img, order='C')


    # generate widget and disable interactor
    widget = VTKOverlayWindow(offscreen=False)
    widget.add_vtk_actor(model.actor)
    widget.set_video_image(bck_img)
    widget.interactor = None
    widget.SetInteractorStyle(widget.interactor)

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

    # resize widget
    if os == 'linux':
        widget.resize(width, height)
    elif os == 'mac':
        pass
        widget.resize(width//2, height//2)
    else:
        raise ValueError("'"+str(os)+"' is an invalid OS, choose either 'mac' or 'linux'")

    # save image
    widget.save_scene_to_file(screenshot_filename)

    if show_widget:
        widget.show()
        app.exec_()
    return


if __name__ == "__main__":
    #render(screenshot_filename='../data/images/gen_img_test_default.png')
    #render(cx=962, cy=540, screenshot_filename='../data/generated_images/gen_img_test_changefocus.png')
    render()




