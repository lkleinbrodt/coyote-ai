import { Email, deleteEmails, fetchEmails } from "../email/services/api";
import React, { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";

import { Button } from "../components/ui/button";
import { Checkbox } from "../components/ui/checkbox";
import { Input } from "../components/ui/input";
import { Loader2 } from "lucide-react";
import { Skeleton } from "../components/ui/skeleton";
import { useToast } from "../hooks/use-toast";

const EmailAssistantPage: React.FC = () => {
  const { toast } = useToast();
  const [emails, setEmails] = useState<Email[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [filterQuery, setFilterQuery] = useState<string>("");
  const [selectedEmails, setSelectedEmails] = useState<Set<string>>(new Set());
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  const loadEmails = async () => {
    setIsLoading(true);
    try {
      const fetchedEmails = await fetchEmails();
      setEmails(fetchedEmails);
    } catch {
      toast({
        title: "Error",
        description: "Failed to fetch emails. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEmails();
  }, [toast]);

  // Filter emails based on the query
  const filteredEmails = React.useMemo(() => {
    if (!filterQuery.trim()) return emails;

    return emails.filter((email) =>
      email.sender.toLowerCase().includes(filterQuery.toLowerCase())
    );
  }, [emails, filterQuery]);

  // Handle checkbox selection
  const toggleEmailSelection = (emailId: string) => {
    const newSelectedEmails = new Set(selectedEmails);
    if (newSelectedEmails.has(emailId)) {
      newSelectedEmails.delete(emailId);
    } else {
      newSelectedEmails.add(emailId);
    }
    setSelectedEmails(newSelectedEmails);
  };

  // Select/deselect all visible emails
  const toggleSelectAll = () => {
    if (selectedEmails.size === filteredEmails.length) {
      // Deselect all if all are selected
      setSelectedEmails(new Set());
    } else {
      // Select all filtered emails
      const allEmailIds = filteredEmails.map((email) => email.id);
      setSelectedEmails(new Set(allEmailIds));
    }
  };

  // Handle email deletion
  const handleDeleteEmails = async () => {
    if (selectedEmails.size === 0) return;

    setIsDeleting(true);
    try {
      const emailIds = Array.from(selectedEmails);
      const success = await deleteEmails(emailIds);

      if (success) {
        toast({
          title: "Success",
          description: `${emailIds.length} email(s) deleted successfully.`,
        });
        // Clear selection and refresh the email list
        setSelectedEmails(new Set());
        await loadEmails();
      } else {
        toast({
          title: "Error",
          description: "Failed to delete emails. Please try again.",
          variant: "destructive",
        });
      }
    } catch {
      toast({
        title: "Error",
        description: "An error occurred while deleting emails.",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="flex flex-col items-center justify-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Email Assistant</h1>
        <p className="text-muted-foreground">
          View, filter, and manage your Gmail messages.
        </p>
      </div>

      <div className="flex flex-col space-y-4">
        {/* Filter and action buttons */}
        <div className="flex justify-between items-center">
          <div className="w-full md:w-1/3">
            <Input
              placeholder="Filter by sender..."
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              disabled={isLoading}
            />
          </div>
          <Button
            variant="destructive"
            disabled={selectedEmails.size === 0 || isDeleting}
            className="ml-2"
            onClick={handleDeleteEmails}
          >
            {isDeleting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              "Delete Selected"
            )}
          </Button>
        </div>

        {/* Email table */}
        {isLoading ? (
          // Loading state with skeleton UI
          <div className="space-y-2">
            {[...Array(5)].map((_, index) => (
              <div key={index} className="flex items-center space-x-4">
                <Skeleton className="h-4 w-4 rounded-sm" />
                <Skeleton className="h-4 w-[250px]" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        ) : (
          // Email table
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[40px]">
                  <Checkbox
                    checked={
                      selectedEmails.size > 0 &&
                      selectedEmails.size === filteredEmails.length
                    }
                    onCheckedChange={toggleSelectAll}
                  />
                </TableHead>
                <TableHead className="w-[250px]">Sender</TableHead>
                <TableHead>Subject</TableHead>
                <TableHead className="hidden md:table-cell">Snippet</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredEmails.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={4}
                    className="text-center py-8 text-muted-foreground"
                  >
                    {emails.length === 0
                      ? "No emails to display."
                      : "No emails match your filter."}
                  </TableCell>
                </TableRow>
              ) : (
                filteredEmails.map((email) => (
                  <TableRow
                    key={email.id}
                    className={`${
                      selectedEmails.has(email.id) ? "bg-muted/50" : ""
                    } ${email.is_unread ? "font-bold" : ""}`}
                  >
                    <TableCell>
                      <Checkbox
                        checked={selectedEmails.has(email.id)}
                        onCheckedChange={() => toggleEmailSelection(email.id)}
                      />
                    </TableCell>
                    <TableCell>{email.sender}</TableCell>
                    <TableCell>{email.subject}</TableCell>
                    <TableCell className="hidden md:table-cell text-muted-foreground truncate max-w-md">
                      {email.snippet}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
};

export default EmailAssistantPage;
