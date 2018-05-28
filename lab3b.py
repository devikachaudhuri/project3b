#!/usr/bin/python

import csv

inode_list = list()
dir_list = list()
superblock = list()

##########################CLASSES#######################################
class Super:
    def __init__(self):
        self.num_inodes = -1
        
class Inodes:
    def __init__(self, number):
        self.number = number
        self.links_to_me = 0
        self.on_free_list = -1 #0 means no, 1 means yes
        self.allocated = -1
        self.recorded_link_count = 0

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

class Directories:
    def __init__(self, parent_inode, file_inode, name):
        self.parent_inode = parent_inode;
        self.file_inode = file_inode;
        self.name = name;
        self.previous_inode;
        
########################HELPER FUNCTIONS#################################

def is_on_free_list(num):
    for item in inode_list:
        if item.number == num and item.on_free_list == "1":
            return 1
        
def update_inode_link_count(linked_ino):
    for item in inode_list:
        if item.number == linked_ino:
            item.links_to_me = item.links_to_me + 1

def update_previous_inodes():#todo: this is slow.
    for item in dir_list:
        inode = item.parent_inode
        for item2 in dirlist:
            if inode == item.file_inode:
                item.previous_inode = item2.parent_inode
            

######################CHECKER FUNCTIONS####################################

def check_inodes():
    for item in inode_list:
        #check allocated vs unallocated
        if item.on_free_list == "1" and item.allocated == "1":
            print "ALLOCATED INODE " + item.number + " ON FREELIST"
        if item.on_free_list == "0" and item.allocated == "0":
            print "UNALLOCATED INODE " + item.number + " NOT ON FREELIST"
        #check link counts match
        if item.recorded_link_count != item.links_to_me:
            print "INODE " + item.number + " HAS " + str(item.recorded_link_count) + " LINKS BUT LINKCOUNT IS " + str(item.links_to_me)

def check_directories():
    update_previous_inodes()
    for item in dir_list:
        #check for invalid inodes
        if item.file_inode < 1 or item.file_inode > superblock[0].num_inodes:
            print "DIRECTORY INODE " + item.parent_inode + " NAME '" + dir_list.name + "' INVALID INODE " + item.file_inode
        #check for unallocate inodes
        if (is_on_free_list(item.file_inode)):
            print "DIRECTORY INODE " + item.parent_inode + " NAME '" + dir_list.name + "' UNALLOCATED INODE " + item.file_inode
        #check for . (itself) and .. (previous inode) correct linking
        if item.name == "." and item.parent_inode != item.file_inode:
            print "DIRECTORY INODE " + item.parent_inode + " NAME '.' LINK TO INODE " + item.file_inode + " SHOULD BE " + item.parent_inode
        if item.name == ".." and item.previous_inode != item.file_inode:
            print "DIRECTORY INODE " + item.parent_inode + " NAME '..' LINK TO INODE " + item.file_inode + " SHOULD BE " + item.previous_inode
        
            
def csv_dict_reader(file_obj):
    reader = csv.reader(file_obj, delimiter=",")
    for row in reader:
        if row[0] == "IFREE": #put the free inodes on the inode list
            i = Inodes(row[1])
            i.on_free_list = 1
            inode_list.append(i)
        if row[0] == "INODE": #put the allocated inodes on the inode list
            i = Inodes(row[1])
            i.allocated = 1
            i.recorded_link_count = row[6]#record the link count
            inode_list.append(i)
        if row[0] == "DIRENT":
            d = Directories(row[1], row[3], row[6])
            update_inode_link_count(row[1])
            dir_list.append(d)
        if row[0] == "SUPERBLOCK":
            s = Super()
            s.num_inodes = row[2]
            superblock.append(s)
        
if __name__ == "__main__":
    with open("trivial.csv") as f_obj:
              csv_dict_reader(f_obj)
    check_inodes()
    check_directories()
