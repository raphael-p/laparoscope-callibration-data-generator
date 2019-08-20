from ..src.model_render import *
from pytest import raises
from sys import platform
import vtk


def test_move_model_modifies_matrix_elements():
    ext_matrix = vtk.vtkMatrix4x4()
    ext_matrix.Identity()
    trans_vector = move_model(ext_matrix)
    has_changed = True
    for i in range(2):
        if trans_vector[i] == 0:
            has_changed = False
        for j in range(3):
            element_ij = ext_matrix.GetElement(i, j)
            if i == j:
                if element_ij == 1:
                    has_changed = False
            else:
                if element_ij == 0:
                    has_changed = False
    assert has_changed


def test_render_wrong_os():
    if platform == 'linux' or platform == 'linux2' or platform == 'win32':
        wrong_os = 'mac'
    elif platform == 'darwin':
        wrong_os = 'linux'
    with raises(AssertionError) as exception:
        render(os=wrong_os, show_widget=False)


def test_render_invalid_os():
    invalid_os = 'windows'
    with raises(ValueError) as exception:
        render(os=invalid_os, show_widget=False)