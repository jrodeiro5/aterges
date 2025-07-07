    async def _execute_function_call(self, function_call) -> Dict[str, Any]:
        """Execute a function call from the AI model"""
        try:
            # Add null check for function_call
            if not function_call:
                logger.error("Function call is None")
                return {"error": "Invalid function call - function_call is None"}
            
            # Check if function_call has name attribute
            if not hasattr(function_call, 'name'):
                logger.error(f"Function call missing 'name' attribute: {type(function_call)}")
                return {"error": "Invalid function call - missing 'name' attribute"}
            
            function_name = function_call.name
            function_args = {}
            
            # Parse function arguments with error handling
            if hasattr(function_call, 'args') and function_call.args:
                for key, value in function_call.args.items():
                    function_args[key] = value
            
            logger.info(f"Executing function: {function_name} with args: {function_args}")
            
            # Route function calls to appropriate agents
            if function_name == "get_ga4_report":
                if 'google_analytics' not in self.agents:
                    return {"error": "Google Analytics agent not available"}
                
                return await self.agents['google_analytics'].get_ga4_report(
                    start_date=function_args.get('start_date'),
                    end_date=function_args.get('end_date'),
                    dimensions=function_args.get('dimensions', ['date']),
                    metrics=function_args.get('metrics', ['sessions', 'pageviews'])
                )
            
            elif function_name == "get_top_pages":
                if 'google_analytics' not in self.agents:
                    return {"error": "Google Analytics agent not available"}
                
                return await self.agents['google_analytics'].get_top_pages(
                    start_date=function_args.get('start_date'),
                    end_date=function_args.get('end_date'),
                    limit=function_args.get('limit', 10)
                )
            
            elif function_name == "get_traffic_sources":
                if 'google_analytics' not in self.agents:
                    return {"error": "Google Analytics agent not available"}
                
                return await self.agents['google_analytics'].get_traffic_sources(
                    start_date=function_args.get('start_date'),
                    end_date=function_args.get('end_date')
                )
            
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except AttributeError as e:
            logger.error(f"AttributeError in function call execution: {e}")
            logger.error(f"Function call object type: {type(function_call)}")
            logger.error(f"Function call object attributes: {dir(function_call) if function_call else 'None'}")
            return {"error": f"Function call attribute error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error executing function call: {e}")
            return {"error": f"Function execution failed: {str(e)}"}
