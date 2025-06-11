import numpy as np
import re, time, pywt
from scipy.interpolate import CubicSpline, Rbf
from scipy.fft import fft, fftfreq, ifft
from decimal import Decimal
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from second_window import SecondWindow

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
    
    try:
        # file1 = open(path_to_file, "r")
        # reader = csv.reader(file1)
        # return list(reader)
        file1 = open(path_to_file, "r")
        lines = file1.readlines()
        
        lines_of_traces = []
        for line in lines:
            if len(line) > 2:
                lines_of_traces.append(line.replace('\x00', ''))
                
        file1.close
        return lines_of_traces
    
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Произошла ошибка! Файл не найдет.")

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
    threshold = tk_threshold.get()
    len_trace = len(traces[0].split(',')) - 3
    begin = tk_begin.get()
    
    end = 0
    if tk_end.get() == 0:
        end = len_trace
    else:
        end = tk_end.get()
            
    if len(threshold) == 0:
        if method_interpolation == "Фурье":
            threshold = end / 10
        if method_interpolation == "Адаптивная интерполяция":
            threshold = 0.25
        if method_interpolation == "Вейвлет":
            threshold = "db16"

    for trace in traces:
        l = trace.split(',')
        t = l.pop(0)
        time_it_trace = l.pop(-2)
        last_element.append(l.pop(-1))
        l_float_full = [float(item) for item in l]
        l_float = [float(l[item]) for item in range (begin, end)]
        y_t = []
        
        if method_interpolation == "Вейвлет":
            cs = pywt.wavedec(np.array(l_float), threshold)
                
            # Пороговая обработка (удаление шума)
            sigma = [np.median(np.abs(c)) / 0.6745 for c in cs[1:]]
            # Универсальный порог
            threshold_t = [s * np.sqrt(2 * np.log(len(c))) for s, c in zip(sigma, cs[1:])]

            cs_thresh = [cs[0]] + [pywt.threshold(c, th, mode='soft') for c, th in zip(cs[1:], threshold_t)]

            # Восстановление сигнала
            y_t = pywt.waverec(cs_thresh, threshold)
        
        elif method_interpolation == "Фурье":
            threshold = float(threshold)
            fs = len(l_float)
            
            #Прямое Фурье
            y = fft(np.array(l_float))
            freqs = fftfreq(fs, 1/fs)
            
            h = np.sqrt(0.4 * (np.abs(freqs) / threshold)**2)
            window = np.hanning(len(y))
            y_filtered = y.copy() * (h - window)

            # Обратное Фурье
            y_t = np.real(ifft(y_filtered))
            
        elif method_interpolation == "CubicSpline":
            x = np.linspace(0, len(l_float) - 1, len(l_float))
            y = np.array(l_float)

            cs = CubicSpline(x, y, bc_type='natural')
                
            x_new = np.linspace(0, len(x) - 1, (len(x)*4))
            y_new = cs(x_new)
                
            for i in range(int(len(y_new)/4)):
                y_t.append((y_new[4*i] + y_new[4*i+1] + y_new[4*i+2] + y_new[4*i+3]) / 4)
                            
        else:
            x = np.linspace(0, len(l_float) - 1, len(l_float))
            y = np.array(l_float)

            cs = Rbf(x, y, function='gaussian', smooth=float(threshold))
                
            x_new = np.linspace(0, len(x) - 1, (len(x)*4))
            y_new = cs(x_new)
                
            for i in range(int(len(y_new)/4)):
                y_t.append((y_new[4*i] + y_new[4*i+1] + y_new[4*i+2] + y_new[4*i+3]) / 4)
        
        y_t = toFixed(y_t)
        l_float_full[begin:end+1] = y_t
        l_float_full = np.append(l_float_full, time_it_trace)
        l_float_full = np.insert(l_float_full, 0, int(t))
        new_array.append(l_float_full)
        
    q = ""
    for i in new_array:
        s = re.sub(r'[^0-9.o: -]', '', str(i))
        s = s.replace(" ", ", ").replace(" ,", "")
        #s = s.replace(".00", "")
        q += s + ',' + last_element[0]
        
    q += trace_time
    end_time = time.time()
    execution_time = end_time - start_time
    tk_time.set("Время выполнения функции: " + str(round(Decimal(execution_time), 2)) + " сек")
    tk_s.set(q)
    
    messagebox.showinfo("Успех", "Операция закончена.")
  
