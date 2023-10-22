import React, { Component } from "react";
import AddVersionModal from "./AddVersionModal";
import UpdateVersionModal from "./UpdateVersionModal";
import PushFilesModal from "./PushFilesModal";
import DeleteVersionModal from "./DeleteVersionModal";


export default function ProjectTittle({
  ProjectName,
  ProjectCommit,
  activeVersionId,
  versions,
  onVersionClick,
}) {
  if (versions === undefined) {
    return <span>Loading..</span>;
  }

  const secondaryVersionsElements = [];
  let chosenVersion = undefined;
  versions.sort((v_1, v_2) => v_1["id"] - v_2["id"]);
  for (
    let versionIndex = versions.length - 1;
    versionIndex >= 0;
    versionIndex--
  ) {
    let version = versions[versionIndex];
    if (version.id == activeVersionId) {
      chosenVersion = version;
      secondaryVersionsElements.push(
        <li key={versionIndex}>
          <button className="dropdown-item active">
            {version.version_label}
          </button>
        </li>
      );
    } else {
      secondaryVersionsElements.push(
        <li key={versionIndex}>
          <button
            className="dropdown-item"
            onClick={onVersionClick.bind(this, version.id)}
          >
            {version.version_label}
          </button>
        </li>
      );
    }
  }
  let errorLabel = undefined;
  if (chosenVersion.error_message){
   errorLabel = <p className="text-danger">{chosenVersion.error_message}</p>
  }

  return (
    <div>
      <div className="project-info">
        <p className="project-name">Project "{ProjectName}", version - </p>
        <div className="dropdown project-version-choose">
          <button
            className="btn btn-secondary btn-lg dropdown-toggle"
            type="button"
            id="dropdownMenuButton1"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            {chosenVersion.version_label}
          </button>
          <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">
            {secondaryVersionsElements}
          </ul>
        </div>
      </div>
      <p className="text-secondary">Commit: {ProjectCommit}</p>
      {errorLabel}
      <div className="version-actions">
        <div className="version-action">
          <AddVersionModal />
        </div>
        <div className="version-action">
          <UpdateVersionModal versionId={activeVersionId} />
        </div>
        <div className="version-action">
            <PushFilesModal versionId={activeVersionId} />
        </div>
        <div className="version-action">
            <DeleteVersionModal
                version={chosenVersion}
                project={ProjectName}
                />
        </div>
      </div>
    </div>
  );
}
