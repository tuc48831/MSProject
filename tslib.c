//
// Created by Peter on 12/7/2020.
//

=======================================================================
/***************** tslib functions *******************/
#include "synergy.h"

#define MAXNAME 128
#define TSPUT_ER -106
#define TSGET_ER -107
#define TSREAD_ER -108

struct {
    char appname[MAXNAME]; /* Application system name */
    char appid[MAXNAME] ; /* Application id (appbane+host+pid) */
    char **args; /* arguments */
    int g ; // Granularity
    int p ; // # of processors (cores)
    int t ; // threshold
    int d ; // Debugging
    sng_int32 host ; /* return hostid */
    sng_int16 port; /* tsh port */
    sng_int16 retport; /* tsh return port */
    int sd; /* socket for reading the retport */
} sng_map_hd;

int uvrCores() { // This function calculates the total number of cores
    deployed at runtime based on .hosts
    FILE *fd;
    char nodeIP[128];
    int cores;
    int totalCores = 0;
    char uvrHostsPath[128];

    sprintf(uvrHostsPath,"%s/.uvr/uvrhosts", getenv("$HOME"));
    if ((fd = fopen("hosts", "r")) == NULL) {
        if ((fd = fopen(uvrHostsPath, "r")) == NULL) {
            printf("No ~/.uvr/uvrhosts found.\n");
            return 0;
        }
        printf("No hosts file found\n");
        return 0;
    }
    while (fscanf(fd,"%s %d", nodeIP, &cores) > 0) {
        totalCores += cores;
    }
    return totalCores;
    fclose(fd);
}

int ts_purge() {
    int sock;
    tsinit_ack out ;
    u_short this_op = htons(TSH_OP_UVRPurge);

    if ((sock = get_socket()) == -1)
    {
        perror("connectTsh::get_socket\n") ;
        return(TSPUT_ER);
    }
    if (!do_connect(sock, (sng_map_hd.host), htons(sng_map_hd.port)))
    {
        perror("connectTsh::do_connect\n") ;
        close(sock);
        return(TSPUT_ER) ;
    }
    if (!writen(sock, (char *)&this_op, sizeof(u_short)))
    {
        perror("tsput: Op code send error\n") ;
        close(sock);
        return(TSPUT_ER) ;
    }
// Wait for ack
    readn(sock, (char *)&out, sizeof(tsinit_ack)) ;
    printf("TS Purge status(%s) status(%d)\n",out.message, out.status);
    return 1;
}

