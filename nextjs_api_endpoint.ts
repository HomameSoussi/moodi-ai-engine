/**
 * MOODI Reflection API Endpoint
 * Next.js API Route Handler
 * 
 * File: /pages/api/moodi-reflection.ts (Pages Router)
 * Or: /app/api/moodi-reflection/route.ts (App Router)
 */

import { NextApiRequest, NextApiResponse } from "next";
import OpenAI from "openai";

// Initialize OpenAI client
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY! });

// System prompt for MOODI Reflection Engine
const SYSTEM_PROMPT = `You are **MOODI Reflection Engine**, an emotion-first micro-coach. 
Your job: transform a user's mood into a short, empathetic reflection + a tiny action.

Non-negotiables:
- **Max 60 words** for \`reflection_text\` (empathetic, human, specific to the mood, never generic).
- Give **one** tiny, doable suggestion in \`action_suggestion\` (max 20 words).
- Keep language and dialect = \`user_locale\` (support: ar, ar-darija, fr, en). If \`user_locale\` is \`ar-darija\`, reply in **Moroccan Darija** (Arabic script acceptable).
- Add a short \`share_caption\` users can post publicly (≤ 15 words, uplifting).
- For sound, give 1 \`soundtrack_hint\` (mood/genre; avoid trademarks where unsure).
- Add 3–6 \`tags\` capturing emotion nuance (e.g., ["calm","gratitude","evening","alone"]).
- **ALWAYS include \`safety_flag\`** in your response. Set it to "ok" for normal moods, or "elevate" if self-harm risk is detected.
- Output **valid JSON** matching the provided schema—no extra keys, no prose outside JSON.

Guardrails:
- No medical/clinical claims. If self-harm risk is present, set \`safety_flag: "elevate"\` and set \`action_suggestion\` to seeking help (culturally appropriate hotline/close person), no coaching beyond that.
- Never include PII. Never shame the user.
- If mood media is present, you may reference it generically (e.g., "in your photo", "in your voice note"); never describe people or private details.

Tone:
- Warm, brief, non-therapeutic. Use everyday language.

Required JSON fields: reflection_text, action_suggestion, share_caption, soundtrack_hint, tags, safety_flag`;

/**
 * Mood Payload Interface
 */
interface MoodPayload {
  mood_emoji: string;
  mood_color: string;
  intensity_0_10: number;
  context_text?: string;
  media_present: boolean;
  time_bucket: "morning" | "afternoon" | "evening" | "late-night";
  geo_hint?: string;
  user_locale: "ar" | "ar-darija" | "fr" | "en";
  user_age_bucket: "teen" | "young-adult" | "adult" | "senior";
}

/**
 * Reflection Response Interface
 */
interface ReflectionResponse {
  reflection_text: string;
  action_suggestion: string;
  share_caption: string;
  soundtrack_hint: string;
  tags: string[];
  safety_flag: "ok" | "elevate";
}

/**
 * API Handler
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Only allow POST requests
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const moodPayload: MoodPayload = req.body;

    // Validate required fields
    if (!moodPayload.mood_emoji || !moodPayload.user_locale) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    // Build user prompt
    const userPrompt = `You will receive a mood payload:

${JSON.stringify(moodPayload, null, 2)}

Return a single JSON object that fits the schema.`;

    // Call OpenAI API
    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      temperature: 0.7,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: userPrompt },
      ],
    });

    // Parse response
    const reflection: ReflectionResponse = JSON.parse(
      response.choices[0].message?.content || "{}"
    );

    // Return reflection
    res.status(200).json(reflection);
  } catch (e: any) {
    console.error("Error generating reflection:", e);
    res.status(500).json({ error: e?.message || "Unknown error" });
  }
}

/**
 * Example cURL test:
 * 
 * curl -X POST http://localhost:3000/api/moodi-reflection \
 *  -H "Content-Type: application/json" \
 *  -d '{
 *    "mood_emoji":"😌",
 *    "mood_color":"#7FD1AE",
 *    "intensity_0_10":4,
 *    "context_text":"petite promenade au bord de mer",
 *    "media_present":true,
 *    "time_bucket":"evening",
 *    "geo_hint":"Casablanca",
 *    "user_locale":"fr",
 *    "user_age_bucket":"adult"
 *  }'
 */
