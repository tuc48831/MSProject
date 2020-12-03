CFLAGS = -I../../include -I/home/shi/anaconda3/envs/tf/include/python3.7m -fno-strict-aliasing -Wdate-time -D_FORTIFY_SOURCE=2 -g -fstack-protector-strong -Wformat -Werror=format-security -DNDEBUG -g -fwrapv -O2 -Wall -O -o

OBJS = -L../../obj -L/usr/lib/python2.7/config-x86_64-linux-gnu -L/usr/lib -lpython2.7 -lpthread -ldl  -lutil -lm  -Xlinker -export-dynamic -Wl,-O1 -Wl,-Bsymbolic-functions

all: pyrunner 
 
pyrunner : pyrunner.c
	cc $(CFLAGS) pyrunner pyrunner.c $(OBJS)

