# DO NOT EDIT THIS FILE!
#
# This code is generated off of PyCDP modules. If you need to make
# changes, edit the generator and regenerate all of the modules.

from __future__ import annotations
import typing

from ..context import get_connection_context, get_session_context

import cdp.storage
from cdp.storage import (
    CacheStorageContentUpdated,
    CacheStorageListUpdated,
    IndexedDBContentUpdated,
    IndexedDBListUpdated,
    StorageType,
    TrustTokens,
    UsageForType
)


async def clear_cookies(
        browser_context_id: typing.Optional[cdp.browser.BrowserContextID] = None
    ) -> None:
    '''
    Clears cookies.

    :param browser_context_id: *(Optional)* Browser context to use when called on the browser endpoint.
    '''
    session = get_session_context('storage.clear_cookies')
    return await session.execute(cdp.storage.clear_cookies(browser_context_id))


async def clear_data_for_origin(
        origin: str,
        storage_types: str
    ) -> None:
    '''
    Clears storage for origin.

    :param origin: Security origin.
    :param storage_types: Comma separated list of StorageType to clear.
    '''
    session = get_session_context('storage.clear_data_for_origin')
    return await session.execute(cdp.storage.clear_data_for_origin(origin, storage_types))


async def clear_trust_tokens(
        issuer_origin: str
    ) -> bool:
    '''
    Removes all Trust Tokens issued by the provided issuerOrigin.
    Leaves other stored data, including the issuer's Redemption Records, intact.

    **EXPERIMENTAL**

    :param issuer_origin:
    :returns: True if any tokens were deleted, false otherwise.
    '''
    session = get_session_context('storage.clear_trust_tokens')
    return await session.execute(cdp.storage.clear_trust_tokens(issuer_origin))


async def get_cookies(
        browser_context_id: typing.Optional[cdp.browser.BrowserContextID] = None
    ) -> typing.List[cdp.network.Cookie]:
    '''
    Returns all browser cookies.

    :param browser_context_id: *(Optional)* Browser context to use when called on the browser endpoint.
    :returns: Array of cookie objects.
    '''
    session = get_session_context('storage.get_cookies')
    return await session.execute(cdp.storage.get_cookies(browser_context_id))


async def get_trust_tokens() -> typing.List[TrustTokens]:
    '''
    Returns the number of stored Trust Tokens per issuer for the
    current browsing context.

    **EXPERIMENTAL**

    :returns: 
    '''
    session = get_session_context('storage.get_trust_tokens')
    return await session.execute(cdp.storage.get_trust_tokens())


async def get_usage_and_quota(
        origin: str
    ) -> typing.Tuple[float, float, bool, typing.List[UsageForType]]:
    '''
    Returns usage and quota in bytes.

    :param origin: Security origin.
    :returns: A tuple with the following items:

        0. **usage** - Storage usage (bytes).
        1. **quota** - Storage quota (bytes).
        2. **overrideActive** - Whether or not the origin has an active storage quota override
        3. **usageBreakdown** - Storage usage per type (bytes).
    '''
    session = get_session_context('storage.get_usage_and_quota')
    return await session.execute(cdp.storage.get_usage_and_quota(origin))


async def override_quota_for_origin(
        origin: str,
        quota_size: typing.Optional[float] = None
    ) -> None:
    '''
    Override quota for the specified origin

    **EXPERIMENTAL**

    :param origin: Security origin.
    :param quota_size: *(Optional)* The quota size (in bytes) to override the original quota with. If this is called multiple times, the overridden quota will be equal to the quotaSize provided in the final call. If this is called without specifying a quotaSize, the quota will be reset to the default value for the specified origin. If this is called multiple times with different origins, the override will be maintained for each origin until it is disabled (called without a quotaSize).
    '''
    session = get_session_context('storage.override_quota_for_origin')
    return await session.execute(cdp.storage.override_quota_for_origin(origin, quota_size))


async def set_cookies(
        cookies: typing.List[cdp.network.CookieParam],
        browser_context_id: typing.Optional[cdp.browser.BrowserContextID] = None
    ) -> None:
    '''
    Sets given cookies.

    :param cookies: Cookies to be set.
    :param browser_context_id: *(Optional)* Browser context to use when called on the browser endpoint.
    '''
    session = get_session_context('storage.set_cookies')
    return await session.execute(cdp.storage.set_cookies(cookies, browser_context_id))


async def track_cache_storage_for_origin(
        origin: str
    ) -> None:
    '''
    Registers origin to be notified when an update occurs to its cache storage list.

    :param origin: Security origin.
    '''
    session = get_session_context('storage.track_cache_storage_for_origin')
    return await session.execute(cdp.storage.track_cache_storage_for_origin(origin))


async def track_indexed_db_for_origin(
        origin: str
    ) -> None:
    '''
    Registers origin to be notified when an update occurs to its IndexedDB.

    :param origin: Security origin.
    '''
    session = get_session_context('storage.track_indexed_db_for_origin')
    return await session.execute(cdp.storage.track_indexed_db_for_origin(origin))


async def untrack_cache_storage_for_origin(
        origin: str
    ) -> None:
    '''
    Unregisters origin from receiving notifications for cache storage.

    :param origin: Security origin.
    '''
    session = get_session_context('storage.untrack_cache_storage_for_origin')
    return await session.execute(cdp.storage.untrack_cache_storage_for_origin(origin))


async def untrack_indexed_db_for_origin(
        origin: str
    ) -> None:
    '''
    Unregisters origin from receiving notifications for IndexedDB.

    :param origin: Security origin.
    '''
    session = get_session_context('storage.untrack_indexed_db_for_origin')
    return await session.execute(cdp.storage.untrack_indexed_db_for_origin(origin))
