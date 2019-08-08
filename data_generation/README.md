# data generation
This code generates training images for camera calibration. By default: a checker pattern
on a calibration board in a random angle and position, 
with an operating theatre image in the background. 

### Dependencies:
See `REQUIREMENTS.txt` for a list of dependencies.
    
### Instructions: 
- To generate a single image, 
```bash
run model_render.py
```
- To generate a batch of images, run 
```bash
python main.py 
```
or run the command line app, 
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
- It is highly recommended to compress images (see command line options).
- The bash script uses the command line program, so it us useful to get familiar with that first.




