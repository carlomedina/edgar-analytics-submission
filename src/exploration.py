
from collections import deque
from collections import OrderedDict
from datetime import datetime
import time

start_time = time.time()


def time_of_entry_to_session_index(latest_time_of_entry, current_time):
	session_index = current_time - latest_time_of_entry
	return session_index

def add_session(session_holder, user_holder, user, current_time):
	# check if user is in any of the dictionary in session_holder
	if user in user_holder:
		# get latest_time_of_entry
		latest_time_of_entry = user_holder[user][1]

		# check if time is the same
		if latest_time_of_entry == current_time:

			session_holder[-1][user] += 1 # just increment the count

		# if time is not the same (but user is still in the queue) move the user from old session index to the latest one
		
		elif current_time - latest_time_of_entry < (lag):
			# convert latest_time_of_entry to session_index
			# note back indexing starts at -1 hence the -1 at the end
			session_index  = -1*time_of_entry_to_session_index(latest_time_of_entry, current_time) - 1

			# for debug purposes
			print(user, session_index, "\nTHESE ARE THE SESSIONS\n", session_holder)

			# place to newest session_index...
			session_holder[-1][user] = session_holder[session_index][user] + 1

			# and remove user from old session_index
			del session_holder[session_index][user]

			# update user's latest_time_of_entry (the second entry of the list value)
			user_holder[user][1] = current_time

		return

	# value of user in user holder is the time at first session hit, and the latest time
	user_holder[user] = [current_time,current_time]

	# add user session in session_holder
	session_holder[-1][user] = 1

	return

def flush(session_holder, user_holder, writer):
	# remove oldest session
	records_to_flush = session_holder.popleft()

	# insert new session
	session_holder.append({})



	for user in records_to_flush.keys():

		# formatting
		first, last = user_holder[user]
		duration = (last - first) + 1
		count = records_to_flush[user]
		out.write("{},{},{},{},{}\n".format(user, datetime.utcfromtimestamp(first).strftime("%Y-%m-%d %H:%M:%S"), datetime.utcfromtimestamp(last).strftime("%Y-%m-%d %H:%M:%S"), duration, count))

		# remove flushed users from user_holder
		del user_holder[user]

	return




def terminal_flush(session_holder, user_holder, current_time, writer):
	print("FLUSHING TERMINALLY")
	while len(user_holder) > 0: 
		user, times = user_holder.popitem(last=False)

		first, last = times
		duration = (last - first) + 1
		
		# -1 due to 0-index
		index = lag - (current_time - last) - 1
		count = session_holder[index][user]
		out.write("{},{},{},{},{}\n".format(user, datetime.utcfromtimestamp(first).strftime("%Y-%m-%d %H:%M:%S %Z"), datetime.utcfromtimestamp(last).strftime("%Y-%m-%d %H:%M:%S %Z"), duration, count))

	return


# session length
lag = 3


session_holder = deque([ OrderedDict({}) for i in range(lag)])

user_holder = OrderedDict({})
file = "./tests/log20161231.csv"
output = "./tests/results.csv"

out = open(output, 'w')
with open(file) as f:
	target_vars = ["ip", "date", "time", "cik", "accession", "extention"]
	colnames = f.readline().split(',')

	# column numbers of targetvars
	colnums = [colnames.index(var) for var in target_vars]
	previous_time = 0 

	# for debug purposes
	i = 1

	for row in f:
		# get only the relevant elements
		row_as_list = row.split(',')
		info = [row_as_list[index] for index in colnums]

		user = info[0]
		current_time = int(datetime.strptime(info[1] + " " + info[2] + " UTC",
											"%Y-%m-%d %H:%M:%S %Z").strftime('%s'))

		if previous_time < current_time:
			# skip is the number of times we should 'move' the queue by flushing
			skip = current_time - previous_time

			for i in range(skip):
				session.flush() # terminates the session of the oldest elements in the session_holder
			
			# update previous time and current time
			previous_time = current_time

		# i still do not get how useful these vars would be
		cik = info[3]
		accession = info[4]
		extention = info[5]

		# for debug purposes
		print("Processing entry {}".format(i))
		add_session(session_holder, user_holder, user, current_time)

		i+=1

	terminal_flush(session_holder, user_holder, current_time)

	out.close()


print("--- %s seconds ---" % (time.time() - start_time))









# add_session(session_holder, user_holder, "jja", 0)
# print(session_holder)

# add_session(session_holder, user_holder, "jfd", 0)
# print(session_holder)

# add_session(session_holder, user_holder, "jfd", 0)
# print(session_holder)

# flush(session_holder, user_holder)
# print(session_holder)

# add_session(session_holder, user_holder, "jfd", 1)
# print(session_holder)


# add_session(session_holder, user_holder, "hbc", 1)
# print(session_holder)

# flush(session_holder, user_holder)
# print(session_holder)

# add_session(session_holder, user_holder, "jie", 2)
# print(session_holder)

# add_session(session_holder, user_holder, "aag", 2)
# print(session_holder)


# flush(session_holder, user_holder)
# print(session_holder)

# add_session(session_holder, user_holder, "jfd", 3)
# print(session_holder)



# flush(session_holder, user_holder)
# print(session_holder)


# add_session(session_holder, user_holder, "aag", 4)
# print(session_holder)

# add_session(session_holder, user_holder, "hbc", 4)
# print(session_holder)

# terminal_flush(session_holder, user_holder, 4)

