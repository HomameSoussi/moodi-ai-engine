# Complete MOODI Integration Example

## End-to-End Flow: From Mood Submission to Database Storage

This guide shows the complete flow of a mood submission through the MOODI system.

---

## 🔄 Complete Flow Diagram

```
User Submits Mood
       ↓
Mobile App (Client)
       ↓
POST /api/reflection
       ↓
MOODI API (Vercel)
       ↓
OpenAI GPT-4.1-mini
       ↓
AI Reflection Generated
       ↓
Return to Mobile App
       ↓
Store in Supabase
       ↓
Update User Stats (Streak, Coins)
       ↓
Display to User
```

---

## 📱 Step 1: User Submits Mood (Mobile App)

### User Action
User selects mood emoji, adds optional text, and submits.

### Mobile App Code (React Native Example)

```javascript
import { useState } from 'react';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabase = createClient(
  'YOUR_SUPABASE_URL',
  'YOUR_SUPABASE_ANON_KEY'
);

const MOODI_API_URL = 'https://moodi-ai-engine.vercel.app';

async function submitMood(moodData) {
  try {
    // Step 1: Get current user
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) throw new Error('Not authenticated');
    
    // Step 2: Prepare mood payload
    const moodPayload = {
      mood_emoji: moodData.emoji,
      mood_color: moodData.color,
      intensity_0_10: moodData.intensity,
      context_text: moodData.note,
      media_present: moodData.hasMedia,
      time_bucket: getCurrentTimeBucket(), // morning, afternoon, evening, late-night
      geo_hint: moodData.location,
      user_locale: moodData.locale || 'en',
      user_age_bucket: moodData.ageBucket || 'adult'
    };
    
    // Step 3: Call MOODI API for AI reflection
    const reflectionResponse = await fetch(`${MOODI_API_URL}/api/reflection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(moodPayload)
    });
    
    if (!reflectionResponse.ok) {
      throw new Error('Failed to generate reflection');
    }
    
    const reflection = await reflectionResponse.json();
    
    // Step 4: Handle safety flag
    if (reflection.safety_flag === 'elevate') {
      // Show crisis support resources
      showCrisisSupport(reflection.action_suggestion);
      return { success: true, elevated: true };
    }
    
    // Step 5: Store mood in Supabase
    const { data: moodRecord, error: moodError } = await supabase
      .from('moods')
      .insert({
        user_id: user.id,
        mood_emoji: moodPayload.mood_emoji,
        mood_color: moodPayload.mood_color,
        intensity_0_10: moodPayload.intensity_0_10,
        context_text: moodPayload.context_text,
        media_present: moodPayload.media_present,
        time_bucket: moodPayload.time_bucket,
        geo_hint: moodPayload.geo_hint
      })
      .select()
      .single();
    
    if (moodError) throw moodError;
    
    // Step 6: Store AI reflection
    const { data: reflectionRecord, error: reflectionError } = await supabase
      .from('mood_reflections')
      .insert({
        mood_id: moodRecord.id,
        reflection_text: reflection.reflection_text,
        action_suggestion: reflection.action_suggestion,
        share_caption: reflection.share_caption,
        soundtrack_hint: reflection.soundtrack_hint,
        tags: reflection.tags,
        safety_flag: reflection.safety_flag
      })
      .select()
      .single();
    
    if (reflectionError) throw reflectionError;
    
    // Step 7: Get updated user stats (streak, coins)
    const { data: userData, error: userError } = await supabase
      .from('users')
      .select('streak_days, moodcoins')
      .eq('id', user.id)
      .single();
    
    if (userError) throw userError;
    
    // Step 8: Check for new unlocks
    const { data: unlocks } = await supabase
      .from('user_unlocks')
      .select('unlock_type')
      .eq('user_id', user.id);
    
    // Step 9: Return complete result
    return {
      success: true,
      reflection: reflection,
      mood_id: moodRecord.id,
      streak_days: userData.streak_days,
      moodcoins: userData.moodcoins,
      unlocks: unlocks.map(u => u.unlock_type),
      elevated: false
    };
    
  } catch (error) {
    console.error('Failed to submit mood:', error);
    throw error;
  }
}

