import React, { useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';

type SpeechRecognitionType = typeof window & {
  webkitSpeechRecognition?: any;
  SpeechRecognition?: any;
};

export const AttentionView: React.FC = () => {
  const navigate = useNavigate();
  const [sessionStarted, setSessionStarted] = useState(false);

  // STT state
  const [isListening, setIsListening] = useState(false);
  const [operatorText, setOperatorText] = useState('');
  const [sttError, setSttError] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);

  const SpeechRecognitionCtor = useMemo(() => {
    const w = window as unknown as SpeechRecognitionType;
    return w.SpeechRecognition || w.webkitSpeechRecognition;
  }, []);

  const initRecognition = () => {
    if (!SpeechRecognitionCtor) return null;

    const rec = new SpeechRecognitionCtor();
    rec.lang = 'es-PE';
    rec.continuous = false;      // una “ráfaga” por pulsación
    rec.interimResults = true;   // texto parcial mientras habla

    rec.onresult = (event: any) => {
      let finalText = '';
      let interimText = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const chunk = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += chunk;
        else interimText += chunk;
      }

      setOperatorText((finalText || interimText).trim());
    };

    rec.onerror = (e: any) => {
      setSttError(e?.error || 'STT error');
      setIsListening(false);
    };

    rec.onend = () => {
      setIsListening(false);
    };

    return rec;
  };

  const startListening = () => {
    setSttError(null);

    if (!SpeechRecognitionCtor) {
      setSttError('Tu navegador no soporta SpeechRecognition. Usa Chrome.');
      return;
    }

    // crea instancia si no existe
    if (!recognitionRef.current) recognitionRef.current = initRecognition();
    if (!recognitionRef.current) {
      setSttError('No se pudo inicializar reconocimiento de voz.');
      return;
    }

    try {
      setIsListening(true);
      recognitionRef.current.start();
    } catch (err) {
      // si haces start doble por algún evento duplicado
      setIsListening(false);
    }
  };

  const stopListening = () => {
    try {
      recognitionRef.current?.stop();
    } catch {}
  };

  const handleBack = () => navigate('/dashboard');
  const handleStartSession = () => setSessionStarted(true);

  if (!sessionStarted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-12 rounded-2xl shadow-2xl max-w-2xl w-full text-center">
          <h1 className="text-4xl font-bold mb-6 text-blue-700">🚀 IncluTalk</h1>
          <p className="text-xl text-gray-700 mb-8">Sistema de Atención Inclusiva con LSP</p>

          <div className="space-y-6">
            <Button onClick={handleStartSession} size="lg" className="w-full">
              ✨ Iniciar Sesión de Atención
            </Button>
            <Button onClick={handleBack} variant="secondary" className="w-full">
              ← Volver al Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="bg-white shadow-lg rounded-2xl p-6 mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-blue-700">IncluTalk - Atención Inclusiva</h1>
          <p className="text-gray-600 mt-1">Sesión activa</p>
        </div>
        <Button onClick={handleBack} variant="danger">Finalizar Sesión</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Operador STT */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">🎤 Operador → Usuario</h2>

          <div className="p-6 bg-blue-50 rounded-xl space-y-4">
            <p className="text-sm text-gray-600">Mantén presionado para hablar:</p>

            <Button
              className="w-full"
              size="lg"
              onMouseDown={startListening}
              onMouseUp={stopListening}
              onMouseLeave={stopListening}
              onTouchStart={startListening}
              onTouchEnd={stopListening}
            >
              {isListening ? '🛑 Grabando...' : '🎙️ Mantener para Hablar'}
            </Button>

            {sttError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                {sttError}
              </div>
            )}
          </div>

          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500 mb-2">Transcripción:</p>
            <p className="text-gray-800 text-lg">{operatorText || '(El texto aparecerá aquí...)'}</p>
          </div>

          <div className="mt-4 flex gap-3">
            <Button
              variant="secondary"
              onClick={() => setOperatorText('')}
              disabled={!operatorText}
              className="flex-1"
            >
              Borrar
            </Button>
            <Button
              onClick={() => console.log('CONFIRMAR STT:', operatorText)}
              disabled={!operatorText}
              className="flex-1"
            >
              Confirmar
            </Button>
          </div>
        </div>

        {/* Usuario (LSP) - lo dejas como está por ahora */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">🤟 Usuario (LSP) → Operador</h2>
          <div className="p-6 bg-green-50 rounded-xl">
            <p className="text-sm text-gray-600 mb-3">Captura de señas:</p>
            <Button className="w-full" size="lg" variant="secondary">
              📹 Iniciar Captura de Señas
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
