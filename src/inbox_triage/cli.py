"""Command-line interface for the inbox triage assistant."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm
from typing import List

from .gmail_client import GmailClient, EmailMessage
from .email_clusterer import EmailClusterer, EmailCluster

console = Console()


@click.command()
@click.option("--email", help="Gmail email address")
@click.option("--password", help="Gmail app password")
@click.option("--clusters", default=5, help="Number of clusters to create")
@click.option("--count", default=200, help="Number of recent emails to process")
def triage(email: str, password: str, clusters: int, count: int):
    """Cluster and triage your Gmail inbox."""
    
    try:
        # Initialize Gmail client
        console.print("[bold blue]Connecting to Gmail...[/bold blue]")
        gmail_client = GmailClient(email, password)
        gmail_client.connect()
        
        # Fetch emails
        console.print(f"[bold blue]Fetching {count} recent emails...[/bold blue]")
        emails = gmail_client.fetch_recent_emails(count)
        console.print(f"[green]Found {len(emails)} emails[/green]")
        
        # Cluster emails
        console.print("[bold blue]Analyzing and clustering emails...[/bold blue]")
        clusterer = EmailClusterer()
        email_clusters = clusterer.cluster_emails(emails, clusters)
        
        # Display clusters
        display_clusters(email_clusters)
        
        # Interactive archive options
        handle_archive_actions(email_clusters, gmail_client)
        
        # Cleanup
        gmail_client.disconnect()
        console.print("[green]Session completed![/green]")
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise click.Abort()


def display_clusters(clusters: List[EmailCluster]) -> None:
    """Display email clusters in a formatted table."""
    console.print("\n[bold green]📧 Email Clusters[/bold green]")
    
    for i, cluster in enumerate(clusters, 1):
        # Create cluster header
        panel_title = f"Cluster {i}: {cluster.name}"
        
        # Create table for emails in this cluster
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("From", style="cyan", no_wrap=True, width=25)
        table.add_column("Subject", style="white", width=40)
        table.add_column("Date", style="yellow", width=12)
        table.add_column("Preview", style="dim white", width=30)
        
        # Add emails to table
        for email in cluster.emails[:10]:  # Show max 10 emails per cluster
            sender_short = email.sender.split('<')[0].strip()[:25]
            subject_short = email.subject[:40] + "..." if len(email.subject) > 40 else email.subject
            date_short = email.date.strftime("%m/%d") if email.date else "N/A"
            preview_short = email.body_preview[:30] + "..." if len(email.body_preview) > 30 else email.body_preview
            
            table.add_row(sender_short, subject_short, date_short, preview_short)
        
        # Show remaining count if there are more emails
        remaining = len(cluster.emails) - 10
        if remaining > 0:
            table.add_row("...", f"+ {remaining} more emails", "", "")
        
        # Create panel content
        panel_content = f"{cluster.description}\n"
        if cluster.keywords:
            panel_content += f"Keywords: {', '.join(cluster.keywords)}\n"
        panel_content += f"\n{table}"
        
        console.print(Panel(table, title=panel_title, expand=False))
        console.print()


def handle_archive_actions(clusters: List[EmailCluster], 
                          gmail_client: GmailClient) -> None:
    """Handle interactive archive actions for clusters."""
    console.print("[bold yellow]Archive Actions[/bold yellow]")
    
    for i, cluster in enumerate(clusters, 1):
        message = f"Archive all {len(cluster.emails)} emails in '{cluster.name}'?"
        
        if Confirm.ask(message, default=False):
            try:
                email_uids = [email.uid for email in cluster.emails]
                gmail_client.archive_emails(email_uids)
                console.print(f"[green]✓ Archived {len(cluster.emails)} emails from '{cluster.name}'[/green]")
            except Exception as e:
                console.print(f"[red]✗ Failed to archive '{cluster.name}': {e}[/red]")


@click.group()
def main():
    """Gmail Inbox Triage Assistant - Cluster and manage your emails efficiently."""
    pass


main.add_command(triage)


if __name__ == "__main__":
    main()