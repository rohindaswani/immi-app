import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import time
import re
from uuid import UUID

from app.ai.context_service import ContextService
from app.core.ai_config import AIConfig


class ChatAIService:
    """Service for AI-powered chat responses with user context"""
    
    def __init__(self, context_service: ContextService):
        self.context_service = context_service
        self.config = AIConfig()
        self.llm_client = None
        
        # Initialize LLM client if configured
        if self.config.is_ai_enabled():
            if self.config.AI_PROVIDER == "openai":
                try:
                    from openai import AsyncOpenAI
                    self.llm_client = AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
                except ImportError:
                    print("OpenAI library not installed. Install with: pip install openai")
            elif self.config.AI_PROVIDER == "anthropic":
                try:
                    import anthropic
                    self.llm_client = anthropic.AsyncAnthropic(api_key=self.config.ANTHROPIC_API_KEY)
                except ImportError:
                    print("Anthropic library not installed. Install with: pip install anthropic")
        
        # Initialize rule-based patterns for common H1-B questions
        self.rule_patterns = self._initialize_rule_patterns()
    
    async def generate_response(
        self,
        user_id: UUID,
        conversation_id: UUID,
        message_id: UUID,
        user_message: str
    ) -> Dict[str, Any]:
        """Generate AI response with user-specific context using hybrid approach"""
        start_time = time.time()
        
        try:
            # Gather user context
            user_context = self.context_service.gather_user_context(
                user_id, 
                conversation_id,
                message_id
            )
            
            # First, check if this matches any rule-based patterns
            rule_response = self._check_rule_based_response(user_message, user_context)
            
            if rule_response:
                # Use rule-based response
                print(f"Using rule-based response for: {user_message[:50]}...")
                response_time_ms = int((time.time() - start_time) * 1000)
                return {
                    "content": rule_response,
                    "model_used": "rule-based",
                    "tokens_used": 0,
                    "response_time_ms": response_time_ms,
                    "is_error": False
                }
            
            # For complex queries, use GPT if available
            print(f"Attempting GPT response. LLM client available: {self.llm_client is not None}")
            print(f"AI Provider: {self.config.AI_PROVIDER}")
            print(f"AI Enabled: {self.config.is_ai_enabled()}")
            
            if self.llm_client:
                # Build the prompt with context
                prompt = self._build_contextual_prompt(user_message, user_context)
                
                # Generate response using LLM
                ai_response = await self._call_llm(prompt, user_message)
                
                # Calculate metrics
                response_time_ms = int((time.time() - start_time) * 1000)
                
                return {
                    "content": ai_response["content"],
                    "model_used": ai_response.get("model", self.config.get_model_config().get("model")),
                    "tokens_used": ai_response.get("tokens", 0),
                    "response_time_ms": response_time_ms,
                    "is_error": False
                }
            else:
                # Fallback to enhanced rule-based response
                print(f"Using fallback response - no LLM client configured")
                print(f"OpenAI API Key present: {self.config.OPENAI_API_KEY is not None}")
                fallback_response = self._generate_fallback_response(user_message, user_context)
                response_time_ms = int((time.time() - start_time) * 1000)
                
                return {
                    "content": fallback_response,
                    "model_used": "fallback-enhanced",
                    "tokens_used": 0,
                    "response_time_ms": response_time_ms,
                    "is_error": False
                }
            
        except Exception as e:
            return {
                "content": "I apologize, but I'm having trouble processing your request. Please try again.",
                "model_used": None,
                "tokens_used": 0,
                "response_time_ms": int((time.time() - start_time) * 1000),
                "is_error": True,
                "error_message": str(e)
            }
    
    def _build_contextual_prompt(
        self, 
        user_message: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Build a prompt with user context for the LLM"""
        
        # System prompt
        system_prompt = """You are an AI immigration assistant helping users with their immigration questions. 
You have access to the user's immigration profile, status, documents, and history. 
Provide accurate, helpful, and personalized advice based on their specific situation.
Always remind users that you're providing general guidance and they should consult with an immigration attorney for legal advice."""
        
        # Format user context
        context_parts = []
        
        # Current status
        if user_context.get("current_status"):
            status = user_context["current_status"]
            context_parts.append(
                f"Current Status: {status.get('status_name')} ({status.get('status_code')})"
            )
            if status.get("employment_restrictions"):
                context_parts.append(f"Employment Restrictions: {status['employment_restrictions']}")
        
        # Upcoming deadlines
        if user_context.get("upcoming_deadlines"):
            context_parts.append("\nUpcoming Deadlines:")
            for deadline in user_context["upcoming_deadlines"]:
                context_parts.append(
                    f"- {deadline['type']}: {deadline['date']} "
                    f"({deadline['days_until']} days, priority: {deadline['priority']})"
                )
        
        # Recent documents
        if user_context.get("recent_documents"):
            expiring_docs = [
                doc for doc in user_context["recent_documents"] 
                if doc.get("is_expiring_soon")
            ]
            if expiring_docs:
                context_parts.append("\nDocuments Expiring Soon:")
                for doc in expiring_docs:
                    context_parts.append(
                        f"- {doc['document_type']}: expires {doc['expiry_date']}"
                    )
        
        # Employment
        if user_context.get("employment"):
            emp = user_context["employment"]
            context_parts.append(
                f"\nCurrent Employment: {emp.get('job_title')} at {emp.get('employer')} "
                f"(since {emp.get('start_date')})"
            )
        
        # Build the full prompt
        context_string = "\n".join(context_parts) if context_parts else "No specific context available."
        
        full_prompt = f"""{system_prompt}

User Context:
{context_string}

User Question: {user_message}

Please provide a helpful and personalized response based on the user's specific immigration situation."""
        
        return full_prompt
    
    async def _call_llm(self, prompt: str, user_message: str) -> Dict[str, Any]:
        """Call the LLM to generate a response"""
        
        if self.config.AI_PROVIDER == "openai" and self.llm_client:
            try:
                print(f"Making OpenAI API call with model: {self.config.OPENAI_MODEL}")
                response = await self.llm_client.chat.completions.create(
                    model=self.config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.config.OPENAI_TEMPERATURE,
                    max_tokens=self.config.OPENAI_MAX_TOKENS
                )
                
                print(f"OpenAI API call successful. Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")
                return {
                    "content": response.choices[0].message.content,
                    "model": response.model,
                    "tokens": response.usage.total_tokens if response.usage else 0
                }
            except Exception as e:
                print(f"OpenAI API error: {e}")
                print(f"Error type: {type(e).__name__}")
                # Fall back to enhanced rule-based response
                return {
                    "content": self._generate_fallback_response(user_message, {}),
                    "model": "fallback-on-error",
                    "tokens": 0
                }
                
        elif self.config.AI_PROVIDER == "anthropic" and self.llm_client:
            try:
                response = await self.llm_client.messages.create(
                    model=self.config.ANTHROPIC_MODEL,
                    max_tokens=1000,
                    temperature=0.7,
                    system=self._get_system_prompt(),
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                return {
                    "content": response.content[0].text,
                    "model": response.model,
                    "tokens": response.usage.input_tokens + response.usage.output_tokens
                }
            except Exception as e:
                print(f"Anthropic API error: {e}")
                # Fall back to enhanced rule-based response
                return {
                    "content": self._generate_fallback_response(user_message, {}),
                    "model": "fallback-on-error",
                    "tokens": 0
                }
        
        # If no LLM is configured, use fallback
        return {
            "content": self._generate_fallback_response(user_message, {}),
            "model": "fallback-no-llm",
            "tokens": 0
        }
    
    def _initialize_rule_patterns(self) -> List[Tuple[re.Pattern, str]]:
        """Initialize rule-based patterns for common H1-B questions"""
        patterns = [
            # H1-B specific patterns
            (re.compile(r'(?i)(h1[\s-]?b|h-1b).*(renew|extend|extension)', re.IGNORECASE), 'h1b_renewal'),
            (re.compile(r'(?i)(h1[\s-]?b|h-1b).*(transfer|change.*employer)', re.IGNORECASE), 'h1b_transfer'),
            (re.compile(r'(?i)(h1[\s-]?b|h-1b).*(amend|amendment)', re.IGNORECASE), 'h1b_amendment'),
            
            # Travel patterns
            (re.compile(r'(?i)(travel|trip|leave.*country|go.*abroad)', re.IGNORECASE), 'travel'),
            (re.compile(r'(?i)(re[\s-]?entry|return.*us|come.*back)', re.IGNORECASE), 'reentry'),
            
            # Document patterns
            (re.compile(r'(?i)(document|paper|form).*(need|require|checklist)', re.IGNORECASE), 'document_checklist'),
            (re.compile(r'(?i)(i[\s-]?94|i94)', re.IGNORECASE), 'i94'),
            (re.compile(r'(?i)(i[\s-]?797|i797)', re.IGNORECASE), 'i797'),
            
            # Employment patterns
            (re.compile(r'(?i)(work|employ).*(authorization|permit|ead)', re.IGNORECASE), 'work_auth'),
            (re.compile(r'(?i)(change.*job|new.*job|switch.*employer)', re.IGNORECASE), 'job_change'),
            
            # Green card patterns
            (re.compile(r'(?i)(green.*card|permanent.*resident|eb[\s-]?[123])', re.IGNORECASE), 'green_card'),
            (re.compile(r'(?i)(perm|labor.*certification)', re.IGNORECASE), 'perm'),
            
            # Status/deadline patterns
            (re.compile(r'(?i)(status|expire|expir|deadline)', re.IGNORECASE), 'status_check'),
            (re.compile(r'(?i)(grace.*period|out.*of.*status)', re.IGNORECASE), 'grace_period'),
        ]
        return patterns
    
    def _check_rule_based_response(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """Check if message matches rule-based patterns and return appropriate response"""
        for pattern, response_type in self.rule_patterns:
            if pattern.search(message):
                return self._get_rule_response(response_type, context)
        return None
    
    def _get_rule_response(self, response_type: str, context: Dict[str, Any]) -> str:
        """Get rule-based response for specific type with context"""
        responses = {
            'h1b_renewal': self._h1b_renewal_response,
            'h1b_transfer': self._h1b_transfer_response,
            'h1b_amendment': self._h1b_amendment_response,
            'travel': self._travel_response,
            'reentry': self._reentry_response,
            'document_checklist': self._document_checklist_response,
            'i94': self._i94_response,
            'i797': self._i797_response,
            'work_auth': self._work_auth_response,
            'job_change': self._job_change_response,
            'green_card': self._green_card_response,
            'perm': self._perm_response,
            'status_check': self._status_check_response,
            'grace_period': self._grace_period_response,
        }
        
        response_func = responses.get(response_type, self._default_response)
        return response_func(context)
    
    def _h1b_renewal_response(self, context: Dict[str, Any]) -> str:
        """Generate H1-B renewal response"""
        deadlines = context.get('upcoming_deadlines', [])
        visa_deadline = next((d for d in deadlines if d['type'] == 'visa_expiry'), None)
        
        response = "Based on your H1-B status, here's what you need to know about renewal:\n\n"
        
        if visa_deadline:
            response += f"⚠️ Your H1-B expires in {visa_deadline['days_until']} days ({visa_deadline['date']})\n\n"
        
        response += """**H1-B Renewal Checklist:**
• Valid passport (6+ months validity)
• Current I-94 record
• Employment verification letter
• Recent pay stubs (last 3-6 months)
• Form I-797 approval notice
• Previous H1-B approvals
• LCA (Labor Condition Application)

**Timeline:** Start the process 6 months before expiry
**Processing:** Regular (4-6 months) or Premium (15 days)

💡 *Tip: You can continue working for 240 days after filing if your employer files before expiry.*

Would you like me to create a personalized timeline for your renewal?"""
        
        return response
    
    def _travel_response(self, context: Dict[str, Any]) -> str:
        """Generate travel guidance response"""
        status = context.get('current_status', {})
        recent_travel = context.get('travel_history', [])
        
        response = "Here's what you need to know about international travel:\n\n"
        
        if status.get('status_code') == 'H1B':
            response += """**For H1-B holders:**
• Valid H1-B visa stamp required for re-entry
• Carry employment letter and recent pay stubs
• Have copy of approved I-797
• Check visa expiry before travel

**Important:** If your visa stamp is expired, you'll need to get it renewed at a US consulate abroad."""
        
        if recent_travel:
            response += f"\n\nI see you've traveled {len(recent_travel)} times in the last 6 months. "
            response += "Make sure to maintain records of all entries/exits."
        
        response += "\n\nNeed help with visa stamping or travel documents?"
        
        return response
    
    def _status_check_response(self, context: Dict[str, Any]) -> str:
        """Generate status check response"""
        profile = context.get('profile', {})
        status = context.get('current_status', {})
        deadlines = context.get('upcoming_deadlines', [])
        
        response = f"**Your Current Immigration Status:**\n"
        
        if status:
            response += f"• Status: {status.get('status_name', 'Unknown')} ({status.get('status_code', 'N/A')})\n"
        
        if profile.get('authorized_stay_until'):
            response += f"• I-94 Expiry: {profile['authorized_stay_until']}\n"
        
        if deadlines:
            response += f"\n**Upcoming Deadlines ({len(deadlines)}):**\n"
            for deadline in deadlines[:3]:  # Show top 3
                emoji = "🔴" if deadline['priority'] == 'critical' else "🟡" if deadline['priority'] == 'high' else "🟢"
                response += f"{emoji} {deadline['type'].replace('_', ' ').title()}: {deadline['days_until']} days\n"
        
        response += "\n*Remember: Always maintain legal status and act before deadlines!*"
        
        return response
    
    def _generate_fallback_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate enhanced fallback response when LLM is not available"""
        # Check for urgent keywords
        urgent_keywords = ['urgent', 'emergency', 'expire', 'deadline', 'overstay', 'out of status']
        is_urgent = any(keyword in message.lower() for keyword in urgent_keywords)
        
        if is_urgent:
            return """I understand this may be an urgent matter. While I can't provide specific legal advice, here's what I recommend:

1. **Document everything** - Keep records of your current status and any deadlines
2. **Contact an immigration attorney** immediately if you're facing urgent deadlines
3. **Don't let your status expire** - File extensions/renewals before expiry

For immediate assistance:
• USCIS Contact Center: 1-800-375-5283
• Find an attorney: aila.org (American Immigration Lawyers Association)

What specific deadline or issue are you concerned about?"""
        
        # Default helpful response
        return """I'm here to help with your immigration questions. I can assist with:

• H1-B renewals, transfers, and amendments
• Travel and re-entry requirements
• Document checklists and deadlines
• Employment authorization questions
• Green card process information
• Status checks and timeline tracking

What specific topic would you like to explore?"""
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM"""
        return """You are an expert immigration assistant specializing in US immigration law, particularly H1-B visas. 
You provide accurate, helpful, and personalized guidance based on users' specific situations.

Important guidelines:
1. Always remind users you provide general guidance, not legal advice
2. Be specific and actionable in your responses
3. Reference the user's specific context when available
4. Highlight urgent deadlines or critical issues
5. Suggest next steps and offer to help with specific tasks
6. Be empathetic and understanding of immigration challenges

Never:
- Provide specific legal advice
- Guarantee any immigration outcomes
- Share other users' information
- Make assumptions about undocumented status"""
    
    # Additional response methods for other patterns
    def _h1b_transfer_response(self, context: Dict[str, Any]) -> str:
        return """**H1-B Transfer Process:**

You can change employers on H1-B. Here's what you need to know:

• You can start working for the new employer once they file the petition
• No need to wait for approval (portability rule)
• Your new employer must file a new H1-B petition

**Required from you:**
• Recent pay stubs (last 3)
• Current I-797 approval
• Resume/CV
• Passport and visa copies

**Timeline:** 4-6 months regular, 15 days premium

Would you like help understanding the transfer timeline?"""
    
    def _default_response(self, context: Dict[str, Any]) -> str:
        return self._generate_fallback_response("", context)
    
    # Implement other response methods similarly...
    def _h1b_amendment_response(self, context: Dict[str, Any]) -> str:
        return "H1-B amendments are required for material changes. Let me explain when you need one..."
    
    def _reentry_response(self, context: Dict[str, Any]) -> str:
        return "For re-entering the US, you'll need valid visa stamp and supporting documents..."
    
    def _document_checklist_response(self, context: Dict[str, Any]) -> str:
        return "Here's a comprehensive document checklist based on your needs..."
    
    def _i94_response(self, context: Dict[str, Any]) -> str:
        return "Your I-94 is your official arrival/departure record. You can access it online..."
    
    def _i797_response(self, context: Dict[str, Any]) -> str:
        return "Form I-797 is your approval notice. Keep it safe as it's crucial for your status..."
    
    def _work_auth_response(self, context: Dict[str, Any]) -> str:
        return "Your work authorization depends on your current status. Let me explain..."
    
    def _job_change_response(self, context: Dict[str, Any]) -> str:
        return self._h1b_transfer_response(context)  # Job change is same as H1-B transfer
    
    def _green_card_response(self, context: Dict[str, Any]) -> str:
        return "There are several paths to a green card from H1-B. Let me explain your options..."
    
    def _perm_response(self, context: Dict[str, Any]) -> str:
        return "PERM is the first step in employment-based green card process..."
    
    def _grace_period_response(self, context: Dict[str, Any]) -> str:
        return "H1-B holders have a 60-day grace period. Here's what you need to know..."