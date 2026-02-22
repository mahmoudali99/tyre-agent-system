'use client';

import { MainLayout } from '@/components/layout/main-layout';
import { AgentChat } from '@/components/chat/agent-chat';

export default function AgentChatPage() {
  return (
    <MainLayout>
      <div className="flex flex-col h-full space-y-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">AI Chat Assistant</h1>
          <p className="text-muted-foreground mt-1">Chat with our intelligent tyre specialist</p>
        </div>

        <div className="flex-1 min-h-0">
          <AgentChat />
        </div>
      </div>
    </MainLayout>
  );
}
