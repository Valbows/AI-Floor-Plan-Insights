import React, { useState } from 'react'
import { MessageCircle, X, Send } from 'lucide-react'

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: 'Hi! I\'m your AI assistant. How can I help you today?',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(true)

  const suggestedQuestions = [
    "How do I upload a floor plan?",
    "What does the AI analyze?",
    "How accurate are the price estimates?",
    "Can I export my property data?",
    "How long does analysis take?",
    "What file formats are supported?"
  ]

  const handleSendMessage = (text) => {
    if (!text.trim()) return

    // Add user message
    const userMessage = {
      type: 'user',
      text: text,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setShowSuggestions(false)

    // Simulate bot response
    setTimeout(() => {
      const botResponse = {
        type: 'bot',
        text: getBotResponse(text),
        timestamp: new Date()
      }
      setMessages(prev => [...prev, botResponse])
      
      // Show suggestions again after bot responds
      setTimeout(() => {
        setShowSuggestions(true)
      }, 100)
    }, 500)
  }

  const getBotResponse = (question) => {
    const lowerQuestion = question.toLowerCase()
    
    if (lowerQuestion.includes('upload') || lowerQuestion.includes('floor plan')) {
      return 'To upload a floor plan, click the "Add Property" button on the dashboard. You can upload images in JPG, PNG, or PDF format. Our AI will automatically extract property details from your floor plan.'
    } else if (lowerQuestion.includes('analyze') || lowerQuestion.includes('ai')) {
      return 'Our AI analyzes floor plans to extract: room counts, square footage, layout type, features, and dimensions. It also provides market insights including price estimates, comparable properties, and investment analysis.'
    } else if (lowerQuestion.includes('price') || lowerQuestion.includes('estimate') || lowerQuestion.includes('accurate')) {
      return 'Price estimates are based on extracted property features, location data, and market comparables. Accuracy varies by data availability, but we provide confidence levels (high/medium/low) with each estimate.'
    } else if (lowerQuestion.includes('export') || lowerQuestion.includes('data')) {
      return 'You can export property data by clicking on any property card to view details, then use the copy buttons to export listing descriptions, social media content, and property specifications.'
    } else if (lowerQuestion.includes('time') || lowerQuestion.includes('long') || lowerQuestion.includes('take')) {
      return 'Floor plan analysis typically takes 30-60 seconds. Market enrichment and listing generation may take an additional 1-2 minutes. You\'ll see real-time status updates as processing completes.'
    } else if (lowerQuestion.includes('format') || lowerQuestion.includes('file')) {
      return 'We support JPG, JPEG, PNG, and PDF formats for floor plan uploads. For best results, use high-resolution images with clear room labels and dimensions.'
    } else {
      return 'I\'m here to help! You can ask me about uploading floor plans, AI analysis features, pricing estimates, data export, processing times, or supported file formats. What would you like to know?'
    }
  }

  const handleQuestionClick = (question) => {
    handleSendMessage(question)
  }

  return (
    <>
      {/* Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 text-white rounded-full p-4 shadow-lg transition-all duration-200 hover:scale-110 z-50"
          style={{background: '#FF5959'}}
          onMouseEnter={(e) => e.currentTarget.style.background = '#E54545'}
          onMouseLeave={(e) => e.currentTarget.style.background = '#FF5959'}
          aria-label="Open chat"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white flex flex-col z-50" style={{borderRadius: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.2)', border: '2px solid #000000'}}>
          {/* Header */}
          <div className="bg-black text-white px-4 py-3 flex items-center justify-between" style={{borderTopLeftRadius: '10px', borderTopRightRadius: '10px', borderBottom: '4px solid #FF5959'}}>
            <div className="flex items-center space-x-2">
              <MessageCircle className="w-5 h-5" style={{color: '#FF5959'}} />
              <span className="font-black uppercase tracking-tight" style={{letterSpacing: '1px'}}>AI Assistant</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="rounded p-1 transition-colors"
              style={{color: '#FF5959'}}
              onMouseEnter={(e) => {e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}}
              onMouseLeave={(e) => {e.currentTarget.style.background = 'transparent'}}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{background: '#F6F1EB'}}>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className="max-w-[80%] px-4 py-2"
                  style={{
                    background: message.type === 'user' ? '#FF5959' : '#FFFFFF',
                    color: message.type === 'user' ? '#FFFFFF' : '#000000',
                    borderRadius: '8px',
                    border: message.type === 'user' ? 'none' : '1px solid #E5E5E5'
                  }}
                >
                  <p className="text-sm">{message.text}</p>
                  <span className="text-xs opacity-70 mt-1 block">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}

            {/* Suggested Questions */}
            {showSuggestions && (
              <div className="space-y-2 animate-fadeIn">
                <p className="text-xs font-bold uppercase" style={{color: '#666666', letterSpacing: '1px'}}>💡 Suggested questions:</p>
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuestionClick(question)}
                    className="w-full text-left text-xs px-3 py-2 transition-all"
                    style={{background: '#FFFFFF', color: '#000000', borderRadius: '4px', border: '1px solid #E5E5E5'}}
                    onMouseEnter={(e) => {e.currentTarget.style.background = '#FFF5F5'; e.currentTarget.style.borderColor = '#FF5959'}}
                    onMouseLeave={(e) => {e.currentTarget.style.background = '#FFFFFF'; e.currentTarget.style.borderColor = '#E5E5E5'}}
                  >
                    {question}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4" style={{borderTop: '2px solid #E5E5E5', background: '#FFFFFF'}}>
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputValue)}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 text-sm focus:outline-none transition-colors"
                style={{border: '2px solid #000000', borderRadius: '4px'}}
                onFocus={(e) => {e.target.style.borderColor = '#FF5959'; e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.1)'}}
                onBlur={(e) => {e.target.style.borderColor = '#000000'; e.target.style.boxShadow = 'none'}}
              />
              <button
                onClick={() => handleSendMessage(inputValue)}
                className="text-white px-4 py-2 transition-all"
                style={{background: '#FF5959', borderRadius: '4px'}}
                onMouseEnter={(e) => {e.currentTarget.style.background = '#E54545'; e.currentTarget.style.transform = 'translateY(-1px)'}}
                onMouseLeave={(e) => {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.transform = 'translateY(0)'}}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default Chatbot
