from charmhelpers.core.hookenv import (
    action_get,
    action_set,
    action_fail,
    config,
    log,
    open_port,
    open_ports,
    status_set,
)
from charmhelpers.core import (
    templating,
)
from charms.reactive import (
    remove_state,
    set_state,
    when,
    when_not,
)
import configparser
import os
from subprocess import (
    Popen,
    CalledProcessError,
    PIPE,
)


@when('actions.add-user')
def add_user():
    """
    Add a user to asterisk

    It would be cool to have this auto-generate a password for a user if none
    is set. Not everyone wants to keep a bash history of passwords. ^_^
    """

    try:
        user = action_get('username')
        pwd = action_get('password')

        ini = configparser.ConfigParser()
        ini.read('/etc/asterisk/sip.conf')

        if user in ini.sections():
            """This user already exists."""
            raise Exception('User {} already exists.'.format(user))

        ini[user] = {}
        ini[user]['type'] = 'friend'
        ini[user]['context'] = 'from-internal'
        ini[user]['host'] = 'dynamic'
        ini[user]['secret'] = pwd
        ini[user]['disallow'] = 'all'
        ini[user]['allow'] = 'ulaw'

        with open('/etc/asterisk/sip.conf', 'w') as configfile:
            ini.write(configfile)

    except Exception as e:
        action_fail(repr(e))
    else:
        reload_config()
        action_set({'output': 'OK'})
    finally:
        remove_state('actions.add-user')


@when('config-changed')
def config_changed():
    """Update asterisk configuration"""
    try:
        # cfg = config()

        open_port('5060', 'UDP')
        open_port('4969', 'UDP')
        open_ports('10000', '20000', 'UDP')

    except Exception as e:
        log(repr(e))
    finally:
        remove_state('config-changed')


@when_not('asterisk.installed')
def install_asterisk():
    """
    For demo purposes, let's manually change some settings that we'll make
    configurable down the road.
    """

    # Workaround a bug in the packaged version of asterisk in 16.04 by
    # disabling the (preferred) pjsip module. I should try to fix that.
    templating.render(
        'etc/asterisk/modules.conf',
        '/etc/asterisk/modules.conf',
        {},
    )

    os.rename('/etc/asterisk/sip.conf', '/etc/asterisk/sip.conf.dpkg')
    ini = configparser.ConfigParser()
    ini['general'] = {}
    ini['general']['context'] = 'default'

    with open('/etc/asterisk/sip.conf', 'w') as configfile:
        ini.write(configfile)

    # Create a very simple dialplan. Drive by Actions later.
    # If you modify the dialplan, you can use the Asterisk CLI command
    # "dialplan reload" to load the new dialplan without disrupting service in
    # your PBX.
    os.rename(
        '/etc/asterisk/extensions.conf',
        '/etc/asterisk/extensions.conf.dpkg'
    )

    # The tricky part with this is it's not really an ini file, because it has
    # multiple "keys", which ConfigParser, et al, can't handle. We can do
    # better here with a proper Asterisk config parser.
    with open('/etc/asterisk/extensions.conf', 'w') as f:
        f.write('[from-internal]\n')
        f.write('exten = 100,1,Answer()\n')
        f.write('same = n,Wait(1)\n')
        f.write('same = n,Playback(hello-world)\n')
        f.write('same = n, Hangup()\n')

    reload_config()

    open_port('5060', 'UDP')
    open_port('', 'UDP')
    open_ports('10000', '20000', 'UDP')

    set_state('asterisk.installed')
    status_set('active', 'Ready!')


#####################
# utility functions #
#####################

# class AsteriskConfig:
#     def __init__(self, filename):
#         pass
#
#     def parse(self, filename):
#         pass
#
#     pass


def reload_config():
    """Tell asterisk to reload its configuration"""
    # run("rasterisk -x reload")
    run("service asterisk restart")
    pass


def run(cmd, env=None):
    """ Run a command, either on the local machine or remotely via SSH. """
    if isinstance(cmd, str):
        cmd = cmd.split(' ') if ' ' in cmd else [cmd]

    p = Popen(cmd,
              env=env,
              shell=True,
              stdout=PIPE,
              stderr=PIPE)
    stdout, stderr = p.communicate()
    retcode = p.poll()
    if retcode > 0:
        raise CalledProcessError(returncode=retcode,
                                 cmd=cmd,
                                 output=stderr.decode("utf-8").strip())
    return (stdout.decode('utf-8').strip(), stderr.decode('utf-8').strip())
