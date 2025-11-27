"""
Database Module - SQLite Storage for Research History

This module provides persistent storage for:
- Research queries
- Findings
- Generated summaries
- Session history

WHY DATABASE?
- Track all research over time
- Enable analytics on research patterns
- Provide audit trail
- Support offline access to past research
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ResearchDatabase:
    """
    SQLite database for storing research history.
    
    Tables:
    - queries: Stores research queries
    - findings: Stores individual findings
    - summaries: Stores generated summaries
    - sessions: Tracks research sessions
    """
    
    def __init__(self, db_path: str = "./research_history.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Queries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        # Findings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id INTEGER,
                title TEXT,
                source TEXT,
                content TEXT,
                relevance TEXT,
                quality_tier TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (query_id) REFERENCES queries (id)
            )
        """)
        
        # Summaries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id INTEGER,
                executive_summary TEXT,
                key_insights TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (query_id) REFERENCES queries (id)
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                query_count INTEGER DEFAULT 0
            )
        """)
        
        self.conn.commit()
        print("   📁 Database initialized")
    
    def save_query(self, query: str, session_id: Optional[str] = None) -> int:
        """
        Save a new research query.
        
        Args:
            query: The research query
            session_id: Optional session identifier
            
        Returns:
            The ID of the saved query
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO queries (query, session_id) VALUES (?, ?)",
            (query, session_id)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def save_findings(self, query_id: int, findings: List[Dict]) -> None:
        """
        Save research findings for a query.
        
        Args:
            query_id: The ID of the associated query
            findings: List of finding dictionaries
        """
        cursor = self.conn.cursor()
        
        for finding in findings:
            cursor.execute("""
                INSERT INTO findings 
                (query_id, title, source, content, relevance, quality_tier)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                query_id,
                finding.get("title", ""),
                finding.get("source", ""),
                finding.get("content", ""),
                finding.get("relevance", ""),
                finding.get("quality_tier", "unknown")
            ))
        
        self.conn.commit()
        print(f"   💾 Saved {len(findings)} findings to database")
    
    def save_summary(self, query_id: int, summary: str, insights: List[str]) -> None:
        """
        Save the executive summary for a query.
        
        Args:
            query_id: The ID of the associated query
            summary: The executive summary text
            insights: List of key insights
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO summaries (query_id, executive_summary, key_insights)
            VALUES (?, ?, ?)
        """, (query_id, summary, json.dumps(insights)))
        
        # Update query status
        cursor.execute(
            "UPDATE queries SET status = 'completed' WHERE id = ?",
            (query_id,)
        )
        
        self.conn.commit()
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict]:
        """Get the most recent research queries."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, query, timestamp, status
            FROM queries
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_query_with_results(self, query_id: int) -> Optional[Dict]:
        """Get a query with all its findings and summary."""
        cursor = self.conn.cursor()
        
        # Get query
        cursor.execute("SELECT * FROM queries WHERE id = ?", (query_id,))
        query_row = cursor.fetchone()
        if not query_row:
            return None
        
        result = dict(query_row)
        
        # Get findings
        cursor.execute("SELECT * FROM findings WHERE query_id = ?", (query_id,))
        result["findings"] = [dict(row) for row in cursor.fetchall()]
        
        # Get summary
        cursor.execute("SELECT * FROM summaries WHERE query_id = ?", (query_id,))
        summary_row = cursor.fetchone()
        if summary_row:
            result["summary"] = dict(summary_row)
            result["summary"]["key_insights"] = json.loads(
                result["summary"]["key_insights"]
            )
        
        return result
    
    def search_past_research(self, keyword: str) -> List[Dict]:
        """Search past research by keyword."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT q.id, q.query, q.timestamp, s.executive_summary
            FROM queries q
            LEFT JOIN summaries s ON q.id = s.query_id
            WHERE q.query LIKE ? OR s.executive_summary LIKE ?
            ORDER BY q.timestamp DESC
            LIMIT 20
        """, (f"%{keyword}%", f"%{keyword}%"))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM queries")
        total_queries = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM findings")
        total_findings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM summaries")
        total_summaries = cursor.fetchone()[0]
        
        return {
            "total_queries": total_queries,
            "total_findings": total_findings,
            "total_summaries": total_summaries,
            "database_path": self.db_path
        }
    
    def start_session(self, session_id: str) -> None:
        """Record a new research session."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO sessions (id, start_time) VALUES (?, ?)",
            (session_id, datetime.now())
        )
        self.conn.commit()
    
    def end_session(self, session_id: str) -> None:
        """End a research session."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE sessions SET end_time = ? WHERE id = ?",
            (datetime.now(), session_id)
        )
        self.conn.commit()
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
    
    def export_to_csv(self, filepath: str = "./research_history.csv") -> str:
        """
        Export all research history to CSV file.
        
        Args:
            filepath: Path to save the CSV file
            
        Returns:
            Path to the created file
        """
        import csv
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                q.id,
                q.query,
                q.timestamp,
                q.status,
                s.executive_summary,
                s.key_insights
            FROM queries q
            LEFT JOIN summaries s ON q.id = s.query_id
            ORDER BY q.timestamp DESC
        """)
        
        rows = cursor.fetchall()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Query', 'Timestamp', 'Status', 'Executive Summary', 'Key Insights'])
            for row in rows:
                writer.writerow(row)
        
        print(f"📄 Exported {len(rows)} records to: {filepath}")
        return filepath
    
    def export_to_txt(self, filepath: str = "./research_history.txt") -> str:
        """
        Export all research history to TXT file (human readable).
        
        Args:
            filepath: Path to save the TXT file
            
        Returns:
            Path to the created file
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                q.id,
                q.query,
                q.timestamp,
                q.status,
                s.executive_summary,
                s.key_insights
            FROM queries q
            LEFT JOIN summaries s ON q.id = s.query_id
            ORDER BY q.timestamp DESC
        """)
        
        rows = cursor.fetchall()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("RESEARCH HISTORY EXPORT\n")
            f.write(f"Total Records: {len(rows)}\n")
            f.write("=" * 70 + "\n\n")
            
            for row in rows:
                id_, query, timestamp, status, summary, insights = row
                f.write(f"{'─' * 70}\n")
                f.write(f"ID: {id_} | Status: {status}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Query: {query}\n")
                f.write(f"{'─' * 70}\n")
                
                if summary:
                    f.write(f"\nEXECUTIVE SUMMARY:\n{summary}\n")
                
                if insights:
                    f.write(f"\nKEY INSIGHTS:\n{insights}\n")
                
                f.write("\n")
        
        print(f"📄 Exported {len(rows)} records to: {filepath}")
        return filepath
    
    def get_full_history(self) -> List[Dict]:
        """Get complete research history with all details."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                q.id,
                q.query,
                q.timestamp,
                q.status,
                s.executive_summary,
                s.key_insights,
                (SELECT COUNT(*) FROM findings f WHERE f.query_id = q.id) as finding_count
            FROM queries q
            LEFT JOIN summaries s ON q.id = s.query_id
            ORDER BY q.timestamp DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'query': row[1],
                'timestamp': row[2],
                'status': row[3],
                'summary': row[4],
                'insights': row[5],
                'finding_count': row[6]
            })
        return results


# Global database instance
_db_instance = None


def get_database(db_path: str = "./research_history.db") -> ResearchDatabase:
    """Get or create the database singleton."""
    global _db_instance
    if _db_instance is None:
        _db_instance = ResearchDatabase(db_path)
    return _db_instance
