# PyStegano
This program is an implementation of steganography that support information hiding in **image**, **video**, and **audio**. The method used is LSB (for all media type) and also BPCS (only for image). This program is developed using Python 3.8 with full GUI using PyQt.

## Installation
In order to properly run this program easily, you first need to have `ffmpeg` in your system. This library can be installed in various way. 

For Linux, you can simply open up terminal and type in:
```
sudo apt install ffmpeg
```
While for Windows, installation is a bit tricky so please refer to <a href=https://ffmpeg.org/download.html>this</a> official documentation.

Next, after you have set up the ffmpeg library, you also need to have Python installed. To make it easier to install all the dependencies, we recommend you install `Miniconda` on your system. Please refer to <a href=https://docs.conda.io/projects/conda/en/latest/user-guide/install/>this</a> documentation.

After installing `Miniconda`, go to the project root directory, open up terminal and type in:
```
conda env create -f env.yml
```
Wait until the process complete, then type:
```
conda activate stegano
```
If all goes well, you should see the word `stegano` in bracket leftmost terminal line like this:
```
(stegano) <yoursystem>@<yourusername>:~$ 
```

## Run
After you successfully follow the installation process, you can simply run the program by going to the project root directory and type in:
```
python main.py
```
A program will be spawned and ready to use.

## Build
If you want to have only single binary file which you can run independently, you need to build it. 

In Linux you can do it by going to the root directory and type:
```
./build.sh
```
In Windows, you can simply type:
```
pyinstaller --onefile stegano.spec
```
Wait until the build process is complete, then the built binary will be located in the `dist` folder.

