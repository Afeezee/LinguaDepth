import { Link, useNavigate } from 'react-router-dom'
import { Flame, Globe2, LogOut, Shield, Star } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import LevelBadge from '../dashboard/LevelBadge'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="sticky top-0 z-40 border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/dashboard" className="flex items-center gap-2">
          <Globe2 className="h-7 w-7 text-emerald-500" />
          <span className="text-xl font-extrabold text-gray-900">
            Lingua<span className="text-emerald-600">Depth</span>
          </span>
        </Link>

        {user && (
          <div className="flex items-center gap-4">
            <span className="hidden items-center gap-1 text-sm font-semibold text-amber-600 sm:flex">
              <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
              {user.xp} XP
            </span>
            <span className="hidden items-center gap-1 text-sm font-semibold text-orange-600 sm:flex">
              <Flame className="h-4 w-4 fill-orange-400 text-orange-500" />
              {user.streak_days}
            </span>
            <LevelBadge level={user.level} />
            {user.is_admin && (
              <Link
                to="/admin"
                className="rounded-xl p-2 text-gray-500 hover:bg-gray-50 hover:text-emerald-600"
                title="Admin dashboard"
              >
                <Shield className="h-5 w-5" />
              </Link>
            )}
            <button
              onClick={handleLogout}
              className="rounded-xl p-2 text-gray-500 hover:bg-gray-50 hover:text-gray-900"
              title="Log out"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}
