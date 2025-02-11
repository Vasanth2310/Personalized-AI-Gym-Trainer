import React from 'react';
import './HomeScreen.css';
import logo from '/assets/ai-trainer.png';
import { useNavigate } from 'react-router-dom';

const HomeScreen = () => {
  const navigate = useNavigate();

  const handleTryNowClick = () => {
    navigate('/trainer');
  };

  return (
    <div className="home-container">
      <header className="header">
        <div className="logo-container">
          <img src={logo} alt="FitAI Logo" className="logo" />
        </div>
        <nav className="navigation">
          <a href="/" className="nav-link">Home</a>
          <a href="/pricing" className="nav-link">Pricing</a>
          <a href="/login" className="nav-link login-button">Login</a>
        </nav>
      </header>

      <div className="hero-section">
        <img src="/assets/HomeScreen Img.JPG" alt="Gym Hero" className="hero-image" />
        <div className="hero-content">
          <div className="quote-container">
            <p className="quote">"Unlock Your Fitness Potential with AI"</p>
            <p className="app-description">Personalized fitness, powered by AI.</p>
            <button className="try-now-button" onClick={handleTryNowClick}>
              Try Now
            </button>
          </div>
        </div>
      </div>

      <section className="features-section">
        <div className="feature-card">
          <h2>AI-Powered Workouts</h2>
          <p>Customized workout plans tailored to your goals and fitness level.</p>
        </div>
        <div className="feature-card">
          <h2>Progress Tracking</h2>
          <p>Monitor your fitness journey with detailed performance tracking and analysis.</p>
        </div>
        <div className="feature-card">
          <h2>Exercise Library</h2>
          <p>Access a vast library of exercises with clear instructions and demonstrations.</p>
        </div>
        <div className="feature-card">
          <h2>Personalized Insights</h2>
          <p>Receive data-driven insights to optimize your training and achieve faster results.</p>
        </div>
      </section>

      <section className="feedback-section">
        <h2>What Our Users Say</h2>
        <div className="feedback-card">
          <p>"FitAI has completely transformed my fitness routine. The personalized workouts and progress tracking have helped me stay motivated and achieve my goals faster than ever before." - John Doe</p>
        </div>
        <div className="feedback-card">
          <p>"I love the exercise library! It's so easy to find new workouts and learn proper form. The AI trainer is also incredibly helpful in keeping me on track." - Jane Smith</p>
        </div>
      </section>

      <section className="gpt-model-section">
        <h2>Powered by Advanced GPT Model</h2>
        <p>Our cutting-edge GPT model analyzes your fitness data and generates personalized workout plans, ensuring optimal results and a dynamic training experience.</p>
      </section>

      <footer className="footer">
        <div className="footer-left">
          <p>Contact Us: info@fitai.com | +1-555-123-4567</p>
        </div>
        <div className="footer-right">
          <a href="/terms" className="footer-link">Terms & Conditions</a> |
          <a href="/privacy" className="footer-link">Privacy Policy</a>
        </div>
      </footer>
    </div>
  );
};

export default HomeScreen;