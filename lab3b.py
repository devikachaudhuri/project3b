#!/usr/bin/python

import csv
import sys

inode_list = list()
inode_numbers = list() #list of just inode numbers
unallocated_and_not_on_free_list = list () #list of un
dir_list = list()
superblock = list()
reserved = 9 #OR 10??? (not including inode 2)

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

class Directories:
    def __init__(self, parent_inode, file_inode, name):
        self.parent_inode = parent_inode;
        self.file_inode = file_inode;
        self.name = name;
        self.previous_inode = -1;
        
########################HELPER FUNCTIONS#################################

def is_on_free_list(num):
    for item in inode_list:
        if item.number == num and item.on_free_list == "1":
            return 1
        
def update_inode_link_count():
#    print "amount " + str(len(inode_list))
    for dir in dir_list:
        linked_ino = dir.file_inode
        for item in inode_list:
            #       print "item number " + item.number
            #      print "linked_ino " + linked_ino
            if item.number == linked_ino:
                item.links_to_me = item.links_to_me + 1
                

def update_previous_inodes():#todo: this is slow.
    for item in dir_list:
        inode = item.parent_inode
        for item2 in dir_list:
            if inode == item.file_inode:
                item.previous_inode = item2.parent_inode

def is_there_unallocated_inodes():
    zero = int(superblock[0].num_inodes) - reserved - len(inode_list)
    if zero != 0:
        for x in range(1, int(superblock[0].num_inodes)):
            if str(x) not in inode_numbers:
                if x > 10:
                    unallocated_and_not_on_free_list.append(x)

######################CHECKER FUNCTIONS####################################

def check_inodes():
    update_inode_link_count()
    is_there_unallocated_inodes()
    for x in unallocated_and_not_on_free_list:
        print "UNALLOCATED INODE " + str(x) + " NOT ON FREELIST"
    for item in inode_list:
        #check allocated vs unallocated
        if item.on_free_list == "1" and item.allocated == "1":
            print "ALLOCATED INODE " + item.number + " ON FREELIST"
        #if item.on_free_list == "0" and item.allocated == "0":
         #   print "UNALLOCATED INODE " + item.number + " NOT ON FREELIST"
        #check link counts match
        if str(item.recorded_link_count) != str(item.links_to_me):
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
            n = row[1]
            inode_numbers.append(n)
            inode_list.append(i)
        if row[0] == "INODE": #put the allocated inodes on the inode list
            k = Inodes(row[1])
            k.allocated = 1
            k.recorded_link_count = row[6]#record the link count
            n = row[1]
            inode_numbers.append(n)
            inode_list.append(k)
        if row[0] == "DIRENT":
            d = Directories(row[1], row[3], row[6])
            #update_inode_link_count(row[3])
            dir_list.append(d)
        if row[0] == "SUPERBLOCK":
            s = Super()
            s.num_inodes = row[2]
            superblock.append(s)
        
if __name__ == "__main__":
    name_of_csv = sys.argv[1];
    with open(name_of_csv) as f_obj:
              csv_dict_reader(f_obj)
    check_inodes()
    check_directories()
