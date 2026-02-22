'use client';

interface MarkdownMessageProps {
  text: string;
  sender: 'user' | 'agent';
}

export function MarkdownMessage({ text, sender }: MarkdownMessageProps) {
  const formatText = (content: string) => {
    let formatted = content;
    
    // Bold text **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Bullet points • or -
    formatted = formatted.replace(/^[•\-]\s+(.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>\n?)+/g, '<ul class="list-disc ml-4 space-y-1">$&</ul>');
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br/>');
    
    return formatted;
  };

  return (
    <div
      className="text-sm"
      dangerouslySetInnerHTML={{ __html: formatText(text) }}
    />
  );
}
