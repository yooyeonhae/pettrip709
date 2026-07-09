import { MOCK_PLACES } from '../data/mockPlaces'
import {
  COMMON_PARAMS,
  KOR_SERVICE,
  NO_DATA_NOTICE,
  PET_FIELDS,
  PET_TOUR_SERVICE,
  TOUR_API_KEY,
  USE_MOCK,
} from './constants'
import { parseRuleFromRaw } from './parseRule'

function mockDelay(ms = 300) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// 두 좌표 사이의 거리(km, 하버사인 공식) - "내 주변" 정렬용
function distanceKm(a, b, c, d) {
  const R = 6371
  const dLat = ((c - a) * Math.PI) / 180
  const dLng = ((d - b) * Math.PI) / 180
  const s =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((a * Math.PI) / 180) * Math.cos((c * Math.PI) / 180) * Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(s), Math.sqrt(1 - s))
}

/**
 * 장소 목록 조회.
 * - region: 시·도 코드 ('' = 전체)
 * - keyword: 검색어
 * - near: { lat, lng } 지정 시 거리순 정렬 ("내 주변")
 */
export async function getPlaces({ region = '', keyword = '', near = null } = {}) {
  if (USE_MOCK) {
    await mockDelay()
    let list = MOCK_PLACES.filter((p) => (region ? p.region === region : true))
    if (keyword.trim()) {
      const kw = keyword.trim().toLowerCase()
      list = list.filter(
        (p) => p.name.toLowerCase().includes(kw) || p.address.toLowerCase().includes(kw),
      )
    }
    if (near) {
      list = [...list].sort(
        (a, b) =>
          distanceKm(near.lat, near.lng, a.lat, a.lng) -
          distanceKm(near.lat, near.lng, b.lat, b.lng),
      )
    }
    return list
  }

  // ---- 실 API 연동 (KorService2: 지역/키워드 기반 장소 목록) ----
  const endpoint = keyword.trim() ? KOR_SERVICE.SEARCH_KEYWORD : KOR_SERVICE.AREA_BASED_LIST
  const params = new URLSearchParams({
    ...COMMON_PARAMS,
    serviceKey: TOUR_API_KEY,
    numOfRows: '30',
    pageNo: '1',
    arrange: 'A',
    ...(region ? { areaCode: region } : {}),
    ...(keyword.trim() ? { keyword } : {}),
  })

  try {
    const res = await fetch(`${endpoint}?${params.toString()}`)
    if (!res.ok) throw new Error(`TourAPI 응답 오류: ${res.status}`)
    const json = await res.json()
    const items = json?.response?.body?.items?.item ?? []
    const list = Array.isArray(items) ? items : [items]

    // 장소별로 반려동물 동반 규정을 detailPetTour로 조회해 병합한다.
    const withPetInfo = await Promise.all(
      list.map(async (item) => {
        const petInfo = await getPetTourInfo(item.contentid)
        return normalizePlace(item, petInfo)
      }),
    )
    return withPetInfo
  } catch (err) {
    console.error('getPlaces 실패, mock 데이터로 대체합니다.', err)
    return MOCK_PLACES
  }
}

/**
 * 특정 장소(contentId)의 반려동물 동반 규정 상세 조회 (KorPetTourService.detailPetTour)
 * mock 모드에서는 MOCK_PLACES에서 contentId로 조회해 동일한 형태로 반환한다.
 */
export async function getPetTourInfo(contentId) {
  if (USE_MOCK) {
    await mockDelay(150)
    const place = MOCK_PLACES.find((p) => p.contentId === contentId || p.id === contentId)
    if (!place) return null
    return { rawRule: place.rawRule, parsedRule: place.parsedRule }
  }

  const params = new URLSearchParams({
    ...COMMON_PARAMS,
    serviceKey: TOUR_API_KEY,
    contentId,
  })

  try {
    const res = await fetch(`${PET_TOUR_SERVICE.DETAIL_PET_TOUR}?${params.toString()}`)
    if (!res.ok) throw new Error(`KorPetTourService 응답 오류: ${res.status}`)
    const json = await res.json()
    const item = json?.response?.body?.items?.item
    const data = Array.isArray(item) ? item[0] : item
    if (!data) return { rawRule: null, parsedRule: null, noData: true }

    const rawRule = {
      allowedAnimalsText: data[PET_FIELDS.ALLOWED_ANIMALS] || NO_DATA_NOTICE,
      accompanyTypeText: data[PET_FIELDS.ACCOMPANY_TYPE] || NO_DATA_NOTICE,
      needMatterText: data[PET_FIELDS.NEED_MATTER] || NO_DATA_NOTICE,
      furnishedItemsText: data[PET_FIELDS.FURNISHED_ITEMS] || NO_DATA_NOTICE,
      purchaseItemsText: data[PET_FIELDS.PURCHASE_ITEMS] || NO_DATA_NOTICE,
      rentalItemsText: data[PET_FIELDS.RENTAL_ITEMS] || NO_DATA_NOTICE,
      accidentRiskText: data[PET_FIELDS.ACCIDENT_RISK] || NO_DATA_NOTICE,
      extraFeeText: data[PET_FIELDS.EXTRA_FEE] || NO_DATA_NOTICE,
    }

    return { rawRule, parsedRule: parseRuleFromRaw(rawRule) }
  } catch (err) {
    console.error('getPetTourInfo 실패', err)
    return { rawRule: null, parsedRule: null, noData: true }
  }
}

// KorService2 원본 item -> 앱 내부 place 모델로 변환
function normalizePlace(item, petInfo) {
  return {
    id: item.contentid,
    contentId: item.contentid,
    name: item.title || '이름 정보 없음',
    category: 'attraction',
    region: item.areacode || '',
    regionName: '',
    address: item.addr1 || NO_DATA_NOTICE,
    lat: Number(item.mapy) || 0,
    lng: Number(item.mapx) || 0,
    image: item.firstimage || '',
    rawRule: petInfo?.rawRule ?? null,
    parsedRule: petInfo?.parsedRule ?? null,
  }
}