int ts_init(int argc, char *argv[])
{
    sng_map_hd.host = sng_gethostid();
    if ((sng_map_hd.sd = get_socket()) == -1) {
        perror("ts_init: get socket error");
        exit(0);
    };
    sng_map_hd.retport = bind_socket(sng_map_hd.sd, 0); // get return port
    if (getenv("TSHPORT") == NULL) sng_map_hd.port = 5000;
    else sng_map_hd.port = atoi(getenv("TSHPORT"));
    printf("init done. host (%d) port (%d) return
    port(%d)\n",sng_map_hd.host,sng_map_hd.port,sng_map_hd.retport);
    return (0);
}

int tsput( tpname, tpvalue, tpsize )
        int tpsize;
        char *tpname;
        char *tpvalue;
{
    tsh_put_it out ;
    tsh_put_ot in ;
    u_short this_op = TSH_OP_PUT;
    tsh_put3_it uvrReturn;
    int tmp, sd, sock, tshSock2;
    char *buff,*st;

    this_op = htons(this_op) ;
    if ((sock = get_socket()) == -1)
    {
        perror("connectTsh::get_socket\n") ;
        return(TSPUT_ER);
    }
    if (!do_connect(sock, (sng_map_hd.host), htons(sng_map_hd.port)))
    {
        perror("connectTsh::do_connect\n") ;
        close(sock);
        return(TSPUT_ER) ;
    }
    if (!writen(sock, (char *)&this_op, sizeof(u_short)))
    {
        perror("tsput: Op code send error\n") ;
        close(sock);
        return(TSPUT_ER) ;
    }
    strcpy(out.name,tpname);
    out.priority = 1; /* Saved for later implementation */
    out.length = tpsize;
    out.host = sng_map_hd.host; /* gethostid(); */
    out.priority = htons(out.priority) ;
    out.length = htonl(out.length) ;
    out.proc_id = htonl(getpid());
// Get return port and host
/* send data to TSH */
    if ((sd = get_socket()) == -1)
    {
        perror("\nReturn sock failure::get_socket. Try a different port.\n")
                ;
        close(sock);
        exit(1);
    }
    if (!(out.port = bind_socket(sd, 0)))
    {
        perror("\nReturn sock failure::bind_socket.\n") ;
        close(sock);
        exit(1);
    }
    out.host = sng_gethostid();

/* send data to TSH */
    if (!writen(sock, (char *)&out, sizeof(tsh_put_it)))
    {
        perror("tsput: Length send error\n") ;
        close(sock);
        return(TSPUT_ER);
    }
/* send tuple to TSH */
    if (!writen(sock, tpvalue, tpsize))
    {
        perror("tsput: Value send error\n");
        close(sock);
        return(TSPUT_ER);
    }
/* read result */
    if (!readn(sock, (char *)&in, sizeof(tsh_put_ot)))
    {
        perror("tsput: read status error\n") ;
        close(sock);
        return(TSPUT_ER) ;
    }

    if (in.status != FAILURE) { // local consumed or single node stored
//printf("Put Phase 1 only done.\n");
        close(sock); // Close tsh connection so the daemon can handle others
        return((int)ntohs(in.error));
    }
    close(sock); // Free tsh socket
// Wait for UVR Put phase 2
//printf("Put Phase 2 initiated:\n");
    sock = get_connection(sd, NULL) ;
    if (!readn(sock, (char *)&uvrReturn, sizeof(uvrReturn)))
    {
        perror("\nOpPut::uvrReturn read failure\n");
        return(TSPUT_ER) ;
    }
//printf("uvrReturn request (%d)\n", uvrReturn.request);
//printf("uvrReturn status (%d)\n", uvrReturn.status);
    tsh_get_ot2 in2 ;
    while (uvrReturn.status != FAILURE) { // Read Match or Get Match
// Send tuple directly to matching clients
//printf("uvrReturn Tuple receiver:(%d|%d)\n", uvrReturn.port,
        uvrReturn.host);
        tshSock2 = connectNode(ntohs(uvrReturn.port), uvrReturn.host);
// Send tuple header
        strcpy(in2.appid,out.appid);
        strcpy(in2.name, out.name);
        in2.priority = out.priority; // Converted earlier
        in2.length = out.length;
        if (!writen(tshSock2, (char *)&in2, sizeof(in2)))
        {
            perror("Direct send to client header failure");
            close(tshSock2);
            return(TSPUT_ER);
        }
/* send tuple to TSH */
//printf("Sending (%s) to requester (%d|%d)\n", out.name,
        uvrReturn.port, uvrReturn.host);
        if (!writen(tshSock2, tpvalue, tpsize))
        {
            perror("\nOpPut::direct send to client content failure\n") ;
            close(tshSock2);
            return(TSPUT_ER) ;
        }
        if (uvrReturn.request == TSH_OP_GET) { // Get Match. No need to save
            tuple. Exit loop
            printf("\nTuple (%s) consumed.\n", out.name);
            close(tshSock2);
            return(TSPUT_ER);
        }
        close(tshSock2); // Disconnect from tuple client
// Read the next match
//printf("Waiting for UVR return: \n");
        sock = get_connection(sd, NULL) ;
        if (!readn(sock, (char *)&uvrReturn, sizeof(uvrReturn)))
        {
            perror("\nOpPut::uvrReturn read failure\n") ;
            return(TSPUT_ER) ;
        }
    }
    close(sock);
