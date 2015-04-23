#!/usr/bin/python
import datetime
import email.utils
import os
import glob
import pytz
import re
import subprocess
import sys
import tempfile


DRY_RUN = False
if os.environ.get('DRY_RUN', ''):
    DRY_RUN = True


def handle_one(tar_filename):
    # We're already in a tmpdir, yay. But there might be other
    # people's stuff here. So let's make a new tmpdir within the
    # current one, and 'cd' in.
    new_place = tempfile.mkdtemp(dir=os.getcwd())
    os.chdir(new_place)

    # Uncompress thing, then throw away output.
    subprocess.check_output(['tar', 'xvf', tar_filename])

    # Grab the commit ID.
    revision_filenames = glob.glob('*/git-revision')
    assert len(revision_filenames) == 1
    revision_filename = revision_filenames[0]

    revision = open(revision_filename).read().strip()

    # Make up a nice tag name.
    number = re.search(r'sandstorm-(\d+).tar.xz',
                       tar_filename).group(1)

    make_branch = ['git', 'tag', 'sandstorm-0.%s' % (number,), revision, '-m', 'Release sandstorm-0.%s' % (number,)]
    print ' '.join(make_branch)
    env = os.environ.copy()
    env['GIT_COMMITTER_DATE'] = filename2date(revision_filename)

    if not DRY_RUN:
        subprocess.check_output(make_branch,
                                cwd='/home/paulproteus/projects/sandstorm',
                                env=env,
        )


def main():
    tar_filenames = [os.path.abspath(f) for f in sys.argv[1:]]
    # sanity-check
    for f in tar_filenames:
        assert os.path.exists(f)

    # Print a tmpdir and let the person running the script remove it.
    tmpdir = tempfile.mkdtemp()
    print 'Created', tmpdir

    # Uncompress it, etc.
    for tar_filename in tar_filenames:
        os.chdir(tmpdir)
        tmpdir = handle_one(tar_filename)


def filename2date(f):
    mtime_float = os.stat(f).st_mtime
    # Localize to Pacific
    pacific = pytz.timezone('US/Pacific')
    fmt =  '%Y-%m-%d %H:%M:%S %Z%z'
    utc_dt = pytz.utc.localize(datetime.datetime.utcfromtimestamp(mtime_float))
    local_dt = utc_dt.astimezone(pacific)
    return local_dt.strftime(fmt)


if __name__ == '__main__':
    main()
