import os, os.path as osp, sys, pprint, logging, shutil

import seutils


PY3 = sys.version_info.major == 3
PY2 = sys.version_info.major == 2


INCLUDE_DIR = osp.join(osp.abspath(osp.dirname(__file__)), "include")
def version():
    with open(osp.join(INCLUDE_DIR, "VERSION"), "r") as f:
        return(f.read().strip())


def setup_logger(name='svj'):
    if name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.info('Logger %s is already defined', name)
    else:
        fmt = logging.Formatter(
            fmt = (
                '\033[92m[%(name)s:%(levelname)s:%(asctime)s:%(module)s:%(lineno)s]\033[0m'
                + ' %(message)s'
                ),
            datefmt='%Y-%m-%d %H:%M:%S'
            )
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    return logger
logger = setup_logger()


class Physics(dict):
    """Holds the desired physics"""

    def __init__(self, *args, **kwargs):
        # Set some default values
        self["mz"] = 150.0
        self["rinv"] = 0.3
        self["boost"] = 0.0
        self["mdark"] = 20.0
        self["alpha"] = "peak"
        self["max_events"] = None
        super(Physics, self).__init__(*args, **kwargs)

    def boost_str(self):
        """Format string if boost > 0"""
        if self["boost"] == 0.0: return ''
        boostvar = self.get('boostvar', 'genjetpt')
        boostvarstr = {'genjetpt' : 'PT', 'madpt' : 'MADPT'}[boostvar]
        return "_{0}{1:.0f}".format(boostvarstr, self["boost"])

    def max_events_str(self):
        return (
            "" if self.get("max_events", None) is None
            else "_n-{0}".format(self["max_events"])
            )

    def __repr__(self):
        return pprint.pformat(dict(self))

    def filename(self, step, ext='.root'):
        """
        Returns the basename of the output rootfile the way SVJProductions would
        format it for the given physics parameters.
        """
        outfile = (
            "{step}_s-channel_mMed-{mz:.0f}_mDark-{mdark:.0f}_rinv-{rinv}_"
            "alpha-{alpha}{boost_str}_13TeV-madgraphMLM-pythia8{max_events_str}".format(
                step=step,
                boost_str=self.boost_str(),
                max_events_str=self.max_events_str(),
                **self
                )
            )
        if self.get("part", None):
            outfile += "_part-{}".format(self["part"])
        outfile += ext
        return outfile

    def gridpack_filename(self):
        """
        Later SVJProductions repo dropped rinv and alpha_dark as part of
        the filename
        """
        return (
            "step0_GRIDPACK_s-channel_mMed-{mz:.0f}_mDark-{mdark:.0f}"
            "{boost_str}_13TeV-madgraphMLM-pythia8_n-{maxEventsIn}"
            ".tar.xz"
            .format(
                boost_str=self.boost_str(),
                maxEventsIn=self.get('maxEventsIn', 10000),
                **self
                )
            )


