import os, os.path as osp, shutil

from cmssw_interface import CMSSW

def pytest_sessionstart(session):
    if not osp.isdir('CMSSW_10_6_29_patch1'):
        CMSSW.from_tarball(
            'root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/svjproductiontarballs'
            '/CMSSW_10_6_29_patch1_svjprod_el7_2018UL_b6852b4_May04_withHLTs.tar.gz',
            '.'
            )

def pytest_sessionfinish(session, exitstatus):
    if osp.isfile('CMSSW_10_6_29_patch1_svjprod_el7_2018UL_b6852b4_May04_withHLTs.tar.gz'):
        os.remove('CMSSW_10_6_29_patch1_svjprod_el7_2018UL_b6852b4_May04_withHLTs.tar.gz')
    if osp.isdir('CMSSW_10_6_29_patch1'):
        shutil.rmtree('CMSSW_10_6_29_patch1')
    if osp.isdir('HLT'):
        shutil.rmtree('HLT')
