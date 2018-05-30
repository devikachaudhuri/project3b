
#!/usr/bin/python

import csv
import sys

inode_list = list()
inode_numbers = list() #list of just inode numbers
free_inode = list ()
alloc_inode = list()
unallocated_and_not_on_free_list = list () #list of un
dir_list = list()
superblock = list()
block_list = list()
group_list = list()
reserved = 9 #OR 10??? (not including inode 2)
first_block = 0
max_block = 0

##########################CLASSES#######################################
class Super:
    def __init__(self, inodeSize, blockSize):
        self.ino_size = inodeSize
        self.blk_size = blockSize

class Group:
    def __init__(self, num_inodes, numBlocks):
        self.num_inodes = num_inodes
        self.num_blks = numBlocks
        
class Inodes:
    def __init__(self, number):
        self.number = number
        self.links_to_me = 0  
        self.recorded_link_count = 0

class BlockRef:
    def __init__(self, inode, offset, indirectness):
        self.inode = inode                # Stored as a string
        self.offset = offset              # Stored as a string
        self.indirectness = indirectness  # Stored as a string

class Block:
    def __init__(self, number):
        self.number = number  # Stored as an int
        self.references = []  # List of BlockRef objects
        self.onFreelist = 0   # Stored as an int (1 or 0)
        self.allocated = 0    # Stored as an int (1 or 0)

    def add_ref(self, inode, offset, indirectness):
        # Arguments are passed as strings
        ref = BlockRef(inode, offset, indirectness)
        self.references.append(ref)

    def found_allocated(self):
        # Set allocated variable (block found allocated)
        self.allocated = 1

    def on_free_list(self):
        # Set freelist variable (block found on the free list)
        self.onFreelist = 1
    
    def chk_unreferenced(self):
        if (self.allocated == 0) and (self.onFreelist == 0):
            # Print appropriate error msg if neither allocated nor on free list
            print("UNREFERENCED BLOCK " + str(self.number))
            return 1
        return 0

    def chk_alloc_on_free(self):
        if (self.allocated == 1) and (self.onFreelist == 1):
            # Print appropriate error msg if allocated and on the free list
            print("ALLOCATED BLOCK " + str(self.number) + " ON FREELIST")
            return 1
        return 0
    
    def chk_duplicate_ref(self):
        if (len(self.references) > 1):
            for ref in self.references:
                # Loop through all the references and print appropriate error msgs
                if ref.indirectness == "3":
                    blk_label = "TRIPLE INDIRECT BLOCK"
                elif ref.indirectness == "2":
                    blk_label = "DOUBLE INDIRECT BLOCK"
                elif ref.indirectness == "1":
                    blk_label = "INDIRECT BLOCK"
                else:
                    blk_label = "BLOCK"
                print("DUPLICATE " + blk_label + " " + str(self.number) + " IN INODE " +\
                      ref.inode + " AT OFFSET " + ref.offset)

class Directories:
    def __init__(self, parent_inode, file_inode, name):
        self.parent_inode = parent_inode;
        self.file_inode = file_inode;
        self.name = name;
        self.previous_inode = -1;
        
########################HELPER FUNCTIONS#################################

def is_on_free_list(num):
    if num in free_inode:
        return 1
    else:
        return 0

def is_on_alloc_list(num):
    if num in alloc_inode:
        return 1
    else:
        return 0
        
def update_inode_link_count():
    for dire in dir_list:
        linked_ino = dire.file_inode
        for item in inode_list:
            if item.number == linked_ino:
                item.links_to_me = item.links_to_me + 1
                

def update_previous_inodes():
    for item in dir_list:
        inode = str(item.parent_inode)
        if inode == '2':
            item.previous_inode = '2'
        else:
            for item2 in dir_list:
                if inode == str(item2.file_inode) and item2.name != "'.'":
                    item.previous_inode = str(item2.parent_inode)
                    continue
            
