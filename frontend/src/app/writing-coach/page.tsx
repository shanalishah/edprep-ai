'use client'

import { useState } from 'react'

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

type Role = 'questioner' | 'explainer' | 'challenger'

export default function WritingCoachPage() {
  const [role, setRole] = useState<Role>('questioner')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [firstPrompt, setFirstPrompt] = useState<string>("")
  const [starting, setStarting] = useState(false)
  const [userInput, setUserInput] = useState("")
  const [draftDelta, setDraftDelta] = useState("")
  const [lastAgentOutput, setLastAgentOutput] = useState("")
  const [stepping, setStepping] = useState(false)
  const [sessions, setSessions] = useState<{id:string, role:Role, latest_draft:{content:string, version:number}}[]>([])
  const [drafts, setDrafts] = useState<{content:string, version:number}[]>([])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <h1 className="text-2xl font-semibold text-gray-900 mb-4">Writing Coach (M1)</h1>

        <div className="bg-white rounded-lg shadow-sm border">
          <div className="flex border-b">
            {(['questioner','explainer','challenger'] as Role[]).map(r => (
              <button
                key={r}
                onClick={() => setRole(r)}
                className={`px-4 py-2 text-sm font-medium border-r last:border-r-0 ${role===r? 'bg-blue-50 text-blue-700':'text-gray-600 hover:bg-gray-50'}`}
              >
                {r.charAt(0).toUpperCase()+r.slice(1)}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-0">
            {/* Chat/Guidance pane */}
            <div className="p-4 border-r">
              <div className="text-sm text-gray-700">
                <p className="mb-2">Role: <span className="font-medium">{role}</span></p>
                {firstPrompt ? (
                  <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded text-blue-800 text-sm">
                    {firstPrompt}
                  </div>
                ) : (
                  <p className="text-gray-500">Start a session to receive the first prompt.</p>
                )}
                {lastAgentOutput && (
                  <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded text-green-800 text-sm">
                    {lastAgentOutput}
                  </div>
                )}
              </div>
              <div className="mt-4">
                <button
                  onClick={async () => {
                    setStarting(true)
                    const res = await startSession(role)
                    if (res) { setSessionId(res.sessionId); setFirstPrompt(res.firstPrompt) }
                    setStarting(false)
                  }}
                  disabled={starting}
                  className={`px-4 py-2 rounded ${starting? 'bg-gray-200 text-gray-500':'bg-blue-600 text-white hover:bg-blue-700'}`}
                >
                  {starting? 'Starting...':'Start Session'}
                </button>
              </div>

              {/* Step controls */}
              <div className="mt-6 space-y-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Your reply</label>
                  <textarea value={userInput} onChange={e=>setUserInput(e.target.value)} className="w-full h-20 border rounded p-2" placeholder="Type a short reply to the agent" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Draft delta (optional)</label>
                  <textarea value={draftDelta} onChange={e=>setDraftDelta(e.target.value)} className="w-full h-20 border rounded p-2" placeholder="Paste or type any draft changes here" />
                </div>
                <button
                  onClick={async ()=>{
                    if(!sessionId) return
                    setStepping(true)
                    try{
                      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
                      if (!token) return
                      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/learning/sessions/${sessionId}/step`,{
                        method:'POST',
                        headers:{'Authorization':`Bearer ${token}`,'Content-Type':'application/json'},
                        body: JSON.stringify({ user_input: userInput || undefined, draft_delta: draftDelta || undefined })
                      })
                      if(res.ok){
                        const data = await res.json()
                        setLastAgentOutput(data.turn?.agent_output || '')
                        setUserInput('')
                        setDraftDelta('')
                      }
                    } finally { setStepping(false) }
                  }}
                  disabled={!sessionId || stepping}
                  className={`px-4 py-2 rounded ${!sessionId||stepping? 'bg-gray-200 text-gray-500':'bg-emerald-600 text-white hover:bg-emerald-700'}`}
                >
                  {stepping? 'Working...':'Send Step'}
                </button>
              </div>
            </div>

            {/* Draft editor pane */}
            <div className="p-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Draft</label>
              <textarea
                disabled
                className="w-full h-64 border rounded p-3 text-gray-500 bg-gray-50 cursor-not-allowed"
                placeholder="Editing will be enabled in M2"
              />
              <div className="mt-3 text-xs text-gray-500">Checkpoints and scoring will be enabled in M2.</div>

              {/* History */}
              <div className="mt-6">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-sm font-semibold text-gray-800">Your Sessions</h2>
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

                {drafts.length>0 && (
                  <div className="mt-4">
                    <h3 className="text-sm font-semibold text-gray-800 mb-1">Draft Versions</h3>
                    <div className="space-y-2 max-h-48 overflow-auto border rounded p-2 bg-gray-50">
                      {drafts.map(d => (
                        <div key={d.version} className="text-xs">
                          <div className="font-medium">v{d.version}</div>
                          <pre className="whitespace-pre-wrap">{d.content}</pre>
                          <hr className="my-2" />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}


