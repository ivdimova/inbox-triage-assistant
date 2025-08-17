"""Email clustering functionality using machine learning."""

import re
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import Counter

from .gmail_client import EmailMessage


@dataclass
class EmailCluster:
    """Represents a cluster of related emails."""
    cluster_id: int
    name: str
    description: str
    emails: List[EmailMessage]
    keywords: List[str]


class EmailClusterer:
    """Clusters emails into actionable groups using ML and heuristics."""
    
    def __init__(self, min_cluster_size: int = 3):
        self.min_cluster_size = min_cluster_size
    
    def cluster_emails(self, emails: List[EmailMessage], 
                      num_clusters: int = 5) -> List[EmailCluster]:
        """Cluster emails into actionable groups using rule-based approach."""
        if len(emails) < self.min_cluster_size:
            return [self._create_single_cluster(emails)]
        
        # Use lightweight rule-based clustering instead of ML
        return self._rule_based_clustering(emails)
    
    def _prepare_email_texts(self, emails: List[EmailMessage]) -> List[str]:
        """Prepare email content for vectorization."""
        texts = []
        for email in emails:
            # Combine subject and body preview for clustering
            combined_text = f"{email.subject} {email.body_preview}"
            # Clean text
            cleaned_text = re.sub(r'[^\w\s]', ' ', combined_text.lower())
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            texts.append(cleaned_text)
        return texts
    
    def _group_emails_by_cluster(self, emails: List[EmailMessage], 
                                labels: np.ndarray) -> Dict[int, List[EmailMessage]]:
        """Group emails by their cluster labels."""
        clusters = {}
        for email, label in zip(emails, labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(email)
        return clusters
    
    def _analyze_cluster(self, cluster_emails: List[EmailMessage], 
                        cluster_id: int) -> EmailCluster:
        """Analyze a cluster to generate name, description, and keywords."""
        # Extract keywords from subjects and senders
        subjects = [email.subject for email in cluster_emails]
        senders = [email.sender for email in cluster_emails]
        
        # Find common keywords
        all_words = []
        for subject in subjects:
            words = re.findall(r'\b\w+\b', subject.lower())
            all_words.extend(words)
        
        # Get most common keywords
        word_counts = Counter(all_words)
        common_words = [word for word, count in word_counts.most_common(5) 
                       if count > 1 and len(word) > 2]
        
        # Analyze sender patterns
        sender_domains = [self._extract_domain(sender) for sender in senders]
        domain_counts = Counter(sender_domains)
        top_domain = domain_counts.most_common(1)[0][0] if domain_counts else ""
        
        # Generate cluster name and description
        name, description = self._generate_cluster_info(
            common_words, top_domain, len(cluster_emails)
        )
        
        return EmailCluster(
            cluster_id=cluster_id,
            name=name,
            description=description,
            emails=cluster_emails,
            keywords=common_words
        )
    
    def _generate_cluster_info(self, keywords: List[str], 
                              domain: str, count: int) -> tuple[str, str]:
        """Generate descriptive name and description for cluster."""
        if not keywords and not domain:
            return f"Mixed Messages ({count})", f"Cluster of {count} diverse emails"
        
        if domain and any(service in domain for service in 
                         ["newsletter", "marketing", "promo", "deals"]):
            return f"Marketing & Newsletters ({count})", f"Promotional emails from {domain}"
        
        if domain and any(service in domain for service in 
                         ["github", "gitlab", "bitbucket"]):
            return f"Code Repository Updates ({count})", f"Notifications from {domain}"
        
        if domain and any(service in domain for service in 
                         ["slack", "teams", "discord"]):
            return f"Team Communication ({count})", f"Messages from {domain}"
        
        if keywords:
            primary_keyword = keywords[0].title()
            return f"{primary_keyword} Related ({count})", f"Emails about {primary_keyword.lower()}"
        
        if domain:
            clean_domain = domain.replace(".com", "").replace("www.", "").title()
            return f"{clean_domain} Messages ({count})", f"Emails from {domain}"
        
        return f"Uncategorized ({count})", f"Cluster of {count} emails"
    
    def _extract_domain(self, sender: str) -> str:
        """Extract domain from sender email address."""
        match = re.search(r'@([^>\s]+)', sender)
        return match.group(1) if match else ""
    
    def _create_single_cluster(self, emails: List[EmailMessage]) -> EmailCluster:
        """Create a single cluster when there are too few emails."""
        return EmailCluster(
            cluster_id=0,
            name=f"All Messages ({len(emails)})",
            description=f"All {len(emails)} recent emails",
            emails=emails,
            keywords=[]
        )
    
    def _create_miscellaneous_cluster(self, emails: List[EmailMessage]) -> EmailCluster:
        """Create cluster for miscellaneous small groups."""
        return EmailCluster(
            cluster_id=999,
            name=f"Miscellaneous ({len(emails)})",
            description=f"Various emails that don't fit other categories",
            emails=emails,
            keywords=[]
        )
    
    def _rule_based_clustering(self, emails: List[EmailMessage]) -> List[EmailCluster]:
        """Simple rule-based clustering as fallback."""
        domain_groups = {}
        
        for email in emails:
            domain = self._extract_domain(email.sender)
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append(email)
        
        clusters = []
        cluster_id = 0
        
        for domain, domain_emails in domain_groups.items():
            if len(domain_emails) >= self.min_cluster_size:
                clean_domain = domain.replace(".com", "").replace("www.", "").title()
                clusters.append(EmailCluster(
                    cluster_id=cluster_id,
                    name=f"{clean_domain} ({len(domain_emails)})",
                    description=f"Emails from {domain}",
                    emails=domain_emails,
                    keywords=[]
                ))
                cluster_id += 1
        
        return clusters if clusters else [self._create_single_cluster(emails)]