// Helper function to determine time bucket
function getCurrentTimeBucket() {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 12) return 'morning';
  if (hour >= 12 && hour < 17) return 'afternoon';
  if (hour >= 17 && hour < 22) return 'evening';
  return 'late-night';
}

// Helper function to show crisis support
function showCrisisSupport(actionSuggestion) {
  // Show alert with crisis resources
  Alert.alert(
    'Support Available',
    actionSuggestion,
    [
      { text: 'Call Hotline', onPress: () => Linking.openURL('tel:988') },
      { text: 'Close', style: 'cancel' }
    ]
  );
}
```

---

## 🗄️ Step 2: Supabase Database Setup

### Execute the SQL Schema

1. Go to your Supabase project dashboard
2. Click on "SQL Editor"
3. Copy and paste the contents of `supabase_schema.sql`
4. Click "Run"

The schema includes:
- ✅ All 6 tables (users, moods, mood_reflections, referrals, user_unlocks, notifications)
- ✅ Automatic triggers for streaks and coins
- ✅ Row-level security policies
- ✅ Indexes for performance

---

## 🎮 Step 3: Gamification Logic (Automatic)

### What Happens Automatically

When a mood is inserted into the `moods` table, Supabase triggers automatically:

1. **Update Streak** (`trigger_update_streak`)
   - Checks last mood date
   - Increments streak if consecutive day
   - Resets to 1 if streak broken

2. **Award Daily Coins** (`trigger_award_coins`)
   - Awards 5 coins for first mood of the day
   - Only once per day

3. **Award Streak Bonus** (`trigger_streak_bonus`)
   - Awards 5 bonus coins every 3 days
   - Triggered when streak_days updates

### Manual Coin Awards

For referrals, update manually:

```javascript
// When a referral is accepted
async function acceptReferral(referralId, invitedUserId) {
  const { error } = await supabase
    .from('referrals')
    .update({
      invited_user_id: invitedUserId,
      accepted: true
    })
    .eq('id', referralId);
  
  // Trigger automatically awards 25 coins to inviter
}
```

---

## 📊 Step 4: Display Results to User

### UI Components

```javascript
function MoodReflectionScreen({ result }) {
  return (
    <View>
      {/* Reflection Card */}
      <Card>
        <Text style={styles.reflection}>
          {result.reflection.reflection_text}
        </Text>
        <Text style={styles.action}>
          💡 {result.reflection.action_suggestion}
        </Text>
      </Card>
      
      {/* Streak & Coins */}
      <StatsCard>
        <Stat icon="🔥" value={result.streak_days} label="Day Streak" />
        <Stat icon="🪙" value={result.moodcoins} label="MoodCoins" />
      </StatsCard>
      
      {/* Tags */}
      <TagsContainer>
        {result.reflection.tags.map(tag => (
          <Tag key={tag}>{tag}</Tag>
        ))}
      </TagsContainer>
      
      {/* Share Button */}
      <ShareButton caption={result.reflection.share_caption} />
      
      {/* Soundtrack Suggestion */}
      <MusicCard hint={result.reflection.soundtrack_hint} />
    </View>
  );
}
```

---

## 🔔 Step 5: Schedule Notifications

### Daily Reminder

```javascript
async function scheduleDailyReminder(userId) {
  // Get user's streak
  const { data: user } = await supabase
    .from('users')
    .select('streak_days, locale')
    .eq('id', userId)
    .single();
  
  // Generate notification copy
  const notificationResponse = await fetch(
    `${MOODI_API_URL}/api/notification`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_locale: user.locale,
        theme: 'streak_nudge',
        days_streak: user.streak_days
      })
    }
  );
  
  const notification = await notificationResponse.json();
  
  // Schedule push notification
  await Notifications.scheduleNotificationAsync({
    content: {
      title: notification.title,
      body: notification.body
    },
    trigger: {
      hour: 20, // 8 PM
      minute: 0,
      repeats: true
    }
  });
}
```

---

## 🔗 Step 6: Referral System

### Generate Referral Link

```javascript
async function generateReferralLink(userId) {
  // Get user data
  const { data: user } = await supabase
    .from('users')
    .select('display_name')
    .eq('id', userId)
    .single();
  
  // Generate referral caption
  const captionResponse = await fetch(
    `${MOODI_API_URL}/api/referral-caption`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_locale: 'en',
        mood_emoji: '😊',
        benefit: 'Track your mood, get a tiny AI nudge'
      })
    }
  );
  
  const { caption } = await captionResponse.json();
  
  // Create referral link
  const referralLink = `https://moodi.app/invite/${userId}`;
  
  // Share
  await Share.share({
    message: `${caption}\n\n${referralLink}`,
    url: referralLink
  });
}

