import xmlrpc.client
from app.custom_logging import setup_logger


logger = setup_logger()


class OdooClient:
    def __init__(self, url="http://localhost:8069", db="supply_chain_db", username="admin", password="admin"):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self._authenticate()


    def _authenticate(self):
        """
            Authenticates with Odoo and retrieves the User ID (UID).
        """
        try:
            common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            self.uid = common.authenticate(self.db, self.username, self.password, {})

            if not self.uid:
                raise Exception("====== Authentication failed: Invalid Credentials =====")

            logger.info(f"===== Successfully authenticated with Odoo. UID: {self.uid} =====")
        except Exception as e:
            logger.error(f"===== Error connecting to Odoo: {e} ===== ")
    

    def execute_kw(self, model, method, *args, **kwargs):
        """
            Executes a command against Odoo models.
        """
        try:
            models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

            return models.execute_kw(self.db, self.uid, self.password, model, method, *args, **kwargs)
        except Exception as e:
            logger.error(f"===== Error executing Odoo method {method} on model {model}: {e} =====")

            return {"error": str(e)}
    

    def check_inventory(self, product_name_query):
        """
            Searches for a product and returns its available stock across warehouses.
        """
        # 1. Find product IDs matching the query
        product_ids = self.execute_kw(
            'product.product', 'search',
            [[['name', 'ilike', product_name_query]]]
        )

        # Guard clause: check if it's an error dict from execute_kw
        if isinstance(product_ids, dict) and "error" in product_ids:
            return product_ids

        if not product_ids:
            return {"message": f"No products found matching '{product_name_query}'."}

        # 2. Read inventory levels (stock.quant) for those products
        stock_data = self.execute_kw(
            'product.product', 'read',
            [product_ids],
            {'fields': ['name', 'qty_available', 'virtual_available', 'display_name']}
        )

        return stock_data
    

    def get_delayed_orders(self):
        """
            Fetches sales orders that are confirmed but not yet fully delivered.
        """
        # Find orders where delivery status is not 'fully delivered' (done) and state is 'sale'
        order_ids = self.execute_kw(
            'sale.order', 'search',
            [[['state', '=', 'sale'], ['delivery_status', '!=', 'full']]]
        )

        # Guard clause: check if it's an error dict from execute_kw
        if isinstance(order_ids, dict) and "error" in order_ids:
            return order_ids

        if not order_ids:
            return {"message": "No delayed or unfulfilled orders found."}

        orders = self.execute_kw(
            'sale.order', 'read',
            [order_ids],
            {'fields': ['name', 'partner_id', 'amount_total', 'delivery_status', 'commitment_date']}
        )

        return orders
    

    def reroute_order_warehouse(self, order_name, warehouse_id):
        """
            Updates an order's fulfillment source warehouse dynamically.
        """
        # 1. Locate the order ID by its display name (e.g., 'S00001')
        order_ids = self.execute_kw(
            'sale.order', 'search',
            [[['name', '=', order_name]]]
        )

        # Guard clause: check if it's an error dict from execute_kw
        if isinstance(order_ids, dict) and "error" in order_ids:
            return order_ids

        if not order_ids:
            return {"error": f"Order {order_name} not found."}

        # Safe cast to integer to prevent NoneType or string errors from LLM hallucinations
        try:
            safe_warehouse_id = int(warehouse_id)
        except (ValueError, TypeError):
            return {"error": f"Invalid warehouse_id provided: {warehouse_id}. Must be an integer."}

        # 2. Write the new warehouse ID to the order
        result = self.execute_kw(
            'sale.order', 'write',
            [order_ids, {'warehouse_id': safe_warehouse_id}]
        )

        if result and not isinstance(result, dict):
            return {"status": "success", "message": f"Order {order_name} successfully rerouted to Warehouse ID {safe_warehouse_id}."}
        
        return {"status": "failed", "error": str(result)}