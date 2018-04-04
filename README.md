# Edgar Analytics Challenge Submission

## Overview

The Insight Data Engineering coding challenge involves the processing of recorded website hits in the Security and Exchange Commission's Electronic Data Gathering, Analysis, and Retrieval (EDGAR) system. It aims to calculate the number of hits a given user made during a session and its duration. Session is defined as a period of time where the gap the user's successive hits is less than some threshold. Beyond this (inactivity) threshold, a user's new incoming hit would be registered as the start of a new session.

## Approach

For the purposes of this challenge, I assumed that the data coming from EDGAR's log file is sanitized, especially the key data fields, `ip`, `date`, `time`. This seems to be te case after processing test log files coming from EDGAR's database.

Further, all observations of the derived `datetime` variable (concatenating `date` and `time`) are assumed to be rounded to the nearest second, and thus, we can treat time as a discrete numeric entity (think integers) than a continuous construct (think real numbers). From this assumption, I derived the data structures that I will use to store the sessions data.

### Data Structures

I think that the best way to explain the data structures that I used is through the following diagrams

#### `session_holder`: a queue
Since we can think of time as a discrete element, we can convert time as a sequence of integers. 

The size of the queue is the value of the threshold of allowed inactivity plus 1 the rational behind this will be explained below.

The queue is structured as:
```
[
	{
		user1: 1, # key, value = ip, count of hits
		user2: 5,
	},
	{
		user3: 1, 
	},
	...
	{
		user9: 20
	}

]
```

For the sake of demonstration, let 4 secs be the inactivity time threshold, hence the size of the queue is 5, and for now, assume that each user hit the website once. 

At the start of processing the data, I take the time of the first user. Say this time is t = 1. I then add all the users whose time is  t = 1 by sequentially going down te file. All these users will be added at the last element of the queue. Suppose that the next user happens at t = 2 (one second after). We shift the queue by one by dequeing the leftmost entry (in this case it is still empty), and adding an empty dictionary at the end. We then add all users who hit at t = 2. This process essentially is like moving a discrete time window through a discrete time points. Similar process occur until we reach time t = 5. As we move to t = 6, all those users who accessed the website at t = 1 have their sessions expired at t = 5. Once we found a user whose hit time is t = 6, before we process them, we will deque these t = 1 users and flush them and write their records to file. After dequeing and queuing a new empty dictionary, we can then process the users with hit time t = 6. 

Now, I briefly explain how I handle users who accessed the wesbite multiple times in a given session. I would use the same diagram as above to demonstrate. Suppose that a Alice accessed the site at t = 1 the first time. At t = 3, Alice accessed the file again. Using the `user_holder` (explained below), I am able to know that Alice has an active session, and I can know that her last hit to the website was at t = 1. From here, I can determine the index of the queue where Alice is currently placed (i.e. index 2, which is 3-1). I can thus move Alice from the dictionary at index 2, and add her to the dictionary at index 4 (the most recent) with and incrementing her current count by one.

The same process continues until we hit the end of the file. At this point, we cannot just flush the data by following the index of `session_holder` since the specification of the problem requires that we output those with remaining active sessions in the order by which they **first** hit the site. For that, we use the ordered dictionary `user_holder`



#### `user_holder`: an ordered dictionary

`user_holder` has the following structure

```
{
	user1 : [1, 3],		# key, value = user ip, [time of first hit, time of latest hit]
	user2 : [1, 2],
	user3 : [2, 3]
}

```

Every user that is being processed in the log is either added to the `user_holder`: if the user is not present as a key, or modified: if the user is already present, update the time of latest hit based on the time written in the log. 

As a session is dequed from `session_holder`, the users whose `ip` value appears in session holder are also removed from `user_holder` so as to create a new record with a new time of first hit value if a new session is created. Also, as a session is dequed, the value of the user (i.e. the list [time of first hit, time of latest hit]) is called and is included in the data being flushed to file, together with the counts found in `session_holder` and the difference between those two times.


## Implementation

This submission is implemented in Python3 with the following dependencies,

- `collections`
- `datetime`
- `pytz`
- `time`
- `sys`

which are all preloaded libraries in Python3, to the best of my knowledge

The submission includes two files,

- sessionization.py
- session.py

`session.py` contains the `SessionStore` class that contains the data structures stated above. It also has the methods for adding the user infos, and flushing user session info to file. (I decided to implement this using a class because it's been a while since I last did a project that uses OOP).

### Run instruction
The run instruction is based on the specifications of the challenge. One has to run the bash script `run.sh`

### Wishlist
I got busy with school and a case competition. I wanted to clean up sessionization.py more by abstracting all the processes of reading the log, checking time, etc. into the `SessionStore` class to get a much cleaner `session.py` (main.py) script.

Also, I wanted to do more rigorous testing if the aggregation of sessions are really done correctly based in the specifications, but that would require building the output another way.
