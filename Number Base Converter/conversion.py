import tkinter as tk
from tkinter import ttk
import json


current_language = '中文'
# 进制下拉框索引基数
current_base_index = 2


def load_language(lang):
    with open(f"languages/{lang}.json", "r", encoding="utf-8") as f:
        return json.load(f)


LANGUAGES = {
    'English': load_language('English'),
    '中文': load_language('Chinese'),
    'Customized ':load_language('Customized')
}


# 窗口居中
def center_window(window):
    # 更新窗口，并得到窗口的尺寸
    window.update_idletasks()

    # 获取屏幕的宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 获取窗口的宽度和高度
    width = window.winfo_width()
    height = window.winfo_height()

    # 计算窗口的起始坐标
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # 设置窗口的位置
    window.geometry(f'{width}x{height}+{x}+{y}')


def switch_language():
    global current_language
    global current_base_index

    current_base_index = base_from_combobox.current()  # 获取当前基数的索引
    current_language = language_combobox.get()
    update_language()  # 更新语种


def update_language():
    # 更新进制下拉框的提示信息
    base_from_combobox['values'] = LANGUAGES[current_language]['bases']

    # 使用保存的索引来设置新语言的基数
    base_from_combobox.current(current_base_index)  # 使用先前保存的索引来设置新基数

    root.title(LANGUAGES[current_language]['window_title'])  # 更新窗口名称
    convert()  # 转换并更新结果


def convert(event=None):
    try:
        value = str(entry.get())
        base_from = base_from_combobox.get()

        if base_from == LANGUAGES[current_language]['bases'][0]:
            value_decimal = int(value, 2)
        elif base_from == LANGUAGES[current_language]['bases'][1]:
            value_decimal = int(value, 8)
        elif base_from == LANGUAGES[current_language]['bases'][2]:
            value_decimal = int(value)
        elif base_from == LANGUAGES[current_language]['bases'][3]:
            value_decimal = int(value, 16)
        else:
            result_var.set(LANGUAGES[current_language]['invalid_base'])
            return

        labels = LANGUAGES[current_language]['output_labels']
        result_content = (
            f"{labels['binary']}{bin(value_decimal)[2:]}\n"
            f"{labels['octal']}{oct(value_decimal)[2:]}\n"
            f"{labels['decimal']}{value_decimal}\n"
            f"{labels['hexadecimal']}{hex(value_decimal)[2:].upper()}"
        )

        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, result_content)
        result_text.config(state=tk.DISABLED)
    except ValueError:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, LANGUAGES[current_language]['invalid_input'])
        result_text.config(state=tk.DISABLED)


root = tk.Tk()
root.title(LANGUAGES[current_language]['window_title'])
root.geometry('400x200')
root.withdraw()


# 切换语言的下拉框
language_combobox = ttk.Combobox(root, values=list(LANGUAGES.keys()), state="readonly")
language_combobox.set(current_language)
language_combobox.pack(pady=10)
language_combobox.bind("<<ComboboxSelected>>", lambda e: switch_language())

# 创建一个框架来组合进制选择和输入框
input_frame = ttk.Frame(root)
input_frame.pack(pady=10)

base_from_combobox = ttk.Combobox(input_frame, values=LANGUAGES[current_language]['bases'], state="readonly")
base_from_combobox.set(LANGUAGES[current_language]['bases'][2])  # 设置默认值为当前语言的"十进制"
base_from_combobox.grid(row=0, column=0, padx=5)

entry = ttk.Entry(input_frame)
entry.grid(row=0, column=1, padx=5)
# 绑定<KeyRelease>事件到convert函数
entry.bind("<KeyRelease>", convert)

# 绑定事件到convert函数，当进制更改时重新计算结果
base_from_combobox.bind("<<ComboboxSelected>>", convert)

result_var = tk.StringVar()
result_text = tk.Text(root, height=5, width=40, wrap=tk.WORD, state=tk.DISABLED)  # 设置初试大小并禁用编辑
result_text.pack(pady=10)

update_language()  # 要在result_text创建之后再调用

center_window(root)
root.deiconify()
root.mainloop()
