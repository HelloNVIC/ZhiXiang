document.addEventListener('DOMContentLoaded', () => {
    const config = {
        apiBaseUrl: '', 
        defaultLang: 'zh',
    };

    const translations = {
        heroTitle: { zh: "NVIC-质象", en: "NVIC-Zhixiang" },
        startCreatingTitle: { zh: "生成", en: "Generate" },
        githubrepo: { zh: "Github 开源仓库", en: "NVIC Github Repo" },
        officialWebsite: { zh: "NVIC 开源社区", en: "NVIC Open Source Community" },
        groupChat: { zh: "联系我们/加入交流群", en: "Contact Us" },
        placeholders: {
            zh: ["输入一个概念", "微积分的几何原理", "黑洞是如何形成的", "冒泡排序","雷达信道"],
            en: ["Enter a concept", "What is Heat Death?", "How are black holes formed?", "What is Bubble Sort?"]
        },
        chatRailEyebrow: { zh: "随便的话", en: "随便的话" },
        chatRailTitle: { zh: "全量流式输出", en: "Full streaming output" },
        chatRailBody: { zh: "每个 token 都会被保留；解析成功后自动渲染动画，解析失败时可一键重新生成。", en: "Every token is preserved. Valid output renders automatically; parse failures can be regenerated in one click." },
        chatHeaderEyebrow: { zh: "LIVE SESSION", en: "LIVE SESSION" },
        chatHeaderTitle: { zh: "NVIC-质象生成台", en: "NVIC-Zhixiang Studio" },
        chatLivePill: { zh: "SSE 流式连接", en: "SSE stream" },
        rawOutputEyebrow: { zh: "RAW RESPONSE", en: "RAW RESPONSE" },
        rawOutputTitle: { zh: "知识 -> 视频", en: "Complete model output" },
        parseRetryEyebrow: { zh: "PARSE FAILED", en: "PARSE FAILED" },
        parseRetryTitle: { zh: "输出已完整保留，但暂时无法渲染动画", en: "The output is preserved, but it cannot be rendered yet" },
        parseRetryBody: { zh: "是否使用同一提示词重新生成一次？", en: "Regenerate with the same prompt?" },
        parseRetryButton: { zh: "重新生成", en: "Regenerate" },
        settings: { zh: "", en: "" },
        settingsTitle: { zh: "专业配置", en: "Professional settings" },
        settingsEyebrow: { zh: "CONFIGURATION", en: "CONFIGURATION" },
        settingsPanelTitle: { zh: "生成前配置", en: "Configure before generation" },
        settingsConfirm: { zh: "确认生成", en: "Confirm generation" },
        closeTitle: { zh: "关闭", en: "Close" },
        styleLabel: { zh: "视觉风格", en: "Visual style" },
        styleCinematic: { zh: "电影叙事", en: "Cinematic" },
        styleMinimal: { zh: "极简专业", en: "Minimal" },
        styleAcademic: { zh: "教学讲解", en: "Academic" },
        styleFuturistic: { zh: "未来科技", en: "Futuristic" },
        durationLabel: { zh: "视频节奏", en: "Pacing" },
        durationPreview: { zh: "快速预览", en: "Quick preview" },
        previewConfirmTitle: { zh: "当前为快速预览模式，如需全量生成请选择其他 视频节奏 ，是否继续？", en: "Quick preview mode is selected. Choose another video pacing option for full generation. Continue?" },
        previewConfirmCancel: { zh: "返回修改", en: "Go back" },
        previewConfirmContinue: { zh: "继续生成", en: "Continue" },
        durationShort: { zh: "短：30 秒", en: "Short: 30s" },
        durationMedium: { zh: "标准：60 秒", en: "Standard: 60s" },
        durationLong: { zh: "长：90 秒", en: "Long: 90s" },
        ratioLabel: { zh: "画幅比例", en: "Aspect ratio" },
        resolutionLabel: { zh: "容器尺寸", en: "Container size" },
        depthLabel: { zh: "讲解深度", en: "Depth" },
        depthStarter: { zh: "入门", en: "Starter" },
        depthStandard: { zh: "标准", en: "Standard" },
        depthExpert: { zh: "专业", en: "Expert" },
        narrationLabel: { zh: "强化文案", en: "Enhanced copy" },
        bilingualLabel: { zh: "双语字幕", en: "Bilingual subtitles" },
        mathjaxLabel: { zh: "使用 MathJax", en: "Use MathJax" },
        newChat: { zh: "新对话", en: "New Chat" },
        newChatTitle: { zh: "新对话", en: "New Chat" },
        generationConfig: { zh: "生成配置", en: "Generation settings" },
        stopGeneration: { zh: "停止", en: "Stop" },
        cancelQueuedTask: { zh: "取消任务", en: "Cancel task" },
        generationStopped: { zh: "用户主动停止任务", en: "Task stopped by user" },
        generationQueued: { zh: "任务正在排队，请稍候...", en: "Your generation task is queued. Please wait..." },
        generationStarted: { zh: "任务已开始执行", en: "Generation has started" },
        openWindowTip: { zh: "新窗口中打开效果更好", en: "It looks better in a new window" },
        openWindowTipBody: { zh: "局限于浏览器容器排布，原视频容器尺寸不能完美契合", en: "Due to browser container layout limits, the original video container size may not fit perfectly." },
        chatPlaceholder: {
            zh: "AI 生成结果具有随机性，您可在此输入修改意见",
            en: "Results are random. Enter your modifications here for adjustments."
        },
        sendTitle: { zh: "发送", en: "Send" },
        agentThinking: { zh: "NVIC Agent 正在进行思考与规划，请稍后。这可能需要数十秒至数分钟...", en: "NVIC Agent is thinking and planning, please wait..." },
        generatingCode: { zh: "生成代码中...", en: "Generating code..." },
        codeComplete: { zh: "代码已完成", en: "Code generated" },
        openInNewWindow: { zh: "在新窗口中打开", en: "Open in new window" },
        saveAsHTML: { zh: "保存为 HTML", en: "Save as HTML" },
        shareHTMLLink: { zh: "分享 HTML 链接", en: "Share HTML link" },
        shareExpirationLabel: { zh: "链接有效期", en: "Link expiration" },
        shareExpire1h: { zh: "1 小时", en: "1 hour" },
        shareExpire3h: { zh: "3 小时", en: "3 hours" },
        shareExpire6h: { zh: "6 小时", en: "6 hours" },
        shareExpire8h: { zh: "8 小时", en: "8 hours" },
        shareExpire1d: { zh: "1 天", en: "1 day" },
        shareExpire3d: { zh: "3 天", en: "3 days" },
        shareExpire7d: { zh: "7 天", en: "7 days" },
        shareExpireForever: { zh: "永久", en: "Forever" },
        sharePasswordLabel: { zh: "访问密码", en: "Access password" },
        sharePasswordPlaceholder: { zh: "请输入 4-20 位数字密码", en: "Enter a 4-20 digit password" },
        shareCreateLink: { zh: "创建并复制链接", en: "Create and copy link" },
        shareCopyDetails: { zh: "复制详细信息", en: "Copy details" },
        shareDetailsCopied: { zh: "分享详细信息已复制", en: "Share details copied" },
        sharePasswordRequired: { zh: "请输入 4-20 位数字密码", en: "Enter a 4-20 digit password" },
        shareResultUrl: { zh: "链接", en: "Link" },
        shareResultStart: { zh: "生效时间", en: "Starts at" },
        shareResultEnd: { zh: "失效时间", en: "Expires at" },
        shareNeverExpires: { zh: "永久有效", en: "Never expires" },
        shareResultPassword: { zh: "访问密码", en: "Access password" },
        htmlLinkCopied: { zh: "HTML 链接已复制，详细信息如下", en: "HTML link copied. Details are shown below." },
        shareFailed: { zh: "分享链接创建失败", en: "Failed to create share link" },
        exportAsVideo: { zh: "导出为视频", en: "Export as Video" },
        featureComingSoon: { zh: "该功能正在开发中，将在不久的将来推出。\n 请关注我的官方 GitHub 仓库以获取最新动态！", en: "This feature is under development and will be available soon.\n Follow our official GitHub repository for the latest updates!" },
        visitGitHub: { zh: "访问 GitHub", en: "Visit GitHub" },
        errorMessage: { zh: "抱歉，服务出现了一点问题。请稍后重试。", en: "Sorry, something went wrong. Please try again later." },
        errorFetchFailed: {zh: "LLM服务不可用，请稍后再试", en: "LLM service is unavailable. Please try again later."},
        errorTooManyRequests: {zh: "今天已经使用太多，请明天再试", en: "Too many requests today. Please try again tomorrow."},
        errorLLMParseError: {zh: "返回的动画代码解析失败，请调整提示词重新生成。", en: "Failed to parse the returned animation code. Please adjust your prompt and try again."},
        errorDetailsLabel: { zh: "错误详情", en: "Error details" },
        passphraseEyebrow: { zh: "ACCESS", en: "ACCESS" },
        passphraseTitle: { zh: "请输入暗号", en: "Enter passphrase" },
        passphrasePlaceholder: { zh: "暗号", en: "Passphrase" },
        passphraseSubmit: { zh: "进入", en: "Enter" },
        passphraseError: { zh: "暗号错误", en: "Invalid passphrase" },
        mobileUnsupported: { zh: "请在PC端访问，移动端暂不支持", en: "Please visit on a PC. Mobile is not supported yet." },
    };

    let currentLang = config.defaultLang;
    const body = document.body;
    const passphraseGate = document.getElementById('passphrase-gate');
    const passphraseForm = document.getElementById('passphrase-form');
    const passphraseInput = document.getElementById('passphrase-input');
    const passphraseError = document.getElementById('passphrase-error');
    const initialForm = document.getElementById('initial-form');
    const initialInput = document.getElementById('initial-input');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatLog = document.getElementById('chat-log');
    const chatRailTitle = document.querySelector('[data-translate-key="chatRailTitle"]');
    const chatRailBody = document.querySelector('[data-translate-key="chatRailBody"]');
    const stopGenerationButton = document.getElementById('stop-generation-button');
    const queueCancelButton = document.getElementById('queue-cancel-button');
    const newChatButton = document.getElementById('new-chat-button');
    const languageSwitcher = document.getElementById('language-switcher');
    const placeholderContainer = document.getElementById('animated-placeholder');
    const featureModal = document.getElementById('feature-modal');
    const previewConfirmModal = document.getElementById('preview-confirm-modal');
    const previewConfirmClose = document.getElementById('preview-confirm-close');
    const previewConfirmCancel = document.getElementById('preview-confirm-cancel');
    const previewConfirmContinue = document.getElementById('preview-confirm-continue');
    const shareModal = document.getElementById('share-modal');
    const shareForm = document.getElementById('share-form');
    const shareExpiration = document.getElementById('share-expiration');
    const sharePassword = document.getElementById('share-password');
    const shareSubmitButton = document.getElementById('share-submit-button');
    const shareResult = document.getElementById('share-result');
    const shareResultUrl = document.getElementById('share-result-url');
    const shareResultStart = document.getElementById('share-result-start');
    const shareResultEnd = document.getElementById('share-result-end');
    const shareResultPassword = document.getElementById('share-result-password');
    const shareQr = document.getElementById('share-qr');
    const shareModalCloseButton = document.getElementById('share-modal-close-button');
    const modalGitHubButton = document.getElementById('modal-github-button');
    const modalCloseButton = document.getElementById('modal-close-button');
    const settingsPanel = document.getElementById('settings-panel');
    const settingsToggles = document.querySelectorAll('[data-settings-toggle]');
    const settingsClose = document.getElementById('settings-close');
    const settingsConfirm = document.getElementById('settings-confirm');
    const settingStyle = document.getElementById('setting-style');
    const settingDuration = document.getElementById('setting-duration');
    const settingRatio = document.getElementById('setting-ratio');
    const settingResolution = document.getElementById('setting-resolution');
    const settingDepth = document.getElementById('setting-depth');
    const settingNarration = document.getElementById('setting-narration');
    const settingBilingual = document.getElementById('setting-bilingual');
    const settingMathjax = document.getElementById('setting-mathjax');

    const templates = {
        user: document.getElementById('user-message-template'),
        status: document.getElementById('agent-status-template'),
        output: document.getElementById('agent-output-template'),
        retry: document.getElementById('parse-retry-template'),
        player: document.getElementById('animation-player-template'),
        error: document.getElementById('agent-error-template'),
    };

    class LLMParseError extends Error {
        constructor(message, code = 'LLM_UNKNOWN_ERROR') {
            super(message);
            this.name = 'LLMParseError';
            this.code = code;
        }
    }

    let conversationHistory = [];
    let accumulatedCode = '';
    let placeholderInterval;
    let oneQuoteInterval;
    let activeGenerationController = null;
    let pendingGenerationTopic = '';
    let pendingGenerationIsInitial = false;
    let pendingShareHtml = '';
    let latestShareDetails = null;
    let previewConfirmResolver = null;

    function unlockPassphraseGate() {
        passphraseGate?.classList.add('hidden');
        sessionStorage.setItem('passphraseVerified', '1');
        initialInput?.focus();
    }

    async function initPassphraseGate() {
        try {
            const response = await fetch(`${config.apiBaseUrl}/config`);
            if (!response.ok) throw new Error('Failed to load config');
            const publicConfig = await response.json();
            if (!publicConfig.requiresPassphrase || sessionStorage.getItem('passphraseVerified') === '1') {
                unlockPassphraseGate();
            }
        } catch (error) {
            console.warn('Failed to initialize passphrase gate:', error);
        }
    }

    async function handlePassphraseSubmit(e) {
        e.preventDefault();
        const passphrase = passphraseInput.value.trim();
        if (!passphrase) return;

        try {
            const response = await fetch(`${config.apiBaseUrl}/verify-passphrase`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ passphrase }),
            });
            if (!response.ok) throw new Error('Invalid passphrase');
            unlockPassphraseGate();
        } catch (error) {
            passphraseError.hidden = false;
            passphraseInput.select();
        }
    }

    function getGenerationSettings() {
        return {
            style: settingStyle?.value || 'minimal',
            duration: settingDuration?.value || 'medium',
            ratio: settingRatio?.value || '16:9',
            resolution: settingResolution?.value || '1080p',
            depth: settingDepth?.value || 'standard',
            narration: Boolean(settingNarration?.checked),
            bilingual: Boolean(settingBilingual?.checked),
            mathjax: Boolean(settingMathjax?.checked),
        };
    }

    function isMobileDevice() {
        const hasCoarsePointer = window.matchMedia?.('(pointer: coarse)').matches;
        const narrowViewport = Math.min(window.innerWidth, window.innerHeight) < 768;
        const mobileAgent = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);
        return mobileAgent || (hasCoarsePointer && narrowViewport);
    }

    function showMobileUnsupportedWarning() {
        if (!isMobileDevice()) return;
        showWarning(translations.mobileUnsupported[currentLang], { persistent: true, blocking: true });
    }

    async function loadOneQuotes() {
        try {
            const response = await fetch('/static/one-quotes.json');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const quotes = await response.json();
            if (!Array.isArray(quotes) || quotes.length === 0) return;

            let index = Math.floor(Math.random() * quotes.length);
            const showQuote = () => {
                const quote = quotes[index % quotes.length];
                [chatRailTitle, chatRailBody].forEach(element => element?.classList.add('is-changing'));
                window.setTimeout(() => {
                    if (chatRailTitle) chatRailTitle.textContent = quote.text;
                    if (chatRailBody) chatRailBody.textContent = quote.source;
                    [chatRailTitle, chatRailBody].forEach(element => element?.classList.remove('is-changing'));
                }, 260);
                index += 1;
            };

            const scheduleNextQuote = () => {
                const delay = 8000 + Math.random() * 4000;
                oneQuoteInterval = window.setTimeout(() => {
                    showQuote();
                    scheduleNextQuote();
                }, delay);
            };

            showQuote();
            if (oneQuoteInterval) clearTimeout(oneQuoteInterval);
            scheduleNextQuote();
        } catch (error) {
            console.warn('Failed to load ONE quotes:', error);
        }
    }

    function handleFormSubmit(e) {
        e.preventDefault();
        const isInitial = e.currentTarget.id === 'initial-form';
        const input = isInitial ? initialInput : chatInput;
        const topic = input.value.trim();
        if (!topic) return;

        if (!isInitial) {
            conversationHistory.push({ role: 'user', content: topic });
            trackUserInput(topic, 'chat');
            startGeneration(topic);
            chatInput.value = '';
            return;
        }

        pendingGenerationTopic = topic;
        pendingGenerationIsInitial = true;
        openSettingsPanel(true);
    }

    function trackUserInput(topic, source) {
        window.umami?.track('user_input', {
            source,
            text: topic,
            length: topic.length,
            language: currentLang,
        });
    }

    async function startGeneration(topic, options = {}) {
        console.log('Getting generation from backend.');
        if (!options.reuseUserMessage) appendUserMessage(topic);
        const agentThinkingMessage = appendAgentStatus(translations.agentThinking[currentLang]);
        const submitButton = document.querySelector('.submit-button');
        activeGenerationController = new AbortController();
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.classList.add('disabled');
        }
        if (stopGenerationButton) stopGenerationButton.hidden = false;
        accumulatedCode = '';
        let fullResponse = '';
        let queueWarningVisible = false;
        const outputElement = appendOutputBlock();

        try {
            const response = await fetch(`${config.apiBaseUrl}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: topic, history: conversationHistory, settings: getGenerationSettings() }),
                signal: activeGenerationController.signal
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;

                    const jsonStr = line.substring(6);
                    if (jsonStr.includes('[DONE]')) {
                        console.log('Streaming complete');
                        accumulatedCode = extractHtmlFromResponse(fullResponse);
                        conversationHistory.push({ role: 'assistant', content: fullResponse });
                        markOutputAsComplete(outputElement);

                        if (!accumulatedCode || !isHtmlContentValid(accumulatedCode)) {
                            console.warn('Unable to parse renderable HTML from full response:', fullResponse);
                            appendRetryPrompt(topic);
                            scrollToBottom();
                            return;
                        }

                        try {
                            appendAnimationPlayer(accumulatedCode, topic);
                        } catch (err) {
                            console.error('appendAnimationPlayer failed:', err);
                            appendRetryPrompt(topic);
                            scrollToBottom();
                            return;
                        }

                        scrollToBottom();
                        return;
                    }

                    let data;
                    try {
                        data = JSON.parse(jsonStr);
                    } catch (err) {
                        console.error('Failed to parse JSON:', jsonStr);
                        throw new LLMParseError('Invalid response format from server.');
                    }

                    if (data.event === 'queued') {
                        queueWarningVisible = true;
                        showWarning(translations.generationQueued[currentLang], {
                            persistent: true,
                            blocking: true,
                            loading: true,
                            cancelable: true,
                            cancelText: translations.cancelQueuedTask[currentLang],
                        });
                        continue;
                    }

                    if (data.event === 'started') {
                        if (queueWarningVisible) {
                            forceHideWarning();
                            showWarning(translations.generationStarted[currentLang]);
                            queueWarningVisible = false;
                        }
                        continue;
                    }

                    if (data.error) {
                        throw new LLMParseError(data.error);
                    }
                    const token = data.token || '';
                    if (agentThinkingMessage) agentThinkingMessage.remove();
                    fullResponse += token;
                    updateOutputBlock(outputElement, token);
                }
            }
        } catch (error) {
            console.error("Streaming failed:", error);
            if (agentThinkingMessage) agentThinkingMessage.remove();

            let displayMessage = translations.errorFetchFailed[currentLang];
            if (error.name === 'AbortError') {
                displayMessage = translations.generationStopped[currentLang];
            } else if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
                displayMessage = translations.errorFetchFailed[currentLang];
            } else if (error.message.includes('status: 429')) {
                displayMessage = translations.errorTooManyRequests[currentLang];
            } else if (error instanceof LLMParseError) {
                displayMessage = translations.errorLLMParseError[currentLang];
            }

            showWarning(displayMessage);
            appendErrorMessage(translations.errorMessage[currentLang], error);
            if (outputElement) markOutputAsComplete(outputElement);
        } finally {
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.classList.remove('disabled');
        }
        if (stopGenerationButton) stopGenerationButton.hidden = true;
        activeGenerationController = null;
    }
    }

    function switchToChatView() {
        body.classList.remove('show-initial-view');
        body.classList.add('show-chat-view');
        languageSwitcher?.style && (languageSwitcher.style.display = 'none');
    }

    function openSettingsPanel(isBeforeGeneration = false) {
        settingsPanel.classList.add('visible');
        settingsPanel.setAttribute('aria-hidden', 'false');
        settingsToggles.forEach(button => button.classList.toggle('is-attention', isBeforeGeneration));
    }

    function closeSettingsPanel() {
        settingsPanel.classList.remove('visible');
        settingsPanel.setAttribute('aria-hidden', 'true');
        settingsToggles.forEach(button => button.classList.remove('is-attention'));
    }

    function showPreviewConfirm() {
        previewConfirmModal.classList.add('visible');
        return new Promise(resolve => {
            previewConfirmResolver = resolve;
        });
    }

    function resolvePreviewConfirm(confirmed) {
        previewConfirmModal.classList.remove('visible');
        if (!previewConfirmResolver) return;
        previewConfirmResolver(confirmed);
        previewConfirmResolver = null;
    }

    async function confirmGenerationFromSettings() {
        const topic = pendingGenerationTopic;
        if (!topic) {
            closeSettingsPanel();
            return;
        }

        if (settingDuration?.value === 'preview' && !await showPreviewConfirm()) {
            return;
        }

        if (pendingGenerationIsInitial) switchToChatView();

        conversationHistory.push({ role: 'user', content: topic });
        trackUserInput(topic, pendingGenerationIsInitial ? 'initial' : 'chat_settings');
        startGeneration(topic);
        if (pendingGenerationIsInitial) {
            initialInput.value = '';
            placeholderContainer?.classList?.remove('hidden');
        } else {
            chatInput.value = '';
        }
        pendingGenerationTopic = '';
        pendingGenerationIsInitial = false;
        closeSettingsPanel();
    }

    function appendFromTemplate(template, text) {
        const node = template.content.cloneNode(true);
        const element = node.firstElementChild;
        if (text) element.innerHTML = element.innerHTML.replace('${text}', text);
        element.querySelectorAll('[data-translate-key]').forEach(el => {
            const key = el.dataset.translateKey;
            const translation = translations[key]?.[currentLang];
            if (translation) el.textContent = translation;
        });
        chatLog.appendChild(element);
        scrollToBottom();
        return element;
    }

    const appendUserMessage = (text) => appendFromTemplate(templates.user, text);
    const appendAgentStatus = (text) => appendFromTemplate(templates.status, text);
    function appendErrorMessage(text, error) {
        const element = appendFromTemplate(templates.error, text);
        const detailText = element.querySelector('.error-detail-text');
        if (detailText) {
            const message = error?.stack || error?.message || String(error || 'Unknown error');
            detailText.textContent = `${translations.errorDetailsLabel[currentLang]}\n${message}`;
        }
        return element;
    }
    const appendOutputBlock = () => appendFromTemplate(templates.output);

    function updateOutputBlock(outputElement, text) {
        const codeElement = outputElement.querySelector('code');
        if (!text || !codeElement) return;
        const span = document.createElement('span');
        span.textContent = text;
        codeElement.appendChild(span);

        const rawOutput = outputElement.querySelector('.raw-output');
        if (rawOutput) {
            requestAnimationFrame(() => {
                rawOutput.scrollTop = rawOutput.scrollHeight;
            });
        }
    }

    function markOutputAsComplete(outputElement) {
        outputElement?.querySelector('.output-card')?.classList.remove('is-streaming');
        const status = outputElement?.querySelector('.output-status');
        if (status) status.textContent = translations.codeComplete[currentLang];
    }

    function extractHtmlFromResponse(responseText) {
        const fencedMatch = responseText.match(/```(?:html)?\s*([\s\S]*?)```/i);
        const candidate = fencedMatch ? fencedMatch[1] : responseText;
        const htmlMatch = candidate.match(/<!doctype html[\s\S]*|<html[\s\S]*<\/html>/i);
        return (htmlMatch ? htmlMatch[0] : candidate).trim();
    }

    function appendRetryPrompt(topic) {
        const element = appendFromTemplate(templates.retry);
        const button = element.querySelector('.retry-generation');
        button?.addEventListener('click', () => {
            element.remove();
            startGeneration(topic, { reuseUserMessage: true });
        });
        return element;
    }

    function getPreviewSize(settings = getGenerationSettings()) {
        const ratioMap = {
            '16:9': [16, 9],
            '9:16': [9, 16],
            '1:1': [1, 1],
        };
        const heightMap = {
            '720p': 720,
            '1080p': 1080,
            '2k': 1152,
        };
        const [ratioWidth, ratioHeight] = ratioMap[settings.ratio] || ratioMap['16:9'];
        const sourceHeight = heightMap[settings.resolution] || heightMap['1080p'];
        const sourceWidth = Math.round(sourceHeight * ratioWidth / ratioHeight);
        const availableWidth = Math.max((chatLog?.clientWidth || sourceWidth) - 72, 320);
        const availableHeight = Math.max(window.innerHeight * 0.72, 320);
        const scale = Math.min(availableWidth / sourceWidth, availableHeight / sourceHeight, 1);
        return {
            width: Math.round(sourceWidth * scale),
            height: Math.round(sourceHeight * scale),
            sourceWidth,
            sourceHeight,
            scale,
        };
    }

    function createHtmlBlobUrl(htmlContent) {
        const blob = new Blob([htmlContent], { type: 'text/html' });
        return URL.createObjectURL(blob);
    }

    function openShareModal(htmlContent) {
        pendingShareHtml = htmlContent;
        sharePassword.value = '';
        shareExpiration.value = '1h';
        shareResult.hidden = true;
        latestShareDetails = null;
        shareSubmitButton.textContent = translations.shareCreateLink[currentLang];
        shareModal.classList.add('visible');
        sharePassword.focus();
    }

    function closeShareModal() {
        shareModal.classList.remove('visible');
        pendingShareHtml = '';
    }

    function formatShareTime(value) {
        return new Date(value).toLocaleString(currentLang === 'zh' ? 'zh-CN' : 'en-US');
    }

    function getShareDetailsText(data = latestShareDetails) {
        if (!data) return '';
        const expiresAt = data.expiresAt ? formatShareTime(data.expiresAt) : translations.shareNeverExpires[currentLang];
        return [
            `${translations.shareResultUrl[currentLang]}：${data.url}`,
            `${translations.shareResultStart[currentLang]}：${formatShareTime(data.createdAt)}`,
            `${translations.shareResultEnd[currentLang]}：${expiresAt}`,
            `${translations.shareResultPassword[currentLang]}：${data.password}`,
        ].join('\n');
    }

    async function copyShareDetails() {
        await navigator.clipboard.writeText(getShareDetailsText());
        showWarning(translations.shareDetailsCopied[currentLang]);
    }

    function renderShareResult(data) {
        latestShareDetails = data;
        shareResultUrl.value = data.url;
        shareResultStart.textContent = formatShareTime(data.createdAt);
        shareResultEnd.textContent = data.expiresAt ? formatShareTime(data.expiresAt) : translations.shareNeverExpires[currentLang];
        shareResultPassword.textContent = data.password;
        shareResult.hidden = false;
        shareSubmitButton.textContent = translations.shareCopyDetails[currentLang];
        shareQr.src = data.qrCode;
    }

    async function shareHtmlLink(htmlContent, expiresIn, password, previewSize) {
        const response = await fetch(`${config.apiBaseUrl}/share`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                html: htmlContent,
                expiresIn,
                password,
                sourceWidth: previewSize.sourceWidth,
                sourceHeight: previewSize.sourceHeight,
            }),
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        renderShareResult(data);
        await copyShareDetails();
    }

    function appendAnimationPlayer(htmlContent, topic) {
        console.log('Appending animation player with topic:', topic);
        const node = templates.player.content.cloneNode(true);
        const playerElement = node.firstElementChild;
        playerElement.querySelectorAll('[data-translate-key]').forEach(el => {
            const key = el.dataset.translateKey;
            el.textContent = translations[key]?.[currentLang] || el.textContent;
        });
        const iframe = playerElement.querySelector('.animation-iframe');
        const iframeWrapper = playerElement.querySelector('.iframe-wrapper');
        const previewSize = getPreviewSize();
        if (iframeWrapper) {
            iframeWrapper.style.setProperty('--preview-width', `${previewSize.width}px`);
            iframeWrapper.style.setProperty('--preview-height', `${previewSize.height}px`);
            iframeWrapper.style.setProperty('--source-width', `${previewSize.sourceWidth}px`);
            iframeWrapper.style.setProperty('--source-height', `${previewSize.sourceHeight}px`);
            iframeWrapper.style.setProperty('--preview-scale', previewSize.scale.toString());
        }
        iframe.width = previewSize.sourceWidth;
        iframe.height = previewSize.sourceHeight;
        iframe.style.width = `${previewSize.sourceWidth}px`;
        iframe.style.height = `${previewSize.sourceHeight}px`;
        iframe.srcdoc = htmlContent;

        playerElement.querySelector('.open-new-window').addEventListener('click', () => {
            window.open(createHtmlBlobUrl(htmlContent), '_blank');
        });
        playerElement.querySelector('.save-html').addEventListener('click', () => {
            const url = createHtmlBlobUrl(htmlContent);
            const a = Object.assign(document.createElement('a'), { href: url, download: `${topic.replace(/\s/g, '_') || 'animation'}.html` });
            document.body.appendChild(a);
            a.click();
            URL.revokeObjectURL(url);
            a.remove();
        });
        playerElement.querySelector('.share-html')?.addEventListener('click', () => {
            openShareModal(htmlContent);
        });
        playerElement.querySelector('.export-video')?.addEventListener('click', () => {
            featureModal.querySelector('p').textContent = translations.featureComingSoon[currentLang];
            modalGitHubButton.textContent = translations.visitGitHub[currentLang];
            featureModal.classList.add('visible');
        });
        chatLog.appendChild(playerElement);
        scrollToBottom();
    }

    function isHtmlContentValid(htmlContent) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, "text/html");

        // 检查是否存在解析错误
        const parseErrors = doc.querySelectorAll("parsererror");
        if (parseErrors.length > 0) {
            console.warn("HTML 解析失败：", parseErrors[0].textContent);
            return false;
        }

        // 可选：检测是否有 <html><body> 结构或是否为空
        if (!doc.body || doc.body.innerHTML.trim() === "") {
            console.warn("HTML 内容为空");
            return false;
        }

        return true;
    }

    const scrollToBottom = () => chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: 'smooth' });

    function setNextPlaceholder() {
        const placeholderTexts = translations.placeholders[currentLang];
        const newSpan = document.createElement('span');
        newSpan.textContent = placeholderTexts[placeholderIndex];
        placeholderContainer.innerHTML = '';
        placeholderContainer.appendChild(newSpan);
        placeholderIndex = (placeholderIndex + 1) % placeholderTexts.length;
    }

    function startPlaceholderAnimation() {
        if (placeholderInterval) clearInterval(placeholderInterval);
        const placeholderTexts = translations.placeholders[currentLang];
        if (placeholderTexts && placeholderTexts.length > 0) {
            placeholderIndex = 0;
            setNextPlaceholder();
            placeholderInterval = setInterval(setNextPlaceholder, 4000);
        }
    }

    function setLanguage(lang) {
        if (!['zh', 'en'].includes(lang)) return;
        currentLang = lang;
        document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
        document.querySelectorAll('[data-translate-key]').forEach(el => {
            const key = el.dataset.translateKey;
            const translation = translations[key]?.[lang];
            if (!translation) return;
            if (el.hasAttribute('placeholder')) el.placeholder = translation;
            else if (el.hasAttribute('title')) el.title = translation;
            else el.textContent = translation;
        });
        languageSwitcher?.querySelectorAll('button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
        startPlaceholderAnimation();
        localStorage.setItem('preferredLanguage', lang);
    }

    let placeholderIndex = 0;

    function init() {
        initialInput.addEventListener('input', () => {
            placeholderContainer.classList.toggle('hidden', initialInput.value.length > 0);
        });
        initialInput.addEventListener('focus', () => clearInterval(placeholderInterval));
        initialInput.addEventListener('blur', () => {
            if (initialInput.value.length === 0) startPlaceholderAnimation();
        });

        initialForm.addEventListener('submit', handleFormSubmit);
        passphraseForm?.addEventListener('submit', handlePassphraseSubmit);
        initPassphraseGate();
        chatForm.addEventListener('submit', handleFormSubmit);
        newChatButton.addEventListener('click', () => location.reload());
        stopGenerationButton?.addEventListener('click', () => {
            activeGenerationController?.abort();
        });
        queueCancelButton?.addEventListener('click', () => {
            activeGenerationController?.abort();
        });
        settingsToggles.forEach(button => {
            button.addEventListener('click', () => openSettingsPanel(false));
        });
        settingsClose.addEventListener('click', closeSettingsPanel);
        settingsPanel.addEventListener('click', (e) => {
            if (e.target === settingsPanel) closeSettingsPanel();
        });
        settingsConfirm.addEventListener('click', confirmGenerationFromSettings);
        previewConfirmClose?.addEventListener('click', () => resolvePreviewConfirm(false));
        previewConfirmCancel?.addEventListener('click', () => resolvePreviewConfirm(false));
        previewConfirmContinue?.addEventListener('click', () => resolvePreviewConfirm(true));
        previewConfirmModal?.addEventListener('click', (e) => {
            if (e.target === previewConfirmModal) resolvePreviewConfirm(false);
        });
        languageSwitcher?.addEventListener('click', (e) => {
            const target = e.target.closest('button');
            if (target) setLanguage(target.dataset.lang);
        });

        function hideModal() {
            featureModal.classList.remove('visible');
        }

        modalCloseButton.addEventListener('click', hideModal);
        featureModal.addEventListener('click', (e) => {
            if (e.target === featureModal) hideModal();
        });
        shareModalCloseButton?.addEventListener('click', closeShareModal);
        shareModal?.addEventListener('click', (e) => {
            if (e.target === shareModal) closeShareModal();
        });
        shareForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (latestShareDetails) {
                await copyShareDetails();
                return;
            }
            const password = sharePassword.value.trim();
            if (!/^\d{4,20}$/.test(password)) {
                showWarning(translations.sharePasswordRequired[currentLang]);
                sharePassword.focus();
                return;
            }
            try {
                await shareHtmlLink(pendingShareHtml, shareExpiration.value, password, getPreviewSize());
            } catch (error) {
                console.error('Failed to create share link:', error);
                showWarning(translations.shareFailed[currentLang]);
            }
        });

        modalGitHubButton.addEventListener('click', () => {
            window.open('https://github.com/HelloNVIC/ZhiXiang', '_blank');
            hideModal();
        });

        const savedLang = localStorage.getItem('preferredLanguage');
        const browserLang = navigator.language?.toLowerCase() || ''; // e.g. 'zh-cn'

        let initialLang = 'en'; 
        if (['zh', 'en'].includes(savedLang)) {
            initialLang = savedLang;
        } else if (browserLang.startsWith('zh')) {
            initialLang = 'zh';
        } else if (browserLang.startsWith('en')) {
            initialLang = 'en';
        }

        setLanguage(initialLang);
        showMobileUnsupportedWarning();
        loadOneQuotes();
    }

    init();
});

function showWarning(message, options = {}) {
    const box = document.getElementById('warning-box');
    const overlay = document.getElementById('overlay');
    const text = document.getElementById('warning-message');
    const description = document.getElementById('warning-description');
    const spinner = document.getElementById('warning-spinner');
    const closeButton = document.getElementById('warning-close-button');
    const cancelButton = document.getElementById('queue-cancel-button');

    text.textContent = message;
    if (cancelButton) {
        cancelButton.textContent = options.cancelText || '取消任务';
        cancelButton.hidden = !options.cancelable;
    }
    if (description) {
        description.textContent = options.description || '';
        description.hidden = !options.description;
    }
    if (spinner) spinner.hidden = !options.loading;
    if (closeButton) closeButton.hidden = Boolean(options.blocking);
    box.classList.toggle('is-blocking', Boolean(options.blocking));
    box.classList.toggle('has-description', Boolean(options.description));
    box.style.display = 'flex';
    overlay.style.display = 'block';

    if (window.warningTimer) clearTimeout(window.warningTimer);
    if (options.persistent) return;

    window.warningTimer = setTimeout(() => {
        hideWarning();
    }, 10000);
}

function hideWarning() {
    const box = document.getElementById('warning-box');
    if (box?.classList.contains('is-blocking')) return;
    forceHideWarning();
}

function forceHideWarning() {
    if (window.warningTimer) {
        clearTimeout(window.warningTimer);
        window.warningTimer = null;
    }
    const box = document.getElementById('warning-box');
    const overlay = document.getElementById('overlay');
    const spinner = document.getElementById('warning-spinner');
    const description = document.getElementById('warning-description');
    const closeButton = document.getElementById('warning-close-button');
    const cancelButton = document.getElementById('queue-cancel-button');
    box?.classList.remove('is-blocking', 'has-description');
    if (spinner) spinner.hidden = true;
    if (description) {
        description.hidden = true;
        description.textContent = '';
    }
    if (closeButton) closeButton.hidden = false;
    if (cancelButton) cancelButton.hidden = true;
    box.style.display = 'none';
    overlay.style.display = 'none';
}
