import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Video, Rocket, Brain, PenTool, Film, Wand2, Clock, Users, Palette, Megaphone, Edit, CheckCircle, AlertTriangle, Download } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface JobStatus {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  progress: number;
  message: string;
  video_url?: string;
  error?: string;
}

export default function ReelForge() {
  const [formData, setFormData] = useState({
    brand_name: "",
    brand_description: "",
    target_audience: "",
    tone: "professional",
    duration: 30,
    call_to_action: "",
    custom_requirements: ""
  });
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  
  const { toast } = useToast();

  const handleInputChange = (field: string, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const pollJobStatus = async (jobId: string) => {
    try {
      const response = await fetch(`/api/status/${jobId}`);
      if (!response.ok) throw new Error("Failed to check job status");
      
      const status: JobStatus = await response.json();
      setJobStatus(status);
      
      if (status.status === "completed") {
        setIsGenerating(false);
        toast({
          title: "Video Generated!",
          description: "Your AI video ad is ready to download.",
        });
      } else if (status.status === "failed") {
        setIsGenerating(false);
        toast({
          title: "Generation Failed",
          description: status.error || "An error occurred during video generation.",
          variant: "destructive",
        });
      } else if (status.status === "processing" || status.status === "queued") {
        // Continue polling
        setTimeout(() => pollJobStatus(jobId), 2000);
      }
    } catch (error) {
      console.error("Status polling error:", error);
      setIsGenerating(false);
      toast({
        title: "Status Check Failed",
        description: "Unable to check job status. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.brand_name || !formData.brand_description) {
      toast({
        title: "Missing Information",
        description: "Please fill in the brand name and description.",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);
    setJobStatus(null);

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setCurrentJobId(result.job_id);
      
      // Start polling for status
      pollJobStatus(result.job_id);
      
      toast({
        title: "Generation Started",
        description: "Your video is being generated. This may take a few minutes.",
      });

    } catch (error) {
      console.error("Generation failed:", error);
      setIsGenerating(false);
      toast({
        title: "Generation Failed",
        description: error instanceof Error ? error.message : "An unexpected error occurred.",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      brand_name: "",
      brand_description: "",
      target_audience: "",
      tone: "professional",
      duration: 30,
      call_to_action: "",
      custom_requirements: ""
    });
    setJobStatus(null);
    setCurrentJobId(null);
    setIsGenerating(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center space-x-2">
            <Video className="h-8 w-8 text-purple-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              ReelForge
            </h1>
          </div>
          <p className="text-gray-600 text-lg">AI-Powered Video Ad Generation</p>
        </div>

        {/* Main Generation Form */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Wand2 className="h-5 w-5 text-purple-600" />
              <span>Create Your AI Video Ad</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="brand_name" className="flex items-center space-x-1">
                    <span>Brand Name</span>
                    <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="brand_name"
                    placeholder="Enter your brand name"
                    value={formData.brand_name}
                    onChange={(e) => handleInputChange("brand_name", e.target.value)}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="flex items-center space-x-1">
                    <Clock className="h-4 w-4" />
                    <span>Duration</span>
                  </Label>
                  <Select
                    value={formData.duration.toString()}
                    onValueChange={(value) => handleInputChange("duration", parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="15">15 seconds</SelectItem>
                      <SelectItem value="30">30 seconds</SelectItem>
                      <SelectItem value="45">45 seconds</SelectItem>
                      <SelectItem value="60">60 seconds</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="brand_description" className="flex items-center space-x-1">
                  <span>Brand Description</span>
                  <span className="text-red-500">*</span>
                </Label>
                <Textarea
                  id="brand_description"
                  placeholder="Describe your brand, product, or service in detail..."
                  rows={3}
                  value={formData.brand_description}
                  onChange={(e) => handleInputChange("brand_description", e.target.value)}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="flex items-center space-x-1">
                    <Users className="h-4 w-4" />
                    <span>Target Audience</span>
                  </Label>
                  <Input
                    placeholder="e.g., Young professionals, Fitness enthusiasts"
                    value={formData.target_audience}
                    onChange={(e) => handleInputChange("target_audience", e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="flex items-center space-x-1">
                    <Palette className="h-4 w-4" />
                    <span>Tone</span>
                  </Label>
                  <Select
                    value={formData.tone}
                    onValueChange={(value) => handleInputChange("tone", value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="energetic">Energetic</SelectItem>
                      <SelectItem value="friendly">Friendly</SelectItem>
                      <SelectItem value="authoritative">Authoritative</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label className="flex items-center space-x-1">
                  <Megaphone className="h-4 w-4" />
                  <span>Call to Action</span>
                </Label>
                <Input
                  placeholder="e.g., Try it free today!, Visit our website"
                  value={formData.call_to_action}
                  onChange={(e) => handleInputChange("call_to_action", e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label className="flex items-center space-x-1">
                  <Edit className="h-4 w-4" />
                  <span>Custom Requirements</span>
                </Label>
                <Textarea
                  placeholder="Any specific requirements or preferences..."
                  rows={2}
                  value={formData.custom_requirements}
                  onChange={(e) => handleInputChange("custom_requirements", e.target.value)}
                />
              </div>

              <div className="flex justify-center pt-4">
                <Button
                  type="submit"
                  size="lg"
                  disabled={isGenerating}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                >
                  <Rocket className="h-5 w-5 mr-2" />
                  {isGenerating ? "Generating..." : "Generate Video Ad"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Status Card */}
        {jobStatus && (
          <Card className="shadow-lg">
            <CardContent className="pt-6">
              {jobStatus.status === "queued" || jobStatus.status === "processing" ? (
                <div className="text-center space-y-4">
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
                    <span className="font-medium">{jobStatus.message}</span>
                  </div>
                  <Progress value={jobStatus.progress} className="w-full" />
                  <Badge variant="secondary">
                    {jobStatus.progress}% Complete
                  </Badge>
                </div>
              ) : jobStatus.status === "completed" ? (
                <div className="space-y-4">
                  <Alert className="border-green-200 bg-green-50">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <AlertDescription className="text-green-800">
                      Video generated successfully! Your AI-created video ad is ready.
                    </AlertDescription>
                  </Alert>
                  
                  {jobStatus.video_url && (
                    <div className="text-center space-y-4">
                      <video
                        controls
                        autoPlay
                        muted
                        loop
                        className="w-full max-w-md mx-auto rounded-lg shadow-lg"
                      >
                        <source src={jobStatus.video_url} type="video/mp4" />
                        Your browser does not support the video tag.
                      </video>
                      
                      <div className="flex justify-center space-x-4">
                        <Button asChild>
                          <a href={jobStatus.video_url} download>
                            <Download className="h-4 w-4 mr-2" />
                            Download Video
                          </a>
                        </Button>
                        <Button variant="outline" onClick={resetForm}>
                          Create Another
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ) : jobStatus.status === "failed" ? (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    {jobStatus.error || "Video generation failed. Please try again."}
                  </AlertDescription>
                </Alert>
              ) : null}
            </CardContent>
          </Card>
        )}

        {/* How It Works */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="h-5 w-5 text-blue-600" />
              <span>How ReelForge Works</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center space-y-3">
                <div className="mx-auto w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                  <Brain className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-semibold">AI Planning</h3>
                <p className="text-sm text-gray-600">
                  Creates comprehensive creative concepts and detailed execution plans
                </p>
              </div>
              
              <div className="text-center space-y-3">
                <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <PenTool className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-semibold">Script Writing</h3>
                <p className="text-sm text-gray-600">
                  Generates compelling voiceover scripts with visual cues
                </p>
              </div>
              
              <div className="text-center space-y-3">
                <div className="mx-auto w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                  <Film className="h-6 w-6 text-yellow-600" />
                </div>
                <h3 className="font-semibold">Asset Assembly</h3>
                <p className="text-sm text-gray-600">
                  Sources stock footage and generates professional voiceovers
                </p>
              </div>
              
              <div className="text-center space-y-3">
                <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <Wand2 className="h-6 w-6 text-red-600" />
                </div>
                <h3 className="font-semibold">Video Production</h3>
                <p className="text-sm text-gray-600">
                  Assembles everything into a polished video with transitions and effects
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
