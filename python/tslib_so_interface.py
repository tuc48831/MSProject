import ctypes

# load c dll from shared object
libso = ctypes.CDLL("./tslib.so")
libso.ts_init()

# prepare c functions with corresponding argtypes
# the ts_init line is commented out because while the ts_init function has argc/argv as args,
# ts_init doesnt actually use them for anything, and ctypes throws an error if you call it without corresponding args
# libso.ts_init.argtypes = [ctypes.c_int, ctypes.c_char_p]
libso.tsput.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
libso.tsread.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
libso.tsget.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]


def tsput(tuple_name, tuple_value, tuple_size):
    if tuple_size <= 0:
        return 1
    return_value = libso.tsput(tuple_name, tuple_value, tuple_size)
    # return value checking, tsput either returns the tuple size or a negative number so this error checking is 'safe'
    if return_value != tuple_size:
        return 1
    else:
        return 0


def tsread(tuple_name, string_buffer_size):
    string_buffer = ctypes.create_string_buffer(string_buffer_size)
    # unsure of possible maximum tuple length/return value
    tuple_name_as_buffer = ctypes.create_string_buffer(2*len(tuple_name))
    tuple_name_as_buffer.value = tuple_name.encode('utf-8')
    return_value = libso.tsread(tuple_name_as_buffer, string_buffer, string_buffer_size)
    # return value is the tuple size, so if it is larger than the buffer we pass in there is a problem
    if return_value > string_buffer_size:
        return 1
    else:
        return string_buffer.value, tuple_name_as_buffer.value


def tsget(tuple_name, string_buffer_size):
    string_buffer = ctypes.create_string_buffer(string_buffer_size)
    # unsure of possible maximum tuple length/return value
    tuple_name_as_buffer = ctypes.create_string_buffer(2*len(tuple_name))
    tuple_name_as_buffer.value = tuple_name.encode('utf-8')
    return_value = libso.tsget(tuple_name_as_buffer, string_buffer, string_buffer_size)
    # return value is the tuple size, so if it is larger than the buffer we pass in there is a problem
    if return_value > string_buffer_size:
        return 1
    else:
        return string_buffer.value, tuple_name_as_buffer.value

