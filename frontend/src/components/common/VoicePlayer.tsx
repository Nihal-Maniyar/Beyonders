import React, { useState, useRef, useEffect } from 'react'
import { Volume2, VolumeX, Play, Pause, RotateCcw, AlertCircle } from 'lucide-react'
import { apiClient } from '../../services/api-client'
import { V1VoiceResponse } from '../../types'

export interface VoicePlayerProps {
  text: string
  label?: string
  interactionId?: string
  autoPlay?: boolean
}

export const VoicePlayer: React.FC<VoicePlayerProps> = ({
  text,
  label = 'Listen to Tutor',
  interactionId,
  autoPlay = false,
}) => {
  const [loading, setLoading] = useState<boolean>(false)
  const [isPlaying, setIsPlaying] = useState<boolean>(false)
  const [fallbackMessage, setFallbackMessage] = useState<string | null>(null)
  const [hasVoice, setHasVoice] = useState<boolean>(true)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const handleSynthesizeAndPlay = async () => {
    if (audioRef.current && audioRef.current.src && hasVoice) {
      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
      } else {
        audioRef.current.play()
        setIsPlaying(true)
      }
      return
    }

    setLoading(true)
    setFallbackMessage(null)

    try {
      const res: V1VoiceResponse = await apiClient.synthesizeVoice(text, interactionId)
      if (res.status === 'succeeded' && res.audio_base64) {
        const audioSrc = `data:${res.mime_type || 'audio/mpeg'};base64,${res.audio_base64}`
        const audio = new Audio(audioSrc)
        audioRef.current = audio

        audio.onended = () => setIsPlaying(false)
        audio.onerror = () => {
          setIsPlaying(false)
          setHasVoice(false)
          setFallbackMessage('Audio playback encountered an error. Reading text is available below.')
        }

        await audio.play()
        setIsPlaying(true)
        setHasVoice(true)
      } else {
        setHasVoice(false)
        setFallbackMessage(res.message || 'Voice audio unavailable. Text explanation shown below.')
      }
    } catch {
      setHasVoice(false)
      setFallbackMessage('Voice service is currently offline. Tutor explanation is shown below.')
    } finally {
      setLoading(false)
    }
  }

  const handleReplay = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0
      audioRef.current.play()
      setIsPlaying(true)
    } else {
      handleSynthesizeAndPlay()
    }
  }

  useEffect(() => {
    if (autoPlay) {
      handleSynthesizeAndPlay()
    }
    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
      }
    }
  }, [text])

  return (
    <div
      style={{
        margin: '12px 0',
        padding: '12px 16px',
        backgroundColor: '#f8fafc',
        border: '1px solid #e2e8f0',
        borderRadius: '8px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
      }}
      role="region"
      aria-label="Tutor voice guidance"
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {hasVoice ? (
            <Volume2 size={18} style={{ color: 'var(--color-brand, #2563eb)' }} aria-hidden="true" />
          ) : (
            <VolumeX size={18} style={{ color: '#64748b' }} aria-hidden="true" />
          )}
          <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#334155' }}>{label}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <button
            type="button"
            onClick={handleSynthesizeAndPlay}
            disabled={loading}
            aria-label={isPlaying ? 'Pause tutor voice' : 'Play tutor voice'}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              backgroundColor: isPlaying ? '#e0f2fe' : '#ffffff',
              border: '1px solid #cbd5e1',
              borderRadius: '6px',
              fontSize: '0.85rem',
              fontWeight: 500,
              color: isPlaying ? '#0369a1' : '#334155',
              cursor: loading ? 'wait' : 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {loading ? (
              <span>Loading audio...</span>
            ) : isPlaying ? (
              <>
                <Pause size={15} aria-hidden="true" />
                <span>Pause Voice</span>
              </>
            ) : (
              <>
                <Play size={15} aria-hidden="true" />
                <span>{audioRef.current ? 'Resume Voice' : 'Listen'}</span>
              </>
            )}
          </button>

          {audioRef.current && (
            <button
              type="button"
              onClick={handleReplay}
              aria-label="Replay tutor voice from beginning"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '6px 10px',
                backgroundColor: '#ffffff',
                border: '1px solid #cbd5e1',
                borderRadius: '6px',
                fontSize: '0.85rem',
                color: '#64748b',
                cursor: 'pointer',
              }}
            >
              <RotateCcw size={14} aria-hidden="true" />
            </button>
          )}
        </div>
      </div>

      {fallbackMessage && (
        <div
          role="status"
          aria-live="polite"
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '8px',
            padding: '8px 12px',
            backgroundColor: '#fffbeb',
            border: '1px solid #fef3c7',
            borderRadius: '6px',
            fontSize: '0.8rem',
            color: '#92400e',
          }}
        >
          <AlertCircle size={15} style={{ flexShrink: 0, marginTop: '2px' }} aria-hidden="true" />
          <span>{fallbackMessage}</span>
        </div>
      )}
    </div>
  )
}

