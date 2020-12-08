import ctypes

libso = ctypes.CDLL("./tslib.so")

libso.tsput.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
libso.tsget.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]

init_size = 256
pbuf = ctypes.create_string_buffer(init_size)

return_value = libso.ts_init()

tp_name = "testTuple"
tp_value = "This is the tuple value"
tp_size = 100
return_value = libso.tsput(tp_name, tp_value, tp_size)

return_value = libso.tsget(tp_name, pbuf, tp_size)

print(pbuf.value)
