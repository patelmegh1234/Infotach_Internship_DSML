# AcousticSpace – Frontend

The **AcousticSpace Frontend** is the user interface component of the AcousticSpace project, a deepfake audio detection system that analyzes acoustic and speech-related characteristics to distinguish between **Real** and **AI-generated (Fake)** audio.

The frontend provides an interactive interface for users to upload audio files, interact with the application, and view the results returned by the backend detection system.

---

## 🎯 Project Objective

AcousticSpace aims to detect AI-generated or manipulated audio by analyzing acoustic characteristics such as:

- Room Impulse Response (RIR)
- Reverberation characteristics
- Background acoustic consistency
- Silence and pause patterns
- Spectral characteristics
- Other extracted audio features

The frontend acts as the communication layer between the user and the backend/audio-processing system.

---

## 🖥️ Frontend Responsibilities

The frontend is responsible for:

- Providing an easy-to-use user interface
- Allowing users to upload audio files
- Sending audio data to the backend API
- Displaying processing and prediction status
- Presenting the final detection result
- Providing a clear and interactive user experience
- Handling frontend validation and user interactions
- Supporting visualization of audio-related information where applicable

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| React | Building reusable UI components |
| TypeScript | Type-safe frontend development |
| Vite | Frontend development and build tool |
| HTML5 | Application structure |
| CSS | Styling and layout |
| JavaScript/TypeScript | Application logic |
| REST API | Communication with backend services |

---

## 📁 Project Structure

```text
frontend/
│
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/             # Application pages
│   ├── services/          # API communication
│   ├── assets/            # Images and static assets
│   └── ...                # Other source files
│
├── .env.example           # Example environment configuration
├── .gitignore             # Git ignored files
├── index.html             # Main HTML entry point
├── package.json            # Project dependencies and scripts
├── package-lock.json       # Locked dependency versions
├── tsconfig.json           # TypeScript configuration
├── vite.config.ts          # Vite configuration
└── README.md               # Frontend documentation
