import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowRight,
  Award,
  BarChart3,
  BookOpen,
  Bot,
  BrainCircuit,
  Flame,
  Globe2,
  GraduationCap,
  Mic,
  Quote,
  Sparkles,
  Star,
  TrendingUp,
  Volume2,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const fadeUp = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-80px' },
  transition: { duration: 0.55, ease: 'easeOut' },
}

const FEATURES = [
  {
    icon: BrainCircuit,
    title: 'AI That Knows Your Level',
    text: 'A machine-learning engine studies how you learn — your scores, speed, and progress — and serves lessons at exactly the right difficulty. Never bored, never lost.',
  },
  {
    icon: Bot,
    title: 'A Tutor That Never Sleeps',
    text: 'Every written answer is graded instantly by an AI language tutor with feedback that names your exact mistake — and celebrates your exact strength.',
  },
  {
    icon: Mic,
    title: 'Speak. Get Heard. Improve.',
    text: 'Practise speaking out loud. Your voice is understood, evaluated, and coached in real time — like having a conversation partner in your pocket.',
  },
  {
    icon: Flame,
    title: 'Learning That Feels Like a Game',
    text: 'Earn XP, build streaks, level up, and celebrate with confetti. Five-minute lessons designed to fit between lectures, not compete with them.',
  },
  {
    icon: Volume2,
    title: 'Hear Every Lesson',
    text: 'Tap once and any lesson is read aloud with natural pronunciation, so your listening improves while you read.',
  },
  {
    icon: BarChart3,
    title: 'See Yourself Improve',
    text: 'Weekly performance charts and weakest-topic breakdowns show you exactly where you stand — and exactly what to practise next.',
  },
]

const STEPS = [
  {
    icon: GraduationCap,
    title: 'Take the placement quiz',
    text: '10 friendly questions find your true starting level — beginner, intermediate, or advanced. No pressure, no timer.',
  },
  {
    icon: BookOpen,
    title: 'Learn in short bursts',
    text: 'Bite-sized lessons with audio, then a quick 5-question quiz mixing multiple choice, writing, and speaking.',
  },
  {
    icon: TrendingUp,
    title: 'Level up automatically',
    text: 'As your scores climb, the AI promotes you to harder material — and throws you a party when it happens.',
  },
]

const TESTIMONIALS = [
  {
    name: 'Adaeze O.',
    role: '200-level student, UNILAG',
    text: "The speaking practice changed everything for me. I used to freeze in presentations — now I rehearse with the AI tutor every night and it corrects me kindly, not like people who laugh.",
  },
  {
    name: 'Ibrahim S.',
    role: '300-level student, ABU Zaria',
    text: 'Five minutes between lectures is all it takes. The streak kept me coming back, and within a month it promoted me to intermediate. The confetti moment? I screenshotted it.',
  },
  {
    name: 'Chiamaka E.',
    role: 'Final year, UNN',
    text: 'The feedback on my writing is better than anything I got in class — it tells me the exact grammar rule I broke, in one sentence, every single time.',
  },
]

