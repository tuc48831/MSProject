import ctypes

libso = ctypes.CDLL("./tslib.so")

libso.tsput.argtypes = [ctypes.c_wchar_p, ctypes.c_char_p, ctypes.c_int]

init_size = 256
#pbuf = ctypes.create_string_buffer(init_size)

tp_name = "testTuple"
tp_value = "This is the tuple value"
tp_size = 100
return_value = libso.tsput(tp_name, tp_value, tp_size)