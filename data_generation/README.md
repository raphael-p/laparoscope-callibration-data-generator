# data generation
This code generates training images for camera calibration. 
By default: a checkerboard pattern
on a calibration board in a random angle and position, 
with an operating theatre image in the background. 

A label containing the intrinsic matrix of the camera and the
3x3 rotation matrix of the calibration board is produced for
each image, and stored into a csv file with the same name as
the image batch.

### Dependencies:
See `REQUIREMENTS.txt` for a list of dependencies.
    
### Instructions: 
- To generate a single image, run
```bash
python model_render.py
```
The parameters can be set by modifying the script directly. 
However, this is not ideal and I recommend using the command
line app instead (see next bullet point).
- To generate a batch of images, run 
```bash
python main.py 
```
Again, it is preferable to use the command line app to set the 
parameters.

To run the command line app, enter the following bash command, 
```bash
python command.py 
```
with flags -h or --help for information on the parameters.
- To generate multiple batches, run the bash script,
 ```bash
 bash mass_generate.sh
 ```
You should set your parameters by modifying the script before running.
- The pattern of the calibration board can be changed by replacing checkerboard-3mm.png
- The background images can be changed by modifying the contents of the operating_theatre
directory.

### Tips:
- It is highly recommended to compress images (see command 
line options).
- The bash script uses the command line program, so it us 
useful to get familiar with that first.
- This may vary by machine, but I found that above a certain 
threshold of generated images in a batch, the program performs
poorly. That is why it is necessary to generate in several
batches, and using a bash script to do so.

### Example output:
![](data/generated_images/gen_img_test.png?raw=true)




