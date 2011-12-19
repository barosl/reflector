#!/usr/bin/env python
# -*- coding: utf-8 -*-

import selector

execfile('config.py')

class Server(selector.Server):
	def on_accept(self, sock):
		pass

	def on_data(self, sock, line):
		if line == 'close':
			self.stop()
		else:
			for _sock in self.socks:
				if _sock != sock: self.send_line(_sock, line)

	def on_close(self, sock):
		pass

def main():
	Server(cfg['host'], cfg['port']).start()

if __name__ == '__main__':
	main()
