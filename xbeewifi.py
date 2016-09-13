# modified file from
# https://github.com/nioinnovation/python-xbee/blob/master/xbee/ieee.py


import struct
from xbee.base import XBeeBase
from xbee.python2to3 import *


class XBeeWiFi(XBeeBase):
    """
    Provides an implementation of the XBee API for IEEE 802.15.4 modules
    with recent firmware.

    Commands may be sent to a device by instansiating this class with
    a serial port object (see PySerial) and then calling the send
    method with the proper information specified by the API. Data may
    be read from a device syncronously by calling wait_read_frame. For
    asynchronous reads, see the definition of XBeeBase.
    """
    # Packets which can be sent to an XBee

    # Format:
    #        {name of command:
    #           [{name:field name, len:field length, default: default value sent}
    #            ...
    #            ]
    #         ...
    #         }
    api_commands = {"at":
                        [{'name': 'id', 'len': 1, 'default': b'\x08'},
                         {'name': 'frame_id', 'len': 1, 'default': b'\x00'},
                         {'name': 'command', 'len': 2, 'default': None},
                         {'name': 'parameter', 'len': None, 'default': None}],
                    "queued_at":
                        [{'name': 'id', 'len': 1, 'default': b'\x09'},
                         {'name': 'frame_id', 'len': 1, 'default': b'\x00'},
                         {'name': 'command', 'len': 2, 'default': None},
                         {'name': 'parameter', 'len': None, 'default': None}],
                    "remote_at":
                        [{'name': 'id', 'len': 1, 'default': b'\x07'},
                         {'name': 'frame_id', 'len': 1, 'default': b'\x00'},
                         # dest_addr_long is 8 bytes (64 bits), so use an unsigned long long
                         {'name': 'dest_addr_long', 'len': 8, 'default': struct.pack('>Q', 0)},
                         #{'name': 'dest_addr', 'len': 2, 'default': b'\xFF\xFE'},
                         {'name': 'options', 'len': 1, 'default': b'\x02'},
                         {'name': 'command', 'len': 2, 'default': None},
                         {'name': 'parameter', 'len': None, 'default': None}],
                    "tx_long_addr":
                        [{'name': 'id', 'len': 1, 'default': b'\x00'},
                         {'name': 'frame_id', 'len': 1, 'default': b'\x00'},
                         {'name': 'dest_addr', 'len': 8, 'default': None},
                         {'name': 'options', 'len': 1, 'default': b'\x00'},
                         {'name': 'data', 'len': None, 'default': None}],
                    "tx_64":
                        [{'name': 'id', 'len': 1, 'default': b'\x00'},
                         {'name': 'frame_id', 'len': 1, 'default': b'\x00'},
                         {'name': 'dest_addr', 'len': 8, 'default': None},
                         {'name': 'options', 'len': 1, 'default': b'\x00'},
                         {'name': 'data', 'len': None, 'default': None}],
                    "tx":
                        [{'name': 'id', 'len': 1, 'default': b'\x01'},
                         {'name': 'frame_id', 'len': 1, 'default': b'\x00'},
                         {'name': 'dest_addr', 'len': 2, 'default': None},
                         {'name': 'options', 'len': 1, 'default': b'\x00'},
                         {'name': 'data', 'len': None, 'default': None}]
                    }

    # Packets which can be received from an XBee

    # Format:
    #        {id byte received from XBee:
    #           {name: name of response
    #            structure:
    #                [ {'name': name of field, 'len':length of field}
    #                  ...
    #                  ]
    #            parsing: [(name of field to parse,
    #						function which accepts an xbee object and the
    #							partially-parsed dictionary of data received
    #							and returns bytes to replace the
    #							field to parse's data with
    #						)]},
    #           }
    #           ...
    #        }
    #
    api_responses = {b"\x80":
                         {'name': 'wifi_rx_64',
                          'structure':
                              [{'name': 'source_addr', 'len': 8},
                               {'name': 'rssi', 'len': 1},
                               {'name': 'options', 'len': 1},
                               {'name': 'rf_data', 'len': None}]},
                     b"\x81":
                         {'name': 'rx',
                          'structure':
                              [{'name': 'source_addr', 'len': 2},
                               {'name': 'rssi', 'len': 1},
                               {'name': 'options', 'len': 1},
                               {'name': 'rf_data', 'len': None}]},
                     b"\x82":
                         {'name': 'rx_io_data_long_addr',
                          'structure':
                              [{'name': 'source_addr_long', 'len': 8},
                               {'name': 'rssi', 'len': 1},
                               {'name': 'options', 'len': 1},
                               {'name': 'samples', 'len': None}],
                          'parsing': [('samples',
                                       lambda xbee, original: xbee._parse_samples(original['samples'])
                                       )]},
                     b"\xb0":
                         {'name': 'wifi_rx_ipv4',
                          'structure':
                              [{'name': 'src_ip', 'len': 4},
                               {'name': 'dest_port', 'len': 4},
                               {'name': 'src_port', 'len': 4},
                               {'name': 'protocol', 'len': 1},
                               {'name': 'rf_data', 'len': None}]},
                     b"\x83":
                         {'name': 'rx_io_data',
                          'structure':
                              [{'name': 'source_addr', 'len': 2},
                               {'name': 'rssi', 'len': 1},
                               {'name': 'options', 'len': 1},
                               {'name': 'samples', 'len': None}],
                          'parsing': [('samples',
                                       lambda xbee, original: xbee._parse_samples(original['samples'])
                                       )]},
                     b"\x8f":
                         {'name': 'wifi_rx_io_data',
                          'structure':
                              [{'name': 'source_addr_long', 'len': 8},
                               {'name': 'rssi', 'len': 1},
                               {'name': 'options', 'len': 1},
                               {'name': 'samples', 'len': None}],
                          'parsing': [('samples',
                                       lambda xbee, original: xbee._wifi_parse_samples(original['samples'])
                                       )]},
                     b"\x89":
                         {'name': 'tx_status',
                          'structure':
                              [{'name': 'frame_id', 'len': 1},
                               {'name': 'status', 'len': 1}]},
                     b"\x8a":
                         {'name': 'status',
                          'structure':
                              [{'name': 'status', 'len': 1}]},
                     b"\x88":
                         {'name': 'at_response',
                          'structure':
                              [{'name': 'frame_id', 'len': 1},
                               {'name': 'command', 'len': 2},
                               {'name': 'status', 'len': 1},
                               {'name': 'parameter', 'len': None}],
                          'parsing': [('parameter',
                                       lambda xbee, original: xbee._parse_IS_at_response(original))]
                          },
                     b"\x87":
                         {'name': 'wifi_remote_at_response',
                          'structure':
                              [{'name': 'frame_id', 'len': 1},
                               {'name': 'source_addr_long', 'len': 8},
                               {'name': 'command', 'len': 2},
                               {'name': 'status', 'len': 1},
                               {'name': 'parameter', 'len': None}],
                          'parsing': [('parameter',
                                       lambda xbee, original: xbee._parse_IS_at_response(original))]
                          },
                     b"\x97":
                         {'name': 'remote_at_response',
                          'structure':
                              [{'name': 'frame_id', 'len': 1},
                               {'name': 'source_addr_long', 'len': 8},
                               {'name': 'source_addr', 'len': 2},
                               {'name': 'command', 'len': 2},
                               {'name': 'status', 'len': 1},
                               {'name': 'parameter', 'len': None}],
                          'parsing': [('parameter',
                                       lambda xbee, original: xbee._parse_IS_at_response(original))]
                          },
                     }

    def _parse_IS_at_response(self, packet_info):
        """
        If the given packet is a successful remote AT response for an IS
        command, parse the parameter field as IO data.
        """
        if packet_info['id'] in ('at_response', 'remote_at_response', 'wifi_remote_at_response') and packet_info['command'].lower() == b'is' and \
                        packet_info['status'] == b'\x00':
            return self._parse_samples(packet_info['parameter'])
        else:
            return packet_info['parameter']

    def _wifi_parse_samples_header(self, io_bytes):
        """
        _parse_samples_header: binary data in XBee IO data format ->
                        (int, [int ...], [int ...], int, int)

        _parse_samples_header will read the first three bytes of the
        binary data given and will return the number of samples which
        follow, a list of enabled digital inputs, a list of enabled
        analog inputs, the dio_mask, and the size of the header in bytes
        """
        header_size = 4

        # number of samples (always 1?) is the first byte
        sample_count = byteToInt(io_bytes[0])

        # part of byte 1 and byte 2 are the DIO mask ( 16 bits )
        dio_mask = (byteToInt(io_bytes[1]) << 8 | byteToInt(io_bytes[2]))

        # upper 7 bits of byte 1 is the AIO mask
        aio_mask = byteToInt(io_bytes[3])

        # sorted lists of enabled channels; value is position of bit in mask
        dio_chans = []
        aio_chans = []

        for i in range(0,9):
            if dio_mask & (1 << i):
                dio_chans.append(i)

        dio_chans.sort()

        for i in range(0,7):
            if aio_mask & (1 << i):
                aio_chans.append(i)

        aio_chans.sort()

        return (sample_count, dio_chans, aio_chans, dio_mask, header_size)

    def _wifi_parse_samples(self, io_bytes):
        """
        _parse_samples: binary data in XBee IO data format ->
                        [ {"dio-0":True,
                           "dio-1":False,
                           "adc-0":100"}, ...]

        _parse_samples reads binary data from an XBee device in the IO
        data format specified by the API. It will then return a
        dictionary indicating the status of each enabled IO port.
        """

        sample_count, dio_chans, aio_chans, dio_mask, header_size = \
            self._wifi_parse_samples_header(io_bytes)

        samples = []

        # split the sample data into a list, so it can be pop()'d
        sample_bytes = [byteToInt(c) for c in io_bytes[header_size:]]

        # repeat for every sample provided
        for sample_ind in range(0, sample_count):
            tmp_samples = {}

            if dio_chans:
                # we have digital data
                digital_data_set = (sample_bytes.pop(0) << 8 | sample_bytes.pop(0))
                digital_values = dio_mask & digital_data_set

                for i in dio_chans:
                    tmp_samples['dio-{0}'.format(i)] = True if (digital_values >> i) & 1 else False

            for i in aio_chans:
                analog_sample = (sample_bytes.pop(0) << 8 | sample_bytes.pop(0))
                tmp_samples['adc-{0}'.format(i)] = analog_sample

            samples.append(tmp_samples)

        return samples

    def __init__(self, *args, **kwargs):
        # Call the super class constructor to save the serial port
        super(XBeeWiFi, self).__init__(*args, **kwargs)
