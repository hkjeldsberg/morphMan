from os import listdir

from morphman.common import *


def clip_single_model(file_path, method="piccinelli"):
    """
    Read in normals and origins and clips
    the models at each interface. With n landmarks, the model
    is divided into n + 2 segments.
    """
    model_path = path.join('/Users/henrikkjeldsberg/Projects/landmarking/morphMan/', file_path, 'model.vtp')
    normals = np.loadtxt(path.join(file_path, "normals_%s.txt" % method))
    origins = np.loadtxt(path.join(file_path, "origin_%s.txt" % method))
    surface = read_polydata(model_path)

    N = len(normals)
    print("Number of landmarks: %s" % (N - 1))
    print("Saving clipped models in: %s" % (file_path + "/clipX_ALGORITHM.vtp"))
    if method == 'piccinelli':
        for i in range(N):
            if i == 0:
                # Segment at inlet
                clip_model(surface, origins, normals, i, True, file_path, "clip%s_%s" % (i, method))
            elif i == (N - 1):
                # Segment after end of ICA
                clip_model(surface, origins, normals, i, False, file_path, "clip%s_%s" % (i + 1, method))
            else:
                tmp_clip = clip_model(surface, origins, normals, i - 1, False, file_path, None)
                clip_model(tmp_clip, origins, normals, i, True, file_path, "clip%s_%s" % (i, method))

                if i == (N - 2):  # End segment of ICA
                    tmp_ica = clip_model(surface, origins, normals, i, False, file_path, None)
                    clip_model(tmp_ica, origins, normals, i + 1, True, file_path, "clip%s_%s" % (i + 1, method))

    if method == 'bogunovic':
        # Start of model
        clip_model(surface, origins, normals, 0, True, file_path, "clip0_%s" % method)
        # First segment
        c2_tmp = clip_model(surface, origins, normals, 0, False, file_path, None)
        clip_model(c2_tmp, origins, normals, 1, True, file_path, "clip1_%s" % method)
        # Second segment
        c3_tmp = clip_model(surface, origins, normals, 1, False, file_path, None)
        clip_model(c3_tmp, origins, normals, 2, True, file_path, "clip2_%s" % method)
        # Third segment
        c4_tmp = clip_model(surface, origins, normals, 2, False, file_path, None)
        clip_model(c4_tmp, origins, normals, 3, True, file_path, "clip3_%s" % method)
        # Fourth segment
        c5_tmp = clip_model(surface, origins, normals, 3, False, file_path, None)
        clip_model(c5_tmp, origins, normals, 4, True, file_path, "clip4_%s" % method)
        # Remaining model after ICA end
        clip_model(surface, origins, normals, N - 1, False, file_path, "clip5_%s" % method)


def clip_model(surface, origins, normals, k, flip, file_path, name):
    center = origins[k]
    normal = normals[k]

    plane = vtk_plane(center, normal)

    # Clip data (naivly)
    if flip:
        clipped, surface = vtk_clip_polydata(surface, plane)
    else:
        surface, clipped = vtk_clip_polydata(surface, plane)
    if flip:
        write_polydata(clipped, "clipped_" + str(k) + "_.vtp")
        write_polydata(surface, "surface_" + str(k) + "_.vtp")
    # Reattach data which should not have been clipped
    surface = attach_clipped_regions_to_surface(surface, clipped, center)

    # Check if surface is connected - else get part closest to center
    connectivity = vtk_compute_connectivity(surface, mode="All")

    if connectivity.GetNumberOfPoints() == 0:
        print("No connectivity")
        return surface

    region_ids = get_point_data_array("RegionId", connectivity)

    # 1 is in region_id if more than one surface
    if 1 in region_ids:
        min_dist = 1e9
        region_id = -1

        for i in range(int(region_ids.max() + 1)):
            surface_part = vtk_compute_threshold(connectivity, "RegionId", lower=i - 0.1, upper=i + 0.1, source=0)
            locator = get_vtk_point_locator(surface_part)
            region_point = surface_part.GetPoint(locator.FindClosestPoint(center))
            tmp_dist = get_distance(region_point, center)
            if tmp_dist < min_dist:
                min_dist = tmp_dist
                region_id = i

        # Extract correct surface
        surface_final = vtk_compute_threshold(connectivity, "RegionId", lower=region_id - 0.1, upper=region_id + 0.1,
                                              source=0)
        surface_final = vtk_clean_polydata(surface_final)
        surface_final = vtk_triangulate_surface(surface_final)
    else:
        surface_final = surface

    if name is not None:
        save_path = path.join('/Users/henrikkjeldsberg/Projects/landmarking/morphMan/', file_path, '%s.vtp' % name)
        write_polydata(surface_final, save_path)

    return surface_final


def main():
    model_path = "morphman/models_80p"
    methods = ["bogunovic", "piccinelli"]
    models = [folder for folder in sorted(listdir(model_path)) if folder[0] == "C"]
    for model in models:
        file_path = path.join(model_path, model, "surface")
        clip_single_model(file_path, method=methods[1])


if __name__ == '__main__':
    main()
