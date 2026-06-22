# Import the required libraries
import requests
from pydantic import create_model
from custom_logging import setup_logger
from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


MCP_SERVER_URL = "http://mcp-server:8000"
logger = setup_logger()

def fetch_mcp_tools():
    """
        Dynamically fetches tools from the MCP Server and registers them for LangChain.
    """
    try:
        response = requests.get(f"{MCP_SERVER_URL}/tools")
        response.raise_for_status()
        mcp_data = response.json()
    except Exception as e:
        logger.error(f"===== Failed to connect to MCP Server: {e} =====")
        return []

    langchain_tools = []
    
    # Dynamically warp MCP server endpoints into LangChain executable tools
    for t_info in mcp_data.get("tools", []):
        tool_name = t_info["name"]
        tool_desc = t_info["description"]
        
        # --- THE FIX: DYNAMIC PYDANTIC SCHEMA MAPPING ---
        # Map the MCP JSON Schema into a Pydantic Model so LangChain retains the arguments
        input_schema = t_info.get("input_schema", {}).get("properties", {})
        fields = {}
        for key, val in input_schema.items():
            # Map JSON schema types to Python types
            py_type = int if val.get("type") == "integer" else str
            fields[key] = (py_type, ...)  # '...' tells Pydantic this field is required
            
        DynamicArgsSchema = create_model(f"{tool_name}Schema", **fields)
        
        # We construct a functional wrapper closure for each tool discovered
        def make_tool_func(name):
            def tool_func(**kwargs):
                res = requests.post(
                    f"{MCP_SERVER_URL}/tools/execute",
                    json={"tool_name": name, "arguments": kwargs}
                )

                return res.json().get("content", [{}])[0].get("text", "No response content.")
            
            return tool_func

        # Instantiate standard LangChain tools dynamically with the schema
        dynamic_tool = StructuredTool.from_function(
            func = make_tool_func(tool_name),
            name = tool_name,
            description = tool_desc,
            args_schema = DynamicArgsSchema
        )
        langchain_tools.append(dynamic_tool)
        
    return langchain_tools


def initialize_supply_chain_agent(groq_api_key):
    """
        Initializes the LLM agent executor bound to the dynamic MCP tools.
    """
    # 1. Fetch current live tools from the MCP Server
    tools = fetch_mcp_tools()
    
    # 2. Initialize the lightweight remote LLM (Llama3 via Groq API)
    llm = ChatGroq(temperature = 0, api_key = groq_api_key, model = "llama-3.3-70b-versatile")
    
    # 3. Define an analytical persona capable of multi-step warehouse routing
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an Autonomous Supply Chain AI Commander. 
        Your job is to analyze delivery delays and resolve inventory routing bottlenecks.
        You have direct access to the enterprise ERP data and warehouse execution functions through your tools.
        Always look at inventory levels before suggesting a fulfillment reroute.
        Be concise, accurate, and metric-driven."""),
        MessagesPlaceholder(variable_name = "chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name = "agent_scratchpad"),
    ])
    
    # 4. Construct the runtime execution loop
    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(agent = agent, tools = tools, verbose = True, handle_parsing_errors = True)