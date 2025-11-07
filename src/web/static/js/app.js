// 전역 변수
let currentCode = '';
let currentLanguage = '';
let currentSessionId = null;

// DOM 요소
const promptInput = document.getElementById('prompt');
const languageSelect = document.getElementById('language');
const generateBtn = document.getElementById('generateBtn');
const resultSection = document.getElementById('resultSection');
const codeOutput = document.getElementById('codeOutput');
const explanation = document.getElementById('explanation');
const explanationText = document.getElementById('explanationText');
const copyBtn = document.getElementById('copyBtn');
const saveBtn = document.getElementById('saveBtn');
const modifyPrompt = document.getElementById('modifyPrompt');
const modifyBtn = document.getElementById('modifyBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const toast = document.getElementById('toast');
const status = document.getElementById('status');

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
});

// 헬스 체크
async function checkHealth() {
    const geminiStatusValue = document.getElementById('geminiStatusValue');

    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        // Gemini 상태
        if (data.gemini_ready) {
            geminiStatusValue.textContent = '✓ 사용 가능';
            geminiStatusValue.className = 'status-value ready';
        } else {
            geminiStatusValue.textContent = '✗ 사용 불가';
            geminiStatusValue.className = 'status-value not-ready';
        }

        // 전체 상태
        if (data.status === 'ok' && data.gemini_ready) {
            status.textContent = '준비됨';
            status.style.background = '#4caf50';
        } else {
            status.textContent = 'Gemini API 설정 필요';
            status.style.background = '#ff9800';
        }
    } catch (error) {
        status.textContent = '오류';
        status.style.background = '#f44336';
        geminiStatusValue.textContent = '✗ 오류';
        geminiStatusValue.className = 'status-value error';
        console.error('Health check failed:', error);
    }
}

// 코드 생성
generateBtn.addEventListener('click', async () => {
    const prompt = promptInput.value.trim();
    if (!prompt) {
        showToast('명령을 입력해주세요', 'error');
        return;
    }

    showLoading(true);
    generateBtn.disabled = true;

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                language: languageSelect.value || null,
                context_id: currentSessionId
            })
        });

        const data = await response.json();

        if (data.success) {
            currentCode = data.code;
            currentLanguage = data.language;
            currentSessionId = data.session_id;

            // 코드 표시
            codeOutput.textContent = data.code;
            codeOutput.className = `language-${data.language}`;
            Prism.highlightElement(codeOutput);

            // 설명 표시
            if (data.explanation) {
                explanationText.textContent = data.explanation;
                explanation.style.display = 'block';
            } else {
                explanation.style.display = 'none';
            }

            resultSection.style.display = 'block';
            showToast('코드 생성 완료!', 'success');
        } else {
            showToast(data.error || '코드 생성 실패', 'error');
        }
    } catch (error) {
        console.error('Generate error:', error);
        showToast('서버 오류가 발생했습니다', 'error');
    } finally {
        showLoading(false);
        generateBtn.disabled = false;
    }
});

// 코드 복사
copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(currentCode).then(() => {
        showToast('코드가 복사되었습니다', 'success');
    }).catch(() => {
        showToast('복사 실패', 'error');
    });
});

// 다운로드
saveBtn.addEventListener('click', () => {
    const filename = prompt('파일명을 입력하세요:', `code.${currentLanguage}`);
    if (!filename) return;

    // Blob 생성 및 다운로드
    const blob = new Blob([currentCode], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    showToast('파일이 다운로드되었습니다!', 'success');
});

// 코드 수정
modifyBtn.addEventListener('click', async () => {
    const modification = modifyPrompt.value.trim();
    if (!modification) {
        showToast('수정 요청을 입력해주세요', 'error');
        return;
    }

    showLoading(true);
    modifyBtn.disabled = true;

    try {
        const response = await fetch('/api/modify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                original_code: currentCode,
                modification: modification
            })
        });

        const data = await response.json();

        if (data.success) {
            currentCode = data.modified_code;

            // 수정된 코드 표시
            codeOutput.textContent = data.modified_code;
            Prism.highlightElement(codeOutput);

            // 설명 표시
            if (data.explanation) {
                explanationText.textContent = data.explanation;
                explanation.style.display = 'block';
            }

            modifyPrompt.value = '';
            showToast('코드가 수정되었습니다', 'success');
        } else {
            showToast(data.error || '수정 실패', 'error');
        }
    } catch (error) {
        console.error('Modify error:', error);
        showToast('수정 중 오류 발생', 'error');
    } finally {
        showLoading(false);
        modifyBtn.disabled = false;
    }
});


// 로딩 표시
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

// Toast 알림
function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 날짜 포맷
function formatDate(dateString) {
    if (!dateString) return '날짜 없음';

    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return '방금 전';
    if (minutes < 60) return `${minutes}분 전`;
    if (hours < 24) return `${hours}시간 전`;
    if (days < 7) return `${days}일 전`;

    return date.toLocaleDateString('ko-KR');
}

// Enter 키로 생성
promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        generateBtn.click();
    }
});
