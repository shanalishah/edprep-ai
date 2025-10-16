'use client'

import { useState } from 'react'

type Role = 'questioner' | 'explainer' | 'challenger'

export default function WritingCoachPage() {
  const [role, setRole] = useState<Role>('questioner')

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
                <p className="text-gray-500">API skeleton is wired. Guidance will appear here in M2.</p>
              </div>
              <div className="mt-4">
                <button
                  disabled
                  className="px-4 py-2 bg-gray-200 text-gray-500 rounded cursor-not-allowed"
                >
                  Start Session (disabled in M1)
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
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}


