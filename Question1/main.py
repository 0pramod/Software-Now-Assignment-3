import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2
import os
import numpy as np
from tkinter import messagebox

# Main class for the image editor application
class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor - Tkinter & OpenCV")

        # Variables to hold original, cropped, and resized images
        self.original_img = None
        self.tk_img = None
        self.cropped_img = None
        self.resized_img = None

        # For cropping rectangle
        self.start_x = self.start_y = self.rect = None

        # ========== Layout ==========

        # Frame for controls (buttons + slider)
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill='x', side='top')

        tk.Button(control_frame, text="Load Image", command=self.load_image).pack(side='left')
        tk.Button(control_frame, text="Save Image", command=self.save_image).pack(side='left')

        self.slider = tk.Scale(control_frame, from_=10, to=300, orient='horizontal', label='Resize %', command=self.resize_image)
        self.slider.set(100)
        self.slider.pack(side='left', padx=10)

        # Scrollable canvas frame
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg='gray')
        self.canvas.pack(side='left', fill='both', expand=True)

        # Scrollbars for canvas
        x_scroll = tk.Scrollbar(canvas_frame, orient='horizontal', command=self.canvas.xview)
        x_scroll.pack(side='bottom', fill='x')
        y_scroll = tk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        y_scroll.pack(side='right', fill='y')

        self.canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        # Bind mouse events for cropping
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    # Load an image from local computer
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        self.original_img = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
        self.display_image(self.original_img)
        self.slider.set(100)

    # Display image on canvas
    def display_image(self, img):
        img_pil = Image.fromarray(img)
        self.tk_img = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, self.tk_img.width(), self.tk_img.height()))
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_img)

    # When mouse button is pressed - start cropping
    def on_mouse_down(self, event):
        self.start_x, self.start_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    # While mouse is moving - show cropping box
    def on_mouse_drag(self, event):
        end_x, end_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, end_x, end_y)

    # When mouse button is released - finish cropping
    def on_mouse_up(self, event):
        if self.original_img is None:
            return

        x0 = int(min(self.start_x, self.canvas.canvasx(event.x)))
        y0 = int(min(self.start_y, self.canvas.canvasy(event.y)))
        x1 = int(max(self.start_x, self.canvas.canvasx(event.x)))
        y1 = int(max(self.start_y, self.canvas.canvasy(event.y)))

        self.cropped_img = self.original_img[y0:y1, x0:x1]
        self.resized_img = self.cropped_img.copy()
        self.display_image_side_by_side(self.original_img, self.cropped_img)

    # Show original and modified image side by side
    def display_image_side_by_side(self, original, cropped):
        if cropped is None:
            return

        h = max(original.shape[0], cropped.shape[0])
        w = original.shape[1] + cropped.shape[1]

        combined = 255 * np.ones((h, w, 3), dtype=np.uint8)
        combined[:original.shape[0], :original.shape[1]] = original
        combined[:cropped.shape[0], original.shape[1]:] = cropped

        self.display_image(combined)

    # Resize cropped image
    def resize_image(self, value):
        if self.cropped_img is None:
            return

        scale = int(value) / 100.0
        width = int(self.cropped_img.shape[1] * scale)
        height = int(self.cropped_img.shape[0] * scale)
        self.resized_img = cv2.resize(self.cropped_img, (width, height))
        self.display_image_side_by_side(self.original_img, self.resized_img)

    # Save the resized image
    def save_image(self):
        if self.resized_img is None:
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if not file_path:
            return

        cv2.imwrite(file_path, cv2.cvtColor(self.resized_img, cv2.COLOR_RGB2BGR))
        messagebox.showinfo("Saved", f"Image saved to {file_path}")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()
