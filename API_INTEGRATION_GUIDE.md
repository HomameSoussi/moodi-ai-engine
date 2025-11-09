# MOODI API Integration Guide

## 🚀 Production API URL

```
https://moodi-ai-engine.vercel.app
```

All endpoints are **live and tested** ✅

---

## 📡 API Endpoints

### 1. Health Check

**Endpoint:** `GET /`

**Purpose:** Verify API is running and healthy

**Request:**
```bash
curl https://moodi-ai-engine.vercel.app/
```

**Response:**
```json
{
  "service": "MOODI Reflection API",
  "status": "healthy",
  "version": "1.0.0",
  "deployment": "Vercel"
}
```

---

### 2. Generate Mood Reflection

**Endpoint:** `POST /api/reflection`

**Purpose:** Transform user mood into empathetic reflection with actionable suggestion

**Request Body:**
```json
{
  "mood_emoji": "😌",
  "mood_color": "#7FD1AE",
  "intensity_0_10": 4,
  "context_text": "petite promenade au bord de mer",
  "media_present": true,
  "time_bucket": "evening",
  "geo_hint": "Casablanca",
  "user_locale": "fr",
  "user_age_bucket": "adult"
}
```

**Field Descriptions:**

| Field | Type | Required | Description | Example Values |
|-------|------|----------|-------------|----------------|
| `mood_emoji` | string | Yes | Emoji representing mood | "😌", "😊", "😣", "😢" |
| `mood_color` | string | Yes | Hex color code | "#7FD1AE", "#F08A5D" |
| `intensity_0_10` | integer | Yes | Mood intensity (0-10) | 0-10 |
| `context_text` | string | No | User's mood note/context | "feeling calm", "stressed about work" |
| `media_present` | boolean | Yes | Whether user attached media | true, false |
| `time_bucket` | string | Yes | Time of day | "morning", "afternoon", "evening", "late-night" |
| `geo_hint` | string | No | City or country | "Casablanca", "Paris", "New York" |
| `user_locale` | string | Yes | Language/dialect | "ar", "ar-darija", "fr", "en" |
| `user_age_bucket` | string | Yes | Age group | "teen", "young-adult", "adult", "senior" |

