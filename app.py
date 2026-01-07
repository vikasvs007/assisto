"""
Policy Document Q&A Assistant
A safe, compliant system for explaining insurance policy clauses in simple language.

Author: Candidate for Assisto Company Assessment
Date: January 2026
"""

import os
import sys
from typing import Optional, Dict
from pathlib import Path
from dotenv import load_dotenv


class PolicyQAAssistant:
    """
    Insurance Policy Q&A Assistant that explains policy clauses in simple language.
    
    Features:
    - Loads policy documents from file or text input
    - Answers questions using LLM (with mock fallback)
    - Ensures safety and compliance (no legal advice)
    - Always includes disclaimer
    """
    
    def __init__(self, policy_path: Optional[str] = None, use_mock: bool = False):
        """
        Initialize the Policy Q&A Assistant.
        
        Args:
            policy_path: Path to the policy document file
            use_mock: Force mock mode even if API key is available
        """
        self.policy_text = ""
        self.prompt_template = ""
        self.use_mock = use_mock
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        # Load prompt template
        self.load_prompt_template()
        
        # Load policy if path provided
        if policy_path:
            self.load_policy(policy_path)
    
    def load_prompt_template(self) -> None:
        """Load the prompt template from file."""
        try:
            prompt_path = Path(__file__).parent / "prompts" / "policy_qa_prompt.txt"
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
            print("✓ Prompt template loaded successfully")
        except FileNotFoundError:
            print("⚠ Warning: Prompt template not found. Using default template.")
            self.prompt_template = self._get_default_prompt_template()
    
    def load_policy(self, policy_path: str) -> None:
        """
        Load policy document from file.
        
        Args:
            policy_path: Path to the policy document
        """
        try:
            with open(policy_path, 'r', encoding='utf-8') as f:
                self.policy_text = f.read()
            print(f"✓ Policy document loaded: {len(self.policy_text)} characters")
        except FileNotFoundError:
            print(f"✗ Error: Policy file not found: {policy_path}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error loading policy: {str(e)}")
            sys.exit(1)
    
    def set_policy_text(self, policy_text: str) -> None:
        """
        Set policy text directly (alternative to loading from file).
        
        Args:
            policy_text: The policy document text
        """
        self.policy_text = policy_text
        print(f"✓ Policy text set: {len(self.policy_text)} characters")
    
    def find_relevant_section(self, question: str) -> str:
        """
        Find the most relevant section of the policy for the question.
        For better accuracy, we send the full policy to Gemini.
        
        Args:
            question: User's question
            
        Returns:
            Full policy text for comprehensive context
        """
        if not self.policy_text:
            return ""
        
        # Send full policy for best accuracy
        # Gemini can handle the full context and find relevant parts
        return self.policy_text
    
    def ask_question(self, question: str) -> str:
        """
        Answer a question about the policy.
        
        Args:
            question: User's question about the policy
            
        Returns:
            Answer with explanation and disclaimer
        """
        # Validation
        if not question or len(question.strip()) == 0:
            return "Please provide a valid question."
        
        if not self.policy_text:
            return "No policy document loaded. Please load a policy first."
        
        if len(question) > 500:
            return "Question is too long. Please keep questions under 500 characters."
        
        # Find relevant section
        relevant_section = self.find_relevant_section(question)
        
        # Determine if we should use mock or real LLM
        if self.use_mock or not self.api_key:
            return self._get_mock_response(question, relevant_section)
        else:
            return self._get_llm_response(question, relevant_section)
    
    def _get_llm_response(self, question: str, relevant_section: str) -> str:
        """
        Get response from Google Gemini API.
        
        Args:
            question: User's question
            relevant_section: Relevant policy section
            
        Returns:
            LLM-generated response
        """
        try:
            import google.generativeai as genai
            
            # Configure Gemini API
            genai.configure(api_key=self.api_key)
            
            # Initialize the model with confirmed available model
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Format the prompt
            prompt = self.prompt_template.format(
                policy_text=relevant_section,
                question=question
            )
            
            # Call Gemini API
            response = model.generate_content(prompt)
            
            answer = response.text.strip()
            
            # Ensure disclaimer is present
            return self.format_response(answer)
            
        except ImportError:
            print("⚠ Google Gemini library not installed. Falling back to mock mode.")
            return self._get_mock_response(question, relevant_section)
        except Exception as e:
            print(f"⚠ Error calling Gemini API: {str(e)}. Falling back to mock mode.")
            return self._get_mock_response(question, relevant_section)
    
    def _get_mock_response(self, question: str, relevant_section: str) -> str:
        """
        Generate a mock response for testing without API key.
        
        Args:
            question: User's question
            relevant_section: Relevant policy section
            
        Returns:
            Mock response demonstrating expected behavior
        """
        question_lower = question.lower()
        
        # Mock responses for common questions
        mock_responses = {
            'negligence': """Negligence means failing to take proper care to avoid causing harm or damage. In simple terms, it's when someone is careless or doesn't do what a reasonable person would do to prevent problems.

For example, if you know your roof is leaking but don't fix it for months, and water damage gets worse, that could be considered negligence. The insurance may not cover the additional damage because you didn't take reasonable steps to prevent it.

Another example: leaving your doors and windows unlocked when you go on vacation, and then experiencing a theft. This might be seen as negligent because you didn't take basic security precautions.

This is not legal advice.""",
            
            'deductible': """A deductible is the amount of money you have to pay out of your own pocket before the insurance company starts paying for a covered claim.

For example, if your policy has a $1,000 deductible and you have $5,000 in covered damage:
- You pay the first $1,000
- The insurance company pays the remaining $4,000

Think of it like a threshold - you handle smaller costs yourself, and insurance kicks in for larger expenses. Generally, policies with higher deductibles have lower monthly premiums, and vice versa.

This is not legal advice.""",
            
            'coverage': """This policy covers damages to your property from several specific events, including:
- Fire and smoke damage
- Water damage from burst pipes
- Theft and burglary
- Natural disasters like storms and lightning
- Accidental damage

For example, if a pipe bursts in your home and causes water damage, this would typically be covered. Or if there's a fire in your kitchen, the policy would help pay for repairs.

However, not everything is covered - there are exclusions like intentional damage, negligence, and normal wear and tear. The maximum coverage amount is $500,000 for the property.

This is not legal advice.""",
            
            'claim': """To file a claim, you need to follow these steps:

1. Report the damage within 48 hours of discovering it
2. Call the claims department at 1-800-CLAIMS-1
3. Have your policy number ready
4. Take photos of the damage if possible
5. Don't throw away damaged items until they've been inspected

For example, if you come home and find your house was broken into, you should:
- Call the police first
- Take photos of the damage
- Make a list of stolen items
- Call the insurance claims line within 48 hours
- Keep all receipts and documentation

The insurance company will investigate and, if approved, settle the claim within 30 days.

This is not legal advice.""",
            
            'cancel': """You can cancel your insurance policy at any time by providing 30 days written notice to the insurance company.

The insurance company can also cancel your policy for specific reasons:
- If you don't pay your premiums (you have a 30-day grace period)
- If you committed fraud or lied on your application
- If the risk has substantially increased

For example, if you stop paying your monthly premium, the insurance company will give you 30 days to catch up. If you don't pay within that time, they can cancel your coverage.

If you want to cancel, you should send a written letter or email stating that you want to cancel, include your policy number, and specify the cancellation date (at least 30 days from when you notify them).

This is not legal advice.""",
        }
        
        # Find matching mock response
        for keyword, response in mock_responses.items():
            if keyword in question_lower:
                return f"[MOCK MODE - No API Key Detected]\n\n{response}"
        
        # Default mock response
        default_response = """Based on the policy document, I can help explain the relevant sections to you. However, I need to see the specific policy language to give you an accurate answer.

The policy document contains information about:
- What is covered and what is excluded
- How to file claims
- Deductibles and coverage limits
- Policy terms and conditions

Could you please rephrase your question or ask about a specific aspect of the policy, such as coverage, exclusions, claims process, or deductibles?

This is not legal advice."""
        
        return f"[MOCK MODE - No API Key Detected]\n\n{default_response}"
    
    def format_response(self, response: str) -> str:
        """
        Ensure response includes disclaimer.
        
        Args:
            response: The response text
            
        Returns:
            Formatted response with disclaimer
        """
        disclaimer = "This is not legal advice."
        
        # Check if disclaimer already exists
        if disclaimer.lower() not in response.lower():
            response = f"{response}\n\n{disclaimer}"
        
        return response
    
    def _get_default_prompt_template(self) -> str:
        """Return default prompt template if file not found."""
        return """You are an insurance policy assistant.

Explain the policy content in simple, clear English.
Avoid legal jargon.
Use examples to help understanding.
Do not give legal advice.

Policy Document:
{policy_text}

User Question:
{question}

Answer clearly and concisely.
End with: "This is not legal advice."
"""


