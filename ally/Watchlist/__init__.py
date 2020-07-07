# MIT License
#
# Copyright (c) 2020 Brett Graves
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from collections.abc	import MutableMapping, MutableSet
from datetime			import datetime, timedelta
import weakref

from .methods import (
	GetWatchlist,
	GetWatchlists,
	AppendWatchlist,
	CreateWatchlist,
	DeleteWatchlist,
	DeleteFromWatchlist
)



class WatchlistWrapper ( MutableSet ):

	def __str__( self ):
		return str(self._syms)


	def __iter__ ( self ):
		return self._syms.__iter__()


	def __contains__ ( self, x ):
		return set(x) in self._syms


	def __len__ ( self ):
		return len(self._syms)


	def add ( self, x, lazy = False ):
		if isinstance(x, str):
			x = [x]

		# Appending to a non-existent watchlist does not do anything
		if not len(self._syms):
			CreateWatchlist(
				auth			= self._auth(),
				watchlist_name		= self._name,
				watchlist_symbols	= x
			).request()

		elif set(x) not in self._syms:
			result = AppendWatchlist(
				auth			= self._auth(),
				watchlist_name		= self._name,
				watchlist_symbols	= x
			).request()

		if not lazy:
			self.update()

	def update(self):
		self._syms = GetWatchlist(
					auth			= self._auth(),
					watchlist_name	= self._name
			).request()


	def discard ( self, x ):
		if x in self._syms:
			result = DeleteFromWatchlist(
				auth				= self._auth(),
				watchlist_name		= self._name,
				watchlist_symbol	= x
			).request()

	def __init__ ( self, parent, name, symbols=None):
		self._name = name
		self._auth = weakref.ref(parent._auth())
		if symbols:
			self._syms = symbols
		else:
			self.update()



class Watchlist ( MutableMapping ):
	"""Handle an accounts watchlists and symbols in a pythonic way.

	The Watchlist account object wraps ally's watchlist
	functionality and mimics python datatypes.

	Examples:

.. code-block:: python

	# See all of your watchlists
	list(a.watchlists)

	# => ['w-list1', 'my-watchlist',...]


.. code-block:: python

	# See all the symbols associated with a watchlist
	list(a.watchlist['w-list1'])

	# => ['aapl, 'googl',...]

.. code-block:: python

	# Create a watchlist, and initialize with symbols
	a.watchlist['new-watchlist'] = ['aapl,'googl',...]

.. code-block:: python

	# Remove a symbol from a watchlist
	a.watchlist['new-watchlist'].pop('aapl')

.. code-block:: python

	# Delete a watchlist
	a.watchlist.pop('new-watchlist')


	"""
	_auth = None
	_expire = None


	def __getitem__ ( self, name ):
		result = GetWatchlist(
			auth			= self._auth(),
			watchlist_name	= name
		).request()

		return WatchlistWrapper( self, name, result )


	def __setitem__ ( self, name, symbols ):
		if name in self.watched:
			# this actually appends to the list if it already exists
			self.pop(name)

		if isinstance(symbols, str):
			symbols = [symbols]

		CreateWatchlist(
			auth				= self._auth(),
			watchlist_name		= name,
			watchlist_symbols	= symbols
		).request()

		# server doesn't actually indicate if it was successful or not :-\
		# we'll just choose to be optimists
		return WatchlistWrapper(self, name)

	def __delitem__ ( self, name ):
		DeleteWatchlist(
			auth				= self._auth(),
			watchlist_name		= name
		).request()



	@property
	def _all ( self ):
		"""Reusable way to get all watchlists
		"""
		print('all is well')
		t = datetime.now()

		if self._expire is None or self._expire < t:

			# Update cache
			self._expire = t + timedelta( seconds=0.75 )

			self._lists = GetWatchlists(
				auth = self._auth(),
			).request()

		return self._lists


	# def update( self):
	#	  self.watched = _all()


	def __str__ ( self ):
		return str(self._all)


	def __iter__ ( self ):
		"""Return list to run ove
		Must be wrapped in some special iterator stuff
		so that python3 will handle it how we want
		"""
		return self._all.__iter__()


	def __len__ ( self ):
		return len(self._all)


	def __init__ ( self, parent ):
		self._auth = weakref.ref(parent.auth)
		# self.update()
		self._all
