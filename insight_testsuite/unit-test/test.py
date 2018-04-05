import sys

sys.path.append('../../src')

import session
import unittest





class test_case(unittest.TestCase):

	# initialize global vars


	# sessions = SessionStore(queue_size, test_writer)

	# # add elements to sessions
	# sessions.add_session("user1", 1)
	# sessions.add_session("user1", 1)
	# sessions.add_session("user1", 1)

	# def setUp(self):
	# 	pass

	# def tearDown(self):
	# 	pass

	def test_time_is_updated(self):
		output_path = "test.txt"
		output = open(output_path, "w")
		session_length = 5

		sessions = session.SessionStore(session_length, output)

		# add multiple elements
		sessions.add_session("user1", '2017-06-30 00:00:00')
		sessions.add_session("user2", '2017-06-30 00:00:00')
		sessions.add_session("user3", '2017-06-30 00:00:02')
		sessions.add_session("user3", '2017-06-30 00:00:03')

		# close writer
		sessions.get_writer().close()

		self.assertEqual(sessions.get_current_time(), sessions.datetime_str_to_timestamp('2017-06-30 00:00:03'))



	def test_check_add_session_error_for_invalid_time(self):
		output_path = "test.txt"
		output = open(output_path, "w")
		session_length = 5

		sessions = session.SessionStore(session_length, output)

		# add multiple elements
		sessions.add_session("user1", '2017-06-30 00:00:00')
		sessions.add_session("user2", '2017-06-30 00:00:00')
		sessions.add_session("user3", '2017-06-30 00:00:02')
		sessions.add_session("user3", '2017-06-30 00:00:03')

		# close writer
		sessions.get_writer().close()

		# add invalid user,
		# the hit time of this incoming user is before the hit time 
		# of the previously added user
		self.assertRaises(ValueError, sessions.add_session, "user4", '2017-06-30 00:00:00')


	def test_sample_flush1(self):
		output_path = "test.txt"
		output = open(output_path, "w")
		session_length = 3

		sessions = session.SessionStore(session_length, output)

		# add multiple elements
		sessions.add_session("user1", '2017-06-30 00:00:00')
		sessions.add_session("user2", '2017-06-30 00:00:01')
		sessions.add_session("user2", '2017-06-30 00:00:02')
		sessions.add_session("user2", '2017-06-30 00:00:03')
		sessions.add_session("user2", '2017-06-30 00:00:04')
		# close writer
		sessions.get_writer().close()

		# read output 
		output = open(output_path, "r")



		# add invalid user,
		# the hit time of this incoming user is before the hit time 
		# of the previously added user
		self.assertEqual(output.readline(), "user1,2017-06-30 00:00:00,2017-06-30 00:00:00,1,1\n")

		output.close()

	def test_sample_flush2(self):
		output_path = "test.txt"
		output = open(output_path, "w")
		session_length = 2

		sessions = session.SessionStore(session_length, output)

		# add multiple elements
		sessions.add_session("user1", '2017-06-30 00:00:00')
		sessions.add_session("user2", '2017-06-30 00:00:01')
		sessions.add_session("user1", '2017-06-30 00:00:02')
		sessions.add_session("user2", '2017-06-30 00:00:03')
		sessions.add_session("user2", '2017-06-30 00:00:04')
		sessions.add_session("user2", '2017-06-30 00:00:05')
		# close writer
		sessions.get_writer().close()

		# read output 
		output = open(output_path, "r")



		# add invalid user,
		# the hit time of this incoming user is before the hit time 
		# of the previously added user
		self.assertEqual(output.readline(), "user1,2017-06-30 00:00:00,2017-06-30 00:00:02,3,2\n")

		output.close()


	def test_sample_terminal_flush(self):
		output_path = "test.txt"
		output = open(output_path, "w")
		session_length = 2

		sessions = session.SessionStore(session_length, output)

		# add multiple elements
		sessions.add_session("user1", '2017-06-30 00:00:00')
		sessions.add_session("user2", '2017-06-30 00:00:00')
		sessions.add_session("user1", '2017-06-30 00:00:02')
		sessions.add_session("user2", '2017-06-30 00:00:03')
		sessions.add_session("user3", '2017-06-30 00:00:03')
		sessions.add_session("user2", '2017-06-30 00:00:05')
		sessions.add_session("user2", '2017-06-30 00:00:05')

		# terminal flush
		sessions.terminal_flush()

		# close writer
		sessions.get_writer().close()

		# read output 
		output = open(output_path, "r")


		# add invalid user,
		# the hit time of this incoming user is before the hit time 
		# of the previously added user
		
		self.assertEqual(output.readline(), "user2,2017-06-30 00:00:00,2017-06-30 00:00:00,1,1\n")
		self.assertEqual(output.readline(), "user1,2017-06-30 00:00:00,2017-06-30 00:00:02,3,2\n")
		self.assertEqual(output.readline(), "user2,2017-06-30 00:00:03,2017-06-30 00:00:05,3,3\n")
		self.assertEqual(output.readline(), "user3,2017-06-30 00:00:03,2017-06-30 00:00:03,1,1\n")
		output.close()





if __name__ == "__main__":
	unittest.main()