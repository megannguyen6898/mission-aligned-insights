import React, { useEffect, useRef, useState } from 'react';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Sparkles, Send, Loader2 } from 'lucide-react';
import { askAI, ChatMessage } from '@/api/ai';
import { cn } from '@/lib/utils';

interface AskAIDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const AskAIDrawer: React.FC<AskAIDrawerProps> = ({ open, onOpenChange }) => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) {
      setQuestion('');
    }
  }, [open]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    const trimmed = question.trim();
    if (!trimmed || isLoading) return;

    const newUserMessage: ChatMessage = { role: 'user', content: trimmed };
    const history = [...messages];
    setMessages((prev) => [...prev, newUserMessage]);
    setQuestion('');
    setIsLoading(true);

    try {
      const { answer } = await askAI(trimmed, history);
      setMessages((prev) => [...prev, { role: 'ai', content: answer }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content:
            "I couldn't reach the AI service right now. Please verify your configuration or try again in a moment.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="flex h-full w-full max-w-xl flex-col p-0">
        <SheetHeader className="border-b border-border px-6 py-5 text-left">
          <SheetTitle className="flex items-center gap-2 text-lg">
            <Sparkles className="h-5 w-5 text-primary" />
            Ask AI
          </SheetTitle>
          <SheetDescription>
            Get concise, human-centered insights about your impact data.
          </SheetDescription>
        </SheetHeader>

        <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center gap-3 text-center text-muted-foreground">
              <Sparkles className="h-12 w-12 text-primary/60" />
              <p className="text-sm">Ask anything about your impact metrics, outcomes, or reporting requirements.</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={`${msg.role}-${idx}`}
                className={cn(
                  'rounded-2xl p-4 text-sm leading-relaxed shadow-sm transition',
                  msg.role === 'user'
                    ? 'ml-auto max-w-[80%] bg-primary text-primary-foreground'
                    : 'mr-auto max-w-[85%] border border-primary/10 bg-background/70 gradient-ai'
                )}
              >
                {msg.content}
              </div>
            ))
          )}

          {isLoading && (
            <div className="mr-auto flex max-w-[85%] items-center gap-3 rounded-2xl border border-primary/20 bg-background/80 px-4 py-3 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              Generating an insight…
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="space-y-4 border-t border-border px-6 py-5">
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
            disabled={isLoading}
            className="min-h-[100px] resize-none"
          />
          <Button onClick={handleSend} className="w-full" disabled={!question.trim() || isLoading}>
            {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
            {isLoading ? 'Thinking' : 'Send'}
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
};
