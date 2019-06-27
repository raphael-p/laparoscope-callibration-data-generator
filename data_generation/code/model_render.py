import vtk
from imageio import imread
from vtk.util import colors
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel
import sksurgeryvtk.camera.vtk_camera_model as Cam
import numpy as np
from sksurgeryvtk.camera.vtk_camera_model import compute_projection_matrix
from PySide2.QtWidgets import QApplication
import vtk
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow

def rotate(target):
    """
    void function, produces rotation matrix for random, normally distributed, small angles
    :param target: rotation matrix
    """
    rot_dev = np.pi/6
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

def shift_and_rotate(centre):
    rotation_std_dev = np.pi / 7
    #rotation_std_dev = np.pi / 20
    #x_angle = np.random.normal(0, rotation_std_dev)
    #y_angle = np.random.normal(0, rotation_std_dev)
    noise = np.random.normal(0, 0.1)
    x_pos, y_pos, z_pos = centre


    translation_std_dev = 2
    x_shift = np.random.normal(0, 20)
    y_shift = np.random.normal(0, 5)
    z_shift = np.random.normal(0, 20)

    x_angle = np.arctan(y_shift / z_pos)

    y_angle = np.arctan(x_shift / z_pos)

    z_angle = np.random.normal(0, rotation_std_dev)

    pitch = np.array([[1, 0, 0],
                      [0, np.cos(x_angle), -np.sin(x_angle)],
                      [0, np.sin(x_angle), np.cos(x_angle)]])
    yaw = np.array([[np.cos(y_angle), 0, np.sin(y_angle)],
                    [0, 1, 0],
                    [-np.sin(y_angle), 0, np.cos(y_angle)]])
    roll = np.array([[np.cos(z_angle), -np.sin(z_angle), 0],
                     [np.sin(z_angle), np.cos(z_angle), 0],
                     [0, 0, 1]])

    #rotation = pitch.dot(yaw.dot(roll))
    #rotation = pitch
    rotation = np.identity(3)
    #rotation = roll.dot(yaw.dot(pitch))
    #rotation = yaw

    extrinsic = np.array([[rotation[0][0], rotation[0][1], rotation[0][2], centre[0] + x_shift],
                          [rotation[1][0], rotation[1][1], rotation[1][2], centre[1] + y_shift],
                          [rotation[2][0], rotation[2][1], rotation[2][2], centre[2] + z_shift],
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

    extrinsic = model.get_model_transform()
    rotate(extrinsic)
    model.set_model_transform(extrinsic)

    # load background image
    jpeg_reader = imread('../data/test_image.jpg')


    # generate widget
    widget = VTKOverlayWindow(offscreen=False, clipping_range=(0.001, 100))
    widget.resize(1920, 1080)
    widget.interactor = None
    widget.SetInteractorStyle(widget.interactor)
    widget.add_vtk_actor(model.actor)
    widget.set_video_image(jpeg_reader)
    widget.show()

    camera = widget.get_foreground_camera()

    cam_matrix = camera.GetModelViewTransformMatrix()
    matrix = Cam.compute_projection_matrix(1920, 1080,  # w, y
                                           1740.660258, 1744.276691,  # fx, fy,
                                           913.206542, 449.961440,  # cx, cy,
                                           0.1, 1000,  # near, far
                                           1  # aspect ratio
                                           )
    Cam.set_projection_matrix(camera, matrix)
    cam_centre = np.array([-cam_matrix.GetElement(0,3),
                           -cam_matrix.GetElement(1,3),
                           cam_matrix.GetElement(2,3)])

    cam_extrinsic = shift_and_rotate(cam_centre)
    widget.set_camera_pose(cam_extrinsic)

    app.exec_()
    # screenshot_filename = 'tests/data/images/set_texture_test.png'
    # widget.save_scene_to_file(screenshot_filename)

