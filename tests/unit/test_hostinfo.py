#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
udocker unit tests: HostInfo
"""
import pwd
import sys
import pytest

try:
    import udocker
except ImportError:
    sys.path.append('.')
    sys.path.append('../')
    import udocker

from udocker.helper.hostinfo import HostInfo

##@pytest.mark.parametrize
def test_username(monkeypatch):
    """Test001 HostInfo.username"""
    def mock_pw_name():
        return 'someuser'

    monkeypatch.setattr(pwd.getpwuid, 'pw_name', mock_pw_name)
    uname = mock_pw_name()
    hinfo = HostInfo()
    assert hinfo.username() == 'someuser'
    # with pytest.raises(KeyError):
    #     hinfo.username()
