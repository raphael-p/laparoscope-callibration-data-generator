# data generation
This code generates training images for camera calibration. By default: a checker pattern
on a calibration board in a random angle and position, 
with an operating theatre image in the background. 

### Dependencies:
   -   scikit-surgeryvtk
    
### Instructions: 
- To generate a single image, run model_render.py
- To generate a batch of images, run main.py or run the command line app code/command.py 
(-h or --help for more information).
- To generate multiple batches, run the bash script mass_generate.sh. 
You should set your parameters before running.
- The pattern of the calibration board can be changed by replacing checkerboard-3mm.png
- The background images can be changed by modifying the contents of the operating_theatre
directory.

### Tips:
- It is highly recommended to compress images (see command line options).
- The bash script uses the command line program, so it us useful to get familiar with it
in order to get familiar with that first.




