import "./Autodraft.css";

import { WorkProvider, useWork } from "../WorkContext";

import DataEditor from "../components/DataEditor";
import Header from "../components/Header";
import ReportEditor from "../components/ReportEditor";
import Sidebar from "../components/Sidebar";

const Home = () => {
  const { selectedTab } = useWork();

  return (
    <div className="autodraft-container">
      {selectedTab === "report" && <ReportEditor />}
      {selectedTab === "data" && <DataEditor />}
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
