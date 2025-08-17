"""Flask web application for Gmail inbox triage."""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
from typing import List, Dict

from .gmail_client import GmailClient, EmailMessage
from .email_clusterer import EmailClusterer, EmailCluster
from .demo_data import generate_demo_emails

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Global storage for current session
current_clusters: List[EmailCluster] = []
current_gmail_client: GmailClient = None


@app.route("/")
def index():
    """Main page with login form."""
    return render_template("index.html")


@app.route("/test")
def test():
    """Test endpoint to verify server is working."""
    return jsonify({"status": "ok", "message": "Server is working!"})


@app.route("/login", methods=["POST"])
def login():
    """Handle Gmail authentication and email clustering."""
    global current_clusters, current_gmail_client
    
    try:
        print("Login attempt received")
        data = request.get_json()
        print(f"Received data: {data}")
        
        email_address = data.get("email") if data else None
        app_password = data.get("password") if data else None
        num_clusters = int(data.get("clusters", 5)) if data else 5
        email_count = int(data.get("count", 200)) if data else 200
        
        print(f"Email: {email_address}, Clusters: {num_clusters}, Count: {email_count}")
        
        if not email_address or not app_password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Use demo data for now to test the interface
        if email_address == "demo@gmail.com":
            print("Using demo data...")
            emails = generate_demo_emails(email_count)
            print(f"Generated {len(emails)} demo emails")
        else:
            print("Connecting to Gmail...")
            # Connect to Gmail
            current_gmail_client = GmailClient(email_address, app_password)
            current_gmail_client.connect()
            print("Connected successfully")
            
            print("Fetching emails...")
            # Fetch emails
            emails = current_gmail_client.fetch_recent_emails(email_count)
            print(f"Fetched {len(emails)} emails")
        
        print("Clustering emails...")
        # Cluster emails
        clusterer = EmailClusterer()
        current_clusters = clusterer.cluster_emails(emails, num_clusters)
        print(f"Created {len(current_clusters)} clusters")
        
        # Prepare cluster data for frontend
        clusters_data = []
        for cluster in current_clusters:
            emails_data = []
            for email in cluster.emails:
                emails_data.append({
                    "uid": str(email.uid),
                    "subject": str(email.subject),
                    "sender": str(email.sender),
                    "date": email.date.strftime("%Y-%m-%d %H:%M") if email.date else "N/A",
                    "preview": str(email.body_preview),
                    "has_attachments": bool(email.has_attachments)
                })
            
            clusters_data.append({
                "id": int(cluster.cluster_id),
                "name": cluster.name,
                "description": cluster.description,
                "keywords": cluster.keywords,
                "email_count": len(cluster.emails),
                "emails": emails_data
            })
        
        print("Sending response...")
        return jsonify({
            "success": True,
            "clusters": clusters_data,
            "total_emails": len(emails)
        })
        
    except Exception as e:
        print(f"Error in login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/archive_cluster", methods=["POST"])
def archive_cluster():
    """Archive all emails in a specific cluster."""
    global current_clusters, current_gmail_client
    
    try:
        data = request.get_json()
        cluster_id = int(data.get("cluster_id"))
        
        if not current_gmail_client:
            return jsonify({"error": "Not connected to Gmail"}), 400
        
        # Find the cluster
        target_cluster = None
        for cluster in current_clusters:
            if cluster.cluster_id == cluster_id:
                target_cluster = cluster
                break
        
        if not target_cluster:
            return jsonify({"error": "Cluster not found"}), 404
        
        # Archive emails
        email_uids = [email.uid for email in target_cluster.emails]
        current_gmail_client.archive_emails(email_uids)
        
        # Remove cluster from current list
        current_clusters = [c for c in current_clusters if c.cluster_id != cluster_id]
        
        return jsonify({
            "success": True,
            "message": f"Archived {len(email_uids)} emails from '{target_cluster.name}'"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/disconnect", methods=["POST"])
def disconnect():
    """Disconnect from Gmail."""
    global current_gmail_client
    
    if current_gmail_client:
        current_gmail_client.disconnect()
        current_gmail_client = None
    
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)