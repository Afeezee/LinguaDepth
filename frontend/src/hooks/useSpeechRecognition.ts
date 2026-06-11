import { useCallback, useEffect, useRef, useState } from 'react'

// webkitSpeechRecognition is not in the standard TS DOM lib
declare global {
  interface Window {
    SpeechRecognition?: any
    webkitSpeechRecognition?: any
  }
}

const SpeechRecognitionImpl =
  typeof window !== 'undefined'
    ? window.SpeechRecognition ?? window.webkitSpeechRecognition
    : undefined

// The browser allows only one active SpeechRecognition. Track it globally so
// starting one mic (e.g. the quiz) aborts another that is live (e.g. the chat)
// instead of throwing and appearing dead.
let activeRecognition: any = null

export function useSpeechRecognition() {
  const [transcript, setTranscript] = useState('')
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef<any>(null)

  const isSupported = Boolean(SpeechRecognitionImpl)

  const start = useCallback(() => {
    if (!isSupported || isListening) return
    setTranscript('')

    activeRecognition?.abort()
    // Silence any text-to-speech so the mic doesn't transcribe the AI's voice
    window.speechSynthesis?.cancel()

    const recognition = new SpeechRecognitionImpl()
    recognition.lang = 'en-US'
    recognition.continuous = false
    recognition.interimResults = true

    recognition.onresult = (event: any) => {
      const text = Array.from(event.results)
        .map((result: any) => result[0].transcript)
        .join('')
      setTranscript(text)
    }
    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => {
      setIsListening(false)
      if (activeRecognition === recognition) activeRecognition = null
    }
    recognition.onerror = () => setIsListening(false)

    recognitionRef.current = recognition
    activeRecognition = recognition
    recognition.start()
  }, [isSupported, isListening])

  const stop = useCallback(() => {
    recognitionRef.current?.stop()
    setIsListening(false)
  }, [])

  useEffect(() => {
    return () => {
      if (activeRecognition === recognitionRef.current) activeRecognition = null
      recognitionRef.current?.abort()
    }
  }, [])

  return { start, stop, transcript, isListening, isSupported }
}
