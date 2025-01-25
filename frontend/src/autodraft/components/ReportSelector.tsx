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
import { Skeleton } from "@/components/ui/skeleton";
import { useWork } from "@/autodraft/WorkContext";

export function ReportSelector() {
  const [newReportName, setNewReportName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [canCreate, setCanCreate] = useState(false);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const {
    selectedReport,
    selectedProject,
    setSelectedReport,
    availableReports,
    setAvailableReports,
    loading,
  } = useWork();

  useEffect(() => {
    if (selectedProject) {
      getReports(selectedProject.id).then((reports) => {
        setAvailableReports(reports);
        if (reports.length > 0 && !selectedReport) {
          setSelectedReport(reports[0]);
        }
      });
    }
  }, [selectedProject, setAvailableReports, setSelectedReport, selectedReport]);

  const handleSubmit = async () => {
    // If the report name is already taken, show an error
    if (availableReports.some((report) => report.name === newReportName)) {
      setError("Report name already taken");
      return;
    }
    try {
      const report: Report = await newReport(
        newReportName,
        selectedProject!.id
      );
      // Add new report to available reports
      setAvailableReports([...availableReports, report]);
      setSelectedReport(report);
      // Reset state
      setError(null);
      setCanCreate(false);
      setNewReportName("");
    } catch (err) {
      // handle possible backend error
      console.error("Failed to create new report:", err);
    }
  };

  const handleChangeReport = (value: { id: string; name: string }) => {
    const report = availableReports.find((r) => r.id === value.id);
    if (report) {
      setSelectedReport(report);
    } else {
      setSelectedReport(null);
    }
  };

  // Validate the new report name whenever it changes
  const handleNewReportChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name = e.target.value;
    setNewReportName(name);
    if (name.trim().length === 0) {
      setCanCreate(false);
      setError("Report name cannot be empty");
      return;
    }
    if (availableReports.some((r) => r.name === name)) {
      setCanCreate(false);
      setError("Report name already taken");
      return;
    }
    setError(null);
    setCanCreate(true);
  };

  const handleOpenSheet = () => {
    // optional custom logic
  };

  if (loading) {
    return (
      <div className="flex flex-row gap-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-10" />
      </div>
    );
  }

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
        //if no project selected, then disable the report selector
        disabled={!selectedProject}
        emptyMessage="Press + to create a new report."
      />
      <Sheet>
        <SheetTrigger asChild>
          <Button
            variant="outline"
            size="icon"
            onClick={handleOpenSheet}
            disabled={!selectedProject}
          >
            <PlusIcon />
          </Button>
        </SheetTrigger>
        <SheetContent side="left">
          <SheetHeader>
            <SheetTitle>New Report</SheetTitle>
            {/* Wrap your input+button in a form */}
            <form
              onSubmit={(e) => {
                e.preventDefault(); // prevents a browser reload
                if (canCreate) {
                  handleSubmit();
                }
              }}
              className="flex w-full gap-2 mt-2"
            >
              <Input
                placeholder="Report name"
                onChange={handleNewReportChange}
                value={newReportName}
              />
              <SheetClose>
                <Button
                  type="submit"
                  ref={closeButtonRef}
                  disabled={!canCreate}
                >
                  Create
                </Button>
              </SheetClose>
            </form>
          </SheetHeader>
          {error && <div className="text-red-500 mt-2">{error}</div>}
        </SheetContent>
      </Sheet>
    </div>
  );
}

export default ReportSelector;
