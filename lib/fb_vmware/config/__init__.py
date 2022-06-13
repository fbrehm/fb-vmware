#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 by Frank Brehm, Berlin
@summary: A module for providing a configuration for VSPhere
"""
from __future__ import absolute_import

# Standard module
import logging
import copy

# Third party modules

from fb_tools.common import is_sequence, to_bool, pp
from fb_tools.multi_config import MultiConfigError, BaseMultiConfig
from fb_tools.multi_config import DEFAULT_ENCODING
from fb_tools.obj import FbGenericBaseObject, FbBaseObject

# Own modules

from ..errors import WrongPortTypeError, WrongPortValueError

from ..xlate import XLATOR

__version__ = '0.5.6'
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext

DEFAULT_CONFIG_DIR = 'pixelpark'

DEFAULT_VSPHERE_PORT = 443
DEFAULT_VSPHERE_USER = 'Administrator@vsphere.local'
DEFAULT_VSPHERE_DC = 'vmcc'
DEFAULT_VSPHERE_CLUSTER = 'vmcc-l105-01'

DEFAULT_PORT_HTTP = 80
DEFAULT_PORT_HTTPS = 443

MAX_PORT_NUMBER = (2 ** 16) - 1


# =============================================================================
class VmwareConfigError(MultiConfigError):
    """Base error class for all exceptions happened during
    execution this configured application"""

    pass


# =============================================================================
class VSPhereConfigInfo(FbBaseObject):
    """Encapsulating all necessary data to connect to a VSPhere server."""

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=__version__, base_dir=None,
            host=None, use_https=True, port=DEFAULT_VSPHERE_PORT, dc=DEFAULT_VSPHERE_DC,
            user=DEFAULT_VSPHERE_USER, password=None, initialized=False):

        self._host = None
        self._port = DEFAULT_VSPHERE_PORT
        self._use_https = True
        self._dc = DEFAULT_VSPHERE_DC
        self._user = DEFAULT_VSPHERE_USER
        self._password = None

        super(VSPhereConfigInfo, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir,
            initialized=False)

        self.host = host
        self.port = port
        self.use_https = use_https
        self.dc = dc
        self.user = user
        self.password = password

        if initialized:
            self.initialized = True

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(VSPhereConfigInfo, self).as_dict(short=short)

        res['host'] = self.host
        res['use_https'] = self.use_https
        res['port'] = self.port
        res['dc'] = self.dc
        res['user'] = self.user
        res['password'] = self.show_password
        res['schema'] = self.schema
        res['url'] = self.url
        res['full_url'] = self.full_url

        return res

    # -----------------------------------------------------------
    @property
    def host(self):
        """The host name (or IP address) of the VSPhere server."""
        return self._host

    @host.setter
    def host(self, value):
        if value is None or str(value).strip() == '':
            self._host = None
            return
        self._host = str(value).strip().lower()

    # -----------------------------------------------------------
    @property
    def use_https(self):
        """Should there be used HTTPS for communicating with the VSPhere server?"""
        return self._use_https

    @use_https.setter
    def use_https(self, value):
        self._use_https = to_bool(value)

    # -----------------------------------------------------------
    @property
    def port(self):
        "The TCP port number of the VSPhere server."
        return self._port

    @port.setter
    def port(self, value):
        try:
            val = int(value)
            if val <= 0 or val > MAX_PORT_NUMBER:
                raise WrongPortValueError(val, MAX_PORT_NUMBER)
        except TypeError as e:
            raise WrongPortTypeError(val, str(e))

        self._port = val

    # -----------------------------------------------------------
    @property
    def dc(self):
        """The name of the datacenter in VSPhere to use."""
        return self._dc

    @dc.setter
    def dc(self, value):
        if value is None or str(value).strip() == '':
            msg = _("An empty name for a VSPhere datacenter is not allowed.")
            LOG.warn(msg)
            return
        self._dc = str(value).strip()

    # -----------------------------------------------------------
    @property
    def user(self):
        """The user name to use to connect to the VSPhere server."""
        return self._user

    @user.setter
    def user(self, value):
        if value is None or str(value).strip() == '':
            msg = _("An empty user name for connecting to a VSPhere datacenter is not allowed.")
            LOG.warn(msg)
            return
        self._user = str(value).strip()

    # -----------------------------------------------------------
    @property
    def password(self):
        """The password of the DN used to connect to the LDAP server."""
        return self._password

    @password.setter
    def password(self, value):
        if value is None or str(value).strip() == '':
            self._password = None
            return
        self._password = str(value).strip()

    # -----------------------------------------------------------
    @property
    def show_password(self):
        """The password for using it in logging messages and in as_dict()."""
        if self.password is None:
            return None
        if self.verbose > 4:
            return self.password
        else:
            return '******'

    # -----------------------------------------------------------
    @property
    def schema(self):
        """The schema as part of the URL to connect to the VSPhere server."""
        if self.use_https:
            return 'https'
        return 'http'

    # -----------------------------------------------------------
    @property
    def url(self):
        """The URL, which can be used to connect to the VSPhere server."""
        if not self.host:
            return None

        port = ''
        if self.use_https:
            if self.port != DEFAULT_PORT_HTTPS:
                port = ':{}'.format(self.port)
        else:
            if self.port != DEFAULT_PORT_HTTP:
                port = ':{}'.format(self.port)

        return '{s}://{h}{p}'.format(s=self.schema, h=self.host, p=port)

    # -----------------------------------------------------------
    @property
    def full_url(self):
        """The full URL, which can be used to connect to the VSPhere server."""
        if not self.host:
            return None

        port = ''
        if self.use_https:
            if self.port != DEFAULT_PORT_HTTPS:
                port = ':{}'.format(self.port)
        else:
            if self.port != DEFAULT_PORT_HTTP:
                port = ':{}'.format(self.port)

        if self.show_password:
            pw = '/' + self.show_password
        else:
            pw = ''

        return '{s}://{u}{pw}@{h}{p}'.format(
            s=self.schema, u=self.user, pw=pw, h=self.host, p=port)

    # -------------------------------------------------------------------------
    @classmethod
    def from_config(
            cls, section_name, vsphere_name, section, appname=None, verbose=0, base_dir=None):

        info = cls(appname=appname, verbose=verbose, base_dir=base_dir, initialized=False)

        try:

            for key in section.keys():

                value = section[key]

                if key.lower() == 'host':
                    info.host = value
                    continue
                if key.lower() == 'port':
                    info.port = value
                    continue
                if key.lower() == 'https':
                    info.use_https = value
                    continue
                if key.lower() == 'dc':
                    info.dc = value
                    continue
                if key.lower() == 'user':
                    info.user = value
                    continue
                if key.lower() == 'password':
                    info.password = value
                    continue

                msg = _(
                    "Unknown key {k!r} with value {v!r} for VSphere {vs!r} in section "
                    "{sec!r} found.").format(k=key, v=value, vs=vsphere_name, sec=section_name)
                LOG.warn(msg)

        except Exception as e:
            msg = _("{e} in section {sn!r} for VSphere {vs!r}:").format(
                e=e.__class__.__name__, sn=section_name, vs=vsphere_name)
            msg += ' ' + str(e)
            raise VmwareConfigError(msg)

        if not info.host:
            msg = _(
                "There must be given at least the VSPhere hostname in section {sn!r} "
                "for VSphere {vs!r}.").format(vs=vsphere_name, sec=section_name)
            raise VmwareConfigError(msg)

        info.initialized = True

        return info

    # -------------------------------------------------------------------------
    def __repr__(self):
        """Typecasting into a string for reproduction."""

        out = "<%s(" % (self.__class__.__name__)

        fields = []
        fields.append("appname={!r}".format(self.appname))
        fields.append("host={!r}".format(self.host))
        fields.append("use_https={!r}".format(self.use_https))
        fields.append("port={!r}".format(self.port))
        fields.append("dc={!r}".format(self.dc))
        fields.append("user={!r}".format(self.user))
        fields.append("password={!r}".format(self.password))
        fields.append("verbose={!r}".format(self.verbose))
        fields.append("base_dir={!r}".format(self.base_dir))
        fields.append("initialized={!r}".format(self.initialized))

        out += ", ".join(fields) + ")>"
        return out

    # -------------------------------------------------------------------------
    def _repr(self):
        """A typecasting into a string for reproduction only with relevant information."""

        out = "<%s(" % (self.__class__.__name__)

        fields = []
        fields.append("host={!r}".format(self.host))
        fields.append("use_https={!r}".format(self.use_https))
        fields.append("port={!r}".format(self.port))
        fields.append("dc={!r}".format(self.dc))
        fields.append("user={!r}".format(self.user))
        fields.append("password={!r}".format(self.show_password))

        out += ", ".join(fields) + ")>"
        return out

    # -------------------------------------------------------------------------
    def __copy__(self):

        new = self.__class__(
            appname=self.appname, verbose=self.verbose, base_dir=self.base_dir, host=self.host,
            use_https=self.use_https, port=self.port, dc=self.dc, user=self.user,
            password=self.password, initialized=self.initialized)

        return new


# =============================================================================
class VSPhereConfigInfoDict(dict, FbGenericBaseObject):
    """A dictionary containing VSPhereConfigInfo as values and their VSPhere names as keys."""

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(VSPhereConfigInfoDict, self).as_dict(short=short)

        for key in self.keys():
            res[key] = self[key].as_dict(short=short)

        return res

    # -------------------------------------------------------------------------
    def __copy__(self):

        new = self.__class__()

        for key in self.keys():
            new[key] = copy.copy(self[key])

        return new


# =============================================================================
class VmwareConfiguration(BaseMultiConfig):
    """
    A class for providing a configuration for an arbitrary Vmware Application
    and methods to read it from configuration files.
    """

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=__version__, base_dir=None,
            append_appname_to_stems=True, additional_stems=None, config_dir=DEFAULT_CONFIG_DIR,
            additional_config_file=None, additional_cfgdirs=None, encoding=DEFAULT_ENCODING,
            use_chardet=True, initialized=False):

        add_stems = []
        if additional_stems:
            if is_sequence(additional_stems):
                for stem in additional_stems:
                    add_stems.append(stem)
            else:
                add_stems.append(additional_stems)

        if 'vmware' not in add_stems:
            add_stems.append('vmware')
        if 'vsphere' not in add_stems:
            add_stems.append('vsphere')

        self.vsphere = VSPhereConfigInfoDict()

        super(VmwareConfiguration, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir,
            append_appname_to_stems=append_appname_to_stems, config_dir=config_dir,
            additional_stems=add_stems, additional_config_file=additional_config_file,
            additional_cfgdirs=additional_cfgdirs, encoding=encoding, use_chardet=use_chardet,
            ensure_privacy=True, initialized=False,
        )

        if initialized:
            self.initialized = True

    # -------------------------------------------------------------------------
    def eval_section(self, section_name):

        super(VmwareConfiguration, self).eval_section(section_name)
        sn = section_name.lower()

        if sn == 'vsphere' or sn.startswith('vsphere:'):

            section = self.cfg[section_name]

            if self.verbose > 2:
                LOG.debug(
                    _("Evaluating config section {!r}:").format(section_name) + '\n' + pp(section))

            if sn == 'vsphere':
                return self._eval_bare_vsphere(section_name, section)

            if sn.startswith('vsphere:'):
                vsphere_name = sn.replace('vsphere:', '').strip()
                return self._eval_vsphere_instance(section_name, vsphere_name, section)

            LOG.error(_("Empty VSphere name found."))

    # -------------------------------------------------------------------------
    def _eval_bare_vsphere(self, section_name, section):

        for vsphere_name in section.keys():
            sub_section = section[vsphere_name]
            vs_name = vsphere_name.strip()
            self._eval_vsphere_instance(section_name, vs_name, sub_section)

    # -------------------------------------------------------------------------
    def _eval_vsphere_instance(self, section_name, vsphere_name, section):

        try:
            vsphere_info = VSPhereConfigInfo.from_config(
                section_name=section_name, vsphere_name=vsphere_name, section=section,
                verbose=self.verbose, base_dir=self.base_dir)
            self.vsphere[vsphere_name] = vsphere_info
        except VmwareConfigError as e:
            LOG.error(str(e))


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
