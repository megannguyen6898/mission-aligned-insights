import React, { useState } from 'react';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Sparkles, Send } from 'lucide-react';

interface AskAIDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const AskAIDrawer: React.FC<AskAIDrawerProps> = ({ open, onOpenChange }) => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'ai'; content: string }>>([]);

  const handleSend = () => {
    if (!question.trim()) return;

    setMessages((prev) => [
      ...prev,
      { role: 'user', content: question },
      { 
        role: 'ai', 
        content: 'This is a placeholder AI response. Connect to your AI service to get real insights.' 
      },
    ]);
    setQuestion('');
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="w-[400px] sm:w-[540px] p-0">
        <div className="flex flex-col h-full">
          <SheetHeader className="p-6 border-b border-border">
            <SheetTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Ask AI
            </SheetTitle>
            <SheetDescription>
              Get insights about your impact data
            </SheetDescription>
          </SheetHeader>

          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-12">
                <Sparkles className="h-12 w-12 mx-auto mb-4 text-primary/50" />
                <p className="text-sm">Ask me anything about your impact data</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={cn(
                    'rounded-2xl p-4',
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground ml-8'
                      : 'gradient-ai border border-primary/10 mr-8'
                  )}
                >
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                </div>
              ))
            )}
          </div>

          <div className="p-6 border-t border-border space-y-4">
            <Textarea
              placeholder="Ask a question about your data..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              className="min-h-[100px] resize-none"
            />
            <Button onClick={handleSend} className="w-full" disabled={!question.trim()}>
              <Send className="h-4 w-4 mr-2" />
              Send
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};

function cn(...classes: (string | undefined)[]) {
  return classes.filter(Boolean).join(' ');
}
