import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { deleteReport, updateReport } from "../services/api";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import PlaceholderMessage from "./PlaceholderMessage";
import { useState } from "react";
import { useWork } from "../WorkContext";

function ReportSettings() {
  const { selectedReport, setSelectedReport, setAvailableReports } = useWork();
  const [newName, setNewName] = useState(selectedReport?.name || "");
  const [isLoading, setIsLoading] = useState(false);

  if (!selectedReport) {
    return (
      <div>
        <h2 className="text-2xl font-bold mb-4">Report Settings</h2>
        <PlaceholderMessage
          title="No report selected"
          description="Select a report to view its settings."
        />
      </div>
    );
  }

  const handleRename = async () => {
    if (newName.trim() && selectedReport) {
      setIsLoading(true);
      try {
        const updatedReport = await updateReport(selectedReport.id, {
          name: newName.trim(),
        });
        setSelectedReport(updatedReport);
        setAvailableReports((prev) =>
          prev.map((report) =>
            report.id === selectedReport.id ? updatedReport : report
          )
        );
      } catch (error) {
        console.error("Failed to rename report:", error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await deleteReport(selectedReport.id);
      setAvailableReports((prev) =>
        prev.filter((report) => report.id !== selectedReport.id)
      );
      setSelectedReport(null);
    } catch (error) {
      console.error("Failed to delete report:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Report Settings</h2>
      <div className="space-y-6">
        {/* Metadata Card */}
        <Card>
          <CardHeader>
            <CardTitle>Report Information</CardTitle>
            <CardDescription>View details about your report</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Report ID</Label>
              <p className="text-sm text-muted-foreground">
                {selectedReport.id}
              </p>
            </div>
            <div>
              <Label>Created</Label>
              <p className="text-sm text-muted-foreground">
                {new Date(selectedReport.created_at).toLocaleDateString()}
              </p>
            </div>
            <div>
              <Label>Last Modified</Label>
              <p className="text-sm text-muted-foreground">
                {new Date(selectedReport.updated_at).toLocaleDateString()}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Actions Card */}
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
            <CardDescription>Manage your report settings</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-row justify-around">
            {/* Rename Dialog */}
            <Dialog>
              <DialogTrigger asChild>
                <Button
                  variant="outline"
                  className="w-1/3 justify-center"
                  disabled={isLoading}
                >
                  {isLoading ? "Saving..." : "Rename Report"}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Rename Report</DialogTitle>
                  <DialogDescription>
                    Enter a new name for your report
                  </DialogDescription>
                </DialogHeader>
                <div className="py-4">
                  <Label htmlFor="name">Report Name</Label>
                  <Input
                    id="name"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="Enter new report name"
                  />
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={handleRename}
                    disabled={isLoading}
                  >
                    {isLoading ? "Saving..." : "Save Changes"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Delete Dialog */}
            <Dialog>
              <DialogTrigger asChild>
                <Button
                  variant="destructive"
                  className="w-1/3 justify-center"
                  disabled={isLoading}
                >
                  {isLoading ? "Deleting..." : "Delete Report"}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Delete Report</DialogTitle>
                  <DialogDescription>
                    Are you sure you want to delete this report? This action
                    cannot be undone.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <Button variant="outline">Cancel</Button>
                  <Button
                    variant="destructive"
                    onClick={handleDelete}
                    disabled={isLoading}
                  >
                    {isLoading ? "Deleting..." : "Delete"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default ReportSettings;
