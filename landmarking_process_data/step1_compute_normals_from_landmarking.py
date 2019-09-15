from os import *

from morphman.common.centerline_operations import *
from morphman.common.common import *

frenetTangentArrayName = 'FrenetTangent'


def find_normals_and_origins(file_path, knots, method="piccinelli"):
    """
    Based on landmarking points, compute the origin (landmarking points) + end point of ICA
    and find the normal vector at each point.

    Combining the origin and the normal at that point, we can define a plane
    which is used to clip the model into segments corresponding to the 4 (Bogunovic) or n (Piccinelli) segments
    """
    # Pathnames to particles
    if method == "piccinelli":
        particles_path = path.join(file_path, "model_landmark_piccinelli_vmtk.particles")
    if method == "bogunovic":
        particles_path = path.join(file_path, "model_landmark_bogunovic_spline_%s.particles" % knots)

    # Centerlines
    centerline_path = path.join(file_path, "model_ica.vtp")
    centerlines = read_polydata(centerline_path)

    # Get particle points as numpy array
    landmarks = np.loadtxt(particles_path)
    seen = set()

    if method == "piccinelli":
        def unique_generator(lst):
            for item in lst:
                tupled = tuple(item)
                if tupled not in seen:
                    seen.add(tupled)
                    yield item

        landmarks = list(unique_generator(landmarks))

        p_end = centerlines.GetPoint(centerlines.GetNumberOfPoints() - 1)
        origins = landmarks + [p_end]

    else:
        p1 = landmarks[2]
        p2 = landmarks[1]
        p3 = landmarks[0]
        p4 = landmarks[3]
        p_end = centerlines.GetPoint(centerlines.GetNumberOfPoints() - 1)
        origins = [p1, p2, p3, p4, p_end]

    # Find fernet tangent vector along centerline for each interface
    centerlines = vmtk_compute_geometric_features(centerlines, smooth=False)
    frenet_tangent_array = get_point_data_array(frenetTangentArrayName, centerlines, k=3)
    normals = []
    locator = get_vtk_point_locator(centerlines)
    for p in origins:
        tmp_id = locator.FindClosestPoint(p)
        normal = frenet_tangent_array[tmp_id]
        normals.append(normal)

    normals = np.asarray(normals)
    origins = np.asarray(origins)

    # Save points
    print("-- Saving normals and origin in %s" % (file_path + "/normals or origin_" + method))
    save_normals_and_origin(normals, origins, file_path, method)


def save_normals_and_origin(normals, origins, file_path, method):
    path_normal = path.join(file_path, "normals_%s.txt" % method)
    np.savetxt(path_normal, normals, delimiter=' ')
    path_origin = path.join(file_path, "origin_%s.txt" % method)
    np.savetxt(path_origin, origins, delimiter=' ')

    # Save particles for debugging
    path_origin_particles = path.join(file_path, "origin_%s.particles" % method)
    np.savetxt(path_origin_particles, origins, delimiter=' ')


def initiate():
    model_path = "morphman/models_80p"
    models = [folder for folder in sorted(listdir(model_path)) if folder[0] == "C"]
    methods = ["bogunovic", "piccinelli"]

    # TODO: Use this as knots in article
    nknots = [9, 10, 11, 9, 12, 10, 10, 9, 10, 8, 13, 10]

    for model, knots in zip(models, nknots):
        file_path = path.join(model_path, model, "surface")
        find_normals_and_origins(file_path, knots, method=methods[1])


if __name__ == "__main__":
    initiate()
