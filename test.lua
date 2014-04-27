local utf8 = require "utf8.c"

local str = "一天50000粮食或银两直接就五本了"
local len = utf8.len(str)
print(str,"->", len)

local t = {}
assert(utf8.toutf32(str, t))
assert(#t == len)

local str1 = utf8.toutf8(t)
assert(str == str1)

