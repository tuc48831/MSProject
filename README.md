             Solving Traveling Salesperson Problem in Parallel

                            Stephen C. Maldony
                  email: smaldony@astro.cis.temple.edu
				tuc48831@temple.edu

                              Summer II, 1994

                       Instructor: Dr. Yuan Shi

                                 Contents


I.   Background and Problem Statement                   

II.  Description of Sequential Approach                   
     a.   Branch and Bound Algorithm               

III. Description of Parallel Approach                       
     a.   Parallel Branch and Bound Algorithm                    
     b.   Tuplespace Object Usage                           
     c.   Implemented Parallel C Code                    
             

IV.  Results                                        

V.   Observations and Conclusions                   
VI.  References                                             


                     Background and Problem Statement

The Traveling Salesperson Problem (TSP) is defined as follows:

A salesman is to visit all cities in his route and return back to
his home city.  The salesman wishes to complete his route in the
shortest amount of time, therefore he seeks the shortest route
(distance) that allows him to visit all of the cities and return
home.

The cities and distances between cities can be thought of as a
fully connected, weighted, directed graph. (This assumption will
be carried throughout the entire discussion and implementation of
the TSP.)

     example:

     Consider the following adjacency matrix, (for a weighted,
     directed graph, n=4).

                               
                1     2     3     4

          1     0     4     5     2 
          2     1     0     2     3
          3     3     1     0     3 
          4     3     2     3     0 


     Possible tours:

     1 -> 2 -> 3 -> 4 -> 1, tour length (cost) = 12

     1 -> 2 -> 4 -> 3 -> 1, tour length (cost) = 13

     1 -> 3 -> 4 -> 2 -> 1, tour length (cost) = 11

     1 -> 3 -> 2 -> 4 -> 1, tour length (cost) = 12

     1 -> 4 -> 3 -> 2 -> 1, tour length (cost) = 7

     1 -> 4 -> 2 -> 3 -> 1, tour length (cost) = 9

     
Clearly the tour 1 -> 4 -> 3 -> 2 -> 1, results in the tour with
the minimal distance and therefore is the solution to the TSP. 
The TSP has been an important part of the discussion of
computability theory and the problem has been classified as
NP-Complete [CORMEN 1].  

The problem space for the TSP grows rapidly for even small
problems.  According to [FOX 2], the problem involves creating
(N-1)!/2 tours for N cities.  

This problem is well suited for parallel processing as the
problem space can be divided among multiple processors (each
processor calculating different tours).

                 Branch and Bound Algorithm

When deciding on an algorithm for non-deterministic problem that
will be converted to a parallel algorithm, Branch and Bound
algorithms are a good choice.  Branch and Bound algorithms use
what I call a "smart brute force" approach.  A "smart brute
force" approach, solves a problem by generating all possible
solutions and maintains a minimal value that is used to prune the
search tree.  For my implementation, I further expand the
"standard" branch and bound algorithm by adding a "greedy" facet
to the solution.  An ordered search tree is maintained which
always expands the node with the best potential of leading to a
solution.

Branch and Bound Algorithms can be classified as having the
following properties:

1)   The ability to break the problem into smaller (sub)
problems.  The rule controlling the big problem will also control
the sub- problems.  In [LAWLER 3] this is referred to as a
"relaxation" of the problem.  For the TSP this is simply the
ability to create sub-tours of the graph which constrain to a
global minimum.

2)   The ability to create additional subproblems from the
current subproblem ("Branching Function").  For my implementation
of TSP, the branching function is a "brute force" method.  A new
sub-tour is created by extending the current sub tour by one
node.  This is done for all unvisited nodes, in that sub-tour.
[LAWLER 3]

3)   A rule controlling the lower bound ("Bounding Function"). 
Each time nodes are added to the subtour or a tour is complete,
the path length is compared to the global minimum. [LAWLER 3]

If the complete tour is smaller, then the new tour becomes the
new global minimum.  The current tour cost is carried with the
tour.  A traversal is not needed to determine the cost.

4)   A sub-problem selection rule is needed.  There are many
rules listed in [LAWLER 4], but I chose "ordered breadth first"
selection rule.  (The reasoning for this choice will become
apparent in the parallel implementation.)  Subtours are expanded
in a breadth first manner.  An ordered (by tour cost) list is
used to store the subtours.  Each time a subtour is selected it
is the tour of lowest cost (thus having the best potential of
leading to a minimal solution).



Pseudo code for the TSP Branch and Bound Algorithm:

input:
     n              number of cities
     seed_value     a value for a pseudo-random number generator
                    that will be used to generate the cost matrix
                    for the TSP

data structures:

     search_tree_node:
          long int current_cost
          int num_of_nodes_in_tour
          array 1 to n of char (this will be used to hold the
                tour)

