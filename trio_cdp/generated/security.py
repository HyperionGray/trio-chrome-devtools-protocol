# DO NOT EDIT THIS FILE!
#
# This code is generated off of PyCDP modules. If you need to make
# changes, edit the generator and regenerate all of the modules.

from __future__ import annotations
import typing

from ..context import get_connection_context, get_session_context

import cdp.security
from cdp.security import (
    CertificateError,
    CertificateErrorAction,
    CertificateId,
    CertificateSecurityState,
    InsecureContentStatus,
    MixedContentType,
    SafetyTipInfo,
    SafetyTipStatus,
    SecurityState,
    SecurityStateChanged,
    SecurityStateExplanation,
    VisibleSecurityState,
    VisibleSecurityStateChanged
)


async def disable() -> None:
    '''
    Disables tracking security state changes.
    '''
    session = get_session_context('security.disable')
    return await session.execute(cdp.security.disable())


async def enable() -> None:
    '''
    Enables tracking security state changes.
    '''
    session = get_session_context('security.enable')
    return await session.execute(cdp.security.enable())


async def handle_certificate_error(
        event_id: int,
        action: CertificateErrorAction
    ) -> None:
    '''
Handles a certificate error that fired a certificateError event.

.. deprecated:: 1.3

:param event_id: The ID of the event.
:param action: The action to take on the certificate error.

.. deprecated:: 1.3
'''
    session = get_session_context('security.handle_certificate_error')
    return await session.execute(cdp.security.handle_certificate_error(event_id, action))


async def set_ignore_certificate_errors(
        ignore: bool
    ) -> None:
    '''
    Enable/disable whether all certificate errors should be ignored.

    **EXPERIMENTAL**

    :param ignore: If true, all certificate errors will be ignored.
    '''
    session = get_session_context('security.set_ignore_certificate_errors')
    return await session.execute(cdp.security.set_ignore_certificate_errors(ignore))


async def set_override_certificate_errors(
        override: bool
    ) -> None:
    '''
Enable/disable overriding certificate errors. If enabled, all certificate error events need to
be handled by the DevTools client and should be answered with ``handleCertificateError`` commands.

.. deprecated:: 1.3

:param override: If true, certificate errors will be overridden.

.. deprecated:: 1.3
'''
    session = get_session_context('security.set_override_certificate_errors')
    return await session.execute(cdp.security.set_override_certificate_errors(override))
