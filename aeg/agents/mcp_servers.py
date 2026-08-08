class MCPServers:
    """
    Model Context Protocol definitions.
    Restricts LLMs to strict, typed tool executions instead of raw Bash.
    """
    
    @staticmethod
    def get_available_tools(role: str) -> list:
        """
        Returns only the tools the specific agent role is allowed to execute.
        """
        common_tools = [
            {
                "name": "query_lsp_references",
                "description": "Finds where a function is used across the codebase.",
                "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}}}
            }
        ]
        
        developer_tools = [
            {
                "name": "run_pytest_in_sandbox",
                "description": "Runs tests securely in the Docker sandbox.",
                "parameters": {"type": "object", "properties": {"test_path": {"type": "string"}}}
            }
        ]
        
        if role == "developer":
            return common_tools + developer_tools
            
        return common_tools
