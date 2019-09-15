from os import *

import cv2
import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc

rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
rc('text', usetex=True)
matplotlib.rcParams['text.usetex'] = True


def step1_set_title(images, save_path, method):
    cases = [name.split("_")[0].split("/")[1] for name in images]

    for i, case in enumerate(cases):
        img = mpimg.imread(images[i])

        plt.title(r"%s" % method.capitalize(), fontsize=15)
        plt.axis('off')
        plt.imshow(img)

        save_location = save_path + "/with-title/%s_landmark_%s_t.png" % (case, method)
        plt.savefig(save_location, dpi=500, bbox_inches='tight')


def step2_combine_landmarking_imges(images1, images2, save_path):
    # STEP 1: Combine Case images
    cases = [name.split("_")[0].split("/")[2] for name in images1]
    print(cases)

    for i, case in enumerate(cases):
        img1 = cv2.imread(images1[i])
        img2 = cv2.imread(images2[i])
        vis = np.concatenate((img1, img2), axis=1)

        save_location = "img/combined/%s_landmarked.jpg" % case
        print("Saving combined images to: %s" % save_location)
        cv2.imwrite(save_location, vis)


def step3_make_grid_image(images):
    cases = [name.split("_")[0].split("/")[-1] for name in images]
    for k in range(2):
        n = 0
        for i in range(6 * k, 6 * (1 + k)):
            plt.subplot(321 + n)
            img = mpimg.imread(images[i])
            plt.title(r"%s" % cases[i], fontsize=5)
            plt.imshow(img)
            plt.axis('off')
            n += 1

        plt.subplots_adjust(left=0.5, bottom=None, right=None, top=None, wspace=None, hspace=None)
        plt.plot()

        save_location = "img/landmark_images/combined_%s.png" % (k + 1)
        plt.savefig(save_location, bbox_inches='tight', dpi=500)
        plt.clf()


def main():
    step = 3

    # Read and find files
    if step == 1:
        model_path = "img"
        images = listdir(model_path)
        bogunovic_images = sorted(
            [model_path + "/" + img for img in images if img.split("_")[-1].split(".")[0] == "bogunovic"])
        piccinelli_images = sorted(
            [model_path + "/" + img for img in images if img.split("_")[-1].split(".")[0] == "piccinelli"])
        step1_set_title(bogunovic_images, model_path, "bogunovic")
        step1_set_title(piccinelli_images, model_path, "piccinelli")

    if step == 2:
        model_path = "img/with-title"
        images = listdir(model_path)
        bogunovic_images = sorted(
            [model_path + "/" + img for img in images if img.split("_")[2] == "bogunovic"])
        piccinelli_images = sorted(
            [model_path + "/" + img for img in images if img.split("_")[2] == "piccinelli"])
        step2_combine_landmarking_imges(bogunovic_images, piccinelli_images, model_path)

    if step == 3:
        images = ["img/combined/" + img for img in sorted(listdir("img/combined"))]
        step3_make_grid_image(images)


if __name__ == '__main__':
    main()
