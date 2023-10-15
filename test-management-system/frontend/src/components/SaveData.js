import React, { Component } from "react";

export default function SaveData(props) {
  return (
    <div className="save-data">
      <button
        type="button"
        className="btn btn-primary btn-lg"
        onClick={() => props.saveAllTests()}
      >
        Save all
      </button>
    </div>
  );
}
