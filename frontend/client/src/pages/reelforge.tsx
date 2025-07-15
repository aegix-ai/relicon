import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";

export default function ReelForge() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [brandName, setBrandName] = useState("");
  const [brandDescription, setBrandDescription] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const { toast } = useToast();

  const handleGenerate = async () => {
    if (!brandName.trim() || !brandDescription.trim()) {
      toast({
        title: "Error",
        description: "Please fill in both brand name and description",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);
    try {
      const response = await apiRequest({
        url: "/api/generate-video",
        method: "POST",
        data: {
          brand_name: brandName,
          brand_description: brandDescription,
        },
      });

      if (response.video_url) {
        setVideoUrl(response.video_url);
        toast({
          title: "Success",
          description: "Video generated successfully!",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate video. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">ReelForge AI</h1>
          <p className="text-gray-300">Create professional video ads with AI</p>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Generate Video Ad</CardTitle>
            <CardDescription>
              Enter your brand information to create a custom video advertisement
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="brand-name">Brand Name</Label>
              <Input
                id="brand-name"
                placeholder="Enter your brand name"
                value={brandName}
                onChange={(e) => setBrandName(e.target.value)}
                disabled={isGenerating}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="brand-description">Brand Description</Label>
              <Textarea
                id="brand-description"
                placeholder="Describe your brand, products, and target audience"
                value={brandDescription}
                onChange={(e) => setBrandDescription(e.target.value)}
                disabled={isGenerating}
                rows={4}
              />
            </div>

            <Button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full"
            >
              {isGenerating ? "Generating..." : "Generate Video"}
            </Button>
          </CardContent>
        </Card>

        {videoUrl && (
          <Card>
            <CardHeader>
              <CardTitle>Generated Video</CardTitle>
              <CardDescription>Your AI-generated video advertisement</CardDescription>
            </CardHeader>
            <CardContent>
              <video
                controls
                className="w-full rounded-lg"
                src={videoUrl}
              >
                Your browser does not support the video tag.
              </video>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}