**Response:**
```json
{
  "reflection_text": "Cette petite promenade au bord de mer à Casablanca apaise doucement ton esprit ce soir. Profiter de ces moments calmes nourrit ton bien-être intérieur.",
  "action_suggestion": "Respire profondément en regardant l'horizon pendant une minute.",
  "share_caption": "Un moment de calme au bord de la mer, précieux et doux.",
  "soundtrack_hint": "musique acoustique douce, ambiance détente",
  "tags": ["calme", "apaisement", "soirée", "nature", "bord de mer"],
  "safety_flag": "ok"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `reflection_text` | string | Empathetic reflection (max 360 chars) |
| `action_suggestion` | string | Actionable micro-suggestion (max 120 chars) |
| `share_caption` | string | Social share caption (max 90 chars) |
| `soundtrack_hint` | string | Music mood/genre suggestion |
| `tags` | array | 3-6 emotion tags |
| `safety_flag` | string | "ok" or "elevate" (for at-risk users) |

---

### 3. Generate Notification

**Endpoint:** `POST /api/notification`

**Purpose:** Create push notification copy for mood reminders

**Request Body:**
```json
{
  "user_locale": "fr",
  "theme": "streak_nudge",
  "days_streak": 7
}
```

**Field Descriptions:**

| Field | Type | Required | Description | Example Values |
|-------|------|----------|-------------|----------------|
| `user_locale` | string | Yes | Language/dialect | "ar", "ar-darija", "fr", "en" |
| `theme` | string | Yes | Notification type | "gentle_reminder", "streak_nudge", "evening_checkin", "milestone" |
| `days_streak` | integer | No | Current streak count | 0-999 |

**Response:**
```json
{
  "title": "Bravo pour 7 jours de suite !",
  "body": "Continue comme ça, chaque jour compte pour ton bien-être."
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Notification title (max 80 chars) |
| `body` | string | Notification body (max 80 chars) |

---

### 4. Generate Referral Caption

**Endpoint:** `POST /api/referral-caption`

**Purpose:** Create social share caption for viral growth

**Request Body:**
```json
{
  "user_locale": "en",
  "mood_emoji": "😊",
  "benefit": "Track your mood, get a tiny AI nudge"
}
```

**Field Descriptions:**

| Field | Type | Required | Description | Example Values |
|-------|------|----------|-------------|----------------|
| `user_locale` | string | Yes | Language/dialect | "ar", "ar-darija", "fr", "en" |
| `mood_emoji` | string | Yes | Emoji for caption | "😊", "😌", "🎉" |
| `benefit` | string | No | App benefit text | "Track your mood, get a tiny AI nudge" |

**Response:**
```json
{
  "caption": "😊 Track your mood daily & get a tiny AI nudge!"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `caption` | string | Social share caption (max 72 chars, ~12 words) |

---

## 📱 Mobile Integration Examples

### Swift (iOS)

```swift
import Foundation

struct MoodPayload: Codable {
    let mood_emoji: String
    let mood_color: String
    let intensity_0_10: Int
    let context_text: String?
    let media_present: Bool
    let time_bucket: String
    let geo_hint: String?
    let user_locale: String
    let user_age_bucket: String
}

struct ReflectionResponse: Codable {
    let reflection_text: String
    let action_suggestion: String
    let share_caption: String
    let soundtrack_hint: String
    let tags: [String]
    let safety_flag: String
}

func generateReflection(payload: MoodPayload) async throws -> ReflectionResponse {
    let url = URL(string: "https://moodi-ai-engine.vercel.app/api/reflection")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.httpBody = try JSONEncoder().encode(payload)
    
    let (data, _) = try await URLSession.shared.data(for: request)
    return try JSONDecoder().decode(ReflectionResponse.self, from: data)
}

// Usage
Task {
    let payload = MoodPayload(
        mood_emoji: "😌",
        mood_color: "#7FD1AE",
        intensity_0_10: 4,
        context_text: "feeling calm",
        media_present: false,
        time_bucket: "evening",
        geo_hint: "New York",
        user_locale: "en",
        user_age_bucket: "adult"
    )
    
    let reflection = try await generateReflection(payload: payload)
    print(reflection.reflection_text)
}
```

---

### Kotlin (Android)

```kotlin
import kotlinx.coroutines.*
import kotlinx.serialization.*
import kotlinx.serialization.json.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType

@Serializable
data class MoodPayload(
    val mood_emoji: String,
    val mood_color: String,
    val intensity_0_10: Int,
    val context_text: String? = null,
    val media_present: Boolean,
    val time_bucket: String,
    val geo_hint: String? = null,
    val user_locale: String,
    val user_age_bucket: String
)

@Serializable
data class ReflectionResponse(
    val reflection_text: String,
    val action_suggestion: String,
    val share_caption: String,
    val soundtrack_hint: String,
    val tags: List<String>,
    val safety_flag: String
)

class MoodiApiClient {
    private val client = OkHttpClient()
    private val json = Json { ignoreUnknownKeys = true }
    private val baseUrl = "https://moodi-ai-engine.vercel.app"
    
    suspend fun generateReflection(payload: MoodPayload): ReflectionResponse {
        return withContext(Dispatchers.IO) {
            val jsonBody = json.encodeToString(payload)
            val request = Request.Builder()
                .url("$baseUrl/api/reflection")
                .post(RequestBody.create("application/json".toMediaType(), jsonBody))
                .build()
            
            val response = client.newCall(request).execute()
            val responseBody = response.body?.string() ?: throw Exception("Empty response")
            json.decodeFromString<ReflectionResponse>(responseBody)
        }
    }
}

// Usage
CoroutineScope(Dispatchers.Main).launch {
    val client = MoodiApiClient()
    val payload = MoodPayload(
        mood_emoji = "😌",
        mood_color = "#7FD1AE",
        intensity_0_10 = 4,
        context_text = "feeling calm",
        media_present = false,
        time_bucket = "evening",
        geo_hint = "New York",
        user_locale = "en",
        user_age_bucket = "adult"
    )
    
    val reflection = client.generateReflection(payload)
    println(reflection.reflection_text)
}
```

---

### React Native (JavaScript)

```javascript
const MOODI_API_URL = 'https://moodi-ai-engine.vercel.app';

async function generateReflection(moodPayload) {
  try {
    const response = await fetch(`${MOODI_API_URL}/api/reflection`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(moodPayload),
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to generate reflection:', error);
    throw error;
  }
}

// Usage
const moodPayload = {
  mood_emoji: '😌',
  mood_color: '#7FD1AE',
  intensity_0_10: 4,
  context_text: 'feeling calm',
  media_present: false,
  time_bucket: 'evening',
  geo_hint: 'New York',
  user_locale: 'en',
  user_age_bucket: 'adult',
};

generateReflection(moodPayload)
  .then(reflection => {
    console.log(reflection.reflection_text);
    console.log(reflection.action_suggestion);
  })
  .catch(error => console.error(error));
```

---

## 🔒 Safety Handling

### Safety Flag Response

Every reflection includes a `safety_flag` field:

- **`"ok"`** - Normal mood, display reflection and action
- **`"elevate"`** - At-risk user detected, show support resources

### Handling Elevated Safety

```javascript
if (reflection.safety_flag === 'elevate') {
  // Show crisis support resources instead of normal reflection
  showCrisisSupport({
    hotline: getLocalHotline(userCountry),
    message: reflection.action_suggestion, // Will suggest seeking help
    emergencyContacts: userEmergencyContacts
  });
} else {
  // Display normal reflection
  displayReflection(reflection);
}
```

### Recommended Crisis Resources

| Country | Hotline | Number |
|---------|---------|--------|
| Morocco | SOS Détresse | 0801 000 180 |
| France | SOS Amitié | 09 72 39 40 50 |
| USA | 988 Suicide & Crisis Lifeline | 988 |
| International | Befrienders Worldwide | https://befrienders.org |

---

## ⚡ Performance & Limits

### Response Times
- **Health Check:** <100ms
- **Reflection:** 2-5 seconds (AI processing)
- **Notification:** 1-3 seconds
- **Referral Caption:** 1-3 seconds

### Rate Limits
- Vercel Hobby: 100 requests/10 seconds
- Vercel Pro: 600 requests/10 seconds

### Timeout
- Function timeout: 10 seconds (Hobby), 60 seconds (Pro)

---

## 🐛 Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Check payload format |
| 422 | Validation Error | Check required fields |
| 500 | Server Error | Retry with exponential backoff |
| 504 | Timeout | Retry request |

### Example Error Response

```json
{
  "detail": "Field required: mood_emoji"
}
```

### Error Handling Example

```javascript
try {
  const reflection = await generateReflection(payload);
  return reflection;
} catch (error) {
  if (error.status === 422) {
    // Validation error - check payload
    console.error('Invalid payload:', error.detail);
  } else if (error.status === 500) {
    // Server error - retry
    await delay(1000);
    return generateReflection(payload);
  } else {
    // Unknown error
    console.error('API error:', error);
  }
}
```

---

## 🧪 Testing

### Postman Collection

Import this JSON into Postman for easy testing:

```json
{
  "info": {
    "name": "MOODI API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "https://moodi-ai-engine.vercel.app/"
      }
    },
    {
      "name": "Generate Reflection",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "url": "https://moodi-ai-engine.vercel.app/api/reflection",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"mood_emoji\": \"😌\",\n  \"mood_color\": \"#7FD1AE\",\n  \"intensity_0_10\": 4,\n  \"context_text\": \"feeling calm\",\n  \"media_present\": false,\n  \"time_bucket\": \"evening\",\n  \"user_locale\": \"en\",\n  \"user_age_bucket\": \"adult\"\n}"
        }
      }
    }
  ]
}
```

---

## 📊 Monitoring

### Track These Metrics

1. **API Response Time** - Should be <5s for reflections
2. **Error Rate** - Should be <1%
3. **Safety Flag Rate** - Monitor "elevate" occurrences
4. **Language Distribution** - Track which locales are used most

---

## 🔗 Additional Resources

- **GitHub Repository:** https://github.com/HomameSoussi/moodi-ai-engine
- **Vercel Dashboard:** https://vercel.com/dashboard
- **OpenAI Status:** https://status.openai.com

---

## 💡 Best Practices

1. **Cache User Preferences** - Store locale, age_bucket locally
2. **Retry Logic** - Implement exponential backoff for failures
3. **Offline Mode** - Cache recent reflections for offline viewing
4. **Analytics** - Track which emotions are most common
5. **Safety First** - Always handle `safety_flag === "elevate"` appropriately

---

**Built with ❤️ for emotional wellness**
