import ctypes

# load c dll from shared object
libso = ctypes.CDLL("./tslib.so")
# prepare c functions with corresponding argtypes
# the ts_init line is commented out because while the ts_init function has argc/argv as args,
# ts_init doesnt actually use them for anything, and ctypes throws an error if you call it without corresponding args
# libso.ts_init.argtypes = [ctypes.c_int, ctypes.c_char_p]
libso.tsput.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
libso.tsread.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
libso.tsget.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]


def initialize():
    # no return value to parse as if ts_init fails it calls exit(0)
    libso.ts_init()


def tsput(tuple_name, tuple_value, tuple_size):
    return_value = libso.tsput(tuple_name, tuple_value, tuple_size)
    # return value checking goes here, tsput either returns the tuple size or a negative number so this error checking is 'safe'
    if return_value != tuple_size:
        return 1
    else:
        return 0


def tsread(tuple_name, string_buffer_size):
    string_buffer = ctypes.create_string_buffer(string_buffer_size)
    return_value = libso.tsread(tuple_name, string_buffer, string_buffer_size)
    # return value checking goes here
    if return_value >= string_buffer_size:
        return 1
    else:
        return string_buffer.value


def tsget(tuple_name, string_buffer_size):
    string_buffer = ctypes.create_string_buffer(string_buffer_size)
    return_value = libso.tsget(tuple_name, string_buffer, string_buffer_size)
    # return value checking goes here
    if return_value >= string_buffer_size:
        return 1
    else:
        return string_buffer.value


if __name__ == "__main__":
    initialize()

    tp_name = "testTuple"
    tp_value = "This is the tuple value"
    tp_size = 100

    tsput(tp_name, tp_value, tp_size)

    tuple_string = tsread(tp_name, tp_size)
    print(tuple_string)

    tuple_string_2 = tsget(tp_name, tp_size)
    print(tuple_string)
