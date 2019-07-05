from argparse import ArgumentParser
import os
from main import run


def process():
    parser = ArgumentParser(description="Generate callibration images")
    parser.add_argument('--number', '-n', type=int, default=30,
                        help="number of images to generate")
    parser.add_argument('--os', '-o', type=str, default='mac',
                        help="operating system of the computer, either mac or linux (Windows users may use linux)")
    parser.add_argument('--background', '-b', type=str, default='../data/operating_theatre/',
                        help="relative address of folder where background images are located")
    parser.add_argument('--savefolder', '-s', type=str, default='../data/generated_images/batch_1/',
                        help="relative address of folder where generated images are stored")
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
        save_folder=arguments.savefolder)





if __name__ == "__main__":
    process()

