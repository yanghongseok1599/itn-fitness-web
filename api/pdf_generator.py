"""
인바디 수치 기반 맞춤 운동 루틴 PDF 생성기 (12페이지 완전판)
브라우저 인쇄용 HTML 생성 — WeasyPrint 불필요
"""
from datetime import date


def _safe_float(val, default=0.0):
    try:
        return float(val) if val not in (None, '', 'None') else default
    except (ValueError, TypeError):
        return default


def _safe_int(val, default=0):
    try:
        return int(float(val)) if val not in (None, '', 'None') else default
    except (ValueError, TypeError):
        return default


def _calc(member, inbody, goal):
    """모든 개인화 수치 계산"""
    weight    = _safe_float(inbody.get('weight'), 65)
    muscle    = _safe_float(inbody.get('muscle_mass'), 24)
    fat_mass  = _safe_float(inbody.get('body_fat_mass'), 18)
    fat_pct   = _safe_float(inbody.get('body_fat_pct'), 28)
    visceral  = _safe_int(inbody.get('visceral_fat_level'), 9)
    bmi       = _safe_float(inbody.get('bmi'), 23)
    score     = _safe_int(inbody.get('inbody_score'), 72)
    bmr       = _safe_int(inbody.get('bmr'), 1380)
    age       = _safe_int(member.get('age'), 35)

    tdee = round(bmr * 1.4)
    max_hr = 220 - age
    fat_burn_lo = round(max_hr * 0.60)
    fat_burn_hi = round(max_hr * 0.70)
    cardio_lo   = round(max_hr * 0.65)
    cardio_hi   = round(max_hr * 0.75)

    calorie_targets = {
        '체지방감소': round(tdee * 0.85),
        '근육증가':   round(tdee * 1.15),
        '체력향상':   tdee,
        '체형교정':   round(tdee * 0.95),
    }
    calorie_target = calorie_targets.get(goal, calorie_targets['체지방감소'])

    macro = {
        '체지방감소': (40, 35, 25),
        '근육증가':   (35, 45, 20),
        '체력향상':   (30, 50, 20),
        '체형교정':   (30, 50, 20),
    }.get(goal, (40, 35, 25))
    p_pct, c_pct, f_pct = macro
    protein_g = round(calorie_target * p_pct / 100 / 4)
    carb_g    = round(calorie_target * c_pct / 100 / 4)
    fat_g     = round(calorie_target * f_pct / 100 / 9)

    water_l = round(weight * 0.033 + 0.5, 1)

    intensity = {
        '체지방감소': {'rm_lo': 55, 'rm_hi': 65, 'rep_lo': 12, 'rep_hi': 15, 'rest': '45~60초', 'sets': '3세트'},
        '근육증가':   {'rm_lo': 70, 'rm_hi': 80, 'rep_lo': 8,  'rep_hi': 10, 'rest': '60~90초', 'sets': '3~4세트'},
        '체력향상':   {'rm_lo': 45, 'rm_hi': 55, 'rep_lo': 15, 'rep_hi': 20, 'rest': '30~45초', 'sets': '3세트'},
        '체형교정':   {'rm_lo': 50, 'rm_hi': 60, 'rep_lo': 12, 'rep_hi': 15, 'rest': '45~60초', 'sets': '3세트'},
    }.get(goal, {'rm_lo': 55, 'rm_hi': 65, 'rep_lo': 12, 'rep_hi': 15, 'rest': '45~60초', 'sets': '3세트'})

    rep_range  = f"{intensity['rep_lo']}~{intensity['rep_hi']}회"
    core_reps  = '15~20회' if goal in ('체지방감소', '체형교정') else '12~15회'
    rm_range   = f"{intensity['rm_lo']}~{intensity['rm_hi']}%"

    # 체형 분류
    if fat_pct >= 30:
        body_type = '마른비만형'
        body_desc = 'BMI는 정상이지만 체지방률이 높은 패턴. 복합운동 + 고횟수로 지방 연소를 극대화하세요.'
    elif fat_pct >= 25:
        body_type = '체지방 과다형'
        body_desc = '체지방 감소와 근육 유지를 동시에. 복합 관절 운동 중심으로 고횟수 진행하세요.'
    else:
        body_type = '근육 부족형'
        body_desc = '근육량 증가가 최우선. 무게 점진적 증가, 충분한 단백질 섭취 필수입니다.'

    # 3개월 목표
    target_fat_pct   = round(max(fat_pct - 4.7, 18), 1)
    target_fat_mass  = round(fat_mass - 3.7, 1)
    target_muscle    = round(muscle + 0.6, 1)
    target_visceral  = max(visceral - 3, 4)

    # 칼로리 소모 추정
    burn_weight  = round(weight * 0.085 * 40)   # 웨이트 40분
    burn_cardio  = round(weight * 0.12 * 20)    # 유산소 20분
    burn_warmup  = round(weight * 0.10 * 10)    # 워밍업 10분
    burn_lower   = burn_weight + burn_cardio + burn_warmup
    burn_upper   = burn_weight + round(weight * 0.12 * 20) + round(weight * 0.10 * 8)
    burn_weekly  = (burn_lower + burn_upper) * 2

    # 체중 기반 추정 중량 (간이식)
    squat_est    = round(weight * 0.7 / 10) * 10
    press_est    = round(weight * 0.4 / 5)  * 5
    pull_est     = round(weight * 0.5 / 5)  * 5

    today_str = date.today().strftime('%Y.%m.%d')

    return {
        'weight': weight, 'muscle': muscle, 'fat_mass': fat_mass, 'fat_pct': fat_pct,
        'visceral': visceral, 'bmi': bmi, 'score': score, 'bmr': bmr, 'age': age,
        'tdee': tdee, 'max_hr': max_hr,
        'fat_burn_lo': fat_burn_lo, 'fat_burn_hi': fat_burn_hi,
        'cardio_lo': cardio_lo, 'cardio_hi': cardio_hi,
        'calorie_target': calorie_target, 'protein_g': protein_g,
        'carb_g': carb_g, 'fat_g': fat_g,
        'p_pct': p_pct, 'c_pct': c_pct, 'f_pct': f_pct,
        'water_l': water_l,
        'rep_range': rep_range, 'core_reps': core_reps,
        'rm_range': rm_range, 'rest': intensity['rest'], 'sets': intensity['sets'],
        'body_type': body_type, 'body_desc': body_desc,
        'target_fat_pct': target_fat_pct, 'target_fat_mass': target_fat_mass,
        'target_muscle': target_muscle, 'target_visceral': target_visceral,
        'burn_lower': burn_lower, 'burn_upper': burn_upper, 'burn_weekly': burn_weekly,
        'squat_est': squat_est, 'press_est': press_est, 'pull_est': pull_est,
        'today_str': today_str,
        'goal': goal,
    }


