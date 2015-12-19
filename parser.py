#/usr/bin/python 
# borrowed from http://alexgorale.com/how-to-program-block-chain-explorers-with-python-part-1

import blocktools 
import os
import fnmatch
import copy
import pdb
from hashlib import sha256
import struct
import binascii
import array
import pickle as pkl
import time

# define global variables
BLKDIR = '../Library/Application Support/Bitcoin/blocks/' # directory where blocks are stored in *.dat format
BLKHASH_FINAL = '00000000000000000355f2dae74e2f6eaee07314702efee154873f2c461b7591' # hash of last block in the all_blockheaders.pkl file


def end_of_blkfile(f, magic_id):
      # check that magic_id contains 4 bytes of data
      if (magic_id == '') or (len(magic_id) < 4):
            return True

      # if magic_is zero, then scan until finding next non-zero value
      magic_id2 = struct.unpack('I', magic_id)[0]
      n = 0
      while magic_id2 == 0:
            temp = f.read(4)
            n += 4
            if (temp == '') or (len(temp) < 4):
                  return True
            else:
                  magic_id2 = struct.unpack('I', temp)[0]

      # nto at end of file, so jump back to starting place and return false
      f.seek(-n, 1)
      return False

# returns a dictionary where keys are block hashes and 
# values are a list containing a file pointer and previous block hash 
# for all blocks in the blockchain (including orphans)
# NOTE: blkdir must end with '/'
def get_all_blockheaders(blkdir):
      blocks = {}
      blkfiles = fnmatch.filter(os.listdir(blkdir), 'blk*.dat')
      # blkfiles = ['blk00346.dat']
      for blkfile in blkfiles:
            start_time = time.time()
            with open(blkdir + blkfile, 'rb') as f:
                  n = 0 # start at zero bytes into file
                  while True:
                        f.seek(n, 0)

                        # get magic id and make sure we are actually at the start of a block
                        magic_id = f.read(4)
                        if end_of_blkfile(f, magic_id):
                              break
                        magic_id = struct.unpack('I', magic_id)[0]
                        while magic_id == 0:
                              temp = f.read(4)
                              magic_id = struct.unpack('I', temp)[0]
                              n += 4
                        if hex(magic_id) != '0xd9b4bef9':
                              n -= (block_size) # hack for blk000328.dat
                              f.seek(n, 0)
                              magic_id = struct.unpack('I', f.read(4))[0]
                              if hex(magic_id) != '0xd9b4bef9':
                                    raise('MAGIC ID: not equal to expected value '+ hex(magic_id))

                        # get block size, hash, and previous hash
                        block_size = struct.unpack('I', f.read(4))[0] #blocktools.uint4(f)
                        block_prefix = f.read(80)
                        current_hash = sha256(sha256(block_prefix).digest()).digest()[::-1].encode('hex') #current_hash = sha256(sha256(block_prefix).digest()).hexdigest()
                        previous_hash = block_prefix[4:36][::-1].encode('hex') #struct.unpack('Q', block_prefix[4:36])[0]
                        
                        # store block data in dictionary
                        blocks[current_hash] = {'blkfile': blkfile, 'byte_offset': n, 'previous_hash': previous_hash}
                        n += (block_size+8) # update current place in file
            
            print "finished "+ blkfile +" in "+ str(time.time() - start_time) +" seconds"
            print "final block hash in file = ", current_hash

      return blocks

def get_mainchain_blocks(all_blocks, blkhash_final):
      blocks = {}
      
      return blocks



def sample_block_parser():
      blkfile = '../Library/Application Support/Bitcoin/blocks/blk00000.dat'
      with open(blkfile, 'rb') as blockfile: 
            print "Magic Number:\t %8x" % blocktools.uint4(blockfile) 
            print "Blocksize:\t %u" % blocktools.uint4(blockfile) 

            """Block Header""" 
            print "Version:\t %d" % blocktools.uint4(blockfile) 
            print "Previous Hash\t %s" % blocktools.hashStr(blocktools.hash32(blockfile)) 
            print "Merkle Root\t %s" % blocktools.hashStr(blocktools.hash32(blockfile)) 
            print "Time\t\t %s" % str(blocktools.time(blockfile)) 
            print "Difficulty\t %8x" % blocktools.uint4(blockfile) 
            print "Nonce\t\t %s" % blocktools.uint4(blockfile) 

            print "Tx Count\t %d" % blocktools.varint(blockfile) 

            print "Version Number\t %s" % blocktools.uint4(blockfile) 
            print "Inputs\t\t %s" % blocktools.varint(blockfile) 
            print "Previous Tx\t %s" % blocktools.hashStr(blocktools.hash32(blockfile)) 
            print "Prev Index \t %d" % blocktools.uint4(blockfile) 
            script_len = blocktools.varint(blockfile) 
            print "Script Length\t %d" % script_len 
            script_sig = blockfile.read(script_len) 
            print "ScriptSig\t %s" % blocktools.hashStr(script_sig) 
            print "ScriptSig\t %s" % blocktools.hashStr(script_sig).decode('hex') 
            print "Seq Num\t\t %8x" % blocktools.uint4(blockfile) 

            print "Outputs\t\t %s" % blocktools.varint(blockfile) 
            print "Value\t\t %s" % str((blocktools.uint8(blockfile)*1.0)/100000000.00) 
            script_len = blocktools.varint(blockfile) 
            print "Script Length\t %d" % script_len 
            script_pubkey = blockfile.read(script_len) 
            print "Script Pub Key\t %s" % blocktools.hashStr(script_pubkey) 
            print "Lock Time %8x" % blocktools.uint4(blockfile) 
            print

def main():
      # sample_block_parser()  
      # blocks = get_all_blockheaders(BLKDIR)
      # f = open('all_blockheaders.pkl', 'wb') # the final blockhash in this pkl is '00000000000000000355f2dae74e2f6eaee07314702efee154873f2c461b7591'
      # pkl.dump(blocks, f)
      # f.close()

      f = open('all_blockheaders.pkl', 'rb')
      all_blocks = pkl.load(f)
      f.close()
      blocks = get_mainchain_blocks(all_blocks, BLKHASH_FINAL)

      

if __name__ == "__main__":
      main()