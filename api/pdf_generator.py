"""
인바디 수치 기반 맞춤 운동 루틴 PDF 생성기
WeasyPrint + HTML → PDF
"""
import io
from datetime import date


def get_routine(fat_pct):
    if fat_pct and float(fat_pct) >= 30:
        reps = "12~15회"
        core_reps = "15~20회"
    elif fat_pct and float(fat_pct) >= 25:
        reps = "10~12회"
        core_reps = "15회"
    else:
        reps = "8~10회"
        core_reps = "12~15회"

    return {
        "월": [
            ("워밍업", "에코바이크", "-", "10분", "싸이클·런닝머신"),
            ("웨이트", "핵스쿼트", "3", reps, "브이스쿼트·스미스"),
            ("웨이트", "45도 파워레그프레스", "3", "15회", "버티컬레그프레스"),
            ("웨이트", "시티드레그컬", "3", reps, "레그컬"),
            ("웨이트", "힙쓰러스트", "3", "15회", "글루트·몬스터글루트"),
            ("웨이트", "토탈힙", "3", "15회", "스탠딩아웃싸이"),
            ("웨이트", "아웃타이이너싸이", "2", "20회", "스탠딩아웃싸이"),
            ("코어", "업도미널", "3", core_reps, "행잉 니레이즈"),
            ("코어★", "AB스윙", "3", core_reps, "토르소·크로스케이블"),
            ("마무리", "천국의 계단", "-", "15분", "인클라인 런닝머신"),
        ],
        "화": [
            ("워밍업", "무동력 트레드밀", "-", "8분", "에코바이크"),
            ("웨이트", "시티드체스트프레스", "3", reps, "벤치프레스·멀티프레스"),
            ("웨이트", "랫풀다운", "3", reps, "하이랫풀·와이드풀다운"),
            ("웨이트", "시티드로우", "3", reps, "로우로우·티바로우"),
            ("웨이트", "숄더프레스", "3", reps, "덤벨 숄더프레스"),
            ("웨이트", "팩덱플라이", "2", "15회", "크로스케이블 플라이"),
            ("코어★", "토르소", "3", core_reps+"(좌우)", "AB스윙"),
            ("코어★", "크로스케이블", "3", "15회(좌우)", "토르소"),
            ("코어", "하이퍼익스텐션", "2", "15회", "백익스텐션"),
            ("마무리", "스키머신", "-", "20분", "엘립티컬"),
        ],
        "목": [
            ("워밍업", "에코바이크", "-", "10분", "싸이클·런닝머신"),
            ("웨이트", "브이스쿼트", "3", reps, "핵스쿼트·스미스"),
            ("웨이트", "버티컬레그프레스", "3", "15회", "45도 파워레그프레스"),
            ("웨이트", "몬스터글루트", "3", "15회", "글루트·힙쓰러스트"),
            ("웨이트", "레그컬", "3", reps, "시티드레그컬"),
            ("웨이트", "덩키킥", "3", "15회(각)", "토탈힙"),
            ("코어", "업도미널", "3", core_reps, "행잉 니레이즈"),
            ("코어★", "AB스윙", "3", core_reps, "토르소"),
            ("마무리", "천국의 계단", "-", "15분", "인클라인 런닝머신"),
        ],
        "금": [
            ("워밍업", "무동력 트레드밀", "-", "8분", "에코바이크"),
            ("웨이트", "인클라인벤치프레스", "3", reps, "시티드체스트프레스"),
            ("웨이트", "와이드리어풀다운", "3", reps, "랫풀다운"),
            ("웨이트", "로우로우 or 티바로우", "3", reps, "시티드로우"),
            ("웨이트", "레터럴레이즈(덤벨)", "3", "15회", "멀티레이즈"),
            ("웨이트", "암컬(덤벨)", "2", "15회", "바벨컬"),
            ("코어★", "토르소", "3", core_reps+"(좌우)", "AB스윙"),
            ("코어★", "크로스케이블", "3", "15회(좌우)", "토르소"),
            ("코어", "백익스텐션", "2", "15회", "하이퍼익스텐션"),
            ("마무리", "엘립티컬", "-", "20분", "스키머신"),
        ],
    }


