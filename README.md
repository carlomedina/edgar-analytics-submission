# Edgar Analytics Challenge Submission

## Overview

The Insight Data Engineering coding challenge involves the processing of recorded website hits in the Security and Exchange Commission's Electronic Data Gathering, Analysis, and Retrieval (EDGAR) system. It aims to calculate the number of hits a given user made during a session and its duration. Session is defined as a period of time where the gap the user's successive hits is less than some threshold. Beyond this (inactivity) threshold, a user's new incoming hit would be registered as the start of a new session.

## Approach

For the purposes of this challenge, I assumed that the data coming from EDGAR's log file is sanitized, especially the key data fields, `ip`, `date`, `time`. This seems to be the case after processing test log files coming from EDGAR's database.

Further, all datetime timestamps (derived by concatenating `date` and `time`) are assumed to be rounded to the nearest second, and thus, we can treat time as a discrete numeric entity (think integers) rather than a continuous construct (think real numbers). From this assumption, I derived the data structures that I will use to store the sessions data.

I also assumed that all current active sessions at any given time would fit in the memory of my computer. The limitation is based on the fact that the input file is read line-by-line, and all sessions that were expired are written to disk and removed from memory. In case that active sessions would be massive, I was thinking of running a Redis instance in an external server to hold the values I'm tracking. Redis has built in queues and ordered dictionary which can be integrated easily with my current implementation.

### Data Structures

#### `session_holder`: a queue
From above, I expained how time can be thought of as a discrete element. Hence, we can convert time into a sequence of integers. 

The size of the queue is the value of the threshold of allowed inactivity plus 1--the rationale behind this will be explained below.

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

At the start of processing the data, we take the time of the first user. Say this time is t = 1. We then add all the users whose time is  t = 1 by sequentially going down te file. All these users will be added at the last element of the queue. 

Suppose that the next user happens at t = 2 (one second after). We shift the queue by one by dequeuing the leftmost entry (in this case it is still empty), and adding an empty dictionary at the end. We then add all users who hit at t = 2. **This process essentially is like moving a discrete time window (the box) through a discrete time points.**

Similar process occur until we reach time t = 5. As we move to t = 6, all those users who accessed the website at t = 1 have their sessions expired at t = 5. Once we found a user whose hit time is t = 6, before we process them, we will deque these users whose last hit time is t = 1 and flush them and write their records to file. After dequeuing and queuing a new empty dictionary, we can then process the users with hit time t = 6. This is the reason behind the queue size being one more than the length of the session threshold: [users to flush, active, active, active, active]

Now, I briefly explain how I handle users who accessed the website multiple times in a given session. I would use the same diagram as above to demonstrate. Suppose that Alice accessed the site at t = 1 the first time. At t = 3, Alice accessed the file again. 

Using the `user_holder` (explained below), I am able to know that Alice has an active session, and I can know that her last hit to the website was at t = 1. From here, I can determine the index of the queue where Alice is currently placed (i.e. index 2, which is 3-1). I can thus move Alice from the dictionary at index 2, and add her to the dictionary at index 4 (the most recent) with and incrementing her current count by one.

The same process continues until we hit the end of the file. At this point, we cannot just flush the data by following the index of `session_holder` since the specification of the problem requires that we output those with remaining active sessions in the order by which they **first** hit the site. For that, we use the ordered dictionary `user_holder`

The best way to explain the process is through this animation
![](./images/insight-demo.gif)

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

As a session is dequeued from `session_holder`, the users whose `ip` value appears in session holder are also removed from `user_holder` so as to create a new record with a new time of first hit value if a new session is created. Also, as a session is dequeued, the value of the user (i.e. the list [time of first hit, time of latest hit]) is called and is included in the data being flushed to file, together with the counts found in `session_holder` and the difference between those two times.

At the processing the last entry of the log file, we flush the entire active sessions sequentiall based on when they first acessed the data. This is essentially the same as when they were first added in `user_holder`. Thus, all we have to do is to pop the ordered dictionary from the left, get the user `ip`, and it's corrensponding value (ie. [time of first hit, time of latest hit], and get the user counts from `session_holder`.


## Implementation

This submission is implemented in **Python3** with the following dependencies,

- `collections`
- `datetime`
- `pytz`
- `time`
- `sys`

which are all preloaded libraries in Python3, to the best of my knowledge. Python3 is required to have the timestamp() method in datetime.datetime classes.

The submission includes two files,

- main.py
- session.py

`session.py` contains the `SessionStore` class that contains the data structures stated above. It also has the methods for adding the user infos, and flushing user session info to file. (I decided to implement this using a class because it's been a while since I last did a project that uses OOP--this exercise was a good refresher).

### Run instruction
The run instruction is based on the specifications of the challenge. One has to run the bash script `run.sh`

## Wishlist
I got busy with school work and a case competition for a management consulting company. I wanted to clean up sessionization.py more by abstracting all the processes of reading the log, checking time, etc. into the `SessionStore` class to get a much cleaner `main.py` script.

Also, I wanted to do more rigorous testing if the aggregation of sessions are really done correctly based in the specifications, but that would require building the output another way.

(UPDATE: I managed to squeezed in some unit testing and two more tests using a curated web logs. I also managed to abstract the checking of time into `SessionStore` however the add_session method became too long. I would refactor it if I had more time.)

## Miscellaneous

## Directory Structure
```
├── images
│   └── insight-demo.gif
├── input
│   ├── inactivity_period.txt
│   └── log.csv
├── insight_testsuite
│   ├── results.txt
│   ├── run_tests.sh
│   ├── tests
│   │   ├── test_1
│   │   │   ├── input
│   │   │   │   ├── inactivity_period.txt
│   │   │   │   └── log.csv
│   │   │   ├── output
│   │   │   │   └── sessionization.txt
│   │   │   └── README.md
│   │   ├── test_2
│   │   │   ├── input
│   │   │   │   ├── inactivity_period.txt
│   │   │   │   └── log.csv
│   │   │   ├── output
│   │   │   │   └── sessionization.txt
│   │   │   └── README.md
│   │   └── test_3
│   │       ├── input
│   │       │   ├── inactivity_period.txt
│   │       │   └── log.csv
│   │       ├── output
│   │       │   └── sessionization.txt
│   │       └── README.md
│   └── unit-test
│       ├── test.py
│       └── test.txt
├── output
│   ├── README.md
│   └── sessionization.txt
├── README.md
├── run.sh
└── src
    ├── main.py
    ├── README.md
    ├── session.py
    └── session.pyc
 ```
