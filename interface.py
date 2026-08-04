import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import data_analysis
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import os


class GUI():

    def __init__(self):
        # define basic window constants
        self.window = tk.Tk()
        self.window.title("Graphite Contrast Calculation")
        self.window.geometry("1500x1200")
        self.main_frame = tk.LabelFrame(self.window, text="main_frame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # define widgets and frame
        self.widgets_frame = tk.LabelFrame(self.main_frame, text="widgets_frame")
        self.widgets_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.filebutton = tk.Button(self.widgets_frame, text="Open Arw File",
                                    font=("Arial", 16), command=self.selectfile)
        self.filebutton.pack()
        # A reminder for user
        self.reminder = tk.Label(self.widgets_frame, text="FIRST RECTANGLE HAS TO BE " \
                                                          "INSIDE GRAPHITE", font=("Arial", 16))
        self.reminder.pack()

        # define frame for histrogram,also three choices of histogram
        self.histo_frame = tk.LabelFrame(self.main_frame, text="histo_frame")
        self.histo_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.channel_var = tk.StringVar(value="red")
        tk.Radiobutton(self.histo_frame, text="red", variable=self.channel_var,
                       value="red", command=self.update_histogram).pack()
        tk.Radiobutton(self.histo_frame, text="green", variable=self.channel_var,
                       value="green", command=self.update_histogram).pack()
        tk.Radiobutton(self.histo_frame, text="blue", variable=self.channel_var,
                       value="blue", command=self.update_histogram).pack()
        # Make histogram figure with matplotlib
        self.fig = Figure(figsize=(3, 2))
        self.ax = self.fig.add_subplot()
        self.histo_canvas = FigureCanvasTkAgg(self.fig, master=self.histo_frame)
        self.histo_canvas.get_tk_widget().pack()

        # Make a combobox for different types of intensity contrast calculation
        self.calc_combobox = ttk.Combobox(self.histo_frame, state="readonly", values=["Full Mean Contrast Calculation",
                                                                                      "Mid 80% Intensity Contrast Calculation"])
        self.calc_combobox.current(1)
        self.calc_combobox.pack(side=tk.TOP)
        # bind a function with combo selection
        self.calc_combobox.bind("<<ComboboxSelected>>", self.calculation_method)
        self.calc_method = "Mid 80% Intensity Contrast Calculation"

        # Method to pick roi
        self.roi_combobox = ttk.Combobox(self.histo_frame, state="readonly", values=["Line", "Polygon"])
        self.roi_combobox.current(1)
        self.roi_combobox.pack(side=tk.TOP)
        self.roi_combobox.bind("<<ComboboxSelected>>", self.roi_method)
        self.the_roi_method = "Polygon"

        # -----------------------------------------
        self.table_buttons_frame = tk.Frame(self.histo_frame)
        self.table_buttons_frame.pack(pady=(10, 5))

        # Add button (+)
        self.record_button = tk.Button(self.table_buttons_frame, text="+", font=("Arial", 12, "bold"),
                                       command=self.record_data, width=3)
        self.record_button.pack(side=tk.LEFT, padx=5)

        # Delete button
        self.delete_button = tk.Button(self.table_buttons_frame, text="-", font=("Arial", 12, "bold"),
                                       command=self.delete_row, width=3)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # Save button
        self.save_button = tk.Button(self.table_buttons_frame, text="Save", font=("Arial", 12),
                                     command=self.save_table)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Load button
        self.load_button = tk.Button(self.table_buttons_frame, text="Load", font=("Arial", 12),
                                     command=self.load_table)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Create Treeview for the table
        columns = ("Filename", "R_Contrast", "G_Contrast", "B_Contrast")
        self.tree = ttk.Treeview(self.histo_frame, columns=columns, show="headings", height=10)

        self.tree.heading("Filename", text="File Name")
        self.tree.heading("R_Contrast", text="Red")
        self.tree.heading("G_Contrast", text="Green")
        self.tree.heading("B_Contrast", text="Blue")

        self.tree.column("Filename", width=120, anchor=tk.CENTER)
        self.tree.column("R_Contrast", width=70, anchor=tk.CENTER)
        self.tree.column("G_Contrast", width=70, anchor=tk.CENTER)
        self.tree.column("B_Contrast", width=70, anchor=tk.CENTER)

        self.tree.pack(fill=tk.X, padx=5, pady=5)

        self.scatter_button = tk.Button(self.histo_frame, text="Scatter Point Plot", font=("Arial", 12),
                                        command=self.plot_scatter)
        self.scatter_button.pack(pady=(0, 10))
        # -----------------------------------------------------

        # frame and canvas for displaying the image
        self.image_frame = tk.LabelFrame(self.main_frame, text="image_frame")
        self.image_frame.pack(side=tk.LEFT, anchor=tk.NW)
        self.canvas = tk.Canvas(self.image_frame, width=1000, height=1000)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # StringVar and labels to show RGB contrast
        self.red_contrast_var = tk.StringVar(value=None)
        self.blue_contrast_var = tk.StringVar(value=None)
        self.green_contrast_var = tk.StringVar(value=None)
        self.red_contrast_label = tk.Label(self.widgets_frame, textvariable=(self.red_contrast_var),
                                           font=('Arial', 12))
        self.blue_contrast_label = tk.Label(self.widgets_frame, textvariable=(self.blue_contrast_var),
                                            font=('Arial', 12))
        self.green_contrast_label = tk.Label(self.widgets_frame, textvariable=(self.green_contrast_var),
                                             font=('Arial', 12))
        self.red_contrast_label.pack()
        self.blue_contrast_label.pack()
        self.green_contrast_label.pack()

        self.current_arw = None  # place holder for current arw
        self.current_line_id = None  # place holder for current line id
        self.lines = []  # to record the lines'id
        self.rois = []  # to record current two lines' coordinates
        self.file_path = None  # Place holder for fild_path
        self.points = []  # place holder for polygon points
        self.polygon_id = []  # place holder for polygon ids
        self.current_polygon_id = None  # current polygon id, the one is drawing
        self.oval_ids = []  # points for drawing the polygon

    # Select file and transfer the file path into arwfile class in data_analysis
    def selectfile(self):
        file_path = filedialog.askopenfilename(filetypes=[("ARW files", "*.ARW")])
        if file_path:
            self.file_path = file_path
            # clear everything before using a new arwfile
            self.canvas.delete("all")
            if self.current_arw is not None:
                self.cleareverything()
            self.current_arw = data_analysis.arwfile(self.file_path)
            self.show_image()

    # show rbg image on tkinter interface
    def show_image(self):
        image = Image.fromarray(self.current_arw.rgb_image)
        # canvas_width = self.canvas.winfo_width()
        # canvas_height = self.canvas.winfo_height()
        image.thumbnail((800, 600))
        self.photo = ImageTk.PhotoImage(image)
        # grab x,y dimensions from canvas image display size
        self.display_width, self.display_height = image.size
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        self.change_roi_method()

    # Functions to pick roi and draw line
    def start_roi(self, event):

        # clean the previous two lines before pick new roi
        if len(self.lines) >= 2:
            self.cleareverything()
        self.start_x = event.x
        self.start_y = event.y
        self.current_line_id = self.canvas.create_line(self.start_x, self.start_y,
                                                       self.start_x, self.start_y, fill="red", width=2, tags="roi")

    def drag_roi(self, event):
        # update line size
        self.canvas.coords(self.current_line_id, self.start_x, self.start_y, event.x, event.y)

    def end_roi(self, event):
        # canvas coordinates to raw_data coordinates
        y_scale = self.current_arw.raw_data.shape[0] / self.display_height
        x_scale = self.current_arw.raw_data.shape[1] / self.display_width
        x1 = self.start_x * x_scale
        x2 = event.x * x_scale
        y1 = self.start_y * y_scale
        y2 = event.y * y_scale

        roi = [x1, y1, x2, y2]
        self.rois.append(roi)
        self.lines.append(self.current_line_id)

        self.start_x = None
        self.start_y = None
        self.current_line_id = None

        # call data anaylsis to calculate light intensity, call show histogram function
        if len(self.lines) >= 2:
            self.current_arw.line_analysis(self.rois, self.calc_method)

            self.red_contrast_var.set(f"Red_Contrast:{self.current_arw.red_contrast}")
            self.blue_contrast_var.set(f"Blue_Contrast:{self.current_arw.blue_contrast}")
            self.green_contrast_var.set(f"Green_Contrast:{self.current_arw.green_contrast}")

            self.update_histogram()

    # Function to pick the method of calculation according to the variable in combobox
    def calculation_method(self, event):
        self.calc_method = self.calc_combobox.get()

    # Functions for picking roi by polygon,reocrd the picked points
    def left_click(self, event):

        if len(self.rois) >= 2:
            # clear polygon, points..etc before draw a new set of rois
            for r in self.oval_ids:
                self.canvas.delete(r)
            self.canvas.delete("roi")
            self.cleareverything()

        self.points.append((event.x, event.y))
        r = 1  # radius of the small circle
        # make a small circle to show the point that the user picked
        oval_id = self.canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r, fill="yellow")
        self.oval_ids.append(oval_id)

    # finishing polygon by connect the current point to first point
    def finish_polygon(self, event):
        # Incase the user mis-clicked before having enough points
        # Create Polygon requires at least three points
        if len(self.points) < 3:
            return

        # create a polygon with points user clicked
        self.current_polygon_id = self.canvas.create_polygon(self.points,
                                                             outline="red", fill='', width=2, tags="roi")
        self.oval_ids.append(self.current_polygon_id)

        y_scale = self.current_arw.raw_data.shape[0] / self.display_height
        x_scale = self.current_arw.raw_data.shape[1] / self.display_width
        # analysis the points in self.points by right scale
        new_points = []  # place holder for raw_data coordinate points
        for x, y in self.points:
            # transfer the x and y recorded by polygon to raw_data coordinate points
            x_new = np.round(x * x_scale)
            y_new = np.round(y * y_scale)
            new_points.append((x_new, y_new))

        self.rois.append(new_points)
        self.points.clear()

        if len(self.rois) == 2:
            self.current_arw.polygon_analysis(self.rois, self.calc_method)

            self.red_contrast_var.set(f"Red_Contrast:{self.current_arw.red_contrast}")
            self.blue_contrast_var.set(f"Blue_Contrast:{self.current_arw.blue_contrast}")
            self.green_contrast_var.set(f"Green_Contrast:{self.current_arw.green_contrast}")

            self.update_histogram()

    # Function to pick a method to pick roi
    # Bind events on functions for picking roi on the canvas, depending on which methods
    def roi_method(self, event):
        for r in self.oval_ids:
            self.canvas.delete(r)
        self.canvas.delete("roi")
        self.the_roi_method = self.roi_combobox.get()
        # clear stored roi data and intensities so old data doesn't leak into the new method
        if self.current_arw is not None:
            self.cleareverything()

        # clear the histogram plot itself
        self.ax.clear()
        self.histo_canvas.draw()

        # clear the contrast labels too, since they reference the old ROI's results
        self.red_contrast_var.set("")
        self.blue_contrast_var.set("")
        self.green_contrast_var.set("")

        self.the_roi_method = self.roi_combobox.get()
        self.change_roi_method()

    def change_roi_method(self):

        # unbind all the buttons before chaning method
        for seq in ("<Button-1>", "<B1-Motion>", "<ButtonRelease-1>", "<Button-2>", "<Button-3>"):
            self.canvas.unbind(seq)

        if self.the_roi_method == "Line":

            self.canvas.bind("<Button-1>", self.start_roi)
            self.canvas.bind("<B1-Motion>", self.drag_roi)
            self.canvas.bind("<ButtonRelease-1>", self.end_roi)

        elif self.the_roi_method == "Polygon":

            self.canvas.bind("<Button-1>", self.left_click)
            self.canvas.bind("<Button-2>", self.finish_polygon)
            self.canvas.bind("<Button-3>", self.finish_polygon)

    # Function to make histogram with matplotlib
    def show_histogram(self, channel):

        # clear the previous histogram before updating new one
        self.ax.clear()
        # The "0" list is the sample value list and "1" list is background value list
        if channel == "red":
            data1 = self.current_arw.intensities["red"][0]
            data2 = self.current_arw.intensities["red"][1]
            color = "red"
            title = "Red Histogram"
        elif channel == "blue":
            data1 = self.current_arw.intensities["blue"][0]
            data2 = self.current_arw.intensities["blue"][1]
            color = "blue"
            title = "Blue Histogram"
        elif channel == "green":
            data1 = self.current_arw.intensities["green"][0]
            data2 = self.current_arw.intensities["green"][1]
            color = "green"
            title = "Green Histogram"

        # histogram information
        self.ax.hist(data1, bins=50, alpha=0.5, color=color, label="Sample")
        self.ax.hist(data2, bins=50, alpha=0.8, color=color, label="Background")
        self.ax.set_title(title)
        self.ax.legend()
        self.histo_canvas.draw()

    # Function to update historgram
    def update_histogram(self):
        if self.file_path is not None:
            channel = self.channel_var.get()
            self.show_histogram(channel)

    def record_data(self):
        if self.file_path is None or len(self.rois) < 2:
            return

        filename = os.path.basename(self.file_path)
        r_val = f"{self.current_arw.red_contrast:.4f}"
        g_val = f"{self.current_arw.green_contrast:.4f}"
        b_val = f"{self.current_arw.blue_contrast:.4f}"

        self.tree.insert("", tk.END, values=(filename, r_val, g_val, b_val))

    def delete_row(self):
        # NOTE: self.tree.selection() returns a tuple of selected item IDs.
        selected_items = self.tree.selection()
        for item in selected_items:
            self.tree.delete(item)

    def save_table(self):
        # NOTE: Opens a save dialog, iterates over the tree, and writes out tab-delimited values.
        save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if save_path:
            with open(save_path, "w") as file:
                for row_id in self.tree.get_children():
                    row_data = self.tree.item(row_id)["values"]
                    # Convert items to strings and join them with a tab character
                    line = "\t".join([str(val) for val in row_data])
                    file.write(line + "\n")

    def load_table(self):
        # NOTE: Opens a load dialog, clears the current table, and populates it from the text file.
        load_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if load_path:
            # Clear existing data in the table first so we don't duplicate it
            for item in self.tree.get_children():
                self.tree.delete(item)

            with open(load_path, "r") as file:
                for line in file:
                    line = line.strip()
                    if line:  # Skip empty lines
                        values = line.split("\t")
                        self.tree.insert("", tk.END, values=values)

    def plot_scatter(self):
        # NOTE: Gather all data from the Treeview
        r_vals, g_vals, b_vals = [], [], []

        for row_id in self.tree.get_children():
            row_data = self.tree.item(row_id)["values"]
            try:
                # Assuming index 1=Red, 2=Green, 3=Blue
                r_vals.append(float(row_data[1]))
                g_vals.append(float(row_data[2]))
                b_vals.append(float(row_data[3]))
            except (ValueError, IndexError):
                # Skip any rows that might be formatted incorrectly
                continue

                # Prevent crashing if the table is empty
        if not r_vals:
            print("No data available to plot.")
            return

        # NOTE: Create a new detached window specifically for the plot
        plot_window = tk.Toplevel(self.window)
        plot_window.title("Contrast Scatter Plot")
        plot_window.geometry("500x400")

        # Create Matplotlib figure
        fig = Figure(figsize=(5, 4))
        ax = fig.add_subplot()

        # NOTE: X-axis acts as categorical labels. Using lists of strings identical to the length of data
        # aligns all the red contrast values under 'R', green under 'G', and blue under 'B'.
        ax.scatter(["R"] * len(r_vals), r_vals, color='red', alpha=0.6, label="Red")
        ax.scatter(["G"] * len(g_vals), g_vals, color='green', alpha=0.6, label="Green")
        # For better visibility against white backgrounds, 'blue' is standard, but you could adjust hex colors
        ax.scatter(["B"] * len(b_vals), b_vals, color='blue', alpha=0.6, label="Blue")

        ax.set_title("RGB Contrast Distribution")
        ax.set_ylabel("Contrast Value")

        # Adds a grid just on the Y axis to make it easier to read values across categories
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)

        # Embed the plot into the new Tkinter Toplevel window
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    # function to clear everything
    def cleareverything(self):
        self.current_arw.mean_blue.clear()
        self.current_arw.mean_red.clear()
        self.current_arw.mean_green.clear()
        self.lines.clear()
        self.points.clear()
        self.oval_ids.clear()
        self.canvas.delete("roi")
        self.rois.clear()
        for i in self.current_arw.intensities.values():
            for j in i:
                j.clear()

    def execute(self):
        self.window.mainloop()
