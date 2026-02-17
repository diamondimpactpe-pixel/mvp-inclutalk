import React, { useState, useRef, useMemo, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

type Turn = 'operator' | 'user-choice' | 'user-signs' | 'user-text' | 'playback';
type SpeechRecWin = typeof window & { webkitSpeechRecognition?: any; SpeechRecognition?: any };

const LSP_WORDS = [
  'DNI','CITA','PAGO','RECLAMO','CONSULTA','NOMBRE','FECHA',
  'VENCIDO','RENOVAR','ESPERAR','FIRMAR','DOCUMENTO','TARJETA',
  'BANCO','CUENTA','DEPÓSITO','RETIRO','TRÁMITE','CERTIFICADO',
  'TURNO','NÚMERO','HORA','HOY','DINERO','REGISTRO',
  'AYUDA','GRACIAS','SÍ','NO','EMERGENCIA',
];

function speakText(text: string, onEnd?: () => void) {
  if (!('speechSynthesis' in window)) { onEnd?.(); return; }
  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.lang = 'es-PE'; utt.rate = 0.88;
  if (onEnd) utt.onend = onEnd;
  window.speechSynthesis.speak(utt);
}

export const AttentionView: React.FC = () => {
  const navigate = useNavigate();
  const [turn, setTurn] = useState<Turn>('operator');

  // Operador
  const [isRecording, setIsRecording] = useState(false);
  const [operatorText, setOperatorText] = useState('');
  const [sttError, setSttError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  // Señas
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const handsRef = useRef<any>(null);
  const animFrameRef = useRef<number>(0);
  const [handDetected, setHandDetected] = useState(false);
  const handDetectedRef = useRef(false);
  const [signsPhase, setSignsPhase] = useState<'idle'|'detected'|'recording'|'classifying'|'done'>('idle');
  const signsPhaseRef = useRef<string>('idle');
  const [countdown, setCountdown] = useState(3);
  const [builtPhrase, setBuiltPhrase] = useState<string[]>([]);
  const [lastWord, setLastWord] = useState('');
  const [lastConfidence, setLastConfidence] = useState<number>(0);
  const lastKeypointsRef = useRef<any[]>([]); // keypoints reales del último frame
  const recordingTimerRef = useRef<ReturnType<typeof setTimeout>|null>(null);
  const countdownRef = useRef<ReturnType<typeof setInterval>|null>(null);

  // Texto
  const [userText, setUserText] = useState('');

  // Playback
  const [playbackText, setPlaybackText] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);

  // ── STT ────────────────────────────────────────────────────────────────────
  const SpeechRecCtor = useMemo(() => {
    const w = window as unknown as SpeechRecWin;
    return w.SpeechRecognition || w.webkitSpeechRecognition;
  }, []);

  const initRecognition = useCallback(() => {
    if (!SpeechRecCtor) return null;
    const rec = new SpeechRecCtor();
    rec.lang = 'es-PE'; rec.continuous = true; rec.interimResults = true;
    rec.onresult = (e: any) => {
      let txt = '';
      for (let i = 0; i < e.results.length; i++) txt += e.results[i][0].transcript;
      setOperatorText(txt.trim());
    };
    rec.onerror = (e: any) => {
      setSttError(e?.error === 'not-allowed' ? 'Permiso de micrófono denegado.' : 'Error de voz. Intenta de nuevo.');
      setIsRecording(false);
    };
    rec.onend = () => setIsRecording(false);
    return rec;
  }, [SpeechRecCtor]);

  const toggleMic = () => {
    setSttError(null);
    if (!SpeechRecCtor) { setSttError('Usa Chrome o Edge para voz.'); return; }
    if (!isRecording) {
      const rec = initRecognition(); if (!rec) return;
      recognitionRef.current = rec; rec.start(); setIsRecording(true);
    } else { recognitionRef.current?.stop(); setIsRecording(false); }
  };

  // ── MediaPipe ──────────────────────────────────────────────────────────────
  const loadMP = useCallback((): Promise<any> => {
    if ((window as any).Hands) return Promise.resolve((window as any).Hands);
    return new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js';
      s.crossOrigin = 'anonymous';
      s.onload = () => resolve((window as any).Hands);
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }, []);

  const drawLandmarks = useCallback((results: any) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;
    const ctx = canvas.getContext('2d'); if (!ctx) return;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!results.multiHandLandmarks?.length) return;
    const conns = [[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],
      [0,9],[9,10],[10,11],[11,12],[0,13],[13,14],[14,15],[15,16],
      [0,17],[17,18],[18,19],[19,20],[5,9],[9,13],[13,17]];
    for (const lms of results.multiHandLandmarks) {
      ctx.strokeStyle = '#4ade80'; ctx.lineWidth = 2.5;
      for (const [a, b] of conns) {
        ctx.beginPath();
        ctx.moveTo(lms[a].x * canvas.width, lms[a].y * canvas.height);
        ctx.lineTo(lms[b].x * canvas.width, lms[b].y * canvas.height);
        ctx.stroke();
      }
      for (const lm of lms) {
        ctx.beginPath();
        ctx.arc(lm.x * canvas.width, lm.y * canvas.height, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#22d3ee'; ctx.fill();
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5; ctx.stroke();
      }
    }
  }, []);

  const startDetectionCountdown = useCallback(() => {
    signsPhaseRef.current = 'detected';
    setSignsPhase('detected');
    setCountdown(3);
    let c = 3;
    countdownRef.current = setInterval(() => {
      c--;
      setCountdown(c);
      if (c <= 0) {
        clearInterval(countdownRef.current!);
        if (handDetectedRef.current) {
          signsPhaseRef.current = 'recording';
          setSignsPhase('recording');
          recordingTimerRef.current = setTimeout(() => {
            signsPhaseRef.current = 'classifying';
            setSignsPhase('classifying');
            // Keypoints reales capturados por MediaPipe ✅
            const kp = lastKeypointsRef.current;
            console.log(`📊 Keypoints reales capturados: ${kp.length} mano(s), ${kp[0]?.length ?? 0} landmarks`);
            console.log('🔬 Para integración real, enviar al endpoint /api/v1/lsp/predict');
            // ─── TODO (producción) ───────────────────────────────────────
            // const res = await fetch('/api/v1/lsp/predict', {
            //   method: 'POST',
            //   headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
            //   body: JSON.stringify({ frames: [kp] })
            // });
            // const { label, confidence } = await res.json();
            // ────────────────────────────────────────────────────────────
            setTimeout(() => {
              // DEMO: resultado aleatorio (confianza baja = honesto que no está entrenado)
              const word = LSP_WORDS[Math.floor(Math.random() * LSP_WORDS.length)];
              const demoConf = 40 + Math.floor(Math.random() * 26); // 40–65%
              setLastWord(word);
              setLastConfidence(demoConf);
              setBuiltPhrase(prev => [...prev, word]);
              signsPhaseRef.current = 'done';
              setSignsPhase('done');
            }, 800);
          }, 2000);
        }
      }
    }, 1000);
  }, []);

  const cancelCountdown = useCallback(() => {
    if (countdownRef.current) clearInterval(countdownRef.current);
    if (recordingTimerRef.current) clearTimeout(recordingTimerRef.current);
    signsPhaseRef.current = 'idle';
    setSignsPhase('idle');
    setCountdown(3);
  }, []);

  const initMP = useCallback(async () => {
    try {
      const HandsCtor = await loadMP();
      const hands = new HandsCtor({
        locateFile: (f: string) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${f}`,
      });
      hands.setOptions({ maxNumHands: 2, modelComplexity: 1, minDetectionConfidence: 0.7, minTrackingConfidence: 0.5 });
      hands.onResults((results: any) => {
        drawLandmarks(results);
        // Guardar keypoints reales para cuando el modelo esté listo
        if (results.multiHandLandmarks?.length) {
          lastKeypointsRef.current = results.multiHandLandmarks;
        }
        const det = results.multiHandLandmarks?.length > 0;
        if (det !== handDetectedRef.current) {
          handDetectedRef.current = det;
          setHandDetected(det);
          if (det && signsPhaseRef.current === 'idle') startDetectionCountdown();
          if (!det && ['detected','recording'].includes(signsPhaseRef.current)) cancelCountdown();
        }
      });
      handsRef.current = hands;
      const loop = async () => {
        if ((videoRef.current?.readyState ?? 0) >= 2 && handsRef.current) {
          await handsRef.current.send({ image: videoRef.current });
        }
        animFrameRef.current = requestAnimationFrame(loop);
      };
      animFrameRef.current = requestAnimationFrame(loop);
    } catch (e) {
      console.error('MediaPipe error:', e);
    }
  }, [loadMP, drawLandmarks, startDetectionCountdown, cancelCountdown]);

  const stopCamera = useCallback(() => {
    cancelAnimationFrame(animFrameRef.current);
    handsRef.current?.close?.();
    handsRef.current = null;
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
    cancelCountdown();
    handDetectedRef.current = false;
    setHandDetected(false);
  }, [cancelCountdown]);

  const openCamera = useCallback(async () => {
    setTurn('user-signs');
    setSignsPhase('idle'); signsPhaseRef.current = 'idle';
    setBuiltPhrase([]); setHandDetected(false); handDetectedRef.current = false; setCountdown(3);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => { videoRef.current!.play(); initMP(); };
      }
    } catch { setSttError('No se pudo acceder a la cámara.'); setTurn('user-choice'); }
  }, [initMP]);

  const confirmSigns = () => {
    stopCamera();
    const text = builtPhrase.join(' ');
    setPlaybackText(text); setTurn('playback'); setIsSpeaking(true);
    speakText(text, () => setIsSpeaking(false));
  };

  const confirmUserText = () => {
    const text = userText.trim(); if (!text) return;
    setPlaybackText(text); setTurn('playback'); setIsSpeaking(true);
    speakText(text, () => setIsSpeaking(false));
  };

  const handleContinue = () => {
    setOperatorText(''); setUserText(''); setPlaybackText('');
    setBuiltPhrase([]); setLastWord(''); setIsSpeaking(false);
    signsPhaseRef.current = 'idle'; setSignsPhase('idle');
    setTurn('operator');
  };

  useEffect(() => () => { recognitionRef.current?.stop(); stopCamera(); window.speechSynthesis?.cancel(); }, [stopCamera]);

  // ── RENDER ──────────────────────────────────────────────────────────────────
  const sp = (bg: string, color: string): React.CSSProperties => ({
    background: bg, color, border: `1px solid ${color}55`,
    borderRadius: 10, padding: '8px 16px', fontSize: 14, fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: 6,
  });

  return (
    <div style={S.root}>
      <style>{CSS}</style>
      <header style={S.header}>
        <b style={S.logo}><span style={{color:'#1e4d7b'}}>Inclu</span><span style={{color:'#2cb87a'}}>Talk</span></b>
        <span style={S.pill}>● Sesión activa</span>
        <button style={S.endBtn} onClick={() => navigate('/dashboard')}>Finalizar sesión</button>
      </header>

      <main style={S.main}>

        {/* OPERADOR */}
        {turn === 'operator' && (
          <div style={S.card} className="it-in">
            <div style={S.stepRow}>
              <span style={{...S.stepN, background:'#2cb87a'}}>1</span>
              <span style={S.stepL}>Turno del Operador</span>
            </div>
            <div style={{...S.icoCircle, background:'#e8f5ee'}}><span style={{fontSize:44}}>🎤</span></div>
            <p style={S.hint}>{isRecording ? 'Grabando… presiona para detener' : 'Presiona el botón para empezar a hablar'}</p>
            <div style={{...S.display, borderColor: isRecording ? '#2cb87a' : '#e5e7eb'}}>
              {operatorText
                ? <p style={S.bigTxt}>{operatorText}</p>
                : <p style={S.ph}>El texto aparecerá aquí mientras hablas…</p>}
            </div>
            {sttError && <p style={S.errTxt}>{sttError}</p>}
            <button style={{...S.micBtn, ...(isRecording ? S.micOn : {})}} onClick={toggleMic}>
              {isRecording ? <><span className="it-blink">⏹</span> Detener grabación</> : '🎙 Iniciar grabación'}
            </button>
            <div style={S.row}>
              <button style={{...S.ghost, opacity: operatorText?1:.3}} disabled={!operatorText} onClick={() => {recognitionRef.current?.stop(); setIsRecording(false); setOperatorText(''); setSttError(null);}}>🗑 Borrar</button>
              <button style={{...S.primary, opacity: operatorText?1:.3}} disabled={!operatorText} onClick={() => {recognitionRef.current?.stop(); setIsRecording(false); setTurn('user-choice');}}>Confirmar y enviar →</button>
            </div>
          </div>
        )}

        {/* USUARIO - ELECCIÓN */}
        {turn === 'user-choice' && (
          <div style={S.card} className="it-in">
            <div style={S.stepRow}>
              <span style={{...S.stepN, background:'#1a7fb5'}}>2</span>
              <span style={S.stepL}>Turno del Usuario</span>
            </div>
            {operatorText && (
              <div style={S.opBubble}>
                <p style={{fontSize:12,color:'#0284c7',margin:'0 0 6px',fontWeight:700,textTransform:'uppercase',letterSpacing:.5}}>El operador dijo:</p>
                <p style={{fontSize:22,fontWeight:600,color:'#1e40af',margin:0,fontStyle:'italic'}}>"{operatorText}"</p>
              </div>
            )}
            <p style={{...S.hint, fontSize:20, fontWeight:700, color:'#1e4d7b'}}>¿Cómo deseas responder?</p>
            <div style={{width:'100%',display:'flex',flexDirection:'column',alignItems:'center',gap:14}}>
              <button style={S.choiceMain} onClick={openCamera}>
                <span style={{fontSize:52}}>🤟</span>
                <span style={{fontSize:22,fontWeight:700,color:'#166534'}}>Responder con Señas</span>
                <span style={{fontSize:14,color:'#6b7280'}}>Activa la cámara — Lenguaje LSP</span>
              </button>
              <button style={S.choiceSec} onClick={() => setTurn('user-text')}>
                ⌨️ &nbsp;Escribir respuesta
              </button>
            </div>
          </div>
        )}

        {/* SEÑAS */}
        {turn === 'user-signs' && (
          <div style={{...S.card, maxWidth:860}} className="it-in">
            <div style={S.stepRow}>
              <span style={{...S.stepN, background:'#1a7fb5'}}>2</span>
              <span style={S.stepL}>Captura de Señas LSP</span>
            </div>

            {/* Banner modelo demo honesto */}
            <div style={S.demoBanner}>
              <span style={{fontSize:18}}>🔬</span>
              <div>
                <p style={{margin:0,fontWeight:700,fontSize:14,color:'#92400e'}}>Modo demo — Detección de manos REAL ✅</p>
                <p style={{margin:0,fontSize:13,color:'#b45309'}}>MediaPipe detecta tus manos correctamente. La <b>clasificación de señas LSP</b> es demo hasta que el modelo LSTM sea entrenado con datos reales.</p>
              </div>
            </div>
            <div style={{display:'flex',gap:20,width:'100%',flexWrap:'wrap',alignItems:'flex-start'}}>
              {/* Cámara */}
              <div style={S.camBox}>
                <video ref={videoRef} autoPlay playsInline muted style={S.video}/>
                <canvas ref={canvasRef} style={S.canvas}/>
                <div style={S.hFrame}/>
                <div style={{position:'absolute',bottom:12,left:12,right:12,textAlign:'center'}}>
                  {signsPhase==='idle' && <span style={sp('#fff8e1','#92400e')}>👋 Coloca tus manos en el recuadro</span>}
                  {signsPhase==='detected' && (
                    <div style={{background:'rgba(0,0,0,.75)',borderRadius:14,padding:14,display:'flex',flexDirection:'column',alignItems:'center',gap:8}}>
                      <span style={sp('#f0fdf4','#166534')}>✅ ¡Manos detectadas!</span>
                      <span style={{fontSize:56,fontWeight:800,color:'#4ade80',lineHeight:1}}>{countdown}</span>
                      <div style={{width:'80%',height:6,background:'rgba(255,255,255,.2)',borderRadius:3,overflow:'hidden'}}>
                        <div style={{height:'100%',background:'linear-gradient(90deg,#4ade80,#22d3ee)',borderRadius:3,transition:'width .9s linear',width:`${((3-countdown)/3)*100}%`}}/>
                      </div>
                      <p style={{color:'#fff',fontSize:13,margin:0,fontWeight:600}}>Mantén la seña {countdown}s…</p>
                    </div>
                  )}
                  {signsPhase==='recording' && <span style={sp('#fef3f3','#991b1b')}><span className="it-blink">⏺</span> Grabando seña…</span>}
                  {signsPhase==='classifying' && <span style={sp('#f0f9ff','#0369a1')}>🧠 Interpretando…</span>}
                </div>
              </div>
              {/* Panel */}
              <div style={{flex:'1 1 180px',display:'flex',flexDirection:'column',gap:14,minWidth:180}}>
                <div style={{background:'#f9fafb',borderRadius:14,padding:16,border:'1px solid #e5e7eb',minHeight:90}}>
                  <p style={{fontSize:12,color:'#9ca3af',margin:'0 0 10px',fontWeight:700,textTransform:'uppercase',letterSpacing:.5}}>Frase detectada:</p>
                  {builtPhrase.length>0
                    ? <div style={{display:'flex',flexWrap:'wrap',gap:8}}>{builtPhrase.map((w,i)=><span key={i} style={{background:'#dcfce7',color:'#166534',border:'1px solid #bbf7d0',borderRadius:8,padding:'5px 12px',fontSize:15,fontWeight:700}}>{w}</span>)}</div>
                    : <p style={{color:'#c0cdd6',fontSize:14,margin:0,fontStyle:'italic'}}>Las palabras aparecerán aquí…</p>
                  }
                </div>
                {signsPhase==='done' && (
                  <div style={{display:'flex',flexDirection:'column',gap:10}}>
                    <div style={{background:'#f0fdf4',borderRadius:10,padding:'10px 14px'}}>
                      <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:8}}>
                        <span style={{fontSize:13,color:'#6b7280'}}>Detectada:</span>
                        <span style={{background:'#2cb87a',color:'#fff',borderRadius:8,padding:'3px 12px',fontSize:15,fontWeight:700}}>{lastWord}</span>
                      </div>
                      {/* Barra de confianza honesta */}
                      <div style={{display:'flex',alignItems:'center',gap:8}}>
                        <span style={{fontSize:12,color:'#9ca3af',whiteSpace:'nowrap'}}>Confianza:</span>
                        <div style={{flex:1,height:6,background:'#e5e7eb',borderRadius:3,overflow:'hidden'}}>
                          <div style={{height:'100%',width:`${lastConfidence}%`,background:lastConfidence>70?'#22c55e':lastConfidence>50?'#f59e0b':'#ef4444',borderRadius:3,transition:'width .5s ease'}}/>
                        </div>
                        <span style={{fontSize:12,fontWeight:700,color:lastConfidence>70?'#166534':lastConfidence>50?'#92400e':'#991b1b'}}>{lastConfidence}%</span>
                      </div>
                      {lastConfidence < 65 && (
                        <p style={{fontSize:11,color:'#b45309',margin:'6px 0 0',fontStyle:'italic'}}>⚠️ Demo: modelo no entrenado. La confianza real mejorará con el dataset LSP.</p>
                      )}
                    </div>
                    <button style={S.ghost} onClick={() => {setBuiltPhrase(p=>p.slice(0,-1)); signsPhaseRef.current='idle'; setSignsPhase('idle'); setCountdown(3);}}>↩ Borrar última</button>
                    <button style={S.ghost} onClick={() => {signsPhaseRef.current='idle'; setSignsPhase('idle'); setCountdown(3);}}>+ Agregar otra seña</button>
                    <button style={{...S.primary,width:'100%',opacity:builtPhrase.length?1:.35}} disabled={!builtPhrase.length} onClick={confirmSigns}>Confirmar frase →</button>
                  </div>
                )}
                {(signsPhase==='idle'||signsPhase==='detected') && (
                  <div style={{background:'#f8fafc',borderRadius:12,padding:14}}>
                    <p style={{fontSize:13,color:'#6b7280',margin:'0 0 8px',fontWeight:700}}>💡 Instrucciones:</p>
                    <ol style={{fontSize:13,color:'#6b7280',margin:0,paddingLeft:18,lineHeight:1.9}}>
                      <li>Coloca tus manos en el recuadro</li>
                      <li>Espera la cuenta regresiva (3s)</li>
                      <li>Mantén la seña 2 segundos</li>
                      <li>Confirma o repite</li>
                    </ol>
                  </div>
                )}
              </div>
            </div>
            <button style={{background:'none',border:'none',color:'#9ca3af',cursor:'pointer',fontSize:14,fontFamily:'inherit',textDecoration:'underline'}} onClick={()=>{stopCamera();setTurn('user-choice');}}>← Volver a opciones</button>
          </div>
        )}

        {/* TEXTO */}
        {turn === 'user-text' && (
          <div style={S.card} className="it-in">
            <div style={S.stepRow}>
              <span style={{...S.stepN, background:'#1a7fb5'}}>2</span>
              <span style={S.stepL}>Escribir Respuesta</span>
            </div>
            <div style={{...S.icoCircle, background:'#e8f0f7'}}><span style={{fontSize:44}}>⌨️</span></div>
            <textarea style={S.ta} value={userText} onChange={e=>setUserText(e.target.value)} placeholder="Escribe aquí tu respuesta…" autoFocus rows={5}/>
            <div style={S.row}>
              <button style={S.ghost} onClick={()=>setTurn('user-choice')}>← Volver</button>
              <button style={{...S.primary,opacity:userText.trim()?1:.35}} disabled={!userText.trim()} onClick={confirmUserText}>Confirmar →</button>
            </div>
          </div>
        )}

        {/* PLAYBACK */}
        {turn === 'playback' && (
          <div style={S.card} className="it-in">
            <div style={S.stepRow}>
              <span style={{...S.stepN, background:'#7c3aed'}}>3</span>
              <span style={S.stepL}>Respuesta del Usuario</span>
            </div>

            {/* Ícono de altavoz — clickeable para repetir */}
            <button
              title="Repetir en voz alta"
              style={{
                ...S.icoCircle,
                background: isSpeaking ? '#ede9fe' : '#f3eeff',
                border: isSpeaking ? '2px solid #a78bfa' : '2px solid transparent',
                cursor: 'pointer',
                transition: 'all .2s',
                position: 'relative',
              }}
              onClick={() => {
                if (!isSpeaking) {
                  setIsSpeaking(true);
                  speakText(playbackText, () => setIsSpeaking(false));
                }
              }}
            >
              <span style={{fontSize:44}}>{isSpeaking ? '🔊' : '🔈'}</span>
               
            </button>

            {/* Texto del usuario */}
            <div style={S.pbBox}>
              <p style={S.pbTxt}>"{playbackText}"</p>
            </div>

            {/* Estado: hablando / botón continuar */}
            {isSpeaking ? (
              <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:12}}>
                <div style={{display:'flex',alignItems:'center',gap:5,height:48}}>
                  {[0,1,2,3,4,3,2,1].map((d,i) => (
                    <div key={i} style={{
                      width:6, height:8, background:'#7c3aed', borderRadius:3,
                      animation:`it-wave .7s ease-in-out ${i*.1}s infinite`,
                      opacity:.3+d*.1,
                    }}/>
                  ))}
                </div>
                <p style={{color:'#7c3aed',fontSize:17,fontWeight:600,margin:0}}>
                  Leyendo en voz alta…
                </p>
              </div>
            ) : (
              <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:12,width:'100%'}}>
                <button style={S.contBtn} onClick={handleContinue}>
                  ↩ Continuar conversación
                </button>
              </div>
            )}
          </div>
        )}
      </main>

      <footer style={S.footer}>
        <div style={{display:'flex',alignItems:'center',gap:10}}>
          {[
            {l:'1. Operador',a:turn==='operator',c:'#2cb87a'},
            {l:'2. Usuario',a:['user-choice','user-signs','user-text'].includes(turn),c:'#1a7fb5'},
            {l:'3. Respuesta',a:turn==='playback',c:'#7c3aed'},
          ].map((t,i)=>(
            <React.Fragment key={i}>
              {i>0&&<div style={{width:48,height:2,borderRadius:1,background:t.a?t.c:'#d1d5db',transition:'background .4s'}}/>}
              <div style={{display:'flex',alignItems:'center',gap:6}}>
                <div style={{width:12,height:12,borderRadius:'50%',background:t.a?t.c:'#d1d5db',transition:'background .4s'}}/>
                <span style={{fontSize:13,fontWeight:600,color:t.a?t.c:'#9ca3af'}}>{t.l}</span>
              </div>
            </React.Fragment>
          ))}
        </div>
      </footer>
    </div>
  );
};

const S: Record<string, React.CSSProperties> = {
  root: { minHeight:'100vh', background:'linear-gradient(150deg,#f0f9f4 0%,#e8f4fb 50%,#f5f0ff 100%)', fontFamily:'"Inter",system-ui,sans-serif', color:'#1a2e3b', display:'flex', flexDirection:'column' },
  header: { display:'flex', alignItems:'center', justifyContent:'space-between', padding:'14px 36px', background:'#fff', boxShadow:'0 1px 12px rgba(0,0,0,.08)', position:'sticky', top:0, zIndex:100 },
  logo: { fontWeight:800, fontSize:26, letterSpacing:-0.5 },
  pill: { background:'#f0fdf4', border:'1px solid #bbf7d0', borderRadius:20, padding:'5px 16px', fontSize:13, fontWeight:600, color:'#166534' },
  endBtn: { background:'#fff0f0', border:'1px solid #fecaca', borderRadius:10, padding:'8px 20px', color:'#dc2626', cursor:'pointer', fontSize:14, fontWeight:600, fontFamily:'inherit' },
  main: { flex:1, display:'flex', alignItems:'center', justifyContent:'center', padding:'32px 20px' },
  card: { width:'100%', maxWidth:700, background:'#fff', borderRadius:24, padding:'40px 48px', display:'flex', flexDirection:'column', alignItems:'center', gap:22, boxShadow:'0 8px 40px rgba(0,0,0,.1)', border:'1px solid rgba(0,0,0,.06)' },
  stepRow: { display:'flex', alignItems:'center', gap:10, alignSelf:'flex-start' },
  stepN: { borderRadius:'50%', width:28, height:28, display:'inline-flex', alignItems:'center', justifyContent:'center', fontSize:13, fontWeight:800, color:'#fff' },
  stepL: { fontSize:16, fontWeight:700, color:'#374151' },
  icoCircle: { width:88, height:88, borderRadius:'50%', display:'flex', alignItems:'center', justifyContent:'center' },
  hint: { fontSize:17, color:'#6b7280', textAlign:'center', margin:0 },
  display: { width:'100%', minHeight:200, background:'#f9fafb', border:'2px solid #e5e7eb', borderRadius:16, padding:'24px 32px', display:'flex', alignItems:'center', justifyContent:'center', transition:'border-color .3s' },
  bigTxt: { fontSize:38, fontWeight:700, color:'#111827', textAlign:'center', margin:0, lineHeight:1.45 },
  ph: { fontSize:18, color:'#c0cdd6', textAlign:'center', margin:0, fontStyle:'italic' },
  errTxt: { color:'#dc2626', fontSize:14, textAlign:'center', margin:0 },
  micBtn: { width:'100%', padding:'18px', borderRadius:14, border:'2px solid #2cb87a', background:'#f0fdf4', color:'#166534', fontSize:20, fontWeight:700, cursor:'pointer', fontFamily:'inherit', transition:'all .2s' },
  micOn: { background:'#fff0f0', borderColor:'#dc2626', color:'#dc2626' },
  row: { display:'flex', gap:12, width:'100%', justifyContent:'center', flexWrap:'wrap' },
  ghost: { padding:'12px 24px', borderRadius:12, border:'1.5px solid #d1d5db', background:'#fff', color:'#374151', fontSize:15, fontWeight:600, cursor:'pointer', fontFamily:'inherit' },
  primary: { padding:'13px 32px', borderRadius:12, border:'none', background:'linear-gradient(135deg,#1e7a52,#2cb87a)', color:'#fff', fontSize:17, fontWeight:700, cursor:'pointer', fontFamily:'inherit', boxShadow:'0 4px 14px rgba(44,184,122,.35)' },
  opBubble: { width:'100%', background:'#f0f9ff', border:'1px solid #bae6fd', borderRadius:14, padding:'14px 22px', textAlign:'center' },
  choiceMain: { width:'100%', maxWidth:460, padding:'28px 24px', borderRadius:18, border:'2px solid #a7f3d0', background:'linear-gradient(135deg,#f0fdf4,#e6f7f1)', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:10, fontFamily:'inherit' },
  choiceSec: { background:'none', border:'1.5px solid #bae6fd', borderRadius:14, color:'#1a7fb5', cursor:'pointer', fontSize:16, fontFamily:'inherit', fontWeight:600, padding:'14px 40px' },
  camBox: { flex:'1 1 320px', aspectRatio:'4/3', position:'relative', borderRadius:16, overflow:'hidden', background:'#1a1a2e', border:'2px solid #d1d5db', minWidth:260 },
  video: { width:'100%', height:'100%', objectFit:'cover', transform:'scaleX(-1)', display:'block' },
  canvas: { position:'absolute', top:0, left:0, width:'100%', height:'100%', transform:'scaleX(-1)', pointerEvents:'none' },
  hFrame: { position:'absolute', top:'15%', left:'15%', width:'70%', height:'70%', border:'2.5px dashed rgba(255,255,255,.45)', borderRadius:14, pointerEvents:'none' },
  ta: { width:'100%', minHeight:140, background:'#f9fafb', border:'1.5px solid #d1d5db', borderRadius:14, padding:'16px 20px', color:'#111827', fontSize:22, fontFamily:'inherit', resize:'vertical', outline:'none', lineHeight:1.5, boxSizing:'border-box' },
  pbBox: { width:'100%', minHeight:180, background:'#f5f3ff', border:'2px solid #ddd6fe', borderRadius:16, padding:'28px 32px', display:'flex', alignItems:'center', justifyContent:'center' },
  pbTxt: { fontSize:34, fontWeight:700, color:'#4c1d95', textAlign:'center', margin:0, lineHeight:1.4 },
  contBtn: { padding:'16px 44px', borderRadius:14, border:'none', background:'linear-gradient(135deg,#5b21b6,#7c3aed)', color:'#fff', fontSize:19, fontWeight:700, cursor:'pointer', fontFamily:'inherit', boxShadow:'0 4px 16px rgba(124,58,237,.4)' },
  demoBanner: { width:'100%', background:'#fffbeb', border:'1.5px solid #fcd34d', borderRadius:12, padding:'12px 18px', display:'flex', gap:12, alignItems:'flex-start' },
  footer: { padding:'14px 36px', background:'#fff', borderTop:'1px solid #f3f4f6', display:'flex', justifyContent:'center' },
};

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  @keyframes it-in { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:none} }
  .it-in { animation: it-in .35s ease both; }
  @keyframes it-blink { 0%,100%{opacity:1} 50%{opacity:.2} }
  .it-blink { animation: it-blink .7s ease infinite; }
  @keyframes it-wave { 0%,100%{height:8px} 50%{height:38px} }
  button:hover { filter: brightness(.95); }
`;