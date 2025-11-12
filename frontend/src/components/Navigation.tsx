import { Brain, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import logo from "@/assets/logo.png";

export const Navigation = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-background/50 border-b border-border/50">
      <div className="container mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img src={logo} alt="InterviewIQ" className="w-10 h-10 animate-pulse-glow" />
          <div className="flex flex-col">
            <span className="text-xl font-bold text-gradient">InterviewIQ</span>
            <span className="text-xs text-muted-foreground">AI Interview Practice</span>
          </div>
        </div>
        
        <div className="hidden md:flex items-center gap-6">
          <a href="#features" className="text-sm text-foreground/80 hover:text-foreground transition-colors">
            Features
          </a>
          <a href="#pricing" className="text-sm text-foreground/80 hover:text-foreground transition-colors">
            Pricing
          </a>
          <a href="#about" className="text-sm text-foreground/80 hover:text-foreground transition-colors">
            About
          </a>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" className="text-foreground/80 hover:text-foreground">
            Sign In
          </Button>
          <Button size="sm" className="bg-gradient-primary text-primary-foreground border-0 hover:opacity-90 transition-opacity">
            Get Started
          </Button>
        </div>
      </div>
    </nav>
  );
};