TSP (n,seed_value)
     {
     initialize_ordered_queue()
     global_minimum = ì

     create initial tree-node:
          current_cost = 0
          number_of_nodes = 1
          graph_node[1] = 1   /* to simplify the algorithm the
                                 start city is always 1, this can
                                 easily be changed to allow any
                                 city to be the start city */

     while queue is not empty do
          {
          cur_tour = dequeue()

          /* check if this node should be expanded, the global
             minimum could have been updated since the subtour
             was created */

          if (cur_tour.current_cost < global_minimum)
               {

               /* try to add as many successor nodes as possible
                  to the current subtour, (this is the branching,
                  the bounding check is performed in the
                  make_child function) */

               for i=1 to n
                    {
                    branching_possible = make_child(i);
                    if (branching_possible)
                         {

                         /* check if the new tour is a complete
                            tour */
                         if (temp_node.num_nodes = n)
                              if (temp_node.cost <global_minimum)
                                   update tour and global minimum
                         else 
                              enqueue(temp_node)
                         }
                    }
               }
          }
     }


This function is the "branching" function of the Branch and Bound
algorithm.

make_child(child,cur_node,new_node)
     {
     j=1
     found=FALSE
     while ((j<=n) and (NOT found))
          {
          if (cur_node.graph_node[j] = child)
               found=TRUE
          j = j + 1
          }

     if (child is not found) and (new_tour's cost < global_min))
         {
         new_node's tour = cur_node's tour || i
         new_node.number_of_nodes = parents tour size + 1
         temp_node.cost = parent's cost + cost of parent to child

          return(TRUE)
          }
     else
          return(FALSE)
     }


This algorithm is adapted from the Branch and Bound Algorithm in
[LAWLER 5].

For the sequential code see: tsp_seq.c

                     Description of Parallel Approach

The following shows the functions of the Client and Workers for
the TSP algorithm.

The Client performs the following:

Perform above Branch and Bound Algorithm until p*c subtours are
created.
     a)   "p" is the number of computers.
     b)   "c" is a constant that is used for load balancing.

After > p*c subtours are created
     a)   Put the subtours and the global minimum (ì) into the
          tuplespace.

     b)   Monitor the tuple space for the finish signal from each
          of the workers.

After all the workers are finished

     a)   Output minimum tour length, tour and execution
          statistics.

Each Worker performs the following:

Retrieve a sub-tour from the tuplespace (blocking retrieval).

Retrieve the global minimum from the tuplespace and set local
minimum to global minimum.

While there are tuples to retrieve
     a)   Perform above branch and bound algorithm using the
          retrieved subtour as the starting point.  
     
     b)   After all tours are created for the current search tree
          node, compared the local minimum with the global
          minimum stored in the tuplespace.  If the local minimum
          is smaller then update the global minimum and the
          minimum tour.

After all the subtour tuples have been exhausted
     a)   Create a tuple indicating that worker is finished and
          put tuple into tuplespace.

Note:     The algorithm for the worker assumes that the worker
will fetch at least one tuple.  The worker will block until one
tuple (search tree node) is obtained.  This assumptions creates
the possibility that some workers will not retrieve any tuples
and continually wait even after the master is finished.  I
noticed that in some cases one or two workers never retrieved a
tuple and stayed in the blocking mode, therefore it is important
that execution of the problem be monitored.


                       Tuplespace Usage


The following tuples were used for the parallel implementation:

     Global Minimum
          name:          g_min

          description:   global minimum of tours found

          data type:     long integer


     Effective Calculations
          name:          eff_calcs

          description:   effective calculations of best tour
                         found (the number of nodes expanded to
                         generate the solution)

          data type:     double precision float


     Best minimal tour
          name:          best_tour

          description:   a character array containing the minimal
                         tour found

          data type:     char best_tour[MAX_NODES+1]


     Finished Tuple
          name:          ffff*

          description:   tuple indicating that node * has been
                         processed

          data type:     char

     Partial Tour Node
          name:          node*

          description:   contains info about the partial tour *

          data type:     struct node_tuple
                           {
                           long tour_cost;
                           int tour_length;
                           char tour[MAX_NODES+1];
                           };

   Startup information
          name:          start

          description:   contains the startup information (ie n,
                         seed value)

          data type:     struct start_tuple
                         {
                         int n;
                         long seed;
                         };

For the header file see: tsp.h

For the client code see: tspclnt.c

For the worker code see: tspwrkr.c


                          Results

For the testing of the parallel TSP, I ran the sequential code
numerous times in order to create a test case with a close-to-worst
sequential run time.  The following input was used to in all parallel tests:

     n = 15
     seed value = 778733393
     
     run time = 17.7 hours (63,746 seconds)
     host : snowhite (DEC AXP3000, Alpha, OSF/1, 100MB Mem, 2G disk)
     effective calculations = 498,914
     eff calcs/sec = 7.83

     minimal tour cost = 52907
     path: 1 5 13 9 8 12 6 14 7 10 4 2 15 3 11

                    Parallel Results

The parallel runs were conducted in a cluster of 9 DEC AXP workstations.
All processors have the same CPU are NFS mounted using node snowhite as 
the file server. The NFS client processors have 32MB memory and 440MB 
disk for local operating system files.

Tests were only conducted on a few scheduling parameters due to time
constrains (each run takes 1/2-1 hour). The sequential running timing 
on snowhite is used as the basis of comparisons.

