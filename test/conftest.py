import os, os.path as osp, shutil

from cmssw_interface import CMSSW

SVJPRODUCTIONS_TARBALL = 'root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/svjproductiontarballs/CMSSW_10_6_29_patch1_svjprod_el7_2018UL_cms-svj_Run2_UL_withHLT_996c8dc_Jan18.tar.gz'

def pytest_sessionstart(session):
    if not osp.isdir('CMSSW_10_6_29_patch1'):
        CMSSW.from_tarball(SVJPRODUCTIONS_TARBALL, '.')

def pytest_sessionfinish(session, exitstatus):
    if osp.isfile(osp.basename(SVJPRODUCTIONS_TARBALL)):
        os.remove(osp.basename(SVJPRODUCTIONS_TARBALL))
    if osp.isdir('CMSSW_10_6_29_patch1'):
        shutil.rmtree('CMSSW_10_6_29_patch1')
    if osp.isdir('HLT'):
        shutil.rmtree('HLT')
