
# misc
import time
import sys

# class to process data
from session import SessionStore


if __name__ == '__main__':
	input_path = sys.argv[1]
	session_length_path = sys.argv[2]
	output_path = sys.argv[3]
	
	# read inactivity_period.txt
	with open(session_length_path) as f:
		try:
			session_length = int(f.readline())

		# stop the program if the string is not coercible to integer or the integer is not between 1 to 86400, inclusive
		except ValueError:
			raise ValueError("The content of inactivity_period.txt is not coercible to an integer!")
			raise SystemExit(0)

		if session_length < 1 or session_length > 86400:
			print("The integer in inactivity_period.txt is beyond the specifications")
			raise SystemExit(0)

	# session lag is the queue size for the data structure holding all current active sessions
	# it is one more than session_length because it also holds the sessions that are about to be flushed 
	# (ie those that are at index zero)

	# e.g. say session_length is 1

	# at time t = k

	#  the queue would look something like this:
	#  where each entry is a dictionary of users
	#   +---------+---------+
	#   |   k-1   |    k    |
	#   +---------+---------+

    # supposed we finished processing all users with hit time of t = k
    # the next user that we are about to processed is has time t = k + 1

    # before we add the user, we have to flush those users in k-1 index
    # hence we need a queue size that is 1 more than the session length

	session_lag = session_length + 1

	# create output file writer
	output = open(output_path, "w")

	# initialize SessionStore object
	sessions = SessionStore(session_lag, output)

	# for benchmarking purposes
	start_execution = time.time()

	# read log data file
	with open(input_path, "r") as f:
		# read first line of the log input file
		target_vars = ["ip", "date", "time", "cik", "accession", "extention"]
		colnames = f.readline().split(',')

		# column index of targetvars
		try:
			column_indices = [colnames.index(var) for var in target_vars]
		except ValueError as err:
			raise ValueError("The input log file: {} is invalid because {}".format(input_path, err))


		# initialize previous time to compare current time to
		previous_time = sessions.get_current_time()

		# for debug purposes
		# i = 1

		for row in f:
			# get only the relevant elements
			row_as_list = row.split(',')
			info = [row_as_list[index] for index in column_indices]

			user = info[0]
			start_date = info[1]
			start_time = info[2]

			
			current_time = sessions.datetime_str_to_timestamp("{} {}".format(start_date, start_time))

			# if new user has a hit time that happened after the hit time of the previous user
			# initiate flushing of the queue
			if previous_time < current_time:

				# skip is the number of times we should 'move' the queue by flushing
				# e.g. if the hit time of the current user happened 3 seconds after the hit time of 
				# the previous user, flush the oldest three entries of the queue
				skips = current_time - previous_time if previous_time != 0 else 0

				for skip in range(skips):
					sessions.flush() # terminates the session of the oldest elements in the session_holder

				# update previous time and current time
				previous_time = current_time
				sessions.update_current_time(current_time)


			# # these variables can be obtained but is currently of no significant use
			# # added here for refactoring purposes (in particular, if we want to track the specific files)
			# # being accessed
			# cik = info[3]
			# accession = info[4]
			# extention = info[5]

			# add user session
			sessions.add_session(user, current_time)

			# for debug purposes
			# i+=1
			# print("Processing entry {}".format(i))

		# once finish reading the input, flush remaining sessions
		sessions.terminal_flush()

		# close connection to the output file
		sessions.get_writer().close()

	# for benchmarking
	print("--- %s seconds ---" % (str(time.time() - start_execution)))



