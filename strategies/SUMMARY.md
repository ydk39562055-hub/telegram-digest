# 반응형 추세추종 전략 — 통합 정리

- 작성일: 2026-09-28
- 상세 규칙은 같은 폴더의 개별 파일 참고 (01~06, etf_01~03)
- 이 문서만 읽어도 결정·구현을 시작할 수 있도록 전체를 합친 버전

---

## 0. 한눈에 보기

| 역할 | 전략 | 비중 | 상태 |
|---|---|---|---|
| **핵심** | HAA 또는 BAA (백테스트로 선택) | 80~90% | 1순위 구현 |
| **위성** | 스타인 슈퍼스톡 + 미너비니·와인스타인 보조 기준 (반자동) | 10~20% | 2순위 구현 |
| 기준선 | 와인스타인 30주선, S&P 500 매수 후 보유 | — | 비교용 |
| 다음 단계 | 클레노우, 사상 최고가 추세추종, 산업 추세추종 | — | 핵심 안정 후 검토 |
| 제외 | 벤스도프, 닉 라지, 단기 평균회귀 전부(코너스 등) | — | — |
| 대기 | 쿨라매기 | — | 자료 수령 후 판정 |

**연결 규칙:** 핵심 ETF 전략이 방어 모드면 위성은 신규 매수 중단.

**정해야 할 것 2가지:**
1. 최대낙폭 상한 (추천 25%)
2. 위성 시장: 미국 소형주 / 한국 (한국이면 내부자 매수 = DART, 가격·유통주 기준 재설정)

---

## 1. 목표와 전제

- 목표: 시장 상황이 바뀌면 반응하는 **추세추종 자동화(반자동화)**
- 남는 효과는 "지수 초과수익"이 아니라 **큰 하락에서 손실 축소 + 규칙 유지**
- 공개 전략은 발표 후 수익이 줄어듦 (McLean·Pontiff 2016: 평균 58% 감소). 백테스트 CAGR은 **절반으로 나눠 기대**
- 낙폭 방어는 수익보다 잘 살아남음 (Faber GTAA: 발표 후 CAGR 11.7% → 6.05%, 낙폭 9.5% → 11.7%)
- 추세추종 승률은 30~45%가 정상. 손익비로 번다. 승률 높은 전략(60~85%)은 평균회귀이고 반응형과 정반대 → 제외
- 규칙이 복잡할수록 표본 내 성적은 좋아지고 발표 후 성적은 나빠짐 (단순한 Faber > 복잡한 GEM)

## 2. 전략 선별 기준

1. **규칙이 숫자로 공개**돼 자동화 가능한가 (재량 부분은 사람 판단으로 분리)
2. **같은 조건에서 직접 백테스트** (기간·비용·다음 날 시가 체결 동일). 남의 숫자는 구현 검증용으로만
3. **최대낙폭 상한 초과 → 탈락**, 남은 것은 **CAGR 순**
4. **발표 이후 구간**에서 순위 재확인
5. 같은 계열이면 **가장 검증된 하나만** 남김

---

## 3. 핵심 후보 — ETF 자산배분

### HAA — Hybrid Asset Allocation (Keller·Keuning 2023)

| 항목 | 내용 |
|---|---|
| 경고 | TIP 1개 |
| 공격 8개 | SPY, IWM, VEA, VWO, VNQ, DBC, IEF, TLT |
| 방어 2개 | BIL, IEF |
| 모멘텀 | 13612U = (1+3+6+12개월 수익률) / 4 |
| 규칙 | TIP ≤ 0 → BIL/IEF 중 나은 쪽 100%. TIP > 0 → 공격 상위 4개 각 25%, 그중 모멘텀 ≤ 0인 몫은 BIL/IEF 중 나은 쪽 |
| 주기 | 월말 판단, 다음 거래일 체결 |
| 성과 | 1971~2022 저자 백테스트(비용 제외). 발표 후 약 3년 |
| 약점 | 단일 경고 자산 의존, TIP 0 근처 왕복 |

### BAA — Bold Asset Allocation (Keller 2022)

