from argparse import ArgumentParser
import os
from main import run


def process():
    parser = ArgumentParser(description="Generate calibration images")
    parser.add_argument('--number', '-n', type=int, default=30,
                        help="number of images to generate, "
                             "default: 30")
    parser.add_argument('--os', '-o', type=str, default='mac',
                        help="operating system of the computer: mac or linux, "
                             "default: mac")
    parser.add_argument('--background', '-b', type=str, default='../data/operating_theatre/',
                        help="relative address of folder where background images are located, "
                             "default: ../data/operating_theatre/")
    parser.add_argument('--savefolder', '-s', type=str, default='../data/generated_images/batch_1/',
                        help="relative address of folder where generated images are stored, "
                             "default: ../data/generated_images/batch_1/")
    parser.add_argument('--compress', '-c', action='store_true',
                        help="boolean, compresses images - this is very slow but greatly reduces storage, "
                             "default: False")
    arguments = parser.parse_args()

    if not os.path.isdir(arguments.savefolder):
        raise TypeError("Generated data storage directory '" + arguments.savefolder
                        + "' is not a valid directory. Please define a valid location. "
                        + "See help: -h or --help")
    if not os.path.isdir(arguments.background):
        raise TypeError("Background images directory '" + arguments.background
                        + "' is not a valid directory. Please define a valid location. "
                        + "See help: -h or --help")

    run(n_images=arguments.number, system=arguments.os, background_folder=arguments.background,
        save_folder=arguments.savefolder, compression=arguments.compress)


if __name__ == "__main__":
    process()

