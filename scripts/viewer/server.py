# -*- coding: utf-8 -*-
"""
HTTP Server module for the MythWeave Lore Explorer.
Routes client API requests to database functions and serves the HTML frontend.
"""
import http.server
import socketserver
import urllib.parse
import json
import os
import sys
import webbrowser
from .database import (
    get_tables, get_table_data, get_characters_graph,
    get_locations_graph, get_quests_graph, get_future_graphs_todo,
    get_story_branches_graph, get_timeline_graph,
    get_factions_graph, get_crafting_graph, get_progression_graph
)
from .frontend import HTML_CONTENT

PORT = 8080

class ViewerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        
        # API: List Tables
        if parsed_url.path == "/api/tables":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            tables = get_tables()
            self.wfile.write(json.dumps(tables).encode('utf-8'))
            
        # API: Table Data
        elif parsed_url.path == "/api/data":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            table_name = query_params.get("table", [None])[0]
            
            if not table_name:
                self.send_error(400, "Missing table parameter")
                return
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            rows = get_table_data(table_name)
            self.wfile.write(json.dumps(rows, default=str).encode('utf-8'))
            
        # API: Character Graph
        elif parsed_url.path == "/api/graph/characters":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            graph_data = get_characters_graph()
            self.wfile.write(json.dumps(graph_data).encode('utf-8'))
            
        # API: Locations Graph
        elif parsed_url.path == "/api/graph/locations":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            graph_data = get_locations_graph()
            self.wfile.write(json.dumps(graph_data).encode('utf-8'))
            
        # API: Quests Graph
        elif parsed_url.path == "/api/graph/quests":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            graph_data = get_quests_graph()
            self.wfile.write(json.dumps(graph_data).encode('utf-8'))
            
        # API: Future Graphs Todo
        elif parsed_url.path == "/api/todo":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            todo_data = get_future_graphs_todo()
            self.wfile.write(json.dumps(todo_data).encode('utf-8'))
            
        # API: Story Branches Graph
        elif parsed_url.path == "/api/graph/story_branches":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            graph_data = get_story_branches_graph()
            self.wfile.write(json.dumps(graph_data).encode('utf-8'))
            
        # API: Timeline Graph
        elif parsed_url.path == "/api/graph/timeline":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            graph_data = get_timeline_graph()
            self.wfile.write(json.dumps(graph_data).encode('utf-8'))

        # API: Factions Diplomacy Graph
        elif parsed_url.path == "/api/graph/factions":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            graph_data = get_factions_graph()
            self.wfile.write(json.dumps(graph_data).encode('utf-8'))

        # API: Crafting & Recipes Graph
        elif parsed_url.path == "/api/graph/crafting":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            graph_data = get_crafting_graph()
            self.wfile.write(json.dumps(graph_data).encode('utf-8'))

        # API: Progression & Skill Trees Graph
        elif parsed_url.path == "/api/graph/progression":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            graph_data = get_progression_graph()
            self.wfile.write(json.dumps(graph_data).encode('utf-8'))
            
        # Frontend index html page
        elif parsed_url.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
            
        else:
            self.send_error(404, "Not Found")

def start_server():
    db_path = "lore_system.db"
    if not os.path.exists(db_path):
        print(f"❌ Error: Database file '{db_path}' not found in the current directory.")
        sys.exit(1)
        
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), ViewerHandler) as httpd:
        print("==================================================")
        print("🎮 MythWeave Modular Lore & Graph Explorer")
        print("==================================================")
        print(f"🔗 URL: http://localhost:{PORT}")
        print(f"📁 Database: {os.path.abspath(db_path)}")
        print("📊 Modes: Data Tables, Characters Graph, Quests Flow, Locations Map")
        print("💡 Press Ctrl+C to stop the viewer.")
        print("==================================================")
        
        # Open browser
        webbrowser.open(f"http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down viewer server...")
