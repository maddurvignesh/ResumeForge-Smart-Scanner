/* ==========================================================================
   ResumeForge Frontend Engine - AJAX upload, Dashboard rendering
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // State Variables
    let selectedFile = null;
    let geminiApiKey = localStorage.getItem('resu_scan_api_key') || '';

    // DOM Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('resume');
    const filePreview = document.getElementById('file-preview');
    const fileNameText = document.getElementById('file-name-text');
    const fileSizeText = document.getElementById('file-size-text');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const dropzoneContent = dropzone.querySelector('.dropzone-content');
    const fileIconType = document.getElementById('file-icon-type');

    const form = document.getElementById('analyze-form');
    const jobDescription = document.getElementById('job-description');
    const submitBtn = document.getElementById('submit-btn');

    const welcomeView = document.getElementById('welcome-view');
    const loadingView = document.getElementById('loading-view');
    const resultsView = document.getElementById('results-view');

    const apiBtn = document.getElementById('api-key-btn');
    const apiModal = document.getElementById('api-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const saveApiKeyBtn = document.getElementById('save-api-key-btn');
    const clearApiKeyBtn = document.getElementById('clear-api-key-btn');
    const modalApiKeyInput = document.getElementById('modal-api-key');

    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    const toast = document.getElementById('toast');

    // Initialize API key status button look
    updateApiButtonState();

    /* ==========================================================================
       Drag and Drop Events
       ========================================================================== */
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            handleFileSelection(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length) {
            handleFileSelection(fileInput.files[0]);
        }
    });

    removeFileBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        clearFileSelection();
    });

    function handleFileSelection(file) {
        const allowedExtensions = ['pdf', 'docx', 'doc', 'txt', 'md'];
        const fileExt = file.name.split('.').pop().toLowerCase();
        
        if (!allowedExtensions.includes(fileExt)) {
            showToast(`Unsupported file type: .${fileExt}. Please upload a PDF, DOCX, or TXT file.`, 'danger');
            return;
        }

        selectedFile = file;
        fileNameText.textContent = file.name;
        fileSizeText.textContent = formatBytes(file.size);

        // Adjust file icon
        if (fileExt === 'pdf') {
            fileIconType.className = 'fa-solid fa-file-pdf file-icon';
            fileIconType.style.color = '#ef4444';
        } else if (fileExt === 'docx' || fileExt === 'doc') {
            fileIconType.className = 'fa-solid fa-file-word file-icon';
            fileIconType.style.color = '#3b82f6';
        } else {
            fileIconType.className = 'fa-solid fa-file-lines file-icon';
            fileIconType.style.color = '#9ca3af';
        }

        dropzoneContent.classList.add('hidden');
        filePreview.classList.remove('hidden');
        fileInput.removeAttribute('required'); // Form handles custom submit validation
    }

    function clearFileSelection() {
        selectedFile = null;
        fileInput.value = '';
        filePreview.classList.add('hidden');
        dropzoneContent.classList.remove('hidden');
        fileInput.setAttribute('required', 'true');
    }

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    /* ==========================================================================
       API Modal Handlers
       ========================================================================== */
    apiBtn.addEventListener('click', () => {
        modalApiKeyInput.value = geminiApiKey;
        apiModal.classList.remove('hidden');
    });

    closeModalBtn.addEventListener('click', () => {
        apiModal.classList.add('hidden');
    });

    window.addEventListener('click', (e) => {
        if (e.target === apiModal) {
            apiModal.classList.add('hidden');
        }
    });

    saveApiKeyBtn.addEventListener('click', () => {
        geminiApiKey = modalApiKeyInput.value.trim();
        if (geminiApiKey) {
            localStorage.setItem('resu_scan_api_key', geminiApiKey);
            showToast('Gemini API key saved successfully.', 'success');
        } else {
            localStorage.removeItem('resu_scan_api_key');
            showToast('API key removed. Running local parsing.', 'success');
        }
        updateApiButtonState();
        apiModal.classList.add('hidden');
    });

    clearApiKeyBtn.addEventListener('click', () => {
        geminiApiKey = '';
        localStorage.removeItem('resu_scan_api_key');
        modalApiKeyInput.value = '';
        updateApiButtonState();
        apiModal.classList.add('hidden');
        showToast('Gemini API key cleared.', 'success');
    });

    function updateApiButtonState() {
        if (geminiApiKey && geminiApiKey.trim()) {
            apiBtn.innerHTML = '<i class="fa-solid fa-key text-success"></i> <span>AI Engine: Gemini Active</span>';
            apiBtn.className = 'btn btn-secondary btn-icon-text active-key-btn';
        } else {
            apiBtn.innerHTML = '<i class="fa-solid fa-key"></i> <span>Configure Gemini AI</span>';
            apiBtn.className = 'btn btn-secondary btn-icon-text';
        }
    }

    /* ==========================================================================
       Tab Navigation Handlers
       ========================================================================== */
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // Toggle buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            button.classList.add('active');

            // Toggle panes
            tabPanes.forEach(pane => {
                if (pane.id === `tab-${targetTab}`) {
                    pane.classList.add('active');
                } else {
                    pane.classList.remove('active');
                }
            });
        });
    });

    /* ==========================================================================
       Toast Handler
       ========================================================================== */
    function showToast(message, type = 'danger') {
        const icon = toast.querySelector('.toast-icon');
        const msg = toast.querySelector('.toast-message');

        msg.textContent = message;
        
        if (type === 'success') {
            toast.style.borderColor = 'var(--success-border)';
            icon.className = 'fa-solid fa-circle-check text-success toast-icon';
        } else if (type === 'warning') {
            toast.style.borderColor = 'var(--warning-border)';
            icon.className = 'fa-solid fa-circle-exclamation text-warning toast-icon';
        } else {
            toast.style.borderColor = 'var(--danger-border)';
            icon.className = 'fa-solid fa-circle-xmark text-danger toast-icon';
        }

        toast.classList.remove('hidden');
        toast.style.opacity = '1';

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                toast.classList.add('hidden');
            }, 300);
        }, 5000);
    }

    /* ==========================================================================
       Form Submission & Analysis AJAX
       ========================================================================== */
    form.addEventListener('submit', (e) => {
        e.preventDefault();

        // Custom validation
        if (!selectedFile) {
            showToast('Please upload a resume file.', 'danger');
            return;
        }

        const jdText = jobDescription.value.trim();
        if (!jdText) {
            showToast('Please enter a job description.', 'danger');
            return;
        }

        // Setup loading state
        welcomeView.classList.add('hidden');
        resultsView.classList.add('hidden');
        loadingView.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.querySelector('span').textContent = 'Analyzing...';
        submitBtn.querySelector('i').className = 'fa-solid fa-spinner fa-spin';

        // Prepare FormData
        const formData = new FormData();
        formData.append('resume', selectedFile);
        formData.append('job_description', jdText);
        
        if (geminiApiKey && geminiApiKey.trim()) {
            formData.append('api_key', geminiApiKey.trim());
        }

        // AJAX Request
        fetch('/api/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            renderResults(data);
            showToast('Analysis completed successfully!', 'success');
        })
        .catch(error => {
            console.error('API Error:', error);
            const msg = error.error || 'Server error occurred during analysis.';
            showToast(msg, 'danger');
            
            // Revert view states
            welcomeView.classList.remove('hidden');
            resultsView.classList.add('hidden');
        })
        .finally(() => {
            loadingView.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.querySelector('span').textContent = 'Analyze Resume';
            submitBtn.querySelector('i').className = 'fa-solid fa-magnifying-glass-chart';
        });
    });

    /* ==========================================================================
       Results Rendering Logic
       ========================================================================== */
    function renderResults(data) {
        // Switch view
        resultsView.classList.remove('hidden');

        // Reset navigation to default Dashboard tab
        tabButtons.forEach(b => b.classList.remove('active'));
        document.querySelector('.tab-btn[data-tab="dashboard"]').classList.add('active');
        tabPanes.forEach(p => p.classList.remove('active'));
        document.getElementById('tab-dashboard').classList.add('active');

        // Render Score Gauge
        const score = data.ats_score || 0;
        const scoreText = document.getElementById('score-text');
        const scoreStatusText = document.getElementById('score-status-text');
        const scoreGaugeFill = document.getElementById('score-gauge-fill');

        scoreText.textContent = `${score}%`;
        
        // Gauge stroke calculation (circumference = 2 * pi * r = 2 * 3.14159 * 40 = 251.2)
        const circumference = 251.2;
        const offset = circumference - (score / 100) * circumference;
        scoreGaugeFill.style.strokeDashoffset = offset;

        // Set Gauge colors and statuses
        if (score >= 80) {
            scoreStatusText.textContent = 'Excellent Match';
            scoreStatusText.style.color = 'var(--success)';
            scoreGaugeFill.style.stroke = 'var(--success)';
        } else if (score >= 60) {
            scoreStatusText.textContent = 'Good Match';
            scoreStatusText.style.color = 'var(--warning)';
            scoreGaugeFill.style.stroke = 'var(--warning)';
        } else {
            scoreStatusText.textContent = 'Action Required';
            scoreStatusText.style.color = 'var(--danger)';
            scoreGaugeFill.style.stroke = 'var(--danger)';
        }

        // Render Profile Card
        document.getElementById('profile-name').textContent = data.candidate_name || 'Candidate';
        document.getElementById('profile-email').textContent = data.email || 'Not found';
        document.getElementById('profile-phone').textContent = data.phone || 'Not found';
        document.getElementById('profile-word-count').textContent = data.word_count || '0';
        
        const engineText = document.getElementById('profile-engine');
        if (data.engine === 'gemini_2.5_flash') {
            engineText.textContent = 'Gemini 2.5 Flash';
            engineText.style.borderColor = 'var(--primary)';
            engineText.style.color = 'var(--primary-light)';
            engineText.style.background = 'rgba(139, 92, 246, 0.15)';
        } else {
            engineText.textContent = 'Local Engine';
            engineText.style.borderColor = 'rgba(14, 165, 233, 0.3)';
            engineText.style.color = 'var(--secondary-light)';
            engineText.style.background = 'rgba(14, 165, 233, 0.15)';
        }

        // Profile Links
        const linksContainer = document.getElementById('profile-links');
        linksContainer.innerHTML = '';
        if (data.links && data.links.length > 0) {
            data.links.forEach(link => {
                let iconClass = 'fa-solid fa-link';
                let domainText = 'Portfolio';
                
                const lowerLink = link.toLowerCase();
                if (lowerLink.includes('github.com')) {
                    iconClass = 'fa-brands fa-github';
                    domainText = 'GitHub';
                } else if (lowerLink.includes('linkedin.com')) {
                    iconClass = 'fa-brands fa-linkedin';
                    domainText = 'LinkedIn';
                }
                
                const a = document.createElement('a');
                a.href = link;
                a.target = '_blank';
                a.className = 'profile-link';
                a.innerHTML = `<i class="${iconClass}"></i> ${domainText}`;
                linksContainer.appendChild(a);
            });
        }

        // Render Summary Alert for API errors if present
        const apiErrorNotice = document.getElementById('api-error-notice');
        if (data.api_error) {
            apiErrorNotice.classList.remove('hidden');
            apiErrorNotice.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> <div><strong>AI Error Fallback:</strong> Gemini failed (${data.api_error}). Run in rule-based fallback mode.</div>`;
        } else {
            apiErrorNotice.classList.add('hidden');
        }

        // Setup Metric Counts
        const matchedCount = data.skills_matched ? data.skills_matched.length : 0;
        const missingCount = data.skills_missing ? data.skills_missing.length : 0;
        const recCount = data.ats_recommendations ? data.ats_recommendations.length : 0;

        document.getElementById('matched-skills-count').textContent = matchedCount;
        document.getElementById('missing-skills-count').textContent = missingCount;
        document.getElementById('issues-count').textContent = recCount;

        // Render Skills
        document.getElementById('matched-skills-badge-count').textContent = matchedCount;
        document.getElementById('missing-skills-badge-count').textContent = missingCount;
        
        const matchedList = document.getElementById('matched-skills-list');
        const missingList = document.getElementById('missing-skills-list');
        
        matchedList.innerHTML = '';
        if (data.skills_matched && data.skills_matched.length > 0) {
            data.skills_matched.forEach(skill => {
                const badge = document.createElement('span');
                badge.className = 'skill-badge skill-badge-matched';
                badge.textContent = skill;
                matchedList.appendChild(badge);
            });
        } else {
            matchedList.innerHTML = '<span class="text-dim">No matching skills identified.</span>';
        }

        missingList.innerHTML = '';
        if (data.skills_missing && data.skills_missing.length > 0) {
            data.skills_missing.forEach(skill => {
                const badge = document.createElement('span');
                badge.className = 'skill-badge skill-badge-missing';
                badge.textContent = skill;
                missingList.appendChild(badge);
            });
        } else {
            missingList.innerHTML = '<span class="text-dim">No missing skills detected! Excellent job.</span>';
        }

        // Render Recommendations
        const recsContainer = document.getElementById('recommendations-list');
        recsContainer.innerHTML = '';
        
        if (data.ats_recommendations && data.ats_recommendations.length > 0) {
            data.ats_recommendations.forEach(rec => {
                const card = document.createElement('div');
                card.className = 'rec-card';
                
                const priorityClass = `priority-${rec.priority.toLowerCase()}`;
                
                card.innerHTML = `
                    <div class="rec-header">
                        <div class="rec-title-group">
                            <span class="rec-category">${rec.category}</span>
                        </div>
                        <span class="rec-priority ${priorityClass}">${rec.priority} Priority</span>
                    </div>
                    <div class="rec-body">
                        <div class="rec-finding"><i class="fa-solid fa-triangle-exclamation text-warning"></i> ${rec.finding}</div>
                        <div class="rec-guidance">${rec.recommendation}</div>
                        ${rec.example ? `<pre class="rec-example">${rec.example}</pre>` : ''}
                    </div>
                `;
                recsContainer.appendChild(card);
            });
        } else {
            recsContainer.innerHTML = `
                <div class="results-placeholder">
                    <i class="fa-solid fa-circle-check text-success placeholder-icon"></i>
                    <h3>Perfect Score!</h3>
                    <p>No major structural or keyword gaps were found in your resume.</p>
                </div>
            `;
        }

        // Render Education Timeline
        const eduTimeline = document.getElementById('education-timeline');
        eduTimeline.innerHTML = '';
        if (data.education && data.education.length > 0) {
            data.education.forEach(edu => {
                const item = document.createElement('div');
                item.className = 'timeline-item';
                item.innerHTML = `
                    <div class="timeline-marker"></div>
                    <div class="timeline-header">
                        <div>
                            <div class="timeline-title">${edu.degree}</div>
                            <div class="timeline-subtitle">${edu.institution}</div>
                        </div>
                        ${edu.duration ? `<span class="timeline-duration">${edu.duration}</span>` : ''}
                    </div>
                `;
                eduTimeline.appendChild(item);
            });
        } else {
            eduTimeline.innerHTML = '<div class="text-dim">No education records parsed.</div>';
        }

        // Render Experience Timeline
        const expTimeline = document.getElementById('experience-timeline');
        expTimeline.innerHTML = '';
        if (data.experience && data.experience.length > 0) {
            data.experience.forEach(exp => {
                const item = document.createElement('div');
                item.className = 'timeline-item';
                item.innerHTML = `
                    <div class="timeline-marker"></div>
                    <div class="timeline-header">
                        <div>
                            <div class="timeline-title">${exp.role}</div>
                            <div class="timeline-subtitle">${exp.company}</div>
                        </div>
                        ${exp.duration ? `<span class="timeline-duration">${exp.duration}</span>` : ''}
                    </div>
                    ${exp.description ? `<div class="timeline-body">${exp.description}</div>` : ''}
                `;
                expTimeline.appendChild(item);
            });
        } else {
            expTimeline.innerHTML = '<div class="text-dim">No experience records parsed.</div>';
        }

        // Render Course Recommendations
        const coursesContainer = document.getElementById('courses-list');
        coursesContainer.innerHTML = '';
        if (data.course_recommendations && data.course_recommendations.length > 0) {
            data.course_recommendations.forEach(course => {
                const card = document.createElement('div');
                card.className = 'course-card';
                card.innerHTML = `
                    <div>
                        <span class="course-skill">${course.skill}</span>
                        <h4 class="course-title">${course.course_name}</h4>
                        <div class="course-platform">
                            <i class="fa-solid fa-circle-play"></i> ${course.platform}
                        </div>
                    </div>
                    <a href="${course.url}" target="_blank" rel="noopener noreferrer" class="course-link-btn">
                        <span>Search Courses</span> <i class="fa-solid fa-arrow-up-right-from-square"></i>
                    </a>
                `;
                coursesContainer.appendChild(card);
            });
        } else {
            coursesContainer.innerHTML = '<div class="text-dim">No learning suggestions needed. You meet all skill requirements!</div>';
        }
    }
});
