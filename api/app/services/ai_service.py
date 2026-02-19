import logging
import os
from openai import OpenAI
from ..config import Config
from ..utils.constants import ALLOWED_CATEGORIES, FALLBACK_CATEGORY

def classify_task(description):
    """
    Classifies the task description using an LLM (mocked or real).
    """
    try:
        api_key = Config.OPENAI_API_KEY
        
        if not api_key:
            logging.info("No OPENAI_API_KEY found. Using mock classification.")
            # Simple mock logic for demonstration/testing locally without key
            desc_upper = description.upper()
            if "BUY" in desc_upper or "PAY" in desc_upper:
                result = "FINANCE"
            elif "GYM" in desc_upper or "DOCTOR" in desc_upper:
                result = "HEALTH"
            elif "MEETING" in desc_upper or "CODE" in desc_upper:
                result = "WORK"
            else:
                result = "PERSONAL"
        else:
            # Real AI classification using OpenAI API
            logging.info("Calling OpenAI API for task classification.")
            client = OpenAI(api_key=api_key)
            
            prompt = (
                "You are a strict classifier. Classify the following task into one of "
                "these categories: WORK, PERSONAL, FINANCE, HEALTH, OTHER.\n"
                "Return ONLY the category name. Do not explain.\n"
                f"Task: \"{description}\""
            )
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0, # low temp for deterministic classification
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
        
        # Validation
        if result not in ALLOWED_CATEGORIES:
            logging.warning(f"AI returned invalid category '{result}', falling back to {FALLBACK_CATEGORY}")
            return FALLBACK_CATEGORY
            
        logging.info(f"Task classified as {result}")
        return result

    except Exception as e:
        logging.error(f"AI Service Failure: {str(e)}")
        return FALLBACK_CATEGORY
