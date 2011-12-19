import socket
import select

class Server:
	def on_accept(self, sock): pass
	def on_data(self, sock, line): pass
	def on_close(self, sock): pass

	selector = None
	serv_sock = None

	socks = {}
	sock_fds = {}
	sock_bufs = {}

	loop_flag = False

	def __init__(self, host, port):
		self.selector = select.epoll()

		self.serv_sock = socket.socket()
		self.serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serv_sock.bind((host, port))
		self.serv_sock.listen(5)
		self.selector.register(self.serv_sock.fileno(), select.EPOLLIN)

	def start(self):
		self.loop_flag = True

		while self.loop_flag:
			for fd, ev in self.selector.poll(1):
				if fd == self.serv_sock.fileno():
					sock, addr = self.serv_sock.accept()
					self.selector.register(sock.fileno(), select.EPOLLIN)

					self.socks[sock] = None
					self.sock_fds[sock.fileno()] = sock
					self.sock_bufs[sock] = ''

					self.on_accept(sock)
				elif ev & select.EPOLLIN:
					sock = self.sock_fds[fd]

					try:
						buf = sock.recv(1024)
						if not buf: raise socket.error
					except socket.error:
						self.selector.unregister(fd)
						sock.close()

						del self.socks[sock]
						del self.sock_fds[fd]
						del self.sock_bufs[sock]

						self.on_close(sock)
					else:
						self.sock_bufs[sock] += buf
						while '\n' in self.sock_bufs[sock]:
							line, self.sock_bufs[sock] = self.sock_bufs[sock].split('\n', 1)
							line = line.strip()

							self.on_data(sock, line)
				else:
					print >> sys.stderr, 'unknown selector event: %d' % ev # FIXME

		for fd, sock in self.sock_fds.iteritems():
			self.selector.unregister(fd)
			sock.close()

			self.on_close(sock)

		self.socks.clear()
		self.sock_fds.clear()
		self.sock_bufs.clear()

		self.selector.unregister(self.serv_sock.fileno())
		self.serv_sock.close()

		self.selector.close()

	def stop(self):
		self.loop_flag = False

	def send_line(self, sock, line):
		sock.send(line+'\n')
