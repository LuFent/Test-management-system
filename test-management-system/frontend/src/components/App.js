import React, { Component } from "react";
import { useRef } from "react";
import { render } from "react-dom";
import { createRoot } from "react-dom/client";
import ProjectTittle from "./ProjectTittle";
import TestFilesBar from "./TestFilesBar";
import AddVersionModal from "./AddVersionModal";
import ShowFileTextModal from "./ShowFileTextModal";


function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      activeVersionId: undefined,
      activeTestFileId: undefined,
      loaded: false,
      newVersionFormData: undefined,
      testsStates: undefined,
      openedTestName: undefined,
      openedTestText: undefined,
    };
    this.updatedTestsIds = [];
  }

  getTestData = (testId) => {
    return this.state.testsStates[testId];
  };

  openShowTestModal = (testId) => {
    let xhr = new XMLHttpRequest();
    const url = "/api/get_test_text/" + testId + "/";
    xhr.open("GET", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
        if (xhr.status >= 400) {
          return;
        }
        const testData = JSON.parse(xhr.responseText);
        this.setState({
            openedTestName: testData.name,
            openedTestText: testData.text
        });

    }.bind(this);
    xhr.send();
  }

  handleTestStatusUpdate = (testId, newStatus) => {
    if (!this.updatedTestsIds.includes(testId)) {
      this.updatedTestsIds.push(testId);
    }

    let testsStates = this.state.testsStates;
    if (testsStates[testId].status == newStatus) {
      testsStates[testId].status = "3";
    } else {
      testsStates[testId].status = newStatus;
    }
    testsStates[testId].file = this.state.activeTestFileId;
    testsStates[testId].version = this.state.activeVersionId;

    this.setState({
      testsStates: testsStates,
    });
  };

  handleTestCommentUpdate = (testId, event) => {
    if (!this.updatedTestsIds.includes(testId)) {
      this.updatedTestsIds.push(testId);
    }
    let testsStates = this.state.testsStates;
    testsStates[testId].comment = event.target.value;
    testsStates[testId].file = this.state.activeTestFileId;
    testsStates[testId].version = this.state.activeVersionId;

    this.setState({
      testsStates: testsStates,
    });
  };

  saveAllTests = () => {
    let data = [];
    for (
      let testIndex = 0;
      testIndex < this.updatedTestsIds.length;
      testIndex++
    ) {
      let testId = this.updatedTestsIds[testIndex];
      data.push({
        id: testId,
        status: this.state.testsStates[testId].status,
        comment: this.state.testsStates[testId].comment,
      });
    }
    let xhr = new XMLHttpRequest();
    const url = "/api/update_test/";
    xhr.open("POST", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
      window.location.reload(false);
    };
    xhr.send(JSON.stringify(data));
  };

  getActiveVersion = () => {
    const version = this.state.data.versions.filter(
      (v) => v.id == this.state.activeVersionId
    )[0];
    return version;
  }

  addTestFileData = (versionId, testFileId) => {
    const version = this.state.data.versions.filter(
      (v) => v.id == versionId
    )[0];
    let testFile = version.test_files.filter((tf) => tf.id == testFileId)[0];
    let testsStates = this.state.testsStates;
    for (let testIndex = 0; testIndex < testFile.tests.length; testIndex++) {
      let test = testFile.tests[testIndex];
      if (!(test.id in testsStates)) {
        testsStates[test.id] = {
          status: test.status,
          comment: test.comment,
        };
      }
    }
    return testsStates;
  };

  deleteVersion = (versionId) => {
    let xhr = new XMLHttpRequest();
    const url = "/api/delete_version/" + versionId + "/";
    xhr.open("DELETE", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
      let data = this.state.data;
      let version = data.versions.filter((v) => v.id == versionId)[0];
      let versionIndex = data.versions.indexOf(version);
      data.versions.splice(versionIndex, 1);
      let newActiveVersionId = undefined;
      if (data.versions.length > 0) {
        newActiveVersionId = data.versions[0].id;
      }
      this.setState({
        data: data,
        activeVersionId: newActiveVersionId,
      });
      if (newActiveVersionId !== undefined) {
        this.makeVersionActive(newActiveVersionId);
      }
    }.bind(this);
    xhr.send();
  };

  makeVersionActive = (versionId) => {
    let version = this.state.data.versions.filter((v) => v.id == versionId)[0];
    if ("test_files" in version) {
      let NewActiveTestFileId = undefined;

      if (version.test_files.length > 0) {
        NewActiveTestFileId = version.test_files[0].id;
      }

      this.setState({
        activeVersionId: versionId,
        activeTestFileId: NewActiveTestFileId,
      });
    } else {
      let xhr = new XMLHttpRequest();
      const url = "/api/project_versions_with_coverage/" + versionId;
      xhr.open("GET", url);
      xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
      xhr.setRequestHeader("Content-Type", "application/json");

      xhr.onload = function () {
        if (xhr.status >= 400) {
          return;
        }
        const versionData = JSON.parse(xhr.responseText);
        let newData = this.state.data;
        let testsStates = this.state.testsStates;
        newData.versions = newData.versions.filter(
          (v) => v.id != versionData.id
        );
        newData.versions.push(versionData);

        let NewActiveTestFileId = undefined;
        if (versionData.test_files.length > 0) {
          let NewActiveTestFile = versionData.test_files[0];
          NewActiveTestFileId = NewActiveTestFile.id;

          testsStates = this.addTestFileData(
            versionData.id,
            NewActiveTestFileId
          );
        }

        this.setState({
          activeVersionId: versionId,
          data: newData,
          activeTestFileId: NewActiveTestFileId,
          testsStates: testsStates,
        });
      }.bind(this);
      xhr.send();
    }
  };

  handleTestFileClick = (testFileId) => {
    const versionId = this.state.activeVersionId;
    const version = this.state.data.versions.filter(
      (v) => v.id == versionId
    )[0];
    let activeTestFile = version.test_files.filter(
      (tf) => tf.id == testFileId
    )[0];
    //let testsStates = this.state.testsStates;
    let testsStates = this.addTestFileData(versionId, testFileId);

    this.setState({
      activeTestFileId: testFileId,
      testsStates: testsStates,
    });
  };

  componentDidMount() {
    const { pathname } = window.location;
    const paths = pathname.split("/").filter((entry) => entry !== "");
    const projectId = paths[paths.length - 1];
    const url = "/api/projects_with_last_version/" + projectId;
    let xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
      const data = JSON.parse(xhr.responseText);
      let activeVersionId = undefined;
      let activeTestFileId = undefined;
      let testsStates = {};

      if (data.versions && data.versions.length > 0) {
        let lastVersion = data.versions.slice(-1)[0];
        activeVersionId = lastVersion.id;
        if (lastVersion.test_files && lastVersion.test_files.length > 0) {
          let activeVersionTestFiles = lastVersion.test_files;
          let activeTestFile = activeVersionTestFiles[0];
          activeTestFileId = activeTestFile.id;
          for (
            let testIndex = 0;
            testIndex < activeTestFile.tests.length;
            testIndex++
          ) {
            let test = activeTestFile.tests[testIndex];
            if (!(test.id in testsStates)) {
              testsStates[test.id] = {
                status: test.status,
                comment: test.comment,
              };
            }
          }
        }
      }

      this.setState({
        data: data,
        activeVersionId: activeVersionId,
        activeTestFileId: activeTestFileId,
        loaded: true,
        testsStates: testsStates,
      });
    }.bind(this);
    xhr.send();
  }

  render() {

    if (!this.state.loaded) {
      return <span>Loading</span>;
    }
    if ((!this.state.data.versions) || (this.state.data.versions && this.state.data.versions.length == 0)){
     return (
        <div className="app-container">
          <p>No versions available</p>
          <AddVersionModal />
        </div>
      );
    }
    let version = this.getActiveVersion();
    let activeTestFiles = version.test_files;

    if ((!activeTestFiles) || (activeTestFiles && activeTestFiles.length == 0)) {
        return (
          <div className="app-container">
            <ProjectTittle
              ProjectCommit={this.getActiveVersion().commit_hash}
              ProjectName={this.state.data.name}
              versions={this.state.data.versions}
              activeVersionId={this.state.activeVersionId}
              onVersionClick={this.makeVersionActive}
            />
            <span>No tests</span>
          </div>
        );
      }
      if (!version.is_valid) {
        return (
          <div className="app-container">
            <ProjectTittle
              ProjectCommit={this.getActiveVersion().commit_hash}
              ProjectName={this.state.data.name}
              versions={this.state.data.versions}
              activeVersionId={this.state.activeVersionId}
              onVersionClick={this.makeVersionActive}
            />
          </div>
        );
      }

      return (
        <div className="app-container">
          <ProjectTittle
            ProjectCommit={this.getActiveVersion().commit_hash}
            ProjectName={this.state.data.name}
            versions={this.state.data.versions}
            activeVersionId={this.state.activeVersionId}
            onVersionClick={this.makeVersionActive}
          />

          <TestFilesBar
            activeVersionId={this.state.activeVersionId}
            testFiles={activeTestFiles}
            activeTestFileId={this.state.activeTestFileId}
            onTestFileClick={this.handleTestFileClick}
            handleTestStatusUpdate={this.handleTestStatusUpdate}
            handleTestCommentUpdate={this.handleTestCommentUpdate}
            getTestData={this.getTestData}
            saveAllTests={this.saveAllTests}
            openShowTestModal={this.openShowTestModal}
          />
        <ShowFileTextModal
            openedTestName={this.state.openedTestName}
            openedTestText={this.state.openedTestText}
        />
        </div>
      );
    }
  }

export default App;

const container = document.getElementById("app");
const root = createRoot(container);
root.render(<App tab="home" />);
