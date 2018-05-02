#!/usr/bin/env python
import asyncio
import unittest
from unittest import mock
from async_mock import patch
from async_receive import receive


def _run(coro):
    """Run the given coroutine."""
    return asyncio.get_event_loop().run_until_complete(coro)


class TestReceive(unittest.TestCase):
    def test_invalid_packet(self):
        self.assertRaises(ValueError, _run, receive('FOO', 'data'))

    @patch('async_receive.send_to_client')
    def test_ping(self, send_to_client):
        _run(receive('PING', 'data'))
        send_to_client.mock.assert_called_once_with('PONG', 'data')

    @patch('async_receive.send_to_client')
    @patch('async_receive.trigger_event')
    def test_message(self, trigger_event, send_to_client):
        trigger_event.mock.return_value = 'my response'
        _run(receive('MESSAGE', 'data'))
        trigger_event.mock.assert_called_once_with('message', 'data')
        send_to_client.mock.assert_called_once_with('MESSAGE', 'my response')


if __name__ == '__main__':
    unittest.main()
