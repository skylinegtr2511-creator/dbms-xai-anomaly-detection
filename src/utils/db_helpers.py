import oracledb
import pandas as pd

# Initialize Thick mode using your exact D drive path
try:
    oracledb.init_oracle_client(lib_dir=r"D:\Trash\DBMS\Oracle\instantclient-basic-windows.x64-23.26.3.0.0\instantclient_23_26")
except Exception as e:
    pass # Streamlit reruns might trigger this, safe to pass if already initialized

def execute_safe_query(query, db_user, db_password, db_dsn):
    """
    Executes a SQL query on the Oracle database and returns the results.
    This function should only be called AFTER the AI model marks the query as safe.
    """
    try:
        # Connect to Oracle (Now operating in Thick mode)
        connection = oracledb.connect(user=db_user, password=db_password, dsn=db_dsn)
        cursor = connection.cursor()
        
        cursor.execute(query)
        
        # If it's a SELECT query, fetch and return the data as a Pandas DataFrame
        if query.strip().upper().startswith("SELECT"):
            columns = [col[0] for col in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            return {"status": "success", "data": df}
        
        # If it's an INSERT/UPDATE/DELETE, commit the changes
        else:
            connection.commit()
            return {"status": "success", "message": "Query executed and committed successfully."}
            
    except oracledb.Error as e:
        error_obj, = e.args
        return {"status": "error", "message": error_obj.message}
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()