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
import { deleteProject, updateProject } from "../services/api";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import PlaceholderMessage from "./PlaceholderMessage";
import { useState } from "react";
import { useWork } from "../WorkContext";

function ProjectSettings() {
  const { selectedProject, setSelectedProject } = useWork();
  const [newName, setNewName] = useState(selectedProject?.name || "");
  const [isLoading, setIsLoading] = useState(false);

  if (!selectedProject) {
    return (
      <div>
        <h2 className="text-2xl font-bold mb-4">Project Settings</h2>
        <PlaceholderMessage
          title="No project selected"
          description="Select a project to view its settings."
        />
      </div>
    );
  }

  const handleRename = async () => {
    if (newName.trim() && selectedProject) {
      setIsLoading(true);
      try {
        const updatedProject = await updateProject(selectedProject.id, {
          name: newName.trim(),
        });
        setSelectedProject(updatedProject);
      } catch (error) {
        console.error("Failed to rename project:", error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await deleteProject(selectedProject.id);
      setSelectedProject(null);
    } catch (error) {
      console.error("Failed to delete project:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Project Settings</h2>
      <div className="space-y-6">
        {/* Metadata Card */}
        <Card>
          <CardHeader>
            <CardTitle>Project Information</CardTitle>
            <CardDescription>View details about your project</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Project ID</Label>
              <p className="text-sm text-muted-foreground">
                {selectedProject.id}
              </p>
            </div>
            <div>
              <Label>Index Status</Label>
              <p className="text-sm text-muted-foreground">
                {selectedProject.index_available ? "Indexed" : "Not Indexed"}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Actions Card */}
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
            <CardDescription>Manage your project settings</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-row justify-around">
            <Dialog>
              <DialogTrigger asChild>
                <Button
                  variant="outline"
                  className="w-1/3"
                  disabled={isLoading}
                >
                  {isLoading ? "Saving..." : "Rename Project"}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Rename Project</DialogTitle>
                  <DialogDescription>
                    Enter a new name for your project
                  </DialogDescription>
                </DialogHeader>
                <div className="py-4">
                  <Label htmlFor="name">Project Name</Label>
                  <Input
                    id="name"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="Enter new project name"
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

            <Dialog>
              <DialogTrigger asChild>
                <Button
                  variant="destructive"
                  className="w-1/3"
                  disabled={isLoading}
                >
                  {isLoading ? "Deleting..." : "Delete Project"}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Delete Project</DialogTitle>
                  <DialogDescription>
                    Are you sure you want to delete this project? This action
                    cannot be undone. All reports and files associated with this
                    project will be permanently deleted.
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

export default ProjectSettings;
