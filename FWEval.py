# Copyright (C) 2025 Spurgeon Woods LLC
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

"""This program evaluates the speed and accuracy of Faster Whisper models. """

__author__ = 'David K. Woods <dwoods@transana.com>'

# import Python modules
import codecs
import difflib
import os, sys, traceback
import time
# import Faster Whisper
import faster_whisper
# import wxPython
import wx
import wx.html
# import graphing module
import ChartGraphic

VERSION = '0.1.0'

# Define i18n function
_ = wx.GetTranslation

def TimeMsToStr(TimeVal):
    """ Converts Time in Milliseconds to a formatted string """
    # Convert from milliseconds to seconds
    seconds = int(TimeVal) // 1000
    # Determine how many whole hours there are in this number of seconds
    hours = seconds // (60 * 60)
    # Remove the hours from the total number of seconds
    seconds = seconds % (60 * 60)
    # Determine the number of minutes in the remaining seconds
    minutes = seconds // 60
    # Remove the minutes from the seconds, and round to the nearest second.
    seconds = round(seconds % 60)
    # Initialize a String
    TempStr = ''
    # Convert to string
    if hours > 0:
        TempStr = '%s:%02d:%02d' % (hours, minutes, seconds)
    else:
        TempStr = '%s:%02d' % (minutes, seconds)
    # Return the string representation to the calling function
    return TempStr

