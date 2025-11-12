import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowLeft, Send, Loader2, Award, TrendingUp } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Progress } from "@/components/ui/progress";

interface SessionData {
  sessionId: string;
  category: string;
  question: string;
  questionNumber: number;
}

export default function Interview() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [session, setSession] = useState<SessionData | null>(null);
  const [answer, setAnswer] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [showEvaluation, setShowEvaluation] = useState(false);
  const [evaluation, setEvaluation] = useState("");
  const [score, setScore] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  // Load session data on mount
  useEffect(() => {
    const sessionData = localStorage.getItem('currentSession');

    if (!sessionData) {
      toast({
        title: "No Active Session",
        description: "Please start an interview first",
        variant: "destructive",
      });
      navigate('/');
      return;
    }

    try {
      const parsed = JSON.parse(sessionData);
      setSession(parsed);
      console.log('📋 Loaded session:', parsed);
    } catch (error) {
      console.error('Failed to parse session data:', error);
      navigate('/');
    }
  }, [navigate, toast]);

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      toast({
        title: "Empty Answer",
        description: "Please write an answer before submitting",
        variant: "destructive",
      });
      return;
    }

    if (!session) return;

    setSubmitting(true);

    try {
      console.log('📤 Submitting answer...');

      const response = await api.submitAnswer({
        session_id: session.sessionId,
        answer: answer.trim()
      });

      console.log('✅ Answer submitted:', response);

      // Show evaluation
      setEvaluation(response.evaluation);
      setScore(response.score);
      setShowEvaluation(true);

      // Clear answer
      setAnswer("");

      // Check if interview continues
      if (response.continue && response.next_question) {
        // Auto-advance after 5 seconds
        setTimeout(() => {
          setSession({
            ...session,
            question: response.next_question!,
            questionNumber: response.question_number
          });
          setShowEvaluation(false);
          setEvaluation("");
          setScore(0);
        }, 5000);
      } else {
        // Interview complete
        setIsComplete(true);
      }

    } catch (error) {
      console.error('❌ Failed to submit answer:', error);
      toast({
        title: "Submission Failed",
        description: "Could not submit your answer. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleBackToHome = () => {
    localStorage.removeItem('currentSession');
    navigate('/');
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-yellow-500";
    return "text-red-500";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return "bg-green-500/10 border-green-500/20";
    if (score >= 60) return "bg-yellow-500/10 border-yellow-500/20";
    return "bg-red-500/10 border-red-500/20";
  };

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (isComplete) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <Card className="max-w-2xl w-full">
          <CardHeader>
            <CardTitle className="text-3xl text-center">
              🎉 Interview Complete!
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center space-y-4">
              <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full ${getScoreBgColor(score)} border-2`}>
                <span className={`text-5xl font-bold ${getScoreColor(score)}`}>
                  {score}
                </span>
              </div>

              <p className="text-xl text-muted-foreground">
                Final Score for {session.category}
              </p>

              <div className="bg-muted/50 rounded-lg p-6 text-left">
                <h3 className="font-semibold mb-2">Evaluation:</h3>
                <p className="text-muted-foreground whitespace-pre-line">
                  {evaluation}
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <Button
                onClick={handleBackToHome}
                variant="outline"
                className="flex-1"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
              <Button
                onClick={() => {
                  localStorage.removeItem('currentSession');
                  window.location.reload();
                }}
                className="flex-1 bg-gradient-primary"
              >
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const progress = (session.questionNumber / 3) * 100;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <nav className="border-b border-border/50 bg-background/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={handleBackToHome}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Exit Interview
          </Button>

          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground capitalize">
              {session.category.replace('_', ' ')}
            </span>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-primary" />
              <span className="text-sm font-semibold">
                Question {session.questionNumber}/3
              </span>
            </div>
          </div>
        </div>
      </nav>

      {/* Progress Bar */}
      <div className="container mx-auto px-6 py-4">
        <Progress value={progress} className="h-2" />
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-12 max-w-4xl">
        {!showEvaluation ? (
          <Card className="border-border/50 bg-muted/30 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl">
                Question {session.questionNumber}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-background/50 rounded-lg p-6">
                <p className="text-lg leading-relaxed">
                  {session.question}
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Your Answer:</label>
                <Textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer here... Be specific and detailed."
                  className="min-h-[300px] resize-none bg-background"
                  disabled={submitting}
                />
                <p className="text-xs text-muted-foreground text-right">
                  {answer.trim().split(/\s+/).filter(Boolean).length} words
                </p>
              </div>

              <Button
                onClick={handleSubmitAnswer}
                disabled={submitting || !answer.trim()}
                className="w-full bg-gradient-primary text-lg py-6"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    Submit Answer
                    <Send className="w-5 h-5 ml-2" />
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-border/50 bg-muted/30 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl flex items-center justify-between">
                <span>Evaluation Results</span>
                <div className={`flex items-center gap-2 ${getScoreColor(score)}`}>
                  <Award className="w-6 h-6" />
                  <span className="text-3xl font-bold">{score}/100</span>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className={`rounded-lg p-6 border-2 ${getScoreBgColor(score)}`}>
                <h3 className="font-semibold mb-3 text-lg">Feedback:</h3>
                <p className="text-muted-foreground whitespace-pre-line leading-relaxed">
                  {evaluation}
                </p>
              </div>

              <div className="bg-primary/10 border border-primary/20 rounded-lg p-4 text-center">
                <p className="text-sm text-muted-foreground">
                  Moving to next question in <span className="font-semibold text-primary">5 seconds</span>...
                </p>
              </div>

              <Button
                onClick={() => {
                  setShowEvaluation(false);
                  setEvaluation("");
                  setScore(0);
                }}
                variant="outline"
                className="w-full"
              >
                Skip Wait & Continue
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
