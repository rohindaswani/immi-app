import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemPromptBuilder:
    """Builds context-aware system prompts for AI chat with user document data"""
    
    def __init__(self):
        self.base_prompt = self._get_base_immigration_prompt()
    
    def build_system_prompt(self, user_context: Dict[str, Any]) -> str:
        """
        Build a comprehensive system prompt including user's document context
        """
        try:
            if "error" in user_context:
                return self.base_prompt
            
            # Build the full context-aware prompt
            prompt_parts = [
                self.base_prompt,
                self._build_user_context_section(user_context),
                self._build_documents_section(user_context.get("documents", {})),
                self._build_compliance_section(user_context.get("compliance_alerts", {})),
                self._build_guidelines_section()
            ]
            
            return "\n\n".join(filter(None, prompt_parts))
            
        except Exception as e:
            logger.error(f"Error building system prompt: {str(e)}")
            return self.base_prompt
    
    def _get_base_immigration_prompt(self) -> str:
        """Base immigration assistant prompt"""
        return """You are an expert immigration advisor AI assistant specializing in U.S. immigration law and processes. You help users navigate complex immigration procedures, understand their status, track important deadlines, and make informed decisions about their immigration journey.

Your expertise includes:
- All U.S. visa categories (H-1B, L-1, O-1, F-1, etc.)
- Green card processes and priority dates
- Travel and re-entry requirements
- Document requirements and renewals
- Compliance and deadline management
- Immigration policy updates and changes

You provide accurate, helpful guidance while being clear about the limitations of AI advice and when users should consult licensed immigration attorneys.

IMPORTANT: Even if the user's profile data is not available, you should still provide comprehensive immigration advice based on the information provided in their question."""
    
    def _build_user_context_section(self, context: Dict[str, Any]) -> str:
        """Build user-specific context section"""
        if not context:
            return ""
        
        profile = context.get("user_profile", {})
        status_info = context.get("immigration_status", {})
        summary = context.get("context_summary", "")
        
        if not profile and not summary:
            return ""
        
        section = "## USER CONTEXT\n"
        
        if summary:
            section += f"**Current Situation:** {summary}\n\n"
        
        # Personal details
        if profile.get("full_name"):
            section += f"**Name:** {profile['full_name']}\n"
        
        if profile.get("nationality"):
            section += f"**Nationality:** {profile['nationality']}\n"
        
        # Immigration status
        current_status = status_info.get("current_status") or profile.get("current_status")
        if current_status:
            section += f"**Current Immigration Status:** {current_status}\n"
        
        if profile.get("authorized_until"):
            section += f"**Authorized Stay Until:** {profile['authorized_until']}\n"
        
        # Employment
        if profile.get("employer"):
            section += f"**Current Employer:** {profile['employer']}\n"
        
        if profile.get("job_title"):
            section += f"**Job Title:** {profile['job_title']}\n"
        
        # Priority dates
        priority_dates = profile.get("priority_dates")
        if priority_dates and isinstance(priority_dates, dict):
            section += "**Priority Dates:**\n"
            for category, info in priority_dates.items():
                if isinstance(info, dict) and "date" in info:
                    section += f"  - {category}: {info['date']}\n"
        
        return section
    
    def _build_documents_section(self, documents: Dict[str, Any]) -> str:
        """Build documents context section with sensitive data protection"""
        if not documents:
            return ""
        
        section = "## USER DOCUMENTS\n"
        section += "The user has uploaded the following documents (sensitive numbers redacted for security):\n\n"
        
        for doc_type, doc_list in documents.items():
            if not doc_list:
                continue
                
            doc_type_name = doc_type.replace('_', ' ').title()
            section += f"**{doc_type_name}:**\n"
            
            for doc in doc_list:
                doc_line = f"  - "
                
                # Use redacted version if available
                if doc.get("document_number_partial"):
                    doc_line += f"Number: {doc['document_number_partial']}"
                elif doc.get("has_document_number"):
                    doc_line += "Document number on file"
                
                if doc.get("issuing_authority"):
                    doc_line += f", Issued by: {doc['issuing_authority']}"
                
                if doc.get("issue_date"):
                    doc_line += f", Issued: {doc['issue_date']}"
                
                if doc.get("expiry_date"):
                    doc_line += f", Expires: {doc['expiry_date']}"
                
                if doc.get("is_verified"):
                    doc_line += " (Verified)"
                
                section += doc_line + "\n"
            
            section += "\n"
        
        return section
    
    def _build_compliance_section(self, compliance: Dict[str, Any]) -> str:
        """Build compliance alerts section"""
        alerts = compliance.get("alerts", [])
        if not alerts:
            return ""
        
        section = "## COMPLIANCE ALERTS\n"
        section += "⚠️ **IMPORTANT:** The following documents require attention:\n\n"
        
        # Group by urgency
        critical = [a for a in alerts if a.get("urgency") == "critical"]
        high = [a for a in alerts if a.get("urgency") == "high"]
        medium = [a for a in alerts if a.get("urgency") == "medium"]
        low = [a for a in alerts if a.get("urgency") == "low"]
        
        if critical:
            section += "**🚨 CRITICAL - EXPIRED:**\n"
            for alert in critical:
                doc_name = alert.get("document", "").replace('_', ' ').title()
                days_expired = alert.get("days_expired", 0)
                section += f"  - {doc_name} expired {days_expired} days ago\n"
            section += "\n"
        
        if high:
            section += "**🔴 HIGH PRIORITY - EXPIRING SOON:**\n"
            for alert in high:
                doc_name = alert.get("document", "").replace('_', ' ').title()
                days_remaining = alert.get("days_remaining", 0)
                section += f"  - {doc_name} expires in {days_remaining} days\n"
            section += "\n"
        
        if medium:
            section += "**🟡 MEDIUM PRIORITY:**\n"
            for alert in medium:
                doc_name = alert.get("document", "").replace('_', ' ').title()
                days_remaining = alert.get("days_remaining", 0)
                section += f"  - {doc_name} expires in {days_remaining} days\n"
            section += "\n"
        
        if low:
            section += "**🟢 UPCOMING:**\n"
            for alert in low:
                doc_name = alert.get("document", "").replace('_', ' ').title()
                days_remaining = alert.get("days_remaining", 0)
                section += f"  - {doc_name} expires in {days_remaining} days\n"
            section += "\n"
        
        return section
    
    def _build_guidelines_section(self) -> str:
        """Build response guidelines section"""
        return """## RESPONSE GUIDELINES

When responding to the user:

1. **Use their context:** Reference their specific documents, status, and situation
2. **Be proactive:** Mention relevant deadlines, required actions, or opportunities
3. **Prioritize urgency:** Address critical/expired items first
4. **Be specific:** Use document numbers, dates, and exact requirements when available
5. **Explain implications:** Help them understand what their situation means
6. **Suggest next steps:** Provide actionable advice based on their documents
7. **Legal disclaimer:** Remind them to consult an attorney for complex legal matters

Remember: You have access to their complete immigration document portfolio. Use this information to provide personalized, relevant advice."""