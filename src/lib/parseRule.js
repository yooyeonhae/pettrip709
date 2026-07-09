// ============================================================
// KorPetTourService는 "소형견 한정, 이동장 필수, 10kg 이하" 같은
// 자연어 텍스트만 제공하고, 판정 엔진이 쓸 구조화된 값(허용 종류/크기/무게/준비물)은
// 주지 않는다. 실 API 연동 시 이 파서가 원문에서 규칙을 최대한 추출하고,
// 애매해서 못 뽑아낸 부분은 비워둔 채 "정보 없음, 방문 전 재확인 권장"으로 넘어간다.
// mock 데이터는 이미 parsedRule을 갖고 있으므로 이 파서를 타지 않는다.
// ============================================================

const SIZE_KEYWORDS = [
  { size: 'small', words: ['소형'] },
  { size: 'medium', words: ['중형'] },
  { size: 'large', words: ['대형'] },
]

const ITEM_KEYWORDS = [
  { item: 'carrier', words: ['이동장', '켄넬', '가방'] },
  { item: 'leash', words: ['목줄', '리드줄'] },
  { item: 'muzzle', words: ['입마개'] },
  { item: 'wasteBag', words: ['배변봉투', '배변 봉투'] },
]

function extractWeight(text) {
  const match = text.match(/(\d+(?:\.\d+)?)\s*kg\s*(이하|미만)/)
  return match ? Number(match[1]) : null
}

function extractSizes(text) {
  const sizes = SIZE_KEYWORDS.filter(({ words }) => words.some((w) => text.includes(w))).map(
    (s) => s.size,
  )
  return sizes
}

function extractItems(text) {
  return ITEM_KEYWORDS.filter(({ words }) => words.some((w) => text.includes(w))).map(
    (i) => i.item,
  )
}

function extractAnimals(text) {
  const animals = []
  if (text.includes('불가') && !text.includes('견') && !text.includes('묘') && !text.includes('고양이')) {
    return [] // "동반 불가" 같은 전면 불가 문구
  }
  if (text.includes('견') || text.includes('강아지') || text.includes('개')) animals.push('dog')
  if (text.includes('묘') || text.includes('고양이')) animals.push('cat')
  if (text.includes('소동물') || text.includes('기타')) animals.push('etc')
  return animals
}

/**
 * rawRule(KorPetTourService 원문 필드 묶음)에서 구조화된 parsedRule을 추출한다.
 * 확실하게 추출되지 않는 값은 null/빈 배열로 두어 "정보 없음" 처리가 되도록 한다.
 */
export function parseRuleFromRaw(rawRule) {
  if (!rawRule) return null

  const combinedText = [
    rawRule.allowedAnimalsText,
    rawRule.accompanyTypeText,
    rawRule.needMatterText,
  ]
    .filter(Boolean)
    .join(' ')

  if (!combinedText.trim()) return null

  const fullyBanned = /동반\s*불가|출입\s*제한|입장\s*불가/.test(combinedText)

  return {
    allowedAnimals: fullyBanned ? [] : extractAnimals(combinedText),
    allowedSizes: fullyBanned ? [] : extractSizes(combinedText),
    maxWeight: fullyBanned ? 0 : extractWeight(combinedText),
    requiredItems: fullyBanned ? [] : extractItems(combinedText),
  }
}