export default function LandingPage() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* ---------- Nav ---------- */}
      <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/80 backdrop-blur">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <a href="#top" className="flex items-center gap-2">
            <Globe2 className="h-7 w-7 text-emerald-500" />
            <span className="text-xl font-extrabold">
              Lingua<span className="text-emerald-600">Depth</span>
            </span>
          </a>
          <div className="hidden items-center gap-6 text-sm font-semibold text-gray-500 md:flex">
            <a href="#features" className="hover:text-gray-900">Features</a>
            <a href="#how-it-works" className="hover:text-gray-900">How it works</a>
            <a href="#testimonials" className="hover:text-gray-900">Students</a>
          </div>
          <div className="flex items-center gap-3">
            {user ? (
              <Link
                to="/dashboard"
                className="rounded-xl bg-emerald-500 px-5 py-2.5 font-semibold text-white transition-colors hover:bg-emerald-600"
              >
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link
                  to="/auth"
                  className="rounded-xl px-4 py-2.5 font-semibold text-gray-700 transition-colors hover:bg-gray-100"
                >
                  Sign In
                </Link>
                <Link
                  to="/auth?mode=register"
                  className="rounded-xl bg-emerald-500 px-5 py-2.5 font-semibold text-white transition-colors hover:bg-emerald-600"
                >
                  Sign Up Free
                </Link>
              </>
            )}
          </div>
        </nav>
      </header>

      {/* ---------- Hero ---------- */}
      <section id="top" className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-emerald-50 via-white to-white" />
        <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-4 py-20 md:grid-cols-2 md:py-28">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="mb-5 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-4 py-1.5 text-sm font-bold text-emerald-700">
              <Sparkles className="h-4 w-4" />
              AI-powered English learning for Nigerian students
            </span>
            <h1 className="mb-5 text-4xl font-extrabold leading-tight md:text-5xl lg:text-6xl">
              Speak English with{' '}
              <span className="text-emerald-600">confidence.</span>
              <br />
              Five minutes at a time.
            </h1>
            <p className="mb-8 max-w-lg text-lg text-gray-500">
              LinguaDepth blends a machine-learning curriculum director with an
              AI language tutor that grades your writing, listens to your
              speech, and chats with you — so every lesson meets you exactly
              where you are.
            </p>
            <div className="flex flex-wrap items-center gap-4">
              <Link
                to="/auth?mode=register"
                className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-7 py-3.5 text-lg font-bold text-white shadow-md transition-colors hover:bg-emerald-600"
              >
                Start Learning Free
                <ArrowRight className="h-5 w-5" />
              </Link>
              <a
                href="#how-it-works"
                className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-7 py-3.5 text-lg font-semibold text-gray-700 transition-colors hover:bg-gray-50"
              >
                See how it works
              </a>
            </div>
            <p className="mt-5 text-sm text-gray-500">
              Free to start · No card required · Works in your browser
            </p>
          </motion.div>

          {/* Hero visual — stylised app preview */}
          <motion.div
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="relative"
          >
            <div className="rounded-3xl border border-gray-200 bg-white p-6 shadow-xl">
              <div className="mb-4 flex items-center justify-between">
                <span className="font-bold">Welcome back, Ada! 👋</span>
                <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-3 py-1 text-sm font-bold text-amber-700">
                  <Award className="h-4 w-4" /> Intermediate
                </span>
              </div>
              <div className="mb-4 grid grid-cols-3 gap-3 text-center">
                <div className="rounded-2xl bg-emerald-50 p-3">
                  <Star className="mx-auto mb-1 h-5 w-5 fill-amber-400 text-amber-400" />
                  <p className="text-lg font-extrabold">1,240</p>
                  <p className="text-xs text-gray-500">XP</p>
                </div>
                <div className="rounded-2xl bg-orange-50 p-3">
                  <Flame className="mx-auto mb-1 h-5 w-5 fill-orange-400 text-orange-500" />
                  <p className="text-lg font-extrabold">17</p>
                  <p className="text-xs text-gray-500">day streak</p>
                </div>
                <div className="rounded-2xl bg-purple-50 p-3">
                  <TrendingUp className="mx-auto mb-1 h-5 w-5 text-purple-600" />
                  <p className="text-lg font-extrabold">86%</p>
                  <p className="text-xs text-gray-500">avg score</p>
                </div>
              </div>
              <div className="space-y-2">
                {[78, 92, 64, 88, 95].map((w, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="w-8 text-xs font-semibold text-gray-500">
                      {['Mon', 'Tue', 'Wed', 'Thu', 'Fri'][i]}
                    </span>
                    <div className="h-3 flex-1 overflow-hidden rounded-full bg-gray-100">
                      <motion.div
                        className="h-full rounded-full bg-emerald-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${w}%` }}
                        transition={{ duration: 0.9, delay: 0.5 + i * 0.12 }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <motion.div
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
              className="absolute -right-3 -top-5 rounded-2xl bg-emerald-500 px-4 py-2.5 text-sm font-bold text-white shadow-lg"
            >
              "Well done — perfect tense usage!" 🎉
            </motion.div>
            <motion.div
              animate={{ y: [0, 8, 0] }}
              transition={{ duration: 3.4, repeat: Infinity, ease: 'easeInOut' }}
              className="absolute -bottom-5 -left-3 flex items-center gap-2 rounded-2xl bg-white px-4 py-2.5 text-sm font-bold shadow-lg"
            >
              <Mic className="h-4 w-4 text-red-500" />
              Listening…
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ---------- Stats band ---------- */}
      <section className="border-y border-gray-200 bg-gray-50">
        <div className="mx-auto grid max-w-6xl grid-cols-2 gap-6 px-4 py-10 text-center md:grid-cols-4">
          {[
            ['35+', 'Bite-sized lessons'],
            ['3', 'Question types — MCQ, written, spoken'],
            ['24/7', 'AI tutor availability'],
            ['5 min', 'Is all a lesson takes'],
          ].map(([stat, label]) => (
            <motion.div key={label} {...fadeUp}>
              <p className="text-3xl font-extrabold text-emerald-600">{stat}</p>
              <p className="mt-1 text-sm font-medium text-gray-500">{label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ---------- Features ---------- */}
      <section id="features" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-20">
        <motion.div {...fadeUp} className="mb-12 text-center">
          <h2 className="mb-3 text-3xl font-extrabold md:text-4xl">
            Everything a great tutor does.{' '}
            <span className="text-emerald-600">Available always.</span>
          </h2>
          <p className="mx-auto max-w-2xl text-lg text-gray-500">
            Built for university life — short, smart, and personal. Here's what
            makes LinguaDepth different from a textbook.
          </p>
        </motion.div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <motion.div
              key={feature.title}
              {...fadeUp}
              className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="mb-4 inline-flex rounded-2xl bg-emerald-50 p-3">
                <feature.icon className="h-7 w-7 text-emerald-600" />
              </div>
              <h3 className="mb-2 text-lg font-bold">{feature.title}</h3>
              <p className="text-gray-500">{feature.text}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ---------- How it works ---------- */}
      <section id="how-it-works" className="scroll-mt-20 bg-gray-50 py-20">
        <div className="mx-auto max-w-6xl px-4">
          <motion.div {...fadeUp} className="mb-12 text-center">
            <h2 className="mb-3 text-3xl font-extrabold md:text-4xl">
              From "How far?" to fluent.{' '}
              <span className="text-emerald-600">In three steps.</span>
            </h2>
          </motion.div>
          <div className="grid gap-8 md:grid-cols-3">
            {STEPS.map((step, i) => (
              <motion.div key={step.title} {...fadeUp} className="relative text-center">
                <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500 text-white shadow-md">
                  <step.icon className="h-8 w-8" />
                </div>
                <span className="mb-2 block text-sm font-extrabold uppercase tracking-wide text-emerald-600">
                  Step {i + 1}
                </span>
                <h3 className="mb-2 text-xl font-bold">{step.title}</h3>
                <p className="mx-auto max-w-xs text-gray-500">{step.text}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------- Testimonials ---------- */}
      <section id="testimonials" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-20">
        <motion.div {...fadeUp} className="mb-12 text-center">
          <h2 className="mb-3 text-3xl font-extrabold md:text-4xl">
            Students are already <span className="text-emerald-600">levelling up.</span>
          </h2>
        </motion.div>
        <div className="grid gap-6 md:grid-cols-3">
          {TESTIMONIALS.map((t) => (
            <motion.figure
              key={t.name}
              {...fadeUp}
              className="flex flex-col rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
            >
              <Quote className="mb-4 h-7 w-7 text-emerald-200" />
              <blockquote className="flex-1 text-gray-700">"{t.text}"</blockquote>
              <figcaption className="mt-5 border-t border-gray-100 pt-4">
                <p className="font-bold">{t.name}</p>
                <p className="text-sm text-gray-500">{t.role}</p>
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </section>

      {/* ---------- CTA ---------- */}
      <section className="px-4 pb-20">
        <motion.div
          {...fadeUp}
          className="mx-auto max-w-4xl rounded-3xl bg-emerald-500 px-8 py-14 text-center text-white shadow-xl"
        >
          <h2 className="mb-3 text-3xl font-extrabold md:text-4xl">
            Your English. Your pace. Your level.
          </h2>
          <p className="mx-auto mb-8 max-w-xl text-lg text-emerald-50">
            Join now, take the 10-question placement quiz, and get a learning
            path built for you — before your next lecture starts.
          </p>
          <Link
            to="/auth?mode=register"
            className="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-4 text-lg font-bold text-emerald-600 shadow-md transition-transform hover:scale-105"
          >
            Create Your Free Account
            <ArrowRight className="h-5 w-5" />
          </Link>
        </motion.div>
      </section>

      {/* ---------- Footer ---------- */}
      <footer className="border-t border-gray-200 bg-gray-50">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 py-8 md:flex-row">
          <div className="flex items-center gap-2">
            <Globe2 className="h-6 w-6 text-emerald-500" />
            <span className="font-extrabold">
              Lingua<span className="text-emerald-600">Depth</span>
            </span>
          </div>
          <p className="text-sm text-gray-500">
            Adaptive English learning for Nigerian university students.
          </p>
          <div className="flex gap-5 text-sm font-semibold text-gray-500">
            <a href="#features" className="hover:text-gray-900">Features</a>
            <a href="#how-it-works" className="hover:text-gray-900">How it works</a>
            <Link to="/auth" className="hover:text-gray-900">Sign In</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
