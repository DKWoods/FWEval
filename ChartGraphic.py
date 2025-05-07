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

"""This module creates a line chart graphic and makes the bitmap available. """

__author__ = 'David K. Woods <dwoods@transana.com>'

# Import wxPython
import wx
# If we're running in stand-alone mode ...
if __name__ == '__main__':
    # ... import wxPython's RichTextCtrl
    import wx.richtext as richtext

class ChartGraphic(object):
    """ This module accepts data, creates a Chart from it, and returns a wx.Bitmap. """
    def __init__(self, title, data, size=(800, 700)):
        """ Create a chart.
               title        Title for the Chart
               data         Dictionary of data values for the Chart
            This module sizes the bitmap for a printed page by default. """

        def xPos(x):
            """ Calculate the horizontal position in pixels """
            # numCategories, chartLeft, and chartWidth are constants in the calling routine
            # Calculate the horizontal distance between categories
            width = chartWidth / numCategories
            # Calculate the position of the selected category
            xPos = (float(x) / numCategories) * chartWidth + width / 2 + chartLeft
            # Return the horizontal position
            return int(xPos)

        def yPos(x, maxVal):
            """ Calculate the vertical position in pixels """
            # data and chartHeight are constants in the calling routine
            # Determine the size of the largest value
            yMax = maxVal
            # Calculate the position of the value passed in
            yPos = float(x) / yMax * chartHeight
            # We return 95% of the height value to give the chart some white space at the top.
            return int(yPos * 0.95)

        def verticalAxisValues(maxVal):
            """ Given the maximum value of the axis, determine what values should appear as axis labels.
                This method implements the 2-5-10 rule. """
            # Initialize a list of values to return
            values = []

            # Let's normalize the data as part of assigning axis labels
            # Initilaize the increment between axis label values
            increment = 1
            # Initialize the conversion factor for axis labels, used in handling large values
            convertFactor = 1
            # While our maxValue is over 100 ...
            while maxVal > 100:
                # ... reduce the maximum value by a factor of 10 ...
                maxVal /= 10
                # ... and increase our conversion factor by a factor of 10.
                convertFactor *= 10
            # If our normalized max value is over 50 ...
            if maxVal > 50:
                # ... increments of 10 will give us between 5 and 10 labels
                increment = 10
            # If our normalized max value is between 20 and 50 ...
            elif maxVal > 20:
                # ... increments of 5 will give us between 4 and 10 labels
                increment = 5
            # If our normalized max value is between 8 and 20 ...
            elif maxVal > 8:
                # ... increments of 2 will give us between 4 and 10 labels
                increment = 2
            # If our normalized max value is 8 or less ...
            else:
                # ... increments of 1 will five us between 1 and 8 labels.
                increment = 1

            # for values between 0 and our max value (plus 1 to include the mac value if a multiple of 10) space by increment ...
            for x in range(0, int(maxVal + 1), increment):
                # ... add the incremental value multiplied by the conversion factor to our list of axis labels
                values.append(x * convertFactor)
            # Return the list of axis labels
            return values

        # Get the Graphic Dimensions
        (imgWidth, imgHeight) = size

        # Create an empty bitmap
        self.bitmap = wx.Bitmap(imgWidth, imgHeight)
        # Get the Device Context for that bitmap
        self.dc = wx.BufferedDC(None, self.bitmap)
     
        # Determine the longest horizontal axis label
        # Define the label font size
        axisLabelFontSize = 11
        # Define a Font for axis labels
        font = wx.Font(axisLabelFontSize, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, False)
        # Set the Font for the DC
        self.dc.SetFont(font)
        # Initize the max width variable
        maxWidth = 0

        dataLabels = list(data.keys())
        # The length of data is the number of bars we need
        numCategories = len(dataLabels)

        # For each horizontal label ...
        for x in range(numCategories):
            # ... determine the size of the label
            (txtWidth, txtHeight) = self.dc.GetTextExtent(dataLabels[x])
            # See if it's bigger than previous labels
            maxWidth = max(txtWidth, maxWidth)

        # Give a left margin of 70 pixels for the vertical axis labels
        chartLeft = 70
        # The width of the chart will be the image width less the left margin and 25 pixels for right margin
        chartWidth = imgWidth - chartLeft - 25
        # Give a top margin of 50 pixels to have room for the chart title
        if title != '':
            chartTop = 50
        # or 20 pixels if there is no title
        else:
            chartTop = 20
        # Reserve almost HALF the image for bar labels.  (Transana uses LONG labels!)
        chartHeight = max(int(imgHeight / 2), imgHeight - maxWidth - chartTop - 30)
        
        # Initialize a colorIndex to track what color to assign each bar
        colorIndx = 0
        # Define the colors to be used in the chart
        colors = [(  0, 255,   0),  # Green
                  (  0,   0, 255),  # Blue
                  (255,   0,   0),  # Red
                  (255,   0, 255),  # Magenta
                  (  0, 128, 255),  # * Greenish Blue
                  (128, 128, 128),  # Grey
                  (128,   0, 128),  # * Dark Magenta
                  (204,  50, 153),  # Violet Red
                  (255,   0, 128),  # * Light Magenta
                  (255, 128, 128),  # * Light Red
                  (  0, 255, 255),  # Cyan
                  (  0, 128,   0),  # * Dark Green
                  (128,   0, 255),  # * Dark Purple
                  (128,   0,   0),  # * Brown
                  (128, 128, 255),  # * Light Blue
                  (255, 128,   0),  # * Light Orange
                  (  0,   0, 128),  # * Dark Blue
                  (128, 255,   0),  # * Light Green
                  (  0, 128, 128),  # * Turquoise
                  (142, 107,  35),  # Sienna
                  (176,   0, 255),  # Purple
                  ( 79,  47,  47),  # Indian Red
                  (255, 128, 255),  # * Pink
                  (204,  50,  50),  # Orange
                  (219, 219, 112),  # Goldenrod
                 ]

        # Define a white brush as the DC Background
        self.dc.SetBackground(wx.Brush((255, 255, 255)))
        # Clear the Image (uses the Brush)
        self.dc.Clear()

        # Draw a border around the whole bitmap
        # Set the DC Pen
        self.dc.SetPen(wx.Pen((0, 0, 0), 2, wx.SOLID))
        # Draw an outline around the whole graphic
        self.dc.DrawRectangle(1, 1, imgWidth - 1, imgHeight - 1)

        # Place the Title on the DC
        # Define a Font
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, False)
        # Set the Font for the DC
        self.dc.SetFont(font)
        # Set the Text Foreground Color to Black
        self.dc.SetTextForeground(wx.Colour(0, 0, 0))
        # Determine the size of the title text
        (titleWidth, titleHeight) = self.dc.GetTextExtent(title)
        # Add the Title to the Memory DC (and therefore the bitmap)
        self.dc.DrawText(title, int(imgWidth / 2.0 - titleWidth / 2.0), 10)

        # Define a Font for axis labels
        font = wx.Font(axisLabelFontSize, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, False)
        # Set the Font for the DC
        self.dc.SetFont(font)

        # Initialize the maximum values for the chart.  We need one for ALL speed values regardless of category and
        # another for accuracy values
        maxVals = {'allkeys' : 0, 'Accuracy' : 100.0}
        # For each dataLabel (model) ...
        for key in dataLabels:
            # ... for each secondary key (device) ...
            for key2 in data[key]:
                # If the secondary key already exists as a maxVals key ...
                if key2 in maxVals.keys():
                    # ... adjust the maxVal group as needed
                    maxVals[key2] = max(maxVals[key2], data[key][key2])
                # If the secondary key is not aleady a maxVals key ...
                else:
                    # ... then the first value is the maxVal for that key
                    maxVals[key2] = data[key][key2]
                # If the seconday key is NOT "Accuracy" ...
                if key2 != 'Accuracy':
                    # ... it should also be considered for the maximum value for all keys (except Accuracy)
                    maxVals['allkeys'] = max(maxVals['allkeys'], maxVals[key2])

        # Draw Axes
        # Draw an outline around the Bar Chart area with just a little extra width so it looks better
        self.dc.DrawRectangle(chartLeft - 3, chartTop, chartWidth + 6, chartHeight)
        # Get the values that should be used for the vertical axis labels
        axisValues = verticalAxisValues(maxVals['allkeys'])
        # For each axis label ...
        for x in axisValues:
            # ... draw a pip at the value
            self.dc.DrawLine(chartLeft - 8, chartTop + chartHeight - yPos(x, maxVals['allkeys']) - 1,
                             chartLeft - 3, chartTop + chartHeight - yPos(x, maxVals['allkeys']) - 1)
            # Convert the axis value to right-justified text
            axisLbl = "{0:10d}".format(x)
            # Determine the size of the axis label
            (txtWidth, txtHeight) = self.dc.GetTextExtent(axisLbl)
            # Add the text to the drawing at just the right position
            self.dc.DrawText(axisLbl, chartLeft - txtWidth - 13, int(chartTop + chartHeight - yPos(x, maxVals['allkeys']) - txtHeight / 2.0))

        # Now draw the Axis Labels for Accuracy
        # Set the Text Foreground Color
        self.dc.SetTextForeground('red')   # (color)
        # Set the DC Pen
        self.dc.SetPen(wx.Pen('red', 2, wx.SOLID))
        # Get the values that should be used for the vertical axis labels
        axisValues = verticalAxisValues(maxVals['Accuracy'])
        # For each axis label ...
        for x in axisValues:
            # ... draw a pip at the value
            self.dc.DrawLine(chartLeft + chartWidth - 5, chartTop + chartHeight - yPos(x, maxVals['Accuracy']) - 1,
                             chartLeft + chartWidth - 0, chartTop + chartHeight - yPos(x, maxVals['Accuracy']) - 1)
            # Convert the axis value to right-justified text
            axisLbl = "{0:10d}".format(x)
            # Determine the size of the axis label
            (txtWidth, txtHeight) = self.dc.GetTextExtent(axisLbl)
            # Add the text to the drawing at just the right position
            self.dc.DrawText(axisLbl, chartLeft + chartWidth - txtWidth - 6, int(chartTop + chartHeight - yPos(x, maxVals['Accuracy']) - txtHeight / 2.0))

        # For Testing of Colors
        if False:
            # Create a wx.ColourDatabase object
            cdb = wx.ColourDatabase()
            # Define initial text position variables
            xPosTmp = 75
            yPosTmp = 55
            # For each color defined above ...
            for color in colors:
                # ... get the Red, Green, and Blue values for the color
                (r, g, b) = color
                # ... create a wx.Colour()
                clr = wx.Colour((r, g, b))
                # ... look up the color's name in the ColourDatabase, if one has been defined
                clrName = cdb.FindName(clr)
                # ... build a string that provides color information
                stTmp = '{0:3} {1:3} {2:3} - {3}'.format(r, g, b, clrName)
                # ... set the DC text color
                self.dc.SetTextForeground(clr)
                # ... display the color information
                self.dc.DrawText(stTmp, xPosTmp, yPosTmp)
                # ... increwment the y position
                yPosTmp += 17

        # We need to remember the last value place to draw lines from one value to the next.
        # Initialize a variable to remember the last value place for each device
        lastVals = {}
        # Initialize a horizontal category counter
        counter = 0
        # Go through the data labels in reverse order 
        for key in sorted(list(data[dataLabels[0]].keys()), reverse = True):
            # Initialize the lastVals dictionary for each key
            lastVals[key] = {'val' : 0,
                             'color' : colors[counter]}
            # Print line labels
            # Set the Text Foreground Color
            self.dc.SetTextForeground(lastVals[key]['color'])
            # Set the DC Pen
            self.dc.SetPen(wx.Pen(lastVals[key]['color'], 2, wx.SOLID))
            # Set the Brush color to the color to be used for the bar
            self.dc.SetBrush(wx.Brush('blue'))
            # Define a bold font
            font = wx.Font(axisLabelFontSize + 2, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD, False)
            # Set the Font for the DC
            self.dc.SetFont(font)
            # Add the text to the drawing at just the right position
            self.dc.DrawText(key, chartLeft + 5, int(chartTop + chartHeight - (counter + 1) * (yPos(6, maxVals['Accuracy']) - txtHeight / 2.0)))
            # Define a normal font
            font = wx.Font(axisLabelFontSize, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, False)
            # Set the Font for the DC
            self.dc.SetFont(font)
            # Increment the counter
            counter += 1

        # For each category in the chart ...
        for x in range(numCategories):
            # Set the DC Pen
            self.dc.SetPen(wx.Pen('black', 2, wx.SOLID))
            # ... draw the pips for the category labels
            self.dc.DrawLine(xPos(x), chartTop + chartHeight, xPos(x), int(chartTop + chartHeight + 3))

            # Label the categories
            # Set the Text Foreground Color
            self.dc.SetTextForeground('black')   # (color)
            # Get the size of the category label
            (txtWidth, txtHeight) = self.dc.GetTextExtent(dataLabels[x])
            # Add the category label to the chart
            self.dc.DrawRotatedText(dataLabels[x], int(xPos(x) + (txtHeight / 2.0)), chartTop + chartHeight + 10, 270)

            # For each category ...
            for key in lastVals.keys():
                # "Accuracy" and time values use different scales, so we calculate the position differently
                if 'Accuracy' in key:
                    # Get the value using the Accuracy max
                    val = chartTop + chartHeight - yPos(data[dataLabels[x]][key], maxVals['Accuracy'])
                else:
                    # For each data key within the data ...
                    if key in data[dataLabels[x]].keys():
                        # Get the value using the max for all non-accuracy values
                        val = chartTop + chartHeight - yPos(data[dataLabels[x]][key], maxVals['allkeys'])
                    # If the key isn't present, the value is also not present.
                    else:
                        val = 0
                                
                # Set the DC Pen
                self.dc.SetPen(wx.Pen(lastVals[key]['color'], 3, wx.SOLID))
                # Set the Brush color to the color to be used for the bar
                self.dc.SetBrush(wx.Brush('blue'))

                # Draw a small filled square (rectangle) as the point marker
                self.dc.DrawRectangle(int(xPos(x)),
                                      val - 3,
                                      6,
                                      6)
                # If there is a non-0 last value ...
                if lastVals[key]['val'] > 0:
                    # ... craw a line from the last value to the current value
                    self.dc.DrawLine(int(xPos(x - 1) + 2),
                                     lastVals[key]['val'],
                                     int(xPos(x) + 2),
                                     val)
                # Update the last value with the current value
                lastVals[key]['val'] = val

    def GetBitmap(self):
        """ Provide the Bitmap to the calling routine """
        # Return the Bitmap object as applied 
        return self.bitmap