// When someone accepts the referral
async function createReferral(inviterUserId, invitedEmail) {
  const { data, error } = await supabase
    .from('referrals')
    .insert({
      inviter_user_id: inviterUserId,
      invited_email: invitedEmail,
      accepted: false
    })
    .select()
    .single();
  
  return data;
}
```

---

## 📈 Step 7: Analytics & Insights

### Track User Mood Patterns

```javascript
async function getMoodHistory(userId, days = 30) {
  const { data: moods } = await supabase
    .from('moods')
    .select(`
      *,
      mood_reflections (
        tags,
        safety_flag
      )
    `)
    .eq('user_id', userId)
    .gte('created_at', new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString())
    .order('created_at', { ascending: false });
  
  return moods;
}

async function getMoodInsights(userId) {
  const moods = await getMoodHistory(userId, 30);
  
  // Calculate insights
  const avgIntensity = moods.reduce((sum, m) => sum + m.intensity_0_10, 0) / moods.length;
  const mostCommonEmoji = getMostCommon(moods.map(m => m.mood_emoji));
  const mostCommonTags = getMostCommon(
    moods.flatMap(m => m.mood_reflections[0]?.tags || [])
  );
  const timeBucketDistribution = getDistribution(moods.map(m => m.time_bucket));
  
  return {
    avgIntensity,
    mostCommonEmoji,
    mostCommonTags: mostCommonTags.slice(0, 5),
    timeBucketDistribution,
    totalMoods: moods.length
  };
}
```

---

## 🎯 Complete Example: Full User Journey

```javascript
// User opens app and submits mood
const userJourney = async () => {
  try {
    // 1. User submits mood
    const moodData = {
      emoji: '😌',
      color: '#7FD1AE',
      intensity: 4,
      note: 'Feeling calm after a walk',
      hasMedia: false,
      location: 'New York',
      locale: 'en',
      ageBucket: 'adult'
    };
    
    const result = await submitMood(moodData);
    
    // 2. Display reflection
    showReflection(result.reflection);
    
    // 3. Update UI with new stats
    updateStats({
      streak: result.streak_days,
      coins: result.moodcoins
    });
    
    // 4. Check for new unlocks
    if (result.moodcoins >= 50 && !result.unlocks.includes('custom_gradient')) {
      showUnlockAnimation('Custom Gradient Unlocked! 🎨');
      await supabase.from('user_unlocks').insert({
        user_id: user.id,
        unlock_type: 'custom_gradient'
      });
    }
    
    // 5. Schedule next reminder
    await scheduleDailyReminder(user.id);
    
    // 6. Track analytics
    await trackEvent('mood_submitted', {
      emoji: moodData.emoji,
      intensity: moodData.intensity,
      streak: result.streak_days
    });
    
  } catch (error) {
    showError('Failed to submit mood. Please try again.');
  }
};
```

---

## ✅ Testing Checklist

- [ ] User can submit mood
- [ ] AI reflection is generated
- [ ] Mood is stored in Supabase
- [ ] Reflection is stored in Supabase
- [ ] Streak is calculated correctly
- [ ] Coins are awarded automatically
- [ ] Unlocks trigger at thresholds
- [ ] Safety flag is handled properly
- [ ] Notifications are scheduled
- [ ] Referral system works
- [ ] Analytics are tracked

---

## 🔐 Security Best Practices

1. **Row Level Security** - Already enabled in schema
2. **API Keys** - Store in environment variables, never in code
3. **User Authentication** - Use Supabase Auth
4. **Input Validation** - Validate on client and server
5. **Rate Limiting** - Implement on client side

---

## 📞 Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check Supabase logs
3. Verify environment variables
4. Test API endpoints individually

---

**Complete MVP Integration Ready!** 🚀
