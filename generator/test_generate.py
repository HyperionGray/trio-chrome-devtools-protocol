from textwrap import dedent

import cdp

from .generate import generate_command


def test_generate_command():

    expected = dedent("""\
        async def query_selector(
                node_id: NodeId,
                selector: str
            ) -> NodeId:
            '''
            Executes `querySelector` on a given node.

            :param node_id: Id of the node to query upon.
            :param selector: Selector string.
            :returns: Query selector result.
            '''
            session = get_session_context('dom.query_selector')
            return await session.execute(cdp.dom.query_selector(node_id, selector))
    """)

    assert expected == generate_command('dom', 'query_selector', cdp.dom.query_selector)
