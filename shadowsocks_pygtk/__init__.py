#!/usr/bin/env python3
# coding: utf8
#
# Copyright (C) 2017 songww
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

from shadowsocks_pygtk.shadowsocks import Shadowsocks


def main():
    application = Shadowsocks()

    try:
        code = application.run(sys.argv)
    except SystemExit as e:
        code = e.code

    sys.exit(code)


if __name__ == '__main__':
    main()
