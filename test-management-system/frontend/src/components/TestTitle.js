import React, { Component } from "react";

export default function TestTitle({
                                    activeTestFileName,
                                    hideCoveredTestsButtonValue,
                                    handleHideCoveredTestsButton,
                                    }) {
  return (
    <div className="test-title">
        <p className="fs-5">{activeTestFileName}</p>
        <div className="form-check form-switch">
          <input className="form-check-input" type="checkbox" role="switch" id="flexSwitchCheckDefault" onChange={handleHideCoveredTestsButton} />
          <label className="form-check-label" htmlFor="flexSwitchCheckDefault">Hide auto-test covered tests</label>
        </div>
    </div>
  );
}
