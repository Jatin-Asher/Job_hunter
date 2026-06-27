import { useAuthStore } from '@/lib/store'

export const useAuth = () => {
  const { user, isLoading, error, setUser, setLoading, setError, logout } = useAuthStore()

  return {
    user,
    isLoading,
    error,
    setUser,
    setLoading,
    setError,
    logout,
    isAuthenticated: !!user,
  }
}
