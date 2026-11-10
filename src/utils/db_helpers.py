import os
import pandas as pd

try:
    import oracledb
except ImportError:
    oracledb = None

# Allow setting Oracle client path via environment variable, with fallback
DEFAULT_ORACLE_CLIENT_DIR = r"D:\Trash\DBMS\Oracle\instantclient-basic-windows.x64-23.26.3.0.0\instantclient_23_26"
oracle_client_dir = os.environ.get("ORACLE_CLIENT_DIR", DEFAULT_ORACLE_CLIENT_DIR)

if oracledb is not None and oracle_client_dir and os.path.exists(oracle_client_dir):
    try:
        oracledb.init_oracle_client(lib_dir=oracle_client_dir)
    except Exception as e:
        # If already initialized (common during Streamlit re-runs), safely ignore
        if "already initialized" not in str(e).lower():
            pass

def execute_safe_query(query, db_user, db_password, db_dsn):
    """
    Executes a SQL query on the Oracle database and returns the results.
    This function should only be called AFTER the AI model marks the query as safe.
    """
    if oracledb is None:
        return {
            "status": "error",
            "message": "The 'oracledb' library is not installed. Please install it using 'pip install oracledb' to enable live database execution."
        }

    connection = None
    cursor = None
    try:
        # Connect to Oracle (operates in Thick mode if initialized, or Thin mode)
        connection = oracledb.connect(user=db_user, password=db_password, dsn=db_dsn)
        cursor = connection.cursor()
        
        cursor.execute(query)
        
        # If it's a SELECT query, fetch and return the data as a Pandas DataFrame
        if query.strip().upper().startswith("SELECT"):
            columns = [col[0] for col in cursor.description] if cursor.description else []
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            return {"status": "success", "data": df}
        
        # If it's an INSERT/UPDATE/DELETE, commit the changes
        else:
            connection.commit()
            return {"status": "success", "message": "Query executed and committed successfully."}
            
    except oracledb.Error as e:
        error_message = str(e)
        if e.args and len(e.args) > 0 and hasattr(e.args[0], 'message'):
            error_message = e.args[0].message
        return {"status": "error", "message": error_message}
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass
