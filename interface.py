import tkinter as tk
from tkinter import filedialog
import data_analysis as analysis
from PIL import Image,ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class GUI():

    def __init__(self):
        #define basic window constants
        self.window = tk.Tk()
        self.window.title("Graphite Contrast Calculation")
        self.window.geometry("1200x900")
        self.main_frame = tk.LabelFrame(self.window,text="main_frame")
        self.main_frame.pack(fill=tk.BOTH,expand=True)

        #define widgets and frame
        self.widgets_frame = tk.LabelFrame(self.main_frame,text="widgets_frame")
        self.widgets_frame.pack(side=tk.BOTTOM,fill=tk.X)
        self.filebutton = tk.Button(self.widgets_frame,text="Open Arw File",
        font=("Arial",16),command=self.selectfile)
        self.filebutton.pack()
         #A reminder for user
        self.reminder = tk.Label(self.widgets_frame,text = "FIRST RECTANGLE HAS TO BE " \
        "INSIDE GRAPHITE",font = ("Arial",16))
        self.reminder.pack()

        #define frame for histrogram,also three choices of histogram
        self.histo_frame = tk.LabelFrame(self.main_frame,text = "histo_frame")
        self.histo_frame.pack(side=tk.RIGHT,fill=tk.Y)
        self.channel_var = tk.StringVar(value="red")
        tk.Radiobutton(self.histo_frame,text="red",variable=self.channel_var,
        value="red",command=self.update_histogram).pack(side=tk.TOP)
        tk.Radiobutton(self.histo_frame,text="green",variable=self.channel_var,
        value="green",command=self.update_histogram).pack(side=tk.TOP)
        tk.Radiobutton(self.histo_frame,text="blue",variable=self.channel_var,
        value="blue",command=self.update_histogram).pack(side=tk.TOP)
        #Make histogram figure with matplotlib
        self.fig = Figure(figsize=(3,2))
        self.ax = self.fig.add_subplot()
        self.histo_canvas = FigureCanvasTkAgg(self.fig,master=self.histo_frame)
        self.histo_canvas.get_tk_widget().pack()

        #frame and canvas for displaying the image
        self.image_frame = tk.LabelFrame(self.main_frame,text="image_frame")
        self.image_frame.pack(side=tk.LEFT,anchor=tk.NW)
        self.canvas = tk.Canvas(self.image_frame,width=1000,height=1000)
        self.canvas.pack(fill=tk.BOTH,expand=True)

        #Bind events on functions for picking roi on the canvas
        self.canvas.bind("<Button-1>", self.start_roi)
        self.canvas.bind("<B1-Motion>", self.drag_roi)
        self.canvas.bind("<ButtonRelease-1>", self.end_roi)

        #StringVar and labels to show RGB contrast
        self.red_contrast_var = tk.StringVar(value=None)
        self.blue_contrast_var = tk.StringVar(value=None)
        self.green_contrast_var = tk.StringVar(value=None)
        self.red_contrast_label = tk.Label(self.widgets_frame,textvariable=(self.red_contrast_var),
        font=('Arial',12))
        self.blue_contrast_label = tk.Label(self.widgets_frame,textvariable=(self.blue_contrast_var),
        font=('Arial',12))
        self.green_contrast_label = tk.Label(self.widgets_frame,textvariable=(self.green_contrast_var),
        font=('Arial',12))
        self.red_contrast_label.pack()
        self.blue_contrast_label.pack()
        self.green_contrast_label.pack()

        self.current_arw = None #place holder for current arw
        self.current_line_id = None #place holder for current rectangle id
        self.lines = [] #to record the lines'id
        self.rois = [] # to record current two lines' coordinates
        self.file_path = None #Place holder for fild_path

    #Select file and transfer the file path into arwfile class in data_analysis
    def selectfile(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("ARW files","*.ARW")])
        if self.file_path:
            #clear everything before using a new arwfile
            self.canvas.delete("all")
            if self.current_arw is not None:
                self.cleareverything()
            self.current_arw = analysis.arwfile(self.file_path)
            self.show_image()

    #show rbg image on tkinter interface
    def show_image(self):
        image = Image.fromarray(self.current_arw.rgb_image)
        # canvas_width = self.canvas.winfo_width()
        # canvas_height = self.canvas.winfo_height()
        image.thumbnail((800,600))
        self.photo = ImageTk.PhotoImage(image)
        #grab x,y dimensions from canvas image display size
        self.display_width,self.display_height = image.size
        self.canvas.create_image(0,0,anchor="nw",image=self.photo)
        

        
    #Functions to pick roi and draw line
    def start_roi(self,event):
        #incase user click on canvas before loading a file
        if self.current_arw is None:
            return
        #clean the previous two rectangles before pick new roi
        if len(self.lines) >= 2:
            for r in self.lines:
                self.canvas.delete(r)
            self.cleareverything()
        self.start_x = event.x
        self.start_y = event.y
        self.current_line_id = self.canvas.create_line(self.start_x,self.start_y,
                self.start_x,self.start_y,fill="red",width=2)
    def drag_roi(self,event):
        #update line size
        self.canvas.coords(self.current_line_id,self.start_x,self.start_y,event.x,event.y)
    def end_roi(self,event):
        #canvas coordinates to raw_data coordinates
        y_scale = self.current_arw.raw_data.shape[0]/self.display_height
        x_scale = self.current_arw.raw_data.shape[1]/self.display_width
        x1 = self.start_x * x_scale
        x2 = event.x * x_scale
        y1 = self.start_y * y_scale
        y2 = event.y * y_scale

        roi = [x1,y1,x2,y2]
        self.rois.append(roi)
        self.lines.append(self.current_line_id)

        self.start_x = None
        self.start_y = None
        self.current_line_id = None

        #call data anaylsis to calculate light intensity, call show histogram function
        if len(self.lines) >= 2:
            self.current_arw.mean_analysis(self.rois)
            self.current_arw.contrast_calculation()
            self.red_contrast_var.set(f"Red_Contrast:{self.current_arw.red_contrast}")
            self.blue_contrast_var.set(f"Blue_Contrast:{self.current_arw.blue_contrast}")
            self.green_contrast_var.set(f"Green_Contrast:{self.current_arw.green_contrast}")
            self.show_histogram("red")
            print("Image:", self.display_width, self.display_height)
            print("Canvas:", self.canvas.winfo_width(), self.canvas.winfo_height())


    #Function to make histogram with matplotlib
    def show_histogram(self,channel):

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

        #histogram information 
        self.ax.hist(data1,bins=50,alpha=0.5,color=color,label="Sample")
        self.ax.hist(data2,bins=50,alpha=0.8,color=color,label="Background")
        self.ax.set_title(title)
        self.ax.legend()
        self.histo_canvas.draw()

    #Function to update historgram
    def update_histogram(self):
        if self.file_path is not None:
            channel = self.channel_var.get()
            #clear the previous histogram before create changing to another color
            self.show_histogram(channel)


    #function to clear everything
    def cleareverything(self):
        self.current_arw.mean_blue.clear()
        self.current_arw.mean_red.clear()
        self.current_arw.mean_green.clear()
        self.lines.clear()
        self.rois.clear()
        for i in self.current_arw.intensities.values():
            for j in i:
                j.clear()

    def execute(self):
        self.window.mainloop()
    
