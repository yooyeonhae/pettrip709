import { JUDGE_LEVEL, PET_ITEMS, PET_SIZES, PET_TYPES } from './constants'

const typeLabel = (v) => PET_TYPES.find((t) => t.value === v)?.label ?? v
const sizeLabel = (v) => PET_SIZES.find((s) => s.value === v)?.label ?? v
const itemLabel = (v) => PET_ITEMS.find((i) => i.value === v)?.label ?? v

/**
 * 반려동물 프로필과 장소의 동반 규정(parsedRule)을 대조해
 * 🟢가능 / 🟡조건부 가능 / 🔴불가 3단계로 판정한다.
 *
 * 판정 우선순위 (하나라도 걸리면 즉시 그 사유로 "불가" 확정):
 *   1. 동물 종류가 허용 목록에 있는가
 *   2. 무게가 제한 이하인가
 *   3. 크기 구분이 허용 범위인가
 * 위 세 가지를 모두 통과했다면:
 *   4. 필수 준비물을 모두 보유했는가 → 미충족 시 "조건부 가능" (준비물은 현장에서 보완 가능하므로)
 * 전부 통과하면 "가능"
 */
export function judgeEntry(pet, rule) {
  if (!rule) {
    return {
      level: JUDGE_LEVEL.WARN,
      reason: '정보 없음, 방문 전 재확인 권장',
      missingItems: [],
      noData: true,
    }
  }

  const { allowedAnimals = [], allowedSizes = [], maxWeight = null, requiredItems = [] } = rule

  // 1. 동물 종류
  if (!allowedAnimals.includes(pet.type)) {
    return {
      level: JUDGE_LEVEL.NO,
      reason: `이 장소는 ${typeLabel(pet.type)} 동반이 불가능해요.`,
      missingItems: [],
    }
  }

  // 2. 무게
  const weight = Number(pet.weight)
  if (maxWeight != null && !Number.isNaN(weight) && weight > maxWeight) {
    return {
      level: JUDGE_LEVEL.NO,
      reason: `무게 제한 ${maxWeight}kg를 초과해요. (우리 아이 ${weight}kg)`,
      missingItems: [],
    }
  }

  // 3. 크기
  if (allowedSizes.length > 0 && !allowedSizes.includes(pet.size)) {
    return {
      level: JUDGE_LEVEL.NO,
      reason: `${sizeLabel(pet.size)} 사이즈는 동반이 어려워요. (허용: ${allowedSizes
        .map(sizeLabel)
        .join(', ')})`,
      missingItems: [],
    }
  }

  // 4. 준비물 (보완 가능한 조건 → 조건부 가능)
  const missingItems = requiredItems.filter((i) => !pet.items?.includes(i))
  if (missingItems.length > 0) {
    return {
      level: JUDGE_LEVEL.WARN,
      reason: `필요 준비물: ${missingItems.map(itemLabel).join(', ')}`,
      missingItems,
    }
  }

  return {
    level: JUDGE_LEVEL.OK,
    reason: '모든 조건을 충족했어요!',
    missingItems: [],
  }
}

/**
 * 모호한 규정 원문(rawRule)을 우리 아이 프로필 기준으로 사람 친화적인 문장으로 번역한다.
 * 예) "소형견 한정, 이동장 필수, 10kg 이하" + 포메 4kg
 *     → "우리 아이(포메 4kg)는 소형·10kg 이하 조건 충족! 단, 이동장이 필요해요."
 */
export function buildInterpretation(pet, rule, judgement) {
  const petDesc = `${pet.breed ? pet.breed : typeLabel(pet.type)} ${pet.weight ? `${pet.weight}kg` : ''}`.trim()

  if (judgement.noData) {
    return `이 장소의 반려동물 동반 규정 정보가 아직 등록되어 있지 않아요. ${judgement.reason}`
  }

  if (judgement.level === JUDGE_LEVEL.NO) {
    return `우리 아이(${petDesc})는 ${judgement.reason}`
  }

  if (judgement.level === JUDGE_LEVEL.WARN) {
    const conditions = []
    if (rule?.allowedSizes?.length) conditions.push(`${rule.allowedSizes.map(sizeLabel).join('·')} 사이즈`)
    if (rule?.maxWeight != null) conditions.push(`${rule.maxWeight}kg 이하`)
    const conditionText = conditions.length ? `${conditions.join(', ')} 조건 충족! ` : ''
    return `우리 아이(${petDesc})는 ${conditionText}단, ${judgement.missingItems
      .map(itemLabel)
      .join(', ')}이(가) 필요해요.`
  }

  return `우리 아이(${petDesc})는 이 장소의 모든 동반 조건을 충족해서 바로 입장할 수 있어요!`
}
