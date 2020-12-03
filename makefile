CFLAGS = -I../../include -I/home/shi/anaconda3/envs/tf/include/python3.7m -O -o -fno-strict-aliasing -Wdate-time -D_FORTIFY_SOURCE=2 -g -fstack-protector-strong -Wformat -Werror=format-security  -DNDEBUG -g -fwrapv -O2 -Wall

OBJS = -L../../obj  -lsng -L/usr/lib/python2.7/config-x86_64-linux-gnu -L/usr/lib -lpython2.7 -lpthread -ldl  -lutil -lm  -Xlinker -export-dynamic -Wl,-O1 -Wl,-Bsymbolic-functions

all: tsp_seq tspclnt tspwrk 
 
tsp_seq : tsp_seq.c
	cc $(CFLAGS) tsp_seq tsp_seq.c $(OBJS)

tspclnt : tspclnt.c
	cc $(CFLAGS) tspclnt -g tspclnt.c $(OBJS)

tspwrk : tspwrk.c 
	gcc $(CFLAGS) tspwrk tspwrk.c $(OBJS)

