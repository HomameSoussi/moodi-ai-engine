-- MOODI Database Schema
-- Supabase PostgreSQL Migration
-- Execute this in your Supabase SQL Editor

-- ============================================================================
-- Table: users
-- Stores user profile, streak, and gamification data
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  locale TEXT NOT NULL DEFAULT 'fr',
  display_name TEXT,
  streak_days INT NOT NULL DEFAULT 0,
  moodcoins INT NOT NULL DEFAULT 0,
  last_mood_date DATE -- Track last mood post for streak calculation
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at);

-- ============================================================================
-- Table: moods
-- Stores individual mood entries from users
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.moods (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  mood_emoji TEXT NOT NULL,
  mood_color TEXT NOT NULL,
  intensity_0_10 INT CHECK (intensity_0_10 BETWEEN 0 AND 10),
  context_text TEXT,
  media_present BOOLEAN NOT NULL DEFAULT FALSE,
  time_bucket TEXT, -- morning, afternoon, evening, late-night
  geo_hint TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_moods_user_id ON public.moods(user_id);
CREATE INDEX IF NOT EXISTS idx_moods_created_at ON public.moods(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_moods_user_created ON public.moods(user_id, created_at DESC);

-- ============================================================================
-- Table: mood_reflections
-- Stores AI-generated reflections for each mood
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.mood_reflections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mood_id UUID REFERENCES public.moods(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  reflection_text TEXT NOT NULL,
  action_suggestion TEXT NOT NULL,
  share_caption TEXT NOT NULL,
  soundtrack_hint TEXT,
  tags TEXT[] NOT NULL,
  safety_flag TEXT NOT NULL CHECK (safety_flag IN ('ok', 'elevate'))
);

-- Index for faster mood-to-reflection lookups
CREATE INDEX IF NOT EXISTS idx_reflections_mood_id ON public.mood_reflections(mood_id);
CREATE INDEX IF NOT EXISTS idx_reflections_safety_flag ON public.mood_reflections(safety_flag);

-- ============================================================================
-- Table: referrals
-- Tracks viral loop and referral rewards
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.referrals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  inviter_user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  invited_email TEXT,
  invited_user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
  accepted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  accepted_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for referral tracking
CREATE INDEX IF NOT EXISTS idx_referrals_inviter ON public.referrals(inviter_user_id);
CREATE INDEX IF NOT EXISTS idx_referrals_email ON public.referrals(invited_email);

-- ============================================================================
-- Table: user_unlocks
-- Tracks gamification unlocks (custom gradients, voice reflections, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_unlocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  unlock_type TEXT NOT NULL, -- 'custom_gradient', 'voice_reflection', etc.
  unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, unlock_type)
);

-- Index for checking unlocks
CREATE INDEX IF NOT EXISTS idx_unlocks_user_id ON public.user_unlocks(user_id);

-- ============================================================================
-- Table: notifications
-- Stores scheduled notifications for users
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  scheduled_for TIMESTAMP WITH TIME ZONE,
  sent_at TIMESTAMP WITH TIME ZONE,
  notification_type TEXT NOT NULL, -- 'gentle_reminder', 'streak_nudge', 'evening_checkin', 'milestone'
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  is_sent BOOLEAN DEFAULT FALSE
);

-- Indexes for notification management
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_scheduled ON public.notifications(scheduled_for) WHERE is_sent = FALSE;

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Function to update streak when a new mood is posted
CREATE OR REPLACE FUNCTION update_user_streak()
RETURNS TRIGGER AS $$
DECLARE
  last_date DATE;
  current_date DATE;
BEGIN
  -- Get the user's last mood date
  SELECT last_mood_date INTO last_date
  FROM public.users
  WHERE id = NEW.user_id;
  
  current_date := DATE(NEW.created_at);
  
  -- Update streak logic
  IF last_date IS NULL THEN
    -- First mood ever
    UPDATE public.users
    SET streak_days = 1, last_mood_date = current_date
    WHERE id = NEW.user_id;
  ELSIF last_date = current_date THEN
    -- Same day, no streak change
    NULL;
  ELSIF last_date = current_date - INTERVAL '1 day' THEN
    -- Consecutive day, increment streak
    UPDATE public.users
    SET streak_days = streak_days + 1, last_mood_date = current_date
    WHERE id = NEW.user_id;
  ELSE
    -- Streak broken, reset to 1
    UPDATE public.users
    SET streak_days = 1, last_mood_date = current_date
    WHERE id = NEW.user_id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update streak on mood insert
