import type { ReactNode } from 'react';

interface ResultCardProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export default function ResultCard({ title, children, className = '' }: ResultCardProps) {
  return (
    <div className={`result-card fade-in ${className}`}>
      <h3 className="result-card__title">{title}</h3>
      <div className="result-card__content">{children}</div>
    </div>
  );
}

