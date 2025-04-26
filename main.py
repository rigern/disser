import pandas as pd
import numpy as np
import re
from scipy.interpolate import CubicSpline
from scipy.interpolate import Rbf
from scipy.interpolate import RBFInterpolator

def toFixed(nums):
    new_nums = []
    for num in nums:
        new_nums.append(f"{num:.{2}f}")
    
    return new_nums

def read_from_csv():
    file1 = open("src/PR0023a1.csv", "r")
    lines = file1.readlines()
    
    for line in lines:
        l = line.split(',')
        
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

def inter_by_parts():
    traces = read_from_csv()
    trace_time = traces.pop()
    time_it_trace = []
    last_element = []
    new_array = []
    
    for trace in traces:
        l = trace.split(',')
        t = l.pop(0)
        time_it_trace = l.pop(-2)
        last_element.append(l.pop(-1))
        parts_trace = split_array(l, 8)
        y_t = [t]
        
        for part in parts_trace:
            x = np.linspace(0, len(part) - 1, len(part))
            y = np.array(part)
            #cs = CubicSpline(x, y, bc_type='natural')
            cs = Rbf(x, y, function='multiquadric', smooth=0.5)
            x_new = np.linspace(0, ((len(x) * 4) - 1), (len(x) * 4))
            y_new = cs(x_new)
            y_new = toFixed(y_new)
            y_t += y_new
            #new_array.append(y_new)
        
        y_t = np.append(y_t, time_it_trace)
        new_array.append(y_t)    
        #y_new = np.append(y_new, last_element)  
    
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
    
    y, t_time, last_elem = inter_by_parts()
    file1 = open("src/inter_by_parts.csv", "w")
    
    #t = re.sub(r'[^0-9.o: -]', '', str(y[0]))
    #t = t.replace(" ", ", ")
    #print(str(y[1]).translate({ord(i): None for i in '[]'}))
    
    for i in y:
        s = re.sub(r'[^0-9.o: -]', '', str(i))
        s = s.replace(" ", ", ")
        s = s.replace(" ,", "")
        s = s.replace(".00", "")
        file1.write(s + "," + last_elem[0])
    
    file1.write(t_time)
    file1.close()
    
write_to_csv()