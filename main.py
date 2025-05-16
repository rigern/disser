import pandas as pd
import numpy as np
import re, time, bezier, pywt
from scipy.interpolate import CubicSpline, RBFInterpolator, Rbf, PchipInterpolator, lagrange
from decimal import Decimal
import tkinter as tk
from tkinter import filedialog, ttk

class ListVar:
    def __init__(self):
        self._data = []

    def set(self, new_list):
        if isinstance(new_list, list):
            self._data = new_list
        else:
            raise ValueError("Только списки можно передавать!")

    def get(self):
        return self._data

    def append(self, item):
        self._data.append(item)

    def clear(self):
        self._data.clear()

def toFixed(nums):
    
    new_nums = []
    for num in nums:
        new_nums.append(round(Decimal(num), 2))
    
    return new_nums

def read_from_csv(path_to_file):
    
    file1 = open(path_to_file, "r")
    lines = file1.readlines()
    file1.close
    
    return lines

def split_array(arr, k):
    
    n = len(arr)
    part_size = n // k
    remainder = n % k
    result = []
    start = 0
    
    for i in range(k):
        end = start + part_size + (1 if i < remainder else 0)
        result.append(arr[start:end])
        start = end
    
    return result

def inter_by_parts(path_to_file, method_interpolation):
    
    start_time = time.time()
    
    traces = read_from_csv(path_to_file)
    trace_time = traces.pop()
    time_it_trace = []
    last_element = []
    new_array = []
    
    for trace in traces:
        l = trace.split(',')
        t = l.pop(0)
        time_it_trace = l.pop(-2)
        last_element.append(l.pop(-1))
        y_t = []       
        
        if method_interpolation == "DWT":
            cs = pywt.wavedec(np.array(l), 'db10')
            
            # Пороговая обработка (удаление шума)
            sigma = np.median(np.abs(cs[-1])) / 0.6745

            # Универсальный порог
            threshold = sigma * np.sqrt(2 * np.log(len(l)))
            cs_thresh = [pywt.threshold(c, threshold, mode='soft') for c in cs]

            # Восстановление сигнала
            y_t = pywt.waverec(cs_thresh, 'db10')
            
        else:
            parts_trace = split_array(l, 8)
            for part in parts_trace:
                x = np.linspace(0, len(part) - 1, len(part))
                y = np.array(part)
                        
                cs = CubicSpline(x, y, bc_type='natural')
                if method_interpolation == "Rbf":
                    cs = Rbf(x, y, function='gaussian', smooth=5)
                elif method_interpolation == "PchipInterpolator":
                    cs = PchipInterpolator(x, y)
                
                x_new = np.linspace(0, len(x), (len(x) * 4))
                y_new = cs(x_new)
                
                if method_interpolation == "bezier":
                    nodes = np.array([x, 
                                    part], dtype=float)
                    cs = bezier.Curve(nodes, degree=len(part) - 1)
                    points = cs.evaluate_multi(np.linspace(0, 1, len(part))).T
                    x_new = points[:, 0]
                    y_new = points[:, 1]
                    y_t.append(y_new)
                else:
                    for i in range(int(len(y_new)/4)):
                        y_t.append((y_new[4*i] + y_new[4*i+1] + y_new[4*i+2] + y_new[4*i+3]) / 4)
                    
        y_t = toFixed(y_t)
        y_t = np.append(y_t, time_it_trace)
        y_t = np.insert(y_t, 0, int(t))
        new_array.append(y_t)
        
    tk_new_array.set(new_array)
    tk_last_element.set(last_element)
    tk_trace_time.set(trace_time)
    
    y = tk_new_array.get()
    t_time = tk_trace_time.get()
    last_elem = tk_last_element.get()

    q = ""
    for i in y:
        s = re.sub(r'[^0-9.o: -]', '', str(i))
        s = s.replace(" ", ", ").replace(" ,", "")
        s = s.replace(".00", "").replace(".0", "")
        q += s + ',' + last_elem[0]
        
    q += t_time
    end_time = time.time()
    execution_time = end_time - start_time
    tk_time.set("Время выполнения функции: " + str(round(Decimal(execution_time), 2)) + " сек")
    tk_s.set(q)
    
    return new_array, trace_time, last_element
    
