[![Downloads](https://static.pepy.tech/personalized-badge/tsubame?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/tsubame)

# Overview

This is a traceroute module written in Python. The module sends speculative probe packets and gets the results immediately. Currently, only IPv4 ICMP echo requests are supported as probe packets.

# Installation

```
$ sudo pip install tsubame
```

# Usage
## Permission
You need to have super user privileges or set CAP_NET_RAW capability to the Python interpreter binary.

## Programing Interface
```python
from tsubame import traceroute

host = 'example.com'
tr = traceroute()

results = tr.probe(host, hop_limit=8, count=1, timeout=1.0, ident=None)
```

### host

A target host name string or an IP address string.

### hop_limit

Maximum number of hops. It must be an integer from 1 to 64.

### count

The number of probe packets for each hop. It must be an integer from 1 to 4.

### ident

Identifier for parallel execution. The size must be 2 bytes. A unique value must be set for each traceroute context. By default, the PID will be set.

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
You can use as a traceroute command as follows.
```
$ sudo tsubame example.com
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