def init_block_list():
    num_inode_blks = int(group_list[0].num_inodes) * int(superblock[0].ino_size)\
                     / int(superblock[0].blk_size)
    global first_block
    global max_block
    first_block = 5 + num_inode_blks
    max_block = int(group_list[0].num_blks)
    for block_num in range(first_block, max_block):
        block = Block(block_num)
        block_list.append(block)

def is_there_unallocated_inodes():
    zero = int(group_list[0].num_inodes) - reserved - len(inode_list)
    if zero != 0:
        for x in range(1, int(group_list[0].num_inodes)):
            if str(x) not in inode_numbers:
                if x > 10:
                    unallocated_and_not_on_free_list.append(x)

######################CHECKER FUNCTIONS####################################

def check_inodes():
    update_inode_link_count()
    is_there_unallocated_inodes()
    for x in unallocated_and_not_on_free_list:
        print "UNALLOCATED INODE " + str(x) + " NOT ON FREELIST"
    for x in free_inode:
        if x in alloc_inode:
            print "ALLOCATED INODE " + x + " ON FREELIST"
    for item in inode_list:
        if str(item.recorded_link_count) != str(item.links_to_me):
            if item.number not in free_inode:
                print "INODE " + item.number + " HAS " + str(item.links_to_me)  + " LINKS BUT LINKCOUNT IS " + str(item.recorded_link_count)

def check_directories():
    update_previous_inodes()
    for item in dir_list:
        #check for invalid inodes
        if item.file_inode < 1 or item.file_inode > group_list[0].num_inodes:
            print "DIRECTORY INODE " + item.parent_inode + " NAME " \
                + item.name + " INVALID INODE " + item.file_inode
        #check for unallocate inodes
        elif (is_on_alloc_list(item.file_inode) == 0):
            print "DIRECTORY INODE " + item.parent_inode + " NAME " \
                + item.name + " UNALLOCATED INODE " + item.file_inode
        #check for . (itself) and .. (previous inode) correct linking
        if item.name == "'.'" and item.parent_inode != item.file_inode:
            print "DIRECTORY INODE " + item.parent_inode + " NAME '.' LINK TO INODE " \
                + item.file_inode + " SHOULD BE " + item.parent_inode
        if item.name == "'..'" and item.previous_inode != item.file_inode:
            print "DIRECTORY INODE " + item.parent_inode + " NAME '..' LINK TO INODE " \
                + item.file_inode + " SHOULD BE " + item.previous_inode

def check_block_num(blk_num_i, blk_num, inode_num, offset):
    ptr_num = blk_num_i - 11                    # Convert the csv index to a pointer index
    # Accept the 15th pointer or a -3 code for the triple indirect blocks
    if (ptr_num == 15) or (blk_num_i == -3):
        blk_label = "TRIPLE INDIRECT BLOCK"
        indirectness = "3"
        if (int(offset) == 0) and (ptr_num == 15): # Offset always 65804 for Inode triple
            offset = str(65804)                    #   indirect pointers
    # Accept the 14th pointer or a -2 code for the double indirect blocks
    elif (ptr_num == 14) or (blk_num_i == -2):
        blk_label = "DOUBLE INDIRECT BLOCK"
        indirectness = "2"
        if (int(offset) == 0) and (ptr_num == 14): # Offset always 268 for Inode double
            offset = str(268)                      #   indirect pointers       
    # Accept the 13th pointer or a -1 code for the single indirect blocks
    elif (ptr_num == 13) or (blk_num_i == -1):
        blk_label = "INDIRECT BLOCK"
        indirectness = "1"
        if (int(offset) == 0) and (ptr_num == 13): # Offset always 12 for Inode triple
            offset = str(12)                       #   indirect pointers
    # All others are normal blocks
    else:
        blk_label = "BLOCK"
        indirectness = "0"
        if (int(offset) == 0) and ((ptr_num < 13) and (ptr_num > 0)):    
            offset = str(ptr_num - 1)           # Offset is the ptr number in inode list
                                                #   if for a regular block
    blk_index = int(blk_num) - first_block # index for the block list
    if (int(blk_num) > max_block) or (int(blk_num) < 0):
        # Invalid if the block number is obviously too big or too small
        print("INVALID " + blk_label + " " + blk_num + " IN INODE "\
              + inode_num + " AT OFFSET " + offset)
        return -1
    if (int(blk_num) == 0):
        # Null pointers/no block referenced
        return 0
    if blk_index >= 0:
        # Valid block indices should be listed
        block_list[blk_index].found_allocated()
        # add_ref(self, inode, offset, indirectness)
        block_list[blk_index].add_ref(inode_num, offset, indirectness)
        return 1
    else:
        # Reserved if within the first set of blocks
        print("RESERVED " + blk_label + " " + blk_num + " IN INODE "\
              + inode_num + " AT OFFSET " + offset)       
        return -1

