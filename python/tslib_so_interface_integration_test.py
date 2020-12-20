import sys

import tslib_so_interface as tslib

import datetime


def main():
    now = datetime.datetime.now()

    print("Current date and time: ")
    print(str(now))
    print("writing date to tuple")

    tuple_size = 200
    tuple_name = "date"

    return_value = tslib.tsput(tuple_name, str(datetime.datetime.now()), tuple_size)
    if return_value == 1:
        print("ERROR, tsput returned 1, failure detected, integration test failed")
        sys.exit(1)
    else:
        print("return value from tsput : " + str(return_value))

    partial_tuple = "da"
    string_from_tuple_space, matched_tuple_name = tslib.tsread(partial_tuple, tuple_size)
    if matched_tuple_name.decode('utf-8') != tuple_name:
        print("ERROR, tsread regex matching from: " + partial_tuple + " | " + matched_tuple_name.decode('utf-8') + " failed, integration test failed")
        sys.exit(1)
    else:
        print("matched tuple name : " + matched_tuple_name)
        print("value retrieved from tuple space : " + string_from_tuple_space)

    string_from_tuple_space = None

    string_from_tuple_space, matched_tuple_name = tslib.tsget("date", tuple_size)
    if matched_tuple_name.decode('utf-8') != tuple_name:
        print("ERROR, tsget regex matching from 'da' to 'date' failed, integration test failed")
        sys.exit(1)
    else:
        print("matched tuple name : " + matched_tuple_name)
        print("value retrieved from tuple space : " + string_from_tuple_space)
    sys.exit(0)


if __name__ == "__main__":
    main()