# Stand-alone Testing of the Graph Creation
if __name__ == '__main__':
    
    class TestFrame(wx.Frame):
        """ Test Frame for stand-alone testing """
        def __init__(self,parent,title):
            # Create a main frame
            wx.Frame.__init__(self,parent,title=title,size=(1300,1000))
            # Create a Sizer
            s1 = wx.BoxSizer(wx.HORIZONTAL)
            # Add a RichTextCtrl
            self.txt = richtext.RichTextCtrl(self, -1)
            # Put the RichTextCtrl on the Sizer
            s1.Add(self.txt, 1, wx.EXPAND)
            # Set the main sizer
            self.SetSizer(s1)
            # Lay out the window
            self.Layout()
            # Set auto-layout
            self.SetAutoLayout(True)
            # Add some space at the top
            self.txt.AppendText('\n\n')

            # Create a test title and some hard-coded test data
            title = "Faster Whisper Processing Speeds"
            data = {
                      'Tiny' : {'CPU' : 1.78,
                                'GPU' : 1.27,
                                'Accuracy' : 94.12
                               },
                      'Base' : {'CPU' : 4.10,
                                'GPU' : 1.05,
                                'Accuracy' : 93.14
                               },
                      'Small' : {'CPU' : 8.97,
                                 'GPU' : 1.90,
                                 'Accuracy' : 93.14
                                },
                      'Medium' : {'CPU' : 27.68,
                                  'GPU' : 3.91,
                                  'Accuracy' : 96.00
                                 },
                      'Medium' : {'CPU' : 27.68,
                                  'GPU' : 3.91,
                                  'Accuracy' : 96.00
                                 },
                      'Large' : {'CPU' : 50.74,
                                 'GPU' : 131.77,
                                 'Accuracy' : 92.23
                                 },
                      'Large-v1' : {'CPU' : 51.70,
                                    'GPU' : 156.87,
                                    'Accuracy' : 96.00
                                 },
                      'Large-v2' : {'CPU' : 52.49,
                                    'GPU' : 123.38,
                                    'Accuracy' : 97.03
                                 },
                      'Large-v3' : {'CPU' : 52.50,
                                    'GPU' : 140.59,
                                    'Accuracy' : 92.23
                                 }
                   }

            # Draw the chart.
            bc1 = ChartGraphic(title, data)
            # Get the Bitmap
            bitmap1 = bc1.GetBitmap()
            # Place the graphic in the Report.
            self.txt.WriteImage(bitmap1.ConvertToImage())

    # Initialize the App when in stand-alone mode
    app = wx.App()
    frame = TestFrame(None, "Chart in RichTextCtrl")
    frame.Show()
    app.MainLoop()
