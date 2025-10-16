'use client'

import { useState, useEffect } from 'react'

type Role = 'questioner' | 'explainer' | 'challenger'
type Message = {
  id: string
  type: 'agent' | 'user'
  content: string
  timestamp: Date
  suggestedActions?: string[]
}

async function startSession(role: Role): Promise<{ sessionId: string, firstPrompt: string } | null> {
  try {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    if (!token) return null
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/learning/sessions/start`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ role, task_type: 'Task 2' })
    })
    if (!res.ok) return null
    const data = await res.json()
    return { sessionId: data.session.id, firstPrompt: data.first_prompt }
  } catch (e) {
    return null
  }
}

async function stepSession(sessionId: string, userInput?: string, draftDelta?: string): Promise<{ agentOutput: string, suggestedActions?: string[] } | null> {
  try {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    if (!token) return null
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/learning/sessions/${sessionId}/step`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: userInput || undefined, draft_delta: draftDelta || undefined })
    })
    if (!res.ok) return null
    const data = await res.json()
    return { 
      agentOutput: data.turn?.agent_output || '',
      suggestedActions: generateSuggestedActions(data.turn?.agent_output || '', data.session?.role || 'questioner')
    }
  } catch (e) {
    return null
  }
}

function generateSuggestedActions(agentOutput: string, role: Role): string[] {
  const output = agentOutput.toLowerCase()
  
  if (role === 'questioner') {
    if (output.includes('thesis') || output.includes('position')) {
      return ['Write my thesis statement', 'Draft my position', 'Outline my argument']
    }
    if (output.includes('example') || output.includes('evidence')) {
      return ['Add a real example', 'Find supporting evidence', 'Cite a study']
    }
    if (output.includes('counter') || output.includes('opposing')) {
      return ['Address the counterargument', 'Acknowledge other views', 'Refute opposing points']
    }
    return ['Continue with my response', 'Ask for clarification', 'Move to next point']
  }
  
  if (role === 'explainer') {
    if (output.includes('structure') || output.includes('paragraph')) {
      return ['Write topic sentence', 'Add supporting details', 'Create transition']
    }
    if (output.includes('vocabulary') || output.includes('word')) {
      return ['Use advanced vocabulary', 'Replace simple words', 'Add academic phrases']
    }
    if (output.includes('grammar') || output.includes('sentence')) {
      return ['Fix grammar errors', 'Vary sentence structure', 'Add complex sentences']
    }
    return ['Apply this tip', 'Try the example', 'Practice this technique']
  }
  
  if (role === 'challenger') {
    if (output.includes('stronger') || output.includes('improve')) {
      return ['Make it stronger', 'Add more detail', 'Be more specific']
    }
    if (output.includes('weak') || output.includes('unclear')) {
      return ['Clarify this point', 'Add explanation', 'Provide evidence']
    }
    if (output.includes('missing') || output.includes('add')) {
      return ['Add missing element', 'Include this component', 'Complete the thought']
    }
    return ['Accept the challenge', 'Try a different approach', 'Ask for help']
  }
  
  return ['Continue writing', 'Ask for guidance', 'Check my progress']
}

