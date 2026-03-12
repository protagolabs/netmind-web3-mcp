"""Agent operation reporting tool."""


async def report_agent_operation(operation: str) -> str:
    """Report the operation being performed by the agent.

    Args:
        operation: Description of the operation being performed,
                   e.g. 'swap', 'query pool', 'query market data'.

    Returns:
        str: The operation string as received.
    """
    return operation
