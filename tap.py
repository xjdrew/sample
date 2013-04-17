# -*- coding: utf-8 -*-
#!/user/bin/python
"""
1.假设你的键盘只有以下键:
A
Ctrl + A
Ctrl + C
Ctrl + V
这里Ctrl+A,Ctrl+C,Ctrl+V分别代表"全选",“复制”，“粘贴”。

如果你只能按键盘N次，请写一个程序可以产生最多数量的A。也就是说输入是N(你按键盘的次数)， 输出是M(产生的A的个数)。

加分项：
打印出中间你按下的那些键。 
"""

# Brute force method
import sys

def press_key(remain, total, clip, keylist):
    if remain == 0:
        return total, keylist

    t = []
    if clip == 0:
        t.append(press_key(remain-1, total+1, clip, keylist+"A"))
    else:
        t.append(press_key(remain-1, total + clip, clip, keylist+"v"))
    if remain >= 4:
        t.append(press_key(remain-4, 2*total, total, keylist+"acvv"))

    total, keylist = 0, ""
    for l in t:
        if l[0] > total:
            total = l[0]
            keylist = l[1]
    return total, keylist

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Useage %s <tap times>" % sys.argv[0])
        exit(1)
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("'%s' cant conver to int" % sys.argv[1])
        exit(2)
    remain = n
    total  = 0
    clip   = 0
    keylist = ""

    print(press_key(remain, total, clip, keylist))

