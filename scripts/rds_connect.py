[ec2-user@ip-10-0-0-199 ~]$ cat rds_connect.py
import mysql.connector
from mysql.connector import Error
import os
from typing import List, Tuple, Any

class RDSConnection:
    def __init__(self):
        # RDS Connection Configuration
        self.config = {
            'host': os.getenv('RDS_HOST'),
            'port': 3306,
            'user': os.getenv('RDS_USER'),
            'password': os.getenv('RDS_PASSWORD'),  # Store password in environment variable
            'database': os.getenv('RDS_DATABASE', 'mysql'),  # Default to 'mysql' system database
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': False
        }
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Establish connection to RDS MySQL instance"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(buffered=True)
                print(f"Successfully connected to MySQL RDS instance")
                print(f"Server version: {self.connection.get_server_info()}")
                return True
        except Error as e:
            print(f"Error connecting to MySQL RDS: {e}")
            return False

    def execute_query(self, query: str, params: Tuple = None) -> List[Tuple[Any, ...]]:
        """Execute SELECT query and return results"""
        try:
            if not self.connection or not self.connection.is_connected():
                print("No active connection. Attempting to reconnect...")
                if not self.connect():
                    return []

            self.cursor.execute(query, params)
            results = self.cursor.fetchall()

            # Get column names
            columns = [desc[0] for desc in self.cursor.description]
            print(f"Query executed successfully. Columns: {columns}")

            return results
        except Error as e:
            print(f"Error executing query: {e}")
            return []

    def execute_update(self, query: str, params: Tuple = None) -> int:
        """Execute INSERT, UPDATE, DELETE queries"""
        try:
            if not self.connection or not self.connection.is_connected():
                print("No active connection. Attempting to reconnect...")
                if not self.connect():
                    return 0

            self.cursor.execute(query, params)
            self.connection.commit()

            affected_rows = self.cursor.rowcount
            print(f"Query executed successfully. Affected rows: {affected_rows}")
            return affected_rows
        except Error as e:
            print(f"Error executing update: {e}")
            self.connection.rollback()
            return 0

    def execute_batch(self, query: str, data: List[Tuple]) -> int:
        """Execute batch operations"""
        try:
            if not self.connection or not self.connection.is_connected():
                print("No active connection. Attempting to reconnect...")
                if not self.connect():
                    return 0

            self.cursor.executemany(query, data)
            self.connection.commit()

            affected_rows = self.cursor.rowcount
            print(f"Batch query executed successfully. Affected rows: {affected_rows}")
            return affected_rows
        except Error as e:
            print(f"Error executing batch: {e}")
            self.connection.rollback()
            return 0

    def get_databases(self) -> List[str]:
        """List all databases"""
        results = self.execute_query("SHOW DATABASES")
        return [db[0] for db in results]

    def get_tables(self, database: str = None) -> List[str]:
        """List all tables in current or specified database"""
        if database:
            self.execute_query(f"USE {database}")

        results = self.execute_query("SHOW TABLES")
        return [table[0] for table in results]

    def describe_table(self, table_name: str) -> List[Tuple]:
        """Get table structure"""
        return self.execute_query(f"DESCRIBE {table_name}")

    def close(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("MySQL RDS connection closed")
        except Error as e:
            print(f"Error closing connection: {e}")

# Example usage
def main():
    # Initialize connection
    db = RDSConnection()

    try:
        # Connect to database
        if not db.connect():
            print("Failed to connect to database")
            return

        # Example 1: List all databases
        print("\n=== Available Databases ===")
        databases = db.get_databases()
        for db_name in databases:
            print(f"- {db_name}")

        # Example 2: Create a sample table (if you have a specific database)
        # Uncomment and modify as needed
        """
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        db.execute_update(create_table_query)
        """

        # Example 3: Insert sample data
        """
        insert_query = "INSERT INTO users (username, email) VALUES (%s, %s)"
        sample_data = [
            ('john_doe', 'john@example.com'),
            ('jane_smith', 'jane@example.com'),
            ('bob_wilson', 'bob@example.com')
        ]
        db.execute_batch(insert_query, sample_data)
        """

        # Example 4: Query data
        """
        select_query = "SELECT * FROM users WHERE created_at >= %s"
        results = db.execute_query(select_query, ('2024-01-01',))

        print("\n=== Query Results ===")
        for row in results:
            print(row)
        """

        # Example 5: Show server status
        status_results = db.execute_query("SHOW STATUS LIKE 'Connections'")
        print(f"\n=== Server Status ===")
        for status in status_results:
            print(f"{status[0]}: {status[1]}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Always close the connection
        db.close()

if __name__ == "__main__":
    main()
