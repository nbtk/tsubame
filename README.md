# Overview

This is traceroute module written in Python. The module sends speculative probe packets and gets results immediately. However, this module may send too many wasted packets. You should specify the minimum number of hops required to reach the target. The module currently supports only IPv4 ICMP Echo Request.

# Installation

No need to install. Just import the module.

# Usage
## Permission
You need super user permission or set CAP_NET_RAW capability to the Python binary.

## Programing Interface
```python
from traceroute import traceroute

host = 'example.com'
tr = traceroute()

results = tr.probe(host, hop_limit=8, count=1, timeout=1.0, ident=None)
```

### host

A target host name string or an IP address string.

### hop_limit

Maximum number of hops. It must be 1 to 64 integer.  You should specify the minimum number of hops required to reach the target.

### count

Number of probe packets to each hop. It must be must be 1 to 4 integer.

### ident

Identifier for parallel execution. When running in parallel, a unique value must be set in each context. It must be length 2 bytes array. If default or set None, uses PID.

## Result Structure

### Nested structure
```python
[
   [ first_probe, second_probe, ..., nth_probe ], # hop 1
   [ first_probe, second_probe, ..., nth_probe ], # hop 2
...
   [ first_probe, second_probe, ..., nth_probe ], # hop n
]
```

###  Each result item

If received a response,
```
(from_addr, delay_sec, is_target)
```
e.g.
```
('192.168.1.1', 0.0011992454528808594, False)
```

else
```
None
```

# Example

## Simple traceroute command
There is a simple traceroute code at the main block in the module. You can use as a command like this.
```
$ sudo ./traceroute.py example.com
traceroute to example.com (93.184.216.34), 32 hops max
1  192.168.1.1  1.146 ms  1.374 ms  1.616 ms
2  * * *
3  * * *
4  * * *
5  * * *
6  111.87.3.234  118.376 ms  118.503 ms  119.928 ms
7  62.115.180.213  123.618 ms  123.894 ms  125.392 ms
8  62.115.155.89  120.319 ms  121.756 ms  122.066 ms
9  152.195.85.133  121.776 ms  123.551 ms  123.544 ms
10  93.184.216.34  127.130 ms  127.199 ms  129.053 ms
```