| 항목 | 내용 |
|---|---|
| 경고 4개 | SPY, VWO, VEA, BND — **하나라도** 음수면 방어 (B=1) |
| 공격 12개 (G12) | SPY, QQQ, IWM, VGK, EWJ, VWO, VNQ, DBC, GLD, TLT, HYG, LQD → 상위 6개 각 1/6 |
| 방어 7개 | TIP, DBC, BIL, IEF, TLT, LQD, BND → 상위 3개 각 1/3, BIL보다 약하면 BIL |
| 모멘텀 | 경고: 13612W = (12×r1 + 4×r3 + 2×r6 + r12)/4 (빠름) / 선택: SMA(12) = 가격 ÷ 최근 13개 월말 평균 − 1 (느림) |
| 성과 | 1970.12~2022.6 연 20%+, 낙폭 15% 이하 (표본 내, 비용 제외). 발표 후 약 4년 |
| 약점 | 방어 모드 시간이 긺, 1개월 수익률에 휘둘림 |

### HAA vs BAA 비교 포인트

- 방어 모드 비율, 공격↔방어 전환 횟수
- **2022년 구간 낙폭** (주식·채권 동반 하락 — GEM이 무너진 해)
- 발표 후 월별 보유가 Allocate Smartly / TuringTrader 공개 보유와 일치하는지 (불일치 = 구현 오류)

---

## 4. 위성 — 스타인 슈퍼스톡 (반자동)

### 원본 기준 (Jesse Stine, *Insider Buy Superstocks*, 2013)

- 돌파 5조건: 주가 < $15 (최적 $4~15), 강한 바닥 돌파, 30주선 상향 돌파, 막대한 주간 거래량, 가파른 각도
- 펀더멘털: 블록버스터 실적 + 쉬운 comps, 연환산 PER ≤ 10, 부채 적음, 유통주 < 1,000만 주, 시총 < $1억, 공매도 적음, 내부자 공개시장 매수
- 보유: 매직 라인(종목별 10~16주선)에서 눌림 매수, 주봉 이탈 시 청산
- 매도: 기록적 주간 변동폭, 30주선 과이격, 강할 때 판다
- 150배 = 순자산 90%+를 1~2종목 + 마진. 본인도 비권장. 출판 후 실적 없음

### 우리 버전 (모호한 기준을 숫자로 교체)

| 단계 | 기준 | 담당 |
|---|---|---|
| 1. 기본 | 주가 $4~15, 시총 < $1억, 유통주 < 1,000만 주, 연환산 PER ≤ 10, 부채 상한 | 자동 |
| 2. 내부자 | 최근 6개월 공개시장 순매수 > 0 (SEC Form 4 / 한국 DART) | 자동 |
| 3. 추세 | 미너비니 템플릿 1~5번: 주가 > 50일 > 150일 > 200일선, 200일선 1개월+ 상승 | 자동 |
| 4. 돌파 | 와인스타인: 20주 박스(폭 ≤ 30%) 상단을 주간 종가로 돌파 + 거래량 ≥ 직전 10주 평균 2배 + 30주선 상승 | 자동 |
| 5. 판단 | 실적 지속성, 내부자 매수 의미, 차트 | 사람 |
| 6. 매수 | 종목당 2~3%, 마진 없음, 위성 전체 10~20% | 사람 |
| 7. 청산 | 주간 종가 30주선 이탈 알림, 30주선 과이격 시 분할 매도 알림 | 자동 알림 → 사람 |
| 연결 | 핵심 ETF 방어 모드면 신규 매수 중단 | 자동 |

- 필터 값은 정하면 **6개월 고정**. 후보 수가 아니라 후보의 이후 성과로 평가
- 매수·미매수 이유를 한 줄씩 기록 → 스크리너 성과와 내 판단 성과를 분리 측정

---

## 5. 기준선

| 전략 | 규칙 |
|---|---|
| 와인스타인 30주선 | 30주선 상승 + 주가 위 = 2단계 보유, 주간 종가 30주선 이탈 = 청산 |
| S&P 500 보유 | 매수 후 보유 |

---

## 6. 다음 단계 후보 (핵심 안정 후)