def main():
    """Main CLI interface for the Policy Q&A Assistant."""
    # Load environment variables from .env file
    load_dotenv()
    
    print("=" * 70)
    print("POLICY DOCUMENT Q&A ASSISTANT")
    print("Assisto Company Assessment - January 2026")
    print("=" * 70)
    print()
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✓ Google Gemini API key detected - Using real LLM")
        use_mock = False
    else:
        print("⚠ No Gemini API key found - Using mock mode")
        print("  (Set GEMINI_API_KEY environment variable to use real LLM)")
        use_mock = True
    
    print()
    
    # Load sample policy
    sample_policy_path = Path(__file__).parent / "data" / "sample_policy.txt"
    
    if not sample_policy_path.exists():
        print(f"✗ Error: Sample policy not found at {sample_policy_path}")
        print("Please ensure the data/sample_policy.txt file exists.")
        sys.exit(1)
    
    # Initialize assistant
    assistant = PolicyQAAssistant(str(sample_policy_path), use_mock=use_mock)
    
    print()
    print("=" * 70)
    print("INTERACTIVE Q&A SESSION")
    print("=" * 70)
    print("Ask questions about the insurance policy.")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 70)
    print()
    
    # Interactive loop
    while True:
        try:
            question = input("\n📝 Your Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using the Policy Q&A Assistant!")
                break
            
            if not question:
                continue
            
            print("\n" + "=" * 70)
            print("💡 ANSWER")
            print("=" * 70)
            print()
            answer = assistant.ask_question(question)
            
            # Format the answer with better spacing
            lines = answer.split('\n')
            for line in lines:
                print(line)
            
            print()
            print("=" * 70)
            
        except KeyboardInterrupt:
            print("\n\nSession ended by user.")
            break
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")


if __name__ == "__main__":
    main()