p     c     eff calcs     eff calcs     eff calcs     run time
             master        worker        total          (sec)    

4    100      449          1289           1738        1144.096
4    300     1330           280           1610        1472.413
4    500     2215           335           2550        3365.352
5    100      554          2240           2794        2355.181
6    100      660          1853           2513        1145.683
7    100      773          1853           2626        2895.245
8    100      889          4060           4949        3668.190
9     50      503          1430           1933        886.147

Key
p =  number of processors
c =  scheduling parameter (master creates p*c nodes before
     passing control to clients)

Computing Effective Calculation Steps

Effective calculation steps are equivalent to the number of nodes
created to solve the TSP.  For the parallel execution the total
effective calculations = number of nodes created by worker +
number of nodes expanded in the subtour that leads to the
solution.  The work performed when expanding nodes not leading to
the solution are not counted.


                           Observations

For NP-complete problems, it is possible for a parallel program to use less 
number of effective calculation steps to yield the optimal solution.
In this case the timing model [Shi 7] becomes a timing study, where 
numerous test are run to gather statistics for the execution behavior of 
the algorithm.

Timing Study

Sequential execution (discussed previously):

     Tseq = 63,476 seconds
     ops/sec = 498,914/63,476 = 7.83

Parallel execution (best run):

     Tpar = 886.147 seconds, p=9, c=5
     ops/sec = 1,933/886 = 2.18


     effective parallel speed = 498,914/886.147 = 563.01 ops/sec.

     Speed-up (Sp) is calculated as follows: Sp = Tseq/Tpar
     Sp = 63,746/886 = 71.95.

     Efficiency (Eff) = Sp/p = 71.95/9 = 7.99 or 799%.

                            Conclusions

The sequential TSP program requires a large amount of memory.
Each time a node is expanded additional memory is
needed.  Each memory access is time consuming and the access is
even more time consuming if the memory page is swapped out to
disk.  In fact, many of the sequential runs of TSP did not
complete due to memory errors (running out memory or insufficient
disk swap space).

NP-complete problems are the few cases that parallel implementation 
can deliver "super linear" speed-up.  In the tests for the
TSP a "super linear" speed-up of 71.95 was achieved using 9 processors.  

The reason for the speedup is the reduced effective calculation steps
towards the optimal solution. Only the working steps that DIRECTLY
contribute to the final solution were responsible the overall elapsed
time observed by the end user. Secondly, the parallel workers requre 
only a fraction of the total memory space on each processor, thus
reducing the swapping costs considerably. Although communication time 
is an important part of any parallel
program, this time did not adversely affect the runtime of the
parallel program.  

The best run times were achieved when the master created between
400 and 1000 subtours.  The scheduling parameter (c) was adjusted
so that the master created the proper number of subtours.

Tests where the master created > 1000 subtours, the run time was
considerably higher than runs with lower number of subtours.  The
increased run time is due to communication overhead.  The more
subtours created the greater the communication time.

Tests where the master created < 400 subtours, the increased run
time is due to work imbalance. Since the actual computing requirements
implied in subtours vary widely and the master cannot terminate only if
all subtours are computed, the probablity of a processor hanging on to
a "heavy" subtour thus slowing down the entire application is increased.
Secondly, the memory problem that plagued the sequential program
can occur on some processors.  The problem is further complicated by 
adding in the communication overhead. These result in a run time worse 
that the sequential program.

The best efficiency calculated is 799% using 9 processors. 

In concluding, for the special case of NP-complete
problems, parallel implementation can achieve run times considerably
better that their sequential counterparts.  I also feel that
parallel algorithms such as the TSP should be considered whenever
problems have massive memory usage and problem space management
(search trees, etc).

                         References

[1]  Cormen, T. H., Leiserson, C.E., Rivest, R.L. Introduction to
     Algorithms. New York: McGraw-Hill Book Company, 1990. p 959.

[2]  Fox, G.C., Johnson, M.A., Lyzenga, G.A., Otto, S.W., Salmon,
     J.K., Walker, D.W. Solving Problems on Concurrent
     Processors,Volume I. Englewood Cliffs, NJ: Prentice
     Hall, 1988. p 213.

[3]  Lawler, E.L., Lenstra, J.K., Rinnooy Kan, A.H.G., Shmoys,
     D.B. The Traveling Salesman Problem. Chichester: John Wiley
     & Sons, 1985. p 362.

[4]  Lawler, E.L., Lenstra, J.K., Rinnooy Kan, A.H.G., Shmoys,
     D.B. The Traveling Salesman Problem. Chichester: John Wiley
     & Sons, 1985. p 367-370.

[5]  Lawler, E.L., Lenstra, J.K., Rinnooy Kan, A.H.G., Shmoys,
     D.B. The Traveling Salesman Problem. Chichester: John Wiley
     & Sons, 1985. p 364.

[6]  Shi, Y., Creating Effective Parallel Programs -- A Toturial to
     Synergy V2.0. Class notes, CIS750, Summer II, 1994.

[7]  Shi, Y., Timing Models -- Towards the Scalability Analysis of
     Parallel Programs, Class notes, CIS669, Fall, 1994.
