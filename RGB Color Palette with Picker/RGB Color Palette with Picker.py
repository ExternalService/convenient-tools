import tkinter as tk
from tkinter import Canvas, Scale, Label, Frame, ttk, Entry
from PIL import Image, ImageTk, ImageDraw, ImageGrab
import pyautogui
import win32api


def rgb_to_hex(rgb):
    # 将RGB值转换为十六进制颜色代码
    return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])


def hex_to_rgb(hex_color):
    # 去掉可能包含的 "#" 前缀
    hex_color = hex_color.lstrip("#")
    # 将十六进制颜色代码转换为RGB值
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b


class RGBColorPaletteWithPicker(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RGB Color Palette with Picker")
        self.geometry("800x400")
        self.setup_ui()

    def setup_ui(self):
        self.canvas_width = 256
        self.canvas_height = 256
        self.canvas = Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(pady=20, side=tk.LEFT)
        self.canvas.bind("<Motion>", self.display_rgb_value)
        self.canvas.bind("<Button-1>", self.display_selected_color)

        # 创建RGB渐变调色板，蓝色通道值默认为127
        self.gradient_image = self.create_rgb_image(self.canvas_width, self.canvas_height, 127)
        self.gradient_photo = ImageTk.PhotoImage(self.gradient_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.gradient_photo)

        # 创建蓝色通道值滚动条(23,153,255)
        self.blue_scale = Scale(self, from_=0, to=255, orient=tk.HORIZONTAL, label="Blue Channel Value", command=self.update_canvas)
        self.blue_scale.config(troughcolor=rgb_to_hex((23, 153, 255)))
        self.blue_scale.set(127)
        self.blue_scale.pack(pady=20)

        # lable标签不可复制内容，所以改为用只读输入框取代
        # self.rgb_label = Label(self, text="RGB: ")
        # self.rgb_label.pack(pady=10)

        # 动态展示鼠标在调色板内时所对应的RGB值的只读输入框
        self.rgb_entry = Entry(self, state='readonly', width=30)
        self.rgb_entry.pack(pady=10)

        self.selected_frame = Frame(self)
        self.selected_frame.pack(pady=20, side=tk.LEFT, padx=20)

        # 动态展示鼠标在调色板内时所对应的颜色的颜色条
        self.color_display_label = Label(self, text="Current Color", width=20, height=2)
        self.color_display_label.pack(pady=10, before=self.rgb_entry)

        # 展示在鼠标左键点击时获取到的颜色和像素值
        self.selected_color_label = Label(self.selected_frame, text="Selected Color", width=20, height=2)
        self.selected_color_label.pack(pady=10)

        self.selected_rgb_entry = Entry(self.selected_frame, state='readonly', width=30)
        self.selected_rgb_entry.pack(pady=10)


        self.picker_label = ttk.Label(self, text="click the botton to pick color from screen")
        self.picker_label.pack(pady=20)
        self.picker_btn = ttk.Button(self, text="pick", command=self.pick_color)
        self.picker_btn.pack(pady=5)

        self.picker_rgb_entry = Entry(self, state='readonly', width=30)
        self.picker_rgb_entry.pack(pady=10)

    # 绘制正方形调色板
    def create_rgb_image(self, width, height, blue_value):
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)

        for x in range(width):
            for y in range(height):
                r = int((x / width) * 255)
                g = int((y / height) * 255)
                b = blue_value
                draw.point((x, y), fill=(r, g, b))

        return image

    # 更新调色板
    def update_canvas(self, blue_value):
        self.gradient_image = self.create_rgb_image(self.canvas_width, self.canvas_height, self.blue_scale.get())
        self.gradient_photo = ImageTk.PhotoImage(self.gradient_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.gradient_photo)

    # 展示
    def display_rgb_value(self, event):
        if 0 <= event.x < self.canvas_width and 0 <= event.y < self.canvas_height:
            r, g, b = self.gradient_image.getpixel((event.x, event.y))
            value = f"RGB: ({r}, {g}, {b})  HEX:{rgb_to_hex((r, g, b))}"

            # 更新颜色条的背景色
            self.color_display_label.config(bg=f"#{r:02x}{g:02x}{b:02x}")

            self.rgb_entry.config(state='normal')
            self.rgb_entry.delete(0, tk.END)
            self.rgb_entry.insert(0, value)
            self.rgb_entry.config(state='readonly')
    #  def display_rgb_value(self, event):
    #     if 0 <= event.x < self.canvas_width and 0 <= event.y < self.canvas_height:
    #         r, g, b = self.gradient_image.getpixel((event.x, event.y))
    #         self.rgb_label.config(text=f"RGB: ({r}, {g}, {b})  HEX:{rgb_to_hex((r, g, b))}")

    def display_selected_color(self, event):
        if 0 <= event.x < self.canvas_width and 0 <= event.y < self.canvas_height:
            r, g, b = self.gradient_image.getpixel((event.x, event.y))
            self.selected_color_label.config(bg=f"#{r:02x}{g:02x}{b:02x}")
            value = f"RGB: ({r}, {g}, {b})  HEX:{rgb_to_hex((r, g, b))}"
            self.selected_rgb_entry.config(state='normal')
            self.selected_rgb_entry.delete(0, tk.END)
            self.selected_rgb_entry.insert(0, value)
            self.selected_rgb_entry.config(state='readonly')

    def pick_color(self):
        self.withdraw()  # hide the main window
        # Wait for a short while before capturing the color to ensure window is hidden
        self.after(100, self.capture_color)

    def capture_color(self):
        while True:
            left_button_state = win32api.GetKeyState(0x01)
            if left_button_state == -127 or left_button_state == -128:
                x, y = pyautogui.position()
                image = ImageGrab.grab(bbox=(x, y, x+1, y+1))
                color = image.getpixel((0, 0))

                value = f"RGB: ({color})  HEX:{rgb_to_hex(color)}"
                self.picker_rgb_entry.config(state='normal')
                self.picker_rgb_entry.delete(0, tk.END)
                self.picker_rgb_entry.insert(0, value)
                self.picker_rgb_entry.config(state='readonly')

                self.deiconify()
                break
            self.after(100)


app = RGBColorPaletteWithPicker()
app.mainloop()
