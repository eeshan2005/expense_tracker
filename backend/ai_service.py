import openai
from typing import List, Dict, Any

# Set your OpenAI API key here
# openai.api_key = "your-api-key"


def categorize_expense(note: str) -> str:
    """Use AI to categorize an expense based on the note"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that categorizes expenses."},
                {"role": "user", "content": f"Categorize this expense: {note}. Respond with only one of these categories: Food, Transport, Housing, Utilities, Entertainment, Shopping, Health, Education, Travel, Other."}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in AI categorization: {e}")
        # Fallback to rule-based categorization
        return rule_based_categorization(note)


def rule_based_categorization(note: str) -> str:
    """Simple rule-based categorization as a fallback"""
    note = note.lower()
    if any(word in note for word in ["food", "restaurant", "meal", "lunch", "dinner", "breakfast", "cafe", "coffee"]):
        return "Food"
    elif any(word in note for word in ["transport", "uber", "taxi", "bus", "train", "gas", "fuel", "car"]):
        return "Transport"
    elif any(word in note for word in ["rent", "house", "apartment", "mortgage"]):
        return "Housing"
    elif any(word in note for word in ["electricity", "water", "internet", "phone", "bill"]):
        return "Utilities"
    elif any(word in note for word in ["movie", "game", "concert", "show", "theater", "netflix", "spotify"]):
        return "Entertainment"
    elif any(word in note for word in ["clothes", "shoes", "mall", "amazon", "online", "purchase"]):
        return "Shopping"
    elif any(word in note for word in ["doctor", "medicine", "hospital", "health", "medical", "pharmacy"]):
        return "Health"
    elif any(word in note for word in ["school", "college", "university", "course", "class", "book", "tuition"]):
        return "Education"
    elif any(word in note for word in ["hotel", "flight", "vacation", "trip", "travel", "airbnb"]):
        return "Travel"
    else:
        return "Other"


def suggest_budget(expenses: List[Dict[str, Any]]) -> Dict[str, float]:
    """Suggest budgets based on spending habits"""
    # Group expenses by category
    category_totals = {}
    for expense in expenses:
        category = expense.get("category", "Other")
        amount = expense.get("amount", 0)
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    # Suggest budgets (20% higher than current spending)
    budget_suggestions = {}
    for category, amount in category_totals.items():
        budget_suggestions[category] = amount * 1.2
    
    return budget_suggestions


def get_savings_tips(expenses: List[Dict[str, Any]]) -> List[str]:
    """Generate personalized savings tips based on spending patterns"""
    try:
        # Analyze spending patterns
        category_totals = {}
        for expense in expenses:
            category = expense.get("category", "Other")
            amount = expense.get("amount", 0)
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount
        
        # Find the top spending categories
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        top_categories = sorted_categories[:3] if len(sorted_categories) >= 3 else sorted_categories
        
        # Generate tips based on top spending categories
        prompt = "Based on my spending, here are my top expense categories:\n"
        for category, amount in top_categories:
            prompt += f"- {category}: ${amount:.2f}\n"
        prompt += "\nGive me 5 specific and actionable tips to save money based on these spending patterns. Be concise."
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful financial advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        
        # Parse the response to get individual tips
        tips_text = response.choices[0].message.content.strip()
        tips = [tip.strip() for tip in tips_text.split("\n") if tip.strip()]
        
        # Filter out any non-tip lines (like numbering or headers)
        filtered_tips = []
        for tip in tips:
            # Remove numbering if present
            if tip.startswith("1." or "2." or "3." or "4." or "5."):
                tip = tip[2:].strip()
            if tip.startswith("-"):
                tip = tip[1:].strip()
            if tip:
                filtered_tips.append(tip)
        
        return filtered_tips[:5]  # Return at most 5 tips
    
    except Exception as e:
        print(f"Error generating savings tips: {e}")
        # Fallback to generic tips
        return [
            "Consider making coffee at home instead of buying it",
            "Look for sales and discounts when shopping",
            "Use public transportation instead of taxis when possible",
            "Cook meals at home instead of eating out",
            "Cancel unused subscriptions"
        ]


def extract_text_from_receipt(image_path: str) -> Dict[str, Any]:
    """Extract information from a receipt image using OCR"""
    try:
        import pytesseract
        from PIL import Image
        
        # Extract text from image
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        
        # Use AI to parse the receipt text
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts information from receipts."},
                {"role": "user", "content": f"Extract the total amount, date, and merchant name from this receipt text:\n\n{text}\n\nRespond in JSON format with keys 'amount', 'date', and 'merchant'."}
            ],
            max_tokens=100
        )
        
        # Parse the response
        import json
        result = json.loads(response.choices[0].message.content.strip())
        
        # Add a suggested category
        merchant = result.get("merchant", "")
        result["category"] = categorize_expense(merchant)
        
        return result
    
    except Exception as e:
        print(f"Error extracting text from receipt: {e}")
        return {"error": str(e)}