def _css():
    return """
    @page { size: A4; margin: 14mm 16mm 16mm 16mm; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
      font-size: 10pt; color: #2a2a2a; background: white; line-height: 1.6;
    }
    .page {
      width: 100%; page-break-after: always;
      min-height: 247mm; display: flex; flex-direction: column;
      padding: 0;
    }
    .page:last-child { page-break-after: avoid; }
    /* 브라우저 미리보기용 여백 */
    @media screen {
      body { background: #e8eaed; padding: 10mm; }
      .page {
        background: white; margin-bottom: 8mm;
        padding: 14mm 16mm 16mm 16mm;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
        border-radius: 2px;
      }
    }
    .ph { /* page header */
      display: flex; justify-content: space-between; align-items: center;
      padding: 2.5mm 0 2.5mm; border-bottom: 0.6pt solid #d0d8e4;
      margin-bottom: 5mm; font-size: 8pt; color: #7a8898;
    }
    .ph strong { color: #1e3a5f; font-weight: 800; }
    .pf { /* page footer */
      margin-top: auto; padding-top: 3.5mm; border-top: 0.4pt solid #d8d4ce;
      font-size: 7pt; color: #9a9488; text-align: center;
    }
    /* ── main header block ── */
    .main-header {
      background: #1e3a5f; color: white;
      padding: 7mm 9mm; border-radius: 6pt;
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 5mm;
    }
    .mh-gym { font-size: 8.5pt; color: #a0bcd8; margin-bottom: 2mm; letter-spacing: 1px; }
    .mh-title { font-size: 20pt; font-weight: 900; line-height: 1.2; }
    .mh-title span { color: #f0a060; }
    .mh-sub { font-size: 8.5pt; color: #a0bcd8; margin-top: 2mm; }
    .score-val { font-size: 34pt; font-weight: 900; color: #f0a060; line-height: 1; text-align: right; }
    .score-sub { font-size: 8pt; color: #a0bcd8; text-align: right; margin-top: 1.5mm; }
    /* ── section title ── */
    .sec { font-size: 9.5pt; font-weight: 900; color: #1e4d7b; border-left: 3.5pt solid #c0603a;
           padding-left: 3.5mm; margin: 5mm 0 3mm; letter-spacing: 0.5px; }
    /* ── stat cards row ── */
    .stats { display: flex; gap: 2.5mm; margin-bottom: 4mm; }
    .stat {
      flex: 1; background: white; border-top: 3pt solid #1e4d7b;
      border-radius: 5pt; padding: 3mm 2mm; text-align: center;
      box-shadow: 0 1pt 4pt rgba(0,0,0,0.07); border: 0.6pt solid #e8e4de;
    }
    .stat.alert { border-top-color: #c0603a; }
    .stat.green { border-top-color: #4a7c59; }
    .stat-v { font-size: 13pt; font-weight: 900; color: #1e4d7b; white-space: nowrap; }
    .stat.alert .stat-v { color: #c0603a; }
    .stat.green .stat-v { color: #4a7c59; }
    .stat-l { font-size: 7.5pt; color: #8a8078; margin-top: 1.5mm; }
    .stat-t { font-size: 7pt; color: #c0603a; font-weight: 700; margin-top: 1mm; }
    /* ── info box ── */
    .pbox { background: #eef3f9; border: 0.8pt solid #c2d3e5; border-radius: 6pt;
            padding: 4mm 5mm; font-size: 9pt; line-height: 1.85; margin-bottom: 4mm; }
    .pbox strong { color: #1e4d7b; }
    .alert-box { background: #fdf0eb; border: 0.8pt solid #e0a080; border-radius: 6pt;
                 padding: 4mm 5mm; font-size: 9pt; line-height: 1.85; margin-bottom: 4mm; }
    .alert-box strong { color: #c0603a; }
    .green-box { background: #eef6f1; border: 0.8pt solid #8abf9a; border-radius: 6pt;
                 padding: 4mm 5mm; font-size: 9pt; line-height: 1.85; margin-bottom: 4mm; }
    .green-box strong { color: #4a7c59; }
    /* ── goal bars ── */
    .goal-row { display: flex; align-items: center; gap: 3mm; margin-bottom: 2.5mm; }
    .gl { font-size: 8.5pt; color: #5a554e; min-width: 20mm; font-weight: 600; }
    .gb-wrap { flex: 1; height: 7pt; background: #e2ded8; border-radius: 3.5pt; overflow: hidden; }
    .gb { height: 100%; border-radius: 3.5pt; }
    .gv { font-size: 8pt; font-weight: 700; color: #1e4d7b; min-width: 55mm; text-align: right; white-space: nowrap; }
    /* ── weekly schedule table ── */
    .week-table { width: 100%; border-collapse: collapse; font-size: 8.5pt; margin-bottom: 5mm; }
    .week-table thead tr { background: #1e3a5f; color: white; }
    .week-table th { padding: 3mm 2.5mm; text-align: center; font-weight: 700; }
    .week-table td { padding: 2.5mm 3mm; border-bottom: 0.4pt solid #e8e4de; vertical-align: top; }
    .week-table tr:nth-child(even) td { background: #f8f7f5; }
    .day-badge { display: inline-block; background: #1e4d7b; color: white; font-weight: 800;
                 font-size: 8.5pt; padding: 1mm 3mm; border-radius: 3pt; }
    .day-badge.rest { background: #8a9aaa; }
    .day-badge.opt  { background: #4a7c59; }
    /* ── benefit boxes ── */
    .benefit-row { display: flex; gap: 3.5mm; margin-bottom: 5mm; }
    .benefit { flex: 1; background: #eef3f9; border-radius: 6pt; padding: 4mm; text-align: center;
               border-top: 3pt solid #1e4d7b; }
    .benefit .b-icon { font-size: 16pt; }
    .benefit .b-title { font-size: 8.5pt; font-weight: 900; color: #1e3a5f; margin-top: 2mm; }
    .benefit .b-desc  { font-size: 8pt; color: #5a6a7a; margin-top: 1.5mm; line-height: 1.65; }
    /* ── tool section ── */
    .tool-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3.5mm; margin-bottom: 5mm; }
    .tool-box { background: white; border: 0.6pt solid #e2ded8; border-radius: 6pt; overflow: hidden; }
    .tool-head { background: #1e4d7b; color: white; padding: 2.5mm 4mm; font-size: 9pt; font-weight: 800; }
    .tool-body { padding: 3mm 4mm; }
    .tool-item { font-size: 8.5pt; padding: 1.5mm 0; border-bottom: 0.4pt solid #f0ece6; line-height: 1.65; }
    .tool-item:last-child { border-bottom: none; }
    .tool-item .num { color: #f0a060; font-weight: 800; margin-right: 1.5mm; }
    /* ── exercise cards ── */
    .ex-col-wrap { display: flex; gap: 4.5mm; margin-bottom: 5mm; }
    .ex-col { flex: 1; }
    .ex-col-head { background: #1e3a5f; color: white; padding: 3mm 4.5mm; font-size: 10pt; font-weight: 900;
                   border-radius: 5pt 5pt 0 0; }
    .ex-card { background: white; border: 0.6pt solid #e2ded8; border-bottom: none; padding: 3mm 4.5mm;
               display: flex; gap: 3mm; align-items: flex-start; }
    .ex-card:last-child { border-bottom: 0.6pt solid #e2ded8; border-radius: 0 0 5pt 5pt; }
    .ex-card:nth-child(odd) { background: #fafaf8; }
    .ex-cat { font-size: 7.5pt; font-weight: 700; padding: 1.5pt 4pt; border-radius: 2pt;
              white-space: nowrap; margin-top: 1pt; }
    .cat-warmup { background: #fdeee8; color: #c0603a; }
    .cat-weight { background: #e8eef6; color: #1e4d7b; }
    .cat-core   { background: #fef5e4; color: #9a6208; }
    .cat-finish { background: #eef6f1; color: #4a7c59; }
    .ex-name { font-size: 9.5pt; font-weight: 700; color: #2a2a2a; }
    .ex-detail { font-size: 8pt; color: #1e4d7b; font-weight: 600; margin-top: 1mm; }
    .ex-alt { font-size: 7.5pt; color: #7a8878; margin-top: 0.8mm; }
    /* ── metric cards ── */
    .metric-row { display: flex; gap: 3.5mm; margin-bottom: 5mm; }
    .metric { flex: 1; background: white; border: 0.6pt solid #e2ded8; border-radius: 6pt;
              text-align: center; padding: 4mm 2mm; border-top: 3pt solid #1e4d7b; }
    .metric.orange { border-top-color: #f0a060; }
    .metric.red    { border-top-color: #c0603a; }
    .metric.green  { border-top-color: #4a7c59; }
    .metric-v { font-size: 15pt; font-weight: 900; color: #1e4d7b; line-height: 1.1; }
    .metric.orange .metric-v { color: #c07020; }
    .metric.red    .metric-v { color: #c0603a; }
    .metric.green  .metric-v { color: #4a7c59; }
    .metric-l { font-size: 8pt; color: #7a8078; margin-top: 2mm; }
    /* ── generic table ── */
    .g-table { width: 100%; border-collapse: collapse; font-size: 8.5pt; margin-bottom: 5mm; }
    .g-table thead tr { background: #1e3a5f; color: white; }
    .g-table th { padding: 3mm 3.5mm; text-align: center; font-weight: 700; }
    .g-table td { padding: 2.5mm 3.5mm; border-bottom: 0.4pt solid #e8e4de; vertical-align: middle; }
    .g-table tr:nth-child(even) td { background: #f8f7f5; }
    .g-table td.center { text-align: center; }
    .g-table td.num { text-align: right; font-weight: 700; color: #1e4d7b; }
    /* ── HR boxes ── */
    .hr-row { display: flex; gap: 3.5mm; margin-bottom: 5mm; }
    .hr-box { flex: 1; border-radius: 6pt; padding: 4mm; text-align: center; }
    .hr-box.blue   { background: #eef3f9; border: 1pt solid #c2d3e5; }
    .hr-box.orange { background: #fdf2e8; border: 1pt solid #e8c090; }
    .hr-box.red    { background: #fdf0eb; border: 1pt solid #e0a080; }
    .hr-val { font-size: 16pt; font-weight: 900; color: #1e3a5f; line-height: 1; }
    .hr-box.orange .hr-val { color: #c07020; }
    .hr-box.red    .hr-val { color: #c0603a; }
    .hr-label { font-size: 7pt; color: #5a6a7a; margin-top: 1.5mm; }
    /* ── macro bars ── */
    .macro-row { display: flex; gap: 0; height: 10mm; border-radius: 5pt; overflow: hidden; margin-bottom: 3mm; }
    .macro-seg { display: flex; align-items: center; justify-content: center; font-size: 7.5pt; font-weight: 800; color: white; }
    /* ── meal timeline ── */
    .tl { margin-bottom: 4mm; }
    .tl-item { display: flex; gap: 0; margin-bottom: 1.5mm; border-radius: 4pt; overflow: hidden; border: 0.6pt solid #e2ded8; }
    .tl-left { min-width: 22mm; background: #1e4d7b; color: white; padding: 2.5mm 2mm; text-align: center; }
    .tl-left.green { background: #4a7c59; }
    .tl-left.terra { background: #c0603a; }
    .tl-left.gold  { background: #9a6208; }
    .tl-left.gray  { background: #6a7a88; }
    .tl-time { font-size: 7.5pt; font-weight: 900; }
    .tl-sub  { font-size: 6pt; color: rgba(255,255,255,0.75); margin-top: 0.5mm; }
    .tl-right { flex: 1; background: white; padding: 2.5mm 4mm; font-size: 7.5pt; line-height: 1.75; }
    /* ── water schedule ── */
    .water-row { display: flex; gap: 3mm; flex-wrap: wrap; margin-bottom: 4mm; }
    .water-item { flex: 1; min-width: 40mm; background: #eef3f9; border-radius: 5pt; padding: 2.5mm 3mm;
                  text-align: center; border-top: 2pt solid #1e4d7b; }
    .water-time { font-size: 7pt; font-weight: 700; color: #1e4d7b; }
    .water-amt  { font-size: 10pt; font-weight: 900; color: #1e3a5f; margin: 1mm 0; }
    .water-note { font-size: 6.5pt; color: #5a6a7a; }
    /* ── checklist ── */
    .check-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; margin-bottom: 4mm; }
    .check-box { background: white; border: 0.6pt solid #e2ded8; border-radius: 5pt; overflow: hidden; }
    .check-head { background: #1e3a5f; color: white; padding: 2.5mm 4mm; font-size: 8pt; font-weight: 800; }
    .check-item { display: flex; align-items: flex-start; gap: 2mm; padding: 1.5mm 4mm;
                  border-bottom: 0.4pt solid #f0ece6; font-size: 7.5pt; }
    .check-item:last-child { border-bottom: none; }
    .chk { width: 10pt; height: 10pt; border: 1pt solid #bbb; border-radius: 2pt; flex-shrink: 0; margin-top: 1pt; }
    /* ── habit cards ── */
    .habit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm; margin-bottom: 4mm; }
    .habit-card { background: white; border: 0.6pt solid #e2ded8; border-radius: 5pt; padding: 3mm 4mm;
                  border-left: 3pt solid #1e4d7b; }
    .habit-card.orange { border-left-color: #f0a060; }
    .habit-card.red    { border-left-color: #c0603a; }
    .habit-card.green  { border-left-color: #4a7c59; }
    .habit-num   { font-size: 8pt; font-weight: 900; color: #f0a060; }
    .habit-title { font-size: 8pt; font-weight: 800; color: #1e3a5f; margin: 0.5mm 0; }
    .habit-desc  { font-size: 7pt; color: #4a5568; line-height: 1.65; }
    /* ── tip box ── */
    .tip { background: #fdf6ec; border-left: 3pt solid #d4900a; padding: 3mm 4mm;
           font-size: 7.5pt; color: #5a440a; border-radius: 0 5pt 5pt 0; line-height: 1.8; margin-bottom: 4mm; }
    .tip strong { color: #9a6208; }
    /* ── closing motivation box ── */
    .motive { background: #1e3a5f; color: white; border-radius: 6pt; padding: 5mm 6mm;
              text-align: center; margin-bottom: 4mm; }
    .motive .m-title { font-size: 13pt; font-weight: 900; color: #f0a060; margin-bottom: 2mm; }
    .motive .m-body  { font-size: 8pt; color: #c0d4e8; line-height: 1.85; }
    """


def _page_header(page_num, page_title, name):
    return f"""<div class="ph">
      <strong>ITN 피트니스 · 동해</strong>&nbsp;&nbsp;|&nbsp;&nbsp;{name}님 맞춤 운동 루틴
      <span>{page_num}/12&nbsp;&nbsp;{page_title}</span>
    </div>"""


def _page_footer(today_str):
    return f"""<div class="pf">
      ITN 피트니스 · 동해 · Body Alignment Specialist &nbsp;|&nbsp; {today_str} &nbsp;|&nbsp; "사람이 먼저, 시스템이 지킨다"
    </div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 1 — 인바디 분석 & 주간 스케줄 오버뷰
# ═══════════════════════════════════════════════════════════
def _page1(c, member, inbody):
    name   = member.get('name', '회원')
    age    = member.get('age', '')
    gender = member.get('gender', '')
    measured = inbody.get('measured_at', date.today().isoformat())
    goal   = c['goal']
    goal_labels = {'체지방감소': '체지방 감소', '근육증가': '근육 증가', '체력향상': '체력 향상', '체형교정': '체형 교정'}
    goal_label = goal_labels.get(goal, goal)

    fat_bar = min(int((c['fat_pct'] - c['target_fat_pct']) / max(c['fat_pct'], 1) * 100 + 55), 88)
    vis_bar = min(int((c['visceral'] - c['target_visceral']) / max(c['visceral'], 1) * 100 + 48), 82)

    key_points = {
        '체지방감소': f'고횟수(12~15회) 복합운동으로 칼로리 소모 극대화 · 세트 간 휴식 45~60초 유지 · 토르소·AB스윙·크로스케이블 매일 포함 · 유산소 12분 이후 지방 연소 본격 시작',
        '근육증가':   f'중량 우선(8~10회 한계) · 점진적 과부하 2주마다 2.5~5kg씩 증가 · 운동 후 30분 내 단백질 섭취 필수 · 세트 간 휴식 60~90초 충분히',
        '체력향상':   f'고반복(15~20회) 서킷 스타일 · 심박수 65~75% 유지 · 유산소 30분 이상 확보 · 전신 균형 강화 중심',
        '체형교정':   f'자세 교정 운동 비중 높게 · 좌우 불균형 체크 · 코어 안정화 최우선 · 스트레칭 충분히',
    }.get(goal, '')

    return f"""
