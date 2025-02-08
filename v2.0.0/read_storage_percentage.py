import os

def read_storage_percentage():
    statvfs = os.statvfs('/')
    total_blocks = statvfs[2]
    free_blocks = statvfs[3]
    used_blocks = total_blocks - free_blocks
    storage_percentage = (used_blocks / total_blocks) * 100
    return storage_percentage