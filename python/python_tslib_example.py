import tslib_so_interface as tslib

import datetime

now = datetime.datetime.now()

print("Current date and time: ")
print(str(now))
print("writing date to tuple")

tuple_size = 200

return_value = tslib.tsput("date", str(datetime.datetime.now()), tuple_size)

print("return value from tsput : " + str(return_value))

# ts read v has a malloc inside the API to modify the buffer size when it returns so you don't have to allocate buffer size manually
string_from_tuple_space = tslib.tsread("date", tuple_size)

print("value retrieved from tuple space : " + string_from_tuple_space)

string_from_tuple_space = None

string_from_tuple_space = tslib.tsget("date", tuple_size)

print("value retrived from tuple space with tsget : " + string_from_tuple_space)
