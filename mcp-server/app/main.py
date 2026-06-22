# Import the required libraries
from app.custom_logging import setup_logger
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.odoo_client import OdooClient


logger = setup_logger()

# Intialize our FastAPI app
app = FastAPI(title = "Autonomous Supply Chain MCP Server", version = "1.0")

# Initialize our Odoo connector
try:
    odoo = OdooClient()
except Exception:
    logger.warning("===== Warning: Could not connect to Odoo on startup. Ensure Odoo is running =====")
    odoo = None


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict


@app.get('/tools')
def list_tools():
    """
        MCP standard protocol mapping to list available tools to the AI client.
    """

    return {
        "tools": [
            {
                "name": "check_inventory",
                "description": "Checks warehouse stock levels and quantities for a specific product name query.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "product_name_query": {
                            "type": "string",
                            "description": "The name or part of the name of the product (e.g., 'Desk', 'Chair')."
                        }
                    },
                    "required": ["product_name_query"]
                }
            },
            {
                "name": "get_delayed_orders",
                "description": "Retrieves open sales orders that face delivery fulfillment bottlenecks.",
                "input_schema": {"type": "object", "properties": {}}
            },
            {
                "name": "reroute_order_warehouse",
                "description": "Changes the origin fulfillment warehouse for a specific sales order ID to clear delays.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "order_name": {"type": "string", "description": "The Order reference code (e.g., 'S00012')."},
                        "warehouse_id": {"type": "integer", "description": "The internal ID of the target warehouse."}
                    },
                    "required": ["order_name", "warehouse_id"]
                }
            }
        ]
    }


@app.post("/tools/execute")
def execute_tool(request: ToolCallRequest):
    """
        Executes a discovered tool dynamically based on AI client request.
    """

    if not odoo:
        raise HTTPException(status_code = 503, detail = "Odoo backend service is unavailable.")
    
    name = request.tool_name
    args = request.arguments

    if name == "check_inventory":
        return {"content": [
            {"type": "text", "text": str(odoo.check_inventory(args.get("product_name_query")))}
        ]}
        
    elif name == "get_delayed_orders":
        return {"content": [
            {"type": "text", "text": str(odoo.get_delayed_orders())}
        ]}
        
    elif name == "reroute_order_warehouse":
        return {"content": [
            {"type": "text", "text": str(odoo.reroute_order_warehouse(args.get("order_name"), args.get("warehouse_id")))}
        ]}
    
    raise HTTPException(status_code = 404, detail = f"Tool '{name}' not found.")
