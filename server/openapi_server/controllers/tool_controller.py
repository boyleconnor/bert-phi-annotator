from openapi_server.models.tool import Tool  # noqa: E501
from openapi_server.models.tool_dependencies import ToolDependencies  # noqa: E501
from openapi_server.models.tool_type import ToolType  # noqa: E501
from openapi_server.models.license import License
from openapi_server.config import config


def get_tool():  # noqa: E501
    """Get tool information

    Get information about the tool # noqa: E501


    :rtype: Tool
    """
    tool = Tool(
        name=f"phi-annotator-huggingface-{config.config_name}",
        version="1.2.0",
        license=License.APACHE_2_0,
        repository="github:nlpsandbox/phi-annotator-huggingface",
        description=f"Hugging Face-based PHI annotator ({config.model_name})",
        author="NLP Sandbox Team",
        author_email="team@nlpsandbox.io",
        url="https://github.com/nlpsandbox/phi-annotator-huggingface",
        type=ToolType.PHI_ANNOTATOR,
        api_version="1.2.0"
    )
    return tool, 200


def get_tool_dependencies():  # noqa: E501
    """Get tool dependencies

    Get the dependencies of this tool # noqa: E501


    :rtype: ToolDependencies
    """
    return ToolDependencies(tools=[]), 200
