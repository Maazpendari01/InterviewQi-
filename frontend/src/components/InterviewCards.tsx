import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Code, Network, MessageSquare, ArrowRight, Zap, Target, Brain } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const interviewTypes = [
  {
    icon: Code,
    title: "Coding Questions",
    description: "Practice algorithms, data structures, and problem-solving",
    stats: "500+ Questions",
    difficulty: "Easy → Hard",
    color: "from-primary to-primary/50",
    iconColor: "text-primary",
    category: "coding" as const,
  },
  {
    icon: Network,
    title: "System Design",
    description: "Master scalable architecture and design patterns",
    stats: "200+ Scenarios",
    difficulty: "Medium → Expert",
    color: "from-accent to-accent/50",
    iconColor: "text-accent",
    category: "system_design" as const,
  },
  {
    icon: MessageSquare,
    title: "Behavioral",
    description: "Ace your soft skills and communication scenarios",
    stats: "300+ Questions",
    difficulty: "All Levels",
    color: "from-secondary to-secondary/50",
    iconColor: "text-secondary",
    category: "behavioral" as const,
  },
];

export const InterviewCards = () => {
  const [loading, setLoading] = useState<string | null>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleStartInterview = async (category: 'coding' | 'system_design' | 'behavioral', title: string) => {
    setLoading(category);

    try {
      console.log(`🚀 Starting ${category} interview...`);

      const response = await api.startInterview({
        category: category,
        difficulty: 'medium'
      });

      console.log('✅ Interview started:', response);

      // Store session data in localStorage for the interview page
      localStorage.setItem('currentSession', JSON.stringify({
        sessionId: response.session_id,
        category: response.category,
        question: response.question,
        questionNumber: response.question_number
      }));

      toast({
        title: "Interview Started! 🎯",
        description: `Get ready for ${title}`,
      });

      // Navigate to interview page (we'll create this route)
      navigate('/interview');

    } catch (error) {
      console.error('❌ Failed to start interview:', error);

      toast({
        title: "Connection Error",
        description: "Could not connect to backend. Make sure it's running on port 8000.",
        variant: "destructive",
      });
    } finally {
      setLoading(null);
    }
  };

  return (
    <section className="relative py-24 px-6">
      <div className="container mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="text-gradient">Choose Your Path</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Practice with real interview questions powered by AI feedback
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {interviewTypes.map((type, index) => (
            <Card
              key={index}
              className="group relative overflow-hidden bg-muted/30 backdrop-blur-sm border-border/50 hover:border-border transition-all duration-300 hover:scale-105 hover:shadow-2xl"
            >
              {/* Gradient Overlay */}
              <div className={`absolute inset-0 bg-gradient-to-br ${type.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />

              <CardHeader className="relative">
                <div className={`w-12 h-12 rounded-xl bg-muted flex items-center justify-center mb-4 group-hover:scale-110 transition-transform ${type.iconColor}`}>
                  <type.icon className="w-6 h-6" />
                </div>
                <CardTitle className="text-2xl">{type.title}</CardTitle>
                <CardDescription className="text-base">{type.description}</CardDescription>
              </CardHeader>

              <CardContent className="relative space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2 text-muted-foreground">
                    <Target className="w-4 h-4" />
                    {type.stats}
                  </span>
                  <span className="flex items-center gap-2 text-muted-foreground">
                    <Zap className="w-4 h-4" />
                    {type.difficulty}
                  </span>
                </div>

                <Button
                  onClick={() => handleStartInterview(type.category, type.title)}
                  disabled={loading !== null}
                  className="w-full group/btn bg-gradient-primary text-primary-foreground border-0 hover:opacity-90 transition-opacity disabled:opacity-50"
                >
                  {loading === type.category ? (
                    <>
                      <span className="animate-pulse">Starting...</span>
                    </>
                  ) : (
                    <>
                      Start Practice
                      <ArrowRight className="ml-2 w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                    </>
                  )}
                </Button>

                <div className="pt-2 flex items-center justify-center gap-2 text-xs text-muted-foreground">
                  <Brain className="w-3 h-3" />
                  <span>AI-powered feedback included</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