<div class="page">
  {_page_header('1', '인바디 분석 & 주간 스케줄', name)}

  <div class="main-header">
    <div>
      <div class="mh-gym">ITN 피트니스 · 동해 · Body Alignment Specialist</div>
      <div class="mh-title">{name}님 <span>맞춤 운동 루틴</span></div>
      <div class="mh-sub">{age}세 {gender} · {c['body_type']} · {goal_label} 프로그램 · {measured}</div>
    </div>
    <div>
      <div class="score-val">{c['score']}<span style="font-size:12pt;color:#7a9ab8">/100</span></div>
      <div class="score-sub">인바디 점수</div>
    </div>
  </div>

  <div class="stats">
    <div class="stat"><div class="stat-v">{c['weight']}<span style="font-size:7.5pt">kg</span></div><div class="stat-l">체중</div><div class="stat-t">유지</div></div>
    <div class="stat green"><div class="stat-v">{c['muscle']}<span style="font-size:7.5pt">kg</span></div><div class="stat-l">골격근량</div><div class="stat-t" style="color:#4a7c59">목표 {c['target_muscle']}kg</div></div>
    <div class="stat alert"><div class="stat-v">{c['fat_pct']}<span style="font-size:7.5pt">%</span></div><div class="stat-l">체지방률</div><div class="stat-t">목표 {c['target_fat_pct']}%</div></div>
    <div class="stat alert"><div class="stat-v">{c['fat_mass']}<span style="font-size:7.5pt">kg</span></div><div class="stat-l">체지방량</div><div class="stat-t">목표 {c['target_fat_mass']}kg</div></div>
    <div class="stat alert"><div class="stat-v">Lv.{c['visceral']}</div><div class="stat-l">내장지방</div><div class="stat-t">목표 Lv.{c['target_visceral']}</div></div>
    <div class="stat"><div class="stat-v">{c['bmi']}</div><div class="stat-l">BMI</div><div class="stat-t">kg/m²</div></div>
    <div class="stat"><div class="stat-v">{c['bmr']}<span style="font-size:6.5pt">kcal</span></div><div class="stat-l">기초대사량</div><div class="stat-t">TDEE {c['tdee']}kcal</div></div>
  </div>

  <div class="pbox"><strong>💡 {name}님 핵심 포인트 ({c['body_type']})</strong><br>
  {c['body_desc']}<br>
  <strong>운동 목적 ({goal_label}):</strong> {key_points}
  </div>

  <div class="sec">주간 운동 스케줄</div>
  <table class="week-table">
    <thead><tr>
      <th style="width:8%">요일</th><th style="width:14%">유형</th>
      <th style="width:52%">주요 운동 (순서대로)</th><th style="width:26%">마무리 유산소</th>
    </tr></thead>
    <tbody>
      <tr><td><span class="day-badge">월</span></td><td style="font-weight:700;color:#1e4d7b">하체+코어</td>
        <td style="font-size:7pt">에코바이크 10분 → 핵스쿼트 · 파워레그프레스 · 시티드레그컬 · 힙쓰러스트 · 토탈힙 · 아웃타이이너싸이 → 업도미널 · AB스윙</td>
        <td style="font-size:7pt;color:#c0603a;font-weight:600">천국의 계단 15분</td></tr>
      <tr><td><span class="day-badge">화</span></td><td style="font-weight:700;color:#1e4d7b">상체+코어</td>
        <td style="font-size:7pt">무동력트레드밀 8분 → 시티드체스트프레스 · 랫풀다운 · 시티드로우 · 숄더프레스 · 팩덱플라이 → 토르소 · 크로스케이블 · 하이퍼익스텐션</td>
        <td style="font-size:7pt;color:#c0603a;font-weight:600">스키머신 20분</td></tr>
      <tr><td><span class="day-badge" style="background:#9a6208">수</span></td><td style="font-weight:700;color:#9a6208">코어+유산소</td>
        <td style="font-size:7pt">에코바이크 10분 → 토르소 · AB스윙 · 크로스케이블 · 업도미널 · 하이퍼익스텐션 · 레그레이즈 → 플랭크 3세트</td>
        <td style="font-size:7pt;color:#c0603a;font-weight:600">스키머신 or 인클라인워킹 25분</td></tr>
      <tr><td><span class="day-badge">목</span></td><td style="font-weight:700;color:#1e4d7b">하체+코어</td>
        <td style="font-size:7pt">에코바이크 10분 → 브이스쿼트 · 버티컬레그프레스 · 몬스터글루트 · 레그컬 · 덩키킥 → 업도미널 · AB스윙</td>
        <td style="font-size:7pt;color:#c0603a;font-weight:600">천국의 계단 15분</td></tr>
      <tr><td><span class="day-badge">금</span></td><td style="font-weight:700;color:#1e4d7b">상체+코어</td>
        <td style="font-size:7pt">무동력트레드밀 8분 → 인클라인벤치 · 와이드리어풀다운 · 로우로우·티바로우 · 레터럴레이즈 · 암컬 → 토르소 · 크로스케이블 · 백익스텐션</td>
        <td style="font-size:7pt;color:#c0603a;font-weight:600">엘립티컬 20분</td></tr>
      <tr><td><span class="day-badge opt">토</span></td><td style="color:#4a7c59;font-weight:700">유산소 (선택)</td>
        <td style="font-size:7pt">인클라인 런닝머신 경사 걷기 or 천국의 계단 30분</td>
        <td style="font-size:7pt;color:#9a9888">—</td></tr>
      <tr><td><span class="day-badge rest">일</span></td><td style="color:#6a7a88">완전 휴식</td>
        <td style="font-size:7pt;color:#7a8888">충분한 수면 · 근육 회복</td>
        <td style="font-size:7pt;color:#9a9888">—</td></tr>
    </tbody>
  </table>

  <div class="sec">3개월 목표</div>
  <div class="goal-row"><div class="gl">체지방률</div><div class="gb-wrap"><div class="gb" style="width:{fat_bar}%;background:linear-gradient(90deg,#1e4d7b,#c0603a)"></div></div><div class="gv">{c['fat_pct']}% → {c['target_fat_pct']}% 이하</div></div>
  <div class="goal-row"><div class="gl">체지방량</div><div class="gb-wrap"><div class="gb" style="width:78%;background:linear-gradient(90deg,#1e4d7b,#c0603a)"></div></div><div class="gv">{c['fat_mass']}kg → {c['target_fat_mass']}kg</div></div>
  <div class="goal-row"><div class="gl">골격근량</div><div class="gb-wrap"><div class="gb" style="width:82%;background:#4a7c59"></div></div><div class="gv">{c['muscle']}kg → {c['target_muscle']}kg 이상 유지</div></div>
  <div class="goal-row"><div class="gl">내장지방</div><div class="gb-wrap"><div class="gb" style="width:{vis_bar}%;background:linear-gradient(90deg,#4a7c59,#d4900a)"></div></div><div class="gv">레벨 {c['visceral']} → 레벨 {c['target_visceral']}</div></div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 2 — 운동 전 근막이완 루틴
# ═══════════════════════════════════════════════════════════
def _page2(c, member):
    name = member.get('name', '회원')
    return f"""
<div class="page">
  {_page_header('2', '운동 전 근막이완 루틴', name)}
  <div class="sec">운동 전 근막이완이 필요한 이유</div>
  <div class="benefit-row">
    <div class="benefit">
      <div class="b-icon">🦵</div>
      <div class="b-title">관절가동범위 확보</div>
      <div class="b-desc">굳은 근막을 이완시켜<br>운동 시 더 넓은 가동범위를<br>안전하게 사용</div>
    </div>
    <div class="benefit" style="border-top-color:#c0603a">
      <div class="b-icon">🛡️</div>
      <div class="b-title">부상 예방</div>
      <div class="b-desc">혈류 증가로 근육과 관절<br>온도를 높여 염좌·근파열<br>위험 70% 감소</div>
    </div>
    <div class="benefit" style="border-top-color:#4a7c59">
      <div class="b-icon">❤️</div>
      <div class="b-title">혈액순환 촉진</div>
      <div class="b-desc">국소 혈류 증가로 산소·<br>영양공급 원활 → 운동<br>퍼포먼스 향상</div>
    </div>
    <div class="benefit" style="border-top-color:#9a6208">
      <div class="b-icon">⏱️</div>
      <div class="b-title">소요 시간</div>
      <div class="b-desc">12~15분이면 충분<br>부위당 30~60초<br>통증 없이 지그시 압박</div>
    </div>
  </div>

  <div class="sec">도구별 근막이완 방법</div>
  <div class="tool-grid">
    <div class="tool-box">
      <div class="tool-head">🟤 폼롤러 (Foam Roller)</div>
      <div class="tool-body">
        <div class="tool-item"><span class="num">①</span><strong>종아리 이완</strong> — 폼롤러 위에 종아리를 올리고 체중을 실어 천천히 앞뒤로 굴리기. 30~60초, 뭉친 곳에서 멈추기</div>
        <div class="tool-item"><span class="num">②</span><strong>허벅지 앞 (대퇴사두) 이완</strong> — 엎드려 허벅지 앞쪽을 롤러 위에 올리고 골반~무릎 구간 천천히 이완. 30~60초</div>
        <div class="tool-item"><span class="num">③</span><strong>허벅지 옆 (IT밴드) 이완</strong> — 옆으로 누워 IT밴드(허벅지 옆)를 위에서 아래로 이완. 뭉친 곳에서 10초 정지</div>
      </div>
    </div>
    <div class="tool-box">
      <div class="tool-head" style="background:#c0603a">🟠 마사지볼 (Massage Ball)</div>
      <div class="tool-body">
        <div class="tool-item"><span class="num">①</span><strong>둔근(엉덩이) 이완</strong> — 의자나 바닥에 앉아 볼 위에 엉덩이 올리고 체중 실어 지그시 압박. 좌우 각 30초</div>
        <div class="tool-item"><span class="num">②</span><strong>발바닥 족각 이완</strong> — 서서 발바닥으로 볼을 굴리며 뭉친 곳 집중 압박. 발꿈치~발볼 전체 30~60초</div>
        <div class="tool-item"><span class="num">③</span><strong>어깨 주변 (삼각근) 이완</strong> — 볼을 벽에 대고 어깨 앞·뒤 체중 실어 압박. 뭉친 곳에서 10~15초 정지</div>
      </div>
    </div>
    <div class="tool-box">
      <div class="tool-head" style="background:#4a7c59">🟢 스틱·폼즈 (Stick / Forms)</div>
      <div class="tool-body">
        <div class="tool-item"><span class="num">①</span><strong>스틱-폼즈 이완</strong> — 스틱으로 허벅지·종아리를 굴려 근막 이완. 적절한 압박으로 앞뒤 10~15회</div>
        <div class="tool-item"><span class="num">②</span><strong>발바닥 족각 이완</strong> — 스틱 끝으로 발바닥 아치 부분을 지그시 압박하며 이완. 각 포인트 10~15초</div>
        <div class="tool-item"><span class="num">③</span><strong>폼즈-척추 정렬</strong> — 폼즈를 척추 방향으로 놓고 등을 대고 누워 흉추 이완. 1~2분 천천히</div>
      </div>
    </div>
    <div class="tool-box">
      <div class="tool-head" style="background:#9a6208">🟡 밴드·요가블록</div>
      <div class="tool-body">
        <div class="tool-item"><span class="num">①</span><strong>밴드-햄스트링 이완</strong> — 누워 밴드를 발에 걸고 무릎 편 채 다리를 위로. 뒤허벅지 가볍게 20~30초</div>
        <div class="tool-item"><span class="num">②</span><strong>밴드-둔근 활성화</strong> — 밴드를 무릎 위에 걸고 클램쉘 동작. 둔근 위아래 느끼며 15회 × 2세트</div>
        <div class="tool-item"><span class="num">③</span><strong>요가블록-고관절 이완</strong> — 블록 위에 골반 올리고 고관절 전면 스트레칭. 좌우 각 30초</div>
      </div>
    </div>
  </div>

  <div class="sec">하체 운동 전 근막이완 순서</div>
  <div class="pbox">
    <strong>권장 순서:</strong> ① 종아리 폼롤러 (30초) → ② 허벅지 앞 폼롤러 (30초) → ③ IT밴드 폼롤러 (30초) → ④ 둔근 마사지볼 (30초) → ⑤ 발바닥 마사지볼 (30초) → ⑥ 밴드 둔근 활성화 (15회×2) → ⑦ 요가블록 고관절 (30초)<br>
    <strong>총 소요:</strong> 약 12~15분 · 에코바이크 탑승 전 완료
  </div>

  <div class="tip"><strong>핵심 팁</strong> — 통증이 느껴지는 부위에서 30초 이상 멈추세요. 호흡을 내쉬면서 천천히 압박하면 효과가 2배입니다. 절대로 뼈 위를 직접 굴리지 마세요. 근막이완 후 스트레칭하면 유연성이 훨씬 더 늘어납니다.</div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 3 — 하체 운동 상세 (월/목)
# ═══════════════════════════════════════════════════════════
def _page3(c, member):
    name = member.get('name', '회원')
    rr = c['rep_range']
    cr = c['core_reps']
    s  = c['sets']

    mon_exs = [
        ('cat-warmup', '워밍업', '에코바이크', '10분', '싸이클 · 런닝머신'),
        ('cat-weight', '웨이트①', '핵스쿼트', f'{s} × {rr}', '브이스쿼트 · 스미스머신'),
        ('cat-weight', '웨이트②', '45도 파워레그프레스', f'{s} × 15회', '버티컬레그프레스'),
        ('cat-weight', '웨이트③', '시티드레그컬', f'{s} × {rr}', '레그컬 머신'),
        ('cat-weight', '웨이트④', '힙쓰러스트', f'{s} × 15회', '몬스터글루트 · 글루트머신'),
        ('cat-weight', '웨이트⑤', '토탈힙', f'{s} × 15회', '스탠딩 아웃싸이'),
        ('cat-weight', '웨이트⑥', '아웃타이·이너싸이', '2세트 × 20회', '스탠딩 아웃싸이'),
        ('cat-core',   '코어①', '업도미널', f'{s} × {cr}', '행잉 니레이즈'),
        ('cat-core',   '코어②★', 'AB스윙', f'{s} × {cr}', '토르소 · 크로스케이블'),
        ('cat-finish', '마무리', '천국의 계단', '15분 (레벨 6~8)', '인클라인 런닝머신'),
    ]
    thu_exs = [
        ('cat-warmup', '워밍업', '에코바이크', '10분', '싸이클 · 런닝머신'),
        ('cat-weight', '웨이트①', '브이스쿼트', f'{s} × {rr}', '핵스쿼트 · 스미스머신'),
        ('cat-weight', '웨이트②', '버티컬레그프레스', f'{s} × 15회', '45도 파워레그프레스'),
        ('cat-weight', '웨이트③', '몬스터글루트', f'{s} × 15회', '힙쓰러스트 · 글루트머신'),
        ('cat-weight', '웨이트④', '레그컬', f'{s} × {rr}', '시티드레그컬'),
        ('cat-weight', '웨이트⑤', '덩키킥', f'{s} × 15회 (각)', '토탈힙 머신'),
        ('cat-core',   '코어①', '업도미널', f'{s} × {cr}', '행잉 니레이즈'),
        ('cat-core',   '코어②★', 'AB스윙', f'{s} × {cr}', '토르소 · 크로스케이블'),
        ('cat-finish', '마무리', '천국의 계단', '15분 (레벨 6~8)', '인클라인 런닝머신'),
    ]

    def ex_cards(exs):
        html = ''
        for cat_cls, cat, name_ex, detail, alt in exs:
            html += f"""<div class="ex-card">
              <div style="min-width:42pt"><span class="ex-cat {cat_cls}">{cat}</span></div>
              <div style="flex:1">
                <div class="ex-name">{name_ex}</div>
                <div class="ex-detail">{detail}</div>
                <div class="ex-alt">대체: {alt}</div>
              </div>
            </div>"""
        return html

    return f"""
