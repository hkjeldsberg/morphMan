import xml.etree.ElementTree as ET
from os import *

from paraview.simple import *

paraview.simple._DisableFirstRenderCameraReset()


def plot_landmarks(color, name, file_path, mode="3D", modelname="C000X"):
    """
    Combine clips in clipX_ALGORITHM.vtp
    and color them accordingly,
    combind and then save figure
    """
    model_path = path.join('/Users/henrikkjeldsberg/Projects/landmarking/morphMan/', file_path, name)

    c1vtp = XMLPolyDataReader(FileName=[model_path])
    c1vtp.PointArrayStatus = ['Normals', 'RegionId']

    renderView1 = GetActiveViewOrCreate('RenderView')

    c1vtpDisplay = Show(c1vtp, renderView1)

    # Show 2D or 3D projection of the model
    if mode == "2D":
        renderView1.InteractionMode = '2D'
    elif mode == "3D":
        renderView1.InteractionMode = '3D'

    renderView1.OrientationAxesVisibility = 0
    renderView1.Background = [1.0, 1.0, 1.0]

    # current camera placement for renderView1
    # Adjust camera settings
    renderView1.ViewSize = [1080, 1578]

    camera_path = path.join('/Users/henrikkjeldsberg/Projects/landmarking/morphMan/camera', modelname + ".pvcc")
    set_camera_position(renderView1, camera_path)

    c1vtpDisplay.DiffuseColor = color
    ColorBy(c1vtpDisplay, ('POINTS', ''))
    return renderView1


def set_camera_position(renderView1, filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    # FIXME: Not sure if index is sorted, and thus the need for filling with 0
    position = [0, 0, 0]
    view_up = [0, 0, 0]
    focal = [0, 0, 0]
    rotation = [0, 0, 0]

    for child in root[0]:
        if child.attrib['name'] == 'CameraFocalPoint':
            for subChild in child:
                focal[int(subChild.attrib["index"])] = float(subChild.attrib['value'])
        if child.attrib['name'] == 'CenterOfRotation':
            for subChild in child:
                rotation[int(subChild.attrib["index"])] = float(subChild.attrib['value'])
        if child.attrib['name'] == 'CameraPosition':
            for subChild in child:
                position[int(subChild.attrib["index"])] = float(subChild.attrib['value'])
        if child.attrib['name'] == 'CameraViewUp':
            for subChild in child:
                view_up[int(subChild.attrib['index'])] = float(subChild.attrib['value'])
        if child.attrib["name"] == "CameraParallelScale":
            for subChild in child:
                parallel_scale = float(subChild.attrib['value'])
        if child.attrib["name"] == "RotationFactor":
            for subChild in child:
                rotation_factor = float(subChild.attrib['value'])
        if child.attrib["name"] == "CameraViewAngle":
            for subChild in child:
                view_angle = float(subChild.attrib['value'])
        if child.attrib["name"] == "CameraParallelProjection":
            for subChild in child:
                if "value" in subChild.attrib.keys():
                    parallel_projection = bool(subChild.attrib['value'])

    renderView1.CenterOfRotation = rotation
    renderView1.CameraPosition = position
    renderView1.CameraFocalPoint = focal
    renderView1.CameraViewUp = view_up
    renderView1.CameraParallelScale = parallel_scale
    renderView1.CameraParallelProjection = 0  # parallel_projection
    renderView1.CameraViewAngle = view_angle
    renderView1.RotationFactor = rotation_factor
    renderView1.CameraViewUp = view_up

    return renderView1


def main():
    # Define colors
    blue = [0.2, 0.1, 1.0]
    green = [0.2, 0.8, 0.3]
    red = [1, 0, 0]
    yellow = [1, 0.9, 0]
    white = [1, 1, 1]
    colors = [white, yellow, red, green, blue, white]

    model_path = "morphman/models_80p"
    methods = ["bogunovic", "piccinelli"]

    # Read and find files
    models = [folder for folder in sorted(listdir(model_path)) if folder[0] == "C"]
    for method in methods:
        for model in models:
            # Read clips in
            file_path = path.join(model_path, model, "surface")
            model_clips = sorted([clip for clip in listdir(file_path) if
                                  "clip" in clip.split("_")[0] and clip.split("_")[1].split(".")[0] == method])

            if method == "piccinelli":
                N = len(model_clips)
                colors_picc = [blue, green, red, yellow]
                color_board = [colors_picc[i % 4] for i in range(N - 2)]
                color_board.reverse()
                colors = [white] + color_board + [white]

            # Plot clips
            for i, name in enumerate(model_clips):
                renderView1 = plot_landmarks(colors[i], name, file_path, modelname=model)
            print("Saving SS to %s" % ("img/" + model + "_landmark_" + method + ".png"))
            SaveScreenshot('img/%s_landmark_%s.png' % (model, method), magnification=2, quality=100, view=renderView1)
            Delete(renderView1)


if __name__ == '__main__':
    main()
