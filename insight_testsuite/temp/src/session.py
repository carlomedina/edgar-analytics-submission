
#### data structures
from collections import deque
from collections import OrderedDict

#### handling datetime

# for creating datetime objects
import datetime
# for timezone
import pytz



class SessionStore:
	"""[summary]
	
	[description]
	"""

	def __init__(self, session_lag, file_writer):
		"""[summary]
		
		[description]
		
		Arguments:
			session_lag {[type]} -- [description]
			file_writer {[type]} -- [description]
		"""
		self.session_holder = deque([ OrderedDict({}) for i in range(session_lag)])
		self.user_holder = user_holder = OrderedDict({})
		self.max_session_length = session_lag
		self.current_time = 0
		self.file_writer = file_writer

		return

	@staticmethod
	def time_of_entry_to_session_index(latest_hit_time, current_time):
		"""[summary]
		
		[description]
		
		Arguments:
			latest_hit_time {[type]} -- [description]
			current_time {[type]} -- [description]
		
		Returns:
			[type] -- [description]
		"""
		session_index = current_time - latest_hit_time
		return session_index

	@staticmethod
	def timestamp_to_datetime(timestamp):
		return datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

	@staticmethod
	def datetime_str_to_timestamp(datetime_str):
	# sample: 2017-06-30 00:00:00
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
			# (session is only active if this condition holds: current_time - latest_hit_time < max_session_length)

			elif current_time - latest_hit_time < (self.max_session_length):
				# update the current_time stored in the SessionStore class
				self.current_time = current_time

				# convert latest_hit_time to session_index
				# note back indexing starts at -1 hence the -1 at the end
				session_index  = -1 * SessionStore.time_of_entry_to_session_index(latest_hit_time, current_time) - 1

				# # for debug purposes
				# print(current_time)
				# print(user, session_index, self.session_holder)
				
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
		# upon processing the last recorded entry
		# flush the remaining users by following the order by which they were added in user_holder
		while len(self.user_holder) > 0: 
			# pop by FIFO
			user, times = self.user_holder.popitem(last=False)

			first, last = times
			duration = (last - first) + 1
			
			# -1 due to 0-index
			index = self.max_session_length - (self.current_time - last) - 1
			count = self.session_holder[index][user]
			self.file_writer.write("{},{},{},{},{}\n".format(user, SessionStore.timestamp_to_datetime(first), SessionStore.timestamp_to_datetime(last), duration, count))

		return

	def get_current_time(self):
		return self.current_time

	def get_user_holder(self):
		return self.user_holder

	def update_current_time(self, current_time):
		self.current_time = current_time
		return

	def get_writer(self):
		return self.file_writer



# def datetime_str_to_timestamp(datetime_str):
# 	# sample: 2017-06-30 00:00:00
# 	return int(datetime.datetime(
# 				int(datetime_str[0:4]),
# 				int(datetime_str[5:7]),
# 				int(datetime_str[8:10]),
# 				int(datetime_str[11:13]),
# 				int(datetime_str[14:16]),
# 				int(datetime_str[17:19]),
# 				0,
# 				pytz.UTC
# 		).timestamp())