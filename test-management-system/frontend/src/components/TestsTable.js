import React, { Component } from "react";
import SaveData from "./SaveData";
import EditFileModal from "./EditFileModal";

import { useState } from 'react';

export default function ProjectTittle({
  tests,
  handleTestStatusUpdate,
  getTestData,
  handleTestCommentUpdate,
  saveAllTestsFunction,
  activeVersionId,
  activeTestFileId,
  activeTestFileName,
  openShowTestModal,
  hideCoveredTestsButtonValue
}) {

  if (tests.length == 0) {
    return <span>No tests</span>;
  }

  const [openedStepsTests, setOpenedStepsTests] = useState([]);
  let tableRows = [];
  let testNumber = 0;

  let openSteps = (testId) => {
        let NewOpenedStepsTests = openedStepsTests.slice();
        let index = NewOpenedStepsTests.indexOf(testId);
        if (index > -1) {
          NewOpenedStepsTests.splice(index, 1);
        } else {
            NewOpenedStepsTests.push(testId);
        }
        setOpenedStepsTests(NewOpenedStepsTests);
  }

  tests.sort((a, b) => {return b["start_line"] - a["start_line"]})
  for (let testIndex = tests.length - 1; testIndex >= 0; testIndex--) {
    const test = tests[testIndex];
    if (hideCoveredTestsButtonValue && (test["covered_steps_amount"] == test["steps_amount"])){
        continue
    }


    const testState = getTestData(test.id);

    let passedButton = (
      <button
        type="button"
        className="btn btn-outline-success"
        onClick={() => handleTestStatusUpdate(test.id, "1")}
      >
        Passed
      </button>
    );
    let failedButton = (
      <button
        type="button"
        className="btn btn-outline-danger"
        onClick={() => handleTestStatusUpdate(test.id, "2")}
      >
        Failed
      </button>
    );

    if (testState.status == 1) {
      passedButton = (
        <button
          type="button"
          className="btn btn-success"
          onClick={() => handleTestStatusUpdate(test.id, "1")}
        >
          Passed
        </button>
      );
      failedButton = (
        <button
          type="button"
          className="btn btn-outline-danger"
          onClick={() => handleTestStatusUpdate(test.id, "2")}
        >
          Failed
        </button>
      );
    }

    if (testState.status == 2) {
      passedButton = (
        <button
          type="button"
          className="btn btn-outline-success"
          onClick={() => handleTestStatusUpdate(test.id, "1")}
        >
          Passed
        </button>
      );
      failedButton = (
        <button
          type="button"
          className="btn btn-danger"
          onClick={() => handleTestStatusUpdate(test.id, "2")}
        >
          Failed
        </button>
      );
    }

    let testComment = testState.comment;
    if (testComment === null) {
      testComment = "";
    }
    testNumber++;
    let testName = test.test_name;
    let steps = [];
    for (let stepIndex = 0; stepIndex < test.steps.length; stepIndex++) {
      let step = test.steps[stepIndex];
      if (step.has_auto_test) {
        steps.push(
          <li key={stepIndex}>
            <p className="text-success test-step" dropdown-item="true">{step.text}</p>
          </li>
        );
      } else {
        steps.push(
          <li key={stepIndex}>
            <p className="text-secondary test-step" dropdown-item="true">{step.text}</p>
          </li>
        );
      }
    }
    let autoTestCoveredSteps = "";
    if (test.steps_amount > 0) {
      autoTestCoveredSteps += (
        (test["covered_steps_amount"] / test["steps_amount"]) *
        100
      ).toFixed(2);
    } else {
      autoTestCoveredSteps += "-";
    }

    let autoTestCoveredOutcomeSteps = "";
    let dropDownId = "dropdownMenuButton" + test.id;

    if (test.outcome_steps_amount > 0) {
      autoTestCoveredOutcomeSteps += (
        (test["covered_outcome_steps_amount"] / test["outcome_steps_amount"]) *
        100
      ).toFixed(2);
    } else {
      autoTestCoveredOutcomeSteps += "-";
    }
    let stepsElements = undefined;
    steps.push(
      <li key={steps.length + 1}>
        <div className="expand-container">
            <p><a type="button"
                  className="link-opacity-100-hover test-step"
                  data-bs-toggle="modal"
                  data-bs-target="#showTestTextModal"
                  onClick={() => openShowTestModal(test.id)}
                  >Expand</a></p>
        </div>
      </li>
      );
    if (openedStepsTests.includes(test.id)) {
        stepsElements = (
        <div className="steps-opened">
            <ul className="steps-list">
              {steps}
            </ul>
        </div>
        )
    }
    else {
     stepsElements = (
        <div className="steps-closed">
            <ul className="steps-list">
              {steps}
            </ul>
        </div>
        )
    }

    let textAreaId = "FormControlTextarea" + test.id;
    tableRows.push(
      <tr key={test.id}>
        <th scope="row">{testNumber}</th>
        <td>
          <div className="dropdown dropdown-container">
            <div
              className="dropdown-toggle dropdown-test"
              type="button"
              onClick={() => openSteps(test.id)}
            >
              {testName}
            </div>
              {stepsElements}
          </div>
        </td>
        <td className="no-break-cells">
          {autoTestCoveredSteps} % / {autoTestCoveredOutcomeSteps} %
        </td>
        <td className="no-break-cells">{passedButton}</td>

        <td className="no-break-cells">{failedButton}</td>

        <td className="textare-cell">
          <textarea
            className="form-control error-textarea"
            value={testComment}
            id={textAreaId}
            rows="3"
            onChange={(e) => handleTestCommentUpdate(test.id, e)}
          ></textarea>
        </td>
      </tr>
    );
  }
  return (
    <div className="table-container">
      <table className="table table-bordered border-primary tests-table">
        <thead>
          <tr>
            <th scope="col" className="number-col">#</th>
            <th scope="col" className="col-md-3">Test name</th>
            <th scope="col" className="col-md-2">
              Autotest covered
              <img
                src="/static/icons/tool-tip.png"
                type="button"
                rel="tooltip"
                data-toggle="tooltip"
                data-placement="top"
                title="Steps covered % /Outcome steps covered %"
              />
            </th>
            <th scope="col" className="col-md-1">Passed</th>
            <th scope="col" className="col-md-1">Failed</th>
            <th scope="col" className="col-md-4">Comment</th>
          </tr>
        </thead>
        <tbody>{tableRows}</tbody>
      </table>
      <div className="file-actions">
            <SaveData saveAllTests={saveAllTestsFunction} />
            <EditFileModal
                activeVersionId={activeVersionId}
                activeTestFileId={activeTestFileId}
                activeTestFileName={activeTestFileName}
            />
      </div>
    </div>
  );
}
