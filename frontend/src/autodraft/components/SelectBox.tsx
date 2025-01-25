"use client";

import * as React from "react";

import { CaretSortIcon, CheckIcon } from "@radix-ui/react-icons";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Props {
  options: Array<{ id: string; name: string }>;
  value: { id: string | undefined; name: string | undefined };
  setValue: (
    value: { id: string; name: string } | { id: string; name: string }
  ) => void;
  disabled?: boolean;
  placeholder?: string;
  emptyMessage?: string;
}

export function SelectBox({
  options,
  value,
  setValue,
  disabled = false,
  placeholder = "Select...",
  emptyMessage = "No options found.",
}: Props) {
  const [open, setOpen] = React.useState(false);

  return (
    <Popover open={disabled ? false : open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[200px] justify-between"
          disabled={disabled}
        >
          {value?.name
            ? options.find((option) => option.name === value.name)?.name
            : placeholder}
          <CaretSortIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          {options.length > 1 && (
            <CommandInput placeholder="Search options..." className="h-9" />
          )}
          <CommandList>
            <CommandEmpty>{emptyMessage}</CommandEmpty>
            <CommandGroup>
              {options.map((option) => (
                <CommandItem
                  key={option.id}
                  value={option.id}
                  onSelect={() => {
                    setValue(option);
                    setOpen(false);
                  }}
                >
                  {option.name}
                  <CheckIcon
                    className={cn(
                      "ml-auto h-4 w-4",
                      value?.id === option.id ? "opacity-100" : "opacity-0"
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