<div class="page">
  {_page_header('3', '하체 운동 상세 (월/목요일)', name)}
  <div class="sec">하체 운동 — 월요일 & 목요일</div>

  <div class="ex-col-wrap">
    <div class="ex-col">
      <div class="ex-col-head">🗓️ 월요일 — 하체 + 코어</div>
      {ex_cards(mon_exs)}
    </div>
    <div class="ex-col">
      <div class="ex-col-head">🗓️ 목요일 — 하체 + 코어</div>
      {ex_cards(thu_exs)}
    </div>
  </div>

  <div class="tip">
    <strong>하체 운동 핵심 포인트</strong><br>
    ① 스쿼트 계열: 무릎이 발끝을 넘지 않도록, 엉덩이를 뒤로 빼는 느낌으로 앉기<br>
    ② 레그프레스: 발 위치에 따라 자극 부위 변경 (높으면 둔근·햄스트링, 낮으면 대퇴사두)<br>
    ③ 힙쓰러스트·몬스터글루트: 골반 상단까지 올려 둔근 최대 수축 1~2초 유지<br>
    ④ 코어 운동: 허리 반동 없이 복부 힘으로만 — 호흡 내쉬면서 수축<br>
    ⑤ 천국의 계단: 손잡이 잡지 않기 — 상체 약간 앞으로 기울여 둔근 집중 자극
  </div>

  <div class="pbox">
    <strong>📌 월·목 운동 포인트 비교</strong><br>
    <strong>월요일</strong> — 핵스쿼트(대퇴사두 집중) + 파워레그프레스(전체 하체) + 힙쓰러스트(둔근 집중) 패턴<br>
    <strong>목요일</strong> — 브이스쿼트(내전근 강조) + 버티컬레그프레스(대퇴사두) + 몬스터글루트(둔근 외측) 패턴<br>
    같은 하체라도 자극 부위를 달리해 균형 잡힌 발달을 도모합니다.
  </div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 4 — 상체 운동 상세 (화/금)
# ═══════════════════════════════════════════════════════════
def _page4(c, member):
    name = member.get('name', '회원')
    rr = c['rep_range']
    cr = c['core_reps']
    s  = c['sets']

    tue_exs = [
        ('cat-warmup', '워밍업', '무동력 트레드밀', '8분', '에코바이크'),
        ('cat-weight', '가슴①', '시티드체스트프레스', f'{s} × {rr}', '벤치프레스 · 멀티프레스'),
        ('cat-weight', '등①', '랫풀다운', f'{s} × {rr}', '하이랫풀 · 와이드풀다운'),
        ('cat-weight', '등②', '시티드로우', f'{s} × {rr}', '로우로우 · 티바로우'),
        ('cat-weight', '어깨①', '숄더프레스', f'{s} × {rr}', '덤벨 숄더프레스'),
        ('cat-weight', '가슴②', '팩덱플라이', '2세트 × 15회', '크로스케이블 플라이'),
        ('cat-core',   '코어①★', '토르소', f'{s} × {cr} (좌우)', 'AB스윙'),
        ('cat-core',   '코어②★', '크로스케이블', f'{s} × 15회 (좌우)', '토르소'),
        ('cat-core',   '코어③', '하이퍼익스텐션', '2세트 × 15회', '백익스텐션'),
        ('cat-finish', '마무리', '스키머신', '20분 (중간~빠른 페이스)', '엘립티컬'),
    ]
    fri_exs = [
        ('cat-warmup', '워밍업', '무동력 트레드밀', '8분', '에코바이크'),
        ('cat-weight', '가슴①', '인클라인벤치프레스', f'{s} × {rr}', '시티드체스트프레스'),
        ('cat-weight', '등①', '와이드리어풀다운', f'{s} × {rr}', '랫풀다운'),
        ('cat-weight', '등②', '로우로우 or 티바로우', f'{s} × {rr}', '시티드로우'),
        ('cat-weight', '어깨①', '레터럴레이즈 (덤벨)', f'{s} × 15회', '멀티레이즈'),
        ('cat-weight', '이두①', '암컬 (덤벨)', '2세트 × 15회', '바벨컬 · 케이블컬'),
        ('cat-core',   '코어①★', '토르소', f'{s} × {cr} (좌우)', 'AB스윙'),
        ('cat-core',   '코어②★', '크로스케이블', f'{s} × 15회 (좌우)', '토르소'),
        ('cat-core',   '코어③', '백익스텐션', '2세트 × 15회', '하이퍼익스텐션'),
        ('cat-finish', '마무리', '엘립티컬', '20분', '스키머신'),
    ]

    def ex_cards(exs):
        html = ''
        for cat_cls, cat, name_ex, detail, alt in exs:
            html += f"""<div class="ex-card">
              <div style="min-width:42pt"><span class="ex-cat {cat_cls}">{cat}</span></div>
              <div style="flex:1">
                <div class="ex-name">{name_ex}</div>
                <div class="ex-detail">{detail}</div>
                <div class="ex-alt">대체: {alt}</div>
              </div>
            </div>"""
        return html

    return f"""
<div class="page">
  {_page_header('4', '상체 운동 상세 (화/금요일)', name)}
  <div class="sec">상체 운동 — 화요일 & 금요일</div>

  <div class="ex-col-wrap">
    <div class="ex-col">
      <div class="ex-col-head">🗓️ 화요일 — 상체 + 코어</div>
      {ex_cards(tue_exs)}
    </div>
    <div class="ex-col">
      <div class="ex-col-head">🗓️ 금요일 — 상체 + 코어</div>
      {ex_cards(fri_exs)}
    </div>
  </div>

  <div class="tip">
    <strong>상체 운동 핵심 포인트</strong><br>
    ① 체스트프레스·인클라인벤치: 어깨를 뒤로 당기고 고정 — 가슴 근육이 수축되는 느낌을 찾기<br>
    ② 랫풀다운·풀다운: 팔꿈치를 아래로 내리는 느낌으로 — 팔 힘이 아닌 등 넓은근 사용<br>
    ③ 숄더프레스: 목 뒤로 내리지 않기 — 귀 옆으로 팔꿈치 정렬, 승모근 과사용 주의<br>
    ④ 토르소·크로스케이블: 복사근과 옆구리 집중 — 상체 회전 시 하체 고정 유지<br>
    ⑤ 백·하이퍼익스텐션: 과신전 금지 — 엉덩이와 허리 중간까지만 올리기
  </div>

  <div class="pbox">
    <strong>📌 화·금 운동 포인트 비교</strong><br>
    <strong>화요일</strong> — 시티드(앉아서) 중심 머신 운동 · 시티드체스트프레스(가슴 전면) + 랫풀다운(광배근) + 시티드로우(중간 등) 패턴<br>
    <strong>금요일</strong> — 인클라인(상부 가슴) + 와이드풀다운(광배근 넓이) + 로우로우·티바로우(등 두께) + 레터럴레이즈(어깨 측면) 패턴<br>
    가슴·등·어깨를 번갈아 자극해 상체 균형을 잡습니다.
  </div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 4-B — 수요일 코어+유산소 상세
# ═══════════════════════════════════════════════════════════
def _page4b(c, member):
    name = member.get('name', '회원')
    cr = c['core_reps']

    wed_exs = [
        ('cat-warmup', '워밍업',  '에코바이크',        '10분',              '싸이클 · 런닝머신'),
        ('cat-core',   '코어★',   '토르소',             f'3 × {cr}(좌우)',   'AB스윙 · 크로스케이블'),
        ('cat-core',   '코어★',   'AB스윙',             f'3 × {cr}',         '토르소 · 크로스케이블'),
        ('cat-core',   '코어★',   '크로스케이블',       f'3 × 15회(좌우)',   '토르소 · 듀얼풀리'),
        ('cat-core',   '코어',    '업도미널',            f'3 × {cr}',         '행잉 니레이즈'),
        ('cat-core',   '코어',    '레그레이즈',          f'3 × 15회',         '힙플렉서 · 업도미널'),
        ('cat-core',   '허리안정', '하이퍼익스텐션',    '2 × 15회',          '백익스텐션'),
        ('cat-core',   '전신코어', '플랭크',             '3 × 40초',          '사이드플랭크'),
        ('cat-finish', '마무리',  '스키머신 or 인클라인워킹', '25분',          '엘립티컬 · 천국의 계단'),
    ]

    def ex_card(cat_cls, cat, nm, detail, alt):
        return f"""<div class="ex-card">
      <span class="ex-cat {cat_cls}">{cat}</span>
      <div style="flex:1">
        <div class="ex-name">{nm}</div>
        <div class="ex-detail">{detail}</div>
        <div class="ex-alt">대체: {alt}</div>
      </div>
    </div>"""

    cards = ''.join(ex_card(*e) for e in wed_exs)

    return f"""
