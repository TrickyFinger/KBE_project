import os


path_wd = os.getcwd()
path_emwet_output = os.path.join(path_wd, '../Output/EMWET_output.txt')
os.remove(path_emwet_output)