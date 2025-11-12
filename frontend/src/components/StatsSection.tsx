import { TrendingUp, Users, Award, Sparkles } from "lucide-react";

const stats = [
  {
    icon: Users,
    value: "50K+",
    label: "Active Users",
    color: "text-primary",
  },
  {
    icon: Award,
    value: "95%",
    label: "Success Rate",
    color: "text-accent",
  },
  {
    icon: TrendingUp,
    value: "1M+",
    label: "Questions Solved",
    color: "text-secondary",
  },
  {
    icon: Sparkles,
    value: "24/7",
    label: "AI Feedback",
    color: "text-primary",
  },
];

export const StatsSection = () => {
  return (
    <section className="relative py-24 px-6">
      <div className="container mx-auto">
        <div className="grid md:grid-cols-4 gap-8 max-w-5xl mx-auto">
          {stats.map((stat, index) => (
            <div 
              key={index}
              className="text-center group"
            >
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-muted/50 backdrop-blur-sm border border-border/50 mb-4 group-hover:scale-110 transition-transform">
                <stat.icon className={`w-8 h-8 ${stat.color}`} />
              </div>
              <div className="text-4xl font-bold text-gradient mb-2">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
