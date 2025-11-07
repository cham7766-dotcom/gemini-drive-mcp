// 전역 변수
let currentCode = '';
let currentLanguage = '';
let currentSessionId = null;
let currentProjectName = '';
let currentImageBase64 = null;
let modifyImageBase64 = null;

// DOM 요소
const promptInput = document.getElementById('prompt');
const projectNameInput = document.getElementById('projectName');
const languageSelect = document.getElementById('language');
const generateBtn = document.getElementById('generateBtn');
const resultSection = document.getElementById('resultSection');
const codeOutput = document.getElementById('codeOutput');
const explanation = document.getElementById('explanation');
const explanationText = document.getElementById('explanationText');
const copyBtn = document.getElementById('copyBtn');
const githubLink = document.getElementById('githubLink');
const modifyPrompt = document.getElementById('modifyPrompt');
const modifyBtn = document.getElementById('modifyBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const toast = document.getElementById('toast');
const status = document.getElementById('status');

// 이미지 첨부 요소
const imageInput = document.getElementById('imageInput');
const attachImageBtn = document.getElementById('attachImageBtn');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const removeImageBtn = document.getElementById('removeImageBtn');

// 수정용 이미지 첨부 요소
const modifyImageInput = document.getElementById('modifyImageInput');
const attachModifyImageBtn = document.getElementById('attachModifyImageBtn');
const modifyImagePreview = document.getElementById('modifyImagePreview');
const modifyPreviewImg = document.getElementById('modifyPreviewImg');
const removeModifyImageBtn = document.getElementById('removeModifyImageBtn');

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupImageHandlers();
});

// 이미지 핸들러 설정
function setupImageHandlers() {
    // 첨부 버튼 클릭
    attachImageBtn.addEventListener('click', () => imageInput.click());
    attachModifyImageBtn.addEventListener('click', () => modifyImageInput.click());

    // 이미지 선택 시
    imageInput.addEventListener('change', (e) => handleImageSelect(e, previewImg, imagePreview, (base64) => {
        currentImageBase64 = base64;
    }));

    modifyImageInput.addEventListener('change', (e) => handleImageSelect(e, modifyPreviewImg, modifyImagePreview, (base64) => {
        modifyImageBase64 = base64;
    }));

    // 제거 버튼
    removeImageBtn.addEventListener('click', () => {
        currentImageBase64 = null;
        imagePreview.style.display = 'none';
        imageInput.value = '';
    });

    removeModifyImageBtn.addEventListener('click', () => {
        modifyImageBase64 = null;
        modifyImagePreview.style.display = 'none';
        modifyImageInput.value = '';
    });
}

// 이미지 선택 처리
function handleImageSelect(event, imgElement, previewElement, callback) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const base64 = e.target.result;
            imgElement.src = base64;
            previewElement.style.display = 'block';
            callback(base64);
        };
        reader.readAsDataURL(file);
    }
}

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
    const projectName = projectNameInput.value.trim() || 'generated-project';

    if (!prompt) {
        showToast('명령을 입력해주세요', 'error');
        return;
    }

    showLoading(true);
    generateBtn.disabled = true;

    try {
        const requestBody = {
            prompt: prompt,
            language: languageSelect.value || null,
            context_id: currentSessionId,
            project_name: projectName,
            push_to_github: true
        };

        // 이미지가 있으면 추가
        if (currentImageBase64) {
            requestBody.image = currentImageBase64;
        }

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (data.success) {
            currentCode = data.code;
            currentLanguage = data.language;
            currentSessionId = data.session_id;
            currentProjectName = projectName;

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

            // GitHub 링크 표시
            if (data.github_url) {
                githubLink.href = data.github_url;
                githubLink.style.display = 'inline-block';
                showToast(`코드 생성 완료! GitHub에 푸시되었습니다`, 'success');
            } else {
                showToast('코드 생성 완료!', 'success');
            }

            resultSection.style.display = 'block';

            // 이미지 미리보기 초기화
            currentImageBase64 = null;
            imagePreview.style.display = 'none';
            imageInput.value = '';
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
        const requestBody = {
            original_code: currentCode,
            modification: modification,
            project_name: currentProjectName,
            push_to_github: true
        };

        // 수정용 이미지가 있으면 추가
        if (modifyImageBase64) {
            requestBody.image = modifyImageBase64;
        }

        const response = await fetch('/api/modify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
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

            // GitHub 링크 업데이트
            if (data.github_url) {
                githubLink.href = data.github_url;
                showToast('코드 수정 완료! GitHub에 푸시되었습니다', 'success');
            } else {
                showToast('코드가 수정되었습니다', 'success');
            }

            modifyPrompt.value = '';

            // 이미지 미리보기 초기화
            modifyImageBase64 = null;
            modifyImagePreview.style.display = 'none';
            modifyImageInput.value = '';
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