def full_inter(path_to_file, method_interpolation):
    start_time = time.time()
    traces = read_from_csv(path_to_file)
    trace_time = traces.pop()
    time_it_trace = []
    last_element = []
    new_array = []
    try:
        threshold = tk_threshold.get()
    except:
        threshold = 0
        
    for trace in traces:
        l = trace.split(',')
        t = l.pop(0)
        time_it_trace = l.pop(-2)
        last_element.append(l.pop(-1))
        y_t = []
        l_float = [float(item) for item in l]
        
        if method_interpolation == "Вейвлет":
            cs = pywt.wavedec(np.array(l_float), threshold)
            
            # Пороговая обработка (удаление шума)
            sigma = np.median(np.abs(cs[-1])) / 0.6745
            # Универсальный порог
            threshold_t = sigma * np.sqrt(2 * np.log(len(l_float)))
            cs_thresh = [pywt.threshold(c, threshold_t, mode='soft') for c in cs]

            # Восстановление сигнала
            y_t = pywt.waverec(cs_thresh, threshold)
            
        elif method_interpolation == "Фурье":
            fs = len(l_float)
            #Прямое Фурье
            y = fft(np.array(l_float))
            freqs = fftfreq(fs, 1/fs)

            # Фильтр: обнуляем частоты выше переменной threshold
            y_filtered = y.copy()
            y_filtered[np.abs(freqs) > float(threshold)] = 0

            # Обратное Фурье
            y_t = np.real(ifft(y_filtered))
        else:
            parts_trace = split_array(l_float, 8)
            
            for part in parts_trace:
                x = np.linspace(0, len(part) - 1, len(part))
                y = np.array(part)
                cs = CubicSpline(x, y, bc_type='not-a-knot')
                
                if method_interpolation == "Адаптивная интерполяция":
                    cs = Rbf(x, y, function='multiquadric', smooth=float(threshold))
                
                x_new = np.linspace(0, len(x) - 1, (len(x)*4))
                y_new = cs(x_new)
                
                for i in range(int(len(y_new)/4)):
                    y_t.append((y_new[4*i] + y_new[4*i+1] + y_new[4*i+2] + y_new[4*i+3]) / 4)
                    #y_t.append(y_new[i])
                    
        y_t = toFixed(y_t)
        y_t = np.append(y_t, time_it_trace)
        y_t = np.insert(y_t, 0, int(t))
        new_array.append(y_t)
        
    q = ""
    for i in new_array:
        s = re.sub(r'[^0-9.o: -]', '', str(i))
        s = s.replace(" ", ", ").replace(" ,", "")
        s = s.replace(".00", "").replace(".0", "")
        q += s + ',' + last_element[0]
        
    q += trace_time
    end_time = time.time()
    execution_time = end_time - start_time
    tk_time.set("Время выполнения функции: " + str(round(Decimal(execution_time), 2)) + " сек")
    tk_s.set(q)
    
    return new_array, trace_time, last_element
    
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
            messagebox.showinfo("Успех", "Файл успешно записан.")

def open_second_window():
    #s = method_interpol_var.get() + "," + str(tk_begin.get()) + "," + str(tk_end.get())
    s = method_interpol_var.get()
    # Передаем главное окно и текст из поля ввода
    SecondWindow(
        parent=root,
        initial_data=s,
        callback=update_response  # Функция для получения ответа
    )

def update_response(response_text):
    response_text_separate = response_text.split(',')
    tk_threshold.set(response_text_separate[0])
    
    if len(response_text_separate[1]) == 0:
        tk_begin.set(0)
    else:
        tk_begin.set(int(response_text_separate[1]))
    
    if len(response_text_separate[2]) == 0:
        tk_end.set(0)
    else:
        tk_end.set(int(response_text_separate[2]))   
    
# Создаем основное окно
root = tk.Tk()
root.title("Восстановление данных радарограмм")
root.geometry("600x400")

tk_new_array = ListVar()
tk_time = tk.StringVar()
tk_s = tk.StringVar()
tk_message_file_path = tk.StringVar()
tk_threshold = tk.StringVar()
tk_begin = tk.IntVar()
tk_end = tk.IntVar()

# Кнопка для выбора файла
select_button = tk.Button(root, text="Выбрать файл", command=select_file)
select_button.pack(pady=20)

# Надпись "выбранный файл"
label = ttk.Label(textvariable=tk_message_file_path, font=("Arial", 14))
#label.pack()

# Выпадающий список выбора метода интерполяции
method_interpol = ["Фурье", "Адаптивная интерполяция", "Вейвлет"]
method_interpol_var = tk.StringVar(value=method_interpol[0])
combobox = ttk.Combobox(textvariable=method_interpol_var, values=method_interpol, width=25)
combobox.pack()

# Кнопка открытия второго окна
open_second_window_button = ttk.Button(root, text="Настроить параметры для выбранного метода", command=open_second_window)
open_second_window_button.pack(pady=20)

# Кнопка для выполнения функции выбранного метода интерполяции
inter_button = tk.Button(root, text="Выполнить", command=lambda: inter_by_parts(tk_message_file_path.get(), method_interpol_var.get()))
inter_button.pack(pady=20)

label = ttk.Label(textvariable=tk_time, font=("Arial", 14))
#label.pack()

# Кнопка для записи в csv
wtite_to_csv_button = tk.Button(root, text="Записать в csv", command=lambda: save_file())
wtite_to_csv_button.pack(pady=20)

# Запускаем главный цикл
root.mainloop()