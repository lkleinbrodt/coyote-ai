import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock, RefreshCw, User } from "lucide-react";
import React, { useEffect, useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";

interface CalendarEvent {
  gym: string;
  startLocal: string;
  endLocal: string;
  publicTitle: string;
  category: string;
  capacityText: string;
  instructorText: string;
  registrationLink: string;
  calendarLink: string;
}

interface CalendarData {
  events: CalendarEvent[];
  total: number;
  gyms: string[];
  categories: string[];
}

const GYM_COLORS = {
  ironworks:
    "bg-blue-100 text-blue-800 border-blue-200 hover:bg-blue-100 hover:text-blue-800",
  pacificpipe:
    "bg-purple-100 text-purple-800 border-purple-200 hover:bg-purple-100 hover:text-purple-800",
};

const CATEGORY_COLORS = {
  Yoga: "bg-pink-100 text-pink-800 hover:bg-pink-100 hover:text-pink-800",
  Climbing:
    "bg-orange-100 text-orange-800 hover:bg-orange-100 hover:text-orange-800",
  Fitness: "bg-red-100 text-red-800 hover:bg-red-100 hover:text-red-800",
  "Youth Programs":
    "bg-yellow-100 text-yellow-800 hover:bg-yellow-100 hover:text-yellow-800",
  "Gym Events":
    "bg-indigo-100 text-indigo-800 hover:bg-indigo-100 hover:text-indigo-800",
  Unknown: "bg-gray-100 text-gray-800 hover:bg-gray-100 hover:text-gray-800",
};

const TouchstoneCalendar: React.FC = () => {
  const [calendarData, setCalendarData] = useState<CalendarData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedGym, setSelectedGym] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [daysToShow, setDaysToShow] = useState<number>(3);
  const [showRefreshButton, setShowRefreshButton] = useState<boolean>(false);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const { user } = useAuth();

  useEffect(() => {
    setShowRefreshButton(user?.email === "lkleinbrodt@gmail.com");
  }, [user]);

  useEffect(() => {
    fetchCalendarData();
  }, []);

  const fetchCalendarData = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/touchstone_calendar/events");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setCalendarData(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch calendar data"
      );
    } finally {
      setLoading(false);
    }
  };

  const refreshCalendarData = async () => {
    try {
      setRefreshing(true);

      const token = import.meta.env.VITE_TOUCHSTONE_TOKEN;
      if (!token) {
        throw new Error("Touchstone token not configured");
      }

      // Call the rebuild endpoint to force refresh
      const rebuildResponse = await fetch("/api/touchstone_calendar/rebuild", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token: token,
        }),
      });

      if (!rebuildResponse.ok) {
        const errorData = await rebuildResponse.json().catch(() => ({}));
        throw new Error(
          `Failed to refresh calendar: ${rebuildResponse.status} - ${
            errorData.error || "Unknown error"
          }`
        );
      }

      // Wait a moment for the rebuild to complete, then fetch fresh data
      await new Promise((resolve) => setTimeout(resolve, 2000));
      await fetchCalendarData();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to refresh calendar data"
      );
    } finally {
      setRefreshing(false);
    }
  };

  const formatTime = (dateTimeStr: string) => {
    try {
      const date = new Date(dateTimeStr);
      return date.toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      });
    } catch {
      return dateTimeStr;
    }
  };

  const getNextDays = () => {
    const days = [];
    const today = new Date();
    for (let i = 0; i < daysToShow; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      days.push(date);
    }
    return days;
  };

  const getEventsForDate = (date: Date) => {
    if (!calendarData) return [];

    // Use local date formatting instead of UTC to avoid timezone issues
    const dateStr = date.toLocaleDateString("en-CA"); // Returns YYYY-MM-DD format

    return calendarData.events.filter((event) => {
      const eventDate = event.startLocal.split(" ")[0];
      const gymMatch = selectedGym === "all" || event.gym === selectedGym;
      const categoryMatch =
        selectedCategory === "all" || event.category === selectedCategory;
      const dateMatch = eventDate === dateStr;

      return gymMatch && categoryMatch && dateMatch;
    });
  };

  const getGymColor = (gym: string) => {
    return (
      GYM_COLORS[gym as keyof typeof GYM_COLORS] ||
      "bg-gray-100 text-gray-800 border-gray-200 hover:bg-gray-100 hover:text-gray-800"
    );
  };

  const getCategoryColor = (category: string) => {
    return (
      CATEGORY_COLORS[category as keyof typeof CATEGORY_COLORS] ||
      "bg-gray-100 text-gray-800 hover:bg-gray-100 hover:text-gray-800"
    );
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-md mx-auto">
          <CardContent className="pt-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-red-600 mb-2">Error</h3>
              <p className="text-gray-600 mb-4">{error}</p>
              <Button onClick={fetchCalendarData} variant="outline">
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!calendarData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-md mx-auto">
          <CardContent className="pt-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">No Data</h3>
              <p className="text-gray-600">No calendar data available.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const nextDays = getNextDays();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 text-center">
          Touchstone Calendar
        </h1>
        <p className="text-gray-600 mb-6 text-center">
          Calendars for my local gyms.
        </p>

        {/* Refresh Button */}
        {showRefreshButton && (
          <div className="flex justify-center mb-6">
            <Button
              onClick={refreshCalendarData}
              disabled={refreshing || loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              <RefreshCw
                className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
              />
              {refreshing ? "Refreshing..." : "Refresh Calendar Data"}
            </Button>
          </div>
        )}

        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-2">
              Days to Show
            </label>
            <Select
              value={daysToShow.toString()}
              onValueChange={(value) => setDaysToShow(parseInt(value))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Days to show" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="3">3 Days</SelectItem>
                <SelectItem value="5">5 Days</SelectItem>
                <SelectItem value="7">7 Days</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium mb-2">
              Filter by Gym
            </label>
            <Select value={selectedGym} onValueChange={setSelectedGym}>
              <SelectTrigger>
                <SelectValue placeholder="All Gyms" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Gyms</SelectItem>
                {calendarData.gyms.map((gym) => (
                  <SelectItem key={gym} value={gym}>
                    {gym.charAt(0).toUpperCase() + gym.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium mb-2">
              Filter by Category
            </label>
            <Select
              value={selectedCategory}
              onValueChange={setSelectedCategory}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {calendarData.categories.map((category) => (
                  <SelectItem key={category} value={category}>
                    {category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <hr className="my-6" />
      </div>

      {/* Calendar Grid */}
      <div
        className={`grid gap-6 ${
          daysToShow <= 3
            ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
            : daysToShow <= 5
            ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5"
            : daysToShow <= 7
            ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-7"
            : "grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-7"
        }`}
      >
        {nextDays.map((date, index) => {
          const events = getEventsForDate(date);
          const isToday = date.toDateString() === new Date().toDateString();

          return (
            <motion.div
              key={date.toISOString()}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card
                className={`h-full ${isToday ? "ring-2 ring-primary" : ""}`}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg font-bold text-center">
                    {date.toLocaleDateString("en-US", {
                      weekday: "short",
                      month: "short",
                      day: "numeric",
                    })}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    {events.length === 0 ? (
                      <p className="text-sm text-gray-400 italic">No events</p>
                    ) : (
                      events.map((event, eventIndex) => (
                        <motion.div
                          key={`${event.startLocal}-${eventIndex}`}
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{
                            delay: index * 0.1 + eventIndex * 0.05,
                          }}
                          className="border rounded-lg p-4 space-y-3"
                        >
                          <div className="flex items-start justify-between">
                            <h4 className="font-medium text-sm leading-tight">
                              {event.publicTitle}
                            </h4>
                            <Badge
                              className={`text-xs ${getGymColor(event.gym)}`}
                            >
                              {event.gym}
                            </Badge>
                          </div>

                          <div className="space-y-2">
                            <div className="flex items-center justify-between text-xs text-gray-600">
                              <div className="flex items-center">
                                <Clock className="h-3 w-3 mr-2" />
                                {formatTime(event.startLocal)} -{" "}
                                {formatTime(event.endLocal)}
                              </div>
                              {event.instructorText && (
                                <div className="flex items-center">
                                  <User className="h-3 w-3 mr-1" />
                                  {event.instructorText}
                                </div>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center justify-between pt-3">
                            <Badge
                              className={`text-xs ${getCategoryColor(
                                event.category
                              )}`}
                            >
                              {event.category}
                            </Badge>

                            {event.registrationLink && (
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-xs h-6 px-2"
                                onClick={() =>
                                  window.open(event.registrationLink, "_blank")
                                }
                              >
                                {event.capacityText
                                  ? `${event.capacityText}`
                                  : "Register"}
                              </Button>
                            )}
                          </div>
                        </motion.div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">Calendar Summary</h3>
              <p className="text-gray-600">
                Showing{" "}
                {
                  calendarData.events.filter((event) => {
                    const gymMatch =
                      selectedGym === "all" || event.gym === selectedGym;
                    const categoryMatch =
                      selectedCategory === "all" ||
                      event.category === selectedCategory;
                    return gymMatch && categoryMatch;
                  }).length
                }{" "}
                events across {calendarData.gyms.length} gyms
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TouchstoneCalendar;
