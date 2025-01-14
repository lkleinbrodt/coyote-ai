"use client";

import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { getReports, newReport } from "@/autodraft/services/api";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PlusIcon } from "@radix-ui/react-icons";
import { Report } from "@/autodraft/types";
import { SelectBox } from "./SelectBox";
import { useAuth } from "@/contexts/AuthContext";
import { useWork } from "@/autodraft/WorkContext";

export function ReportSelector() {
  const [availableReports, setAvailableReports] = useState<Report[]>([]);
  const [newReportName, setNewReportName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [canCreate, setCanCreate] = useState(false);
  const { selectedReport, selectedProject, setSelectedReport } = useWork();
  const { user } = useAuth();
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (user && selectedProject) {
      getReports(selectedProject.id).then((reports) => {
        setAvailableReports(reports);
        //set selected report to the first one
        if (reports.length > 0) {
          setSelectedReport(reports[0]);
        }
      });
    }
  }, [user, selectedProject, setSelectedReport]);

  const handleSubmit = () => {
    //check if the report name is already taken
    if (availableReports.some((report) => report.name === newReportName)) {
      setError("Report name already taken");
      return;
    }
    newReport(newReportName, selectedProject!.id).then((report: Report) => {
      //add new report to available reports
      setAvailableReports([...availableReports, report]);
      setSelectedReport(report);
    });
    closeButtonRef.current?.click();
    setError(null);
    setCanCreate(false);
    setNewReportName("");
  };

  const handleChangeReport = (value: { id: string; name: string }) => {
    const report = availableReports.find((r) => r.id === value.id);
    if (report) {
      setSelectedReport(report);
    } else {
      setSelectedReport(null);
    }
  };

  const handleNewReportChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    //check the following conditions to see if the user can create a new report
    //1) new report name is not empty
    //2) new report name is not already taken
    const name = e.target.value;
    setNewReportName(name);
    if (name.length === 0) {
      setCanCreate(false);
      setError("Report name cannot be empty");
      return;
    }
    setError(null);

    if (availableReports.some((report) => report.name === name)) {
      setCanCreate(false);
      setError("Report name already taken");
      return;
    }
    setError(null);

    setCanCreate(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && canCreate) {
      handleSubmit();
    }
  };

  const handleOpenSheet = () => {
    //pass
  };

  return (
    <div className="flex flex-row gap-4">
      <SelectBox
        value={
          selectedReport
            ? { id: selectedReport.id, name: selectedReport.name }
            : { id: undefined, name: undefined }
        }
        options={availableReports}
        setValue={handleChangeReport}
      />
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="outline" size="icon" onClick={handleOpenSheet}>
            <PlusIcon />
          </Button>
        </SheetTrigger>
        <SheetContent side="left">
          <SheetHeader>
            <SheetTitle>New Report</SheetTitle>
            <div className="flex flex-row gap-2">
              <Input
                placeholder="Report name"
                onChange={handleNewReportChange}
                onKeyDown={handleKeyDown}
              />
              <SheetClose>
                <Button
                  onClick={handleSubmit}
                  ref={closeButtonRef}
                  disabled={!canCreate}
                >
                  Create
                </Button>
              </SheetClose>
            </div>
          </SheetHeader>

          {error && <div className="text-red-500">{error}</div>}
        </SheetContent>
      </Sheet>
    </div>
  );
}

export default ReportSelector;
