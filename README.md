# Firebase 주문시스템 - 셀러별 배포 가이드

## 🚀 **빠른 배포 방법**

### **1. 셀러별 필수 수정 항목**

```bash
# 다음 항목들을 실제 셀러 정보로 변경하세요
```

- [ ] **셀러명** (`0000셀러` → 실제 셀러명)
- [ ] **Firebase 프로젝트 ID** (`seller1-b8a4c` → 실제 프로젝트 ID)
- [ ] **Firebase 데이터베이스 URL** (`https://seller1-b8a4c-default-rtdb.asia-southeast1.firebasedatabase.app` → 실제 URL)
- [ ] **관리자 PIN 번호** (`2001012501` → 실제 PIN)
- [ ] **입금 계좌번호** (`0000-0000-0000-0000` → 실제 계좌번호)
- [ ] **셀러 계좌명** (`0000셀러` → 실제 계좌명)

### **2. 수정할 파일들**

#### **config.js**
```javascript
const CONFIG = {
    ADMIN_PIN: "실제_PIN_번호"  // 여기만 변경
};
```

#### **index.html**
```html
<title>실제셀러명 주문 수집 페이지</title>
<!-- 입금계좌: 실제계좌번호 (실제셀러명) -->
```

#### **admin.html**
```html
<title>실제셀러명 주문 관리자 페이지</title>
<h1>실제셀러명 주문 접수 관리자</h1>

<!-- Firebase 설정 -->
projectId: "실제_프로젝트_ID",
databaseURL: "실제_데이터베이스_URL"
```

### **3. 배포 순서**

1. **셀러별 정보 수정** (위 체크리스트 완료)
2. **Git에 커밋**
3. **Netlify에 배포**
4. **Firebase 프로젝트 생성 및 설정**
5. **테스트 및 검증**

## 📋 **기능 요약**

### **고객 페이지 (index.html)**
- 주문 접수 (신규/교환/반품/취소)
- 기존 주문 정보 자동 로드
- 주문 내역 이미지 다운로드
- 관리자 페이지 접근

### **관리자 페이지 (admin.html)**
- 실시간 주문 모니터링
- 필터링 및 검색
- 페이지네이션 (30/50/100개씩)
- 일괄 상태 업데이트
- Excel 내보내기
- 7일 자동 데이터 삭제

## 🔧 **기술 스택**

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: Firebase Realtime Database
- **Storage**: Firebase Storage
- **Deployment**: Netlify
- **Excel**: XLSX.js 라이브러리

## 📞 **지원**

**다음에 요청할 때는:**
> "이거 뭐 바꿔줘"

**이렇게 말씀하시면 됩니다!** 🎯

---

**마지막 업데이트**: 2024년 1월
**버전**: v1.0.0

