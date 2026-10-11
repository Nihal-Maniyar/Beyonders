import React, { useState, useRef, useEffect } from 'react'
import { Mic, Square, Loader2, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react'
import { apiClient } from '../../services/api-client'

export interface VoiceInputButtonProps {
  onTranscript: (text: string) => void
  label?: string
  interactionId?: string
  disabled?: boolean
  autoStopSeconds?: number
}

type RecordingState = 'idle' | 'recording' | 'transcribing' | 'success' | 'error'

export const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({
  onTranscript,
  label = 'Speak Answer',
  interactionId,
  disabled = false,
  autoStopSeconds = 60,
}) => {
  const [state, setState] = useState<RecordingState>('idle')
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0)
  const [statusMessage, setStatusMessage] = useState<string | null>(null)
  const [transcribedPreview, setTranscribedPreview] = useState<string | null>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<number | null>(null)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        window.clearInterval(timerRef.current)
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
      }
    }
  }, [])

  const startRecording = async () => {
    setStatusMessage(null)
    setTranscribedPreview(null)

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setState('error')
      setStatusMessage('Voice recording is not supported in this browser. Please type your explanation.')
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      // Pick supported mime type
      const mimeTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/mp4',
        '',
      ]
      let selectedMimeType = ''
      for (const mime of mimeTypes) {
        if (!mime || MediaRecorder.isTypeSupported(mime)) {
          selectedMimeType = mime
          break
        }
      }

      const mediaRecorder = selectedMimeType
        ? new MediaRecorder(stream, { mimeType: selectedMimeType })
        : new MediaRecorder(stream)

      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        if (timerRef.current) {
          window.clearInterval(timerRef.current)
          timerRef.current = null
        }

        // Stop all audio tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop())
          streamRef.current = null
        }

        const audioBlob = new Blob(chunksRef.current, {
          type: selectedMimeType || 'audio/webm',
        })

        if (audioBlob.size === 0) {
          setState('error')
          setStatusMessage('No audio was captured. Please try speaking again.')
          return
        }

        // Send to ElevenLabs STT proxy
        setState('transcribing')
        try {
          const res = await apiClient.transcribeVoice(audioBlob, interactionId)
          if (res.status === 'succeeded' && res.text.trim()) {
            setState('success')
            setTranscribedPreview(res.text)
            setStatusMessage(`Speech transcribed (${Math.round(res.duration_ms / 100) / 10}s).`)
            onTranscript(res.text)
          } else {
            setState('error')
            setStatusMessage(
              res.message || 'No clear speech detected. You can type directly in the box below.'
            )
          }
        } catch (err: any) {
          setState('error')
          setStatusMessage(
            err.message || 'Speech-to-text service is temporarily unavailable. Please type your answer.'
          )
        }
      }

      mediaRecorder.start(250) // collect slices every 250ms
      setState('recording')
      setElapsedSeconds(0)

      timerRef.current = window.setInterval(() => {
        setElapsedSeconds((prev) => {
          if (prev + 1 >= autoStopSeconds) {
            stopRecording()
            return autoStopSeconds
          }
          return prev + 1
        })
      }, 1000)
    } catch (err: any) {
      setState('error')
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setStatusMessage('Microphone access was denied. Please allow microphone permissions or type your answer.')
      } else {
        setStatusMessage(`Microphone error: ${err.message || 'Unable to record'}. You can type directly below.`)
      }
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    if (timerRef.current) {
      window.clearInterval(timerRef.current)
      timerRef.current = null
    }
  }

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60)
    const s = secs % 60
    return `${m}:${s < 10 ? '0' : ''}${s}`
  }

  return (
    <div
      style={{
        display: 'inline-flex',
        flexDirection: 'column',
        gap: '6px',
        alignItems: 'flex-start',
      }}
      role="region"
      aria-label="Speech to text input"
    >
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
        {state === 'idle' || state === 'error' || state === 'success' ? (
          <button
            type="button"
            onClick={startRecording}
            disabled={disabled}
            aria-label={label}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 14px',
              backgroundColor: '#eff6ff',
              color: '#1d4ed8',
              border: '1.5px solid #93c5fd',
              borderRadius: '8px',
              fontSize: '0.9rem',
              fontWeight: 600,
              cursor: disabled ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s ease',
              boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
            }}
          >
            <Mic size={16} aria-hidden="true" style={{ color: '#2563eb' }} />
            <span>{label}</span>
          </button>
        ) : state === 'recording' ? (
          <button
            type="button"
            onClick={stopRecording}
            aria-label="Stop recording and transcribe"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              backgroundColor: '#fef2f2',
              color: '#b91c1c',
              border: '1.5px solid #f87171',
              borderRadius: '8px',
              fontSize: '0.9rem',
              fontWeight: 600,
              cursor: 'pointer',
              animation: 'pulse 1.5s infinite',
              boxShadow: '0 0 0 3px rgba(239, 68, 68, 0.2)',
            }}
          >
            <span
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: '#dc2626',
                display: 'inline-block',
                boxShadow: '0 0 6px #dc2626',
              }}
            />
            <Square size={14} style={{ fill: '#b91c1c' }} aria-hidden="true" />
            <span>Stop Recording ({formatTimer(elapsedSeconds)} / {formatTimer(autoStopSeconds)})</span>
          </button>
        ) : (
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 14px',
              backgroundColor: '#f8fafc',
              color: '#475569',
              border: '1.5px solid #cbd5e1',
              borderRadius: '8px',
              fontSize: '0.9rem',
              fontWeight: 500,
            }}
          >
            <Loader2 size={16} className="animate-spin" style={{ color: '#2563eb' }} aria-hidden="true" />
            <span>Transcribing speech with ElevenLabs...</span>
          </div>
        )}

        {state === 'recording' && (
          <span style={{ fontSize: '0.85rem', color: '#dc2626', fontWeight: 500 }}>
            🎙️ Listening... Click stop when finished
          </span>
        )}
      </div>

      {/* Visual Feedback Notifications */}
      {statusMessage && (
        <div
          role="status"
          aria-live="polite"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '0.85rem',
            backgroundColor:
              state === 'error' ? '#fff1f2' : state === 'success' ? '#f0fdf4' : '#f8fafc',
            border: `1px solid ${
              state === 'error' ? '#fecdd3' : state === 'success' ? '#bbf7d0' : '#e2e8f0'
            }`,
            color: state === 'error' ? '#9f1239' : state === 'success' ? '#166534' : '#334155',
          }}
        >
          {state === 'error' ? (
            <AlertCircle size={15} style={{ flexShrink: 0 }} aria-hidden="true" />
          ) : state === 'success' ? (
            <CheckCircle2 size={15} style={{ flexShrink: 0, color: '#16a34a' }} aria-hidden="true" />
          ) : (
            <Sparkles size={15} style={{ flexShrink: 0, color: '#2563eb' }} aria-hidden="true" />
          )}
          <span>{statusMessage}</span>
        </div>
      )}

      {transcribedPreview && state === 'success' && (
        <div
          style={{
            fontSize: '0.8rem',
            color: '#475569',
            fontStyle: 'italic',
            paddingLeft: '4px',
          }}
        >
          Last transcript: &quot;{transcribedPreview.length > 80 ? transcribedPreview.substring(0, 80) + '...' : transcribedPreview}&quot;
        </div>
      )}
    </div>
  )
}

