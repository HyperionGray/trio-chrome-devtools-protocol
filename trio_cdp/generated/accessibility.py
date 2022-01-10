# DO NOT EDIT THIS FILE!
#
# This code is generated off of PyCDP modules. If you need to make
# changes, edit the generator and regenerate all of the modules.

from __future__ import annotations
import typing

from ..context import get_connection_context, get_session_context

import cdp.accessibility
from cdp.accessibility import (
    AXNode,
    AXNodeId,
    AXProperty,
    AXPropertyName,
    AXRelatedNode,
    AXValue,
    AXValueNativeSourceType,
    AXValueSource,
    AXValueSourceType,
    AXValueType,
    LoadComplete,
    NodesUpdated
)


async def disable() -> None:
    r'''
    Disables the accessibility domain.
    '''
    session = get_session_context('accessibility.disable')
    return await session.execute(cdp.accessibility.disable())


async def enable() -> None:
    r'''
    Enables the accessibility domain which causes ``AXNodeId``'s to remain consistent between method calls.
    This turns on accessibility for the page, which can impact performance until accessibility is disabled.
    '''
    session = get_session_context('accessibility.enable')
    return await session.execute(cdp.accessibility.enable())


async def get_ax_node_and_ancestors(
        node_id: typing.Optional[cdp.dom.NodeId] = None,
        backend_node_id: typing.Optional[cdp.dom.BackendNodeId] = None,
        object_id: typing.Optional[cdp.runtime.RemoteObjectId] = None
    ) -> typing.List[AXNode]:
    r'''
    Fetches a node and all ancestors up to and including the root.
    Requires ``enable()`` to have been called previously.

    **EXPERIMENTAL**

    :param node_id: *(Optional)* Identifier of the node to get.
    :param backend_node_id: *(Optional)* Identifier of the backend node to get.
    :param object_id: *(Optional)* JavaScript object id of the node wrapper to get.
    :returns: 
    '''
    session = get_session_context('accessibility.get_ax_node_and_ancestors')
    return await session.execute(cdp.accessibility.get_ax_node_and_ancestors(node_id, backend_node_id, object_id))


async def get_child_ax_nodes(
        id_: AXNodeId,
        frame_id: typing.Optional[cdp.page.FrameId] = None
    ) -> typing.List[AXNode]:
    r'''
    Fetches a particular accessibility node by AXNodeId.
    Requires ``enable()`` to have been called previously.

    **EXPERIMENTAL**

    :param id_:
    :param frame_id: *(Optional)* The frame in whose document the node resides. If omitted, the root frame is used.
    :returns: 
    '''
    session = get_session_context('accessibility.get_child_ax_nodes')
    return await session.execute(cdp.accessibility.get_child_ax_nodes(id_, frame_id))


async def get_full_ax_tree(
        depth: typing.Optional[int] = None,
        max_depth: typing.Optional[int] = None,
        frame_id: typing.Optional[cdp.page.FrameId] = None
    ) -> typing.List[AXNode]:
    r'''
    Fetches the entire accessibility tree for the root Document

    **EXPERIMENTAL**

    :param depth: *(Optional)* The maximum depth at which descendants of the root node should be retrieved. If omitted, the full tree is returned.
    :param max_depth: **(DEPRECATED)** *(Optional)* Deprecated. This parameter has been renamed to ```depth```. If depth is not provided, max_depth will be used.
    :param frame_id: *(Optional)* The frame for whose document the AX tree should be retrieved. If omited, the root frame is used.
    :returns: 
    '''
    session = get_session_context('accessibility.get_full_ax_tree')
    return await session.execute(cdp.accessibility.get_full_ax_tree(depth, max_depth, frame_id))


async def get_partial_ax_tree(
        node_id: typing.Optional[cdp.dom.NodeId] = None,
        backend_node_id: typing.Optional[cdp.dom.BackendNodeId] = None,
        object_id: typing.Optional[cdp.runtime.RemoteObjectId] = None,
        fetch_relatives: typing.Optional[bool] = None
    ) -> typing.List[AXNode]:
    r'''
    Fetches the accessibility node and partial accessibility tree for this DOM node, if it exists.

    **EXPERIMENTAL**

    :param node_id: *(Optional)* Identifier of the node to get the partial accessibility tree for.
    :param backend_node_id: *(Optional)* Identifier of the backend node to get the partial accessibility tree for.
    :param object_id: *(Optional)* JavaScript object id of the node wrapper to get the partial accessibility tree for.
    :param fetch_relatives: *(Optional)* Whether to fetch this nodes ancestors, siblings and children. Defaults to true.
    :returns: The ``Accessibility.AXNode`` for this DOM node, if it exists, plus its ancestors, siblings and children, if requested.
    '''
    session = get_session_context('accessibility.get_partial_ax_tree')
    return await session.execute(cdp.accessibility.get_partial_ax_tree(node_id, backend_node_id, object_id, fetch_relatives))


async def get_root_ax_node(
        frame_id: typing.Optional[cdp.page.FrameId] = None
    ) -> AXNode:
    r'''
    Fetches the root node.
    Requires ``enable()`` to have been called previously.

    **EXPERIMENTAL**

    :param frame_id: *(Optional)* The frame in whose document the node resides. If omitted, the root frame is used.
    :returns: 
    '''
    session = get_session_context('accessibility.get_root_ax_node')
    return await session.execute(cdp.accessibility.get_root_ax_node(frame_id))


async def query_ax_tree(
        node_id: typing.Optional[cdp.dom.NodeId] = None,
        backend_node_id: typing.Optional[cdp.dom.BackendNodeId] = None,
        object_id: typing.Optional[cdp.runtime.RemoteObjectId] = None,
        accessible_name: typing.Optional[str] = None,
        role: typing.Optional[str] = None
    ) -> typing.List[AXNode]:
    r'''
    Query a DOM node's accessibility subtree for accessible name and role.
    This command computes the name and role for all nodes in the subtree, including those that are
    ignored for accessibility, and returns those that mactch the specified name and role. If no DOM
    node is specified, or the DOM node does not exist, the command returns an error. If neither
    ``accessibleName`` or ``role`` is specified, it returns all the accessibility nodes in the subtree.

    **EXPERIMENTAL**

    :param node_id: *(Optional)* Identifier of the node for the root to query.
    :param backend_node_id: *(Optional)* Identifier of the backend node for the root to query.
    :param object_id: *(Optional)* JavaScript object id of the node wrapper for the root to query.
    :param accessible_name: *(Optional)* Find nodes with this computed name.
    :param role: *(Optional)* Find nodes with this computed role.
    :returns: A list of ``Accessibility.AXNode`` matching the specified attributes, including nodes that are ignored for accessibility.
    '''
    session = get_session_context('accessibility.query_ax_tree')
    return await session.execute(cdp.accessibility.query_ax_tree(node_id, backend_node_id, object_id, accessible_name, role))
