import React from 'react'

const Home: React.FC = () => {
    return (
        <div className="py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center">
                    <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
                        <span className="block">AI-Powered</span>
                        <span className="block text-blue-600">Attack Simulation Platform</span>
                    </h1>
                    <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                        A secure educational environment for learning cybersecurity through hands-on attack simulations.
                    </p>
                    <div className="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
                        <div className="rounded-md shadow">
                            <a
                                href="/register"
                                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:text-base"
                            >
                                Get Started
                            </a>
                        </div>
                        <div className="mt-3 sm:mt-0 sm:ml-3">
                            <a
                                href="/labs"
                                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 md:text-base"
                            >
                                Explore Labs
                            </a>
                        </div>
                    </div>
                </div>

                <div className="mt-12">
                    <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                    </svg>
                                </div>
                                <div className="ml-5">
                                    <h3 className="text-lg font-medium text-gray-900">Simulated Attacks</h3>
                                    <p className="mt-2 text-base text-gray-500">Practice security testing in a safe, controlled environment</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                    </svg>
                                </div>
                                <div className="ml-5">
                                    <h3 className="text-lg font-medium text-gray-900">AI Analysis</h3>
                                    <p className="mt-2 text-base text-gray-500">Get expert-level explanations and remediation advice</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-purple-500 rounded-md p-3">
                                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                    </svg>
                                </div>
                                <div className="ml-5">
                                    <h3 className="text-lg font-medium text-gray-900">Real Labs</h3>
                                    <p className="mt-2 text-base text-gray-500">Dockerized vulnerable applications for realistic training</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                    </svg>
                                </div>
                                <div className="ml-5">
                                    <h3 className="text-lg font-medium text-gray-900">Learning Center</h3>
                                    <p className="mt-2 text-base text-gray-500">Comprehensive educational resources on web security</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mt-16">
                    <div className="text-center">
                        <h2 className="text-3xl font-extrabold text-gray-900">How It Works</h2>
                        <p className="mt-4 max-w-2xl text-xl text-gray-500 mx-auto">
                            A simple, five-step process to learn cybersecurity through hands-on experience
                        </p>
                    </div>

                    <div className="mt-12">
                        <div className="flex flex-col md:flex-row items-center justify-between">
                            <div className="flex-1 text-center md:text-left mb-8 md:mb-0">
                                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto md:mx-0 mb-4">
                                    <span className="text-blue-800 font-bold text-lg">1</span>
                                </div>
                                <h3 className="text-xl font-medium text-gray-900 mb-2">Login or Register</h3>
                                <p className="text-gray-600">Create an account to track your progress and access all features</p>
                            </div>

                            <div className="flex-1 text-center md:text-left mb-8 md:mb-0">
                                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto md:mx-0 mb-4">
                                    <span className="text-blue-800 font-bold text-lg">2</span>
                                </div>
                                <h3 className="text-xl font-medium text-gray-900 mb-2">Start a Lab</h3>
                                <p className="text-gray-600">Launch one of our intentionally vulnerable applications in seconds</p>
                            </div>

                            <div className="flex-1 text-center md:text-left mb-8 md:mb-0">
                                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto md:mx-0 mb-4">
                                    <span className="text-blue-800 font-bold text-lg">3</span>
                                </div>
                                <h3 className="text-xl font-medium text-gray-900 mb-2">Choose an Attack</h3>
                                <p className="text-gray-600">Select from common vulnerabilities like SQL Injection, XSS, or IDOR</p>
                            </div>

                            <div className="flex-1 text-center md:text-left mb-8 md:mb-0">
                                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto md:mx-0 mb-4">
                                    <span className="text-blue-800 font-bold text-lg">4</span>
                                </div>
                                <h3 className="text-xl font-medium text-gray-900 mb-2">Run the Attack</h3>
                                <p className="text-gray-600">Execute your payload and watch the results in real-time</p>
                            </div>

                            <div className="flex-1 text-center md:text-left">
                                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto md:mx-0 mb-4">
                                    <span className="text-blue-800 font-bold text-lg">5</span>
                                </div>
                                <h3 className="text-xl font-medium text-gray-900 mb-2">Get AI Analysis</h3>
                                <p className="text-gray-600">Receive expert explanations and secure coding recommendations</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Home