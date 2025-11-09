"""
MOODI Integration Workflow
Complete end-to-end flow with gamification logic
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from openai import OpenAI

# Import the reflection API
from moodi_reflection_api import generate_mood_reflection, validate_response

# Initialize OpenAI client
client = OpenAI()


# ============================================================================
# Safety & Moderation
# ============================================================================

def check_content_safety(text: str) -> Dict[str, Any]:
    """
    Check content for safety issues using OpenAI Moderation API
    
    Returns:
        Dictionary with 'flagged' boolean and 'categories' dict
    """
    try:
        response = client.moderations.create(input=text)
        result = response.results[0]
        
        return {
            "flagged": result.flagged,
            "categories": result.categories.model_dump(),
            "category_scores": result.category_scores.model_dump()
        }
    except Exception as e:
        print(f"Moderation check failed: {e}")
        return {"flagged": False, "categories": {}}


def classify_safety_risk(context_text: str) -> str:
    """
    Optional secondary classifier for safety escalation
    
    Returns:
        'ok' or 'elevate'
    """
    if not context_text or len(context_text.strip()) == 0:
        return 'ok'
    
    system_prompt = """You classify mood texts for safety escalation.
If self-harm intent or severe distress is implied, return: {"safety_flag":"elevate"}
Else return: {"safety_flag":"ok"}
Only output valid JSON with key safety_flag."""
    
    user_prompt = f'Text: """{context_text}"""'
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("safety_flag", "ok")
        
    except Exception as e:
        print(f"Safety classification failed: {e}")
        return "ok"


# ============================================================================
# Gamification Logic
# ============================================================================

class GamificationEngine:
    """Handles MoodCoins, streaks, and unlocks"""
    
    # Coin rewards
    DAILY_POST_COINS = 5
    STREAK_BONUS_COINS = 5
    STREAK_BONUS_INTERVAL = 3  # Every 3 days
    REFERRAL_COINS = 25
    
    # Unlock thresholds
    UNLOCK_CUSTOM_GRADIENT = 50
    UNLOCK_VOICE_REFLECTION = 120
    
    @staticmethod
    def calculate_streak(last_mood_date: Optional[date], current_date: date) -> int:
        """
        Calculate streak based on last mood date
        
        Args:
            last_mood_date: Date of last mood post (None if first post)
            current_date: Current date
            
        Returns:
            New streak count
        """
        if last_mood_date is None:
            # First mood ever
            return 1
        
        days_diff = (current_date - last_mood_date).days
        
        if days_diff == 0:
            # Same day, no change (return current streak, handled by caller)
            return 0  # Indicates no change
        elif days_diff == 1:
            # Consecutive day, increment
            return 1  # Indicates increment
        else:
            # Streak broken, reset
            return -1  # Indicates reset to 1
    
    @staticmethod
    def award_daily_coins(user_data: Dict, is_new_day: bool) -> int:
        """
        Award coins for daily post
        
        Returns:
            Coins awarded
        """
        if is_new_day:
            return GamificationEngine.DAILY_POST_COINS
        return 0
    
    @staticmethod
    def award_streak_bonus(streak_days: int, old_streak: int) -> int:
        """
        Award bonus coins for streak milestones
        
        Returns:
            Bonus coins awarded
        """
        # Check if we just hit a multiple of 3
        if streak_days > old_streak and streak_days % GamificationEngine.STREAK_BONUS_INTERVAL == 0:
            return GamificationEngine.STREAK_BONUS_COINS
        return 0
    
    @staticmethod
    def check_unlocks(total_coins: int) -> list:
        """
        Check which features should be unlocked
        
        Returns:
            List of unlock types
        """
        unlocks = []
        
        if total_coins >= GamificationEngine.UNLOCK_CUSTOM_GRADIENT:
            unlocks.append("custom_gradient")
        
        if total_coins >= GamificationEngine.UNLOCK_VOICE_REFLECTION:
            unlocks.append("voice_reflection")
        
        return unlocks


# ============================================================================
# Notification Generator
# ============================================================================

def generate_notification(user_locale: str, theme: str, days_streak: int = 0) -> Dict[str, str]:
    """
    Generate push notification copy
    
    Args:
        user_locale: Language/locale code
        theme: Type of notification (gentle_reminder, streak_nudge, evening_checkin, milestone)
        days_streak: Current streak count
        
    Returns:
        Dictionary with 'title' and 'body'
    """
    system_prompt = """You write ultra-short, empathetic push notifications and microcopies for mood journaling apps.
Rules: ≤ 80 characters, friendly, zero guilt. Match `user_locale`.
Output JSON: {"title": "...", "body": "..."} with both ≤ 80 chars."""
    
    user_prompt = f"""user_locale="{user_locale}"
theme="{theme}"
days_streak={days_streak}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Notification generation failed: {e}")
        return {"title": "MOODI", "body": "How are you feeling today?"}


# ============================================================================
# Referral Caption Generator
# ============================================================================

def generate_referral_caption(user_locale: str, mood_emoji: str, benefit: str) -> str:
    """
    Generate social share caption for referrals
    
    Returns:
        Caption string
    """
    system_prompt = """Write a catchy share caption for social. ≤ 12 words. Match locale.
Return JSON: {"caption":"..."} Only."""
    
    user_prompt = f"""user_locale="{user_locale}"
mood_emoji="{mood_emoji}"
benefit="{benefit}" """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.8,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("caption", "Check out MOODI!")
        
    except Exception as e:
        print(f"Caption generation failed: {e}")
        return "Check out MOODI!"


