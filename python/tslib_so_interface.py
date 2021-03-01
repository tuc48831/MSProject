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
    tuple_name_as_buffer = ctypes.create_string_buffer(len(tuple_name))
    tuple_name_as_buffer.value = tuple_name.encode('utf-8')
    tuple_value_as_buffer = ctypes.create_string_buffer(len(tuple_value))
    tuple_value_as_buffer.value = tuple_value.encode('utf-8')
    print(tuple_name_as_buffer.value)
    print(tuple_value_as_buffer.value)
    return_value = libso.tsput(tuple_name_as_buffer, tuple_value_as_buffer, tuple_size)
    # return value checking, tsput either returns (int)ntohs(in.error) which i think is always 400 when success or a negative number so this error checking is 'safe'
    # OR ts put error is defined as -106 in tslib.c, usually because tsh is not running
    if return_value != 400 or return_value == -106:
        return 1
    else:
        return 0


def tsput_bytes(tuple_name, tuple_value, tuple_size):
    if tuple_size <= 0:
        return 1
    tuple_name_as_buffer = ctypes.create_string_buffer(len(tuple_name))
    tuple_name_as_buffer.value = tuple_name.encode('utf-8')
    return_value = libso.tsput(tuple_name_as_buffer, tuple_value, tuple_size)
    # return value checking, tsput either returns (int)ntohs(in.error) which i think is always 400 when success or a negative number so this error checking is 'safe'
    # OR ts put error is defined as -106 in tslib.c, usually because tsh is not running
    if return_value != 400 or return_value == -106:
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
    # OR ts read error is defined as -108 in tslib.c, usually because tsh is not running
    if return_value > string_buffer_size or return_value == -108:
        return 1
    else:
        print(string_buffer.value)
        print(tuple_name_as_buffer.value)
        return string_buffer.value.decode('utf-8'), tuple_name_as_buffer.value.decode('utf-8')


def tsread_bytes(tuple_name, string_buffer_size):
    string_buffer = ctypes.create_string_buffer(string_buffer_size)
    # unsure of possible maximum tuple length/return value
    tuple_name_as_buffer = ctypes.create_string_buffer(2*len(tuple_name))
    tuple_name_as_buffer.value = tuple_name.encode('utf-8')
    return_value = libso.tsread(tuple_name_as_buffer, string_buffer, string_buffer_size)
    # return value is the tuple size, so if it is larger than the buffer we pass in there is a problem
    # OR ts read error is defined as -108 in tslib.c, usually because tsh is not running
    if return_value > string_buffer_size or return_value == -108:
        return 1
    else:
        return string_buffer.value, tuple_name_as_buffer.value


def tsget(tuple_name, string_buffer_size):
    string_buffer = ctypes.create_string_buffer(string_buffer_size)
    # unsure of possible maximum tuple length/return value
    tuple_name_as_buffer = ctypes.create_string_buffer(2*len(tuple_name))
    # try explicitly setting whole buffer to null terminator
    tuple_name_as_buffer.value = ('\x00' * 2 * len(tuple_name)).encode('utf-8')
    tuple_name_as_buffer.value = tuple_name.encode('utf-8')
    return_value = libso.tsget(tuple_name_as_buffer, string_buffer, string_buffer_size)
    # return value is the tuple size, so if it is larger than the buffer we pass in there is a problem
    # OR ts get error is defined as -107 in tslib.c, usually because tsh is not running
    if return_value > string_buffer_size or return_value == -107:
        return 1
    else:
        print(string_buffer.value)
        print(tuple_name_as_buffer.value)
        return string_buffer.value.decode('utf-8'), tuple_name_as_buffer.value.decode('utf-8')


def tsget_bytes(tuple_name, string_buffer_size):
    string_buffer = ctypes.create_string_buffer(string_buffer_size)
    # unsure of possible maximum tuple length/return value
    tuple_name_as_buffer = ctypes.create_string_buffer(2*len(tuple_name))
    tuple_name_as_buffer.value = tuple_name.encode('utf-8')
    return_value = libso.tsget(tuple_name_as_buffer, string_buffer, string_buffer_size)
    # return value is the tuple size, so if it is larger than the buffer we pass in there is a problem
    # OR ts get error is defined as -107 in tslib.c, usually because tsh is not running
    if return_value > string_buffer_size or return_value == -107:
        return 1
    else:
        return string_buffer.value, tuple_name_as_buffer.value


def uvr_cores():
    return libso.uvrCores()