export default function WritingCoachPage() {
  const [role, setRole] = useState<Role>('questioner')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [starting, setStarting] = useState(false)
  const [userInput, setUserInput] = useState("")
  const [draftDelta, setDraftDelta] = useState("")
  const [stepping, setStepping] = useState(false)
  const [sessions, setSessions] = useState<{id:string, role:Role, latest_draft:{content:string, version:number}}[]>([])
  const [drafts, setDrafts] = useState<{content:string, version:number}[]>([])
  const [scores, setScores] = useState<{overall_band_score?: number, task_achievement?: number, coherence_cohesion?: number, lexical_resource?: number, grammatical_range?: number}>({})
  const [checking, setChecking] = useState(false)
  const [currentDraft, setCurrentDraft] = useState("")
  const [wizardMode, setWizardMode] = useState<boolean>(false)
  const wizardSteps = [
    { key: 'intro', label: 'Introduction' },
    { key: 'outline', label: 'Outline' },
    { key: 'body1', label: 'Body Paragraph 1' },
    { key: 'body2', label: 'Body Paragraph 2' },
    { key: 'conclusion', label: 'Conclusion' }
  ] as const
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0)

  const wizardScaffolds: Record<typeof wizardSteps[number]['key'], { hint: string, responseTemplate: Record<Role, string>, draftTemplate: Record<Role, string> }> = {
    intro: {
      hint: 'State your position clearly and preview your two main reasons.',
      responseTemplate: {
        questioner: 'My position is that ____. The two main reasons are ____ and ____.',
        explainer: 'I will state a clear thesis and preview two reasons.',
        challenger: 'I will make my stance specific and debatable.'
      },
      draftTemplate: {
        questioner: 'In today\'s world, ____. While some argue ____, I believe ____ because ____ and ____.',
        explainer: 'This essay argues that ____. This is because ____ and ____.',
        challenger: 'I contend that ____, primarily due to ____ and ____, despite common objections.'
      }
    },
    outline: {
      hint: 'Plan topic sentences and evidence for each body paragraph.',
      responseTemplate: {
        questioner: 'Body 1: topic sentence ____, evidence ____. Body 2: topic sentence ____, evidence ____.',
        explainer: 'I will outline two paragraphs with topic sentences and examples.',
        challenger: 'I will ensure each paragraph advances a distinct, non-overlapping reason.'
      },
      draftTemplate: {
        questioner: '- BP1: ____ (TS). Support: ____.\n- BP2: ____ (TS). Support: ____.',
        explainer: 'Outline:\n1) ____. Example: ____.\n2) ____. Example: ____.',
        challenger: 'Plan:\n- Para 1 proves ____ with ____.\n- Para 2 proves ____ with ____.'
      }
    },
    body1: {
      hint: 'Write Body 1: clear topic sentence, explanation, specific example, mini-conclusion.',
      responseTemplate: {
        questioner: 'I will write Body 1 focusing on ____, with an example about ____.',
        explainer: 'I will use the pattern: TS → Explain → Example → Therefore.',
        challenger: 'I will avoid vague claims and add concrete, verifiable detail.'
      },
      draftTemplate: {
        questioner: 'Firstly, ____. This matters because ____. For example, ____. Therefore, ____.',
        explainer: 'First, ____. This can be seen in ____. Therefore, this supports the position because ____.',
        challenger: 'To begin with, ____. Consider ____, where ____. Consequently, ____.'
      }
    },
    body2: {
      hint: 'Write Body 2: second reason, different from Body 1; add counterpoint if possible.',
      responseTemplate: {
        questioner: 'I will write Body 2 focusing on a distinct reason: ____.',
        explainer: 'I will follow TS → Explain → Example → Therefore again, avoiding repetition.',
        challenger: 'I will address a likely counterargument and then refute it.'
      },
      draftTemplate: {
        questioner: 'Moreover, ____. This is because ____. For instance, ____. Hence, ____.',
        explainer: 'Secondly, ____. For example, ____. Therefore, ____.',
        challenger: 'Admittedly, some argue ____. However, ____. Therefore, ____.'
      }
    },
    conclusion: {
      hint: 'Summarise your reasons and restate your position without new arguments.',
      responseTemplate: {
        questioner: 'I will summarise both reasons and restate the thesis concisely.',
        explainer: 'I will paraphrase the thesis and synthesise the two reasons.',
        challenger: 'I will avoid adding any new points and keep it decisive.'
      },
      draftTemplate: {
        questioner: 'In summary, ____. Because ____ and ____, it is clear that ____.',
        explainer: 'In conclusion, this essay has shown that ____ due to ____ and ____.',
        challenger: 'Taken together, the evidence for ____ and ____ demonstrates that ____.'
      }
    }
  }

  const handleStartSession = async () => {
    setStarting(true)
    const res = await startSession(role)
    if (res) {
      setSessionId(res.sessionId)
      const firstMessage: Message = {
        id: '1',
        type: 'agent',
        content: res.firstPrompt,
        timestamp: new Date(),
        suggestedActions: generateSuggestedActions(res.firstPrompt, role)
      }
      setMessages([firstMessage])
    }
    setStarting(false)
  }

  const handleStep = async () => {
    if (!sessionId) return
    setStepping(true)
    
    // Add user message to conversation
    if (userInput.trim()) {
      const userMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: userInput,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, userMessage])
    }
    
    // Update draft if provided
    if (draftDelta.trim()) {
      setCurrentDraft(prev => prev + (prev ? '\n\n' : '') + draftDelta)
    }
    
    try {
      const result = await stepSession(sessionId, userInput || undefined, draftDelta || undefined)
      if (result) {
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'agent',
          content: result.agentOutput,
          timestamp: new Date(),
          suggestedActions: result.suggestedActions
        }
        setMessages(prev => [...prev, agentMessage])
      }
    } finally {
      setUserInput('')
      setDraftDelta('')
      setStepping(false)
    }
  }

  const handleSuggestedAction = (action: string) => {
    setUserInput(action)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">Writing Coach</h1>
          <div className="flex space-x-2">
            {(['questioner','explainer','challenger'] as Role[]).map(r => (
              <button
                key={r}
                onClick={() => setRole(r)}
                className={`px-3 py-1 text-sm font-medium rounded ${role===r? 'bg-blue-600 text-white':'bg-white text-gray-600 border hover:bg-gray-50'}`}
              >
                {r.charAt(0).toUpperCase()+r.slice(1)}
              </button>
            ))}
            <button
              onClick={() => setWizardMode(v => !v)}
              className={`px-3 py-1 text-sm font-medium rounded ${wizardMode? 'bg-emerald-600 text-white':'bg-white text-gray-600 border hover:bg-gray-50'}`}
            >
              {wizardMode ? 'Wizard: On' : 'Wizard: Off'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Conversation Thread */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold text-gray-800">Conversation with {role.charAt(0).toUpperCase() + role.slice(1)}</h2>
                {!sessionId && (
                  <p className="text-sm text-gray-500 mt-1">Choose a coach role and start a session to begin</p>
                )}
              </div>
              
              <div className="p-4">
                {!sessionId ? (
                  <div className="text-center py-8">
                    <button
                      onClick={handleStartSession}
                      disabled={starting}
                      className={`px-6 py-3 rounded-lg text-lg font-semibold ${starting? 'bg-gray-200 text-gray-500':'bg-blue-600 text-white hover:bg-blue-700'}`}
                    >
                      {starting? 'Starting Session...':'Start Session'}
                    </button>
                    <p className="text-sm text-gray-500 mt-2">
                      {role === 'questioner' && 'I\'ll guide you with Socratic questions to develop your ideas'}
                      {role === 'explainer' && 'I\'ll provide clear explanations and examples from IELTS materials'}
                      {role === 'challenger' && 'I\'ll push you to strengthen weak points and add depth'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Guided Wizard */}
                    {wizardMode && (
                      <div className="border rounded-lg p-4 bg-amber-50 border-amber-200">
                        <div className="flex items-center justify-between mb-3">
                          <div className="text-sm font-semibold text-amber-800">Guided Wizard</div>
                          <div className="flex items-center space-x-2">
                            <button
                              className="text-xs px-2 py-1 rounded border bg-white hover:bg-gray-50"
                              onClick={() => setCurrentStepIndex(i => Math.max(0, i - 1))}
                              disabled={currentStepIndex===0}
                            >Prev</button>
                            <div className="text-xs text-amber-700">
                              Step {currentStepIndex+1} / {wizardSteps.length}: {wizardSteps[currentStepIndex].label}
                            </div>
                            <button
                              className="text-xs px-2 py-1 rounded border bg-white hover:bg-gray-50"
                              onClick={() => setCurrentStepIndex(i => Math.min(wizardSteps.length-1, i + 1))}
                              disabled={currentStepIndex===wizardSteps.length-1}
                            >Next</button>
                          </div>
                        </div>
                        <div className="text-xs text-amber-900 mb-2">{wizardScaffolds[wizardSteps[currentStepIndex].key].hint}</div>
                        <div className="flex flex-wrap gap-2">
                          <button
                            className="text-xs px-3 py-1 rounded bg-white border hover:bg-gray-50"
                            onClick={() => setUserInput(wizardScaffolds[wizardSteps[currentStepIndex].key].responseTemplate[role])}
                          >Use response scaffold</button>
                          <button
                            className="text-xs px-3 py-1 rounded bg-white border hover:bg-gray-50"
                            onClick={() => setDraftDelta(prev => wizardScaffolds[wizardSteps[currentStepIndex].key].draftTemplate[role])}
                          >Use draft scaffold</button>
                          <button
                            className="text-xs px-3 py-1 rounded bg-emerald-600 text-white hover:bg-emerald-700"
                            onClick={handleStep}
                          >Complete step</button>
                        </div>
                      </div>
                    )}

                    {/* Messages */}
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {messages.map((message) => (
                        <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                            message.type === 'user' 
                              ? 'bg-blue-600 text-white' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            <div className="text-sm">{message.content}</div>
                            <div className={`text-xs mt-1 ${
                              message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                            }`}>
                              {message.timestamp.toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Suggested Actions */}
                    {messages.length > 0 && messages[messages.length - 1].suggestedActions && (
                      <div className="border-t pt-4">
                        <p className="text-sm text-gray-600 mb-2">Suggested actions:</p>
                        <div className="flex flex-wrap gap-2">
                          {messages[messages.length - 1].suggestedActions!.map((action, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleSuggestedAction(action)}
                              className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full border"
                            >
                              {action}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Input Area */}
                    <div className="border-t pt-4 space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Your response</label>
                        <textarea 
                          value={userInput} 
                          onChange={e => setUserInput(e.target.value)} 
                          className="w-full h-20 border rounded-lg p-3 text-sm" 
                          placeholder="Type your response to the coach..."
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Draft changes (optional)</label>
                        <textarea 
                          value={draftDelta} 
                          onChange={e => setDraftDelta(e.target.value)} 
                          className="w-full h-20 border rounded-lg p-3 text-sm" 
                          placeholder="Paste any new writing here..."
                        />
                      </div>
                      <button
                        onClick={handleStep}
                        disabled={stepping}
                        className={`w-full py-2 px-4 rounded-lg font-medium ${stepping? 'bg-gray-200 text-gray-500':'bg-emerald-600 text-white hover:bg-emerald-700'}`}
                      >
                        {stepping? 'Sending...':'Send Response'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Current Draft */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-4 border-b">
                <h3 className="text-lg font-semibold text-gray-800">Current Draft</h3>
              </div>
              <div className="p-4">
                <textarea
                  value={currentDraft}
                  onChange={e => setCurrentDraft(e.target.value)}
                  className="w-full h-48 border rounded-lg p-3 text-sm"
                  placeholder="Your essay will appear here as you write..."
                />
                <div className="mt-2 text-xs text-gray-500">
                  {currentDraft.length} characters
                </div>
              </div>
            </div>

            {/* Rubric */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-4 border-b">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-800">Rubric</h3>
                  <button
                    disabled={!sessionId || checking}
                    onClick={async()=>{
                      if(!sessionId) return
                      setChecking(true)
                      try{
                        const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
                        if (!token) return
                        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/learning/sessions/${sessionId}/checkpoint`,{ method:'POST', headers:{'Authorization':`Bearer ${token}`}})
                        if(res.ok){
                          const data = await res.json()
                          const s = data.scores || {}
                          setScores({ overall_band_score: s.overall_band_score, task_achievement: s.task_achievement, coherence_cohesion: s.coherence_cohesion, lexical_resource: s.lexical_resource, grammatical_range: s.grammatical_range })
                        }
                      } finally { setChecking(false) }
                    }}
                    className={`text-xs px-3 py-1 rounded ${!sessionId||checking? 'bg-gray-200 text-gray-500':'bg-purple-600 text-white hover:bg-purple-700'}`}
                  >{checking? 'Checking...':'Checkpoint'}</button>
                </div>
              </div>
              <div className="p-4">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Overall:</span>
                    <span className="font-medium">{scores.overall_band_score ?? '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Task Achievement:</span>
                    <span className="font-medium">{scores.task_achievement ?? '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Coherence & Cohesion:</span>
                    <span className="font-medium">{scores.coherence_cohesion ?? '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Lexical Resource:</span>
                    <span className="font-medium">{scores.lexical_resource ?? '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Grammatical Range:</span>
                    <span className="font-medium">{scores.grammatical_range ?? '-'}</span>
                  </div>
                </div>
                <div className="mt-3 text-xs text-gray-500">Target: 7.0+ across all criteria</div>
              </div>
            </div>

            {/* Session History */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-4 border-b">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-800">Sessions</h3>
                  <button
                    className="text-xs text-blue-600 hover:underline"
                    onClick={async()=>{
                      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
                      if (!token) return
                      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/learning/sessions/`,{ headers:{'Authorization':`Bearer ${token}`}})
                      if(res.ok){ const data = await res.json(); setSessions(data.sessions || []) }
                    }}
                  >Refresh</button>
                </div>
              </div>
              <div className="p-4">
                <div className="space-y-2">
                  {sessions.map(s=> (
                    <div key={s.id} className="border rounded p-2 text-sm">
                      <div className="flex items-center justify-between">
                        <div>#{s.id} • {s.role}</div>
                        <button
                          className="text-xs text-emerald-700 hover:underline"
                          onClick={async()=>{
                            const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
                            if (!token) return
                            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/learning/sessions/${s.id}/drafts`,{ headers:{'Authorization':`Bearer ${token}`}})
                            if(res.ok){ const data = await res.json(); setDrafts(data.drafts || []) }
                          }}
                        >View drafts</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}


