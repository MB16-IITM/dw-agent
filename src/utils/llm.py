import os
import requests
import json
from typing import List, Dict
from .cache import save_response, load_response


import logging  
logger = logging.getLogger(__name__)  

AI_PROXY_BASE = "https://aiproxy.sanand.workers.dev/openai/v1"
AIPROXY_TOKEN = os.environ.get('AIPROXY_TOKEN')

class TaskHandler:
    def __init__(self):
        self.token = os.getenv("AIPROXY_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_function_schemas(self) -> List[Dict]:
        return [
            {
            "name": "a1_install_run",
            "description": "Install UV and execute datagen.py script. If email provided replace the user_email parameter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_email": {
                        "type": "string",
                        "format": "email",
                        "default": "24f1001631@ds.study.iitm.ac.in"
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        },
        {
            "name": "a2_format_markdown",
            "description": "Format markdown file using Prettier 3.4.2. If no file path mentioned return default file_path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "format": "path",
                        "pattern": "^/data/.*\\.md$",
                        "default": "/data/format.md"
                    }
                },
                "required": ["file_path"],
                "additionalProperties": False
            }
        },
        {
            "name": "a3_count_weekdays",
            "description": "Count occurrences of specified weekday in date file",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Path to input file containing dates"
                    },
                    "weekday": {
                        "type": "string",
                        "description": "Full English weekday name (e.g. wednesday) in lowercase",
                        "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                    },
                    "output_file": {
                        "type": "string", 
                        "description": "Path to output file for count"
                    }
                },
                "required": ["weekday", "input_file", "output_file"],
                "additionalProperties": False
            }
        },
        {
            "name": "a4_sort_contacts",
            "description": "Sort JSON contacts by last_name then first_name",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "default": "/app/data/contacts.json"
                    },
                    "output_file": {
                        "type": "string", 
                        "default": "/app/data/contacts-sorted.json"
                    },
                    "sort_keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["last_name", "first_name"]
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        },
        {
            "name": "a5_process_logs",
            "description": "Process most recent log files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_dir": {
                        "type": "string",
                        "default": "/data/logs",
                        "ensure-exists": True
                    },
                    "output_file": {
                        "type": "string",
                        "default": "/data/logs-recent.txt",
                        "pattern": "^/data/.*\\.txt$"
                    },
                    "file_pattern": {
                        "type": "string",
                        "default": "*.log"
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        },
        {
            "name": "a6_generate_md_index",
            "description": "Generate markdown file index with H1 headings",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_dir": {
                        "type": "string",
                        "default": "/data/docs",
                        "pattern": "^/data/docs"
                    },
                    "output_file": {
                        "type": "string", 
                        "default": "/data/docs/index.json"
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        },
        {
            "name": "a7_extract_email",
            "description": "Extract sender email from email message content",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "default": "/data/email.txt",
                        "pattern": "^/data/.*\\.txt$"
                    },
                    "output_file": {
                        "type": "string", 
                        "default": "/data/email-sender.txt",
                        "pattern": "^/data/.*\\.txt$"
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        },
        {
            "name": "a8_extract_cc_number",
            "description": "Extract credit card number from image and save as text file",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "default": "/data/credit-card.png",
                        "pattern": "^/data/.*\\.png$"
                    },
                    "output_file": {
                        "type": "string",
                        "default": "/data/credit-card.txt", 
                        "pattern": "^/data/.*\\.txt$"
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        },
        {
            "name": "a9_find_similar_comments",
            "description": "Find most similar comment pairs using embeddings",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "default": "/data/comments.txt",
                        "pattern": "^/data/.*\\.txt$"
                    },
                    "output_file": {
                        "type": "string",
                        "default": "/data/comments-similar.txt",
                        "pattern": "^/data/.*\\.txt$"
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        },
        {
            "name": "a10_calculate_sales",
            "description": "Calculate total sales for ticket type",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string", 
                        "default": "/data/ticket-sales.db",
                        "pattern": "^/data/.*\\.db$"
                    },
                    "ticket_type": {
                        "type": "string",
                        "enum": ["Gold", "Silver", "Platinum"]
                    },
                    "output_file": {
                        "type": "string",
                        "default": "/data/ticket-sales-gold.txt",
                        "pattern": "^/data/.*\\.txt$"
                    }
                },
                "required": ["ticket_type"]
            }
        }
        ]

    def parse_task(self, task_description: str) -> Dict:
        # Get preliminary params
        # preliminary_params = self._get_params_from_task(task_description)

         # Check cache first
        # if cached := load_response(task_description, preliminary_params):
            # return {"tool_calls": [{"function": cached}]}
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": task_description}],
            "functions": self.get_function_schemas(),  # ✅ Use 'functions' not 'tools'
            "function_call": "auto"  # ✅ Required for legacy format
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AIPROXY_TOKEN}"
        }

        response = requests.post(
            f"{AI_PROXY_BASE}/chat/completions",
            headers=headers,
            json=payload
        )

        try:
            result = response.json()
            print("LLM Raw Response:", json.dumps(result, indent=2))  # Debug logging

            #validate current structure
            if "choices" not in result or not result["choices"]:
                raise ValueError("Invalid LLM response format")
            
            choice = result["choices"][0]["message"]

        
            if "function_call" not in choice:
                raise ValueError("Missing function_call in response")
                
            func_call = result["choices"][0]["message"]["function_call"]
            return {
                "tool_calls": [{
                    "function": {
                        "name": func_call["name"],
                        "arguments": func_call["arguments"]
                    }
                }]
            }
        except KeyError as e:
            logger.error(f"Missing key: {str(e)}")
            
    def query_vision(self, prompt: str, images: List[str], max_tokens: int):
        """Handle vision requests with proper image formatting"""
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }]

        # Add properly formatted image objects
        for img_base64 in images:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}",  # Proper object structure
                    "detail": "high"
                }
            })

        payload = {
            "model": "gpt-4o-mini",  # Must use vision-specific model
            "messages": messages,
            "max_tokens": max_tokens
        }

        response = requests.post(
            f"{AI_PROXY_BASE}/chat/completions",
            headers=self.headers,
            json=payload
        )
        
        # Handle potential errors
        if response.status_code != 200:
            raise ValueError(f"Vision API error: {response.text}")
        
        result = response.json()
        print("LLM after Reading Image Response:", json.dumps(result, indent=2))
        return result['choices'][0]['message']['content']  # Direct text response

        












        # try:
        #     result = response.json()
            
        #     # Validate response structure
        #     if "choices" not in result or not result["choices"]:
        #         raise ValueError("Invalid LLM response format")
                
        #     choice = result["choices"][0]
        #     if "tool_calls" not in choice["message"]:
        #         raise ValueError("LLM response missing tool_calls")
                
        #     tool_call = choice["message"]["tool_calls"][0]
        #     raw_args = result["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]
        #     logger.debug(f"Raw arguments: {raw_args}")

        #     final_params = json.loads(raw_args)
        #     logger.debug(f"Parsed params: {final_params}")

            
        #     # Save to cache
        #     save_response(task_description, final_params, result)
            
        #     logger.debug(f"Final tool call structure: {json.dumps({
        #         'name': tool_call['function']['name'],
        #         'args': raw_args
        #     }, indent=2)}")
        #     print({json.dumps({
        #         'name': tool_call['function']['name'],
        #         'args': raw_args
        #         }, indent=2)})

        #     return {
        #         "tool_calls": [{
        #             "function": {
        #                 "name": tool_call["function"]["name"],  # Use already parsed tool_call
        #                 "arguments": raw_args  # Directly use original JSON string
        #             }
        #         }]
        #     }
            
        # except KeyError as e:
        #     logger.error(f"Missing key in response: {str(e)}")
        #     raise
        # except json.JSONDecodeError:
        #     logger.error("Invalid JSON in LLM response")
        #     raise





    def _get_params_from_task(self, task: str) -> dict:
        """Heuristic to extract key params for cache key"""
        return {
            "input": "/data/dates.txt" if "dates.txt" in task else None,
            "day": "wednesday" if "wednesday" in task.lower() else None
        }
    


        # result = response.json()
        # print(result)
        # final_params = json.loads(result["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])
        # choice = result["choices"][0]
        
        # # Save to cache with final params
        # save_response(task_description, final_params, result)

        # return response.json()["choices"][0]["message"]


# Og API call
        # payload = {
        #     "model": "gpt-4o-mini",
        #     "messages": [{"role": "user", "content": task_description}],
        #     "tools": [{
        #         "type": "function",
        #         "function": schema
        #     } for schema in self.get_function_schemas()]
        # }