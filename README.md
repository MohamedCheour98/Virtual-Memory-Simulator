# Virtual-Memory-Simulator

This simulator translates virtual memory addresses (like those that come from a process) to physical memory addresses (as managed by the operating system)

Page replacement algorithms such as FIFO, LRU or OPT were implemented (depending on the user choice) in order to allow the user to decide on the physical memory size by choosing the number of frames desired to be in memory. 

Usage: 

memSim <reference-sequence-file.txt> <FRAMES<FRAMES>> <PRA<FRAMES>>  
1. reference-sequence-file.txt contains the list of logical memory addresses.  
2. FRAMES is an integer <= 256 and > 0, which is the number of frames in memory. Note that a FRAMES number of 256 means logical and physical memory are of the same size.   
3. PRA is “FIFO” or “LRU” or “OPT,” representing first-in first-out, least recently used, and optimal algorithms, respectively. 


Output:
The output of the executable will have these components, printed to standard out.
1. For every address in the given addresses file, print one line of comma-separated fields, consisting of  
&emsp;&emsp;- The full address (from the reference file)  
&emsp;&emsp;- The value of the byte referenced (1 signed integer)  
&emsp;&emsp;- The physical memory frame number (one positive integer)  
&emsp;&emsp;- The content of the entire frame (256 bytes in hex ASCII characters, no spaces in between)  
2. Total number of page faults and a % page fault rate
3. Total number of TLB hits, misses and % TLB hit rate


NB: This application only supports reading operations. 
