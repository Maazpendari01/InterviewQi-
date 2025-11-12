import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  TrendingUp,
  Award,
  Target,
  Code,
  Network,
  MessageSquare,
  Calendar,
  BarChart3
} from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Progress } from "@/components/ui/progress";

interface SessionData {
  session_id: string;
  category: string;
  started_at: string;
  completed: boolean;
  average_score: number;
  total_questions: number;
}

interface PlatformStats {
  total_sessions: number;
  completed_sessions: number;
  completion_rate: number;
  average_score: number;
  by_category: Record<string, number>;
}

interface LeaderboardEntry {
  rank: number;
  session_id: string;
  category: string;
  score: number;
  questions: number;
  date: string;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [recentSessions, setRecentSessions] = useState<SessionData[]>([]);
  const [platformStats, setPlatformStats] = useState<PlatformStats | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load recent sessions
      const sessionsData = await api.getRecentSessions(10);
      setRecentSessions(sessionsData.sessions);

      // Load platform stats
      const stats = await api.getPlatformStats();
      setPlatformStats(stats);

      // Load leaderboard
      const leaderboardData = await api.getLeaderboard(undefined, 5);
      setLeaderboard(leaderboardData.leaderboard);

    } catch (error) {
      console.error('Failed to load dashboard:', error);
      toast({
        title: "Failed to load data",
        description: "Could not connect to backend. Make sure it's running.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'coding': return Code;
      case 'system_design': return Network;
      case 'behavioral': return MessageSquare;
      default: return Target;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'coding': return 'text-primary';
      case 'system_design': return 'text-accent';
      case 'behavioral': return 'text-secondary';
      default: return 'text-muted-foreground';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCategory = (category: string) => {
    return category.replace('_', ' ').split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <nav className="border-b border-border/50 bg-background/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Button>
            <h1 className="text-2xl font-bold text-gradient">Dashboard</h1>
          </div>

          <Button
            onClick={() => navigate('/')}
            className="bg-gradient-primary"
          >
            Start New Interview
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-12">
        {/* Stats Overview */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <Card className="border-border/50 bg-muted/30 backdrop-blur-sm">
            <CardHeader className="pb-3">
              <CardDescription className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-primary" />
                Total Sessions
              </CardDescription>
              <CardTitle className="text-3xl">
                {platformStats?.total_sessions || 0}
              </CardTitle>
            </CardHeader>
          </Card>

          <Card className="border-border/50 bg-muted/30 backdrop-blur-sm">
            <CardHeader className="pb-3">
              <CardDescription className="flex items-center gap-2">
                <Award className="w-4 h-4 text-accent" />
                Completed
              </CardDescription>
              <CardTitle className="text-3xl">
                {platformStats?.completed_sessions || 0}
              </CardTitle>
            </CardHeader>
          </Card>

          <Card className="border-border/50 bg-muted/30 backdrop-blur-sm">
            <CardHeader className="pb-3">
              <CardDescription className="flex items-center gap-2">
                <Target className="w-4 h-4 text-secondary" />
                Completion Rate
              </CardDescription>
              <CardTitle className="text-3xl">
                {platformStats?.completion_rate || 0}%
              </CardTitle>
            </CardHeader>
          </Card>

          <Card className="border-border/50 bg-muted/30 backdrop-blur-sm">
            <CardHeader className="pb-3">
              <CardDescription className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-primary" />
                Avg Score
              </CardDescription>
              <CardTitle className="text-3xl">
                {platformStats?.average_score?.toFixed(0) || 0}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Recent Sessions */}
          <div className="md:col-span-2 space-y-6">
            <Card className="border-border/50 bg-muted/30 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Recent Interview Sessions
                </CardTitle>
                <CardDescription>
                  Your latest interview attempts
                </CardDescription>
              </CardHeader>
              <CardContent>
                {recentSessions.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No sessions yet. Start your first interview!</p>
                    <Button
                      onClick={() => navigate('/')}
                      className="mt-4"
                      variant="outline"
                    >
                      Start Interview
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {recentSessions.map((session) => {
                      const CategoryIcon = getCategoryIcon(session.category);
                      const categoryColor = getCategoryColor(session.category);
                      const scoreColor = getScoreColor(session.average_score || 0);

                      return (
                        <div
                          key={session.session_id}
                          className="flex items-center justify-between p-4 rounded-lg bg-background/50 border border-border/50 hover:border-border transition-colors"
                        >
                          <div className="flex items-center gap-4 flex-1">
                            <div className={`p-3 rounded-lg bg-muted ${categoryColor}`}>
                              <CategoryIcon className="w-5 h-5" />
                            </div>

                            <div className="flex-1">
                              <h3 className="font-semibold">
                                {formatCategory(session.category)}
                              </h3>
                              <p className="text-sm text-muted-foreground">
                                {formatDate(session.started_at)}
                              </p>
                            </div>

                            <div className="text-right">
                              <div className={`text-2xl font-bold ${scoreColor}`}>
                                {session.average_score?.toFixed(0) || '--'}
                              </div>
                              <p className="text-xs text-muted-foreground">
                                {session.total_questions} questions
                              </p>
                            </div>

                            <div>
                              {session.completed ? (
                                <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-500 text-xs font-semibold">
                                  Completed
                                </span>
                              ) : (
                                <span className="px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-500 text-xs font-semibold">
                                  In Progress
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Category Breakdown */}
            {platformStats && Object.keys(platformStats.by_category).length > 0 && (
              <Card className="border-border/50 bg-muted/30 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle>Sessions by Category</CardTitle>
                  <CardDescription>Distribution across interview types</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {Object.entries(platformStats.by_category).map(([category, count]) => {
                    const CategoryIcon = getCategoryIcon(category);
                    const total = platformStats.total_sessions;
                    const percentage = total > 0 ? (count / total) * 100 : 0;

                    return (
                      <div key={category} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <CategoryIcon className={`w-4 h-4 ${getCategoryColor(category)}`} />
                            <span className="font-medium">{formatCategory(category)}</span>
                          </div>
                          <span className="text-sm text-muted-foreground">
                            {count} ({percentage.toFixed(0)}%)
                          </span>
                        </div>
                        <Progress value={percentage} className="h-2" />
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Leaderboard */}
          <div>
            <Card className="border-border/50 bg-muted/30 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-accent" />
                  Top Performers
                </CardTitle>
                <CardDescription>
                  Highest scoring sessions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {leaderboard.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    No data yet
                  </div>
                ) : (
                  <div className="space-y-3">
                    {leaderboard.map((entry) => (
                      <div
                        key={entry.session_id}
                        className="flex items-center gap-3 p-3 rounded-lg bg-background/50"
                      >
                        <div className={`flex items-center justify-center w-8 h-8 rounded-full font-bold ${
                          entry.rank === 1 ? 'bg-yellow-500/20 text-yellow-500' :
                          entry.rank === 2 ? 'bg-gray-400/20 text-gray-400' :
                          entry.rank === 3 ? 'bg-orange-500/20 text-orange-500' :
                          'bg-muted text-muted-foreground'
                        }`}>
                          {entry.rank}
                        </div>

                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate text-sm">
                            {formatCategory(entry.category)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {entry.questions} questions
                          </p>
                        </div>

                        <div className={`text-xl font-bold ${getScoreColor(entry.score)}`}>
                          {entry.score}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="border-border/50 bg-muted/30 backdrop-blur-sm mt-6">
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  onClick={() => navigate('/')}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Code className="w-4 h-4 mr-2" />
                  Practice Coding
                </Button>
                <Button
                  onClick={() => navigate('/')}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Network className="w-4 h-4 mr-2" />
                  System Design
                </Button>
                <Button
                  onClick={() => navigate('/')}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Behavioral
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