// No match or Read Match, send to tsh for storage
//printf("Put Phase 3: Store (%s)\n", out.name);
    this_op = TSH_OP_UVRPut3; // Store tuple
    this_op = htons(this_op) ;
    if ((sock = get_socket()) == -1)
    {
        perror("connectTsh3::get_socket\n") ;
        return(TSPUT_ER);
    }
    if (!do_connect(sock, (sng_map_hd.host), htons(sng_map_hd.port)))
    {
        perror("connectTsh3::do_connect\n") ;
        close(sock);
        return(TSPUT_ER) ;
    }
// Send this_op to TSH
    if (!writen(sock, (char *)&this_op, sizeof(this_op)))
    {
        perror("Store tuple op failure");
        close(sock);
        return(TSPUT_ER);
    }
// Send tuple header
    if (!writen(sock, (char *)&out, sizeof(out))) {
        perror("Store tuple header failure\n");
        close(sock);
        return(TSPUT_ER);
    }
// Send tuple
    if (!writen(sock, tpvalue, tpsize)) { // Need to covert back to host
        perror("Store tuple body failure\n");
        close(sock);
        return(TSPUT_ER);
    }
    if (!readn(sock, (char *)&in, sizeof(in)))
    {
        perror("PUT final: read status error\n") ;
        close(sock);
        getchar();
        return(TSPUT_ER);
    }
/* print result from TSH */
//printf("ts_put (%s) completed\n",tpname);
    close(sock);
    return((int)ntohs(in.error));
}

int tsget( tpname, tpvalue, tpsize )
        int tpsize;
        char *tpname;
        char *tpvalue;
{
    int sock;
    u_short this_op = TSH_OP_GET;
    tsh_get_it out;
    tsh_get_ot1 in1;
    tsh_get_ot2 in2;

    this_op = htons(this_op) ;
    if ((sock = get_socket()) == -1)
    {
        perror("tsget: get_socket error\n") ;
        close(sock);
        return(TSGET_ER) ;
    }
    if (!do_connect(sock, (sng_map_hd.host), htons(sng_map_hd.port)))
    {
        perror("tsget: TSH connection error\n") ;
        close(sock);
        return(TSGET_ER) ;
    }
    if (!writen(sock, (char *)&this_op, sizeof(u_short)))
    {
        perror("tsget: Op code send error\n") ;
        close(sock);
        return(TSGET_ER) ;
    }
    strcpy(out.expr,tpname);
    out.host = (sng_map_hd.host); /* gethostid(); */
    out.port = (sng_map_hd.retport); // Wait on ret_port
    out.len = htonl(tpsize);
    out.proc_id = htonl(getpid());
// sprintf(mapid, "sng$cid$%s", getpwuid(getuid())->pw_name);
// out.cidport = pmd_getmap(mapid, sng_map_hd.host, (u_short)PMD_PROT_TCP);
/* send data to TSH */
    if (!writen(sock, (char *)&out, sizeof(tsh_get_it)))
    {
        perror("tsget: Length send error\n") ;
        close(sock);
        return(TSGET_ER);
    }
/* read result */
    if (!readn(sock, (char *)&in1, sizeof(tsh_get_ot1)))
    {
        perror("tsget: read status error\n") ;
        close(sock);
        return(TSGET_ER) ;
    }
/* get connection in the return port */
    if (ntohs(in1.status) != SUCCESS) // Not immediately available
    {
        close(sock);
        if (tpsize == -1) return(0); /* async read */
        sock = get_connection(sng_map_hd.sd, 0) ; // wait until available
    }
/* read tuple details from TSH */
    if (!readn(sock, (char *)&in2, sizeof(tsh_get_ot2)))
    {
        perror("tsget: read result length error\n") ;
        close(sock) ;
        return(-1);
    } /* print tuple details from TSH */
    strcpy(tpname,in2.name) ;
    tpsize = ntohl(in2.length) ;
//*tpvalue = (char *) malloc(tpsize);
/* read, print tuple from TSH */
    if (!readn(sock, tpvalue, tpsize))
    {
        perror("tsget: tuple read error\n") ;
        close(sock);
        return(TSGET_ER);
    }

    printf(" TSGET. Sent in host(%ul) port(%d) tpname(%s)\n", out.host,
           out.cidport, tpname);
    close(sock) ;
    return(tpsize);
}
int tsread( tpname, tpvalue, tpsize )
        int tpsize;
        char *tpname;
        char *tpvalue;
{
    int sock;
    char mapid[MAP_LEN] ;
    u_short this_op = TSH_OP_READ;
// sng_map *link_pt;
    tsh_get_it out;
    tsh_get_ot1 in1;
    tsh_get_ot2 in2;

    this_op = htons(this_op) ;

    if ((sock = get_socket()) == -1)
    {
        perror("tsread: get_socket error\n") ;
        close(sock);
        return(TSREAD_ER) ;
    }
    if (!do_connect(sock, (sng_map_hd.host),
                    htons(sng_map_hd.port))) // Same treatment
    {
        perror("tsread: TSH connection error\n") ;
        close(sock);
        return(TSREAD_ER) ;
    }
    if (!writen(sock, (char *)&this_op, sizeof(u_short)))
    {
        perror("tsread: Op code send error\n") ;
        close(sock);
        return(TSREAD_ER) ;
    }
    strcpy(out.expr,tpname);
    out.host = (sng_map_hd.host); /* gethostid(); */
    out.port = (sng_map_hd.retport);
    printf("ts_read: return host (%d) port(%d)\n",out.host, out.port);
    out.len = htonl(tpsize);
    out.proc_id = htonl(getpid());
/* send data to TSH */
    if (!writen(sock, (char *)&out, sizeof(tsh_get_it)))
    {
        perror("tsread: Length send error\n") ;
        close(sock);
        return(TSREAD_ER);
    }
/* read result */
    if (!readn(sock, (char *)&in1, sizeof(tsh_get_ot1)))
    {
        perror("tsread: read status error\n") ;
        close(sock);
        return(TSREAD_ER) ;
    }
/* get connection in the return port */
    if (ntohs(in1.status) != SUCCESS)
    {
        close(sock);
        if (tpsize == -1) return(0); /* non-blocking read */
        sock = get_connection(sng_map_hd.sd,0) ;
    }
/* read tuple details from TSH */
    if (!readn(sock, (char *)&in2, sizeof(tsh_get_ot2)))
    {
        perror("tsread: read result length error\n") ;
        close(sock) ;
        return(-1);
    } /* print tuple details from TSH */
    strcpy(tpname,in2.name) ;
    tpsize = ntohl(in2.length) ;
//*tpvalue = (char *) malloc(tpsize);
/* read, print tuple from TSH */
    if (!readn(sock, tpvalue, tpsize))
    {
        perror("tsread: tuple read error\n") ;
        close(sock);
        return(TSREAD_ER);
    }
    close(sock) ;
    return(tpsize);
}

