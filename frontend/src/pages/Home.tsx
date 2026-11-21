import React from 'react'
import { Link } from 'react-router-dom'

const Home: React.FC = () => {
    return (
        <div className="home-page">
            <div className="hero-section">
                <div className="hero-content">
                    <h1 className="hero-title">
                        <span className="hero-highlight">AI-Powered</span>
                        <span className="hero-subtitle-text">Attack Simulation Platform</span>
                    </h1>
                    <p className="hero-description">
                        A secure educational environment for learning cybersecurity through hands-on attack simulations.
                    </p>
                    <div className="hero-actions">
                        <div className="hero-btn-wrap">
                            <Link
                                to={localStorage.getItem('auth') ? '/dashboard' : '/register'}
                              className="btn btn-primary btn-lg"
                            >
                              Get Started
                            </Link>
                        </div>
                        <div className="hero-btn-wrap">
                            <Link
                                to="/labs"
                                className="btn btn-outline btn-lg"
                            >
                                Explore Labs
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            <div className="features-section">
                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon-wrap">
                            <svg className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                        </div>
                        <div className="feature-info">
                            <h3 className="feature-title">Simulated Attacks</h3>
                            <p className="feature-desc">Practice security testing in a safe, controlled environment</p>
                        </div>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon-wrap">
                            <svg className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                        </div>
                        <div className="feature-info">
                            <h3 className="feature-title">AI Analysis</h3>
                            <p className="feature-desc">Get expert-level explanations and remediation advice</p>
                        </div>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon-wrap">
                            <svg className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                        </div>
                        <div className="feature-info">
                            <h3 className="feature-title">Live Labs</h3>
                            <p className="feature-desc">Active cloud-hosted vulnerable applications for realistic training</p>
                        </div>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon-wrap">
                            <svg className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                        </div>
                        <div className="feature-info">
                            <h3 className="feature-title">Learning Center</h3>
                            <p className="feature-desc">Comprehensive educational resources on web security</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="how-it-works-section">
                <div className="section-header">
                    <h2 className="section-title">How It Works</h2>
                    <p className="section-subtitle">
                        A simple, five-step process to learn cybersecurity through hands-on experience
                    </p>
                </div>

                <div className="steps-container">
                    <div className="steps-grid">
                        <div className="step-card">
                            <div className="step-number-wrap">
                                <span className="step-number">1</span>
                            </div>
                            <h3 className="step-title">Login or Register</h3>
                            <p className="step-desc">Create an account to track your progress and access all features</p>
                        </div>

                        <div className="step-card">
                            <div className="step-number-wrap">
                                <span className="step-number">2</span>
                            </div>
                            <h3 className="step-title">Select a Lab</h3>
                            <p className="step-desc">Choose one of our active vulnerable applications</p>
                        </div>

                        <div className="step-card">
                            <div className="step-number-wrap">
                                <span className="step-number">3</span>
                            </div>
                            <h3 className="step-title">Choose an Attack</h3>
                            <p className="step-desc">Select from common vulnerabilities like SQL Injection, XSS, or IDOR</p>
                        </div>

                        <div className="step-card">
                            <div className="step-number-wrap">
                                <span className="step-number">4</span>
                            </div>
                            <h3 className="step-title">Run the Attack</h3>
                            <p className="step-desc">Execute your payload and watch the results in real-time</p>
                        </div>

                        <div className="step-card">
                            <div className="step-number-wrap">
                                <span className="step-number">5</span>
                            </div>
                            <h3 className="step-title">Get AI Analysis</h3>
                            <p className="step-desc">Receive expert explanations and secure coding recommendations</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Home
