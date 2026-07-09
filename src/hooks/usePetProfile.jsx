import { createContext, useContext, useMemo, useState } from 'react'

// 반려동물 프로필 초기값. localStorage를 쓰지 않고 세션 동안만 유지되는 메모리 상태로 관리한다.
export const EMPTY_PROFILE = {
  type: '',        // 'dog' | 'cat' | 'etc'
  breed: '',        // 견종/묘종 (선택)
  weight: '',       // kg
  size: '',         // 'small' | 'medium' | 'large'
  items: [],        // 'carrier' | 'leash' | 'muzzle' | 'wasteBag'
  vaccinated: false,
  name: '',
}

const PetProfileContext = createContext(null)

export function PetProfileProvider({ children }) {
  const [profile, setProfile] = useState(EMPTY_PROFILE)
  const [onboarded, setOnboarded] = useState(false)

  const value = useMemo(
    () => ({
      profile,
      setProfile,
      onboarded,
      setOnboarded,
      resetProfile: () => {
        setProfile(EMPTY_PROFILE)
        setOnboarded(false)
      },
    }),
    [profile, onboarded],
  )

  return <PetProfileContext.Provider value={value}>{children}</PetProfileContext.Provider>
}

export function usePetProfile() {
  const ctx = useContext(PetProfileContext)
  if (!ctx) throw new Error('usePetProfile은 PetProfileProvider 내부에서만 사용할 수 있습니다.')
  return ctx
}
