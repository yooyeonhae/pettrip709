import { createContext, useContext, useMemo, useState } from 'react'

// 즐겨찾기(코스 담기) 목록도 세션 동안만 유지되는 메모리 상태로 관리한다.
const FavoritesContext = createContext(null)

export function FavoritesProvider({ children }) {
  const [favorites, setFavorites] = useState([]) // place 객체 배열

  const value = useMemo(
    () => ({
      favorites,
      isFavorite: (id) => favorites.some((f) => f.id === id),
      toggleFavorite: (place) =>
        setFavorites((prev) =>
          prev.some((f) => f.id === place.id)
            ? prev.filter((f) => f.id !== place.id)
            : [...prev, place],
        ),
      removeFavorite: (id) => setFavorites((prev) => prev.filter((f) => f.id !== id)),
    }),
    [favorites],
  )

  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>
}

export function useFavorites() {
  const ctx = useContext(FavoritesContext)
  if (!ctx) throw new Error('useFavorites는 FavoritesProvider 내부에서만 사용할 수 있습니다.')
  return ctx
}
