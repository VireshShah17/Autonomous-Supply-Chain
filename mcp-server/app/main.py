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
except Exception as e:
    logger.warning(f"===== Warning: Could not connect to Odoo on startup. Ensure Odoo is running. Error: {e} =====")
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
                "description": "CRITICAL: You MUST use the exact argument names 'order_name' (string) and 'warehouse_id' (integer). Do not use 'order_id' or 'W001'. Example: order_name: 'S00012', warehouse_id: 1.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "order_name": {
                            "type": "string", 
                            "description": "The exact Order reference code string (e.g., 'S00012'). Do not use 'order_id'."
                        },
                        "warehouse_id": {
                            "type": "integer", 
                            "description": "The internal numerical ID of the target warehouse (e.g., 1). Do not use letters like 'W'."
                        }
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

    # ---- NEW DEBUG PRINT STATEMENT ----
    logger.info(f"\n[DEBUG] Tool Name: {name}")
    logger.info(f"[DEBUG] Raw Arguments Received: {args}")
    logger.info(f"[DEBUG] Type of args: {type(args)}")
    # -----------------------------------

    try:
        if name == "check_inventory":
            query = args.get("product_name_query")

            if not query:
                return {"content": [
                    {"type": "text", "text": "Error: Missing product_name_query argument. Ask the user for the product name."}
                ]}

            return {"content": [
                {"type": "text", "text": str(odoo.check_inventory(query))}
            ]}
            
        elif name == "get_delayed_orders":
            return {"content": [
                {"type": "text", "text": str(odoo.get_delayed_orders())}
            ]}
            
        elif name == "reroute_order_warehouse":
            order_name = args.get("order_name")
            warehouse_id = args.get("warehouse_id")
            
            # Catch LLM hallucinations here
            if not order_name or warehouse_id is None:
                return {"content": [
                    {"type": "text", "text": "Error: Missing order_name or warehouse_id. Please verify the order name and target warehouse ID and try again."}
                ]}

            return {"content": [
                {"type": "text", "text": str(odoo.reroute_order_warehouse(order_name, warehouse_id))}
            ]}
        
        raise HTTPException(status_code = 404, detail = f"Tool '{name}' not found.")
        
    except Exception as e:
        logger.error(f"===== Tool execution failed internally for {name}: {e} =====")

        # Prevent 500 errors from crashing the server by returning exceptions as text to the LLM
        return {"content": [
            {"type": "text", "text": f"Tool execution failed internally: {str(e)}"}
        ]}