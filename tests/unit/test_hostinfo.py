#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
udocker unit tests: HostInfo
"""
import pytest
from udocker.helper.hostinfo import HostInfo

def test_username():
    """Test001 HostInfo.username"""
    hinfo = HostInfo()
    assert hinfo.username() == 'david'
