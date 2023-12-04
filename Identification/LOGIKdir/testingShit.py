import multiprocessing
import os
import psutil

prosess = psutil.process_iter()
for element in prosess:
    print(element.name())