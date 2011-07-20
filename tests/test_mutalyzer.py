"""
Tests for the Mutalyzer module.
"""


#import logging; logging.basicConfig()
import re
import os
import random
from nose.tools import *
from Bio.Seq import Seq

import mutalyzer
from mutalyzer.config import Config
from mutalyzer.output import Output
from mutalyzer.variantchecker import check_variant


class TestMutalyzer():
    """
    Test the Mutalyzer module.
    """

    def setUp(self):
        """
        Initialize test Mutalyzer module.
        """
        self.config = Config()
        self.output = Output(__file__, self.config.Output)

    def test_roll(self):
        """
        Just a variant where we should roll.
        """
        check_variant('NM_003002.2:c.273del', self.config, self.output)
        wroll = self.output.getMessagesWithErrorCode('WROLLFORWARD')
        assert len(wroll) > 0

    def test_no_roll(self):
        """
        Just a variant where we cannot roll.
        """
        check_variant('NM_003002.2:c.274del', self.config, self.output)
        wroll = self.output.getMessagesWithErrorCode('WROLLFORWARD')
        assert len(wroll) == 0

    def test_no_roll_splice(self):
        """
        Here we can roll but should not, because it is over a splice site.
        """
        check_variant('NM_000088.3:g.459del', self.config, self.output)
        wrollback = self.output.getMessagesWithErrorCode('IROLLBACK')
        assert len(wrollback) > 0
        wroll = self.output.getMessagesWithErrorCode('WROLLFORWARD')
        assert len(wroll) == 0

    def test_partial_roll_splice(self):
        """
        Here we can roll two positions, but should roll only one because
        otherwise it is over a splice site.
        """
        check_variant('NM_000088.3:g.494del', self.config, self.output)
        wrollback = self.output.getMessagesWithErrorCode('IROLLBACK')
        assert len(wrollback) > 0
        wroll = self.output.getMessagesWithErrorCode('WROLLFORWARD')
        assert len(wroll) > 0

    def test_roll_after_splice(self):
        """
        Here we can roll and should, we stay in the same exon.
        """
        check_variant('NM_000088.3:g.460del', self.config, self.output)
        wroll = self.output.getMessagesWithErrorCode('WROLLFORWARD')
        assert len(wroll) > 0

    def test_roll_both_ins(self):
        """
        Insertion that rolls should not use the same inserted sequence in
        descriptions on forward and reverse strands.

        Here we have the following situation on the forward strand:

                                65470 (genomic)
                                  |
          CGGTGCGTTGGGCAGCGCCCCCGCCTCCAGCAGCGCCCGCACCTCCTCTA

        Now, an insertion of TAC after 65470 should be rolled to an insertion
        of ACT after 65471:

          CGGTGCGTTGGGCAGCGCCCCCGCC --- TCCAGCAGCGCCCGCACCTCCTCTA
          CGGTGCGTTGGGCAGCGCCCCCGCC TAC TCCAGCAGCGCCCGCACCTCCTCTA  =>

          CGGTGCGTTGGGCAGCGCCCCCGCCT --- CCAGCAGCGCCCGCACCTCCTCTA
          CGGTGCGTTGGGCAGCGCCCCCGCCT ACT CCAGCAGCGCCCGCACCTCCTCTA

        However, in CDKN2A_v001 (on the reverse strand), this insertion should
        roll the other direction and the inserted sequence should be the reverse
        complement of CTA, which is TAG, and not that of ACT, which is AGT.

        The next test (test_roll_reverse_ins) tests the situation for an input
        of AL449423.14:g.65471_65472insACT, where only the reverse roll should
        be done.
        """
        check_variant('AL449423.14:g.65470_65471insTAC', self.config, self.output)
        assert 'AL449423.14(CDKN2A_v001):c.99_100insTAG' in self.output.getOutput('descriptions')
        assert_equal ('AL449423.14:g.65471_65472insACT', self.output.getIndexedOutput('genomicDescription', 0, ''))
        assert len(self.output.getMessagesWithErrorCode('WROLLFORWARD')) == 1

    def test_roll_reverse_ins(self):
        """
        Insertion that rolls on the reverse strand should not use the same
        inserted sequence in descriptions on forward and reverse strands.
        """
        check_variant('AL449423.14:g.65471_65472insACT', self.config, self.output)
        assert 'AL449423.14(CDKN2A_v001):c.99_100insTAG' in self.output.getOutput('descriptions')
        assert_equal ('AL449423.14:g.65471_65472insACT', self.output.getIndexedOutput('genomicDescription', 0, ''))
        assert len(self.output.getMessagesWithErrorCode('WROLLFORWARD')) == 0

    def test_roll_message_forward(self):
        """
        Roll warning message should only be shown for currently selected
        strand (forward).
        """
        check_variant('AL449423.14:g.65470_65471insTAC', self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WROLLFORWARD')) == 1
        assert len(self.output.getMessagesWithErrorCode('WROLLREVERSE')) == 0

    def test_roll_message_reverse(self):
        """
        Roll warning message should only be shown for currently selected
        strand (reverse).
        """
        check_variant('AL449423.14(CDKN2A_v001):c.98_99insGTA', self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WROLLFORWARD')) == 0
        assert len(self.output.getMessagesWithErrorCode('WROLLREVERSE')) == 1

    def test_ins_cds_start(self):
        """
        Insertion on CDS start boundary should not be included in CDS.
        """
        check_variant('NM_000143.3:c.-1_1insCAT', self.config, self.output)
        assert_equal(self.output.getIndexedOutput("newprotein", 0), None)
        # Todo: Is this a good test?

    def test_ins_cds_start_after(self):
        """
        Insertion after CDS start boundary should be included in CDS.
        """
        check_variant('NM_000143.3:c.1_2insCAT', self.config, self.output)
        assert_equal(self.output.getIndexedOutput("newprotein", 0), '?')
        # Todo: Is this a good test?

    def test_del_splice_site(self):
        """
        Deletion hitting one splice site should not do a protein prediction.
        """
        check_variant('NG_012772.1(BRCA2_v001):c.632-5_670del',
                      self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WOVERSPLICE')) > 0
        assert len(self.output.getMessagesWithErrorCode('IDELSPLICE')) == 0
        # Todo: For now, the following is how to check if no protein
        # prediction is done.
        assert not self.output.getOutput('newprotein')

    def test_del_exon(self):
        """
        Deletion of an entire exon should be possible.
        """
        check_variant('NG_012772.1(BRCA2_v001):c.632-5_681+7del',
                      self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WOVERSPLICE')) > 0
        assert len(self.output.getMessagesWithErrorCode('IDELSPLICE')) > 0
        # Todo: For now, the following is how to check if protein
        # prediction is done.
        assert self.output.getOutput('newprotein')

    def test_del_exon_in_frame(self):
        """
        Deletion of an entire exon with length a triplicate should give a
        proteine product with just this deletion (and possibly substitutions
        directly before and after).

        NG_012772.1(BRCA2_v001):c.68-7_316+7del is such a variant, since
        positions 68 through 316 are exactly one exon and (316-68+1)/3 = 83.
        """
        check_variant('NG_012772.1(BRCA2_v001):c.68-7_316+7del',
                      self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WOVERSPLICE')) > 0
        assert len(self.output.getMessagesWithErrorCode('IDELSPLICE')) > 0
        # Todo: For now, the following is how to check if protein
        # prediction is done.
        assert self.output.getOutput('newprotein')
        # Todo: assert that protein products indeed have only this difference.

    def test_del_exons(self):
        """
        Deletion of two entire exons should be possible.
        """
        check_variant('NG_012772.1(BRCA2_v001):c.632-5_793+7del',
                      self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WOVERSPLICE')) > 0
        assert len(self.output.getMessagesWithErrorCode('IDELSPLICE')) > 0
        # Todo: For now, the following is how to check if protein
        # prediction is done.
        assert self.output.getOutput('newprotein')

    def test_del_intron(self):
        """
        Deletion of an entire intron should be possible (fusion of remaining
        exonic parts).
        """
        check_variant('NG_012772.1(BRCA2_v001):c.622_674del',
                      self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WOVERSPLICE')) > 0
        assert len(self.output.getMessagesWithErrorCode('IDELSPLICE')) > 0
        # Todo: For now, the following is how to check if protein
        # prediction is done.
        assert self.output.getOutput('newprotein')

    def test_del_intron_in_frame(self):
        """
        Deletion of an entire intron should be possible (fusion of remaining
        exonic parts).
        """
        check_variant('NG_012772.1(BRCA2_v001):c.622_672del',
                      self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WOVERSPLICE')) > 0
        assert len(self.output.getMessagesWithErrorCode('IDELSPLICE')) > 0
        # Todo: For now, the following is how to check if protein
        # prediction is done.
        assert self.output.getOutput('newprotein')
        # Todo: assert that protein products indeed have only this difference.

    def test_del_exon_unknown_offsets(self):
        """
        Deletion of an entire exon with unknown offsets should be possible.
        """
        return # Todo
        check_variant('NG_012772.1(BRCA2_v001):c.632-?_681+?del',
                      self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WOVERSPLICE')) > 0
        assert len(self.output.getMessagesWithErrorCode('IDELSPLICE')) > 0
        # Todo: For now, the following is how to check if protein
        # prediction is done.
        assert self.output.getOutput('newprotein')
        # Genomic positions should be centered in flanking introns and unsure.
        assert_equal(self.output.getIndexedOutput('genomicDescription', 0),
                     'NG_012772.1:g.(17550_19725)del')
        assert 'NG_012772.1(BRCA2_v001):c.632-?_681+?del' \
               in self.output.getOutput('descriptions')
        # Todo: .c notation should still be c.632-?_681+?del, but what about
        # other transcripts?

    def test_del_exon_unknown_offsets_in_frame(self):
        """
        Deletion of an entire exon with unknown offsets and length a
        triplicate should give a proteine product with just this deletion
        (and possibly substitutions directly before and after).

        NG_012772.1(BRCA2_v001):c.68-?_316+?del is such a variant, since
        positions 68 through 316 are exactly one exon and (316-68+1)/3 = 83.
        """
        return # Todo
        check_variant('NG_012772.1(BRCA2_v001):c.68-?_316+?del',
                      self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WOVERSPLICE')) > 0
        assert len(self.output.getMessagesWithErrorCode('IDELSPLICE')) > 0
        # Todo: For now, the following is how to check if protein
        # prediction is done.
        assert self.output.getOutput('newprotein')
        # Genomic positions should be centered in flanking introns and unsure.
        assert_equal(self.output.getIndexedOutput('genomicDescription', 0),
                     'NG_012772.1:g.(7324_11720)del')
        assert 'NG_012772.1(BRCA2_v001):c.68-?_316+?del' \
               in self.output.getOutput('descriptions')
        # Todo: .c notation should still be c.632-?_681+?del, but what about
        # other transcripts?

    def test_del_exon_unknown_offsets_composed(self):
        """
        Deletion of an entire exon with unknown offsets and another composed
        variant with exact positioning should be possible.
        """
        return # Todo
        check_variant('UD_129433404385(DMD_v010):c.[281-?_492+?del;492+4del]',
                      self.config, self.output)
        assert len(self.output.getMessagesWithErrorCode('WOVERSPLICE')) > 0
        assert len(self.output.getMessagesWithErrorCode('IDELSPLICE')) > 0
        # Todo: For now, the following is how to check if protein
        # prediction is done.
        assert self.output.getOutput('newprotein')
        # Genomic positions should be centered in flanking introns and unsure.
        assert_equal(self.output.getIndexedOutput('genomicDescription', 0),
                     'UD_129433404385:g.[(1640003_1675849)del;1665239del]')
        assert 'UD_129433404385(DMD_v010):c.[281-?_492+?del;492+4del]' \
               in self.output.getOutput('descriptions')
        # Todo: .c notation should still be c.632-?_681+?del, but what about
        # other transcripts?