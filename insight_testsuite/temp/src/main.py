
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

	# create output file writer
	output = open(output_path, "w")

	# initialize SessionStore object
	sessions = SessionStore(session_length, output)

	# for benchmarking purposes
	start_execution = time.time()

	# read log data file
	with open(input_path, "r") as f:
		# read first line of the log input file
		target_vars = ["ip", "date", "time", "cik", "accession", "extention"]
		colnames = f.readline().replace("\n", "").split(',')

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


			current_time = "{} {}".format(start_date, start_time)
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



