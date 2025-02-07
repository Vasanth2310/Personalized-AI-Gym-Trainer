// PricingScreen.jsx
import React from 'react';
import './PricingScreen.css'; // Import your CSS file

const PricingScreen = () => {
  return (
    <div className="pricing-container">
      <h2>Pricing Plans</h2>

      <div className="plan-card">
        <h3>Free Trial</h3>
        <div className="plan-details">
          <p>Get a taste of AI-powered fitness with our free trial!</p>
          <ul>
            <li>Limited AI posture correction</li>
            <li>Limited exercise counting</li>
          </ul>
        </div>
        <div className="plan-price">Free</div>
        <button>Start Free Trial</button> {/* Or a Link component if you use routing */}
      </div>

      <div className="plan-card">
        <h3>AI Fitness Basic</h3>
        <div className="plan-details">
          <p>Unlock the power of AI for your workouts.</p>
          <ul>
            <li>Unlimited AI posture correction</li>
            <li>Unlimited exercise counting</li>
          </ul>
        </div>
        <div className="plan-price">₹500/month</div>
        <button>Subscribe Now</button>
      </div>

      <div className="plan-card">
        <h3>AI Fitness Premium</h3>
        <div className="plan-details">
          <p>Maximize your fitness journey with AI and GPT.</p>
          <ul>
            <li>Unlimited AI posture correction</li>
            <li>Unlimited exercise counting</li>
            <li>GPT chat for fitness advice and questions</li>
          </ul>
        </div>
        <div className="plan-price">₹800/month</div>
        <button>Subscribe Now</button>
      </div>
    </div>
  );
};

export default PricingScreen;