int tsgetv( tpname, tpvalue, tpsize )
        int tpsize;
        char *tpname;
        char **tpvalue;
{
    int sock;
    u_short this_op = TSH_OP_GET;
    tsh_get_it out;
    tsh_get_ot1 in1;
    tsh_get_ot2 in2;

    this_op = htons(this_op) ;
    if ((sock = get_socket()) == -1)
    {
        perror("tsget: get_socket error\n") ;
        close(sock);
        return(TSGET_ER) ;
    }
    if (!do_connect(sock, (sng_map_hd.host), htons(sng_map_hd.port)))
    {
        perror("tsget: TSH connection error\n") ;
        close(sock);
        return(TSGET_ER) ;
    }
    if (!writen(sock, (char *)&this_op, sizeof(u_short)))
    {
        perror("tsget: Op code send error\n") ;
        close(sock);
        return(TSGET_ER) ;
    }
    strcpy(out.expr,tpname);
    out.host = (sng_map_hd.host); /* gethostid(); */
    out.port = (sng_map_hd.retport); // Wait on ret_port
    out.len = htonl(tpsize);
    out.proc_id = htonl(getpid());
// sprintf(mapid, "sng$cid$%s", getpwuid(getuid())->pw_name);
// out.cidport = pmd_getmap(mapid, sng_map_hd.host, (u_short)PMD_PROT_TCP);
/* send data to TSH */
    if (!writen(sock, (char *)&out, sizeof(tsh_get_it)))
    {
        perror("tsget: Length send error\n") ;
        close(sock);
        return(TSGET_ER);
    }
/* read result */
    if (!readn(sock, (char *)&in1, sizeof(tsh_get_ot1)))
    {
        perror("tsget: read status error\n") ;
        close(sock);
        return(TSGET_ER) ;
    }
/* get connection in the return port */
    if (ntohs(in1.status) != SUCCESS) // Not immediately available
    {
        close(sock);
        if (tpsize == -1) return(0); /* async read */
        sock = get_connection(sng_map_hd.sd, 0) ; // wait until available
    }
/* read tuple details from TSH */
    if (!readn(sock, (char *)&in2, sizeof(tsh_get_ot2)))
    {
        perror("tsget: read result length error\n") ;
        close(sock) ;
        return(-1);
    } /* print tuple details from TSH */
    strcpy(tpname,in2.name) ;
    tpsize = ntohl(in2.length) ;
    *tpvalue = (char *) malloc(tpsize);
/* read, print tuple from TSH */
    if (!readn(sock, *tpvalue, tpsize))
    {
        perror("tsget: tuple read error\n") ;
        close(sock);
        return(TSGET_ER);
    }
/*
printf(" TSGET. Sent in host(%ul) port(%d) tpname(%s)\n",
out.host, out.cidport, tpname);
*/
    close(sock) ;
    return(tpsize);
}
int tsreadv( tpname, tpvalue, tpsize )
        int tpsize;
        char *tpname;
        char **tpvalue;
{
    int sock;
    char mapid[MAP_LEN] ;
    u_short this_op = TSH_OP_READ;
// sng_map *link_pt;
    tsh_get_it out;
    tsh_get_ot1 in1;
    tsh_get_ot2 in2;

    this_op = htons(this_op) ;

    if ((sock = get_socket()) == -1)
    {
        perror("tsread: get_socket error\n") ;
        close(sock);
        return(TSREAD_ER) ;
    }
    if (!do_connect(sock, (sng_map_hd.host),
                    htons(sng_map_hd.port))) // Same treatment
    {
        perror("tsread: TSH connection error\n") ;
        close(sock);
        return(TSREAD_ER) ;
    }
    if (!writen(sock, (char *)&this_op, sizeof(u_short)))
    {
        perror("tsread: Op code send error\n") ;
        close(sock);
        return(TSREAD_ER) ;
    }
    strcpy(out.expr,tpname);
    out.host = (sng_map_hd.host); /* gethostid(); */
    out.port = (sng_map_hd.retport);
    printf("ts_read: return host (%d) port(%d)\n",out.host, out.port);
    out.len = htonl(tpsize);
    out.proc_id = htonl(getpid());
/* send data to TSH */
    if (!writen(sock, (char *)&out, sizeof(tsh_get_it)))
    {
        perror("tsread: Length send error\n") ;
        close(sock);
        return(TSREAD_ER);
    }
/* read result */
    if (!readn(sock, (char *)&in1, sizeof(tsh_get_ot1)))
    {
        perror("tsread: read status error\n") ;
        close(sock);
        return(TSREAD_ER) ;
    }
/* get connection in the return port */
    if (ntohs(in1.status) != SUCCESS)
    {
        close(sock);
        if (tpsize == -1) return(0); /* non-blocking read */
        sock = get_connection(sng_map_hd.sd,0) ;
    }
/* read tuple details from TSH */
    if (!readn(sock, (char *)&in2, sizeof(tsh_get_ot2)))
    {
        perror("tsread: read result length error\n") ;
        close(sock) ;
        return(-1);
    } /* print tuple details from TSH */
    strcpy(tpname,in2.name) ;
    tpsize = ntohl(in2.length) ;
    *tpvalue = (char *) malloc(tpsize);
/* read, print tuple from TSH */
    if (!readn(sock, *tpvalue, tpsize))
    {
        perror("tsread: tuple read error\n") ;
        close(sock);
        return(TSREAD_ER);
    }
    close(sock) ;
    return(tpsize);
}