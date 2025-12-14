import React from "react";

const SignUp = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-5xl bg-white rounded-lg shadow-2xl overflow-hidden flex">
        <div className="w-full md:w-1/2 p-12 bg-gray-50">
          <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
            Sign Up
          </h1>
          <div className="space-y-4">
            <input
              type="text"
              name="username"
              placeholder="Username"
              className="w-full px-6 py-4 bg-blue-50 rounded-xl text-gray-700 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 shadow-sm"
            ></input>

            <input
              type="email"
              name="email"
              placeholder="Email Address"
              className="w-full px-6 py-4 bg-blue-50 rounded-xl text-gray-700 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 shadow-sm"
            ></input>

            <input
              type="password"
              name="password"
              placeholder="Password"
              className="w-full px-6 py-4 bg-blue-50 rounded-xl text-gray-700 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 shadow-sm"
            ></input>

            <input
              type="password"
              name="confirmPassword"
              placeholder="Confirm Password"
              className="w-full px-6 py-4 bg-blue-50 rounded-xl text-gray-700 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 shadow-sm"
            ></input>

            <button className="w-full py-4 bg-gray-800 font-smibold rounded-xl hover:bg-gray-900 tansition-colors text-white cursor-pointer">
              Sign Up
            </button>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm mb-4 text-gray-600">or continue with</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