def run_step(cmssw, step, physics=None, in_rootfile=None, move=True, inpre=None, delete_inrootfile=True):
    """
    Runs 1 step of the SVJProductions chain.
    """
    if physics is None: physics = Physics()
    if inpre is None: inpre = 'INPRE'
    in_rootfile_svj = osp.join(cmssw.src, 'SVJ/Production/test', physics.filename(inpre))
    if in_rootfile:
        if not osp.isfile(in_rootfile_svj):
            logger.info('Copying input %s -> %s', in_rootfile, in_rootfile_svj)
            if seutils.path.has_protocol(in_rootfile):
                seutils.cp(in_rootfile, in_rootfile_svj)
            elif move:
                shutil.move(in_rootfile, in_rootfile_svj)
            else:
                shutil.copyfile(in_rootfile, in_rootfile_svj)
        else:
            logger.info(
                'Would now copy %s -> %s, but %s already exist'
                ' (this is probably a debug session)',
                in_rootfile, in_rootfile_svj, in_rootfile_svj
                )
    if inpre != 'step0_GRIDPACK' and not osp.isfile(in_rootfile_svj):
        raise Exception(
            'File {} does not exist.'
            ' Did you mean to supply the argument in_rootfile?'
            .format(in_rootfile_svj)
            )
    cmd = (
        "cmsRun runSVJ.py"
        " year={year}"
        " madgraph=1"
        " channel=s"
        " outpre={outpre}"
        " config={outpre}"
        " part={part}"
        " mMediator={mz:.0f}"
        " mDark={mdark:.0f}"
        " rinv={rinv}"
        " inpre={inpre}".format(inpre=inpre, outpre=step, **physics)
        )
    if 'maxEventsIn' in physics or inpre=='step0_GRIDPACK':
        cmd += ' maxEventsIn={:.0f}'.format(physics.get('maxEventsIn', 10000))
    if "mingenjetpt" in physics:
        cmd += " mingenjetpt={0:.1f}".format(physics["mingenjetpt"])
    if "boost" in physics:
        cmd += " boost={0:.0f}".format(physics["boost"])
    if "boostvar" in physics:
        cmd += " boostvar={0}".format(physics["boostvar"])
    if "max_events" in physics:
        cmd += " maxEvents={0}".format(physics["max_events"])
    cmssw.run(['cd SVJ/Production/test', cmd])
    outfile = osp.join(cmssw.src, 'SVJ/Production/test', physics.filename(step))
    if osp.isfile(outfile) and delete_inrootfile and step != 'step0_GRIDPACK':
        logger.warning('Step succeeded; deleting input rootfile %s', in_rootfile_svj)
    logger.info('Outfile of step: %s', outfile)
    return outfile


def run_treemaker(cmssw, rootfile, year=2018, outfile_tag='out'):
        scenario = {
            2018 : 'Summer20UL18sig',
            # '2017' : 'Fall17sig',      # Should probably be different for UL
            # '2016' : 'Summer16v3sig',  # Should probably be different for UL
            }
        if not seutils.path.has_protocol(rootfile) and not rootfile.startswith('file:'):
            rootfile = 'file:' + rootfile
        cmssw.run([
            'cd TreeMaker/Production/test',
            '_CONDOR_CHIRP_CONFIG="" cmsRun runMakeTreeFromMiniAOD_cfg.py'
            ' numevents=-1'
            ' outfile={}'
            ' scenario={}'
            ' lostlepton=0'
            ' doZinv=0'
            ' systematics=0'
            ' deepAK8=0'
            ' deepDoubleB=0'
            ' doPDFs=0'
            ' nestedVectors=False'
            ' debugjets=0'
            ' splitLevel=99'
            ' boostedsemivisible=1'
            ' dataset={}'
            .format(outfile_tag, scenario[2018], rootfile)
            ])
        expected_outfile = osp.join(cmssw.src, 'TreeMaker/Production/test/out_RA2AnalysisTree.root')
        if not osp.isfile(expected_outfile):
            logger.error(
                'Treemaker finished but expected outfile %s does not exist!',
                expected_outfile
                )
        return expected_outfile


def download_madgraph_tarball(
    cmssw, physics,
    search_path='root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/mgtarballs/2023MADPT',
    ):
    """
    Downloads tarball from the storage element to correct path inside CMSSW.
    """
    # Even though the tarball content does not depend on boost or n_events,
    # it must still have these things in its filename. It must not have `part`
    # though.
    dst = osp.join(cmssw.src, 'SVJ/Production/test', physics.gridpack_filename())
    if osp.isfile(dst):
        logger.info("File %s already exists", dst)
        return dst
    src = osp.join(search_path, physics.gridpack_filename())
    if not seutils.isfile(src):
        raise Exception('File {} does not exist.'.format(src))
    logger.info("Downloading %s --> %s", src, dst)
    seutils.cp(src, dst)
    return dst