def csv_init_reader(file_obj):
    # Read the Superblock and Group entries first for initialization
    reader = csv.reader(file_obj, delimiter=",")
    for row in reader:
        if len(row) < 0:
            print "The CSV file is invalid"
            sys.exit(2)
        if row[0] == "SUPERBLOCK":
            s = Super(row[4], row[3])
            superblock.append(s)
        if row[0] == "GROUP":
            g = Group(row[3], row[2])
            group_list.append(g)
            
def csv_dict_reader(file_obj):
    reader = csv.reader(file_obj, delimiter=",")
    for row in reader:
        if len(row) < 0:
            print "The CSV file is invalid"
            sys.exit(2)
        if row[0] == "BFREE": #denote the block is free
            block_list[int(row[1]) - first_block].on_free_list()
        elif row[0] == "IFREE": #put the free inodes on the inode list
            i = Inodes(row[1])
            n = row[1]
            inode_numbers.append(n)
            free_inode.append(n)
            inode_list.append(i)
        elif row[0] == "INODE": #put the allocated inodes on the inode list
            k = Inodes(row[1])
            k.recorded_link_count = row[6]#record the link count
            n = row[1]
            inode_numbers.append(n)
            alloc_inode.append(n)
            inode_list.append(k)
            # Update the blocks in the inode entry
            if len(row) == 27: # Only loop if this has the appropriate number of entries
                for blk_num_i in range(12, 26 + 1):
                    #def check_block_num(blk_num_i, blk_num, inode_num, offset)
                    check_blk_ret = check_block_num(blk_num_i, row[blk_num_i], row[1], "0")
        elif row[0] == "DIRENT":
            d = Directories(row[1], row[3], row[6])
            dir_list.append(d)
        elif row[0] == "INDIRECT":
            # Allocated if in an indirect block
            block_list[int(row[4]) - first_block].found_allocated()
            # Check the pointed to block - also marks referred to
            check_blk_ret = check_block_num(-int(row[2]), row[5], row[1], row[3])
            if check_blk_ret != 1:
                continue
            # Pointed to block allocated too
            block_list[int(row[5]) - first_block].found_allocated()


def check_blocks():
    for blk in block_list:
        blk.chk_unreferenced()
        blk.chk_alloc_on_free()
        blk.chk_duplicate_ref()
              
       
if __name__ == "__main__":
    name_of_csv = sys.argv[1];
    try:
        f_obj = open(name_of_csv)
    except IOError as e:
        sys.stderr.write("Open error: " + e.strerror + "\n")
        sys.exit(1)
    csv_init_reader(f_obj)
    init_block_list()
    try:
        f_obj2 = open(name_of_csv)
    except IOError as e:
        sys.stderr.write("Open error: " + e.strerror + "\n")
        sys.exit(1)
    csv_dict_reader(f_obj2)
    check_inodes()
    check_directories()
    check_blocks()
