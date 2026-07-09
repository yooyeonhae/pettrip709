// ============================================================
// 한국관광공사 TourAPI 4.0 관련 상수
// 실제 서비스 연동 시 엔드포인트/파라미터/필드명이 바뀌어도
// 이 파일만 수정하면 되도록 모든 상수를 여기로 분리했다.
// (공공데이터포털 명세: https://www.data.go.kr 참고, 배포 전 최신 명세 재확인 필요)
// ============================================================

export const TOUR_API_BASE = 'https://apis.data.go.kr/B551011'

// 국문 관광정보 서비스 (KorService2)
export const KOR_SERVICE = {
  AREA_BASED_LIST: `${TOUR_API_BASE}/KorService2/areaBasedList2`,
  LOCATION_BASED_LIST: `${TOUR_API_BASE}/KorService2/locationBasedList2`,
  SEARCH_KEYWORD: `${TOUR_API_BASE}/KorService2/searchKeyword2`,
  DETAIL_COMMON: `${TOUR_API_BASE}/KorService2/detailCommon2`,
  DETAIL_IMAGE: `${TOUR_API_BASE}/KorService2/detailImage2`,
}

// 반려동물 동반여행 서비스 (KorPetTourService)
export const PET_TOUR_SERVICE = {
  AREA_BASED_LIST: `${TOUR_API_BASE}/KorPetTourService/areaBasedList`,
  DETAIL_PET_TOUR: `${TOUR_API_BASE}/KorPetTourService/detailPetTour`,
}

// 공통 호출 파라미터
export const COMMON_PARAMS = {
  MobileOS: 'ETC',
  MobileApp: 'PetTrip',
  _type: 'json',
}

// KorPetTourService detailPetTour 응답 필드명 (명세 변경 시 이 부분만 수정)
export const PET_FIELDS = {
  ALLOWED_ANIMALS: 'acmpyPsblCpam',   // 동반 가능 반려동물
  ACCOMPANY_TYPE: 'acmpyTypeCd',      // 동반 유형 (실내/실외 등)
  NEED_MATTER: 'acmpyNeedMtr',        // 동반 시 필요사항
  FURNISHED_ITEMS: 'relaFrnshPrdlst', // 구비 물품
  PURCHASE_ITEMS: 'relaPurcPrdlst',   // 구매 물품
  RENTAL_ITEMS: 'relaRntlPrdlst',     // 렌탈 물품
  ACCIDENT_RISK: 'relaAcdntRiskMtr',  // 사고대비 사항
  EXTRA_FEE: 'acmpyReqCst',           // 동반 요금
}

// 지역(시·도) 목록 - areaCode 기준 (TourAPI 표준 코드)
export const REGIONS = [
  { code: '', name: '전체' },
  { code: '1', name: '서울' },
  { code: '6', name: '부산' },
  { code: '4', name: '대구' },
  { code: '2', name: '인천' },
  { code: '5', name: '광주' },
  { code: '3', name: '대전' },
  { code: '7', name: '울산' },
  { code: '8', name: '세종' },
  { code: '31', name: '경기' },
  { code: '32', name: '강원' },
  { code: '33', name: '충북' },
  { code: '34', name: '충남' },
  { code: '35', name: '경북' },
  { code: '36', name: '경남' },
  { code: '37', name: '전북' },
  { code: '38', name: '전남' },
  { code: '39', name: '제주' },
]

// 반려동물 종류
export const PET_TYPES = [
  { value: 'dog', label: '강아지', emoji: '🐶' },
  { value: 'cat', label: '고양이', emoji: '🐱' },
  { value: 'etc', label: '기타', emoji: '🐾' },
]

// 크기 구분
export const PET_SIZES = [
  { value: 'small', label: '소형', desc: '~5kg' },
  { value: 'medium', label: '중형', desc: '5~15kg' },
  { value: 'large', label: '대형', desc: '15kg~' },
]

// 준비물 항목
export const PET_ITEMS = [
  { value: 'carrier', label: '이동장', emoji: '🧳' },
  { value: 'leash', label: '목줄', emoji: '🦮' },
  { value: 'muzzle', label: '입마개', emoji: '😷' },
  { value: 'wasteBag', label: '배변봉투', emoji: '💩' },
]

// 장소 카테고리
export const CATEGORIES = [
  { value: 'cafe', label: '카페/식당', emoji: '☕' },
  { value: 'attraction', label: '관광지', emoji: '🏞️' },
  { value: 'lodging', label: '숙소', emoji: '🏨' },
  { value: 'park', label: '공원/산책', emoji: '🌳' },
  { value: 'culture', label: '문화시설', emoji: '🖼️' },
]

// 판정 결과 레벨
export const JUDGE_LEVEL = {
  OK: 'ok',
  WARN: 'warn',
  NO: 'no',
}

export const JUDGE_META = {
  [JUDGE_LEVEL.OK]: { label: '가능', color: '#22c55e', emoji: '🟢' },
  [JUDGE_LEVEL.WARN]: { label: '조건부 가능', color: '#eab308', emoji: '🟡' },
  [JUDGE_LEVEL.NO]: { label: '불가', color: '#ef4444', emoji: '🔴' },
}

export const NO_DATA_NOTICE = '정보 없음, 방문 전 재확인 권장'

// 실 API 사용 여부: 키가 있고 강제 mock 모드가 아닐 때만 실 API 시도
export const USE_MOCK =
  import.meta.env.VITE_USE_MOCK === 'true' || !import.meta.env.VITE_TOUR_API_KEY

export const TOUR_API_KEY = import.meta.env.VITE_TOUR_API_KEY || ''
export const KAKAO_MAP_KEY = import.meta.env.VITE_KAKAO_MAP_KEY || ''
