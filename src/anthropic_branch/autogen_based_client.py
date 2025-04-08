import asyncio
from pathlib import Path
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from dotenv import load_dotenv
import sys
load_dotenv()


async def main() -> None:
    # Setup server params for local filesystem access
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
    try:

        desktop = str(Path.home())
        server_params = StdioServerParams(
        command="python", args=[sys.argv[1]],env=None
        )

        print(f"SERVER PARAMS !!! {server_params}")
        print("CLIENT CREATED")
        # Get all available tools from the server

        try:
            tools = await mcp_server_tools(server_params)
            print(f"TOOLS EXTRACTED ------------------------- {tools}")
        except Exception as e:
            print(f"Failed to get tools: {str(e)}")

        # Create an agent that can use all the tools
        agent = AssistantAgent(
            name="Financial_Analyst",
            model_client=OpenAIChatCompletionClient(model="claude-3-5-sonnet-20241022"),
            tools=tools,  # type: ignore
        )
        print("Financial Analyst Agent in play !!!!!!!!!!!")
        # The agent can now use any of the filesystem tools
        await agent.run(task="Provide sentiment analysis for Infosys.", cancellation_token=CancellationToken())

    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    asyncio.run(main())
