import tkinter as tk
from tkinter import ttk
import re

class SecondWindow:
    def __init__(self, parent, initial_data="", callback=None):
        self.parent = parent
        self.callback = callback  # Функция для отправки ответа обратно
        
        self.window = tk.Toplevel(parent)
        self.window.title("Настройка параметров")
        self.window.geometry("400x200")
        
        self.response_data_begin = tk.StringVar()
        self.response_data_end = tk.StringVar()
        self.response_data_fft = tk.StringVar()
        self.thres = ""
        
        # Выводим данные, полученные из главного окна
        #ttk.Label(self.window, text=f"Получено из главного окна:").grid()
        ttk.Label(self.window, text=initial_data, font=("Arial", 12, "bold")).grid(row=0, column=1)
        
        ttk.Label(self.window, text=f"Начало ряда").grid(row=1, column=0, pady=5)
        ttk.Entry(self.window, textvariable=self.response_data_begin).grid(row=2, column=0, pady=5, padx=5)
        
        ttk.Label(self.window, text=f"Конец ряда").grid(row=1, column=1, pady=5,)
        ttk.Entry(self.window, textvariable=self.response_data_end).grid(row=2, column=1, pady=5,)
        
        if initial_data == "Адаптивная интерполяция":
            self.thres = "Сглаживание"              
        elif initial_data == "Фурье":
            self.thres = "Частота среза"
        elif initial_data == "Вейвлет":
            self.thres = "вид вейвлета"
        
        check = (self.window.register(self.is_valid), "%P")
            
        # Поле для ввода ответа
        ttk.Label(self.window, text=f"{self.thres}:").grid(row=3, column=0, pady=5)    
        ttk.Entry(self.window, textvariable=self.response_data_fft, validate="key", validatecommand=check).grid(row=3, column=1, pady=5)
        # Кнопка отправки ответа
        ttk.Button(
            self.window,
            text="Применить",
            command=self.send_response
        ).grid(row=4, column=1)
    
    def is_valid(self, newval):
        s = ""
        if self.thres == "Частота среза":
            s = "^\d{0,}$"
        elif self.thres == "Сглаживание":
            s = "^\d{0,}([.]\d{0,})?$"
        else:
            s = "^[a-z]{0,}\d{0,}$"
        return re.match(s, newval) is not None
        
    def send_response(self):
        """Отправляем текст из поля ввода обратно в главное окно."""
        if self.callback:
            r = self.response_data_fft.get() + "," + self.response_data_begin.get() + "," + self.response_data_end.get()
            self.callback(r)
        self.window.destroy()  # Закрываем окно