<div class="page">
  {_page_header('4-B', '수요일 코어+유산소 상세', name)}

  <div class="main-header">
    <div>
      <div class="mh-gym">ITN 피트니스 · 동해 · Body Alignment Specialist</div>
      <div class="mh-title">수요일 — <span>코어 집중 + 유산소</span></div>
      <div class="mh-sub">복부·옆구리 직접 공략 · 코어 전체 + 지방 연소 유산소</div>
    </div>
  </div>

  <div class="pbox">
    <strong>💡 수요일 포인트</strong> — 월·화 웨이트 후 근육 회복을 유지하면서 코어와 유산소로 지방 연소를 이어갑니다.
    토르소·AB스윙·크로스케이블 <strong>3종 세트</strong>는 복부·옆구리 지방 공략의 핵심입니다.
    무게 없이도 제대로 하면 충분히 자극이 옵니다. 호흡에 집중하며 천천히 수행하세요.
  </div>

  <div class="sec">🔥 수요일 운동 구성</div>
  <div class="ex-col-wrap">
    <div class="ex-col">
      <div class="ex-col-head">수요일 — 코어 + 유산소</div>
      {cards}
    </div>
    <div class="ex-col" style="max-width:44%">
      <div class="ex-col-head">코어 운동 핵심 포인트</div>
      <div style="padding:4mm;font-size:8.5pt;line-height:1.8;border:0.6pt solid #e2ded8;border-top:none">
        <div style="margin-bottom:3mm"><strong style="color:#c0603a">토르소·AB스윙</strong><br>
        허리 반동 ❌ · 복부와 옆구리로만 회전<br>끝점에서 1초 멈추며 수축 느끼기</div>
        <div style="margin-bottom:3mm"><strong style="color:#c0603a">크로스케이블</strong><br>
        팔꿈치 고정 · 대각선으로 당길 때 옆구리 수축<br>양쪽 동일한 횟수 유지</div>
        <div style="margin-bottom:3mm"><strong style="color:#1e4d7b">업도미널·레그레이즈</strong><br>
        허리가 바닥에서 뜨지 않게 유지<br>올릴 때 내쉬고, 내릴 때 들이쉬기</div>
        <div style="margin-bottom:3mm"><strong style="color:#1e4d7b">플랭크</strong><br>
        몸통이 일직선 · 엉덩이 들리거나 내려앉지 않게<br>40초가 힘들면 20초 × 2세트로 분할</div>
        <div style="background:#fdf6ec;border-left:3pt solid #d4900a;padding:3mm;border-radius:0 4pt 4pt 0;font-size:8pt">
          <strong style="color:#9a6208">유산소 타이밍</strong> — 코어 운동 완료 후 유산소.
          지방 연소는 12분 이후 본격 시작되므로 25분 이상 유지하세요.
          심박수 목표: <strong>{c['fat_burn_lo']}~{c['fat_burn_hi']}bpm</strong>
        </div>
      </div>
    </div>
  </div>

  <div class="green-box">
    <strong>✅ 수요일 목표 칼로리 소모</strong> —
    코어 운동 약 <strong>80kcal</strong> + 유산소 25분 약 <strong>180kcal</strong> = 총 약 <strong>260kcal</strong> 소모.
    월·화 웨이트 후 회복하면서도 꾸준히 지방을 줄이는 가장 효율적인 방법입니다.
  </div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 5 — 웨이트 & 유산소 가이드라인
# ═══════════════════════════════════════════════════════════
def _page5(c, member):
    name = member.get('name', '회원')
    return f"""
<div class="page">
  {_page_header('5', '웨이트 & 유산소 가이드라인', name)}
  <div class="sec">웨이트 트레이닝 강도 지침</div>

  <div class="metric-row">
    <div class="metric orange">
      <div class="metric-v">{c['rm_range']}</div>
      <div class="metric-l">1RM 대비 중량</div>
    </div>
    <div class="metric">
      <div class="metric-v">{c['rep_range']}</div>
      <div class="metric-l">주운동 횟수</div>
    </div>
    <div class="metric">
      <div class="metric-v">{c['sets']}</div>
      <div class="metric-l">세트 수</div>
    </div>
    <div class="metric red">
      <div class="metric-v">{c['rest']}</div>
      <div class="metric-l">세트 간 휴식</div>
    </div>
    <div class="metric green">
      <div class="metric-v">2주마다</div>
      <div class="metric-l">무게 점검 주기</div>
    </div>
  </div>

  <div class="sec">운동 부위별 세트·횟수·휴식 가이드</div>
  <table class="g-table">
    <thead><tr><th>운동 부위</th><th>대표 운동</th><th>세트</th><th>횟수</th><th>세트 간 휴식</th><th>중량 기준</th></tr></thead>
    <tbody>
      <tr><td>하체 (대퇴사두)</td><td>핵스쿼트, 브이스쿼트, 레그프레스</td><td class="center">3</td><td class="center">{c['rep_range']}</td><td class="center">{c['rest']}</td><td class="num">{c['rm_range']} 1RM</td></tr>
      <tr><td>둔근 (엉덩이)</td><td>힙쓰러스트, 몬스터글루트, 덩키킥</td><td class="center">3</td><td class="center">15회</td><td class="center">{c['rest']}</td><td class="num">{c['rm_range']} 1RM</td></tr>
      <tr><td>햄스트링</td><td>시티드레그컬, 레그컬</td><td class="center">3</td><td class="center">{c['rep_range']}</td><td class="center">{c['rest']}</td><td class="num">{c['rm_range']} 1RM</td></tr>
      <tr><td>가슴 (대흉근)</td><td>체스트프레스, 인클라인벤치, 팩덱플라이</td><td class="center">3</td><td class="center">{c['rep_range']}</td><td class="center">{c['rest']}</td><td class="num">{c['rm_range']} 1RM</td></tr>
      <tr><td>등 (광배근·중간등)</td><td>랫풀다운, 로우, 티바로우</td><td class="center">3</td><td class="center">{c['rep_range']}</td><td class="center">{c['rest']}</td><td class="num">{c['rm_range']} 1RM</td></tr>
      <tr><td>어깨 (삼각근)</td><td>숄더프레스, 레터럴레이즈</td><td class="center">3</td><td class="center">{c['rep_range']}</td><td class="center">{c['rest']}</td><td class="num">{c['rm_range']} 1RM</td></tr>
      <tr><td>코어 (복근·복사근)</td><td>업도미널, AB스윙, 토르소, 크로스케이블</td><td class="center">3</td><td class="center">{c['core_reps']}</td><td class="center">30~45초</td><td class="num">체중 이용</td></tr>
      <tr><td>코어 (척추기립근)</td><td>백익스텐션, 하이퍼익스텐션</td><td class="center">2</td><td class="center">15회</td><td class="center">45초</td><td class="num">체중 이용</td></tr>
    </tbody>
  </table>

  <div class="sec">유산소 기구별 강도 가이드</div>
  <table class="g-table">
    <thead><tr><th>기구</th><th>설정</th><th>지속 시간</th><th>강도</th><th>지방 연소 효과</th></tr></thead>
    <tbody>
      <tr><td>천국의 계단</td><td>레벨 6~8 (처음엔 4~5부터)</td><td class="center">15분</td><td class="center">중~고강도</td><td style="color:#4a7c59;font-weight:600">★★★★★</td></tr>
      <tr><td>스키머신</td><td>중간~빠른 페이스, 팔다리 협응</td><td class="center">20분</td><td class="center">중강도</td><td style="color:#4a7c59;font-weight:600">★★★★☆</td></tr>
      <tr><td>인클라인 런닝머신</td><td>경사 8~12도, 속도 4~5km/h 걷기</td><td class="center">30분</td><td class="center">저~중강도</td><td style="color:#4a7c59;font-weight:600">★★★★☆</td></tr>
      <tr><td>에코바이크 (워밍업)</td><td>가볍게 페달링, 땀 살짝 날 정도</td><td class="center">10분</td><td class="center">저강도</td><td style="color:#4a7c59;font-weight:600">★★☆☆☆</td></tr>
      <tr><td>엘립티컬</td><td>팔 동작 적극 활용, 경사 4~6</td><td class="center">20분</td><td class="center">중강도</td><td style="color:#4a7c59;font-weight:600">★★★☆☆</td></tr>
      <tr><td>무동력 트레드밀 (워밍업)</td><td>빠른 걷기~가벼운 달리기</td><td class="center">8분</td><td class="center">저~중강도</td><td style="color:#4a7c59;font-weight:600">★★★☆☆</td></tr>
    </tbody>
  </table>

  <div class="sec">목표 심박수 ({member.get('age','?')}세 기준)</div>
  <div class="hr-row">
    <div class="hr-box blue">
      <div class="hr-val">{c['max_hr']}</div>
      <div class="hr-label">최대 심박수 (220 - {c['age']}세)</div>
    </div>
    <div class="hr-box orange">
      <div class="hr-val">{c['fat_burn_lo']}~{c['fat_burn_hi']}</div>
      <div class="hr-label">지방 연소 구간 (60~70%)</div>
    </div>
    <div class="hr-box orange">
      <div class="hr-val">{c['cardio_lo']}~{c['cardio_hi']}</div>
      <div class="hr-label">유산소 운동 구간 (65~75%)</div>
    </div>
    <div class="hr-box red">
      <div class="hr-val">{round(c['max_hr']*0.85)}~{round(c['max_hr']*0.90)}</div>
      <div class="hr-label">고강도 구간 (85~90%)</div>
    </div>
  </div>

  <div class="tip"><strong>중량 점진적 증가 원칙</strong> — 설정 횟수를 모두 완료하면 다음 주에 2.5~5kg 증가. 마지막 세트에서 2~3회 더 할 수 있으면 무게를 올릴 시점입니다. 관절 통증이 있으면 무게를 줄이고 자세를 점검하세요.</div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 6 — 운동 강도 & 칼로리 소모 분석
# ═══════════════════════════════════════════════════════════
def _page6(c, member):
    name = member.get('name', '회원')
    bmr_daily = round(c['bmr'] + (c['burn_lower'] + c['burn_upper']) / 2)
    return f"""
<div class="page">
  {_page_header('6', '운동 강도 & 칼로리 소모 분석', name)}
  <div class="sec">RPE (자각적 운동 강도) 기준표</div>
  <table class="g-table">
    <thead><tr><th>RPE</th><th>강도</th><th>느낌</th><th>적용 구간</th><th>심박수</th></tr></thead>
    <tbody>
      <tr><td class="center" style="font-weight:700;color:#4a7c59">5~6</td><td>저강도</td><td>숨 쉬며 대화 가능 · 약간 땀</td><td>워밍업 · 마무리 유산소</td><td class="center">{c['fat_burn_lo']}↓ bpm</td></tr>
      <tr><td class="center" style="font-weight:700;color:#f0a060">7</td><td>중강도</td><td>대화 약간 힘듦 · 땀 흐름</td><td>웨이트 주 작업 세트 · 유산소 메인</td><td class="center">{c['fat_burn_lo']}~{c['fat_burn_hi']} bpm</td></tr>
      <tr><td class="center" style="font-weight:700;color:#c0603a">8~9</td><td>고강도</td><td>말하기 힘듦 · 마지막 1~2회 한계</td><td>웨이트 마지막 세트 · 천국의 계단</td><td class="center">{c['cardio_hi']}~{round(c['max_hr']*0.85)} bpm</td></tr>
      <tr><td class="center" style="font-weight:700;color:#8b0000">10</td><td>최고강도</td><td>더 이상 불가능</td><td>테스트 시에만 (일반 루틴 금지)</td><td class="center">{c['max_hr']}+ bpm</td></tr>
    </tbody>
  </table>

  <div class="sec">운동별 예상 칼로리 소모 ({c['weight']}kg 기준)</div>
  <table class="g-table">
    <thead><tr><th>운동 항목</th><th>시간/세트</th><th>강도(RPE)</th><th>소모 칼로리</th><th>비고</th></tr></thead>
    <tbody>
      <tr><td>에코바이크 워밍업</td><td class="center">10분</td><td class="center">5~6</td><td class="num">{round(c['weight']*0.10*10)} kcal</td><td>저강도 유산소</td></tr>
      <tr><td>무동력 트레드밀 워밍업</td><td class="center">8분</td><td class="center">6~7</td><td class="num">{round(c['weight']*0.12*8)} kcal</td><td>전신 워밍업</td></tr>
      <tr><td>하체 웨이트 (핵스쿼트 등)</td><td class="center">30~40분</td><td class="center">7~8</td><td class="num">{round(c['weight']*0.085*35)} kcal</td><td>대근육군 고소모</td></tr>
      <tr><td>상체 웨이트 (프레스·풀)</td><td class="center">30~40분</td><td class="center">7~8</td><td class="num">{round(c['weight']*0.075*35)} kcal</td><td>중~대근육군</td></tr>
      <tr><td>코어 운동 (AB스윙·토르소)</td><td class="center">15분</td><td class="center">6~7</td><td class="num">{round(c['weight']*0.06*15)} kcal</td><td>국소 근육</td></tr>
      <tr><td>천국의 계단</td><td class="center">15분</td><td class="center">7~8</td><td class="num">{round(c['weight']*0.15*15)} kcal</td><td>최고 지방연소</td></tr>
      <tr><td>스키머신</td><td class="center">20분</td><td class="center">6~7</td><td class="num">{round(c['weight']*0.12*20)} kcal</td><td>전신 유산소</td></tr>
      <tr><td>엘립티컬</td><td class="center">20분</td><td class="center">6~7</td><td class="num">{round(c['weight']*0.10*20)} kcal</td><td>저충격 유산소</td></tr>
    </tbody>
  </table>

  <div class="sec">세션별 총 칼로리 소모 요약</div>
  <div class="metric-row">
    <div class="metric orange">
      <div class="metric-v">{c['burn_lower']}<span style="font-size:9pt">kcal</span></div>
      <div class="metric-l">하체 운동일 총 소모<br>(월·목요일)</div>
    </div>
    <div class="metric">
      <div class="metric-v">{c['burn_upper']}<span style="font-size:9pt">kcal</span></div>
      <div class="metric-l">상체 운동일 총 소모<br>(화·금요일)</div>
    </div>
    <div class="metric red">
      <div class="metric-v">{c['burn_weekly']}<span style="font-size:9pt">kcal</span></div>
      <div class="metric-l">주 4회 합계<br>운동 소모 칼로리</div>
    </div>
    <div class="metric green">
      <div class="metric-v">{bmr_daily}<span style="font-size:9pt">kcal</span></div>
      <div class="metric-l">운동일 총 에너지 소비<br>(기초대사 + 운동)</div>
    </div>
  </div>

  <div class="pbox">
    <strong>칼로리 적자 계산</strong><br>
    목표 섭취 칼로리 <strong>{c['calorie_target']}kcal</strong> - 운동일 평균 소비 <strong>{bmr_daily}kcal</strong> =
    약 <strong style="color:#c0603a">{bmr_daily - c['calorie_target']}kcal 적자</strong>
    (하루 기준)<br>
    주 4회 운동 기준 주간 적자: 약 <strong style="color:#c0603a">{(bmr_daily - c['calorie_target']) * 4}kcal</strong> →
    체지방 약 <strong style="color:#c0603a">{round((bmr_daily - c['calorie_target']) * 4 / 7700, 2)}kg/주</strong> 감소 가능
  </div>

  <div class="tip"><strong>칼로리 소모는 추정치</strong> — 실제 소모량은 운동 강도·세트 수·휴식 시간에 따라 ±20% 차이가 날 수 있습니다. 가장 중요한 것은 꾸준함입니다. 매주 같은 요일에 운동하는 습관을 만들어 보세요.</div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 7 — 맞춤 식단 계획
