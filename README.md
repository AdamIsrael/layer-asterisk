# Overview

This is a work-in-progress charm to deploy and operate Asterisk as a
virtualized network service (VNF), currently focusing on SIP functionality.

This has been successfully tested on LXD and Amazon EC2.

Once the `asterisk` charm has been deployed, configured, and a user added, you
can test it out by using a SIP phone, configured with the new users credentials,
and call extension 100. If successful, you should here a brief message.

# Usage

```
juju deploy cs:~aisrael/asterisk
juju expose asterisk
```

If you are deploying to Amazon EC2 or other cloud that uses NAT, you'll need
to enable this functionality:

```
juju set asterisk sip-nat='yes'
```

By default, no users have been added. To do that, run the `add-user` action,
specifying the username and password.
```
juju run-action asterisk/0 add-user username=demo password=demo
```

## Scale out Usage

None yet.

## Known Limitations and Issues

The charm is pretty limited at the moment.

- The `pjsip` module is disabled, due to a bug in the Ubuntu 16.04 asterisk package. The package will need to be fixed in order for that module to be enabled.
- Does not auto-detect NAT
- Configuration options are limited.
- dialpans are not configurable yet.

# Configuration

- sip-nat: 'yes', 'no', 'force_rport', or 'comedia'. Please note that only 'yes' has been tested.
- sip-port: The SIP port to listen on.

# Contact Information

Please submit [issues](https://github.com/AdamIsrael/layer-asterisk/issues) or
[pull requests](https://github.com/AdamIsrael/layer-asterisk/pulls) against this
charm on its [github repository](https://github.com/AdamIsrael/layer-asterisk).

## Upstream Project Name

[Asterisk](http://www.asterisk.org/) - a free and open source framework for building communications applications, sponsored by Digium.
