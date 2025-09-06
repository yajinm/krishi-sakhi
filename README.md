Krishi Sakhi: AI-Powered Personal Farming Assistant :-

This project is a prototype for the Krishi Sakhi (Farmer's Friend) backend, an AI-powered personal assistant designed to bridge the information gap for Kerala farmers. 
It addresses challenges like language barriers and limited digital access by providing a conversational interface in their local dialect. 
The goal is to deliver a complete, scalable, and secure solution for the Smart India Hackathon.

Core Functionality :-

The backend is built as a robust, containerized FastAPI application handling the full lifecycle of a farmer's interaction.

* Multilingual Conversational AI: The system uses Google Gemini for advanced, multilingual Natural Language Understanding (NLU) to interpret farmer queries and synthesize advice.
* Data-Driven Insights: The system logs activities from conversational text and uses a personalized advisory engine to generate proactive alerts. This is powered by a searchable knowledge base built with Google Firestore.
* Proactive Communication: Advisories and alerts are instantly pushed to the farmer's device using Firestore's real-time capabilities, ensuring timely information.

Technology Stack :-

* Backend: FastAPI (Python). A high-performance, asynchronous framework ideal for handling concurrent API calls and integrating AI services without blocking. Its native Pydantic integration ensures our API is robust and type-safe.
* Frontend: React (with Vite). Chosen for its component-based architecture, allowing us to build a fast, modern, and highly interactive user interface. Perfect for the app's core chat and dashboard experience.
* Database: Google Firestore (NoSQL). Selected for its real-time capabilities and effortless scalability. Firestore's listeners are crucial for instantly pushing new advisories and alerts to the farmer's device.AI Engine: Google Gemini. Used for its advanced, multilingual Natural Language Understanding (NLU) to interpret farmer queries in Malayalam. It extracts structured data from conversational text and synthesizes it with external data to generate personalized advice.

Getting Started :-

1. Prerequisites: Ensure you have a Google Cloud account and the Firebase CLI installed.
2. Set Up Project: Create a new Google Cloud project, then enable Firebase, Firestore, and the Gemini API.
3. Configure Credentials: Set up authentication by either using a Service Account key for server-side access or by configuring Firebase Authentication for the frontend.

Robustness & Compliance

The project includes a comprehensive test suite with pytest and httpx to ensure high code quality. Security is a priority, with Firebase Authentication providing secure user management.
The system is also designed for adherence to the India DPDP Act through features like data export and deletion endpoints.