DROP TRIGGER IF EXISTS trigger_update_streak ON public.moods;
CREATE TRIGGER trigger_update_streak
  AFTER INSERT ON public.moods
  FOR EACH ROW
  EXECUTE FUNCTION update_user_streak();

-- Function to award MoodCoins for daily posts
CREATE OR REPLACE FUNCTION award_daily_moodcoins()
RETURNS TRIGGER AS $$
DECLARE
  last_date DATE;
  current_date DATE;
BEGIN
  SELECT last_mood_date INTO last_date
  FROM public.users
  WHERE id = NEW.user_id;
  
  current_date := DATE(NEW.created_at);
  
  -- Award 5 coins for daily post (only once per day)
  IF last_date IS NULL OR last_date < current_date THEN
    UPDATE public.users
    SET moodcoins = moodcoins + 5
    WHERE id = NEW.user_id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to award coins on mood insert
DROP TRIGGER IF EXISTS trigger_award_coins ON public.moods;
CREATE TRIGGER trigger_award_coins
  AFTER INSERT ON public.moods
  FOR EACH ROW
  EXECUTE FUNCTION award_daily_moodcoins();

-- Function to award streak bonus coins (every 3 days)
CREATE OR REPLACE FUNCTION award_streak_bonus()
RETURNS TRIGGER AS $$
BEGIN
  -- Award 5 bonus coins every 3 days of streak
  IF NEW.streak_days % 3 = 0 AND NEW.streak_days > 0 THEN
    UPDATE public.users
    SET moodcoins = moodcoins + 5
    WHERE id = NEW.id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to award streak bonus
DROP TRIGGER IF EXISTS trigger_streak_bonus ON public.users;
CREATE TRIGGER trigger_streak_bonus
  AFTER UPDATE OF streak_days ON public.users
  FOR EACH ROW
  WHEN (NEW.streak_days > OLD.streak_days)
  EXECUTE FUNCTION award_streak_bonus();

-- Function to award referral coins
CREATE OR REPLACE FUNCTION award_referral_coins()
RETURNS TRIGGER AS $$
BEGIN
  -- Award 25 coins to inviter when referral is accepted
  IF NEW.accepted = TRUE AND OLD.accepted = FALSE THEN
    UPDATE public.users
    SET moodcoins = moodcoins + 25
    WHERE id = NEW.inviter_user_id;
    
    UPDATE public.referrals
    SET accepted_at = NOW()
    WHERE id = NEW.id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to award referral coins
DROP TRIGGER IF EXISTS trigger_referral_coins ON public.referrals;
CREATE TRIGGER trigger_referral_coins
  AFTER UPDATE OF accepted ON public.referrals
  FOR EACH ROW
  EXECUTE FUNCTION award_referral_coins();

-- ============================================================================
-- Row Level Security (RLS) Policies
-- Enable RLS for all tables
-- ============================================================================

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.moods ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mood_reflections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_unlocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Users can only read/update their own profile
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- Users can only read/create their own moods
CREATE POLICY "Users can view own moods" ON public.moods
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own moods" ON public.moods
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can only read reflections for their own moods
CREATE POLICY "Users can view own reflections" ON public.mood_reflections
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.moods
      WHERE moods.id = mood_reflections.mood_id
      AND moods.user_id = auth.uid()
    )
  );

-- Users can view their own referrals
CREATE POLICY "Users can view own referrals" ON public.referrals
  FOR SELECT USING (auth.uid() = inviter_user_id);

CREATE POLICY "Users can create referrals" ON public.referrals
  FOR INSERT WITH CHECK (auth.uid() = inviter_user_id);

-- Users can view their own unlocks
CREATE POLICY "Users can view own unlocks" ON public.user_unlocks
  FOR SELECT USING (auth.uid() = user_id);

-- Users can view their own notifications
CREATE POLICY "Users can view own notifications" ON public.notifications
  FOR SELECT USING (auth.uid() = user_id);

-- ============================================================================
-- Sample Data (Optional - for testing)
-- ============================================================================

-- Uncomment to insert sample users
-- INSERT INTO public.users (locale, display_name, streak_days, moodcoins)
-- VALUES 
--   ('fr', 'Sophie', 5, 30),
--   ('ar-darija', 'Youssef', 3, 20),
--   ('en', 'Emma', 10, 65);

-- ============================================================================
-- End of Migration
-- ============================================================================