def get_goals(inbody):
    fat_pct = float(inbody.get('body_fat_pct') or 32)
    muscle = float(inbody.get('muscle_mass') or 20)
    visceral = int(inbody.get('visceral_fat_level') or 9)
    fat_mass = float(inbody.get('body_fat_mass') or 18)

    target_fat_pct = max(fat_pct - 4.7, 18)
    target_muscle = muscle + 0.6
    target_visceral = max(visceral - 3, 4)
    target_fat_mass = round(fat_mass - 3.7, 1)

    return {
        'fat_pct': f"{fat_pct}% → {target_fat_pct:.1f}% 이하",
        'fat_mass': f"{fat_mass}kg → {target_fat_mass}kg",
        'muscle': f"{muscle}kg → {target_muscle:.1f}kg 이상 유지",
        'visceral': f"레벨 {visceral} → 레벨 {target_visceral}",
        'fat_pct_bar': min(int((fat_pct - target_fat_pct) / fat_pct * 100 + 60), 90),
        'muscle_bar': 85,
        'visceral_bar': min(int((visceral - target_visceral) / visceral * 100 + 50), 80),
    }


def build_html(member, inbody):
    name = member.get('name', '회원')
    age = member.get('age', '')
    gender = member.get('gender', '')
    measured = inbody.get('measured_at', date.today().isoformat())
    weight = inbody.get('weight', '')
    muscle = inbody.get('muscle_mass', '')
    fat_mass = inbody.get('body_fat_mass', '')
    fat_pct = inbody.get('body_fat_pct', '')
    visceral = inbody.get('visceral_fat_level', '')
    bmi = inbody.get('bmi', '')
    score = inbody.get('inbody_score', '')
    bmr = inbody.get('bmr', '')

    routine = get_routine(fat_pct)
    goals = get_goals(inbody)

    if fat_pct and float(fat_pct) >= 30:
        body_type = "마른비만형"
        body_desc = "BMI는 정상이지만 체지방률이 높은 패턴. 토르소·AB스윙·크로스케이블이 복부·옆구리 지방 공략 핵심."
    elif fat_pct and float(fat_pct) >= 25:
        body_type = "체지방 과다형"
        body_desc = "체지방 감소와 근육 유지를 동시에. 복합 관절 운동 중심으로 고횟수 진행."
    else:
        body_type = "근육 부족형"
        body_desc = "근육량 증가가 최우선. 무게 점진적 증가, 충분한 단백질 섭취 필수."

    def routine_table(day, exercises):
        color_map = {
            "워밍업": "#c0603a", "웨이트": "#1e4d7b",
            "코어": "#9a6208", "코어★": "#c0603a", "마무리": "#4a7c59",
        }
        rows = ""
        for cat, name_ex, sets, reps_ex, alt in exercises:
            color = color_map.get(cat, "#1e4d7b")
            rows += f"""
            <tr>
              <td style="color:{color};font-weight:700;font-size:8pt;white-space:nowrap">{cat}</td>
              <td style="font-weight:600">{name_ex}</td>
              <td style="text-align:center">{sets}</td>
              <td style="text-align:center;font-weight:700;color:#1e4d7b">{reps_ex}</td>
              <td style="color:#4a7c59;font-size:7.5pt">{alt}</td>
            </tr>"""
        return f"""
        <div class="day-block">
          <div class="day-title">{day}요일</div>
          <table class="ex-table">
            <thead><tr><th>구분</th><th>운동</th><th>세트</th><th>횟수</th><th>대체기구</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>"""

    routine_html = ""
    for day, exs in routine.items():
        routine_html += routine_table(day, exs)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
  @page {{ size: 210mm 297mm; margin: 12mm 12mm 16mm 12mm; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Noto Sans CJK KR', sans-serif; font-size: 9pt; color: #2a2a2a; background: #f7f6f3; line-height: 1.6; }}
  .header {{ background: #1e3a5f; color: white; padding: 8mm 10mm; margin-bottom: 6mm; border-radius: 4pt; display: flex; justify-content: space-between; align-items: center; }}
  .header-left .gym {{ font-size: 8pt; color: #a0bcd8; margin-bottom: 2mm; letter-spacing: 1px; }}
  .header-left .title {{ font-size: 18pt; font-weight: 900; line-height: 1.2; }}
  .header-left .title span {{ color: #f0a060; }}
  .header-left .sub {{ font-size: 8pt; color: #a0bcd8; margin-top: 2mm; }}
  .header-right {{ text-align: right; }}
  .score-val {{ font-size: 32pt; font-weight: 900; color: #f0a060; line-height: 1; }}
  .score-label {{ font-size: 7.5pt; color: #a0bcd8; margin-top: 1.5mm; }}
  .sec {{ font-size: 8pt; font-weight: 900; color: #1e4d7b; border-left: 3pt solid #c0603a; padding-left: 3mm; margin: 5mm 0 3mm; letter-spacing: 0.8px; text-transform: uppercase; }}
  .stats {{ display: flex; gap: 2.5mm; margin-bottom: 5mm; }}
  .stat {{ flex: 1; background: white; border-top: 2.5pt solid #1e4d7b; border-radius: 4pt; padding: 3mm 2mm; text-align: center; box-shadow: 0 1pt 3pt rgba(0,0,0,0.06); }}
  .stat.alert {{ border-top-color: #c0603a; }}
  .stat-v {{ font-size: 12pt; font-weight: 900; color: #1e4d7b; white-space: nowrap; }}
  .stat.alert .stat-v {{ color: #c0603a; }}
  .stat-l {{ font-size: 6.5pt; color: #8a8078; margin-top: 1mm; }}
  .stat-c {{ font-size: 6.5pt; color: #c0603a; font-weight: 700; margin-top: 1mm; }}
  .pbox {{ background: #eef3f9; border: 0.8pt solid #c2d3e5; border-radius: 5pt; padding: 3.5mm 4.5mm; font-size: 8pt; line-height: 1.85; margin-bottom: 4mm; }}
  .pbox strong {{ color: #1e4d7b; }}
  .goal-row {{ display: flex; align-items: center; gap: 3mm; margin-bottom: 2.5mm; }}
  .gl {{ font-size: 7.5pt; color: #5a554e; min-width: 18mm; }}
  .gb-wrap {{ flex: 1; height: 6pt; background: #e2ded8; border-radius: 3pt; overflow: hidden; }}
  .gb {{ height: 100%; border-radius: 3pt; }}
  .gv {{ font-size: 7.5pt; font-weight: 700; color: #1e4d7b; min-width: 48mm; text-align: right; white-space: nowrap; }}
  .routine-grid {{ display: flex; flex-wrap: wrap; gap: 4mm; margin-bottom: 5mm; }}
  .day-block {{ flex: 1; min-width: 85mm; background: white; border-radius: 5pt; border: 0.6pt solid #e2ded8; box-shadow: 0 1pt 3pt rgba(0,0,0,0.05); overflow: hidden; }}
  .day-title {{ background: #1e4d7b; color: white; font-size: 9pt; font-weight: 900; padding: 2.5mm 4mm; }}
  .ex-table {{ width: 100%; border-collapse: collapse; font-size: 7.5pt; }}
  .ex-table thead tr {{ background: #eef3f9; }}
  .ex-table th {{ padding: 2mm; text-align: center; font-size: 7pt; color: #1e4d7b; font-weight: 700; border-bottom: 0.6pt solid #e2ded8; }}
  .ex-table td {{ padding: 2mm 2.5mm; border-bottom: 0.4pt solid #eeece8; vertical-align: middle; }}
  .ex-table tr:last-child td {{ border-bottom: none; }}
  .ex-table tr:nth-child(even) td {{ background: #fafafa; }}
  .guide-row {{ display: flex; gap: 3mm; margin-bottom: 4mm; }}
  .guide-box {{ flex: 1; background: white; border-radius: 5pt; padding: 3.5mm 4mm; border: 0.6pt solid #e2ded8; }}
  .guide-title {{ font-size: 8pt; font-weight: 900; color: #1e4d7b; margin-bottom: 2.5mm; padding-bottom: 2mm; border-bottom: 0.6pt solid #e2ded8; }}
  .guide-item {{ font-size: 7.5pt; color: #3a3a3a; margin-bottom: 1.5mm; line-height: 1.7; }}
  .guide-item strong {{ color: #1e4d7b; }}
  .timeline {{ margin-bottom: 4mm; }}
  .tl-item {{ display: flex; gap: 0; margin-bottom: 2mm; border-radius: 4pt; overflow: hidden; border: 0.6pt solid #e2ded8; }}
  .tl-left {{ width: 24mm; background: #1e4d7b; color: white; padding: 3mm 2mm; text-align: center; display: flex; flex-direction: column; justify-content: center; }}
  .tl-left.green {{ background: #4a7c59; }}
  .tl-left.terra {{ background: #c0603a; }}
  .tl-left.gold {{ background: #9a6208; }}
  .tl-time {{ font-size: 7.5pt; font-weight: 900; }}
  .tl-sub {{ font-size: 6pt; color: rgba(255,255,255,0.75); margin-top: 1mm; }}
  .tl-right {{ flex: 1; background: white; padding: 3mm 4mm; font-size: 7.5pt; line-height: 1.8; color: #3a3a3a; }}
  .tip {{ background: #fdf6ec; border-left: 3pt solid #d4900a; padding: 3.5mm 4.5mm; font-size: 7.5pt; color: #5a440a; border-radius: 0 5pt 5pt 0; line-height: 1.85; margin-bottom: 4mm; }}
  .tip strong {{ color: #9a6208; }}
  .page-break {{ page-break-after: always; }}
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <div class="gym">ITN 피트니스 · 동해 · Body Alignment Specialist</div>
    <div class="title">복부·옆구리 집중 <span>맞춤 운동 루틴</span></div>
    <div class="sub">{age}세 {gender} · {body_type} · 체지방 감소 프로그램 · {measured}</div>
  </div>
  <div class="header-right">
    <div class="score-val">{score}<span style="font-size:14pt;color:#7a9ab8">/100</span></div>
    <div class="score-label">인바디 점수</div>
  </div>
</div>

<div class="stats">
  <div class="stat"><div class="stat-v">{weight}<span style="font-size:8pt">kg</span></div><div class="stat-l">체중</div></div>
  <div class="stat"><div class="stat-v">{muscle}<span style="font-size:8pt">kg</span></div><div class="stat-l">골격근량</div><div class="stat-c">목표 +0.6kg</div></div>
  <div class="stat alert"><div class="stat-v">{fat_pct}<span style="font-size:8pt">%</span></div><div class="stat-l">체지방률</div></div>
  <div class="stat alert"><div class="stat-v">{fat_mass}<span style="font-size:8pt">kg</span></div><div class="stat-l">체지방량</div></div>
  <div class="stat alert"><div class="stat-v">레벨 {visceral}</div><div class="stat-l">내장지방</div></div>
  <div class="stat"><div class="stat-v">{bmi}</div><div class="stat-l">BMI</div></div>
  <div class="stat"><div class="stat-v">{bmr}<span style="font-size:7pt">kcal</span></div><div class="stat-l">기초대사량</div></div>
</div>

<div class="pbox">
  <strong>💡 {name}님 핵심 포인트</strong><br>
  {body_desc} 적정 중량 고횟수 (15회↑)로 진행하고, <strong>토르소 + AB스윙 + 크로스케이블</strong>은 매 운동 시 반드시 포함하세요.
</div>

<div class="sec">3개월 목표</div>
<div class="goal-row"><div class="gl">체지방률</div><div class="gb-wrap"><div class="gb" style="width:{goals['fat_pct_bar']}%;background:linear-gradient(90deg,#1e4d7b,#c0603a)"></div></div><div class="gv">{goals['fat_pct']}</div></div>
<div class="goal-row"><div class="gl">체지방량</div><div class="gb-wrap"><div class="gb" style="width:80%;background:linear-gradient(90deg,#1e4d7b,#c0603a)"></div></div><div class="gv">{goals['fat_mass']}</div></div>
<div class="goal-row"><div class="gl">골격근량</div><div class="gb-wrap"><div class="gb" style="width:{goals['muscle_bar']}%;background:#1e4d7b"></div></div><div class="gv">{goals['muscle']}</div></div>
<div class="goal-row"><div class="gl">내장지방</div><div class="gb-wrap"><div class="gb" style="width:{goals['visceral_bar']}%;background:linear-gradient(90deg,#4a7c59,#d4900a)"></div></div><div class="gv">{goals['visceral']}</div></div>

<div class="page-break"></div>

<div class="sec" style="margin-top:0">💪 요일별 운동 루틴</div>
<div class="routine-grid">
  {routine_html}
</div>

<div class="sec">⚖️ 운동 강도 기준</div>
<div class="guide-row">
  <div class="guide-box">
    <div class="guide-title">웨이트 기본 공식</div>
    <div class="guide-item"><strong>무게</strong> — 1RM의 55~65%</div>
    <div class="guide-item"><strong>횟수</strong> — 12~15회 / 코어 15~20회</div>
    <div class="guide-item"><strong>세트</strong> — 주운동 3세트 / 보조 2세트</div>
    <div class="guide-item"><strong>세트 간 휴식</strong> — 45~60초</div>
    <div class="guide-item"><strong>무게 점검</strong> — 2주마다 2.5~5kg씩</div>
  </div>
  <div class="guide-box">
    <div class="guide-title">유산소 기준</div>
    <div class="guide-item"><strong>천국의 계단</strong> — 레벨 6~8 · 15분</div>
    <div class="guide-item"><strong>스키머신</strong> — 중간~빠른 페이스 · 20분</div>
    <div class="guide-item"><strong>인클라인 런닝머신</strong> — 경사 8~12도</div>
    <div class="guide-item"><strong>목표 심박수</strong> — 최대심박수의 60~70%</div>
    <div class="guide-item"><strong>지방연소</strong> — 12분 이후 본격 시작</div>
  </div>
  <div class="guide-box">
    <div class="guide-title">통증 vs 근육통</div>
    <div class="guide-item">✅ <strong>정상</strong> — 12~48시간 뒤 뻐근함, 2~4일 소멸</div>
    <div class="guide-item">⚠️ <strong>즉시 중단</strong> — 운동 중 찌릿·날카로운 통증</div>
    <div class="guide-item">💧 <strong>수분</strong> — 15~20분마다 150~200ml</div>
  </div>
</div>

<div class="page-break"></div>

<div class="sec" style="margin-top:0">🥗 하루 식단 타임라인</div>
<div class="timeline">
  <div class="tl-item">
    <div class="tl-left"><div class="tl-time">기상 직후</div><div class="tl-sub">아침 전</div></div>
    <div class="tl-right"><strong>알칼리 소금물</strong> — 따뜻한 물 200~300ml + 소금 0.5~1g · 수분 보충 + 신진대사 활성화<br><span style="color:#c0603a;font-size:7pt">⚠️ 고혈압이면 소금 생략</span></div>
  </div>
  <div class="tl-item">
    <div class="tl-left"><div class="tl-time">아침</div><div class="tl-sub">운동 1.5~2시간 전</div></div>
    <div class="tl-right"><strong>잡곡밥 반공기 + 달걀 2개 + 채소</strong> — 복합탄수화물로 에너지 안정적 공급</div>
  </div>
  <div class="tl-item">
    <div class="tl-left terra"><div class="tl-time">운동 중</div><div class="tl-sub">시작~종료</div></div>
    <div class="tl-right">15~20분마다 물 <strong>150~200ml</strong> · 이온음료·단백질바 ❌</div>
  </div>
  <div class="tl-item">
    <div class="tl-left green"><div class="tl-time">운동 직후</div><div class="tl-sub">30분 내 ★골든타임</div></div>
    <div class="tl-right"><strong>단백질 쉐이크 or 두유 1팩 + 바나나 반개</strong> — 근육 합성 최고조, 단백질 15~20g 빠르게</div>
  </div>
  <div class="tl-item">
    <div class="tl-left gold"><div class="tl-time">점심·저녁</div><div class="tl-sub">운동 후 1~2시간</div></div>
    <div class="tl-right"><strong>닭가슴살 or 생선 150g + 채소 반찬</strong> — 라면·빵·술 ❌</div>
  </div>
</div>

<div class="tip">
  <strong>3개월 핵심 요약</strong> — 하루 1,250kcal 섭취 + 운동 370kcal 소모 = <strong>약 315kcal 적자</strong>.
  밀가루·술·단음식 줄이기만 해도 내장지방 빠르게 감소. 3개월 꾸준히 하면 체지방률 목표 달성 가능합니다. 💪
</div>

<div style="text-align:center;font-size:7.5pt;color:#8a8078;margin-top:5mm;padding-top:3mm;border-top:0.5pt solid #c8c2ba">
  ITN 피트니스 · 동해 · Body Alignment Specialist · "사람이 먼저, 시스템이 지킨다" · {date.today().strftime('%Y.%m.%d')}
</div>

</body>
</html>"""
    return html


def generate_routine_pdf(member, inbody):
    import weasyprint
    html = build_html(member, inbody)
    pdf_bytes = weasyprint.HTML(string=html).write_pdf()
    return pdf_bytes