# ═══════════════════════════════════════════════════════════
def _page7(c, member):
    name = member.get('name', '회원')
    goal = c['goal']

    goal_foods = {
        '체지방감소': {
            'eat':  '닭가슴살·생선(150g) · 달걀흰자 · 두부·콩류 · 잡곡밥(반공기) · 고구마·현미 · 채소 무제한 · 견과류(한줌) · 그릭요거트',
            'avoid': '밀가루·빵·라면 · 설탕·과자·케이크 · 술(맥주·소주) · 튀김류 · 단음료(콜라·주스) · 가공육(소시지·햄) · 야식',
        },
        '근육증가': {
            'eat':  '닭가슴살·소고기·연어(200g↑) · 달걀 3~4개 · 유청단백질 · 잡곡밥(1공기) · 오트밀·고구마 · 바나나·과일 · 아보카도·견과류',
            'avoid': '정제 탄수화물 · 알코올 · 과도한 지방 · 야식',
        },
        '체력향상': {
            'eat':  '복합탄수화물 충분히(밥·파스타·빵) · 닭가슴살·생선(150g) · 과일·채소 · 스포츠음료(운동 중) · 견과류',
            'avoid': '과도한 지방 · 알코올 · 식이섬유 과다 (운동 직전)',
        },
        '체형교정': {
            'eat':  '닭가슴살·생선(130g) · 달걀 2개 · 잡곡밥(반공기) · 채소 무제한 · 견과류(한줌) · 그릭요거트 · 두부',
            'avoid': '밀가루 · 설탕 · 알코올 · 야식 · 가공식품',
        },
    }.get(goal, {'eat': '', 'avoid': ''})

    return f"""
<div class="page">
  {_page_header('7', '맞춤 식단 계획', name)}
  <div class="sec">하루 칼로리 & 영양소 목표</div>

  <div class="metric-row">
    <div class="metric orange" style="flex:2">
      <div class="metric-v" style="font-size:20pt">{c['calorie_target']}<span style="font-size:11pt">kcal</span></div>
      <div class="metric-l">하루 목표 섭취 칼로리 ({c['goal']})</div>
    </div>
    <div class="metric">
      <div class="metric-v">{c['protein_g']}g</div>
      <div class="metric-l">단백질 ({c['p_pct']}%)<br>{c['protein_g']*4}kcal</div>
    </div>
    <div class="metric">
      <div class="metric-v">{c['carb_g']}g</div>
      <div class="metric-l">탄수화물 ({c['c_pct']}%)<br>{c['carb_g']*4}kcal</div>
    </div>
    <div class="metric">
      <div class="metric-v">{c['fat_g']}g</div>
      <div class="metric-l">지방 ({c['f_pct']}%)<br>{c['fat_g']*9}kcal</div>
    </div>
  </div>

  <div class="macro-row">
    <div class="macro-seg" style="width:{c['p_pct']}%;background:#1e4d7b">단백질 {c['p_pct']}%</div>
    <div class="macro-seg" style="width:{c['c_pct']}%;background:#f0a060;color:#1e3a5f">탄수화물 {c['c_pct']}%</div>
    <div class="macro-seg" style="width:{c['f_pct']}%;background:#c0603a">지방 {c['f_pct']}%</div>
  </div>

  <div class="sec">시간대별 식사 계획</div>
  <div class="tl">
    <div class="tl-item">
      <div class="tl-left"><div class="tl-time">기상 직후</div><div class="tl-sub">AM 6~7시</div></div>
      <div class="tl-right"><strong>알칼리 소금물</strong> — 따뜻한 물 200~300ml + 천일염 0.5~1g · 수분 보충 + 신진대사 활성화<br><span style="color:#c0603a;font-size:7pt">⚠️ 고혈압 있으면 소금 생략, 물만 섭취</span></div>
    </div>
    <div class="tl-item">
      <div class="tl-left"><div class="tl-time">아침 식사</div><div class="tl-sub">운동 1.5~2시간 전</div></div>
      <div class="tl-right"><strong>잡곡밥 반공기 + 달걀 2개 + 채소 반찬</strong> — 복합탄수화물로 에너지 안정 공급 · 단백질 {round(c['protein_g']/5)}g 목표</div>
    </div>
    <div class="tl-item">
      <div class="tl-left gold"><div class="tl-time">운동 1시간 전</div><div class="tl-sub">선택사항</div></div>
      <div class="tl-right"><strong>바나나 반개 or 고구마 작은 것 1개</strong> — 빠른 에너지 공급 · 속이 불편하면 생략 가능</div>
    </div>
    <div class="tl-item">
      <div class="tl-left terra"><div class="tl-time">운동 중</div><div class="tl-sub">시작~종료</div></div>
      <div class="tl-right">15~20분마다 물 <strong>150~200ml</strong> · 이온음료·단백질바·과자 ❌ · 총 수분 500ml 이상 목표</div>
    </div>
    <div class="tl-item">
      <div class="tl-left green"><div class="tl-time">운동 직후</div><div class="tl-sub">30분 내 ★골든타임</div></div>
      <div class="tl-right"><strong>단백질 쉐이크 or 두유 1팩 + 바나나 반개</strong> — 근육 합성 최고조 · 단백질 20~30g 빠르게 섭취</div>
    </div>
    <div class="tl-item">
      <div class="tl-left"><div class="tl-time">점심</div><div class="tl-sub">운동 후 1~2시간</div></div>
      <div class="tl-right"><strong>닭가슴살 or 생선 {round(c['weight']*1.5)}g + 잡곡밥 반공기 + 채소 반찬</strong> — 라면·빵·술 ❌</div>
    </div>
    <div class="tl-item">
      <div class="tl-left gray"><div class="tl-time">저녁</div><div class="tl-sub">취침 3시간 전</div></div>
      <div class="tl-right"><strong>단백질 위주 + 채소 많이</strong> — 탄수화물 줄이기 · 닭가슴살·두부·달걀 · 잡곡밥 1/4공기 이하</div>
    </div>
    <div class="tl-item">
      <div class="tl-left gray"><div class="tl-time">취침 2시간 전</div><div class="tl-sub">야식 금지 구간</div></div>
      <div class="tl-right">그릭요거트 or 카제인 단백질 1스쿱 (선택) · 야식 ❌ · 물 한 잔만</div>
    </div>
  </div>

  <div style="display:flex;gap:3mm;margin-bottom:3mm">
    <div class="green-box" style="flex:1">
      <strong>✅ 먹어야 할 음식</strong><br>{goal_foods['eat']}
    </div>
    <div class="alert-box" style="flex:1">
      <strong>❌ 피해야 할 음식</strong><br>{goal_foods['avoid']}
    </div>
  </div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 8 — 수분 섭취 & 수면 가이드
# ═══════════════════════════════════════════════════════════
def _page8(c, member):
    name = member.get('name', '회원')
    water = c['water_l']
    cups  = round(water / 0.2)
    return f"""
<div class="page">
  {_page_header('8', '수분 섭취 & 수면 가이드', name)}
  <div class="sec">하루 수분 섭취 목표</div>

  <div class="metric-row">
    <div class="metric" style="flex:2;border-top-color:#1e4d7b">
      <div class="metric-v" style="font-size:22pt;color:#1e4d7b">{water}L</div>
      <div class="metric-l">하루 목표 수분 섭취량<br>({c['weight']}kg × 0.033 + 운동 0.5L)</div>
    </div>
    <div class="metric">
      <div class="metric-v">{cups}잔</div>
      <div class="metric-l">200ml 기준 컵 수</div>
    </div>
    <div class="metric">
      <div class="metric-v">{round(c['weight']*0.033, 1)}L</div>
      <div class="metric-l">기본 섭취량<br>(체중 기반)</div>
    </div>
    <div class="metric green">
      <div class="metric-v">0.5L</div>
      <div class="metric-l">운동 중<br>추가 섭취량</div>
    </div>
  </div>

  <div class="sec">시간대별 수분 섭취 가이드</div>
  <div class="water-row">
    <div class="water-item">
      <div class="water-time">기상 직후</div>
      <div class="water-amt">300ml</div>
      <div class="water-note">따뜻한 물 / 소금물<br>신진대사 활성화</div>
    </div>
    <div class="water-item">
      <div class="water-time">오전 (아침~점심)</div>
      <div class="water-amt">600ml</div>
      <div class="water-note">식사 30분 전 200ml<br>나머지는 천천히</div>
    </div>
    <div class="water-item">
      <div class="water-time">운동 전</div>
      <div class="water-amt">200ml</div>
      <div class="water-note">운동 30분 전<br>충분한 수화 상태</div>
    </div>
    <div class="water-item" style="border-top-color:#c0603a;background:#fdf0eb">
      <div class="water-time" style="color:#c0603a">운동 중</div>
      <div class="water-amt" style="color:#c0603a">500ml</div>
      <div class="water-note">15~20분마다<br>150~200ml씩</div>
    </div>
    <div class="water-item">
      <div class="water-time">오후 (점심~저녁)</div>
      <div class="water-amt">500ml</div>
      <div class="water-note">식사와 함께<br>소화 도움</div>
    </div>
    <div class="water-item">
      <div class="water-time">저녁~취침 전</div>
      <div class="water-amt">200ml</div>
      <div class="water-note">취침 1시간 전까지<br>너무 많으면 수면 방해</div>
    </div>
  </div>

  <div class="sec">수면 & 회복 가이드</div>
  <div style="display:flex;gap:3mm;margin-bottom:3mm">
    <div class="pbox" style="flex:1">
      <strong>💤 권장 수면 시간: 7~9시간</strong><br>
      수면 중 성장호르몬이 분비되어 근육 회복과 합성이 일어납니다.<br>
      <strong>취침 전 루틴 (30분):</strong><br>
      • 핸드폰·TV 끄기 (블루라이트 차단)<br>
      • 따뜻한 샤워 (체온 조절로 수면 유도)<br>
      • 가벼운 스트레칭 10분<br>
      • 내일 운동 루틴 확인
    </div>
    <div class="pbox" style="flex:1">
      <strong>🔋 근육 회복 핵심 원칙</strong><br>
      • 같은 부위를 연속 2일 이상 운동하지 않기<br>
      • 수·일요일 완전 휴식 (근육 회복의 날)<br>
      • 근육통이 심할 때는 가벼운 걷기로 혈류 증가<br>
      • DOMS (지연성 근육통): 24~72시간 내 정상<br>
      • 찌릿하거나 관절 통증은 즉시 중단
    </div>
  </div>

  <div class="sec">탈수 징후 & 대처법</div>
  <table class="g-table">
    <thead><tr><th>증상</th><th>의미</th><th>대처법</th></tr></thead>
    <tbody>
      <tr><td>소변 색이 진한 노란색</td><td>경미한 탈수</td><td>즉시 물 200~300ml 섭취</td></tr>
      <tr><td>두통·집중력 저하</td><td>뇌의 수분 부족</td><td>물 마시고 10분 휴식</td></tr>
      <tr><td>근육 경련·쥐 남</td><td>전해질 불균형</td><td>이온음료 or 바나나 섭취</td></tr>
      <tr><td>운동 중 어지러움</td><td>즉시 중단 신호</td><td>앉아서 물 마시고 쉬기</td></tr>
      <tr><td>소변 색이 투명</td><td>과수화 (드물게)</td><td>물 섭취 잠시 줄이기</td></tr>
    </tbody>
  </table>

  <div class="tip"><strong>꿀팁</strong> — 아침에 일어나자마자 체중계에 올라가 전날과 비교하세요. 0.5kg 이상 감소했다면 탈수 신호일 수 있습니다. 운동 전후 체중 차이 = 땀으로 잃은 수분량 (1kg = 1L). 반드시 보충하세요.</div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 9 — 기구 사용법 & 핵심 자세
