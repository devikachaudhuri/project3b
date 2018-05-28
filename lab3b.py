#!/usr/bin/python

import csv


inode_list = list()


class Inodes:
    def __init__(self, number):
        self.number = number;
        self.links_to_me = 0;
        self.on_free_list = -1;#0 means no, 1 means yes
        print("hi\n")

class Blocks:
    class BlockRef:
        def __init__(self, inode, offset):
            self.inode = 0
            self.offset = 0
            print("reference made\n")
    def __init__(self, number):
        self.number = number
        self.references = []
        self.onFreelist = 0
        self.allocated = 0

def csv_dict_reader(file_obj):
    reader = csv.reader(file_obj, delimiter=",")
    for row in reader:
        if row[0] == "IFREE":
            i = Inodes(row[1])
            i.on_free_list = 1
            inode_list.append(i)xs
            

if __name__ == "__main__":
    with open("trivial.csv") as f_obj:
              csv_dict_reader(f_obj)
    print(inode_list[3].number)
