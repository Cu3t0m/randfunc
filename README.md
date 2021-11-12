# randfunc
-----------------------

### Installation
- From source (for the latest untested version)
```
pip install git+https://github.com/Cu3t0m/randfunc.git
```
- With pip
```
pip install randfunc
```
-----------------------
### Example use

#### String
```
>>> randfunc.string(10)
'iDa7FZl7rW'
```
#### Integer
```
>>> randfunc.integer(0, 100)
15
```
#### Array
```
>>> randfunc.array('123456789', 5)
['7', '5', '9', '3', '2']
```
#### Datetime
```
datetime.datetime(2016, 5, 24, 16, 34, 2, 726892)
>>> randfunc.datetime(
... start=datetime.datetime(year=2016, month=1, day=1),
... end=datetime.datetime(year=2016, month=12, day=31))
datetime.datetime(2016, 2, 13, 21, 34, 58, 268978)
```

#### Mail Address
```
>>> randfunc.mail()
'iYpZpde@jslx4.com'
```

#### MAC Address
```
>>> randfunc.mac_address()
'fe:23:1d:1d:ec:be'
```
It's also possible to define an own prefix.
```
>>> randfunc.mac_address('02:00:00')
'02:00:00:84:62:3e'

>>> mac_address('02:00:00:00:00')
'02:00:00:00:00:63'
```

#### IPv4 Address
```
>>> randfunc.ipv4address()
'108.146.211.120'
```

#### IPv6 Address
```
>>> randfunc.ipv6address()
'7dd7:c3ee:b1b6:ba15:6bb6:c908:541a:efe4'
```

----------------------------
Contributing
----------------------------

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)