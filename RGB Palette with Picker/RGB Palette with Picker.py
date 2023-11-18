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
        self.geometry("1000x400")
        # 使用 grid 布局替代 pack 布局
        # 设置 grid 布局的列配置，使两列具有相同的宽度
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        self.canvas_width = 256
        self.canvas_height = 256
        self.canvas = Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        self.canvas.bind("<Motion>", self.display_palette_color)
        self.canvas.bind("<Button-1>", self.display_selected_color)

        # 创建RGB渐变调色板，蓝色通道值默认为127
        self.gradient_image = self.create_rgb_palette(self.canvas_width, self.canvas_height, 127)
        self.gradient_photo = ImageTk.PhotoImage(self.gradient_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.gradient_photo)

        # 创建蓝色通道值滚动条(23,153,255)
        self.blue_scale = Scale(self, from_=0, to=255, orient=tk.HORIZONTAL, label="Blue Channel", command=self.update_canvas)
        self.blue_scale.config(troughcolor=rgb_to_hex((23, 153, 255)))  # 滚动条底色
        self.blue_scale.set(127)  # 默认值
        self.blue_scale.grid(row=1, column=0, padx=10, pady=10, sticky='ns')

        # self.rowconfigure(0, pad=0)  # 设置第一行的额外垂直空间为 0
        # self.rowconfigure(1, pad=0)  # 设置第二行的额外垂直空间为 0

        # 动态展示鼠标所对应的调色板RGB值(只读输入框)
        self.palette_color_entry = Entry(self, state='readonly', width=30)
        self.palette_color_entry.grid(row=1, column=1, padx=10, pady=2, sticky='ns')

        # 动态展示鼠标所对应的调色板RGB值的颜色条
        self.palette_color_label = Label(self, text="Current Color", width=20, height=2)
        self.palette_color_label.grid(row=0, column=1, padx=10, pady=2, sticky='ns')

        # 展示鼠标左键单击选中的颜色的RGB值(只读输入框)
        self.selected_color_entry = Entry(self, state='readonly', width=30)
        self.selected_color_entry.grid(row=1, column=2, padx=10, pady=2, sticky='ns')

        # 展示在鼠标左键点击时获取到的颜色和像素值
        self.selected_color_label = Label(self, text="Selected Color", width=20, height=2)
        self.selected_color_label.grid(row=0, column=2, padx=10, pady=2, sticky='ns')

        self.picker_btn = ttk.Button(self, text="pick color from screen", command=self.pick_color)
        self.picker_btn.grid(row=0, column=3, padx=10, pady=2, sticky='ns')

        self.picked_color_entry = Entry(self, state='readonly', width=30)
        self.picked_color_entry.grid(row=1, column=3, padx=10, pady=2, sticky='ns')

        self.picked_color_label = Label(self, width=50, height=20)
        self.picked_color_label.grid(row=2, column=3, padx=10, pady=2, sticky='ns')

    # 绘制正方形调色板
    def create_rgb_palette(self, width, height, blue_value):
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        for x in range(width):
            for y in range(height):
                r = int((x / width) * 255)
                g = int((y / height) * 255)
                b = blue_value
                draw.point((x, y), fill=(r, g, b))

        return image

    # 在改变蓝色通道值后调用以更新调色板
    def update_canvas(self, blue_value):
        self.gradient_image = self.create_rgb_palette(self.canvas_width, self.canvas_height, self.blue_scale.get())
        self.gradient_photo = ImageTk.PhotoImage(self.gradient_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.gradient_photo)

    """
    更新颜色显示。
        参数:
        - event: 事件对象
        - color_label: 显示颜色的标签
        - color_entry: 显示颜色值的输入框
    """
    def update_color_display(self, event, color_label, color_entry):
        if 0 <= event.x < self.canvas_width and 0 <= event.y < self.canvas_height:
            r, g, b = self.gradient_image.getpixel((event.x, event.y))
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            value = f"RGB: ({r}, {g}, {b})  HEX:{rgb_to_hex((r, g, b))}"
            # 更新标签和输入框
            color_label.config(bg=hex_color)
            color_entry.config(state='normal')
            color_entry.delete(0, tk.END)
            color_entry.insert(0, value)
            color_entry.config(state='readonly')

    # 更新鼠标指针颜色条
    def display_palette_color(self, event):
        self.update_color_display(event, self.palette_color_label, self.palette_color_entry)

    # 更新鼠标左键点击颜色条
    def display_selected_color(self, event):
        self.update_color_display(event, self.selected_color_label, self.selected_color_entry)

    # 从屏幕取色
    def pick_color(self):
        self.withdraw()  # hide the main window
        # Wait for a short while before capturing the color to ensure window is hidden
        self.after(100, self.capture_color)

    # 从屏幕取色
    def capture_color(self):
        while True:
            left_button_state = win32api.GetKeyState(0x01)
            if left_button_state == -127 or left_button_state == -128:
                x, y = pyautogui.position()
                image = ImageGrab.grab(bbox=(x, y, x+1, y+1))
                color = image.getpixel((0, 0))

                value = f"RGB: {color}  HEX:{rgb_to_hex(color)}"
                self.picked_color_entry.config(state='normal')
                self.picked_color_entry.delete(0, tk.END)
                self.picked_color_entry.insert(0, value)
                self.picked_color_entry.config(state='readonly')

                self.deiconify()
                break
            self.after(100)


app = RGBColorPaletteWithPicker()
app.mainloop()
