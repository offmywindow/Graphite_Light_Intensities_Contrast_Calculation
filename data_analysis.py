import rawpy as r
import numpy as np

# black level is a constant,512
# black_level = raw.black_level_per_channel
black_level = 512


class arwfile:

    def __init__(self, file_path):

        self.file_path = file_path
        self.mean_green = []
        self.mean_red = []
        self.mean_blue = []
        self.intensities = {"red": [[], []], "blue": [[], []], "green": [[], []]}
        with r.imread(self.file_path) as raw:
            self.raw_data = raw.raw_image.copy().astype(np.float32)
            self.corrected_data = np.maximum(self.raw_data - black_level, 0)
            self.rgb_image = raw.postprocess()

    # Function to analysis data from rois,collect mean values from each channel
    def mean_analysis(self, rois,method):

        for i, roi in enumerate(rois):
            x1, y1, x2, y2 = roi
            # Make x,y points for the line,length is the number of points
            length = np.round(np.hypot(x2 - x1, y2 - y1)).astype(int)
            x_values = np.round(np.linspace(x1, x2, length)).astype(int)
            y_values = np.round(np.linspace(y1, y2, length)).astype(int)

            """Extract green, red and blue from each photosite,but there's maybe some
            error generated because of rounding """
            for x, y in zip(x_values, y_values):
                value = self.corrected_data[y, x]  # the light intensity value
                # print(raw.pattern) confirmed the number to be pick up from each
                if x % 2 == 0 and y % 2 == 0:
                    self.intensities["red"][i].append(value)
                elif x % 2 == 1 and y % 2 == 1:
                    self.intensities["blue"][i].append(value)
                else:
                    self.intensities["green"][i].append(value)
            if method == "Full Mean Contrast Calculation":
                self.mean_red.append(np.mean(self.intensities["red"][i]))
                self.mean_blue.append(np.mean(self.intensities["blue"][i]))
                self.mean_green.append(np.mean(self.intensities["green"][i]))
            elif method == "Mid 80% Intensity Contrast Calculation":
                for channel in self.intensities:
                    for x in self.intensities[channel]:
                        
            

    def contrast_calculation(self):
        self.red_contrast = (self.mean_red[0] - self.mean_red[1]) / self.mean_red[1]
        self.blue_contrast = (self.mean_blue[0] - self.mean_blue[1]) / self.mean_blue[1]
        self.green_contrast = (self.mean_green[0] - self.mean_green[1]) / self.mean_green[1]


