import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import QAPage from './pages/QAPage'
import RecommendPage from './pages/RecommendPage'
import NotFound from './pages/NotFound'
import ProblemsPage from './pages/_mine/ProblemsPage'
import ProblemsHistory from './pages/_mine/ProblemsHistory'
import ProblemsQuizPage from './pages/ProblemsQuizPage'
import QuizReviewPage from './pages/QuizReviewPage'
import MyAttemptsPage from './pages/MyAttemptsPage'
import ProblemsRetryPage from './pages/ProblemsRetryPage'
import AdminPage from './pages/AdminPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/qa" element={<QAPage />} />
        <Route path="/recommend" element={<RecommendPage />} />
        <Route path="/problems" element={<ProblemsPage />} />
        <Route path="/problems/history" element={<ProblemsHistory />} />
        <Route path="/problems/quiz" element={<ProblemsQuizPage />} />
        <Route path="/problems/quiz/review/:attemptId" element={<QuizReviewPage />} />
        <Route path="/problems/retry/:attemptId" element={<ProblemsRetryPage />} />
        <Route path="/my-attempts" element={<MyAttemptsPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  )
}

export default App

