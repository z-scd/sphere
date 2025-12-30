# Sphere

An AI-powered teaching and learning companion designed for job and academic preparation, with specialized support for Bangladesh's National Curriculum and Textbook Board (NCTB) materials.

## Features

- **RAG (Retrieval Augmented Generation)**: Intelligent document processing and question-answering system
- **NCTB Book Support**: Specialized support for Class 9-10 textbooks from Bangladesh's NCTB curriculum
- **Notebook Integration**: Upload and query your own educational documents
- **Multi-language Support**: Answers in Bengali or English based on the source material
- **FastAPI Backend**: Robust REST API for document processing and queries
- **Vector Search**: FAISS-based semantic search for accurate document retrieval

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LangChain**: LLM orchestration and document processing
- **FAISS**: Vector similarity search
- **OpenRouter API**: LLM integration
- **Sentence Transformers**: Text embeddings
- **PyPDF2**: PDF document processing

### Frontend
- **Next.js**: React framework
- **TypeScript**: Type-safe development
- **Clerk**: Authentication
- **Arcjet**: Security

## Project Structure

```
sphere/
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── api/          # API routes
│   │   │   ├── notebook.py
│   │   │   ├── class_9_10.py
│   │   │   └── router.py
│   │   ├── services/     # Business logic
│   │   │   ├── document_processor.py
│   │   │   ├── vector_store.py
│   │   │   ├── llm_service.py
│   │   │   ├── notebook.py
│   │   │   └── class_9_10.py
│   │   ├── models/       # Data models and schemas
│   │   ├── data/         # Documents and vector indexes (gitignored)
│   │   └── main.py       # FastAPI application entry point
│   └── requirements.txt
├── src/                  # Next.js frontend
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- OpenRouter API key (for LLM services)

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the backend directory:**
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=openai/gpt-oss-120b:free
   ```

5. **Run the FastAPI server:**
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

2. **Set up environment variables:**
   Create a `.env.local` file with your configuration:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

## API Endpoints

### Notebook Service
- `POST /api/v1/notebook/upload` - Upload and process documents
- `POST /api/v1/notebook/query` - Query uploaded documents
- `GET /api/v1/notebook/documents` - List uploaded documents

### Class 9-10 Service
- `POST /api/v1/class-9-10/query` - Query NCTB Class 9-10 textbooks
- `GET /api/v1/class-9-10/documents` - List available textbooks

## Features in Detail

### Document Processing
- Supports PDF, TXT, and MD file formats
- Automatic text extraction and chunking
- Semantic embedding generation
- Vector index creation for fast retrieval

### Query System
- Natural language question processing
- Context-aware retrieval from documents
- Multi-language response generation
- Curriculum-aligned answers for NCTB materials

### Vector Store
- FAISS-based similarity search
- Automatic index persistence
- Support for multiple document collections
- Efficient retrieval of relevant document chunks

## Development

### Backend Development
- The backend uses FastAPI with automatic API documentation
- Services are modular and can be extended
- Vector indexes are stored in `backend/app/data/faiss_index/`
- Uploaded documents are stored in `backend/app/data/documents/`

### Adding New Services
1. Create a new service file in `backend/app/services/`
2. Create corresponding API routes in `backend/app/api/`
3. Register the router in `backend/app/api/router.py`

## Environment Variables

### Backend (.env)
- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `OPENROUTER_MODEL`: LLM model to use (default: `openai/gpt-oss-120b:free`)

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL

**⚠️ Important**: Never commit `.env` files to version control. They are already included in `.gitignore`.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

Built with ❤️ for students and educators in Bangladesh
