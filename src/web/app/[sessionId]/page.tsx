import { ChatInterface } from "@/components/chat";

interface PageProps {
  params: Promise<{
    sessionId: string;
  }>;
}

export default async function SessionPage({ params }: PageProps) {
  const { sessionId } = await params;
  return (
    <div className="h-screen">
      <ChatInterface sessionId={sessionId} />
    </div>
  );
}