def full_inter():
    traces = read_from_csv()
    trace_time = traces.pop()
    time_it_trace = []
    last_element = []
    new_array = []
    
    for trace in traces:
        l = trace.split(',')
        t = l.pop(0)
        x = np.linspace(0, len(l) - 3, len(l) - 2)
        y = np.delete(np.array(l), [-1, -2])
        
        time_it_trace = (l[-2])
        last_element.append(l[-1])
        
        #cs = CubicSpline(x, y, bc_type='natural')
        cs = Rbf(x, y, function='multiquadric', epsilon=1.0)
        y_t = [t]
        x_new = np.linspace(0, ((len(x) * 4) - 1), (len(x) * 4))
        y_new = cs(x_new)
        y_new = toFixed(y_new)
        y_t += y_new
        y_t = np.append(y_t, time_it_trace)
        #y_new = np.append(y_new, last_element)
        
        new_array.append(y_t)
        
    return new_array, trace_time, last_element

def write_to_csv():
    
    y = tk_new_array.get()
    t_time = tk_trace_time.get()
    last_elem = tk_last_element.get()
    #file1 = open("src/inter_by_parts.csv", "w")

    q = ""
    for i in y:
        s = re.sub(r'[^0-9.o: -]', '', str(i))
        s = s.replace(" ", ", ")
        s = s.replace(" ,", "")
        s = s.replace(".00", "").replace(".0", "")
        q += s + ',' + last_elem[0]
        #file1.write(s + "," + last_elem[0])
        
    q += t_time
    tk_s.set(q)
    #file1.write(t_time)
    #file1.close()
    

def select_file():
    
    file_path = filedialog.askopenfilename(
        title="Выберите файл",
        filetypes=(("CSV файлы", "*.csv"), ("Все файлы", "*.*"))
    )
    if file_path:
        tk_message_file_path.set(file_path)
        
def save_file():
    
    file_path = filedialog.asksaveasfilename(
        title="Сохранить файл как...",
        defaultextension=".csv",
        filetypes=(("CSV файлы", "*.csv"), ("Все файлы", "*.*"))
    )
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(tk_s.get())

# Создаем основное окно
root = tk.Tk()
root.title("Интерполяция георадарограмм")
root.geometry("600x400")

tk_new_array = ListVar()
tk_last_element = ListVar()
tk_time = tk.StringVar()
tk_trace_time = tk.StringVar()
tk_s = tk.StringVar()
tk_message_file_path = tk.StringVar()
# Кнопка для выбора файла
select_button = tk.Button(root, text="Выбрать файл", command=select_file)
select_button.pack(pady=20)

# Надпись "выбранный файл"
label = ttk.Label(textvariable=tk_message_file_path, font=("Arial", 14))
#label.pack()

# Выпадающий список выбора метода интерполяции
method_interpol = ["DWT", "Rbf", "PchipInterpolator", "bezier"]
method_interpol_var = tk.StringVar(value=method_interpol[0])
combobox = ttk.Combobox(textvariable=method_interpol_var, values=method_interpol)
combobox.pack()

# Кнопка для выполнения функции выбранного метода интерполяции
inter_button = tk.Button(root, text="Выполнить", command=lambda: inter_by_parts(tk_message_file_path.get(), method_interpol_var.get()))
inter_button.pack(pady=20)

label = ttk.Label(textvariable=tk_time, font=("Arial", 14))
label.pack()

# Кнопка для записи в csv
wtite_to_csv_button = tk.Button(root, text="Записать в csv", command=lambda: save_file())
wtite_to_csv_button.pack(pady=20)

# Запускаем главный цикл
root.mainloop()
