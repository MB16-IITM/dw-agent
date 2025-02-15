from fastapi import APIRouter, Query, HTTPException
from src.utils.llm import TaskHandler
from src.tasks import a1, a2, a3, a4, a5, a6, a7, a8, a9, a10
from src.tasks import b3, b4, b5, b6, b7
import json
import logging
from fastapi import Response

router = APIRouter()
handler = TaskHandler()
logger = logging.getLogger(__name__)

@router.post("/run")
async def execute_task(task: str = Query(...)):
    try:
        parsed = handler.parse_task(task)
        
        if not isinstance(parsed.get("tool_calls"), list) or len(parsed["tool_calls"]) == 0:
            raise HTTPException(400, "Invalid task structure")
            
        tool_call = parsed["tool_calls"][0]
        if not isinstance(tool_call.get("function"), dict):
            raise HTTPException(400, "Malformed function call")
        func_name = tool_call["function"]["name"]
        params = json.loads(tool_call["function"]["arguments"])
        
        # Handle A1 specifically
        if func_name == "a1_install_run":
            # Enforce default email if missing
            if "user_email" not in params:
                params["user_email"] = "24f1001631@ds.study.iitm.ac.in"
            result = a1.handle_a1(params)
            # return {"result": result}
            
        elif func_name == "a2_format_markdown":
            result = a2.handle_a2(params)
            # return {"result": result}
        
        elif func_name == "a3_count_weekdays":
            params.setdefault("input_file", "/data/dates.txt")
            params.setdefault("output_file", "/data/days-count.txt")
            if not params.get("weekday"):
                raise HTTPException(400, "Missing day parameter")
            result = a3.handle_a3(params)
            # return {"result": result}
        elif func_name == "a4_sort_contacts":
            # Enforce default paths if not provided
            params.setdefault("input_file", "/data/contacts.json")
            params.setdefault("output_file", "/data/contacts-sorted.json")
            
            try:
                result = a4.handle_a4(params)
                # return {"result": result}
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"Sorting failed: {str(e)}")
        elif func_name == "a5_process_logs":
            params.setdefault("input_dir", "/data/logs")
            params.setdefault("output_file", "/data/logs-recent.txt")
            try:
                result = a5.handle_a5(params)
                # return {"result": result}
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"Log processing failed: {str(e)}")
        elif func_name == "a6_generate_md_index":
            try:
                params.setdefault("input_dir", "/data/docs")
                params.setdefault("output_file", "/data/docs/index.json")
                result = a6.handle_a6(params)
                # return{"result": result}
            except Exception as e:
                raise HTTPException(500, f"Index generation failed: {str(e)}")
        elif func_name == "a7_extract_email":
            params.setdefault("input_file", "/data/email.txt")
            params.setdefault("output_file", "/data/email-sender.txt")
            try:
                result = a7.handle_a7(params)
                # return {"result": result}
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"Email extraction failed: {str(e)}")
        elif func_name == "a8_extract_cc_number":
            params.setdefault("input_file", "/data/credit-card.png")
            params.setdefault("output_file", "/data/credit-card.txt")
            try:
                result = a8.handle_a8(params)
                # return {"result": result}
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"CC extraction failed: {str(e)}")
        elif func_name == "a9_find_similar_comments":
            params.setdefault("input_file", "/data/comments.txt")
            params.setdefault("output_file", "/data/comments-similar.txt")
            try:
                result = a9.handle_a9(params)
                # return {"result": result}
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"Similarity check failed: {str(e)}")
        elif func_name == "a10_calculate_sales":
            params.setdefault("db_path", "/data/ticket-sales.db")
            params.setdefault("output_file", "/data/ticket-sales-gold.txt")
            try:
                result = a10.handle_a10(params)
                # return {"result": result}
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"Sales calculation failed: {str(e)}")
        elif func_name == "b3_fetch_api":
            try:
                result = b3.handle_b3(params)
                # return {"result": result}
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"API fetch failed: {str(e)}")
            # Add in the execute_task() function's conditional block
        elif func_name == "b4_git_ops":
            try:
                # Enforce required parameters
                if not params.get("repository_url") or not params.get("commit_message"):
                    raise HTTPException(400, "Missing required git parameters")
                    
                # Set default file patterns if not provided
                params.setdefault("file_patterns", ["."])
                
                result = b4.handle_b4(params)
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"Git operation failed: {str(e)}")
        elif func_name == "b5_execute_sql":
            try:
                # Enforce parameterized queries
                if "?" in params["query"] and not params.get("parameters"):
                    raise HTTPException(400, "Missing parameters for parameterized query")
                    
                result = b5.handle_b5(params)
                print(result)
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"SQL execution failed: {str(e)}")
        elif func_name == "b6_scrape_website":
            try:
                params.setdefault("selectors", [])
                result = b6.handle_b6(params)
                return {"result": result}
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"Scraping failed: {str(e)}")
        elif func_name == "b7_process_image":
            try:
                # Enforce output path validation
                if not params["output_path"].startswith("/data/"):
                    raise HTTPException(400, "Output path must be under /data")
                    
                result = b7.handle_b7(params)
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"Image processing failed: {str(e)}")
        elif func_name == "b9_markdown_to_html":
            try:
                # Enforce file patterns
                if not params["input_file"].endswith('.md'):
                    raise HTTPException(400, "Input must be .md file")
                if not params["output_file"].endswith('.html'):
                    raise HTTPException(400, "Output must be .html")
                    
                result = b9.handle_b9(params)
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(500, f"Markdown conversion failed: {str(e)}")
        return Response(status_code=200)
    
        
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid parameters: {str(e)}")
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        raise HTTPException(500, f"Execution error: {str(e)}")



        # elif func_name == "a3_count_days":
        #     # Enforce default paths
        #     params.setdefault("input_file", "/data/dates.txt")
        #     params.setdefault("output_file", "/data/days-count.txt")
            
        #     if not params.get("day"):
        #         raise HTTPException(400, "Missing day parameter")
                
        #     try:
        #         result = a3.handle_a3(
        #             input_path=params["input_file"],
        #             output_path=params["output_file"],
        #             day=params["day"].lower()
        #         )
        #         return {"result": result}
        #     except FileNotFoundError as e:
        #         raise HTTPException(404, str(e))