class SettingsPanel(wx.Panel):
    """ Create a Panel for program settings """
    def __init__(self, parent, processCmd):
        """ Initialize the Program Settings panel.  The processCmd parameter takes a function from the parent
            that should be called if the "Process" button is pressed. """
        # Remember the parent and the processCmd
        self.parent = parent
        self.processCmd = processCmd

        # Create default entries for the program settings
        drive = os.path.split(__file__)[0][:2] + os.sep
        modelPath = drive
        mediaLibraryPath = os.path.join(drive, 'Video')
        outputPath = os.path.join(drive, 'Video', 'Comparisons')

        # Create the Panel
        wx.Panel.__init__(self, parent=parent)
        # Define the main Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a fixed-width font for the TextCtrl
        font1 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        # Create a TextCtrl
        self.txt = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE)
        self.txt.SetFont(font1)
        # Add the TextCtrl to the Sizer
        sizer.Add(self.txt, 1, wx.EXPAND | wx.ALL, 0)
        # Populate the TextCtrl with instructions
        self.txt.AppendText('Instructions:\n\n')
        self.txt.AppendText('1.  Set the "Models" directory below to your "faster_whisper_models" directory.\n\n')
        self.txt.AppendText('2.  Select a WAV file for testing under "File".  It should probably be 10 minutes or less in length.\n\n')
        self.txt.AppendText('3.  Select an "Output" directory.  It should contain a reference file for your selected file.  ')
        self.txt.AppendText('For example, if your test file is "Test.wav", your reference file should be "Test_reference.txt".  ')
        self.txt.AppendText('If you have not created a manual reference file, you can press the "Create Reference" button to ')
        self.txt.AppendText('create a "Large-v2" transcription file, which you can then edit manually.\n\n')
        self.txt.AppendText('4.  Press the Process button.')
        # Add a spacer
        sizer.Add((1, 11), 0)

        # Create a Row Sizer
        hSizer3 = wx.BoxSizer(wx.HORIZONTAL)
        # Add a label to the Row Sizer
        lbl = wx.StaticText(self, wx.ID_ANY, "Models:")
        hSizer3.Add(lbl, 1, wx.LEFT | wx.TOP, 10)
        # Add a control for the Model Path
        self.modelPathCtrl = wx.DirPickerCtrl(self, wx.ID_ANY, path=modelPath,
                                              message='Select Model Path')
        hSizer3.Add(self.modelPathCtrl, 8, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Add a checkbox for Transana Models Only
        self.transanaModels = wx.CheckBox(self, wx.ID_ANY, "Transana Models Only")
        self.transanaModels.SetValue(True)
        hSizer3.Add(self.transanaModels, 2, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        # Add the row sizer to the main sizer
        sizer.Add(hSizer3, 0, wx.EXPAND)

        # Create a Row Sizer
        hSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        # Add a label to the Row Sizer
        lbl = wx.StaticText(self, wx.ID_ANY, "File:")
        hSizer1.Add(lbl, 1, wx.LEFT | wx.TOP, 10)
        # Add a control for the Test File
        self.filenameCtrl = wx.FilePickerCtrl(self, wx.ID_ANY, path=os.path.join(mediaLibraryPath, 'Demo.wav'),
                                              message='Select an audio file', wildcard="WAV files (*.wav)|*.wav")
        self.filenameCtrl.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnFileSelected)
        hSizer1.Add(self.filenameCtrl, 8, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Add a checkbox for GPU Support
        self.includeGPU = wx.CheckBox(self, wx.ID_ANY, "GPU supported")
        self.includeGPU.SetValue(True)
        hSizer1.Add(self.includeGPU, 2, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        # Add the row sizer to the main sizer
        sizer.Add(hSizer1, 0, wx.EXPAND)

        # Create a Row Sizer
        hSizer5 = wx.BoxSizer(wx.HORIZONTAL)
        # Add a label to the Row Sizer
        lbl = wx.StaticText(self, wx.ID_ANY, "Language:")
        hSizer5.Add(lbl, 1, wx.LEFT | wx.TOP, 10)
        # Add a control for selecting transcription language
        self.language = wx.Choice(self, wx.ID_ANY, choices = list(LanguageLookup.keys()))
        self.language.SetStringSelection('English')
        hSizer5.Add(self.language, 2, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        # Add an expandable spacer for horizontal positioning
        hSizer5.Add((1, 1), 8, wx.EXPAND)
        # Add the row sizer to the main sizer
        sizer.Add(hSizer5, 0, wx.EXPAND)

        # Create a Row Sizer
        hSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        # Add a label to the Row Sizer
        lbl = wx.StaticText(self, wx.ID_ANY, "Output:")
        hSizer2.Add(lbl, 1, wx.LEFT | wx.TOP, 10)
        # Add a control for selecting the output path
        self.filePathCtrl = wx.DirPickerCtrl(self, wx.ID_ANY, path=mediaLibraryPath,
                                              message='Select Output Library')
        self.filePathCtrl.Bind(wx.EVT_DIRPICKER_CHANGED, self.OnFileSelected)
        hSizer2.Add(self.filePathCtrl, 8, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Add a button for creating the Reference File
        self.btnCreateReference = wx.Button(self, wx.ID_ANY, "Create Reference")
        self.btnCreateReference.Bind(wx.EVT_BUTTON, self.OnCreateReference)
        hSizer2.Add(self.btnCreateReference, 2, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Determine the Reference File Name
        referenceFilename = self.GetReferenceFileName()
        # If the Reference File ixists, disable the Reference File Button
        if os.path.exists(referenceFilename):
            self.btnCreateReference.Enable(False)
        else:
            self.btnCreateReference.Enable(True)
        # Add the row sizer to the main sizer
        sizer.Add(hSizer2, 0, wx.EXPAND)
        # Add an expandable spacer for vertical positioning
        sizer.Add((1, 1), 1, wx.EXPAND)

        # Create a Row Sizer
        hSizer4 = wx.BoxSizer(wx.HORIZONTAL)
        # Add a Process button
        self.btnProcess = wx.Button(self, wx.ID_OK, "Process")
        self.btnProcess.Bind(wx.EVT_BUTTON, self.OnProcess)
        hSizer4.Add(self.btnProcess, 8, wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        # Add the row sizer to the main sizer
        sizer.Add(hSizer4, 0, wx.EXPAND)

        # Set the main Sizer as the panel's sizer        
        self.SetSizer(sizer)

    def GetReferenceFileName(self):
        """ Determine the Reference File Name based on current program settings """
        # Get the path and name of the Data File, separate it to the path, the root file name, and the file extension
        datafile = self.filenameCtrl.GetPath()
        (path, fn) = os.path.split(datafile)
        (fnroot, fnext) = os.path.splitext(fn)

        # Get the output path
        outputPath = self.filePathCtrl.GetPath()  # os.path.join(self.Settings.filePathCtrl.GetPath(), 'Comparisons')

        # The Reference File Name combines the output path, the data file root, the "reference" modifier, and the txt extension.
        referenceFilename = os.path.join(outputPath, fnroot + '_reference.txt')
        # Return the reference file name
        return referenceFilename

    def OnFileSelected(self, event):
        """ Process change events from the text entry and Browse buttons for file name and output path """
        # Get the updated Reference File Name
        referenceFilename = self.GetReferenceFileName()
        # If the Reference File ixists, disable the Reference File Button
        if os.path.exists(referenceFilename):
            self.btnCreateReference.Enable(False)
        else:
            self.btnCreateReference.Enable(True)

    def OnProcess(self, event):
        """ Handle the EVT_BUTTON event from the Process Button """
        # Call the function passed in by the calling routine
        self.processCmd(event)

    def OnCreateReference(self, event):
        """ Process the EVT_BUTTON event from the Create Reference button """

        # Get the Reference File Name
        outputFilename = self.GetReferenceFileName()
        # Remember the contents of the Instructions box
        instructions = self.txt.GetValue()
        # Clear the Instructions
        self.txt.Clear()
        # Let the user know the Reference File is being created
        self.txt.AppendText('Creating Reference File.  This process can take significant time, depending on the size of the data ')
        self.txt.AppendText('file.\n\n')
        self.txt.AppendText('The Reference File is called "{0}".  You should manually check and correct this file '.format(outputFilename))
        self.txt.AppendText('before running the full battery of tests.\n\n')
        # Disable the Create Reference and Process Buttons
        self.btnCreateReference.Enable(False)
        self.btnProcess.Enable(False)
        # Update the app so the feedback will show up!
        wx.Yield()

        # NOTE:  Yeah, yeah, this code block should be in a shared function with the main Faster Whisper processing routine below.
        #        It's not yet.  Feel free to make that change if you'd like.

        # Historically (in English), I've gotten the most accuraate transcripts using the Large-v2 model.
        # We will create the initial Reference File with this model, although the user should correct this file manually
        # before continuing.
        modelToUse = 'large-v2'
        # Determine the model's path by combining the model path specification with the model selected
        modelDir = os.path.join(self.modelPathCtrl.GetPath(), modelToUse)  # , 'faster_whisper_models'
        # If the model directory does not exist ...
        if not os.path.isdir(modelDir):
            # ... download the model
            faster_whisper.download_model(modelToUse, cache_dir=modelDir)

        # Determine, based on the GPU Available checkbox, whether we should use the CPU or CUDA device
        if self.includeGPU.IsChecked():
            device = 'cuda'
        else:
            device = 'cpu'

        # Initialize the Transcript
        transcript = ''
        # Initialize a list of punctuation marks that signal the end of a sentence
        sentenceEnds = ['.', '?']

        # Set values for Faster Whisper parameters
        compute_type = "float32"
        language = LanguageLookup[self.language.GetStringSelection()]
        action = 'transcribe'
        temperature = 0.0
        compression_ratio = 2.4
        log_prob_threshold = -1

        # Load the Faster Whisper model
        model = faster_whisper.WhisperModel(modelToUse, 
                                            device=device, 
                                            compute_type=compute_type,
                                            download_root=modelDir)
        # Process the data file using the selected model and settings
        (segments, info) = model.transcribe(self.filenameCtrl.GetPath(),
                                            language=language,
                                            task=action,
                                            temperature=temperature,
                                            compression_ratio_threshold=compression_ratio,
                                            log_prob_threshold=log_prob_threshold, 
                                            word_timestamps=True)

        # Initialize a blank line
        line = ''
        # We'll loop through all the segments, dividing them up into sentences
        for segment in segments:
            # Now look through each segment, dividing it up into individual words
            for word in segment.words:
                # Add the word to the line
                line += word.word
                # If the word ends with a sentence ending punctuation mark ...
                if word.word[-1] in sentenceEnds:
                    # ... add the line to the transcript, add a line break, and start a new line
                    transcript += line + '\n'
                    line = ''

            # Provide feedback to the user
            self.txt.AppendText("Processing with {0} - {1} : {2}\n".format(modelToUse, device, TimeMsToStr(segment.end * 1000)))
            # Update the app so the feedback will show up!
            wx.Yield()

        # If we still have info in the line, add it to the transcript
        if line != '':
            transcript += line + '\n'

        # Save the reference file using UTF-8 encoding, required for many non-English languages
        f = codecs.open(outputFilename, mode='w', encoding="utf8")
        f.write(transcript)
        f.flush()
        f.close()

        # Clear the note to the user about the reference file being created
        self.txt.Clear()
        # Return the Instructions to their rightful place on the panel
        self.txt.SetValue(instructions)
        # Enable the Create Reference and Process buttons
        self.btnCreateReference.Enable(True)
        self.btnProcess.Enable(True)

class ResultsPanel(wx.Panel):
    """ Create a Panel for test results presentation """
    def __init__(self, parent):
        # Create the Panel
        wx.Panel.__init__(self, parent=parent)
        # Define the main Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a font and a TextCtrl using that font
        font1 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        self.txt = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE)
        self.txt.SetFont(font1)
        sizer.Add(self.txt, 1, wx.EXPAND | wx.ALL, 0)

        # Set the main Sizer as the panel's sizer        
        self.SetSizer(sizer)
        
class GraphPanel(wx.Panel):
    """ Create a Panel for test results graphic """
    def __init__(self, parent):
        # Create the Panel
        wx.Panel.__init__(self, parent=parent)
        # Define the main Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a StaticBitmap for the results graph
        self.graphic = wx.StaticBitmap(self, wx.ID_ANY)
        sizer.Add(self.graphic, 1, wx.EXPAND | wx.ALL, 10)

        # Set the main Sizer as the panel's sizer        
        self.SetSizer(sizer)
    
class ComparisonPanel(wx.Panel):
    """ Create a Panel for test results file comparisons """
    def __init__(self, parent):
        # Create the Panel
        wx.Panel.__init__(self, parent=parent)
        # Define the main Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create an HTML Window for displaying the file comparison results with formatting and color
        self.html = wx.html.HtmlWindow(self, wx.ID_ANY)
        sizer.Add(self.html, 1, wx.EXPAND | wx.ALL, 0)

        # Set the main Sizer as the panel's sizer        
        self.SetSizer(sizer)

class FWEval(wx.Frame):
    """ This window displays the main Program form. """
    def __init__(self, parent, id, title):
        """ Initialize the main Faster Whisper Evaluation Frame """
        # Define the main Frame
        wx.Frame.__init__(self, parent, id, title + ' {0}'.format(VERSION), size = (1000, 1000), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour("sky blue")

        # Create a panel to hold the form contents.  This ensures that Tab Order works properly.
        self.panel = wx.Panel(self, wx.ID_ANY)
        # Create the main sizer for the panel
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a Notebook so we can create multiple tabs for different types of data results
        self.nb = wx.Notebook(self.panel, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        sizer.Add(self.nb, 1, wx.EXPAND | wx.ALL, 10)

        # Create the Program Settings tab
        self.Settings = SettingsPanel(self.nb, self.OnProcess)
        self.nb.AddPage(self.Settings, "Program Settings")

        # Create the (text) Results tab
        self.Results = ResultsPanel(self.nb)
        self.nb.AddPage(self.Results, "Results")

        # Redirect "self.txt" to the notebook Results tab txt ctrl
        self.txt = self.Results.txt

        # Create the Graph tab for the results graph
        self.Graph = GraphPanel(self.nb)
        self.nb.AddPage(self.Graph, "Graph")

        # Create the Comparison tab
        self.Comparison = ComparisonPanel(self.nb)
        self.nb.AddPage(self.Comparison, "Quality Comparison")

        # Redirect "self.html" to the notebook Comparison tab html ctrl
        self.html = self.Comparison.html

        # Create a Row sizer
        hSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        # Create a Save button
        self.btnSave = wx.Button(self.panel, wx.ID_OK, "Save")
        self.btnSave.Bind(wx.EVT_BUTTON, self.OnSave)
        # Add the Save Button to the Row Sizer
        hSizer1.Add(self.btnSave, 2, wx.ALL, 10)
        # Add the Row Sizer to the main panel sizer
        sizer.Add(hSizer1, 0, wx.EXPAND)

        # Status Bar
        self.CreateStatusBar()
        self.SetStatusText("")

        # Set the main sizer to the panel
        self.panel.SetSizer(sizer)
        # Set up automatic form layout
        self.panel.SetAutoLayout(True)
        self.panel.Layout()
        self.Layout()
        self.CenterOnScreen()
        self.Show(True)

        # Initialize the Results Data
        self.resultsData = {}

    def OnProcess(self, event):
        """ Process the file selected on the Settings tab """

        def GetWords(text):
            """ Return a list of words """
            # Initialize a list of words
            words = []
            # For each line in the text ...
            for line in text.split('\n'):
                # ... for each word in the line ...
                for word in line.split(' '):
                    # ... strip punctuation from words
                    punctuation = ('.', ',', '?', '!')
                    for mark in punctuation:
                        word = word.replace(mark, '')
                    # If there's anything left ...
                    if not word in ('', ' ', '\n'):
                        # ... add it to the word list
                        words.append(word.strip().lower())
                # Add an HTML Line Break at the end of each line
                words.append('<BR>')
            # Return the word list
            return(words)

        # Select the Program Settings tab in the Notebook control
        self.nb.SetSelection(1)

        # Clear the Results text and initialize the HTML for the Comparison text
        self.txt.Clear()
        self.html.SetPage('<html><body></body></html>')

        # Get the data file from the Settings tab and divide it up into path, filename root, and file extension
        datafile = self.Settings.filenameCtrl.GetPath()
        (path, fn) = os.path.split(datafile)
        (fnroot, fnext) = os.path.splitext(fn)

        # Get the Output Path and the Model Path from the Settings tab
        outputPath = self.Settings.filePathCtrl.GetPath()
        modelPath = self.Settings.modelPathCtrl.GetPath()

        # Provide user feedback
        self.txt.AppendText('File "{0}" selected\n\n'.format(fn))

        # Get the Reference File Name
        referenceFilename = self.Settings.GetReferenceFileName()
        # Open the Reference File using UTF-8 encoding, required for many non-English languages
        f = codecs.open(referenceFilename, mode='r', encoding='utf8')
        # Load the Reference Transcript
        reference_transcript = f.read()
        # Close the Reference File
        f.close()

        # Extract the words from the Reference Transcript
        reference_words = GetWords(reference_transcript)
        # Define sentence-ending characters
        sentenceEnds = ['.', '?']

        # If we are using the Transana Models only ...
        if self.Settings.transanaModels.IsChecked():
            # ... (Transana removes English-only models and the useless distil-large-v2 model
            models = ['tiny', 'base', 'small', 'medium', 'large', 'large-v1', 'large-v2', 'large-v3', 'distil-large-v3', 'large-v3-turbo', 'turbo']
#            models = ['tiny', 'base', 'small', 'medium','distil-large-v3', 'large-v3-turbo', 'turbo']
#            models = ['tiny', 'base']
        # If we are NOT using only the Transana models ...
        else:
            # ... get a list of all available models for Faster Whisper
            models = faster_whisper.available_models()

        # Initialize the list of available devices.  CPU is always available.
        devices = ['cpu']
        # GPU processing is supported on Windows (if NVidia files are installed) but not macOS.
        if 'wxMSW' in wx.PlatformInfo:
            # We use the Settings tab checkbox to indicate GPU availability rather than trying to auto-detect.
            if self.Settings.includeGPU.IsChecked():
                # Add the GPU (cuda) model if requested
                devices.append('cuda')

        # Convert the Settings tab language selection to the language abbreviation required by Faster Whisper
        language = LanguageLookup[self.Settings.language.GetStringSelection()]
        # Set other Faster Whisper settings
        compute_type = "float32"
        action = 'transcribe'  # 'translate'
        temperature = 0.0  # [0.0, 0.2, 0.4, 0.6, 0.8, 1.0,]
        compression_ratio = 2.4  # 2.4  20.0
        log_prob_threshold = -1   # -1   -300

        # Initialize a dictionary for transcription results
        results = {}
        # Initialize a string for HTML Comparison Results
        self.htmlData = ''

        # Start exception handling
        try:
            # Initialize HTML Comparison feedback
            st = '<html><head><title>Faster Whisper Model Comparisons</title></head><body>'
            self.html.SetPage(st)
            self.htmlData += st

            # Initialize a title for the results graph and initialize a dictionary for its data
            graphName = "Faster Whisper Accuracy and Processing Times"
            graphData = {}

            # For each model ...
            for modelToUse in models:
                # Determine the model's path by combining the model path specification with the model selected
                modelDir = os.path.join(modelPath, modelToUse)
                # If the model directory does not exist ...
                if not os.path.isdir(modelDir):
                    # ... download the model
                    faster_whisper.download_model(modelToUse, cache_dir=modelDir)

                # For each defined device ...
                for device in devices:
                    # ... provide user feedback
                    self.SetStatusText("Processing with {0} - {1}".format(modelToUse, device))
                    self.txt.AppendText('Model:  {0:16}  Device:  {1:7}'.format(modelToUse, device))

                    # Set the Output File Name based on the Settings Tab output path, the file's name, the device, and the model
                    outputFilename = os.path.join(outputPath, fnroot + '_' + device + '_' + modelToUse + '.txt')

                    # Initialize the Transcript
                    transcript = ''

                    # Load the Faster Whisper model
                    model = faster_whisper.WhisperModel(modelToUse, 
                                                        device=device, 
                                                        compute_type=compute_type,
                                                        download_root=modelDir)
                    # If the selected language is supported by the model ...
                    if language in model.supported_languages:

                        # CPU and GPU accuracy results are identical.  Theefore, only update the HTML Comparison information
                        # for one, the CPU models, which is always present.
                        if device == 'cpu':
                            st = "<H1>Processing {0} with {1} - {2}</H1>".format(fn, modelToUse, device)
                            self.html.AppendToPage(st)
                            self.htmlData += st

                        # Start timing the transcription process
                        startTime = time.time()

                        # Process the data file using the selected model and settings
                        (segments, info) = model.transcribe(datafile, 
                                                            language=language,
                                                            task=action,
                                                            temperature=temperature,
                                                            compression_ratio_threshold=compression_ratio,
                                                            log_prob_threshold=log_prob_threshold, 
                                                            word_timestamps=True)

                        # Initialize a blank line
                        line = ''
                        # We'll loop through all the segments, dividing them up into sentences
                        for segment in segments:
                            # Now look through each segment, dividing it up into individual words
                            for word in segment.words:
                                # Add the word to the line
                                line += word.word
                                # If the word ends with a sentence ending punctuation mark ...
                                if word.word[-1] in sentenceEnds:
                                    # ... add the line to the transcript, add a line break, and start a new line
                                    transcript += line + '\n'
                                    line = ''

                            # Provide feedback to the user
                            self.SetStatusText("Processing with {0} - {1} : {2}".format(modelToUse, device, TimeMsToStr(segment.end * 1000)))
                            # Update the app so the feedback will show up!
                            wx.Yield()

                        # If we still have info in the line, add it to the transcript
                        if line != '':
                            transcript += line + '\n'

                        # Save the transcription file using UTF-8 encoding, required for many non-English languages
                        f = codecs.open(outputFilename, mode='w', encoding='utf8')
                        f.write(transcript)
                        f.flush()
                        f.close()

                        # Stop the transcription processing timing
                        elapsedTime = time.time() - startTime
                        # Provide user feedback
                        self.txt.AppendText('  Elapsed Time:  {0:8.2f}'.format(elapsedTime))

                        # Create human-readable labels for devices
                        if device == 'cpu':
                            deviceLbl = 'CPU'
                        elif device == 'cuda':
                            deviceLbl = 'GPU'

                        # Add the elapsed time to the Graphics data dictionary, creating an entry if needed and updating an entry if it exists
                        if not modelToUse in graphData.keys():
                            graphData[modelToUse] = {deviceLbl : elapsedTime}
                        else:
                            graphData[modelToUse][deviceLbl] = elapsedTime

                        # CPU and GPU accuracy results are identical.  Theefore, only update the HTML Comparison information
                        # for one, the CPU models, which is always present.
                        if device == 'cpu':

                            # Now add the file comparison results to the HTML control
                            
                            # Provide user feedback
                            self.SetStatusText("Performing comparison for {0} - {1}".format(modelToUse, device))
                            wx.Yield()

                            # Isolate the words from the new transcript for comparison
                            transcript_words = GetWords(transcript)
                            # Initialize a dictionary for the comparison results
                            comparison_counter = {'delete' : 0,
                              'equal' : 0,
                              'insert' : 0,
                              'replace' : 0}

                            # Use difflib.SequenceMatcher to compare the reference words list to the transcripts word list
                            seq_compare = difflib.SequenceMatcher(None, reference_words, transcript_words)
                            # Document the comparison using HTML
                            st = '<p>'
                            self.html.AppendToPage(st)
                            self.htmlData += st

                            # For each section of the comparison results ...
                            for opcode in seq_compare.get_opcodes():
                                # ... get the words compared in the two files
                                text1 = reference_words[opcode[1]:opcode[2]]
                                text2 = transcript_words[opcode[3]:opcode[4]]

                                # If the section is "equal", display each word from the reference text in black
                                if opcode[0] == 'equal':
                                    for newWord in text1:
                                        st = '{0} '.format(newWord)
                                        self.html.AppendToPage(st)
                                        self.htmlData += st
                                        # If we don't have a line break, count the word as "equal"
                                        if newWord != '<BR>':
                                            comparison_counter[opcode[0]] += 1

                                # If the section is "replace", display each word from the reference text, a slash, and the transcript word list in light blue
                                elif opcode[0] == 'replace':
                                    # Handle it if the lists are different lengths
                                    for cnt in range(max(len(text1), len(text2))):
                                        if cnt < len(text1):
                                            newWord = text1[cnt]
                                        else:
                                            newWord = ''
                                        if cnt < len(text2):
                                            newWord2 = text2[cnt]
                                        else:
                                            newWord2 = ''
                                        st = '<B><FONT COLOR="#00BFFF">{0}</FONT>/<FONT COLOR="#00bfcc">{1}</FONT></B> '.format(newWord, newWord2)
                                        self.html.AppendToPage(st)
                                        self.htmlData += st
                                        # If we don't have a line break, count the word as "replace"
                                        if newWord != '<BR>' and newWord2 != '<BR>':
                                            comparison_counter[opcode[0]] += 1
                                    
                                # If the section is "insert", display each inserted word from the transcript word list in green
                                elif opcode[0] == 'insert':
                                    for newWord in text2:
                                        st = '<I><FONT COLOR="#00FF00">{0}</FONT></I> '.format(newWord)
                                        self.html.AppendToPage(st)
                                        self.htmlData += st
                                        # If we don't have a line break, count the word as "insert"
                                        if newWord != '<BR>':
                                            comparison_counter[opcode[0]] += 1

                                # If the section is "delete", display each deleted word from the reference word list in red
                                elif opcode[0] == 'delete':
                                    for newWord in text1:
                                        st = '<B><FONT COLOR="#FF0000">{0}</FONT></B> '.format(newWord)
                                        self.html.AppendToPage(st)
                                        self.htmlData += st
                                        # If we don't have a line break, count the word as "delete"
                                        if newWord != '<BR>':
                                            comparison_counter[opcode[0]] += 1

##                                wx.YieldIfNeeded()

                            # Close the HTML paragraph
                            st = '</p>'
                            self.html.AppendToPage(st)
                            self.htmlData += st

                            # Add the legend to the HTML
                            st = 'Equal: {0}<BR>'.format(comparison_counter['equal'])
                            self.html.AppendToPage(st)
                            self.htmlData += st
                            st = 'Changed: {0}<BR>'.format(comparison_counter['replace'])
                            self.html.AppendToPage(st)
                            self.htmlData += st
                            st = 'Added: {0}<BR>'.format(comparison_counter['insert'])
                            self.html.AppendToPage(st)
                            self.htmlData += st
                            st = 'Deleted: {0}<BR>'.format(comparison_counter['delete'])
                            self.html.AppendToPage(st)
                            self.htmlData += st
                            totalWords = comparison_counter['equal'] + comparison_counter['replace'] + comparison_counter['insert'] + comparison_counter['delete']
                            correctWords = comparison_counter['equal']
                            correctPercent = correctWords / totalWords * 100.0
                            wrongWords = comparison_counter['replace'] + comparison_counter['insert'] + comparison_counter['delete']
                            wrongPercent = wrongWords / totalWords * 100.0
                            st = '<p>Accuracy:  {0:5.2f}%  Error Rate: {1:5.2f}%</p>'.format(correctPercent, wrongPercent)
                            self.html.AppendToPage(st)
                            self.htmlData += st
                            st = '<p>Key: Black = same.&nbsp;&nbsp;&nbsp;<FONT COLOR="#00BFFF">Blue = Changed</FONT>&nbsp;&nbsp;&nbsp;<FONT COLOR="#00FF00">Green = Added to 2nd</FONT>'
                            self.html.AppendToPage(st)
                            self.htmlData += st
                            st = '&nbsp;&nbsp;&nbsp;<FONT COLOR="#FF0000">Red = Removed from 1st</FONT></p>'
                            self.html.AppendToPage(st)
                            self.htmlData += st

                        # Add the speed and accuracy results to the results dictionary
                        results[(modelToUse, device)] = { 'time' : elapsedTime,
                                                          'accuracy' : correctPercent }
                        # Add the accuracy results to the graph data
                        graphData[modelToUse]['Accuracy'] = correctPercent

                        # Provide user feedback
                        self.txt.AppendText('  Accuracy:  {0:8.2f}\n'.format(correctPercent))

                        # Create the Chart Graphic
                        chartGraphic = ChartGraphic.ChartGraphic(graphName, graphData, self.Graph.graphic.GetSize())
                        # Get the Bitmap from the Chart Graphic
                        bitmap1 = chartGraphic.GetBitmap()
                        # Place the Bitmap on the Graph tab
                        self.Graph.graphic.SetBitmap(bitmap1)
                        self.Graph.graphic.Update()
                        self.Graph.graphic.Refresh()
                        wx.Yield()
                    # If the selected language is not supported by the model ...
                    else:
                        # ... provide user feedback
                        self.txt.AppendText('  Language "{0}" not supported by this model.\n'.format(self.Settings.language.GetStringSelection()))

        # Handle Runtime Errors
        except RuntimeError as e:
            exc = sys.exc_info()
            print()
            print(exc[0])
            print(exc[1])
            traceback.print_exc()

            # We need to explicitly clear the GPU Memory by deleting the model
            if model == 'cuda':
                del(results[model])

        # Handle all other exceptions
        except:
            exc = sys.exc_info()
            print()
            print(exc[0])
            print(exc[1])
            traceback.print_exc()

        # Complete the comparison HTML
        st = '</body></html>'
        self.html.AppendToPage(st)
        self.htmlData += st

        # Let's save the results for possible export
        self.resultsData = results

        # Create a "Final Text Report" for the user.  This signals that the evaluation is done.
        self.txt.AppendText('\n\n\n')
        self.txt.AppendText("This tool is designed to let you know when to use the GPU and when not to.  Here's what we found:\n\n")
        self.txt.AppendText('{0:20} | {1:10} | {2:10} | Recommendation\n'.format('Model', 'CPU', 'GPU'))
        self.txt.AppendText('---------------------|------------|------------|--------------------------------------\n')

        # For each model in the list of models ...
        for model in models:
            # ... check to see if the model - CPU pairing has data.  It won't if the language was not supported
            if (model, 'cpu') in results.keys():
                # On Windows, when the GPU option is checked ...
                if 'wxMSW' in wx.PlatformInfo and self.Settings.includeGPU.IsChecked():
                    # Compare the CPU and GPU results for processing speed and report the result
                    if results[(model, 'cpu')]['time'] < results[(model, 'cuda')]['time']:
                        (1 - (results[(model, 'cpu')]['time'] / results[(model, 'cpu')]['time'])) * 100
                        rec = 'CPU is {0:5.2f} percent faster than GPU'.format((1 - (results[(model, 'cpu')]['time'] / results[(model, 'cuda')]['time'])) * 100)
                    else:
                        rec = 'GPU is {0:5.2f} percent faster than CPU'.format((1 - (results[(model, 'cuda')]['time'] / results[(model, 'cpu')]['time'])) * 100)
                    # Compare the CPU and GPU results for Accuracy and report the result.  (Turns out, they're always equal!!)
                    if results[(model, 'cpu')]['accuracy'] > results[(model, 'cuda')]['accuracy']:
                        rec2 = 'CPU is more accurate than GPU'
                    elif results[(model, 'cpu')]['accuracy'] == results[(model, 'cuda')]['accuracy']:
                        rec2 = 'CPU and GPU are equally accurate'
                    else:
                        rec2 = 'GPU is more accurate than CPU'
                    # Display results
                    self.txt.AppendText('{0:20} | {1:10.2f} | {2:10.2f} | {3}\n'.format(model, results[(model, 'cpu')]['time'], results[(model, 'cuda')]['time'], rec))
                    self.txt.AppendText('{0:20} | {1:10.2f} | {2:10.2f} | {3}\n'.format('', results[(model, 'cpu')]['accuracy'], results[(model, 'cuda')]['accuracy'], rec2))
                # If we're not on Windows OR the GPU option is not selected ...
                else:
                    # ... this can be left blank
                    rec = ''
                    rec2 = ''
                    # Display results
                    self.txt.AppendText('{0:20} | {1:10.2f} | {2:10.2f} | {3}\n'.format(model, results[(model, 'cpu')]['time'], 0, rec))
                    self.txt.AppendText('{0:20} | {1:10.2f} | {2:10.2f} | {3}\n'.format('', results[(model, 'cpu')]['accuracy'], 0, rec2))
                self.txt.AppendText('---------------------|------------|------------|--------------------------------------\n')

    def OnSave(self, event):
        """ Save the data outputs, including the text output, the Comma Separated Values output, the Comparison HTML file, and the
            results graph (png) """
        # Get the data file info and extract path, filename, and extension 
        datafile = self.Settings.filenameCtrl.GetPath()
        (path, fn) = os.path.split(datafile)
        (fnroot, fnext) = os.path.splitext(fn)

        # Build file names for the text output (transcript) file, ...
        textOutputFile = os.path.join(self.Settings.filePathCtrl.GetPath(), fnroot + '_results.txt')
        # ... the Comma Seperated Values file, ...
        dataOutputFile = os.path.join(self.Settings.filePathCtrl.GetPath(), fnroot + '_data.csv')
        # ... the Comparison HTML file, ...
        comparisonOutputFile = os.path.join(self.Settings.filePathCtrl.GetPath(), fnroot + '_comparisons.html')
        # ... and the output graph (PNG)
        graphOutputFile = os.path.join(self.Settings.filePathCtrl.GetPath(), fnroot + '_graph.png')

        # Save the Transcript using UTF-8 encoding, required for many non-English languages
        f = codecs.open(textOutputFile, mode='w', encoding="utf8")
        f.write(self.txt.GetValue())
        f.flush()
        f.close()

        # Initialize a dictionary for the output data
        outputData = {}
        # We need to re-organize the data before outputting it!
        # For each entry in the resultsData dictionary ...
        for (model, device) in self.resultsData.keys():
            # ... if the output data does NOT have a key for the model for this resultsData entry ...
            if not model in outputData.keys():
                # ... create an entry for the model.  The initial model entry gets an Accuracy element as well
                outputData[model] = {device : self.resultsData[(model, device)]['time'],
                                     'accuracy' : self.resultsData[(model, device)]['accuracy']}
            # If the output data HAS a model entry, add the Time value for the additional device
            else:
                outputData[model][device] = self.resultsData[(model, device)]['time']

        # Open the CSV file for output
        f = open(dataOutputFile, 'w')
        # Add the source file name to the file
        f.write(fn + '\n')
        # GPU is supported on Windows but not the Mac.  Add the correct header to the CSV file.
        if 'wxMSW' in wx.PlatformInfo and self.Settings.includeGPU.IsChecked():
            f.write('Model, CPU, GPU, Accuracy\n')
        else:
            f.write('Model, CPU, Accuracy\n')
        # For each entry in the output data ...
        for key in outputData.keys():
            # ... create an output line
            line = '{0}, {1:5.2f}, '.format(key, outputData[key]['cpu'])
            # ... add the GPU data if appropriate
            if 'cuda' in outputData[key].keys():
                line += '{0:5.2f}, '.format(outputData[key]['cuda'])
            # ... complete the output line
            line += '{0:5.2f}\n'.format(outputData[key]['accuracy'])
            # ... and write the output line to the CSV file
            f.write(line)
        # Flush the file buffer and close the file
        f.flush()
        f.close()

        # Create the appropriate output graph
        bmp = self.Graph.graphic.GetBitmap()
        # Save the graph
        bmp.SaveFile(graphOutputFile, wx.BITMAP_TYPE_PNG)

        # Open the HTML file using UTF-8 encoding, required for many non-English languages
        f = codecs.open(comparisonOutputFile, mode='w', encoding='utf8')
        # Dump the HTML output to the file
        f.writelines(self.htmlData)
        # Flush the file buffer and close the file
        f.flush()
        f.close()

class FWEvalApp(wx.App):
    """ The Faster Whisper Evaluation Main Application """

    def OnInit(self):
        """ Initialize the Application """
        # Create the main application frame
        frame = FWEval(None, wx.ID_ANY, "Faster Whisper Speed and Accuracy Test")
        return True
    
# Define all available languages and their associated language codes as a global dictionary
LanguageLookup = {_('Auto-detect') : None,
                  _('Afrikaans') : 'af',
                  _('Albanian') : 'sq',
                  _('Amharic') : 'am',
                  _('Arabic') : 'ar',
                  _('Armenian') : 'hy',
                  _('Assamese') : 'as',
                  _('Aserbaijani') : 'az',
                  _('Bashkir') : 'ba',
                  _('Basque') : 'eu',
                  _('Belarusian') : 'be',
                  _('Bengali') : 'bn',
                  _('Bosnian') : 'bs',
                  _("Breton") : 'br',
                  _('Bulgarian') : 'bg',
                  _('Burmese') : 'my',
                  _('Cantonese') : 'yue',
                  _('Catalan') : 'ca',
                  _('Chinese') : 'zh',
                  _('Croatian') : 'hr',
                  _('Czech') : 'cs',
                  _('Danish') : 'da',
                  _('Dutch') : 'nl',
                  _('English') : 'en',
                  _('Estonian') : 'et',
                  _('Faroese') : 'fo',
                  _('Finnish') : 'fi',
                  _('French') : 'fr',
                  _('Galician') : 'gl',
                  _('Georgian') : 'ka',
                  _('German') : 'de',
                  _('Greek') : 'el',
                  _('Gujarati') : 'gu',
                  _('Haitian') : 'ht',
                  _('Hausa') : 'ha',
                  _('Hawaiian') : 'haw',
                  _('Hebrew') : 'he',
                  _('Hindi') : 'hi',
                  _('Hungarian') : 'hu',
                  _('Icelandic') : 'is',
                  _('Indonesian') : 'id',
                  _('Italian') : 'it',
                  _('Japanese') : 'ja',
                  _('Javanese') : 'jw',  # Typo for jv, Javanese
                  _('Kannada') : 'kn',
                  _('Kazakh') : 'kk',
                  _('Central Khmer') : 'km',
                  _('Korean') : 'ko',
                  _('Latin') : 'la',
                  _('Latvian') : 'lv',
                  _('Lao') : 'lo',
                  _('Lingala') : 'ln',
                  _('Lithuanian') : 'lt',
                  _('Luxembourgish') : 'lb',
                  _('Macedonian') : 'mk',
                  _('Malagasy') : 'mg',
                  _('Malay') : 'ms',
                  _('Malayalam') : 'ml',
                  _('Maltese') : 'mt',
                  _('Maori') : 'mi',
                  _('Marathi') : 'mr',
                  _('Mongolian') : 'mn',
                  _('Nepali') : 'ne',
                  _('Norwegian Bokmal') : 'no',
                  _('Norwegian Nynorsk') : 'nn',
                  _('Occitan') : 'oc',
                  _('Pashto') : 'ps',
                  _('Persian') : 'fa',
                  _('Polish') : 'pl',
                  _('Portuguese') : 'pt',
                  _('Punjabi') : 'pa',
                  _('Romanian') : 'ro',
                  _('Russian') : 'ru',
                  _('Sanskrit') : 'sa',
                  _('Serbian') : 'sr',
                  _('Shona') : 'sn',
                  _('Sindhi') : 'sd',
                  _('Sinhala') : 'si',
                  _('Slovak') : 'sk',
                  _('Slovenian') : 'sl',
                  _('Somali') : 'so',
                  _('Spanish') : 'es',
                  _('Sundanese') : 'su',
                  _('Swahili') : 'sw',
                  _('Swedish') : 'sv',
                  _('Tagalog') : 'tl',
                  _('Tajik') : 'tg',
                  _('Tamil') : 'ta',
                  _('Tatar') : 'tt',
                  _('Telugu') : 'te',
                  _('Thai') : 'th',
                  _('Tibetan') : 'bo',
                  _('Turkish') : 'tr',
                  _('Turkmen') : 'tk',
                  _('Ukranian') : 'uk',
                  _('Urdu') : 'ur',
                  _('Uzbek') : 'uz',
                  _('Vietnamese') : 'vi',
                  _('Welsh') : 'cy',
                  _('Yiddish') : 'yi',
                  _('Yoruba') : 'yo', }

# Create the Faster Whisper Evaluation app and launch the app's Main Loop
app = FWEvalApp()
app.MainLoop()