# ============================================================================
# Complete Integration Workflow
# ============================================================================

def process_mood_submission(mood_payload: Dict, user_data: Dict) -> Dict[str, Any]:
    """
    Complete end-to-end mood processing workflow
    
    Args:
        mood_payload: Mood data from user
        user_data: Current user profile data (streak_days, moodcoins, last_mood_date, etc.)
        
    Returns:
        Complete result with reflection, coins awarded, streak updates, etc.
    """
    result = {
        "success": False,
        "reflection": None,
        "safety_check": None,
        "coins_awarded": 0,
        "streak_updated": False,
        "new_streak": user_data.get("streak_days", 0),
        "new_coin_total": user_data.get("moodcoins", 0),
        "unlocks": [],
        "errors": []
    }
    
    try:
        # Step 1: Pre-check with OpenAI Moderation
        context_text = mood_payload.get("context_text", "")
        if context_text:
            moderation = check_content_safety(context_text)
            result["safety_check"] = moderation
            
            if moderation["flagged"]:
                # Optional: Run secondary classifier
                safety_flag = classify_safety_risk(context_text)
                result["safety_flag"] = safety_flag
                
                if safety_flag == "elevate":
                    result["errors"].append("Safety concern detected - escalation required")
        
        # Step 2: Generate AI Reflection
        reflection = generate_mood_reflection(mood_payload)
        
        # Validate reflection
        is_valid, errors = validate_response(reflection)
        if not is_valid:
            result["errors"].extend(errors)
            return result
        
        result["reflection"] = reflection
        
        # Step 3: Update Streak
        current_date = date.today()
        last_mood_date = user_data.get("last_mood_date")
        current_streak = user_data.get("streak_days", 0)
        
        if last_mood_date:
            last_mood_date = date.fromisoformat(last_mood_date) if isinstance(last_mood_date, str) else last_mood_date
        
        is_new_day = last_mood_date is None or last_mood_date < current_date
        
        streak_change = GamificationEngine.calculate_streak(last_mood_date, current_date)
        
        if streak_change == 1:
            # Increment streak
            result["new_streak"] = current_streak + 1
            result["streak_updated"] = True
        elif streak_change == -1:
            # Reset streak
            result["new_streak"] = 1
            result["streak_updated"] = True
        elif streak_change == 0 and last_mood_date is None:
            # First post ever
            result["new_streak"] = 1
            result["streak_updated"] = True
        else:
            # Same day, no change
            result["new_streak"] = current_streak
        
        # Step 4: Award Coins
        # Daily post coins
        daily_coins = GamificationEngine.award_daily_coins(user_data, is_new_day)
        result["coins_awarded"] += daily_coins
        
        # Streak bonus coins
        streak_bonus = GamificationEngine.award_streak_bonus(result["new_streak"], current_streak)
        result["coins_awarded"] += streak_bonus
        
        result["new_coin_total"] = user_data.get("moodcoins", 0) + result["coins_awarded"]
        
        # Step 5: Check Unlocks
        result["unlocks"] = GamificationEngine.check_unlocks(result["new_coin_total"])
        
        result["success"] = True
        
    except Exception as e:
        result["errors"].append(f"Processing error: {str(e)}")
    
    return result


# ============================================================================
# Testing & Examples
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("MOODI Complete Integration Workflow Test")
    print("=" * 80)
    print()
    
    # Simulate user data
    user_data = {
        "user_id": "test-user-123",
        "streak_days": 2,
        "moodcoins": 45,
        "last_mood_date": str(date.today() - timedelta(days=1)),  # Yesterday
        "locale": "fr"
    }
    
    # Test mood payload
    mood_payload = {
        "mood_emoji": "😌",
        "mood_color": "#7FD1AE",
        "intensity_0_10": 4,
        "context_text": "petite promenade au bord de mer",
        "media_present": True,
        "time_bucket": "evening",
        "geo_hint": "Casablanca",
        "user_locale": "fr",
        "user_age_bucket": "adult"
    }
    
    print("User Data:")
    print(json.dumps(user_data, indent=2))
    print()
    
    print("Mood Payload:")
    print(json.dumps(mood_payload, indent=2, ensure_ascii=False))
    print()
    
    print("-" * 80)
    print("Processing mood submission...")
    print("-" * 80)
    print()
    
    # Process the mood
    result = process_mood_submission(mood_payload, user_data)
    
    print("Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    print()
    
    # Test notification generation
    print("-" * 80)
    print("Testing notification generation...")
    print("-" * 80)
    print()
    
    notification = generate_notification("fr", "streak_nudge", result["new_streak"])
    print(f"Notification: {json.dumps(notification, indent=2, ensure_ascii=False)}")
    print()
    
    # Test referral caption
    print("-" * 80)
    print("Testing referral caption generation...")
    print("-" * 80)
    print()
    
    caption = generate_referral_caption("fr", "😌", "Track your mood, get a tiny AI nudge")
    print(f"Referral Caption: {caption}")
    print()
    
    print("=" * 80)
    print("Integration test complete!")
    print("=" * 80)
