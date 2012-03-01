"""
Tests for the mutalyzer.describe module.
"""


#import logging; logging.basicConfig()
import os
from nose.tools import *

import mutalyzer
from mutalyzer import describe


class TestDescribe():
    """
    Test the mytalyzer.describe module.
    """

    def setUp(self):
        """
        Nothing.
        """
        pass

    def test1(self):
        """
        Test 1.
        """
        result = describe.describeDNA(
            'ATGATGATCAGATACAGTGTGATACAGGTAGTTAGACAA',
            'ATGATTTGATCAGATACATGTGATACCGGTAGTTAGGACAA')
        description = describe.alleleDescription(result)
        assert_equal(description, '[5_6insTT;17del;26A>C;35dup]')

    def test2(self):
        """
        Test 2.
        """
        result = describe.describeDNA(
            'TAAGCACCAGGAGTCCATGAAGAAGATGGCTCCTGCCATGGAATCCCCTACTCTACTGTG',
            'TAAGCACCAGGAGTCCATGAAGAAGCTGGATCCTCCCATGGAATCCCCTACTCTACTGTG')
        description = describe.alleleDescription(result)
        assert_equal(description, '[26A>C;30C>A;35G>C]')

    def test3(self):
        """
        Test 3.
        """
        result = describe.describeDNA(
            'TAAGCACCAGGAGTCCATGAAGAAGATGGCTCCTGCCATGGAATCCCCTACTCTA',
            'TAAGCACCAGGAGTCCATGAAGAAGCCATGTCCTGCCATGGAATCCCCTACTCTA')
        description = describe.alleleDescription(result)
        assert_equal(description, '[26_29inv;30C>G]')

    def test4(self):
        """
        Test 4.
        """
        result = describe.describeDNA(
            'TAAGCACCAGGAGTCCATGAAGAAGATGGCTCCTGCCATGGAATCCCCTACTCTA',
            'TAAGCACCAGGAGTCCATGAAGAAGCCATGTCCTGCCATGAATCCCCTACTCTA')
        description = describe.alleleDescription(result)
        assert_equal(description, '[26_29inv;30C>G;41del]')