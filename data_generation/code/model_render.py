import vtk
from imageio import imread
from vtk.util import colors
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel
import sksurgeryvtk.camera.vtk_camera_model as VTKCameraModel
import numpy as np
from sksurgeryvtk.camera.vtk_camera_model import compute_projection_matrix
from PySide2.QtWidgets import QApplication
import vtk
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow


def rotate_model(target):
    """
    void function, produces rotation matrix for random, normally distributed, small angles
    :param target: rotation matrix
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
    xtrans_std_dev = 20
    ytrans_std_dev = 5
    ztrans_std_dev = 20

    x_shift = np.random.normal(0, xtrans_std_dev)
    y_shift = np.random.normal(0, ytrans_std_dev)
    z_shift = np.random.normal(0, ztrans_std_dev)

    # x_shift = 0; y_shift = 0; z_shift = 0; <-- FOR DEBUGGING

    x_pos, y_pos, z_pos = centre
    extrinsic = np.array([[1, 0, 0, x_pos + x_shift],
                          [0, 1, 0, y_pos + y_shift],
                          [0, 0, 1, z_pos + z_shift],
                          [0, 0, 0, 1]])
    return extrinsic


if __name__ == "__main__":
    app = QApplication([])

    err_out = vtk.vtkFileOutputWindow()
    err_out.SetFileName('output/vtk.err.txt')
    vtk_std_err = vtk.vtkOutputWindow()
    vtk_std_err.SetInstance(err_out)

    factory = vtk.vtkGraphicsFactory()
    factory.SetOffScreenOnlyMode(False)
    factory.SetUseMesaClasses(False)

    # create foreground image (checkerboard)
    input_file = '../data/grid_manual.ply'
    model = VTKSurfaceModel(input_file, colors.white)
    model.set_texture('../data/checkerboard-3mm.png')

    # rotate model
    extrinsic = model.get_model_transform()
    rotate_model(extrinsic)
    model.set_model_transform(extrinsic)

    # load background image
    jpeg_reader = imread('../data/operating_theatre/op_th_1.jpg')

    # generate widget
    widget = VTKOverlayWindow(offscreen=False)
    # widget.resize(1920, 1080) <-- LINUX
    widget.resize(960, 540) # <-- MAC
    widget.interactor = None
    widget.SetInteractorStyle(widget.interactor)
    widget.add_vtk_actor(model.actor)
    widget.set_video_image(jpeg_reader)
    widget.show()

    camera = widget.get_foreground_camera()

    # generate and set intrinsic matrix
    cam_matrix = camera.GetModelViewTransformMatrix()
    projection_matrix = VTKCameraModel.compute_projection_matrix(1920, 1080,  # w, y
                                                                 1740.660258, 1744.276691,  # fx, fy,
                                                                 913.206542, 449.961440,  # cx, cy,
                                                                 0.1, 1000,  # near, far
                                                                 1  # aspect ratio
                                                                 )
    VTKCameraModel.set_projection_matrix(camera, projection_matrix)

    # translate camera position
    cam_centre = np.array([-cam_matrix.GetElement(0, 3),
                           -cam_matrix.GetElement(1, 3),
                           cam_matrix.GetElement(2, 3)])
    cam_extrinsic = shift_camera(cam_centre)
    widget.set_camera_pose(cam_extrinsic)

    # save image
    screenshot_filename = '../data/images/gen_img_test.png'
    widget.save_scene_to_file(screenshot_filename)

    app.exec_()


