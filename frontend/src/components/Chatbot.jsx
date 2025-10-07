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

    // Simulate bot response
    setTimeout(() => {
      const botResponse = {
        type: 'bot',
        text: getBotResponse(text),
        timestamp: new Date()
      }
      setMessages(prev => [...prev, botResponse])
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
          className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-200 hover:scale-110 z-50"
          aria-label="Open chat"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col z-50 border border-gray-200">
          {/* Header */}
          <div className="bg-blue-600 text-white px-4 py-3 rounded-t-lg flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MessageCircle className="w-5 h-5" />
              <span className="font-semibold">AI Assistant</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-blue-700 rounded p-1 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <span className="text-xs opacity-70 mt-1 block">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}

            {/* Suggested Questions */}
            {messages.length === 1 && (
              <div className="space-y-2">
                <p className="text-xs text-gray-500 font-semibold">Suggested questions:</p>
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuestionClick(question)}
                    className="w-full text-left text-xs bg-gray-50 hover:bg-gray-100 text-gray-700 px-3 py-2 rounded border border-gray-200 transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputValue)}
                placeholder="Type your message..."
                className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={() => handleSendMessage(inputValue)}
                className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 transition-colors"
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
