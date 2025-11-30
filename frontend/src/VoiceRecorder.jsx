import React, { useEffect, useRef, useState } from 'react'
import { api } from './apiClient'

export default function VoiceRecorder() {
  const [recording, setRecording] = useState(false)
  const [chunks, setChunks] = useState([])
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [error, setError] = useState('')
  const [uploadResp, setUploadResp] = useState(null)
  const [transcript, setTranscript] = useState('')
  const audioRef = useRef(null)
  const recognitionRef = useRef(null)

  useEffect(() => {
    return () => {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop()
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [mediaRecorder])

  async function startRecording() {
    setError('')
    setUploadResp(null)
    setTranscript('')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mr = new MediaRecorder(stream)
      const localChunks = []
      mr.ondataavailable = e => { if (e.data.size > 0) localChunks.push(e.data) }
      mr.onstop = () => {
        setChunks(localChunks)
        const blob = new Blob(localChunks, { type: 'audio/webm' })
        if (audioRef.current) audioRef.current.src = URL.createObjectURL(blob)
      }
      mr.start()
      setMediaRecorder(mr)
      setRecording(true)
      initSpeechToText()
    } catch (e) {
      setError('Mic access denied or unavailable: ' + e.message)
    }
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop()
    setRecording(false)
    if (recognitionRef.current) recognitionRef.current.stop()
  }

  async function uploadAudio() {
    if (!chunks.length) return
    setError('')
    setUploadResp(null)
    const blob = new Blob(chunks, { type: 'audio/webm' })
    const formData = new FormData()
    formData.append('audio', blob, 'recording.webm')
    const res = await api.voiceUpload(formData)
    if (res.ok) setUploadResp(res.data)
    else setError(JSON.stringify(res.data))
  }

  function initSpeechToText() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) return // not supported
    const rec = new SpeechRecognition()
    rec.continuous = true
    rec.interimResults = true
    rec.lang = 'en-US'
    rec.onresult = (ev) => {
      let text = ''
      for (let i = ev.resultIndex; i < ev.results.length; i++) {
        text += ev.results[i][0].transcript + ' '
      }
      setTranscript(text.trim())
    }
    rec.onerror = (e) => {
      console.warn('Speech recognition error', e.error)
    }
    rec.start()
    recognitionRef.current = rec
  }

  return (
    <div className="voice-recorder">
      <h2>Voice</h2>
      <p className="small muted">Record a short audio message and upload it to backend. Live speech-to-text when supported.</p>
      <div className="flex gap-sm wrap mt-sm">
        {!recording && <button onClick={startRecording}>Start Recording</button>}
        {recording && <button onClick={stopRecording}>Stop Recording</button>}
        <button disabled={!chunks.length} onClick={uploadAudio}>Upload</button>
        <button disabled={!chunks.length} onClick={() => { setChunks([]); setUploadResp(null); setTranscript(''); if (audioRef.current) audioRef.current.src = '' }}>Reset</button>
      </div>
      <div className="mt-sm">
        <audio ref={audioRef} controls style={{ width: '100%' }} />
      </div>
      {transcript && (
        <div className="panel mt-sm" style={{ background: '#14181d' }}>
          <strong>Live Transcript:</strong>
          <p style={{ fontSize: 13, lineHeight: 1.4 }}>{transcript}</p>
        </div>
      )}
      {uploadResp && (
        <pre className="code mt-sm">{JSON.stringify(uploadResp, null, 2)}</pre>
      )}
      {error && <div className="error mt-sm"><strong>Error:</strong> {error}</div>}
    </div>
  )}
