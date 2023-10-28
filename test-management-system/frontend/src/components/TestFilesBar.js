import React, { Component } from "react";
import TestTable from "./TestsTable";
import AddFileModal from "./AddFileModal";


export default function TestFilesBar({
  activeVersionId,
  activeTestFileId,
  testFiles,
  onTestFileClick,
  handleTestStatusUpdate,
  handleTestCommentUpdate,
  getTestData,
  saveAllTests,
  openShowTestModal
}) {
  if (testFiles.length == 0) {
    return <span>No test files</span>;
  }

  let maxTestFileLength = 20;
  let getTestFileWithCoverageElement = (testFile, coverage) => {
    let coverageLabel = coverage.toFixed(2);
    coverageLabel = coverageLabel.toString() + " %";
    if (testFile.length > maxTestFileLength) {
        testFile = testFile.slice(0, maxTestFileLength) + "...";
    }
    return (
    <div className="test-files-label-container">
        <div className="test-files--file-label">{testFile}</div>
        <div>{coverageLabel}</div>
    </div>
    )
  }
  const TestFilesElements = [];
  let activeTestFile = undefined;
  let coverageElement = undefined;
  for (
    let testFileIndex = testFiles.length - 1;
    testFileIndex >= 0;
    testFileIndex--
  ) {
    let testFile = testFiles[testFileIndex];

    if (testFile.steps_amount == undefined){
        let steps_amount = 0;
        let covered_steps_amount = 0;
        for (
        let testIndex = testFile.tests.length - 1;
        testIndex >= 0;
        testIndex--
          ) {
            steps_amount += testFile.tests[testIndex].steps_amount;
            covered_steps_amount += testFile.tests[testIndex].covered_steps_amount;
          }
        testFile.steps_amount = steps_amount
        testFile.covered_steps_amount = covered_steps_amount
    }
    let coverage = testFile.covered_steps_amount/testFile.steps_amount * 100;
    let testFileName = testFile.file_name;
    let testFileElement = getTestFileWithCoverageElement(testFileName, coverage)
    if (testFile.id == activeTestFileId) {
      activeTestFile = testFile;
      if (testFile.manually_created) {
          TestFilesElements.push(
            <li
              key={testFileIndex}
              className="file-label new-active-file-label"
              type="button"
            >
                {testFileElement}
            </li>
          );
      }
      else {
          TestFilesElements.push(
            <li
              key={testFileIndex}
              className="file-label active-file-label"
              type="button"
            >
                {testFileElement}
            </li>
          );
      }
    } else {
      if (testFile.manually_created) {
          TestFilesElements.push(
            <li
              key={testFileIndex}
              className="file-label new-file-label"
              type="button"
              onClick={onTestFileClick.bind(this, testFile.id)}
            >
                {testFileElement}
            </li>
          );
      }
      else {
        TestFilesElements.push(
            <li
              key={testFileIndex}
              className="file-label"
              type="button"
              onClick={onTestFileClick.bind(this, testFile.id)}
            >
                {testFileElement}
            </li>
          );
      }
    }
  }
  const activeTests = activeTestFile.tests;
  return (
    <div>
      <div className="table-with-bar-container">
       <div className="files-bar-container">
        <div className="files-list">
          <ul className="list-group  feature-files-links position-relative overflow-auto">
            {TestFilesElements}
          </ul>
        </div>
        <AddFileModal
           activeVersionId={activeVersionId}
        />
       </div>
        <TestTable
          tests={activeTests}
          handleTestStatusUpdate={handleTestStatusUpdate}
          handleTestCommentUpdate={handleTestCommentUpdate}
          getTestData={getTestData}
          saveAllTestsFunction={saveAllTests}
          activeVersionId={activeVersionId}
          activeTestFileId={activeTestFileId}
          activeTestFileName={activeTestFile.file_name}
          openShowTestModal={openShowTestModal}
        />
      </div>
    </div>
  );
}
