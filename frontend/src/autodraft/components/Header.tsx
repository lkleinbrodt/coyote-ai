import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { useWork } from "../WorkContext";

export default function Header() {
  const { selectedTab, setSelectedTab } = useWork();

  const handleTabChange = (value: string) => {
    setSelectedTab(value);
  };

  return (
    <div className="gap-4 p-4 border-b">
      <Tabs
        defaultValue={selectedTab}
        value={selectedTab}
        onValueChange={handleTabChange}
        className="w-[400px]"
      >
        <TabsList>
          <TabsTrigger value="report">Report</TabsTrigger>
          <TabsTrigger value="data">Data</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>
      </Tabs>
    </div>
  );
}
