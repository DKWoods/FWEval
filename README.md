# FWEval

**Faster Whisper Evaluation**
The FWEval program takes a file in *.WAV format and provides information about transcription speed and accuracy for different available models using the [faster_whisper](https://github.com/SYSTRAN/faster-whisper) python module.

## Evaluations

FWEval evaluates the Faster Whisper processing of a file **for all available models** by looking at both transcription speed and accuracy.   It has an option for comparing CPU and CUDA processing of the same files.  To assess accuracy, you must provide a *reference file* in the Output directory.  (See below.  FWEval can automatically create an initial reference file that you should manually correct if needed.) 

## GPUs and CUDA functionality

Faster Whisper can use a properly configured NVidia GPU to radically speed the automated transcription process.  FWEval is not able to determine if the necessary hardware is available or if the necessary software is properly installed, so it provides a checkbox for **GPU support**.  If you attempt to run FWEval with this checkbox checked on a computer that does not meet the necessary criteria, Faster Whisper will likely crash.

Faster Whisper does not support GPU functionality on Apple Silicon processors.  The *GPU support* is not offered when running on macOS.

## Detailed Instructions for Program Use

When you start the FWEval program, the **Program Settings** tab will be displayed.  Take the following steps:

1.  Browse to your **Models** directory.  This is the directory where Faster Whisper stores its model files, the directory you pass using the *download_root* parameter in your *faster_whisper.WhisperModel()* command.  FWEval will download the model files if needed, but why waste time and disk space if you already have a copy of these files?

2.  Un-check the **Transana Models Only** checkbox if it is checked.  If this box is checked, FWEval will use a subset of the Faster Whisper models, those supported by a program I write named *Transana*, rather than all available models.  Nobody but me is likely to need this functionality.

3.  Browse to select a **File** in *.WAV format.  This is the file that will be used for testing.  It should be at least 1 minute long, but the longer the file, the longer FWEval will take, so I recommend using a file no longer than about 4 or 5 minutes in length.

4.  If your computer uses Windows or Linux, has a CUDA-enabled (NVidia) Graphics Card or GPU, and has been properly configured with the necessary NVidia CUDA and CDNN libraries, you can check the **GPU supported** checkbox to compare CPU and GPU performance for Faster Whisper.  If you don't meet these criteria, make sure this box is ***NOT*** checked to avoid program crashes.

5.  Select the **Language** used in the data file.

6.  Browse to select an **Output** directory.  This is where you want FWEval to store all of the files it generates.  (See below.)

7.  As described above, FWEval requires a *reference* file, a text file containing the words that should be included in the transcript.  For the file *DataFile.wav*, the *reference* file should be named *DataFile_reference.txt* and should be stored in the Output directory.  If you do not have a reference file, you can create an initial one by pressing the **Create Reference** button.  

FWEval uses the Large-v2 model, which is the most accurate model but is among the slowest in my esperience, to create this reference file, so please be patient.  You should carefully check the accuracy of the reference file agaunst the original audio file and made corrections before proceeding.  

8.  When ready, press the **Process** button near the bottom of the form.

## Program Outputs

When you run FWEval, the program provides feedback in several ways.

### The Results Tab

The *Results Tab* provides user feedback during processing and shows the results of all tests completed.  It shows what model is being tested, and provides speed and accuracy results for each model.  The status bar at the bottom of the window provides (admittedly minimal) feedback about how far into the file each test has progressed during the automated transcription process.

When all tests have been completed, the Results tab provides a table summarizing the results of all tests.

## Output Files

FWEval creates a **text file** in the Output Directory for each Faster Whisper transcription it performs.  The output file name indicates the source file name, the device used (cpu vs. cuda), and the model used.  The file contains the transcription results for that test in plain text, with one line per sentence.  You can review these files individually to make sense of the summary information FWEval provides.  

### The Graph Tab

The **Graph Tab** presents speed and accuracy results graphically.  This summarizes Faster Whisper performance across models for your data file in an easily=interpretable way.

### The Quality Comparisons Tab

The **Quality Comparisons Tab** shows comparisons of each model's transcription text to the transcription text in the *reference file*.  This allows you to see the details of how a given model's transcription deviates from the (theoreticaly) perfectly-accurate reference file. 

### Saving Results

If you press the Save button after FWEval processing is compelete, FWEval will save 4 files in the *Output Directory*. Files are named systematically based on the data file name, which we will assume is *DataFile.wav* for this example.

- *DataFile_results.txt* is a copy of the text-based results presented on the **Results Tab**.  The file is UTF-8 encoded.

- *DataFile_graph.png* is a copy of the image on the **Graph Tab**.

- *DataFile_data.csv* is a comma-separated-values file of the data produced by FWEval.  This can be loaded into Excel, Google Sheets, or many qualitative software packages.  The file is UTF-8 encoded.

- *DataFile_comparison.html* is an HTML file containing a copy of the information on the **Quality Comparisons Tab**.  The file is UTF-8 encoded.  

## Setup

To use the FWEval code, after you've downloaded it, first run `python -m pip install -r requirements.txt` to install the python modules this code requires.  

This program uses wxPython, which might not install correctly from requirements on Linux.  For me, using Ubuntu 22.04, the following commands installed wxPython and some necessary libraries:

``pip install -v -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04 wxPython

sudo apt-get install git curl libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0``

Your mileage may vary, but Google can help.  

## Things I have found using this program

So far, I've learned a number of interesting things using this program.

I've learned that the NVidia GeForce GTX 1660 Ti video card in my Windows computer does not have enough memory for the Large, Large-v1, Large-v2, and Large-v3 models.  These models run 3 to 4 times *slower* using the GPU than they do using the CPU because my video card has only 6 GB of memory and these large models require more memory than that.  For these 4 models, I'm better off *not* using CUDA.  The GPU speeds the transcription process up a lot for all other models.  Further, a computer with a newer 8 GB NVidia graphics card did not show a similar performance degradation for these Large models.    

I've learned that M1 and M2 Macs produce transcription results that are identical with Windows computer in terms of transcription contents and accuracy.  However, they do so more slowly than Windows computers of roughly the same vintage.  Faster Whisper is not able to use the GPU on Apple processors at this time, to the best of my knowledge.

In fact, transcription results, in terms of actual transcripts, are identical across all computers I tested, both with and without CUDA support.  Processing speeds vary wildly, but the actual results were identical to the word, including errors and hallucinations.

I've learned that for the most part, the English-specific versions of Faster Whisper models are not really any better than the multi-lingual versions.  

I've learned that the Distil-Large-v2, Distil-Medium.en, and Distil-Small.en models are wildly inaccurate under most circumstances, even with high quality audio in English.  The Tiny model requires really high quality audio or it, too, is not acceptably accurate.

I've learned that the Distil-Large-v2 and Distil-Large-v3 models only work for English data, despite claiming to be multi-lingual.  That is, these models provide English transcripts even when given non-English data.

And using Transana rather than FWEval, I've learned that when you explicitly request an English translation of a non-English data file, the Large-v3-Turbo and the Turbo models do not perform a translation, but give you a native-language transcript that differs from the native-language transcript you get when you don't request an English translation.  I am not able to assess the differences between the two transcripts.

Please see the following blog posts for more detail of my findings:
[Accuracy](https://www.transana.com/blog/2025/04/25/faster-whisper-in-transana-5-30-accuracy-1-of-3/)
[Transcription Speed]https://www.transana.com/blog/2025/04/28/faster-whisper-in-transana-5-30-processing-speed-2-of-3/
[Accuracy and Processing Speed]https://www.transana.com/blog/2025/05/01/faster-whisper-in-transana-5-30-accuracy-and-processing-speed-3-of-3/

## To Do list

I want to make several improvements to FWEval, which I may or may not be able to find time for.

- Detect file length and provide better user feedback during processing of files using Faster Whisper.

- Add configuration data to save the Program Settings values from one session to the next.

- Add a "Translate to English" option, along with a *translation reference* file for comparison.

- Add a "Multiple Languages" option that mirrors Faster Whisper's Multiple Languages support.

- It might be nice to be able to select models individually for inclusion or exclusion from each data processing run.

I also have created a rough program that looks at the output files (particularly the *.csv files) from multiple data runs and aggregates this information into summary graphs.  I used this to compare results across different data files and different computers for the blog posts listed above.  But I'm not sure it's worth the effort to make this program usable by others.  Let me know if you're interested.   