# ═══════════════════════════════════════════════════════════
def _page9(c, member):
    name = member.get('name', '회원')
    return f"""
<div class="page">
  {_page_header('9', '기구 사용법 & 핵심 자세', name)}
  <div class="sec">주요 기구 핵심 자세 가이드</div>

  <div class="tool-grid">
    <div class="tool-box">
      <div class="tool-head">🦵 하체 — 핵스쿼트 / 브이스쿼트</div>
      <div class="tool-body">
        <div class="tool-item"><span class="num">①</span><strong>발 위치</strong> — 플레이트 중앙, 어깨 너비, 발끝 15~30도 바깥 향하게</div>
        <div class="tool-item"><span class="num">②</span><strong>하강 시</strong> — 무릎이 발끝 방향으로 열리며 내려가기 · 무릎이 안쪽으로 모이지 않도록</div>
        <div class="tool-item"><span class="num">③</span><strong>깊이</strong> — 허벅지가 바닥과 평행 or 그 이하 (여건에 따라)</div>
        <div class="tool-item"><span class="num">④</span><strong>허리</strong> — 허리 아치 유지 · 상체 과도하게 숙이지 않기</div>
        <div class="tool-item"><span class="num">⑤</span><strong>호흡</strong> — 내려갈 때 들이마시고 올라올 때 내쉬기</div>
      </div>
    </div>
    <div class="tool-box">
      <div class="tool-head" style="background:#c0603a">🍑 둔근 — 힙쓰러스트 / 몬스터글루트</div>
      <div class="tool-body">
        <div class="tool-item"><span class="num">①</span><strong>등 위치</strong> — 벤치 모서리가 어깨뼈 아래에 위치</div>
        <div class="tool-item"><span class="num">②</span><strong>발 위치</strong> — 무릎 90도 될 때 발꿈치가 바닥에 평평하게</div>
        <div class="tool-item"><span class="num">③</span><strong>최고점</strong> — 골반을 완전히 올려 허리·엉덩이·무릎이 일직선 · 1~2초 유지</div>
        <div class="tool-item"><span class="num">④</span><strong>주의</strong> — 허리를 과신전하지 않기 · 엉덩이 쥐어짜는 느낌 집중</div>
        <div class="tool-item"><span class="num">⑤</span><strong>호흡</strong> — 올라갈 때 내쉬기 (복압 활용)</div>
      </div>
    </div>
    <div class="tool-box">
      <div class="tool-head" style="background:#4a7c59">💪 가슴 — 체스트프레스 / 인클라인벤치</div>
      <div class="tool-body">
        <div class="tool-item"><span class="num">①</span><strong>어깨 세팅</strong> — 어깨를 뒤·아래로 당겨 고정 (으쓱 올라가지 않게)</div>
        <div class="tool-item"><span class="num">②</span><strong>그립</strong> — 손목 중립 유지 · 바가 손바닥 아래쪽에 위치</div>
        <div class="tool-item"><span class="num">③</span><strong>내릴 때</strong> — 팔꿈치 70~80도 각도 · 가슴이 늘어나는 느낌</div>
        <div class="tool-item"><span class="num">④</span><strong>올릴 때</strong> — 가슴을 쥐어짜는 느낌으로 · 팔꿈치 완전히 펴지 않기</div>
        <div class="tool-item"><span class="num">⑤</span><strong>발</strong> — 발바닥 완전히 바닥에 붙이기</div>
      </div>
    </div>
    <div class="tool-box">
      <div class="tool-head" style="background:#9a6208">🔙 등 — 랫풀다운 / 시티드로우</div>
      <div class="tool-body">
        <div class="tool-item"><span class="num">①</span><strong>앉는 자세</strong> — 허벅지 패드를 허벅지에 단단히 고정 · 상체 약간 뒤로 기울이기</div>
        <div class="tool-item"><span class="num">②</span><strong>그립</strong> — 광배근 느끼려면 엄지손가락 같은 방향으로 (오버그립)</div>
        <div class="tool-item"><span class="num">③</span><strong>당길 때</strong> — 팔꿈치를 겨드랑이 방향으로 끌어당기기 · 팔 힘 최소화</div>
        <div class="tool-item"><span class="num">④</span><strong>최고 수축</strong> — 날개뼈를 모아주는 느낌 · 1초 유지</div>
        <div class="tool-item"><span class="num">⑤</span><strong>이완</strong> — 완전히 펴서 광배근 스트레칭 느끼기</div>
      </div>
    </div>
    <div class="tool-box">
      <div class="tool-head" style="background:#1e3a5f">🌀 코어 — AB스윙 / 토르소</div>
      <div class="tool-body">
        <div class="tool-item"><span class="num">①</span><strong>AB스윙</strong> — 허리 반동 금지 · 복부 힘으로만 상체를 내리기</div>
        <div class="tool-item"><span class="num">②</span><strong>토르소</strong> — 하체를 완전히 고정 · 상체만 회전 · 복사근 집중</div>
        <div class="tool-item"><span class="num">③</span><strong>크로스케이블</strong> — 케이블이 몸을 대각선으로 통과하는 느낌 · 천천히</div>
        <div class="tool-item"><span class="num">④</span><strong>호흡</strong> — 수축 시 내쉬기 · 이완 시 들이마시기</div>
        <div class="tool-item"><span class="num">⑤</span><strong>횟수</strong> — {c['core_reps']} · 속도보다 정확한 자세 우선</div>
      </div>
    </div>
    <div class="tool-box">
      <div class="tool-head" style="background:#6a7a88">🏃 유산소 — 천국의 계단 / 스키머신</div>
      <div class="tool-body">
        <div class="tool-item"><span class="num">①</span><strong>천국의 계단</strong> — 손잡이 잡지 않기 (코어 활성화) · 상체 약간 앞으로 기울여 둔근 자극</div>
        <div class="tool-item"><span class="num">②</span><strong>속도</strong> — 레벨 6~8 · 대화 가능한 수준 (RPE 6~7)</div>
        <div class="tool-item"><span class="num">③</span><strong>스키머신</strong> — 팔과 다리 협응 · 팔을 앞뒤로 크게 흔들기</div>
        <div class="tool-item"><span class="num">④</span><strong>무동력 트레드밀</strong> — 뒤꿈치가 아닌 발 중앙으로 착지 · 상체 직립</div>
        <div class="tool-item"><span class="num">⑤</span><strong>목표 심박수</strong> — {c['fat_burn_lo']}~{c['fat_burn_hi']} bpm (지방 연소 구간)</div>
      </div>
    </div>
  </div>

  <div class="tip"><strong>자세 점검 체크리스트</strong> — 운동 시작 전 거울을 보며 자세를 확인하세요. 처음 2주는 가벼운 무게로 자세를 완벽히 익힌 후 중량을 늘리세요. 자세가 무너지면 즉시 무게를 줄이세요. 부상은 잘못된 자세에서 시작됩니다.</div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 10 — 통증 VS 근육통 & 첫 2주 적응 플랜
# ═══════════════════════════════════════════════════════════
def _page10(c, member):
    name = member.get('name', '회원')
    return f"""
<div class="page">
  {_page_header('10', '통증 VS 근육통 & 2주 적응 플랜', name)}
  <div class="sec">통증 vs 근육통 구분하기</div>
  <table class="g-table">
    <thead><tr><th>구분</th><th>정상 근육통 (DOMS)</th><th>부상 징후 (즉시 중단)</th></tr></thead>
    <tbody>
      <tr><td><strong>발생 시점</strong></td><td>운동 12~48시간 후</td><td>운동 중 또는 직후 즉시</td></tr>
      <tr><td><strong>통증 성질</strong></td><td>뻐근하고 묵직한 느낌 · 근육 전체에 퍼짐</td><td>날카롭고 찌릿함 · 국소적으로 집중</td></tr>
      <tr><td><strong>지속 시간</strong></td><td>2~4일 내 자연 소멸</td><td>지속되거나 점점 악화</td></tr>
      <tr><td><strong>관절 부위</strong></td><td>관절 자체는 아프지 않음</td><td>관절 부위 통증 동반</td></tr>
      <tr><td><strong>대처법</strong></td><td>가벼운 걷기 · 스트레칭 · 충분한 수분</td><td>즉시 중단 · 냉찜질 · 전문가 상담</td></tr>
      <tr><td><strong>운동 가능 여부</strong></td><td>다른 부위 가능 · 같은 부위는 48시간 후</td><td>절대 운동 금지 · 병원 방문</td></tr>
    </tbody>
  </table>

  <div class="sec">첫 2주 적응 플랜 (RPE 기반 4주 점진 프로그램)</div>
  <table class="g-table">
    <thead><tr><th>주차</th><th>웨이트 강도</th><th>유산소</th><th>목표 RPE</th><th>중점 사항</th></tr></thead>
    <tbody>
      <tr>
        <td style="background:#eef6f1;font-weight:700">1주차<br><span style="font-size:6.5pt;color:#4a7c59">적응기</span></td>
        <td>{c['rm_range']} 1RM의 70%<br>{c['rep_range']} · 2세트</td>
        <td>천국의 계단 레벨 4~5 · 10분<br>스키머신 저강도 · 15분</td>
        <td class="center" style="color:#4a7c59;font-weight:700">5~6</td>
        <td style="font-size:7.5pt">자세 익히기 · 기구 사용법 숙지 · 통증 여부 확인</td>
      </tr>
      <tr>
        <td style="background:#eef3f9;font-weight:700">2주차<br><span style="font-size:6.5pt;color:#1e4d7b">적응기</span></td>
        <td>{c['rm_range']} 1RM의 80%<br>{c['rep_range']} · 3세트</td>
        <td>천국의 계단 레벨 5~6 · 12분<br>스키머신 중강도 · 18분</td>
        <td class="center" style="color:#1e4d7b;font-weight:700">6~7</td>
        <td style="font-size:7.5pt">세트 수 늘리기 · 자세 점검 · 심박수 모니터링</td>
      </tr>
      <tr>
        <td style="background:#fdf2e8;font-weight:700">3주차<br><span style="font-size:6.5pt;color:#c07020">본운동기</span></td>
        <td>{c['rm_range']} 1RM의 90%<br>{c['rep_range']} · 3세트</td>
        <td>천국의 계단 레벨 6~7 · 15분<br>스키머신 중~고강도 · 20분</td>
        <td class="center" style="color:#c07020;font-weight:700">7~8</td>
        <td style="font-size:7.5pt">목표 무게 도달 · 유산소 강도 올리기 · 식단 병행</td>
      </tr>
      <tr>
        <td style="background:#fdf0eb;font-weight:700">4주차<br><span style="font-size:6.5pt;color:#c0603a">강화기</span></td>
        <td>{c['rm_range']} 1RM 100%<br>{c['rep_range']} · 3세트</td>
        <td>천국의 계단 레벨 7~8 · 15분<br>스키머신 빠른 페이스 · 20분</td>
        <td class="center" style="color:#c0603a;font-weight:700">8~9</td>
        <td style="font-size:7.5pt">정규 루틴 완성 · 중량 점진 증가 시작 · 체성분 체크</td>
      </tr>
    </tbody>
  </table>

  <div class="sec">부위별 자주 발생하는 불편감 & 대처</div>
  <table class="g-table">
    <thead><tr><th>부위</th><th>증상</th><th>원인</th><th>대처법</th></tr></thead>
    <tbody>
      <tr><td>무릎</td><td>스쿼트 시 무릎 앞 통증</td><td>무릎이 발끝 안쪽으로 무너짐</td><td>밴드로 무릎 고정 연습 · 깊이 줄이기</td></tr>
      <tr><td>허리</td><td>레그프레스 후 허리 통증</td><td>골반 후방 경사 (엉덩이 들림)</td><td>발 위치 높이기 · 가동범위 줄이기</td></tr>
      <tr><td>어깨</td><td>숄더프레스 시 앞 어깨 통증</td><td>팔꿈치가 너무 앞으로 나옴</td><td>그립 너비 줄이기 · 팔꿈치를 귀 옆으로</td></tr>
      <tr><td>목</td><td>랫풀다운 후 목 뒤 통증</td><td>목 뒤로 바 내리기</td><td>가슴 앞으로 당기기로 변경</td></tr>
      <tr><td>손목</td><td>바벨 컬 시 손목 통증</td><td>손목 과신전</td><td>손목 중립 유지 · EZ바 or 덤벨로 변경</td></tr>
    </tbody>
  </table>

  <div class="alert-box"><strong>⚠️ 즉시 병원을 가야 하는 신호</strong> — 운동 중 가슴 통증·호흡 곤란 / 관절에서 소리와 함께 극심한 통증 / 어지러움·구토 / 운동 후 48시간 이상 지속되는 날카로운 통증. 이런 경우 즉시 운동을 중단하고 전문가와 상담하세요.</div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 11 — 4주마다 진도 체크리스트
