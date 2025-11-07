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
const filesList = document.getElementById('filesList');
const refreshBtn = document.getElementById('refreshBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const toast = document.getElementById('toast');
const status = document.getElementById('status');
const oauthBtn = document.getElementById('oauthBtn');

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadFiles();
});

// OAuth 인증 버튼
oauthBtn.addEventListener('click', async () => {
    showLoading(true);
    try {
        const response = await fetch('/api/oauth/authorize');
        const data = await response.json();

        if (data.success && data.auth_url) {
            // 새 창으로 OAuth URL 열기
            const authWindow = window.open(data.auth_url, 'OAuth 인증', 'width=600,height=700');

            // 5초마다 상태 확인
            const checkInterval = setInterval(async () => {
                const statusResponse = await fetch('/api/oauth/status');
                const statusData = await statusResponse.json();

                if (statusData.authenticated) {
                    clearInterval(checkInterval);
                    if (authWindow) authWindow.close();
                    showToast('Drive 인증 완료!', 'success');
                    checkHealth();
                    loadFiles();
                }
            }, 3000);

            // 2분 후 타임아웃
            setTimeout(() => {
                clearInterval(checkInterval);
            }, 120000);
        } else {
            showToast(data.error || 'OAuth 인증 시작 실패', 'error');
        }
    } catch (error) {
        console.error('OAuth error:', error);
        showToast('OAuth 인증 중 오류 발생', 'error');
    } finally {
        showLoading(false);
    }
});

// 헬스 체크
async function checkHealth() {
    const geminiStatusValue = document.getElementById('geminiStatusValue');
    const driveStatusValue = document.getElementById('driveStatusValue');

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

        // Drive 상태
        if (data.drive_ready) {
            driveStatusValue.textContent = '✓ 연결됨';
            driveStatusValue.className = 'status-value ready';
            oauthBtn.style.display = 'none';
        } else {
            driveStatusValue.textContent = '✗ OAuth 필요';
            driveStatusValue.className = 'status-value not-ready';
            oauthBtn.style.display = 'inline-block';
        }

        // 전체 상태
        if (data.status === 'ok' && data.gemini_ready) {
            status.textContent = '준비됨';
            status.style.background = '#4caf50';
        } else {
            status.textContent = '일부 기능 제한';
            status.style.background = '#ff9800';
        }
    } catch (error) {
        status.textContent = '오류';
        status.style.background = '#f44336';
        geminiStatusValue.textContent = '✗ 오류';
        geminiStatusValue.className = 'status-value error';
        driveStatusValue.textContent = '✗ 오류';
        driveStatusValue.className = 'status-value error';
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

// Drive에 저장
saveBtn.addEventListener('click', async () => {
    const filename = prompt('파일명을 입력하세요:', `code.${currentLanguage}`);
    if (!filename) return;

    showLoading(true);
    saveBtn.disabled = true;

    try {
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: currentCode,
                filename: filename
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Drive에 저장되었습니다!', 'success');
            loadFiles(); // 파일 목록 새로고침

            // 파일 링크 열기
            if (data.web_view_link) {
                setTimeout(() => {
                    if (confirm('Drive에서 파일을 열까요?')) {
                        window.open(data.web_view_link, '_blank');
                    }
                }, 500);
            }
        } else {
            showToast(data.error || '저장 실패', 'error');
        }
    } catch (error) {
        console.error('Save error:', error);
        showToast('저장 중 오류 발생', 'error');
    } finally {
        showLoading(false);
        saveBtn.disabled = false;
    }
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

// 파일 목록 로드
async function loadFiles() {
    try {
        const response = await fetch('/api/files');
        const data = await response.json();

        if (data.success && data.files && data.files.length > 0) {
            filesList.innerHTML = data.files.map(file => `
                <div class="file-item" onclick="loadFile('${file.id}')">
                    <div class="file-name">${file.name}</div>
                    <div class="file-date">${formatDate(file.created_time)}</div>
                </div>
            `).join('');
        } else {
            filesList.innerHTML = '<p class="empty-message">저장된 파일이 없습니다</p>';
        }
    } catch (error) {
        console.error('Load files error:', error);
        filesList.innerHTML = '<p class="empty-message">파일 목록을 불러올 수 없습니다</p>';
    }
}

// 파일 불러오기
async function loadFile(fileId) {
    showLoading(true);

    try {
        const response = await fetch(`/api/file/${fileId}`);
        const data = await response.json();

        if (data.success) {
            currentCode = data.content;
            currentLanguage = data.language;

            // 코드 표시
            codeOutput.textContent = data.content;
            codeOutput.className = `language-${data.language}`;
            Prism.highlightElement(codeOutput);

            explanation.style.display = 'none';
            resultSection.style.display = 'block';

            showToast(`${data.filename} 불러오기 완료`, 'success');
        } else {
            showToast(data.error || '파일 불러오기 실패', 'error');
        }
    } catch (error) {
        console.error('Load file error:', error);
        showToast('파일 불러오기 중 오류 발생', 'error');
    } finally {
        showLoading(false);
    }
}

// 파일 목록 새로고침
refreshBtn.addEventListener('click', loadFiles);

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