| 전략 | 규칙 요약 | 근거 | 보류 이유 |
|---|---|---|---|
| **클레노우** Stocks on the Move (2015) | S&P 500, 90일 회귀기울기×R² 상위 20%, 100일선·15% 갭 제외, ATR 비중(계좌×0.1%/ATR20), 지수 200일선 아래면 신규 매수만 중단, 주 1회 | 재현 다수 (CAGR 9~15%, 결과 편차 큼), 2015년 −0.2% | 과거 시점 구성종목 데이터 필요 |
| **사상 최고가 추세추종** (Zarattini·Pagani·Wilcox 2024) | 사상 최고가 경신 시 매수, ATR 추적손절 | 1991~2024 CAGR ~15%, 샤프 0.85, 낙폭 32% (시장 55%). 원 논문 2005 → **발표 후 20년 검증**. 이익은 매매 7% 미만에서 | 낙폭 32% > 25% 상한, 계좌 $1M 미만은 비용 문제 → 회전율 제어 필요 |
| **산업 추세추종** (Zarattini·Antonacci 2024) | 48개 산업, 돈치안 20일 또는 켈트너(20 EMA + 1.4 ATR) 돌파 진입, 40일 아래선 래칫 손절, 변동성 역가중 | 1926~2024 연 18.2%, 샤프 1.39. 2025 CMT Dow Award | 재검증 논문이 한계 지적, 일 단위 매매, 섹터 ETF 이식 필요 |

---

## 7. 제외 목록과 이유

| 전략 | 이유 |
|---|---|
| 벤스도프 Weekly Rotation / LTHM | 클레노우와 구조 동일. 저자의 낮은 낙폭은 평균회귀·숏 결합 덕분 |
| 닉 라지 Weekend Trend Trader | 20주 신고가 + ROC>30%, 시장 상태별 40%/10% 추적손절, MAR 1.16. 같은 원리를 사상 최고가 논문이 더 강하게 검증 |
| 미너비니 (단독) | VCP 진입이 재량 → 템플릿만 위성 필터로 사용 |
| 코너스 RSI(2)·Double 7s | 단기 평균회귀. Double 7: 승률 82.5%지만 CAGR 6.3%, 낙폭 33%, 이익 대부분 2010년 이전 |
| 듀얼 모멘텀 GEM | 2010년 이후 지수 대비 연 −4.8%p, 2022년 채권 피신 중 최대 낙폭 → HAA/BAA로 대체 |
| 다바스, 그린블랫 | 역사적 참고 / 가치 전략(추세 아님) |

---

## 8. 구현 순서 (로컬)

1. **데이터:** ETF 월말 총수익 가격 (Yahoo Finance 등 무료). HAA 12개 + BAA 23개 티커, 가능한 가장 긴 기간
2. **HAA·BAA 백테스트:** 월말 신호 → 다음 거래일 시가 체결, 비용 반영, 발표 전/후 구간 분리, 2022년 별도
3. **검증:** 최근 월별 보유를 Allocate Smartly / TuringTrader / quantist와 대조
4. **핵심 선택:** 낙폭 상한 통과 + CAGR 높은 쪽
5. **월간 신호 봇:** 기존 텔레그램 다이제스트 인프라로 매월 말 "현재 → 권고 보유" 발송
6. **스타인 스크리너:** 주 1회 후보 체크리스트 발송, 매수 판단 기록 기능
7. **6개월 운용 후** 다음 단계 후보 검토

---

## 9. 출처

- McLean·Pontiff (2016) — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2156623
- HAA — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4346906
- BAA — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4166845
- Allocate Smartly HAA/BAA — https://allocatesmartly.com/hybrid-asset-allocation/ , https://allocatesmartly.com/bold-asset-allocation/
- quantist BAA (한국어) — https://quantist.co.kr/baa_pages
- Faber GTAA 표본 외 — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5230603
- GEM 재현 — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7427878
- Stine 책 — https://www.goodreads.com/book/show/18012667-insider-buy-superstocks
- 미너비니 템플릿 — https://www.chartmill.com/documentation/stock-screener/technical-analysis-trading-strategies/496-Mark-Minervini-Trend-Template-A-Step-by-Step-Guide-for-Beginners
- 와인스타인 — https://traderlion.com/trading-strategies/stage-analysis/
- 클레노우 — https://raposa.trade/blog/how-to-follow-the-crowd-a-complete-momentum-trading-strategy/ , https://github.com/skyte/momentum
- 사상 최고가 추세추종 — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5084316
- 산업 추세추종 — https://papers.ssrn.com/sol3/Delivery.cfm/4857230.pdf?abstractid=4857230&mirid=1 , 재검증 https://arxiv.org/html/2412.14361v2
- 벤스도프 구현 — https://github.com/fbertram/TuringTrader/blob/develop/BooksAndPubs/Bensdorp_30MinStockTrader.cs
- 라지 — https://www.quantifiedstrategies.com/weekend-trend-trader-trading-strategy/
- Double 7 — https://www.quantifiedstrategies.com/larry-connors-double-seven-strategy-does-it-still-work/
