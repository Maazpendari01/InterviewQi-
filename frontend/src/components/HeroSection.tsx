import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export const HeroSection = () => {
  const navigate = useNavigate();
  const [interviewCount, setInterviewCount] = useState(12847);

  useEffect(() => {
    const interval = setInterval(() => {
      setInterviewCount((prev) => prev + Math.floor(Math.random() * 3));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const scrollToInterviewCards = () => {
    const cardsSection = document.querySelector('[data-interview-cards]');
    if (cardsSection) {
      cardsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      {/* Animated Gradient Mesh Background */}
      <div className="absolute inset-0 bg-gradient-mesh opacity-50" />

      {/* Floating Orbs */}
      <div className="absolute top-20 left-10 w-64 h-64 bg-primary/20 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-secondary/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '4s' }} />

      <div className="relative z-10 container mx-auto px-6 text-center">
        {/* Stats Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-muted/50 backdrop-blur-sm border border-border/50 mb-8 animate-fade-in">
          <TrendingUp className="w-4 h-4 text-primary" />
          <span className="text-sm text-muted-foreground">
            <span className="font-semibold text-foreground">{interviewCount.toLocaleString()}</span> interviews completed today
          </span>
          <Sparkles className="w-4 h-4 text-accent" />
        </div>

        {/* Main Headline */}
        <h1 className="text-6xl md:text-8xl font-bold mb-6 animate-pulse-glow">
          <span className="text-gradient">Master Tech</span>
          <br />
          <span className="text-gradient">Interviews</span>
        </h1>

        {/* Subheadline */}
        <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto">
          Get <span className="text-accent font-semibold">AI-Powered Feedback</span> in Real-Time
          <br />
          Practice coding, system design, and behavioral questions
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <Button
            size="lg"
            onClick={scrollToInterviewCards}
            className="bg-gradient-primary text-primary-foreground border-0 hover:opacity-90 transition-opacity text-lg px-8 py-6 group"
          >
            Start Practice Free
            <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate('/dashboard')}
            className="border-border/50 bg-muted/30 backdrop-blur-sm hover:bg-muted/50 text-lg px-8 py-6"
          >
            View Dashboard
          </Button>
        </div>

        {/* Trust Indicators */}
        <div className="flex items-center justify-center gap-8 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            <span>1000+ Questions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse" style={{ animationDelay: '1s' }} />
            <span>Real Interview Format</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-secondary rounded-full animate-pulse" style={{ animationDelay: '2s' }} />
            <span>Instant AI Feedback</span>
          </div>
        </div>
      </div>
    </section>
  );
};
