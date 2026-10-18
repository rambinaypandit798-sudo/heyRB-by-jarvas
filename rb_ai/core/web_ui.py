"""
RB.AI - Master Mobile PWA & Autonomous Operating System Interface
Developed for: Ram Binay kumar Pandit
Mobile-First Single-Screen View • Jarvis Arc Reactor HUD • 5 Blinking Sub-Agents • Sticky 'ASK RB Agent' Dock
"""

WEB_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>RB Agent — Personal AI Assistant</title>
    <meta name="theme-color" content="#FFFFFF">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="RB Agent OS">
    <link rel="manifest" href="/manifest.json">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-base: #F8FAFC;
            --bg-surface: #FFFFFF;
            --bg-card: #FFFFFF;
            --bg-input: #F1F5F9;
            --border: #E2E8F0;
            --border-glow: rgba(2, 132, 199, 0.25);
            --text-primary: #0F172A;
            --text-muted: #64748B;
            --accent-cyan: #0284C7;
            --accent-blue: #0284C7;
            --accent-green: #10B981;
            --accent-amber: #D97706;
            --accent-purple: #7C3AED;
            --accent-pink: #DB2777;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; -webkit-tap-highlight-color: transparent; }
        html, body {
            background: #EFF6FF;
            color: var(--text-primary);
            height: 100%;
            width: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* App Wrapper - Mobile First Single Screen */
        .app-container {
            display: flex;
            flex-direction: column;
            height: 100%;
            height: 100dvh;
            width: 100%;
            max-width: 480px;
            margin: 0 auto;
            position: relative;
            overflow: hidden;
            background: var(--bg-base);
            box-shadow: 0 10px 40px rgba(15, 23, 42, 0.08);
        }

        /* 1. Top Header */
        .app-header {
            height: 52px; background: var(--bg-surface); border-bottom: 1px solid var(--border);
            padding: 0 16px; display: flex; align-items: center; justify-content: space-between; z-index: 30; flex-shrink: 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        }
        .header-left { display: flex; align-items: center; gap: 12px; }
        .btn-hamburger { background: none; border: none; color: var(--text-primary); font-size: 1.25rem; cursor: pointer; padding: 4px; display: flex; align-items: center; }
        .header-title-box { display: flex; flex-direction: column; }
        .header-title { font-size: 0.95rem; font-weight: 800; color: var(--text-primary); letter-spacing: 0.3px; display: flex; align-items: center; gap: 6px; }
        .header-title span { color: var(--accent-cyan); }
        .header-subtitle { font-size: 0.65rem; color: var(--text-muted); font-weight: 600; }
        .status-pill {
            background: #ECFDF5; border: 1px solid #A7F3D0;
            padding: 3px 9px; border-radius: 12px; display: flex; align-items: center; gap: 5px; font-size: 0.68rem; font-weight: 700; color: #059669;
        }
        .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #10B981; animation: pulseDot 2s infinite; }
        @keyframes pulseDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(0.8); opacity: 0.4; } }

        /* Main Scrollable Core Stage */
        .app-stage {
            flex: 1; overflow-y: auto; overflow-x: hidden; display: flex; flex-direction: column;
            padding: 10px 14px 125px 14px; gap: 10px; scroll-behavior: smooth;
        }
        .app-stage::-webkit-scrollbar { width: 4px; }
        .app-stage::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }

        /* Dynamic Greeting Card */
        .greeting-banner {
            background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
            border: 1px solid #7DD3FC; border-radius: 14px; padding: 12px 14px;
            display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.08);
        }
        .greeting-text-title { font-size: 0.98rem; font-weight: 800; color: #0369A1; letter-spacing: -0.2px; }
        .greeting-text-sub { font-size: 0.74rem; color: #0284C7; font-weight: 600; margin-top: 2px; }
        .greeting-icon { color: #0284C7; font-size: 1.2rem; filter: drop-shadow(0 0 6px rgba(2, 132, 199, 0.35)); }

        /* 2. Centerpiece: Stunning Jarvis Arc Reactor Circular HUD */
        .jarvis-reactor-stage {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            padding: 8px 0 4px 0; position: relative; user-select: none; flex-shrink: 0;
        }
        .jarvis-reactor-disc {
            width: 132px; height: 132px; position: relative; display: flex; align-items: center; justify-content: center;
            cursor: pointer;
        }
        /* Outer Dashed Orbit */
        .orbit-outer {
            position: absolute; inset: 0; border-radius: 50%;
            border: 2px dashed rgba(2, 132, 199, 0.55);
            animation: spinClockwise 12s linear infinite;
        }
        /* Middle Planetary Ring */
        .orbit-mid {
            position: absolute; inset: 10px; border-radius: 50%;
            border: 2px solid rgba(14, 165, 233, 0.35);
            border-top-color: #0284C7; border-bottom-color: #8B5CF6;
            animation: spinCounter 7s linear infinite;
        }
        /* Inner Glowing Orb Core */
        .reactor-orb-core {
            width: 84px; height: 84px; border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, #38BDF8 0%, #0284C7 55%, #0369A1 100%);
            border: 2.5px solid #7DD3FC;
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.35), inset 0 0 15px rgba(255, 255, 255, 0.4);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            text-align: center; transition: all 0.25s ease;
            animation: coreBreath 3s infinite ease-in-out;
        }
        .jarvis-reactor-disc:active .reactor-orb-core {
            transform: scale(0.92); box-shadow: 0 8px 25px rgba(2, 132, 199, 0.5);
        }
        @keyframes spinClockwise { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes spinCounter { 0% { transform: rotate(360deg); } 100% { transform: rotate(0deg); } }
        @keyframes coreBreath { 0%, 100% { transform: scale(1); filter: brightness(1); } 50% { transform: scale(1.03); filter: brightness(1.1); } }

        .orb-title { font-size: 0.82rem; font-weight: 900; color: #FFF; letter-spacing: 0.6px; text-shadow: 0 1px 3px rgba(0,0,0,0.3); }
        .orb-subtitle { font-size: 0.52rem; color: #E0F2FE; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; margin-top: 1px; }

        .reactor-hint {
            font-size: 0.68rem; color: #0284C7; margin-top: 6px; font-weight: 700;
            display: flex; align-items: center; gap: 4px;
        }

        /* 3. Sub-Agents Integration (Compact Cards with Pulsing/Blinking Glow) */
        .subagents-strip {
            display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; flex-shrink: 0;
        }
        .subagent-pill {
            background: var(--bg-surface); border: 1px solid var(--border); border-radius: 10px;
            padding: 8px 3px; display: flex; flex-direction: column; align-items: center; text-align: center;
            cursor: pointer; transition: all 0.2s ease; position: relative; overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }
        .subagent-pill:hover { border-color: #CBD5E1; transform: translateY(-1px); box-shadow: 0 3px 8px rgba(0,0,0,0.06); }
        .subagent-icon-emoji { font-size: 1.25rem; line-height: 1.1; margin-bottom: 3px; }
        .subagent-name-text { font-size: 0.65rem; font-weight: 800; color: #0F172A; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
        .subagent-state-badge {
            font-size: 0.5rem; font-weight: 800; padding: 2px 4px; border-radius: 4px; margin-top: 3px;
            text-transform: uppercase; letter-spacing: 0.3px;
        }

        /* Pulsing/Blinking Glow Animations for Active Sub-Agents */
        .agent-pill-research { border-color: #BAE6FD; }
        .agent-pill-research .subagent-state-badge { background: #E0F2FE; color: #0284C7; }
        .agent-pill-research.active-blink {
            border-color: #0284C7 !important;
            box-shadow: 0 0 14px rgba(2, 132, 199, 0.45) !important;
            animation: pulseCyan 1s infinite alternate;
        }
        @keyframes pulseCyan {
            0% { box-shadow: 0 0 4px rgba(2, 132, 199, 0.3); transform: scale(1); }
            100% { box-shadow: 0 0 16px rgba(2, 132, 199, 0.6); transform: scale(1.05); }
        }

        .agent-pill-memory { border-color: #A7F3D0; }
        .agent-pill-memory .subagent-state-badge { background: #ECFDF5; color: #059669; }
        .agent-pill-memory.active-blink {
            border-color: #10B981 !important;
            box-shadow: 0 0 14px rgba(16, 185, 129, 0.45) !important;
            animation: pulseGreen 1s infinite alternate;
        }
        @keyframes pulseGreen {
            0% { box-shadow: 0 0 4px rgba(16, 185, 129, 0.3); transform: scale(1); }
            100% { box-shadow: 0 0 16px rgba(16, 185, 129, 0.6); transform: scale(1.05); }
        }

        .agent-pill-preview { border-color: #FDE68A; }
        .agent-pill-preview .subagent-state-badge { background: #FFFBEB; color: #D97706; }
        .agent-pill-preview.active-blink {
            border-color: #F59E0B !important;
            box-shadow: 0 0 14px rgba(245, 158, 11, 0.45) !important;
            animation: pulseAmber 1s infinite alternate;
        }
        @keyframes pulseAmber {
            0% { box-shadow: 0 0 4px rgba(245, 158, 11, 0.3); transform: scale(1); }
            100% { box-shadow: 0 0 16px rgba(245, 158, 11, 0.6); transform: scale(1.05); }
        }

        .agent-pill-automation { border-color: #DDD6FE; }
        .agent-pill-automation .subagent-state-badge { background: #F5F3FF; color: #7C3AED; }
        .agent-pill-automation.active-blink {
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 14px rgba(139, 92, 246, 0.45) !important;
            animation: pulsePurple 1s infinite alternate;
        }
        @keyframes pulsePurple {
            0% { box-shadow: 0 0 4px rgba(139, 92, 246, 0.3); transform: scale(1); }
            100% { box-shadow: 0 0 16px rgba(139, 92, 246, 0.6); transform: scale(1.05); }
        }

        .agent-pill-coding { border-color: #FBCFE8; }
        .agent-pill-coding .subagent-state-badge { background: #FDF2F8; color: #DB2777; }
        .agent-pill-coding.active-blink {
            border-color: #EC4899 !important;
            box-shadow: 0 0 14px rgba(236, 72, 153, 0.45) !important;
            animation: pulsePink 1s infinite alternate;
        }
        @keyframes pulsePink {
            0% { box-shadow: 0 0 4px rgba(236, 72, 153, 0.3); transform: scale(1); }
            100% { box-shadow: 0 0 16px rgba(236, 72, 153, 0.6); transform: scale(1.05); }
        }

        /* 4. Conversational Chat Stream */
        .chat-feed {
            display: flex; flex-direction: column; gap: 8px; flex: 1; padding: 4px 0;
        }
        .chat-bubble {
            max-width: 88%; padding: 10px 14px; border-radius: 14px; font-size: 0.86rem; line-height: 1.44; word-break: break-word;
        }
        .chat-bubble.user { align-self: flex-end; background: linear-gradient(135deg, #0284C7, #0369A1); color: #FFF; border-bottom-right-radius: 3px; box-shadow: 0 2px 8px rgba(2, 132, 199, 0.2); }
        .chat-bubble.assistant {
            align-self: flex-start; background: #FFFFFF; color: var(--text-primary);
            border: 1px solid var(--border); border-bottom-left-radius: 3px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }
        .agent-pill-tag {
            display: inline-block; font-size: 0.6rem; font-weight: 800; padding: 2px 6px; border-radius: 5px;
            margin-bottom: 4px; text-transform: uppercase;
        }
        .tag-research { background: #E0F2FE; color: #0284C7; }
        .tag-memory { background: #ECFDF5; color: #059669; }
        .tag-preview { background: #FFFBEB; color: #D97706; }
        .tag-automation { background: #F5F3FF; color: #7C3AED; }
        .tag-coding { background: #FDF2F8; color: #DB2777; }
        .tag-core { background: #F0F9FF; color: #0284C7; }

        /* 5. Live Ticker / Subtitles Bar (Right above the dock) */
        .subtitles-ticker-bar {
            position: absolute; bottom: 62px; left: 0; right: 0; max-width: 480px; margin: 0 auto;
            padding: 0 12px 3px 12px; z-index: 25; pointer-events: none;
        }
        .subtitles-box {
            background: rgba(255, 255, 255, 0.96); border: 1px solid #BAE6FD;
            border-radius: 14px; padding: 5px 12px; display: flex; align-items: center; gap: 8px;
            font-size: 0.72rem; color: #0369A1; pointer-events: auto; backdrop-filter: blur(8px);
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.1);
        }
        .subtitles-box i { font-size: 0.85rem; color: #0284C7; }
        .subtitles-content { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 600; }

        /* 6. Bottom Sticky Dock ("ASK RB Agent") */
        .ask-rb-dock {
            position: absolute; bottom: 0; left: 0; right: 0; max-width: 480px; margin: 0 auto;
            height: 62px; background: #FFFFFF; border-top: 1px solid var(--border);
            padding: 8px 12px; display: flex; align-items: center; gap: 6px; z-index: 30;
            box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.04);
        }
        
        /* 1. Plus (+) Attachment Button */
        .dock-btn-plus {
            width: 36px; height: 36px; border-radius: 50%; background: #F1F5F9; border: 1px solid var(--border);
            color: #0284C7; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center;
            flex-shrink: 0; transition: all 0.2s;
        }
        .dock-btn-plus:active { transform: scale(0.92); }

        /* 2. Pill Selector */
        .dock-model-pill {
            background: #F0F9FF; border: 1px solid #BAE6FD; border-radius: 16px;
            padding: 4px 8px; font-size: 0.68rem; font-weight: 700; color: #0284C7; cursor: pointer;
            display: flex; align-items: center; gap: 4px; white-space: nowrap; flex-shrink: 0;
        }

        /* Input Shell ("ASK RB Agent...") */
        .dock-input-shell {
            flex: 1; background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 20px;
            padding: 6px 12px; display: flex; align-items: center; min-width: 0;
        }
        .dock-input-shell input {
            width: 100%; background: transparent; border: none; outline: none; color: #0F172A; font-size: 0.84rem;
        }
        .dock-input-shell input::placeholder { color: #94A3B8; font-size: 0.8rem; }

        /* 3. Animated "Live Chat" Circular Button (Pulsing Voice Mode) */
        .dock-btn-livechat {
            width: 36px; height: 36px; border-radius: 50%;
            background: radial-gradient(circle, #0284C7 0%, #0369A1 70%);
            border: 1.5px solid #38BDF8;
            color: #FFF; font-size: 0.85rem; cursor: pointer; display: flex; align-items: center; justify-content: center;
            flex-shrink: 0; position: relative; animation: pulseLiveChat 2s infinite ease-in-out;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
        }
        @keyframes pulseLiveChat {
            0%, 100% { box-shadow: 0 0 4px rgba(2, 132, 199, 0.3); transform: scale(1); }
            50% { box-shadow: 0 0 14px rgba(2, 132, 199, 0.6); transform: scale(1.06); }
        }

        /* 4. Microphone Audio Button */
        .dock-btn-mic {
            width: 36px; height: 36px; border-radius: 50%; background: #F1F5F9; border: 1px solid var(--border);
            color: #0284C7; font-size: 0.95rem; cursor: pointer; display: flex; align-items: center; justify-content: center;
            flex-shrink: 0; transition: all 0.2s;
        }
        .dock-btn-mic.recording {
            background: #EF4444; color: #FFF; animation: pulseRecording 1.1s infinite;
        }
        @keyframes pulseRecording { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.16); } }

        /* 5. Send Button */
        .dock-btn-send {
            width: 36px; height: 36px; border-radius: 50%;
            background: linear-gradient(135deg, #0284C7, #0EA5E9); border: none;
            color: #FFFFFF; font-size: 0.95rem; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center;
            flex-shrink: 0; transition: all 0.2s; box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
        }
        .dock-btn-send:active { transform: scale(0.92); }

        /* Collapsible Navigation Drawer */
        .drawer-overlay {
            position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px);
            z-index: 50; display: none; opacity: 0; transition: opacity 0.3s;
        }
        .drawer-overlay.active { display: block; opacity: 1; }
        .drawer {
            position: fixed; top: 0; bottom: 0; left: 0; width: 280px; max-width: 80vw;
            background: #FFFFFF; z-index: 55; display: flex; flex-direction: column;
            transform: translateX(-100%); transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            border-right: 1px solid var(--border); box-shadow: 10px 0 30px rgba(0, 0, 0, 0.08);
        }
        .drawer.active { transform: translateX(0); }
        .drawer-header {
            padding: 20px 18px 14px 18px; border-bottom: 1px solid var(--border); background: #F8FAFC;
        }
        .drawer-user-row { display: flex; align-items: center; gap: 12px; }
        .drawer-avatar {
            width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, #0284C7, #0EA5E9);
            color: #FFFFFF; font-weight: 900; font-size: 1rem; display: flex; align-items: center; justify-content: center;
        }
        .drawer-user-name { font-size: 0.88rem; font-weight: 800; color: #0F172A; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 170px; }
        .drawer-user-sub { font-size: 0.68rem; color: #059669; font-weight: 700; margin-top: 2px; }

        .drawer-menu { flex: 1; overflow-y: auto; padding: 10px 12px; display: flex; flex-direction: column; gap: 3px; }
        .drawer-item {
            display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 10px;
            color: #475569; font-size: 0.86rem; font-weight: 600; cursor: pointer; transition: all 0.2s;
        }
        .drawer-item i { width: 18px; text-align: center; font-size: 0.95rem; }
        .drawer-item:hover, .drawer-item.active { background: #F0F9FF; color: #0284C7; }

        .drawer-footer {
            padding: 12px 14px; border-top: 1px solid var(--border); display: flex; flex-direction: column; gap: 8px; background: #F8FAFC;
        }
        .drawer-search-input {
            background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px;
            padding: 7px 12px; font-size: 0.78rem; color: #0F172A; outline: none; width: 100%;
        }
        .btn-new-chat {
            background: linear-gradient(135deg, #0284C7, #0EA5E9); color: #FFFFFF; border: none;
            padding: 9px; border-radius: 8px; font-size: 0.82rem; font-weight: 800; cursor: pointer;
            display: flex; align-items: center; justify-content: center; gap: 6px; box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
        }

        /* Sub-Agents Expanded Modal / View */
        .subagents-expanded-modal {
            position: fixed; inset: 0; background: rgba(248, 250, 252, 0.98); backdrop-filter: blur(8px);
            z-index: 60; display: none; flex-direction: column; max-width: 480px; margin: 0 auto;
        }
        .subagents-expanded-modal.active { display: flex; }
        .modal-top-bar {
            padding: 12px 16px; border-bottom: 1px solid var(--border); background: #FFFFFF;
            display: flex; align-items: center; justify-content: space-between;
        }
        .modal-top-title { font-size: 0.95rem; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 8px; }
        .modal-close-btn { background: none; border: none; color: #64748B; font-size: 1.3rem; cursor: pointer; }
        .modal-scroll-body { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; }

        .expanded-agent-card {
            background: #FFFFFF; border: 1px solid var(--border); border-radius: 12px; padding: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }
        .expanded-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
        .expanded-agent-title { font-weight: 800; font-size: 0.88rem; color: #0F172A; display: flex; align-items: center; gap: 8px; }
        .expanded-input-row { display: flex; gap: 6px; margin-top: 8px; }
        .expanded-input-row input {
            flex: 1; background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px;
            padding: 7px 10px; font-size: 0.8rem; color: #0F172A; outline: none;
        }
        .btn-run-agent {
            background: #0284C7; color: #FFF; border: none; border-radius: 8px;
            padding: 7px 12px; font-size: 0.78rem; font-weight: 700; cursor: pointer;
        }
        .agent-output-box {
            margin-top: 8px; background: #F8FAFC; border: 1px solid #E2E8F0;
            border-radius: 8px; padding: 8px; font-size: 0.76rem; color: #334155; max-height: 120px; overflow-y: auto; white-space: pre-wrap; display: none;
        }

        /* Generic Modals (Settings, Notes, Skills, Code, Web Preview) */
        .subview-modal {
            position: fixed; inset: 0; background: rgba(248, 250, 252, 0.98); backdrop-filter: blur(8px);
            z-index: 60; display: none; flex-direction: column; max-width: 480px; margin: 0 auto;
        }
        .subview-modal.active { display: flex; }
        .subview-body { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 12px; }

        .form-group { display: flex; flex-direction: column; gap: 5px; }
        .form-group label { font-size: 0.74rem; font-weight: 700; color: #475569; }
        .form-group input, .form-group select, .form-group textarea {
            background: #FFFFFF; border: 1px solid #CBD5E1; color: #0F172A;
            padding: 8px 12px; border-radius: 8px; font-size: 0.84rem; outline: none;
        }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: #0284C7; }
        .btn-primary-action {
            background: linear-gradient(135deg, #0284C7, #0EA5E9); color: #FFFFFF; font-weight: 800;
            border: none; padding: 9px 16px; border-radius: 8px; font-size: 0.84rem; cursor: pointer;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
        }

        .settings-tab-strip { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 6px; border-bottom: 1px solid var(--border); }
        .stab-btn {
            background: #F1F5F9; border: 1px solid var(--border); color: #64748B;
            padding: 6px 10px; border-radius: 8px; font-size: 0.74rem; font-weight: 600; cursor: pointer; white-space: nowrap;
        }
        .stab-btn.active { background: #E0F2FE; color: #0284C7; border-color: #0284C7; }
        .stab-pane { display: none; flex-direction: column; gap: 10px; margin-top: 10px; }
        .stab-pane.active { display: flex; }

        .status-chip-tag { display: inline-block; padding: 3px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; }
        .chip-success { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
        .chip-warning { background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; }
        .chip-danger { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }

        /* Responsive Viewport & Device Adapters */
        @media (min-width: 501px) {
            body {
                background: radial-gradient(circle at 50% 20%, #E0F2FE 0%, #EFF6FF 100%);
            }
            .app-container {
                height: 94dvh;
                max-height: 890px;
                border-radius: 28px;
                border: 1px solid #CBD5E1;
                box-shadow: 0 20px 60px rgba(15, 23, 42, 0.12);
            }
            .subtitles-ticker-bar {
                max-width: 480px;
            }
            .ask-rb-dock {
                max-width: 480px;
                border-bottom-left-radius: 28px;
                border-bottom-right-radius: 28px;
            }
            .drawer {
                border-top-left-radius: 28px;
                border-bottom-left-radius: 28px;
            }
        }

        @media (max-width: 420px) {
            .app-stage { padding: 8px 10px 115px 10px; gap: 8px; }
            .jarvis-reactor-disc { width: 114px; height: 114px; }
            .reactor-orb-core { width: 72px; height: 72px; }
            .orb-title { font-size: 0.74rem; }
            .orb-subtitle { font-size: 0.48rem; }
            .subagent-pill { padding: 6px 2px; }
            .subagent-icon-emoji { font-size: 1.1rem; }
            .subagent-name-text { font-size: 0.58rem; }
            .subagent-state-badge { font-size: 0.46rem; padding: 1px 3px; }
            .ask-rb-dock { height: 56px; padding: 6px 8px; gap: 4px; }
            .dock-btn-plus, .dock-btn-livechat, .dock-btn-mic, .dock-btn-send { width: 32px; height: 32px; font-size: 0.8rem; }
            .dock-model-pill { padding: 3px 6px; font-size: 0.60rem; gap: 3px; }
            .dock-input-shell { padding: 5px 8px; }
            .dock-input-shell input { font-size: 0.78rem; }
            .subtitles-ticker-bar { bottom: 56px; padding: 0 8px 3px 8px; }
            .subtitles-box { font-size: 0.68rem; padding: 4px 8px; }
        }
    </style>
</head>
<body>

    <div class="app-container">
        <!-- 1. Top Header -->
        <header class="app-header">
            <div class="header-left">
                <button class="btn-hamburger" onclick="toggleDrawer(true)" aria-label="Open Menu">
                    <i class="fa-solid fa-bars"></i>
                </button>
                <div class="header-title-box">
                    <div class="header-title">RB<span>.AGENT</span></div>
                    <div class="header-subtitle">Personal AI Assistant</div>
                </div>
            </div>
            <div class="status-pill">
                <div class="status-dot"></div>
                <span id="headerBattStatus">LIVE</span>
            </div>
        </header>

        <!-- Main Core Stage -->
        <main class="app-stage" id="appMainStage">
            <!-- Dynamic Greeting Banner -->
            <div class="greeting-banner">
                <div>
                    <div class="greeting-text-title" id="greetingText">नमस्ते, Ram Binay Pandit</div>
                    <div class="greeting-text-sub">आज आपका क्या प्लान है</div>
                </div>
                <i class="fa-solid fa-bolt greeting-icon"></i>
            </div>

            <!-- 2. Centerpiece: Jarvis Arc Reactor Circular HUD -->
            <div class="jarvis-reactor-stage">
                <div class="jarvis-reactor-disc" onclick="openAgentsExpandedModal()" title="Tap to expand Sub-Agents">
                    <div class="orbit-outer"></div>
                    <div class="orbit-mid"></div>
                    <div class="reactor-orb-core">
                        <i class="fa-solid fa-atom" style="color: var(--accent-cyan); font-size: 0.85rem; margin-bottom: 1px;"></i>
                        <div class="orb-title">RB Agent</div>
                        <div class="orb-subtitle">ORCHESTRATOR</div>
                    </div>
                </div>
                <div class="reactor-hint" onclick="openAgentsExpandedModal()">
                    <i class="fa-solid fa-circle-nodes"></i> Tap to expand 5 Sub-Agents
                </div>
            </div>

            <!-- 3. Sub-Agents Integration (Compact Cards with Real-Time Blinking Glow) -->
            <div class="subagents-strip">
                <!-- 1. 🌐 Research & Web Agent (Cyan) -->
                <div class="subagent-pill agent-pill-research" id="card-agent-research" onclick="openAgentsExpandedModal('research')">
                    <div class="subagent-icon-emoji">🌐</div>
                    <div class="subagent-name-text">Research</div>
                    <div class="subagent-state-badge" id="badge-research">READY</div>
                </div>

                <!-- 2. 🧠 Memory & Notes Agent (Emerald Green) -->
                <div class="subagent-pill agent-pill-memory" id="card-agent-memory" onclick="openAgentsExpandedModal('memory')">
                    <div class="subagent-icon-emoji">🧠</div>
                    <div class="subagent-name-text">Memory</div>
                    <div class="subagent-state-badge" id="badge-memory">SYNCED</div>
                </div>

                <!-- 3. 👁️ Preview / View Agent (Amber) -->
                <div class="subagent-pill agent-pill-preview" id="card-agent-preview" onclick="openAgentsExpandedModal('preview')">
                    <div class="subagent-icon-emoji">👁️</div>
                    <div class="subagent-name-text">Preview</div>
                    <div class="subagent-state-badge" id="badge-preview">STANDBY</div>
                </div>

                <!-- 4. ⚡ Automation Agent (Electric Purple) -->
                <div class="subagent-pill agent-pill-automation" id="card-agent-automation" onclick="triggerCallAnnouncementTest()">
                    <div class="subagent-icon-emoji">⚡</div>
                    <div class="subagent-name-text">Automation</div>
                    <div class="subagent-state-badge" id="badge-automation">HARDWARE</div>
                </div>

                <!-- 5. 💻 Coding & GitHub Agent (Hot Pink) -->
                <div class="subagent-pill agent-pill-coding" id="card-agent-coding" onclick="openAgentsExpandedModal('coding')">
                    <div class="subagent-icon-emoji">💻</div>
                    <div class="subagent-name-text">Coding</div>
                    <div class="subagent-state-badge" id="badge-coding">SANDBOX</div>
                </div>
            </div>

            <!-- 4. Conversational Chat Stream -->
            <div class="chat-feed" id="chatFeedStream">
                <div class="chat-bubble assistant">
                    <div class="agent-pill-tag tag-core">RB System</div>
                    <div>नमस्ते Ram Binay Pandit! RB Agent OS is online. Jarvis Arc Reactor is synchronized with all 5 Sub-Agents and persistent memory. आज आपका क्या प्लान है?</div>
                </div>
            </div>
        </main>

        <!-- 5. Live Ticker / Subtitles Bar (Right above the dock) -->
        <div class="subtitles-ticker-bar">
            <div class="subtitles-box">
                <i class="fa-solid fa-closed-captioning"></i>
                <div class="subtitles-content" id="subtitlesTickerText">
                    RB Agent ready • Autonomous intent routing active
                </div>
            </div>
        </div>

        <!-- 6. Bottom Sticky Dock ("ASK RB Agent") -->
        <footer class="ask-rb-dock">
            <!-- 1. Plus (+) Attachment Button -->
            <button class="dock-btn-plus" onclick="triggerCameraCapture()" title="Attach / Camera">
                <i class="fa-solid fa-plus"></i>
            </button>

            <!-- 2. "Gemini 3 Flash" Pill Selector -->
            <div class="dock-model-pill" onclick="cycleGeminiModel()" id="dockModelSelector" title="LLM Model Selector">
                <i class="fa-solid fa-bolt" style="font-size: 0.65rem;"></i>
                <span id="dockModelText">Gemini 3 Flash</span>
            </div>

            <!-- Input Box -->
            <div class="dock-input-shell">
                <input type="text" id="dockChatInput" placeholder="ASK RB Agent..." onkeypress="onDockEnter(event)">
            </div>

            <!-- 3. Animated "Live Chat" Circular Button (Pulsing Voice Mode) -->
            <div class="dock-btn-livechat" onclick="toggleVoiceMode()" title="Live Chat (Pulsing Audio Mode)">
                <i class="fa-solid fa-wave-square"></i>
            </div>

            <!-- 4. Microphone Audio Button -->
            <button class="dock-btn-mic" id="dockMicBtn" onclick="toggleVoiceMode()" title="Voice Input">
                <i class="fa-solid fa-microphone"></i>
            </button>

            <!-- 5. Send Button -->
            <button class="dock-btn-send" onclick="sendDockMessage()" title="Send Command">
                <i class="fa-solid fa-paper-plane"></i>
            </button>
        </footer>

        <!-- Collapsible Navigation Drawer (8 Clean Items) -->
        <div class="drawer-overlay" id="drawerBackdrop" onclick="toggleDrawer(false)"></div>
        <aside class="drawer" id="mainSidebarDrawer">
            <div class="drawer-header">
                <div class="drawer-user-row">
                    <div class="drawer-avatar" id="drawerAvatarPill">RP</div>
                    <div>
                        <div class="drawer-user-name" id="drawerUserName">Ram Binay Pandit</div>
                        <div class="drawer-user-sub"><i class="fa-solid fa-circle" style="font-size: 0.45rem;"></i> Master Operator</div>
                    </div>
                </div>
            </div>

            <nav class="drawer-menu">
                <div class="drawer-item active" onclick="navigateDrawer('home')">
                    <i class="fa-solid fa-house"></i> Home
                </div>
                <div class="drawer-item" onclick="openSubview('web-preview')">
                    <i class="fa-solid fa-globe"></i> Web Preview
                </div>
                <div class="drawer-item" onclick="openSubview('code-preview')">
                    <i class="fa-solid fa-code"></i> Code Preview & Terminal
                </div>
                <div class="drawer-item" onclick="openSubview('file-preview')">
                    <i class="fa-solid fa-folder-open"></i> File Preview & Notes
                </div>
                <div class="drawer-item" onclick="openSubview('settings')">
                    <i class="fa-solid fa-sliders"></i> Settings Hub
                </div>
                <div class="drawer-item" onclick="openSubview('projects')">
                    <i class="fa-solid fa-cubes"></i> Projects
                </div>
                <div class="drawer-item" onclick="openSubview('skills')">
                    <i class="fa-solid fa-puzzle-piece"></i> Skill Add & Self-Training
                </div>
                <div class="drawer-item" onclick="openSubview('chats')">
                    <i class="fa-solid fa-comments"></i> Chats History
                </div>
            </nav>

            <div class="drawer-footer">
                <input type="text" class="drawer-search-input" id="drawerSearchInput" placeholder="Search chats..." oninput="filterDrawerChats()">
                <button class="btn-new-chat" onclick="startNewChatSession()">
                    <i class="fa-solid fa-plus"></i> New chat
                </button>
            </div>
        </aside>

        <!-- Sub-Agents Expanded Interactive Modal -->
        <div class="subagents-expanded-modal" id="agentsExpandedModal">
            <div class="modal-top-bar">
                <div class="modal-top-title">
                    <i class="fa-solid fa-network-wired" style="color: var(--accent-cyan);"></i> 5 SUB-AGENTS WORKSPACE
                </div>
                <button class="modal-close-btn" onclick="closeAgentsExpandedModal()"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="modal-scroll-body">
                <!-- 1. Research & Web Agent -->
                <div class="expanded-agent-card" style="border-left: 3px solid var(--accent-cyan);">
                    <div class="expanded-card-header">
                        <div class="expanded-agent-title">🌐 Research & Web Agent</div>
                        <span class="status-chip-tag chip-success">LIVE API</span>
                    </div>
                    <div style="font-size: 0.74rem; color: var(--text-muted);">Real-time DuckDuckGo instant web intelligence and live URL scraper.</div>
                    <div class="expanded-input-row">
                        <input type="text" id="wsResearchInput" value="latest Google Gemini 2.5 flash updates">
                        <button class="btn-run-agent" onclick="executeWsResearch()">Search</button>
                    </div>
                    <div class="agent-output-box" id="wsResearchOutput"></div>
                </div>

                <!-- 2. Memory & Notes Agent -->
                <div class="expanded-agent-card" style="border-left: 3px solid var(--accent-green);">
                    <div class="expanded-card-header">
                        <div class="expanded-agent-title">🧠 Memory & Notes Agent</div>
                        <span class="status-chip-tag chip-success">SQLITE & SUPABASE</span>
                    </div>
                    <div style="font-size: 0.74rem; color: var(--text-muted);">Parses intents like "यह चीज़ सेव कर लो" and syncs long-term memory.</div>
                    <div class="expanded-input-row">
                        <input type="text" id="wsMemoryInput" value="यह चीज़ सेव कर लो: Meeting with Ram Binay Pandit tomorrow">
                        <button class="btn-run-agent" onclick="executeWsMemory()">Store</button>
                    </div>
                    <div class="agent-output-box" id="wsMemoryOutput"></div>
                </div>

                <!-- 3. Preview / View Agent -->
                <div class="expanded-agent-card" style="border-left: 3px solid var(--accent-amber);">
                    <div class="expanded-card-header">
                        <div class="expanded-agent-title">👁️ Preview / View Agent</div>
                        <span class="status-chip-tag chip-warning">SCRAPER</span>
                    </div>
                    <div style="font-size: 0.74rem; color: var(--text-muted);">Scrapes metadata, page titles, and inspects Markdown content.</div>
                    <div class="expanded-input-row">
                        <input type="text" id="wsPreviewInput" value="https://deepmind.google/technologies/gemini/">
                        <button class="btn-run-agent" onclick="executeWsPreview()">Preview</button>
                    </div>
                    <div class="agent-output-box" id="wsPreviewOutput"></div>
                </div>

                <!-- 4. Automation Agent -->
                <div class="expanded-agent-card" style="border-left: 3px solid var(--accent-purple);">
                    <div class="expanded-card-header">
                        <div class="expanded-agent-title">⚡ Automation Agent</div>
                        <span class="status-chip-tag chip-success">TERMUX API</span>
                    </div>
                    <div style="font-size: 0.74rem; color: var(--text-muted);">Device controls (flashlight, battery, haptics, and voice call announcements).</div>
                    <div style="display: flex; gap: 6px; margin-top: 8px;">
                        <button class="btn-run-agent" onclick="triggerHardwareAction('torch')"><i class="fa-solid fa-lightbulb"></i> Torch</button>
                        <button class="btn-run-agent" onclick="triggerHardwareAction('battery')"><i class="fa-solid fa-battery-half"></i> Battery</button>
                        <button class="btn-run-agent" onclick="triggerHardwareAction('vibrate')"><i class="fa-solid fa-mobile-screen"></i> Haptic</button>
                        <button class="btn-run-agent" onclick="triggerCallAnnouncementTest()"><i class="fa-solid fa-phone"></i> Call Announce</button>
                    </div>
                    <div class="agent-output-box" id="wsAutomationOutput"></div>
                </div>

                <!-- 5. Coding & GitHub Agent -->
                <div class="expanded-agent-card" style="border-left: 3px solid var(--accent-pink);">
                    <div class="expanded-card-header">
                        <div class="expanded-agent-title">💻 Coding & GitHub Agent</div>
                        <span class="status-chip-tag chip-success">SANDBOX</span>
                    </div>
                    <div style="font-size: 0.74rem; color: var(--text-muted);">Runs Python 3 on Termux Linux and syncs repositories via GitHub API.</div>
                    <div class="expanded-input-row">
                        <input type="text" id="wsCodingInput" value="torvalds">
                        <button class="btn-run-agent" onclick="executeWsGithub()">Fetch Repos</button>
                    </div>
                    <div class="agent-output-box" id="wsCodingOutput"></div>
                </div>
            </div>
        </div>

        <!-- Generic Subviews (Settings Hub, Notes, Skills, Code, Web Preview) -->
        <!-- View: Settings Hub -->
        <div class="subview-modal" id="modal-settings">
            <div class="modal-top-bar">
                <div class="modal-top-title"><i class="fa-solid fa-sliders" style="color: var(--accent-cyan);"></i> Centralized Settings Hub</div>
                <button class="modal-close-btn" onclick="closeSubview('settings')"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="subview-body">
                <div class="settings-tab-strip">
                    <button class="stab-btn active" onclick="switchSettingTab('telegram')">Telegram</button>
                    <button class="stab-btn" onclick="switchSettingTab('whatsapp')">WhatsApp</button>
                    <button class="stab-btn" onclick="switchSettingTab('github')">GitHub PAT</button>
                    <button class="stab-btn" onclick="switchSettingTab('voice')">Voice Profiles</button>
                    <button class="stab-btn" onclick="switchSettingTab('supabase')">Supabase Keys</button>
                    <button class="stab-btn" onclick="switchSettingTab('gemini')">Google Gemini</button>
                </div>

                <!-- Tab: Telegram -->
                <div class="stab-pane active" id="spane-telegram">
                    <div class="form-group">
                        <label>Telegram Bot Token</label>
                        <input type="text" id="setTgToken" placeholder="123456789:ABCdefGhIJKlmNoPQRstuvwxYZ">
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn-primary-action" onclick="handshakeTelegram()"><i class="fa-solid fa-link"></i> Test Handshake</button>
                        <button class="btn-run-agent" onclick="controlTelegram('start')">Start Bot</button>
                        <button class="btn-run-agent" style="background:#475569;" onclick="controlTelegram('stop')">Stop</button>
                    </div>
                    <div id="tgStatusFeedback" style="font-size: 0.74rem; color: var(--text-muted); margin-top: 4px;"></div>
                </div>

                <!-- Tab: WhatsApp -->
                <div class="stab-pane" id="spane-whatsapp">
                    <div class="form-group">
                        <label>Target Phone Number with Country Code</label>
                        <input type="text" id="setWaPhone" placeholder="91XXXXXXXXXX">
                    </div>
                    <div class="form-group">
                        <label>Default Message</label>
                        <input type="text" id="setWaMsg" value="नमस्ते Ram Binay, RB Agent OS message.">
                    </div>
                    <button class="btn-primary-action" onclick="launchWaBridge()"><i class="fa-brands fa-whatsapp"></i> Test WhatsApp Bridge</button>
                </div>

                <!-- Tab: GitHub -->
                <div class="stab-pane" id="spane-github">
                    <div class="form-group">
                        <label>GitHub Username</label>
                        <input type="text" id="setGhUser" value="rambinaypandit798-sudo">
                    </div>
                    <div class="form-group">
                        <label>Personal Access Token (PAT)</label>
                        <input type="password" id="setGhToken" placeholder="ghp_...">
                    </div>
                    <button class="btn-primary-action" onclick="handshakeGitHub()"><i class="fa-brands fa-github"></i> Test Handshake & Sync</button>
                    <div id="ghStatusFeedback" style="font-size: 0.74rem; color: var(--text-muted); margin-top: 4px;"></div>
                </div>

                <!-- Tab: Voice Profiles -->
                <div class="stab-pane" id="spane-voice">
                    <div class="form-group">
                        <label>Voice Accent / Language</label>
                        <select id="setVoiceAccent">
                            <option value="hi-IN">Hindi (India) - hi-IN</option>
                            <option value="en-IN">English (India) - en-IN</option>
                            <option value="en-US">English (US) - en-US</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Speech Pitch (0.5 - 2.0)</label>
                        <input type="number" id="setVoicePitch" step="0.1" value="1.0">
                    </div>
                    <div class="form-group">
                        <label>Speech Rate (0.5 - 2.0)</label>
                        <input type="number" id="setVoiceRate" step="0.1" value="0.95">
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 4px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: #FFF;">
                            <input type="checkbox" id="setWakeWord" checked> Enable "Hey RB" Wake Word
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: #FFF;">
                            <input type="checkbox" id="setCallAnnounce" checked> Enable Voice Call Announcements
                        </label>
                    </div>
                </div>

                <!-- Tab: Supabase -->
                <div class="stab-pane" id="spane-supabase">
                    <div class="form-group">
                        <label>Supabase Project URL</label>
                        <input type="text" id="setSbUrl" placeholder="https://xxxxxxxx.supabase.co">
                    </div>
                    <div class="form-group">
                        <label>Supabase API Key (anon public or service_role)</label>
                        <input type="password" id="setSbKey" placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...">
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn-primary-action" onclick="handshakeSupabase()"><i class="fa-solid fa-database"></i> Test & Auto-Migrate Schema</button>
                        <button class="btn-run-agent" onclick="syncSupabaseCloud()"><i class="fa-solid fa-cloud-arrow-up"></i> Sync Now</button>
                    </div>
                    <div id="sbStatusFeedback" style="font-size: 0.74rem; color: var(--text-muted); margin-top: 4px;"></div>
                </div>

                <!-- Tab: Gemini -->
                <div class="stab-pane" id="spane-gemini">
                    <div class="form-group">
                        <label>Google Gemini API Key</label>
                        <input type="password" id="setGeminiKey" placeholder="AIzaSy...">
                    </div>
                    <button class="btn-primary-action" onclick="handshakeGemini()"><i class="fa-solid fa-key"></i> Test Gemini Handshake</button>
                    <div id="geminiStatusFeedback" style="font-size: 0.74rem; color: var(--text-muted); margin-top: 4px;"></div>
                </div>

                <button class="btn-primary-action" style="margin-top: 14px;" onclick="saveAllSettingsLive()">
                    <i class="fa-solid fa-floppy-disk"></i> Save Configurations
                </button>
            </div>
        </div>

        <!-- View: Skills Add & Self-Training -->
        <div class="subview-modal" id="modal-skills">
            <div class="modal-top-bar">
                <div class="modal-top-title"><i class="fa-solid fa-puzzle-piece" style="color: var(--accent-green);"></i> Skill Add & Self-Training</div>
                <button class="modal-close-btn" onclick="closeSubview('skills')"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="subview-body">
                <div style="font-size: 0.76rem; color: var(--text-muted);">Feed custom prompt directives to auto-improve RB Agent. Persists dynamically to SQLite & Supabase.</div>
                <div class="form-group">
                    <label>Skill Name (e.g. Hindi Tech Translator)</label>
                    <input type="text" id="skillNameInput" placeholder="Skill Name">
                </div>
                <div class="form-group">
                    <label>Trigger / Context Description</label>
                    <input type="text" id="skillDescInput" placeholder="When user asks about...">
                </div>
                <div class="form-group">
                    <label>System Directives & Instructions</label>
                    <textarea id="skillPromptInput" rows="4" placeholder="You are a specialized expert in..."></textarea>
                </div>
                <button class="btn-primary-action" onclick="saveSkillTraining()"><i class="fa-solid fa-graduation-cap"></i> Train & Register Skill</button>
                <div id="skillFeedbackMsg" style="font-size: 0.74rem; margin-top: 4px;"></div>

                <div style="font-weight: 800; font-size: 0.86rem; color: #FFF; margin-top: 14px;">Active Skills in Live Memory:</div>
                <div id="activeSkillsList" style="display: flex; flex-direction: column; gap: 8px;">Loading skills...</div>
            </div>
        </div>

        <!-- View: Web Preview -->
        <div class="subview-modal" id="modal-web-preview">
            <div class="modal-top-bar">
                <div class="modal-top-title"><i class="fa-solid fa-globe" style="color: var(--accent-cyan);"></i> Web Preview & Live Search</div>
                <button class="modal-close-btn" onclick="closeSubview('web-preview')"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="subview-body">
                <div class="form-group">
                    <label>Web Search Query or URL</label>
                    <div style="display: flex; gap: 6px;">
                        <input type="text" id="webPreviewQuery" value="Google Gemini latest updates">
                        <button class="btn-primary-action" onclick="runWebPreviewSearch()">Search</button>
                    </div>
                </div>
                <div id="webPreviewOutputBox" style="font-size: 0.8rem; color: #CBD5E1; line-height: 1.5; white-space: pre-wrap; max-height: 400px; overflow-y: auto;"></div>
            </div>
        </div>

        <!-- View: Code Preview & Terminal -->
        <div class="subview-modal" id="modal-code-preview">
            <div class="modal-top-bar">
                <div class="modal-top-title"><i class="fa-solid fa-code" style="color: var(--accent-pink);"></i> Code Preview & Terminal</div>
                <button class="modal-close-btn" onclick="closeSubview('code-preview')"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="subview-body">
                <div class="form-group">
                    <label>Python 3 Sandbox Execution</label>
                    <textarea id="codeRunnerArea" rows="6" style="font-family: monospace;">name = "Ram Binay Pandit"
print(f"नमस्ते {name}, RB Agent code runner executed live!")
</textarea>
                </div>
                <button class="btn-primary-action" onclick="runCodeLive()"><i class="fa-solid fa-play"></i> Run Script</button>
                <pre id="codeOutputConsole" style="background: #05080E; border: 1px solid var(--border); border-radius: 8px; padding: 10px; font-size: 0.78rem; color: var(--accent-cyan); max-height: 160px; overflow-y: auto;">Terminal ready.</pre>
            </div>
        </div>

        <!-- View: File Preview & Notes -->
        <div class="subview-modal" id="modal-file-preview">
            <div class="modal-top-bar">
                <div class="modal-top-title"><i class="fa-solid fa-folder-open" style="color: var(--accent-amber);"></i> File Preview & Notes</div>
                <button class="modal-close-btn" onclick="closeSubview('file-preview')"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="subview-body">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 800; font-size: 0.86rem; color: #FFF;">Persistent SQLite Notes</div>
                    <button class="btn-run-agent" onclick="loadNotesList()">Refresh</button>
                </div>
                <div id="notesContainerList" style="display: flex; flex-direction: column; gap: 8px;">Loading notes...</div>
            </div>
        </div>

        <!-- View: Projects -->
        <div class="subview-modal" id="modal-projects">
            <div class="modal-top-bar">
                <div class="modal-top-title"><i class="fa-solid fa-cubes" style="color: var(--accent-purple);"></i> Projects Overview</div>
                <button class="modal-close-btn" onclick="closeSubview('projects')"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="subview-body">
                <div class="expanded-agent-card">
                    <div style="font-weight: 800; font-size: 1rem; color: #FFF;">rb_ai (RB Agent OS)</div>
                    <div style="font-size: 0.76rem; color: var(--text-muted); margin-top: 2px;">Developed for Ram Binay kumar Pandit</div>
                    <div style="margin-top: 10px; font-size: 0.78rem; color: #CBD5E1; display: flex; flex-direction: column; gap: 4px;">
                        <div>• <strong>Host</strong>: Android Termux Linux Userland (aarch64)</div>
                        <div>• <strong>Storage</strong>: SQLite 3 (<code>rb_agent.db</code>) + Live Supabase Engine</div>
                        <div>• <strong>Orchestrator</strong>: Jarvis Arc Reactor Core + 5 Sub-Agents</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- View: Chats -->
        <div class="subview-modal" id="modal-chats">
            <div class="modal-top-bar">
                <div class="modal-top-title"><i class="fa-solid fa-comments" style="color: var(--accent-blue);"></i> Chat History</div>
                <button class="modal-close-btn" onclick="closeSubview('chats')"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="subview-body">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.76rem; color: var(--text-muted);">Stored in SQLite <code>chat_history</code></span>
                    <button class="btn-run-agent" style="background: #EF4444;" onclick="clearAllChatsLive()">Clear History</button>
                </div>
                <div id="chatsModalList" style="display: flex; flex-direction: column; gap: 8px; max-height: 420px; overflow-y: auto;">Loading chats...</div>
            </div>
        </div>
    </div>

    <script>
        let currentMaster = "Ram Binay Pandit";
        let isVoiceMode = false;
        let speechRec = null;
        let currentModel = "gemini-3-flash-preview";

        window.addEventListener('DOMContentLoaded', () => {
            initSystemOS();
            initSpeechRecognizer();
        });

        async function initSystemOS() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                if (data.user_name) {
                    currentMaster = data.user_name;
                    syncUserHeaders(data.user_name);
                }
                if (data.device && data.device.battery) {
                    const b = data.device.battery;
                    document.getElementById('headerBattStatus').innerText = `${b.percentage || '85'}% LIVE`;
                }
            } catch(e) {
                console.log(e);
            }
            loadNotesList();
            loadSkillsList();
            loadChatsList();
        }

        function syncUserHeaders(name) {
            document.getElementById('greetingText').innerText = `नमस्ते, ${name}`;
            document.getElementById('drawerUserName').innerText = name;
            const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
            document.getElementById('drawerAvatarPill').innerText = initials || 'RP';
        }

        // Sub-Agent Blinking / Pulsing
        function triggerAgentBlink(tag, isBlinking = true) {
            const map = {
                'research': { id: 'card-agent-research', badge: 'badge-research', name: 'Research & Web Agent' },
                'memory': { id: 'card-agent-memory', badge: 'badge-memory', name: 'Memory & Notes Agent' },
                'preview': { id: 'card-agent-preview', badge: 'badge-preview', name: 'Preview / View Agent' },
                'automation': { id: 'card-agent-automation', badge: 'badge-automation', name: 'Automation Agent' },
                'coding': { id: 'card-agent-coding', badge: 'badge-coding', name: 'Coding & GitHub Agent' }
            };

            Object.values(map).forEach(a => {
                const el = document.getElementById(a.id);
                if (el) el.classList.remove('active-blink');
            });

            if (isBlinking && map[tag]) {
                const target = map[tag];
                const card = document.getElementById(target.id);
                const badge = document.getElementById(target.badge);
                if (card) card.classList.add('active-blink');
                if (badge) badge.innerText = 'ACTIVE';
                setSubtitle(`${target.name} actively processing...`);
            } else if (!isBlinking && map[tag]) {
                const badge = document.getElementById(map[tag].badge);
                if (badge) badge.innerText = 'READY';
            }
        }

        // Chat Message Dispatcher from Bottom Dock
        async function sendDockMessage() {
            const input = document.getElementById('dockChatInput');
            const text = input.value.trim();
            if (!text) return;

            addChatBubble('user', text);
            input.value = '';
            setSubtitle(`User: "${text}"`);

            // Predict intent for instant visual blinking
            const lower = text.toLowerCase();
            let predicted = 'core';
            if (lower.includes('सेव') || lower.includes('save') || lower.includes('remember') || lower.includes('याद')) predicted = 'memory';
            else if (lower.includes('torch') || lower.includes('battery') || lower.includes('vibrate') || lower.includes('फोन') || lower.includes('call')) predicted = 'automation';
            else if (lower.includes('search') || lower.includes('google') || lower.includes('खोजो')) predicted = 'research';
            else if (lower.includes('code') || lower.includes('github') || lower.includes('python')) predicted = 'coding';

            if (predicted !== 'core') triggerAgentBlink(predicted, true);

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ text, is_voice: isVoiceMode, model: currentModel })
                });
                const d = await res.json();
                const reply = d.response || "Task completed.";
                const activeTag = d.tag || predicted || 'automation';

                triggerAgentBlink(activeTag, true);
                addChatBubble('assistant', reply, activeTag);

                speakAloud(reply, () => {
                    setSubtitle("Agent idle • Ready for next command");
                    setTimeout(() => triggerAgentBlink(activeTag, false), 1500);
                });

                loadNotesList();
                loadChatsList();
            } catch(e) {
                addChatBubble('assistant', 'Error: ' + e.message, 'core');
                triggerAgentBlink(predicted, false);
            }
        }

        function onDockEnter(e) {
            if (e.key === 'Enter') sendDockMessage();
        }

        function addChatBubble(sender, text, tag = 'core') {
            const feed = document.getElementById('chatFeedStream');
            const div = document.createElement('div');
            div.className = `chat-bubble ${sender}`;
            if (sender === 'assistant') {
                div.innerHTML = `<div class="agent-pill-tag tag-${tag}">RB Agent • ${tag.toUpperCase()}</div><div>${text}</div>`;
            } else {
                div.innerText = text;
            }
            feed.appendChild(div);
            const stage = document.getElementById('appMainStage');
            stage.scrollTop = stage.scrollHeight;
        }

        function setSubtitle(txt) {
            document.getElementById('subtitlesTickerText').innerText = txt;
        }

        // Voice TTS & Speech Recognition
        function speakAloud(text, onDone) {
            if (!('speechSynthesis' in window)) {
                if (onDone) onDone();
                return;
            }
            window.speechSynthesis.cancel();
            const clean = text.replace(/[*#`_\[\]]/g, '');
            const u = new SpeechSynthesisUtterance(clean);
            u.lang = document.getElementById('setVoiceAccent') ? document.getElementById('setVoiceAccent').value : 'hi-IN';
            u.pitch = parseFloat(document.getElementById('setVoicePitch') ? document.getElementById('setVoicePitch').value : 1.0) || 1.0;
            u.rate = parseFloat(document.getElementById('setVoiceRate') ? document.getElementById('setVoiceRate').value : 0.95) || 0.95;
            u.onstart = () => setSubtitle(`Speaking: "${clean.substring(0, 48)}..."`);
            u.onend = () => { if (onDone) onDone(); };
            window.speechSynthesis.speak(u);
        }

        function initSpeechRecognizer() {
            const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (Speech) {
                speechRec = new Speech();
                speechRec.continuous = true;
                speechRec.interimResults = true;
                speechRec.lang = 'hi-IN';

                speechRec.onresult = (e) => {
                    let transcript = '';
                    for (let i = e.resultIndex; i < e.results.length; i++) {
                        transcript += e.results[i][0].transcript;
                    }
                    setSubtitle(`Listening: "${transcript}"`);
                    const lower = transcript.toLowerCase();
                    if (lower.includes("hey rb") || lower.includes("हे आरबी")) {
                        const stripped = transcript.replace(/hey rb|हे आरबी/gi, '').trim();
                        document.getElementById('dockChatInput').value = stripped;
                        if (stripped.length > 2) sendDockMessage();
                    }
                };
            }
        }

        function toggleVoiceMode() {
            isVoiceMode = !isVoiceMode;
            const micBtn = document.getElementById('dockMicBtn');
            if (isVoiceMode) {
                micBtn.classList.add('recording');
                if (speechRec) try { speechRec.start(); } catch(e){}
                setSubtitle("Listening for voice input or 'Hey RB'...");
            } else {
                micBtn.classList.remove('recording');
                if (speechRec) try { speechRec.stop(); } catch(e){}
                setSubtitle("Voice mode paused.");
            }
        }

        // Model Selector Cycle
        function cycleGeminiModel() {
            if (currentModel === "gemini-3-flash-preview") {
                currentModel = "gemini-3.5-flash-lite";
                document.getElementById('dockModelText').innerText = "Gemini 3.5 Lite";
            } else {
                currentModel = "gemini-3-flash-preview";
                document.getElementById('dockModelText').innerText = "Gemini 3 Flash";
            }
            setSubtitle(`Active Model: ${currentModel}`);
        }

        // Call Announcement Trigger
        function triggerCallAnnouncementTest() {
            triggerAgentBlink('automation', true);
            fetch('/api/call_announcement', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ caller_name: "Ram Pandit", phone: "+91-9876543210" })
            }).then(r => r.json()).then(d => {
                setSubtitle(d.announced || "Call announcement triggered.");
                addChatBubble('assistant', `📞 ${d.announced}`, 'automation');
                setTimeout(() => triggerAgentBlink('automation', false), 2000);
            });
        }

        function triggerCameraCapture() {
            fetch('/api/action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action: 'shell', args: { command: 'termux-camera-photo ~/rb_ai/latest.jpg' } })
            });
            setSubtitle("Camera snapshot requested via Termux API.");
        }

        // Sub-Agents Expanded Modal
        function openAgentsExpandedModal(preselectTag) {
            document.getElementById('agentsExpandedModal').classList.add('active');
            if (preselectTag) triggerAgentBlink(preselectTag, true);
        }
        function closeAgentsExpandedModal() {
            document.getElementById('agentsExpandedModal').classList.remove('active');
        }

        async function executeWsResearch() {
            const q = document.getElementById('wsResearchInput').value;
            const out = document.getElementById('wsResearchOutput');
            out.style.display = 'block'; out.innerText = 'Searching web...';
            triggerAgentBlink('research', true);
            const res = await fetch('/api/agents', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ agent: 'research', action: 'run', params: { query: q } })
            });
            const d = await res.json();
            out.innerText = JSON.stringify(d.result, null, 2);
            triggerAgentBlink('research', false);
        }

        async function executeWsMemory() {
            const t = document.getElementById('wsMemoryInput').value;
            const out = document.getElementById('wsMemoryOutput');
            out.style.display = 'block'; out.innerText = 'Storing note...';
            triggerAgentBlink('memory', true);
            const res = await fetch('/api/agents', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ agent: 'memory', action: 'run', params: { text: t } })
            });
            const d = await res.json();
            out.innerText = d.result.message || JSON.stringify(d.result);
            triggerAgentBlink('memory', false);
            loadNotesList();
        }

        async function executeWsPreview() {
            const target = document.getElementById('wsPreviewInput').value;
            const out = document.getElementById('wsPreviewOutput');
            out.style.display = 'block'; out.innerText = 'Loading preview...';
            triggerAgentBlink('preview', true);
            const res = await fetch('/api/agents', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ agent: 'preview', action: 'run', params: { target } })
            });
            const d = await res.json();
            out.innerText = JSON.stringify(d.result, null, 2);
            triggerAgentBlink('preview', false);
        }

        async function triggerHardwareAction(action) {
            triggerAgentBlink('automation', true);
            const res = await fetch('/api/action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action: action === 'torch' ? 'torch' : action, args: { enabled: true, duration: 300 } })
            });
            const d = await res.json();
            const out = document.getElementById('wsAutomationOutput');
            out.style.display = 'block';
            out.innerText = JSON.stringify(d.result, null, 2);
            setTimeout(() => triggerAgentBlink('automation', false), 1500);
        }

        async function executeWsGithub() {
            const u = document.getElementById('wsCodingInput').value;
            const out = document.getElementById('wsCodingOutput');
            out.style.display = 'block'; out.innerText = 'Fetching repos...';
            triggerAgentBlink('coding', true);
            const res = await fetch(`/api/github?username=${encodeURIComponent(u)}`);
            const d = await res.json();
            out.innerText = JSON.stringify(d.repositories || d.error, null, 2);
            triggerAgentBlink('coding', false);
        }

        // Subviews Management
        function openSubview(viewId) {
            toggleDrawer(false);
            const m = document.getElementById(`modal-${viewId}`);
            if (m) m.classList.add('active');
        }
        function closeSubview(viewId) {
            const m = document.getElementById(`modal-${viewId}`);
            if (m) m.classList.remove('active');
        }

        function toggleDrawer(open) {
            document.getElementById('mainSidebarDrawer').classList.toggle('active', open);
            document.getElementById('drawerBackdrop').classList.toggle('active', open);
        }

        function navigateDrawer(id) {
            toggleDrawer(false);
            if (id === 'home') {
                document.querySelectorAll('.subview-modal').forEach(m => m.classList.remove('active'));
            }
        }

        function switchSettingTab(tab) {
            document.querySelectorAll('.stab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.stab-pane').forEach(p => p.classList.remove('active'));
            if (event && event.target) event.target.classList.add('active');
            const target = document.getElementById(`spane-${tab}`);
            if (target) target.classList.add('active');
        }

        // Live Credential Handshakes
        async function handshakeTelegram() {
            const token = document.getElementById('setTgToken').value.trim();
            const fb = document.getElementById('tgStatusFeedback');
            fb.innerText = 'Testing handshake...';
            const res = await fetch('/api/test_credentials', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ service: 'telegram', credentials: { token } })
            });
            const d = await res.json();
            fb.innerHTML = d.success ? `<span class="status-chip-tag chip-success">${d.message}</span>` : `<span class="status-chip-tag chip-danger">${d.error}</span>`;
        }

        async function controlTelegram(action) {
            const token = document.getElementById('setTgToken').value.trim();
            const res = await fetch('/api/telegram', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action, token })
            });
            const d = await res.json();
            document.getElementById('tgStatusFeedback').innerText = d.message || d.error || "Updated";
        }

        async function launchWaBridge() {
            const phone = document.getElementById('setWaPhone').value.trim();
            const msg = document.getElementById('setWaMsg').value.trim();
            if (!phone) return alert("Enter phone number");
            const res = await fetch('/api/whatsapp', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ phone, message: msg })
            });
            const d = await res.json();
            if (d.url) window.open(d.url, '_blank');
        }

        async function handshakeGitHub() {
            const username = document.getElementById('setGhUser').value.trim();
            const token = document.getElementById('setGhToken').value.trim();
            const fb = document.getElementById('ghStatusFeedback');
            fb.innerText = 'Testing handshake...';
            const res = await fetch('/api/test_credentials', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ service: 'github', credentials: { username, token } })
            });
            const d = await res.json();
            fb.innerHTML = d.success ? `<span class="status-chip-tag chip-success">${d.message}</span>` : `<span class="status-chip-tag chip-danger">${d.error}</span>`;
        }

        async function handshakeSupabase() {
            const url = document.getElementById('setSbUrl').value.trim();
            const key = document.getElementById('setSbKey').value.trim();
            const fb = document.getElementById('sbStatusFeedback');
            fb.innerText = 'Testing Supabase handshake...';
            const res = await fetch('/api/test_credentials', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ service: 'supabase', credentials: { url, key } })
            });
            const d = await res.json();
            fb.innerHTML = d.success ? `<span class="status-chip-tag chip-success">${d.message}</span>` : `<span class="status-chip-tag chip-danger">${d.error}</span>`;
        }

        async function syncSupabaseCloud() {
            const fb = document.getElementById('sbStatusFeedback');
            fb.innerText = 'Syncing SQLite to Supabase...';
            const res = await fetch('/api/supabase/sync', { method: 'POST' });
            const d = await res.json();
            fb.innerHTML = d.success ? `<span class="status-chip-tag chip-success">${d.message}</span>` : `<span class="status-chip-tag chip-danger">${d.error}</span>`;
        }

        async function handshakeGemini() {
            const key = document.getElementById('setGeminiKey').value.trim();
            const fb = document.getElementById('geminiStatusFeedback');
            fb.innerText = 'Testing Gemini API key...';
            const res = await fetch('/api/test_credentials', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ service: 'gemini', credentials: { api_key: key } })
            });
            const d = await res.json();
            fb.innerHTML = d.success ? `<span class="status-chip-tag chip-success">${d.message}</span>` : `<span class="status-chip-tag chip-danger">${d.error}</span>`;
        }

        async function saveAllSettingsLive() {
            const accent = document.getElementById('setVoiceAccent').value;
            const pitch = document.getElementById('setVoicePitch').value;
            const rate = document.getElementById('setVoiceRate').value;
            const wake = document.getElementById('setWakeWord').checked;
            const call = document.getElementById('setCallAnnounce').checked;
            const gKey = document.getElementById('setGeminiKey').value.trim();

            await fetch('/api/settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    voice_accent: accent,
                    voice_pitch: pitch,
                    voice_rate: rate,
                    wake_phrase_enabled: wake ? 'true' : 'false',
                    call_announcement_enabled: call ? 'true' : 'false'
                })
            });

            if (gKey) {
                await fetch('/api/config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ gemini_api_key: gKey })
                });
            }

            alert("Configurations saved to SQLite & Supabase!");
            closeSubview('settings');
        }

        // Skills Management
        async function loadSkillsList() {
            const container = document.getElementById('activeSkillsList');
            try {
                const res = await fetch('/api/skills');
                const d = await res.json();
                if (d.skills && d.skills.length > 0) {
                    container.innerHTML = d.skills.map(s => `
                        <div style="background:#0F1A34; border:1px solid var(--border); border-radius:8px; padding:10px; display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <div style="font-weight:800; color:var(--accent-green); font-size:0.84rem;">${s.name}</div>
                                <div style="color:var(--text-muted); font-size:0.75rem; margin-top:2px;">${s.description || 'Specialized Directive'}</div>
                                <div style="font-size:0.68rem; color:#94A3B8; margin-top:4px; font-family:monospace; background:rgba(255,255,255,0.04); padding:3px 6px; border-radius:4px;">${s.system_prompt.substring(0, 80)}...</div>
                            </div>
                            <button onclick="deleteSkillItem(${s.id})" style="background:none; border:none; color:#EF4444; cursor:pointer; padding:4px;"><i class="fa-solid fa-trash"></i></button>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<div style="color:var(--text-muted); font-size:0.78rem;">No custom skills yet. Use the form above to train RB Agent!</div>';
                }
            } catch(e) {
                container.innerHTML = 'Failed to load skills.';
            }
        }

        async function saveSkillTraining() {
            const name = document.getElementById('skillNameInput').value.trim();
            const desc = document.getElementById('skillDescInput').value.trim();
            const prompt = document.getElementById('skillPromptInput').value.trim();
            const fb = document.getElementById('skillFeedbackMsg');

            if (!name || !prompt) {
                fb.innerHTML = '<span class="status-chip-tag chip-danger">Name and Directives required.</span>';
                return;
            }

            const res = await fetch('/api/skills', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name, description: desc, system_prompt: prompt })
            });
            const d = await res.json();
            if (d.success) {
                fb.innerHTML = `<span class="status-chip-tag chip-success">${d.message}</span>`;
                document.getElementById('skillNameInput').value = '';
                document.getElementById('skillDescInput').value = '';
                document.getElementById('skillPromptInput').value = '';
                loadSkillsList();
            } else {
                fb.innerHTML = `<span class="status-chip-tag chip-danger">${d.error || 'Failed'}</span>`;
            }
        }

        async function deleteSkillItem(id) {
            await fetch(`/api/skills/${id}`, { method: 'DELETE' });
            loadSkillsList();
        }

        // Notes Management
        async function loadNotesList() {
            const c = document.getElementById('notesContainerList');
            try {
                const res = await fetch('/api/notes');
                const d = await res.json();
                if (d.notes && d.notes.length > 0) {
                    c.innerHTML = d.notes.map(n => `
                        <div style="background:#0F1A34; border:1px solid var(--border); border-radius:8px; padding:10px; display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <div style="font-weight:700; color:#FFF; font-size:0.84rem;">${n.title}</div>
                                <div style="color:var(--text-muted); font-size:0.76rem; margin-top:2px;">${n.content}</div>
                                <div style="font-size:0.65rem; color:#64748B; margin-top:4px;">${n.created_at}</div>
                            </div>
                            <button onclick="deleteNoteItem(${n.id})" style="background:none; border:none; color:#EF4444; cursor:pointer; padding:4px;"><i class="fa-solid fa-trash"></i></button>
                        </div>
                    `).join('');
                } else {
                    c.innerHTML = '<div style="color:var(--text-muted); font-size:0.78rem;">No notes stored. Say "यह चीज़ सेव कर लो" to create one!</div>';
                }
            } catch(e) {
                c.innerHTML = 'Unable to load notes.';
            }
        }

        async function deleteNoteItem(id) {
            await fetch(`/api/notes/${id}`, { method: 'DELETE' });
            loadNotesList();
        }

        // Web Preview & Code Runner
        async function runWebPreviewSearch() {
            const q = document.getElementById('webPreviewQuery').value;
            const box = document.getElementById('webPreviewOutputBox');
            box.innerText = "Searching web...";
            const res = await fetch('/api/agents', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ agent: 'research', action: 'run', params: { query: q } })
            });
            const d = await res.json();
            const items = d.result.results || [];
            if (items.length > 0) {
                box.innerHTML = items.map(it => `
                    <div style="background:#0F1A34; border:1px solid var(--border); border-radius:8px; padding:8px; margin-bottom:6px;">
                        <div style="font-weight:700; color:var(--accent-cyan); font-size:0.84rem;">${it.title}</div>
                        <div style="font-size:0.76rem; color:#CBD5E1; margin:3px 0;">${it.snippet}</div>
                        <a href="${it.url}" target="_blank" style="font-size:0.7rem; color:var(--accent-blue); word-break:break-all;">${it.url}</a>
                    </div>
                `).join('');
            } else {
                box.innerText = "No search results returned.";
            }
        }

        async function runCodeLive() {
            const code = document.getElementById('codeRunnerArea').value;
            const c = document.getElementById('codeOutputConsole');
            c.innerText = "Running Python script...";
            const res = await fetch('/api/action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action: 'shell', args: { command: `python3 -c ${JSON.stringify(code)}` } })
            });
            const d = await res.json();
            c.innerText = d.result.stdout || d.result.stderr || "Executed (No output)";
        }

        // Chats History
        async function loadChatsList() {
            const c = document.getElementById('chatsModalList');
            try {
                const res = await fetch('/api/chats');
                const d = await res.json();
                if (d.chats && d.chats.length > 0) {
                    c.innerHTML = d.chats.map(ch => `
                        <div style="background:#0F1A34; border:1px solid var(--border); border-radius:8px; padding:8px 10px; font-size:0.78rem;">
                            <span style="color:${ch.sender === 'user' ? 'var(--accent-cyan)' : 'var(--accent-green)'}; font-weight:700;">${ch.sender.toUpperCase()}:</span>
                            <span style="color:#FFF; margin-left:6px;">${ch.message.substring(0, 65)}...</span>
                        </div>
                    `).join('');
                } else {
                    c.innerHTML = '<div style="color:var(--text-muted); font-size:0.78rem;">No previous chats.</div>';
                }
            } catch(e) {
                c.innerHTML = 'Unable to load chats.';
            }
        }

        async function clearAllChatsLive() {
            if (!confirm("Clear all persistent chat messages?")) return;
            await fetch('/api/chats', { method: 'DELETE' });
            loadChatsList();
        }

        function filterDrawerChats() {
            const q = document.getElementById('drawerSearchInput').value.toLowerCase();
            document.querySelectorAll('#chatsModalList > div').forEach(el => {
                el.style.display = el.innerText.toLowerCase().includes(q) ? 'block' : 'none';
            });
        }

        function startNewChatSession() {
            toggleDrawer(false);
            document.getElementById('chatFeedStream').innerHTML = `
                <div class="chat-bubble assistant">
                    <div class="agent-pill-tag tag-core">RB System</div>
                    <div>नमस्ते Ram Binay Pandit! New chat session started. What shall we achieve today?</div>
                </div>
            `;
            navigateDrawer('home');
        }
    </script>
</body>
</html>
"""
