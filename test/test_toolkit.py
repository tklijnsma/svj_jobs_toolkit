import os, os.path as osp, shutil

from cmssw_interface import CMSSW
import svj_jobs_toolkit as svj


def cleanup(*files):
    for file in files:
        if osp.isfile(file):
            os.remove(file)
        elif osp.isdir(file):
            shutil.rmtree(file)


def test_download_tarball():
    cmssw = CMSSW('CMSSW_10_6_29_patch1')
    physics = svj.Physics({
        'year' : 2018, 'mz' : 250, 'mdark' : 10, 'rinv' : .3,
        'boost': 0., 'max_events' : 5, 'part' : 1
        })
    dst = svj.download_madgraph_tarball(cmssw, physics)
    assert osp.isfile(dst)
    cleanup(dst)


def test_chain():
    cmssw = CMSSW('CMSSW_10_6_29_patch1')
    physics = svj.Physics({
        'year' : 2018, 'mz' : 250, 'mdark' : 10, 'rinv' : .3,
        'boost': 0., 'max_events' : 5, 'part' : 1,
        })
    mgtarball = svj.download_madgraph_tarball(cmssw, physics)
    rootfile = svj.run_step(cmssw, 'step_LHE-GEN', physics, inpre='step0_GRIDPACK')
    assert osp.isfile(rootfile)
    rootfile = svj.run_step(cmssw, 'step_SIM', physics, in_rootfile=rootfile)
    assert osp.isfile(rootfile)
    cleanup(rootfile, mgtarball)