# ═══════════════════════════════════════════════════════════
def _page11(c, member):
    name = member.get('name', '회원')
    return f"""
<div class="page">
  {_page_header('11', '4주마다 진도 체크리스트', name)}
  <div class="sec">4주 체크리스트 — 체성분 & 체력 변화 기록</div>

  <div class="check-grid">
    <div class="check-box">
      <div class="check-head">📊 체성분 변화 체크 (인바디 재측정)</div>
      <div class="check-item"><div class="chk"></div><span>체중 변화 확인 (목표 대비 ±?kg)</span></div>
      <div class="check-item"><div class="chk"></div><span>체지방률 변화 확인 (목표: -{round((c['fat_pct']-c['target_fat_pct'])/3, 1)}%/월)</span></div>
      <div class="check-item"><div class="chk"></div><span>골격근량 유지/증가 여부 확인</span></div>
      <div class="check-item"><div class="chk"></div><span>내장지방 레벨 변화 확인</span></div>
      <div class="check-item"><div class="chk"></div><span>인바디 점수 변화 확인 (목표: +3~5점)</span></div>
      <div class="check-item"><div class="chk"></div><span>BMR 변화 확인 (근육 증가 시 상승)</span></div>
    </div>
    <div class="check-box">
      <div class="check-head">💪 운동 체력 변화 체크</div>
      <div class="check-item"><div class="chk"></div><span>핵스쿼트·레그프레스 중량 증가 여부</span></div>
      <div class="check-item"><div class="chk"></div><span>체스트프레스·랫풀다운 중량 증가 여부</span></div>
      <div class="check-item"><div class="chk"></div><span>천국의 계단 레벨 상승 여부 (목표: +1~2레벨)</span></div>
      <div class="check-item"><div class="chk"></div><span>유산소 지속 시간 증가 여부</span></div>
      <div class="check-item"><div class="chk"></div><span>운동 후 회복 시간 단축 여부</span></div>
      <div class="check-item"><div class="chk"></div><span>코어 운동 횟수 증가 여부</span></div>
    </div>
    <div class="check-box">
      <div class="check-head">🥗 식단 & 생활습관 체크</div>
      <div class="check-item"><div class="chk"></div><span>하루 단백질 {c['protein_g']}g 섭취 달성</span></div>
      <div class="check-item"><div class="chk"></div><span>하루 수분 {c['water_l']}L 섭취 습관화</span></div>
      <div class="check-item"><div class="chk"></div><span>야식·술 주 1회 미만으로 줄임</span></div>
      <div class="check-item"><div class="chk"></div><span>운동 후 골든타임 단백질 섭취 습관</span></div>
      <div class="check-item"><div class="chk"></div><span>매일 수면 7시간 이상 확보</span></div>
      <div class="check-item"><div class="chk"></div><span>밀가루·단음식 주 2회 미만으로 줄임</span></div>
    </div>
    <div class="check-box">
      <div class="check-head">🎯 다음 4주 목표 설정</div>
      <div class="check-item"><div class="chk"></div><span>체지방률 목표: ___% (현재 {c['fat_pct']}%)</span></div>
      <div class="check-item"><div class="chk"></div><span>핵스쿼트 목표 중량: ___kg</span></div>
      <div class="check-item"><div class="chk"></div><span>천국의 계단 목표 레벨: ___</span></div>
      <div class="check-item"><div class="chk"></div><span>하루 운동 시간 목표: ___ 분</span></div>
      <div class="check-item"><div class="chk"></div><span>개선할 식단 습관 1가지: ___</span></div>
      <div class="check-item"><div class="chk"></div><span>다음 인바디 측정 예정일: ___</span></div>
    </div>
  </div>

  <div class="sec">월별 진도 기록표</div>
  <table class="g-table">
    <thead><tr><th>항목</th><th>현재 (시작)</th><th>4주 후</th><th>8주 후</th><th>12주 후 (목표)</th></tr></thead>
    <tbody>
      <tr><td>체중 (kg)</td><td class="center">{c['weight']}</td><td class="center">____</td><td class="center">____</td><td class="center">____</td></tr>
      <tr><td>체지방률 (%)</td><td class="center">{c['fat_pct']}</td><td class="center">____</td><td class="center">____</td><td class="center" style="color:#c0603a;font-weight:700">{c['target_fat_pct']}</td></tr>
      <tr><td>골격근량 (kg)</td><td class="center">{c['muscle']}</td><td class="center">____</td><td class="center">____</td><td class="center" style="color:#4a7c59;font-weight:700">{c['target_muscle']}</td></tr>
      <tr><td>내장지방 레벨</td><td class="center">{c['visceral']}</td><td class="center">____</td><td class="center">____</td><td class="center" style="color:#4a7c59;font-weight:700">{c['target_visceral']}</td></tr>
      <tr><td>인바디 점수</td><td class="center">{c['score']}</td><td class="center">____</td><td class="center">____</td><td class="center" style="color:#1e4d7b;font-weight:700">____</td></tr>
      <tr><td>천국의 계단 레벨</td><td class="center">____</td><td class="center">____</td><td class="center">____</td><td class="center">____</td></tr>
    </tbody>
  </table>

  <div class="pbox"><strong>📌 4주마다 체크 포인트</strong> — 4주마다 인바디를 측정하여 변화를 기록하세요. 체지방이 줄고 근육이 유지되면 올바른 방향입니다. 체중만 보지 말고 체성분 변화를 보는 것이 핵심입니다. 필요하면 루틴·식단을 조정하세요.</div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# PAGE 12 — 운동 습관 & 마음가짐 가이드
# ═══════════════════════════════════════════════════════════
def _page12(c, member):
    name = member.get('name', '회원')
    return f"""
<div class="page">
  {_page_header('12', '운동 습관 & 마음가짐 가이드', name)}
  <div class="sec">성공하는 7가지 운동 습관</div>

  <div class="habit-grid">
    <div class="habit-card">
      <div class="habit-num">HABIT 01</div>
      <div class="habit-title">고정 운동 시간 확보</div>
      <div class="habit-desc">매일 같은 시간에 운동하면 습관이 됩니다. 아침이든 저녁이든 본인 라이프스타일에 맞는 시간을 정하고 달력에 표시하세요. '나중에'는 없습니다.</div>
    </div>
    <div class="habit-card orange">
      <div class="habit-num">HABIT 02</div>
      <div class="habit-title">운동 일지 기록하기</div>
      <div class="habit-desc">오늘 한 운동, 무게, 세트, 횟수를 기록하세요. 2주 후 처음보다 얼마나 늘었는지 보이면 동기부여가 됩니다. 스마트폰 메모앱이면 충분합니다.</div>
    </div>
    <div class="habit-card green">
      <div class="habit-num">HABIT 03</div>
      <div class="habit-title">완벽보다 꾸준함 선택</div>
      <div class="habit-desc">컨디션이 나빠도 헬스장에 가세요. 30분만 해도 됩니다. '오늘 못 했다'보다 '오늘도 갔다'가 중요합니다. 3개월 기준 80%만 출석해도 변화가 옵니다.</div>
    </div>
    <div class="habit-card red">
      <div class="habit-num">HABIT 04</div>
      <div class="habit-title">단기 결과에 흔들리지 않기</div>
      <div class="habit-desc">체중은 수분·음식·생리주기 등으로 매일 1~2kg씩 변합니다. 주 1~2회 같은 조건(아침 공복)에 재세요. 4주 단위로 변화를 평가하세요.</div>
    </div>
    <div class="habit-card">
      <div class="habit-num">HABIT 05</div>
      <div class="habit-title">식단과 운동 동시에</div>
      <div class="habit-desc">운동만 열심히 하고 식단을 무시하면 결과가 절반입니다. 반대도 마찬가지입니다. 체지방 감소는 '운동 40% + 식단 60%' 공식을 기억하세요.</div>
    </div>
    <div class="habit-card orange">
      <div class="habit-num">HABIT 06</div>
      <div class="habit-title">수면 최우선 투자</div>
      <div class="habit-desc">잠이 부족하면 성장호르몬이 줄고, 코르티솔이 늘어 근육이 분해됩니다. 7~9시간 수면은 최고의 보충제입니다. 야식과 늦은 음주를 줄이세요.</div>
    </div>
    <div class="habit-card green">
      <div class="habit-num">HABIT 07</div>
      <div class="habit-title">사회적 책임감 활용</div>
      <div class="habit-desc">운동 파트너를 만들거나, 가족·친구에게 목표를 공개하세요. '누군가 보고 있다'는 심리가 포기를 막아줍니다. ITN 트레이너에게 진도를 보고하는 것도 방법입니다.</div>
    </div>
    <div class="habit-card red">
      <div class="habit-num">HABIT 07+</div>
      <div class="habit-title">스스로를 칭찬하기</div>
      <div class="habit-desc">오늘 운동을 마쳤다면 스스로를 칭찬하세요. 작은 성취를 축하하는 습관이 장기적인 동기부여의 원천입니다. 결과보다 과정을 사랑하세요.</div>
    </div>
  </div>

  <div class="motive">
    <div class="m-title">{name}님, 시작이 반입니다</div>
    <div class="m-body">
      체지방 감소는 하루아침에 되지 않습니다. 하지만 오늘 이 루틴을 손에 든 {name}님은 이미 시작했습니다.<br>
      3개월 뒤 거울 속의 자신이 달라져 있을 것입니다. 체중계 숫자보다 중요한 것은 건강해진 몸과 마음입니다.<br><br>
      <strong style="color:#f0a060;font-size:10pt">"오늘 하지 않으면 내일도 하지 않습니다. 오늘의 땀이 3개월 후의 몸을 만듭니다."</strong><br><br>
      ITN 피트니스가 응원합니다. 궁금한 점이 있으면 언제든지 트레이너에게 문의하세요.
    </div>
  </div>

  {_page_footer(c['today_str'])}
</div>"""


# ═══════════════════════════════════════════════════════════
# 메인 함수
# ═══════════════════════════════════════════════════════════
def build_html(member, inbody, goal='체지방감소'):
    c = _calc(member, inbody, goal)
    name = member.get('name', '회원')

    pages = (
        _page1(c, member, inbody) +
        _page2(c, member) +
        _page3(c, member) +
        _page4(c, member) +
        _page4b(c, member) +
        _page5(c, member) +
        _page6(c, member) +
        _page7(c, member) +
        _page8(c, member) +
        _page9(c, member) +
        _page10(c, member) +
        _page11(c, member) +
        _page12(c, member)
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>ITN 피트니스 — {name}님 맞춤 운동 루틴</title>
<style>
{_css()}
</style>
</head>
<body>
{pages}
<script>
  window.onload = function() {{
    setTimeout(function() {{ window.print(); }}, 600);
  }};
</script>
</body>
</html>"""


# WeasyPrint 레거시 호환 (사용 안 함)
def generate_routine_pdf(member, inbody):
    html = build_html(member, inbody)
    return html.encode('utf-8')
