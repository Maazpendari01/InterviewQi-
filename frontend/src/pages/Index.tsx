import { Navigation } from "@/components/Navigation";
import { HeroSection } from "@/components/HeroSection";
import { InterviewCards } from "@/components/InterviewCards";
import { StatsSection } from "@/components/StatsSection";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <HeroSection />
      <div data-interview-cards>
        <InterviewCards />
      </div>
      <StatsSection />
    </div>
  );
};

export default Index;
