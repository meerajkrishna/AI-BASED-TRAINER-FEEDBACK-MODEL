// Learning Module Types

export interface Topic {
	id: number;
	name: string;
	definition: string;
	description: string;
	videoUrl: string;
	level: "Beginner" | "Intermediate" | "Advanced" | "Hard";
	icon: string;
	category?: string;
	categoryLabel?: string;
	hasQuiz?: boolean;
}

export interface Question {
	id: number;
	topicId: number;
	text: string;
	options: string[];
	correctAnswer: string;
}

export interface QuizAttempt {
	topicId: number;
	responses: QuestionResponse[];
	score: number;
	totalQuestions: number;
	timeSpent: number;
	completedAt: string;
}

export interface QuestionResponse {
	questionId: number;
	selectedAnswer: string;
	isCorrect: boolean;
	timeSpent: number;
}

export interface UserProgress {
	topicId: number;
	completed: boolean;
	bestScore: number;
	attempts: number;
	lastAttemptAt: string | null;
}
