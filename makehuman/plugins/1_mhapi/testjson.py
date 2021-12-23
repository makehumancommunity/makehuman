#!/usr/bin/python

from .JsonCall import JsonCall

a = dict()
a["aaa"] = 1;
a["bbb"] = None
a["ccc"] = ["a","b",1.54]

jsc = JsonCall()
jsc.setFunction("testfunction")
jsc.setParam("hej","hopp")
jsc.setParam("abc",2)
jsc.setData([ [1,2,3.3], [1,2,3], a ])

print(jsc.serialize())

#js = "{\
#  \"function\": \"testfunction\",\
#  \"error\": \"\",\
#  \"params\": {\
#    \"abc\": 2,\
#    \"hej\": \"hopp\"\
#  },\
#  \"data\": null\
#}"
#
#jsc = JsonCall(js)
#
#print jsc.serialize()



