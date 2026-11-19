import React from "react";
import { Link } from "react-router-dom";

export default function NoStudentBanner() {
  return (
    <div className="card">
      <p>No active student selected.</p>
      <Link to="/profile"><button>Go to Student Profile</button></Link>
    </div>
  );
}
