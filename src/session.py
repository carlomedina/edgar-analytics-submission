
#### data structures
from collections import deque
from collections import OrderedDict

#### handling datetime

# for creating datetime objects
import datetime
# for timezone
import pytz




class SessionStore:
	"""SessionStore is the main workhorse of processing the sessions data
	
	SessionStore contains a queue, and an ordered dictionary that stores the values of sessions 
	that are currently active

	Its main methods include adding the user into the queue and the ordered dictionary and 
	dequeing users and removing from the dictionary once their session expires and writes the data into a file
	"""

	def __init__(self, session_lag, file_writer):
		"""Initializes an instance of a SessionStore class

		Creates the queue with size = maximum inactivity time + 1 = session_lag
		
		Creates an ordered dictionary which will contain the user ip as the key and 
		[time of first hit, time of latest hit] as the value

		Initializes current time as zero (all times are expected to be greater than zero)
		since we are converting timestamps that are after starting epoch

		Stores the connection of the output file writer

		
		Arguments:
			session_lag {int} -- this will be the queue size. it is the length of maximum inactivity time + 1
			file_writer {file} -- connection to the file writer
		"""
		self.session_holder = deque([ OrderedDict({}) for i in range(session_lag)])
		self.user_holder = user_holder = OrderedDict({})
		self.max_session_length = session_lag
		self.current_time = 0
		self.file_writer = file_writer
		return

	@staticmethod
	def time_of_entry_to_session_index(latest_hit_time, current_time):
		"""Returns how far is the user from the newest element from the queue

		This is in essence the value of time elapsed in seconds
		One can think of this as a measure of how far is the user's latest record from the
		the latest entry in the queue

		For example, suppose we have a queue size of 5, the current time is t = 10, and the user's
		latest hit time is t = 6. Then, the user's session_index is 4. In particular, the user's latest hit time
		is the fourth entry from the newest element in the queue

		
		Arguments:
			latest_hit_time {int} -- [description]
			current_time {int} -- [description]
		
		Returns:
			int -- the session index
		"""
		session_index = current_time - latest_hit_time
		return session_index

	@staticmethod
	def timestamp_to_datetime(timestamp):
		"""converts timestamp (seconds from epoch) to datetime string in the following
		format %Y-%m-%d %H:%M:%S
		
		Arguments:
			timestamp {int} -- seconds from epoch
		
		Returns:
			str -- datetime in the specified format
		"""
		return datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

	@staticmethod
	def datetime_str_to_timestamp(datetime_str):
		"""converts datetime string to seconds since epoch
		sample: 2017-06-30 00:00:00

		Arguments:
			datetime_str {str} -- datetime string with the following format
		
		Returns:
			int -- the specified datetime as seconds from epoch
		"""
	
		return int(datetime.datetime(
					int(datetime_str[0:4]),
					int(datetime_str[5:7]),
					int(datetime_str[8:10]),
					int(datetime_str[11:13]),
					int(datetime_str[14:16]),
					int(datetime_str[17:19]),
					0,
					pytz.UTC
			).timestamp())
		
	def add_session(self, user, current_time):
		"""adds/updates user information to the queue and dictionary
		
		Arguments:
			user {str} -- unique user ip address
			current_time {int} -- timestamp of user's hit time (as seconds since epoch)
		"""

		# check if user has a current session
		if user in self.user_holder:

			# get user's time of latest hit in its session
			latest_hit_time = self.user_holder[user][1]

			# check if time of latest hit occured at current time
			if latest_hit_time == current_time:

				self.session_holder[-1][user] += 1 # increment the hit count

			# if latest hit time is not the same as the current hit time
			# but user has an active session (i.e. still in the session_holder queue) 
			# move the user from its current queue index to the most recent queue index 
			# (NOTE: session is only active if this condition holds: current_time - latest_hit_time < max_session_length)

			elif current_time - latest_hit_time < (self.max_session_length):
				# update the current_time stored in the SessionStore class
				self.current_time = current_time

				# convert latest_hit_time to session_index
				# note back indexing starts at -1 hence the -1 at the end
				session_index  = -1 * SessionStore.time_of_entry_to_session_index(latest_hit_time, current_time) - 1
				
				# place to newest session_index...
				self.session_holder[-1][user] = self.session_holder[session_index][user] + 1

				# and remove user from old session_index
				del self.session_holder[session_index][user]

				# update user's latest_hit_time (the second entry of the list value)
				self.user_holder[user][1] = current_time

			return

		# value of user in user holder is [the time at first session hit, the latest time]
		# in this case, at initialization, these two values are equal 
		self.user_holder[user] = [current_time,current_time]

		# add number of hits 
		self.session_holder[-1][user] = 1
		return

	def flush(self):
		"""deques entries whose session ended and write the sessions to file

		As `flush` removes the oldest entries, it also appends and empty dictionary
		where the incoming user hits would be placed
		
		"""
		# remove oldest session
		records_to_flush = self.session_holder.popleft()

		# insert an empty dictionary containing the incoming users
		self.session_holder.append({})


		for user in records_to_flush.keys():
			# formatting
			first, last = self.user_holder[user]
			duration = (last - first) + 1
			count = records_to_flush[user]

			# write to output
			self.file_writer.write("{},{},{},{},{}\n".format(user, SessionStore.timestamp_to_datetime(first), SessionStore.timestamp_to_datetime(last), duration, count))

			# remove flushed users from user_holder
			del self.user_holder[user]
		return

	def terminal_flush(self):
		"""deques remaining sessions in the session_holder once the last entry has been processed

		Due to the ordered nature of user_holder, we are able to processed the sessions that have not been 
		terminated by expiration of session (but by the fact that there is no more following records) chronologically

		"""
		# upon processing the last recorded entry
		# flush the remaining users one-by-one by 
		# following the order by which they were added in user_holder
		while len(self.user_holder) > 0: 
			# pop by FIFO
			user, times = self.user_holder.popitem(last=False)

			first, last = times
			duration = (last - first) + 1
			
			# -1 due to 0-index
			index = self.max_session_length - (self.current_time - last) - 1
			count = self.session_holder[index][user]	# get number of hits
			self.file_writer.write("{},{},{},{},{}\n".format(user, SessionStore.timestamp_to_datetime(first), SessionStore.timestamp_to_datetime(last), duration, count))
		return

	def get_current_time(self):
		"""exposes the timestamp of the newest entry of the queue

		Returns:
			int -- the timestamp of the newest entry of the queue 
		"""
		return self.current_time

	def update_current_time(self, current_time):
		"""updates the current time of the queue
		"""
		self.current_time = current_time
		return

	def get_writer(self):
		return self.file_writer

	# for debug purposes
	def get_user_holder(self):
		return self.user_holder

