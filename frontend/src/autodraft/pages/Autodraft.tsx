import "./Autodraft.css";

import { Suspense, lazy } from "react";
import { WorkProvider, useWork } from "../WorkContext";

import Header from "../components/Header";
import LoadingPage from "./LoadingPage";
import Sidebar from "../components/Sidebar";

const ReportEditor = lazy(() => import("../components/ReportEditor"));
const DataEditor = lazy(() => import("../components/DataEditor"));
const Settings = lazy(() => import("../components/Settings"));

const Home = () => {
  const { selectedTab } = useWork();

  return (
    <div className="autodraft-container">
      <Suspense fallback={<LoadingPage />}>
        {selectedTab === "report" && <ReportEditor />}
        {selectedTab === "data" && <DataEditor />}
        {selectedTab === "settings" && <Settings />}
      </Suspense>
    </div>
  );
};

const Autodraft = () => (
  <div className="autodraft-page">
    <WorkProvider>
      <Sidebar />
      <main className="grid w-full h-full pl-[300px] mt-0">
        <Header />
        <Home />
      </main>
    </WorkProvider>
  </div>
);

export default Autodraft;
