# -*- coding: utf-8 -*-

'''
status value == match length
'''
def compute_status_transfer_table(pattern):
    o = []
    for i,c in enumerate(pattern):
        if len(o) < i:
            o.append(0)

        for j in range(i,0,-1):
            if pattern[:j] == pattern[i-j+1:i+1]:
                o.append(j)
                break
    return o

"status machine"
def machine(pattern, c, status, transfer):
    if pattern[status] == c:
        return status + 1
    elif status == 0:
        return status
    else:
        return machine(pattern, c, transfer[status-1], transfer)

def search_kmp(target, pattern):
    ret = []
    transfer = compute_status_transfer_table(pattern)
    status = 0
    for i,c in enumerate(target):
        status = machine(pattern,c,status,transfer)
        if status == len(pattern):
            ret.append(i - len(pattern) + 1)
            status = 0
    return ret
            
def search_default(target, pattern):
    ret = []
    i = 0
    step = len(pattern)
    while True:
        index = target.find(pattern, i)
        if index == -1:
            break
        ret.append(index)
        i = step + index
    return ret


if __name__ == "__main__":
    target = '''
        While The Python Language Reference describes the exact syntax and semantics of the Python language, this library reference manual describes the standard library that is distributed with Python. It also describes some of the optional components that are commonly included in Python distributions.
    '''
    pattern = "th"
    print(target)
    print(pattern)
    kmp = search_kmp(target, pattern)
    default = search_default(target, pattern)
    print(kmp)
    print(default)
    assert(kmp == default)

