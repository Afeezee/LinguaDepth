export type Level = 'beginner' | 'intermediate' | 'advanced'
export type QuestionType = 'objective' | 'theory' | 'oral'
export type Difficulty = 'easy' | 'medium' | 'hard'

export interface User {
  id: number
  name: string
  email: string
  level: Level
  xp: number
  streak_days: number
  is_admin?: boolean
}

export interface AdminUser extends User {
  sessions_completed: number
  avg_score: number | null
  last_active: string | null
  created_at: string | null
}

export interface AdminAnalytics {
  totals: {
    users: number
    sessions_completed: number
    lessons: number
    questions: number
    avg_score: number
    active_today: number
    active_week: number
  }
  level_distribution: { level: Level; count: number }[]
  signups_daily: { date: string; count: number }[]
  sessions_daily: { date: string; count: number }[]
  weak_topics: { topic: string; wrong: number; error_rate: number }[]
}

export interface Lesson {
  id: number
  title: string
  content: string
  level: Level
  topic: string
  path_type: 'core' | 'level_path'
  order_index: number
  quiz_types: QuestionType[]
  completed: boolean
}

export interface Question {
  id: number
  lesson_id: number
  type: QuestionType
  difficulty: Difficulty
  level: Level
  question_text: string
  options: string[] | null
}

export interface AnswerResult {
  correct: boolean
  skipped?: boolean
  score?: number
  feedback?: string
  explanation?: string
  correct_answer?: string
  xp_earned: number
}

export interface QuizCompleteResult {
  final_score: number
  level_changed: boolean
  new_level: Level
  xp_earned: number
  streak_updated: boolean
  streak_days: number
}

export interface DashboardStats {
  level: Level
  xp: number
  streak_days: number
  lessons_completed: number
  total_lessons: number
  completion_percent: number
  weekly_scores: { date: string; score: number }[]
  top_weak_topics: { topic: string; error_rate: number }[]
}

export interface ReportData {
  weekly_scores: { date: string; avg_score: number }[]
  wrong_by_topic: { topic: string; count: number }[]
  avg_quiz_time: number
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface AnsweredQuestion {
  question: Question
  userAnswer: string
  result: AnswerResult
}
