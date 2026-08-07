import rawpy as r
import numpy as np
from PIL import Image, ImageDraw

# black level is a constant,512
# black_level = raw.black_level_per_channel
black_level = 512


class arwfile:

    def __init__(self, file_path):

        self.file_path = file_path
        self.mean_green = []
        self.mean_red = []
        self.mean_blue = []
        self.red_contrast_list = []
        self.blue_contrast_list = []
        self.green_contrast_list = []

        self.intensities = {"red": [[], []], "blue": [[], []], "green": [[], []]}
        with r.imread(self.file_path) as raw:
            self.raw_data = raw.raw_image.copy().astype(np.float32)
            #Apply minus black level when not using a background file, minus background file automatically reduce black level
            self.corrected_data = np.maximum(self.raw_data - black_level,0)
            # self.corrected_data = self.raw_data
            self.rgb_image = raw.postprocess()

    def background_file_analysis(self,roi,background_file_path,calc_method):

        self.background_file_path = background_file_path
        with r.imread(self.background_file_path) as raw:
            self.background_raw_data = raw.raw_image.copy().astype(np.float32)
            self.background_corrected_data = np.maximum(self.background_raw_data - black_level,0)
            # self.background_corrected_data = self.background_raw_data

        if self.background_raw_data.shape != self.raw_data.shape:

            raise ValueError("Background image shape don't much main image shape")
        """Getting the shape of main picture
        Make sure the picture we are drawing with pillow has the exactly same shape, so our coordinates would be right"""
        height,width = self.raw_data.shape

        #L represent a gary picture, 0 is every value inside picture were zero
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.polygon(roi[0], outline=1, fill=1)
        # turn in the picture into a numpy array
        mask_array = np.array(mask)

        #get all the coordinates from mask_array, all the coordinates inside the polygon
        #numpy.nonzero() function returns the indices of all non-zero (or True) elements within an array.
        y_values,x_values = np.nonzero(mask_array)

        for y,x in zip(y_values,x_values):

            value = self.corrected_data[y, x]  # the light intensity value for sample
            background_value = self.background_corrected_data[y,x] #light intensity value for background
            #append both value and background_value
            if x % 2 == 0 and y % 2 == 0:
                self.intensities["red"][0].append(value)
                self.intensities["red"][1].append(background_value)
            elif x % 2 == 1 and y % 2 == 1:
                self.intensities["blue"][0].append(value)
                self.intensities["blue"][1].append(background_value)
            else:
                self.intensities["green"][0].append(value)
                self.intensities["green"][1].append(background_value)

        # Two methods of mean_contrast calculation
        if calc_method == "Full Mean Contrast Calculation" or calc_method == "Mid 80% Contrast Pixel by Pixel":
            pass
        elif calc_method == "Mid 80% Intensity Contrast Calculation":
            for channel in self.intensities:
                for i in range(0,2):
                    # transfer the list to numpy array
                    values = np.array(self.intensities[channel][i])

                    low = np.percentile(values, 10)
                    high = np.percentile(values, 90)
                    mid_80 = values[(values > low) & (values < high)]
                    # The reason convert numpy array to python list is make sure the function "cleareverything"(.clear()method) in interface moduel works fine
                    self.intensities[channel][i] = mid_80.tolist()

        self.contrast_calculation(calc_method)

    # Function to analysis data from rois,collect mean values from each channel
    def line_analysis(self, rois, calc_method):

        for i, roi in enumerate(rois):
            x1, y1, x2, y2 = roi
            # Make x,y points for the line,length is the number of points
            length = np.round(np.hypot(x2 - x1, y2 - y1)).astype(int)
            x_values = np.round(np.linspace(x1, x2, length)).astype(int)
            y_values = np.round(np.linspace(y1, y2, length)).astype(int)

            """Extract green, red and blue from each photosite,but there's maybe some
            error generated because of rounding"""
            for x, y in zip(x_values, y_values):
                value = self.corrected_data[y, x]  # the light intensity value
                # print(raw.pattern) confirmed the number to be pick up from each
                if x % 2 == 0 and y % 2 == 0:
                    self.intensities["red"][i].append(value)
                elif x % 2 == 1 and y % 2 == 1:
                    self.intensities["blue"][i].append(value)
                else:
                    self.intensities["green"][i].append(value)

            # Two methods of mean_contrast calculation
            if calc_method == "Full Mean Contrast Calculation" or calc_method == "Mid 80% Contrast Pixel by Pixel":
                pass
            elif calc_method == "Mid 80% Intensity Contrast Calculation":
                for channel in self.intensities:
                    # transfer the list to numpy array
                    values = np.array(self.intensities[channel][i])

                    low = np.percentile(values, 10)
                    high = np.percentile(values, 90)
                    mid_80 = values[(values > low) & (values < high)]
                    # The reason convert numpy array to python list is make sure the function "cleareverything"(.clear()method) in interface moduel works fine
                    self.intensities[channel][i] = mid_80.tolist()

        self.contrast_calculation(calc_method)

    # mean intensity analysis when roi pick method is rectangle
    def polygon_analysis(self, rois, calc_method):

        height, width = self.raw_data.shape

        for i,points in enumerate(rois):

            mask = Image.new("L", (width, height), 0)
            draw = ImageDraw.Draw(mask)
            draw.polygon(points, outline=1, fill=1)
            # turn in the picture into a numpy array
            mask_array = np.array(mask)

            #get all the coordinates from mask_array, all the coordinates inside the polygon
            #numpy.nonzero() function returns the indices of all non-zero (or True) elements within an array.
            y_values,x_values = np.nonzero(mask_array)

            for y,x in zip(y_values,x_values):

                value = self.corrected_data[y, x]  # the light intensity value
                # print(raw.pattern) confirmed the number to be pick up from each
                if x % 2 == 0 and y % 2 == 0:
                    self.intensities["red"][i].append(value)
                elif x % 2 == 1 and y % 2 == 1:
                    self.intensities["blue"][i].append(value)
                else:
                    self.intensities["green"][i].append(value)

            # Two calculation methods of mean_contrast calculation
            if calc_method == "Full Mean Contrast Calculation" or calc_method == "Mid 80% Contrast Pixel by Pixel":
                #Useless if statement, just to clarify
                pass
            elif calc_method == "Mid 80% Intensity Contrast Calculation":
                for channel in self.intensities:
                    # transfer the list to numpy array
                    values = np.array(self.intensities[channel][i])

                    low = np.percentile(values, 10)
                    high = np.percentile(values, 90)
                    mid_80 = values[(values > low) & (values < high)]
                    # The reason convert numpy array to python list is make sure the function "cleareverything"(.clear()method) in interface moduel works fine
                    self.intensities[channel][i] = mid_80.tolist()

        self.contrast_calculation(calc_method)



    def contrast_calculation(self,calc_method):

        if calc_method == "Mid 80% Contrast Pixel by Pixel":
            #To calculate the contrast pixel by pixel and use the mean of the contrast
            for i in range (0,len(self.intensities["red"][0])):
                red_contrast = (self.intensities["red"][0][i] - self.intensities["red"][1][i])/self.intensities["red"][1][i]
                self.red_contrast_list.append(red_contrast)
            for i in range (0,len(self.intensities["blue"][0])):
                blue_contrast = (self.intensities["blue"][0][i] - self.intensities["blue"][1][i])/self.intensities["blue"][1][i]
                self.blue_contrast_list.append(blue_contrast)
            for i in range (0,len(self.intensities["green"][0])):
                green_contrast = (self.intensities["green"][0][i] - self.intensities["green"][1][i])/self.intensities["green"][1][i]
                self.green_contrast_list.append(green_contrast)

            self.red_contrast = np.median(self.red_contrast_list)
            self.blue_contrast = np.median(self.blue_contrast_list)
            self.green_contrast = np.median(self.green_contrast_list)

            return

        for i in range(0, 2):
            self.mean_red.append(np.mean(self.intensities["red"][i]))
            self.mean_blue.append(np.mean(self.intensities["blue"][i]))
            self.mean_green.append(np.mean(self.intensities["green"][i]))

        self.red_contrast = (self.mean_red[0] - self.mean_red[1]) / self.mean_red[1]
        self.blue_contrast = (self.mean_blue[0] - self.mean_blue[1]) / self.mean_blue[1]
        self.green_contrast = (self.mean_green[0] - self.mean_green[1]) / self.mean_green[1]
