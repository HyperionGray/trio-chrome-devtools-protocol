from textwrap import dedent

import cdp

from .generate import generate_command


def test_dom_query_selector():

    expected = dedent("""\
        async def query_selector(
                node_id: NodeId,
                selector: str
            ) -> NodeId:
            r'''
            Executes ``querySelector`` on a given node.

            :param node_id: Id of the node to query upon.
            :param selector: Selector string.
            :returns: Query selector result.
            '''
            session = get_session_context('dom.query_selector')
            return await session.execute(cdp.dom.query_selector(node_id, selector))
    """)

    assert expected == generate_command(cdp.dom, 'dom', cdp.dom.query_selector)


def test_accessibility_disable():
    expected = dedent("""\
        async def disable() -> None:
            r'''
            Disables the accessibility domain.
            '''
            session = get_session_context('accessibility.disable')
            return await session.execute(cdp.accessibility.disable())
    """)

    assert expected == generate_command(cdp.accessibility, 'accessibility',
        cdp.accessibility.disable)


def test_accessibility_get_partial_ax_tree():
    expected = dedent("""\
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
    """)

    assert expected == generate_command(cdp.accessibility, 'accessibility',
        cdp.accessibility.get_partial_ax_tree)
